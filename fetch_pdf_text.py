#!/usr/bin/env python3
"""
fetch_pdf_text.py — download a PDF and extract its text.

Used as a fallback by /scan-boards when an org publishes board dates inside
PDFs (annual board calendars, board agendas with "next meeting" notes,
schedule of meetings docs) rather than on a webpage.

Two delivery routes:
  * `requests` GET — fast, but blocked on Cloudflare-protected sites.
  * `--playwright` — uses fetch_with_playwright.py's request context (real
    browser) to bypass UA/Cloudflare blocks. Slower but works on the trusts
    that need it.

Usage:
    python fetch_pdf_text.py URL [--playwright] [--out FILE] [--head N]
"""
import argparse
import sys
import tempfile
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def fetch_pdf_requests(url, dest):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status >= 400:
            raise RuntimeError(f"HTTP {r.status}")
        Path(dest).write_bytes(r.read())


def fetch_pdf_playwright(url, dest):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fetch_with_playwright import render
    render(url, mode="download", out_path=dest, timeout=45)


def extract_text(pdf_path):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception as e:
            parts.append(f"[page extract error: {e}]")
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--playwright", action="store_true", help="Use Playwright to bypass blocks")
    ap.add_argument("--out", help="Where to save the PDF (default: temp file, deleted after)")
    ap.add_argument("--head", type=int, help="Print only first N chars of text")
    args = ap.parse_args()

    tmp = None
    if args.out:
        dest = Path(args.out)
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        dest = Path(tmp.name)

    try:
        if args.playwright:
            fetch_pdf_playwright(args.url, dest)
        else:
            try:
                fetch_pdf_requests(args.url, dest)
            except Exception as e:
                print(f"requests fetch failed ({e}) — retrying with Playwright", file=sys.stderr)
                fetch_pdf_playwright(args.url, dest)

        text = extract_text(dest)
        if args.head:
            text = text[: args.head]
        sys.stdout.write(text)
    finally:
        if tmp:
            try:
                Path(tmp.name).unlink()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

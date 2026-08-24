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


def write_out(text):
    """Write extracted text to stdout as UTF-8, whatever the console codepage is.

    Board packs are full of £ and — . On Windows, sys.stdout defaults to cp1252 and
    `sys.stdout.write` raises UnicodeEncodeError on the first character it cannot map
    (a ballot-box glyph killed this script on 2026-08-24), so the caller sees a traceback
    and an empty file rather than the pack text.
    """
    data = text.encode("utf-8", "replace")
    buf = getattr(sys.stdout, "buffer", None)
    if buf is not None:
        buf.write(data)
        buf.flush()
    else:
        sys.stdout.write(data.decode("utf-8", "replace"))


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


def sniff(path):
    """What did we actually download? Trusts serve documents from extension-less handler
    URLs (/download_file/view/8769/2198), so the URL tells you nothing about the format."""
    head = Path(path).read_bytes()[:8]
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK\x03\x04"):
        return "ooxml"          # .docx / .xlsx / .pptx — a zip
    if head.startswith(b"\xd0\xcf\x11\xe0"):
        return "ole"            # legacy .doc / .xls
    if head[:5].lower() in (b"<!doc", b"<html"):
        return "html"           # usually a login wall or an error page
    return "unknown"


def extract_ooxml(path):
    """Text from a .docx (and enough of .pptx/.xlsx to be useful).

    Surrey and Sussex publishes its entire board pack as Word files served from
    extension-less URLs. They download intact and pypdf then rejects every one with
    "Stream has ended unexpectedly", so on 2026-08-24 eight of ten papers — including the
    auditor's report carrying a section 30 referral to the Secretary of State — looked
    unreadable. Sniff the header instead of trusting the URL.
    """
    import re
    import zipfile
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "word/document.xml" in names:
            targets = ["word/document.xml"]
            targets += sorted(n for n in names
                              if re.match(r"word/(header|footer)\d*\.xml$", n))
        elif any(n.startswith("ppt/slides/slide") for n in names):
            targets = sorted(n for n in names
                             if re.match(r"ppt/slides/slide\d+\.xml$", n))
        elif "xl/sharedStrings.xml" in names:
            targets = ["xl/sharedStrings.xml"]
        else:
            raise RuntimeError("zip is not a recognised Office document: %s" % names[:5])
        parts = []
        for t in targets:
            x = z.read(t).decode("utf-8", "replace")
            x = re.sub(r"</w:p>|</a:p>|</w:tr>", "\n", x)
            x = re.sub(r"<w:tab[^>]*/>|</w:tc>", "\t", x)
            x = re.sub(r"<[^>]+>", "", x)
            for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                         ("&quot;", '"'), ("&apos;", "'")):
                x = x.replace(a, b)
            parts.append(re.sub(r"\n{3,}", "\n\n", x))
    return "\n\n".join(parts)


def extract_pdf(pdf_path):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception as e:
            parts.append(f"[page extract error: {e}]")
    return "\n\n".join(parts)


def extract_text(path):
    kind = sniff(path)
    if kind == "ooxml":
        return extract_ooxml(path)
    if kind == "html":
        raise RuntimeError(
            "downloaded an HTML page, not a document — the URL is probably a landing page "
            "or the host served a block page; retry with --playwright")
    if kind == "ole":
        raise RuntimeError("legacy .doc/.xls binary format — not supported, open manually")
    return extract_pdf(path)


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
        write_out(text)
    finally:
        if tmp:
            try:
                Path(tmp.name).unlink()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())

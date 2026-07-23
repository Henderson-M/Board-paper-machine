#!/usr/bin/env python3
"""
extract_board_html.py — deterministic (no-LLM) extractor for board pages.

WHY THIS EXISTS
---------------
WebFetch (and Playwright `--text`) read a page by running a small summariser
model over it. That model sometimes *drops* real content — a meeting date or a
PDF link that is genuinely in the page's HTML — especially when rows sit in a
long, non-chronological table where most cells say "Currently unavailable".
This is an OMISSION failure, and the skill's anti-fabrication guard (which only
rejects *invented* dates) does nothing about it. On 2026-06-24 the Leeds
Community Healthcare (RY6) page dropped its 23 July + 24 June rows this way, so
the board pack was never detected.

This script is the deterministic ground-truth the skill reconciles against. It
does NO summarising: it pulls raw HTML and reports, verbatim, every PDF/document
link and every date-like string actually present, plus a table-row pairing so a
date can be matched to its papers link (or its "Currently unavailable" cell).

It is trust-agnostic — nothing here is specific to Leeds Community. Any page
where the content is in static HTML benefits.

DELIVERY
--------
  * requests-style GET first (fast).
  * `--playwright` (or automatic on block/JS) reuses fetch_with_playwright.py's
    browser context to get rendered HTML for Cloudflare/UA/JS pages.
  * `--html-file FILE` parses HTML you already fetched (e.g. the `--html` dump
    from a Playwright call in the skill) so no page is fetched twice.

USAGE
    python extract_board_html.py URL [--playwright] [--html-file FILE]
                                     [--base-url URL] [--pretty]

OUTPUT (stdout): JSON
    {
      "source_url": "...",
      "fetched_via": "requests|playwright|html-file",
      "pdf_links":  [{"url","text","kind","context"}],   # absolute URLs
      "dates":      [{"iso","raw","context"}],            # every date in text
      "rows":       [{"text","dates":[iso...],"pdf_links":[{url,text}]}]
    }
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

# --- Encoding guard (same rationale as fetch_with_playwright.py) ------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
# ---------------------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

DOC_EXTS = (".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt")

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_RE = "|".join(sorted(_MONTHS, key=len, reverse=True))

# Date patterns, tried in order. Each returns (year, month, day) via _parse_*.
_DATE_PATTERNS = [
    # 23 July 2026  /  Thursday 23rd July 2026
    (re.compile(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + _MONTH_RE + r")\.?\s+(\d{4})\b",
        re.I), "dmy_name"),
    # July 23, 2026  /  July 23 2026
    (re.compile(
        r"\b(" + _MONTH_RE + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b",
        re.I), "mdy_name"),
    # 2026-07-23
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "iso"),
    # 23/07/2026 or 23-07-2026 (UK order: DD/MM/YYYY)
    (re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b"), "dmy_num"),
]


def _norm(y, m, d):
    """Validate and return an ISO date string, or None if not a real date."""
    try:
        y, m, d = int(y), int(m), int(d)
        if not (1 <= m <= 12 and 1 <= d <= 31 and 2000 <= y <= 2100):
            return None
        # cheap day-of-month sanity without importing calendar edge cases
        import datetime
        return datetime.date(y, m, d).isoformat()
    except (ValueError, TypeError):
        return None


def _parse(kind, groups):
    if kind == "dmy_name":
        d, mon, y = groups
        return _norm(y, _MONTHS[mon.lower().rstrip(".")], d)
    if kind == "mdy_name":
        mon, d, y = groups
        return _norm(y, _MONTHS[mon.lower().rstrip(".")], d)
    if kind == "iso":
        y, m, d = groups
        return _norm(y, m, d)
    if kind == "dmy_num":
        d, m, y = groups            # NHS pages are DD/MM/YYYY
        return _norm(y, m, d)
    return None


def find_dates(text):
    """Every date literally present in `text`, ISO-normalised, de-duped in order."""
    seen = set()
    out = []
    for rx, kind in _DATE_PATTERNS:
        for m in rx.finditer(text):
            iso = _parse(kind, m.groups())
            if not iso or iso in seen:
                continue
            seen.add(iso)
            start = max(0, m.start() - 60)
            ctx = re.sub(r"\s+", " ", text[start:m.end() + 60]).strip()
            out.append({"iso": iso, "raw": m.group(0), "context": ctx})
    return sorted(out, key=lambda r: r["iso"])


_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)
_ANCHOR_RE = re.compile(
    r'<a\b[^>]*?href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.I | re.S)


def _visible_text(html):
    html = _SCRIPT_STYLE_RE.sub(" ", html)
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", html))


def _clean(s):
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", s)).strip()


def _is_doc(href):
    low = href.lower().split("?")[0].split("#")[0]
    return any(low.endswith(ext) for ext in DOC_EXTS)


def find_pdf_links(html, base_url):
    """Every document link in the HTML, absolute URL, in document order."""
    out = []
    seen = set()
    for m in _ANCHOR_RE.finditer(html):
        href, inner = m.group(1), m.group(2)
        if not _is_doc(href):
            continue
        url = urljoin(base_url, href.strip())
        if url in seen:
            continue
        seen.add(url)
        ext = url.lower().split("?")[0].rsplit(".", 1)[-1]
        start = max(0, m.start() - 140)
        out.append({
            "url": url,
            "text": _clean(inner),
            "kind": "pdf" if ext == "pdf" else ext,
            "context": _clean(html[start:m.start()])[-140:],
        })
    return out


def find_rows(html, base_url):
    """
    Table-row pairing: for each <tr>, the dates and document links inside it.
    This is what lets the skill match '23 July 2026' to its papers link (or to a
    'Currently unavailable' cell) even when rows are out of chronological order.
    Rows with neither a date nor a link are dropped as noise.
    """
    rows = []
    for m in _ROW_RE.finditer(html):
        cell_html = m.group(1)
        text = _clean(cell_html)
        dates = [d["iso"] for d in find_dates(text)]
        links = [{"url": l["url"], "text": l["text"]}
                 for l in find_pdf_links(cell_html, base_url)]
        if dates or links:
            rows.append({"text": text, "dates": dates, "pdf_links": links})
    return rows


def fetch_html(url, use_playwright=False):
    if not use_playwright:
        try:
            import urllib.request
            req = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT,
                              "Accept": "text/html,application/xhtml+xml,*/*"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            enc = "utf-8"
            ctype = r.headers.get("Content-Type", "")
            m = re.search(r"charset=([\w-]+)", ctype)
            if m:
                enc = m.group(1)
            return raw.decode(enc, errors="replace"), "requests"
        except Exception as e:
            print(f"requests fetch failed ({e}) — retrying with Playwright",
                  file=sys.stderr)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fetch_with_playwright import render
    return render(url, mode="html", timeout=45), "playwright"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--playwright", action="store_true",
                    help="Force the browser fetch (skip requests)")
    ap.add_argument("--html-file",
                    help="Parse this already-fetched HTML file instead of fetching")
    ap.add_argument("--base-url",
                    help="Base URL for resolving relative links (default: url)")
    ap.add_argument("--pretty", action="store_true", help="Indent the JSON")
    args = ap.parse_args()

    base = args.base_url or args.url

    if args.html_file:
        html = Path(args.html_file).read_text(encoding="utf-8", errors="replace")
        via = "html-file"
    else:
        try:
            html, via = fetch_html(args.url, use_playwright=args.playwright)
        except Exception as e:
            print(json.dumps({"source_url": args.url, "error": str(e),
                              "pdf_links": [], "dates": [], "rows": []}))
            return 1

    result = {
        "source_url": args.url,
        "fetched_via": via,
        "pdf_links": find_pdf_links(html, base),
        "dates": find_dates(_visible_text(html)),
        "rows": find_rows(html, base),
    }
    sys.stdout.write(json.dumps(result, indent=2 if args.pretty else None,
                               ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

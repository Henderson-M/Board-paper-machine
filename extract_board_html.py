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

# NHS CMS "download handler" URLs serve a document with NO file extension, e.g.
#   /download-attachment/55670   (NEL ICB)
#   /download_file/view/5110/785 (CLCH)
#   /download_file/<uuid>/258    (CNTW)
#   /seecmsfile/?id=8713         (York & Scarborough)
#   /download/july-2026.pdf      (Homerton — also caught by extension)
# Missing these caused real packs to be dropped on the 2026-07-23 run (WebFetch
# happened to catch them; the extractor did not). Match on the path only.
_DOWNLOAD_HANDLER_RE = re.compile(
    r"/(?:download[-_]?attachment|download[-_]?file|downloadfile"
    r"|seecmsfile|getfile|servefile|attachment)\b|/download/",
    re.I)

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


# A bare "day month" carrying no year of its own (the "7 October" in
# "board dates 2026: 5 August, 7 October, 2 December").
_BARE_DM = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)?\s+(" + _MONTH_RE + r")\.?\b(?!\.?\s*,?\s*\d{4})",
    re.I)
# An EXPLICIT year "list head": a year introducing a run of dates, either
# "2026:" / "2026 –" or "board dates 2026" / "meetings 2026". We ONLY inherit a
# year from a head like this — never from an arbitrary nearby 4-digit number
# (a copyright line, an awards year, etc.), because that guesses. Pages that
# simply list year-less dates (e.g. BSMHFT/RXT) are left to the date-scan step,
# which resolves the year with real context rather than a coincidence.
_YEAR_HEAD = re.compile(
    r"(?:meetings?|dates?|schedule|programme|calendar)\s+(20\d\d)\b"
    r"|\b(20\d\d)\s*[:–—]",
    re.I)


def find_dates(text):
    """Every date literally present in `text`, ISO-normalised, de-duped in order.

    Two passes: (1) dates that carry their own year; (2) bare "day month" tokens
    that follow an explicit year "list head" such as "board dates 2026: 5 August,
    7 October, 2 December" (flagged year_inferred=True). Pass 2 deliberately does
    NOT infer a year from a stray nearby number — only from a real list head — so
    it recovers dropped schedules without ever guessing.
    """
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
            out.append({"iso": iso, "raw": m.group(0), "context": ctx,
                        "year_inferred": False})
    # Pass 2 — bare day-months following an explicit year list head. Consume the
    # run up to the next 4-digit year (a new head) or 300 chars, whichever first.
    for hm in _YEAR_HEAD.finditer(text):
        year = hm.group(1) or hm.group(2)
        chunk_start = hm.end()
        nxt = re.search(r"\b20\d\d\b", text[chunk_start:])
        chunk_end = chunk_start + (nxt.start() if nxt else 300)
        for m in _BARE_DM.finditer(text[chunk_start:chunk_end]):
            iso = _norm(year, _MONTHS[m.group(2).lower().rstrip(".")], m.group(1))
            if not iso or iso in seen:
                continue
            seen.add(iso)
            abs_start = chunk_start + m.start()
            ctx = re.sub(r"\s+", " ", text[max(0, abs_start - 60):abs_start + m.end() - m.start() + 20]).strip()
            out.append({"iso": iso, "raw": m.group(0), "context": ctx,
                        "year_inferred": True})
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
    low = href.lower().split("#")[0]
    path = low.split("?")[0]
    if any(path.endswith(ext) for ext in DOC_EXTS):
        return True
    return bool(_DOWNLOAD_HANDLER_RE.search(path))


def _link_kind(url):
    path = url.lower().split("?")[0].split("#")[0]
    if path.endswith(".pdf"):
        return "pdf"
    last = path.rsplit("/", 1)[-1]
    if "." in last:
        return last.rsplit(".", 1)[-1]
    return "download"  # extension-less handler URL


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
        start = max(0, m.start() - 140)
        out.append({
            "url": url,
            "text": _clean(inner),
            "kind": _link_kind(url),
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
                              "Accept": "text/html,application/xhtml+xml,*/*",
                              "Accept-Encoding": "gzip, deflate"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            # Some NHS sites (e.g. southwestyorkshire.nhs.uk) return gzip even
            # when it wasn't requested. urllib does NOT auto-decompress, so
            # without this the body decodes to mojibake containing no hrefs and
            # no dates — the extractor then reports 0 links with no error, which
            # silently defeats the anti-omission cross-check it exists to provide.
            cenc = (r.headers.get("Content-Encoding") or "").lower()
            if cenc == "gzip" or raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)
            elif cenc == "deflate":
                import zlib
                try:
                    raw = zlib.decompress(raw)
                except zlib.error:
                    raw = zlib.decompress(raw, -zlib.MAX_WBITS)
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

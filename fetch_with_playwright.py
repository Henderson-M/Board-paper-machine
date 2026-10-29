#!/usr/bin/env python3
"""
fetch_with_playwright.py — render a URL with headless Chromium so we can
                          extract content from JS pages and bypass simple
                          UA/Cloudflare blocks that WebFetch hits.

Used by /scan-boards as a fallback when WebFetch returns 403, needs_js,
or empty content.

Two modes:
  --text       Print the rendered page text to stdout (default).
  --html       Print the rendered HTML to stdout.
  --download   Treat the URL as a file (e.g. PDF); save bytes to --out.

--headed opens a VISIBLE Chrome window instead of headless (real installed
Chrome preferred over bundled Chromium). Henry approved visible windows on
operator machines (2026-10-29), for his runs and Dave's alike — the window
opens and closes by itself; the operator just shouldn't be surprised by it.
Only use it after headless has failed.

Known limitation: GSTT (RJ1) still serves "Access forbidden" on its whole
/about-us/our-board section even to a headed real Chrome (tested 2026-10-29),
while the rest of the site renders — so --headed does NOT fix RJ1. Do not
escalate beyond this (no referrer spoofing / cookie click-through); ask the
operator to open the page in their own browser instead.

Usage:
    python fetch_with_playwright.py URL [--text|--html|--download] [--out FILE] [--timeout SEC] [--headed]
"""
import argparse
import sys
from pathlib import Path

# --- Encoding guard (added 2026-07-21) -------------------------------------
# Windows consoles default to cp1252. NHS board pages routinely contain curly
# apostrophes, en/em dashes and arrows, which cp1252 cannot encode. Without
# this, the fetch SUCCEEDS and then the *write* to stdout raises
# UnicodeEncodeError — leaving a 0-byte or traceback-only output file. Callers
# read that as "empty page" and report the site as dead, so a working trust
# looks like a broken one. Reported independently by 8+ scan workers on the
# 2026-07-20 run; one batch had a third of its orgs silently zeroed.
#
# If this ever needs reverting, the interim workaround is to set
# PYTHONIOENCODING=utf-8 in the environment before invoking the script.
# See DATA_QUALITY_2026-07-20.md section 1.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass  # older Python, or a stream that does not support reconfigure
# ---------------------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def render(url, *, mode="text", out_path=None, timeout=30, headed=False):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        launch_kwargs = dict(
            headless=not headed,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        if headed:
            # Headed implies a WAF that profiles the browser build itself, so
            # prefer the real installed Chrome over bundled Chromium — several
            # WAFs pass the former and block the latter. Fall back silently if
            # no system Chrome is installed.
            try:
                browser = p.chromium.launch(channel="chrome", **launch_kwargs)
            except Exception:
                browser = p.chromium.launch(**launch_kwargs)
        else:
            browser = p.chromium.launch(**launch_kwargs)
        ctx = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="en-GB",
            timezone_id="Europe/London",
            extra_http_headers={
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        # Light stealth: remove navigator.webdriver
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        page = ctx.new_page()

        if mode == "download":
            # Use request context to fetch raw bytes
            resp = ctx.request.get(url, timeout=timeout * 1000)
            if not resp.ok:
                browser.close()
                raise RuntimeError(f"HTTP {resp.status} fetching {url}")
            data = resp.body()
            Path(out_path).write_bytes(data)
            browser.close()
            return f"saved {len(data)} bytes to {out_path}"

        page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
        # Give JS a moment to finish rendering
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        if mode == "html":
            content = page.content()
        else:
            # Extract visible text. Use innerText on body which respects CSS visibility.
            content = page.evaluate("() => document.body.innerText")

        browser.close()
        return content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--text", action="store_true", help="Print visible text (default)")
    g.add_argument("--html", action="store_true", help="Print full rendered HTML")
    g.add_argument("--download", action="store_true", help="Download bytes (use --out)")
    ap.add_argument("--out", help="Output file for --download")
    ap.add_argument("--timeout", type=int, default=30, help="Seconds")
    ap.add_argument(
        "--headed",
        action="store_true",
        help="Open a visible Chrome window (for WAFs that block headless, e.g. GSTT)",
    )
    args = ap.parse_args()

    mode = "html" if args.html else "download" if args.download else "text"
    if mode == "download" and not args.out:
        print("--download requires --out", file=sys.stderr)
        return 2

    try:
        result = render(
            args.url, mode=mode, out_path=args.out, timeout=args.timeout, headed=args.headed
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if mode == "download":
        print(result)
    else:
        sys.stdout.write(result or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())

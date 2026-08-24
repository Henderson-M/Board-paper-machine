#!/usr/bin/env python
"""Probe and correct the URLs the sweep reads, without guessing.

Why this exists
---------------
`org_health.py` could only ever *report* a broken org. Nothing acted on the report, and
there was no safe way to correct a URL: the only route was hand-editing
`data/trust_urls.json` and hoping. So Alder Hey served a 2017 archive for six consecutive
runs, and Cheshire and Wirral sat on the broken list for six runs while its page in fact
read perfectly — nothing had ever re-probed it properly.

Two things follow from that, and this module does both:

1. **Probe with the FULL ladder before judging.** A single `requests` fetch returning
   nothing is not evidence the org is broken. On 2026-08-24 three orgs were recorded as
   `blocked` off the back of one 403; all three read fine under Playwright and simply
   publish no forward schedule. `probe()` runs requests -> Playwright -> landing-page
   follow, and only then decides.

2. **Validate before writing.** `set` refuses to store a URL that does not actually yield
   board dates or documents, so a correction cannot quietly make things worse. A wrong URL
   and a right one look identical in a data file until the next sweep.

Usage
-----
  python org_urls.py probe   --ods RBS                    # what does the current URL give?
  python org_urls.py probe   --ods RBS --url https://...  # would this candidate be better?
  python org_urls.py set     --ods RBS --url https://...  # validate, then write + clear health
  python org_urls.py recheck                              # re-probe every broken/degraded org
"""
import argparse
import datetime
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = ("data/trust_urls.json", "data/icb_urls.json")
FIELDS = ("url", "schedule_url", "papers_url")

# Verdicts, worst to best.
DEAD = "dead"                    # nothing readable by any fetcher
BLOCKED = "blocked"              # readable-ish but no usable content, host is fighting us
EMPTY = "empty"                  # page reads, but no dates and no documents at all
STALE = "stale_content"          # reads, has content, but nothing newer than STALE_MONTHS
NO_SCHEDULE = "ok_no_schedule"   # reads fine, publishes documents but no FUTURE dates
OK = "ok_schedule"               # reads fine and publishes future board dates
GOOD = (OK, NO_SCHEDULE)

STALE_MONTHS = 8


def _load(p):
    return json.load(io.open(os.path.join(HERE, p), encoding="utf-8"))


def find_org(ods):
    for f in DATA_FILES:
        recs = _load(f)
        for o in recs:
            if o.get("ods_code", "").upper() == ods.upper():
                return f, recs, o
    return None, None, None


def _extract(url, playwright=False, follow=0):
    cmd = [sys.executable, "extract_board_html.py", url]
    if playwright:
        cmd.append("--playwright")
    if follow:
        cmd += ["--follow-landing", str(follow)]
    try:
        r = subprocess.run(cmd, cwd=HERE, capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    out = (r.stdout or b"").decode("utf-8", "replace").strip()
    if not out.startswith("{"):
        return None
    try:
        return json.loads(out)
    except ValueError:
        return None


def probe(url, today=None, follow=10):
    """Run the full fetch ladder against a URL and return a verdict dict.

    This is the same ladder the sweep is supposed to use. Recording health off anything
    less is what produced six runs of false 'broken' at Cheshire and Wirral.
    """
    today = today or datetime.date.today()
    horizon = today + datetime.timedelta(days=548)
    steps = []
    best = None
    for label, kw in (("requests", {}),
                      ("playwright", {"playwright": True}),
                      ("playwright+landing", {"playwright": True, "follow": follow})):
        d = _extract(url, **kw)
        if d is None:
            steps.append("%s: no output" % label)
            continue
        docs = len(d.get("pdf_links") or [])
        isos = sorted({e.get("iso") for e in (d.get("dates") or []) if e.get("iso")})
        steps.append("%s: %d docs, %d dates" % (label, docs, len(isos)))
        if best is None or (docs + len(isos)) > (best["docs"] + len(best["dates"])):
            best = {"via": d.get("fetched_via", label), "docs": docs, "dates": isos,
                    "landing": len(d.get("landing_links") or [])}
        # Stop early once we have a forward schedule; no need to escalate further.
        if isos and any(today.isoformat() <= x <= horizon.isoformat() for x in isos):
            break

    if best is None:
        return {"verdict": DEAD, "url": url, "steps": steps,
                "detail": "no fetcher returned parseable output"}

    future = [x for x in best["dates"] if today.isoformat() <= x <= horizon.isoformat()]
    newest = best["dates"][-1] if best["dates"] else None
    cutoff = (today - datetime.timedelta(days=30 * STALE_MONTHS)).isoformat()

    if future:
        v, detail = OK, "%d future date(s), earliest %s" % (len(future), future[0])
    elif not best["dates"] and not best["docs"]:
        v, detail = (BLOCKED if best["landing"] == 0 else EMPTY), "no dates and no documents"
    elif newest and newest < cutoff:
        v, detail = STALE, ("nothing newer than %s — the page is an old archive, "
                            "which is a wrong-URL signal, not a fetch problem" % newest)
    else:
        v, detail = NO_SCHEDULE, ("reads fine; %d document(s), latest content %s, but no "
                                  "future dates — belongs on the papers watchlist, not the "
                                  "broken list" % (best["docs"], newest or "-"))
    return {"verdict": v, "url": url, "via": best["via"], "documents": best["docs"],
            "future_dates": future[:6], "newest_content": newest,
            "steps": steps, "detail": detail}


def apply_health(ods, p, now=None):
    """Translate a probe verdict into an org_health record."""
    sys.path.insert(0, HERE)
    import org_health as oh
    v = p["verdict"]
    if v == OK:
        return oh.record(ods, "ok", dates=len(p.get("future_dates") or []), now=now)
    if v == NO_SCHEDULE:
        return oh.record(ods, "ok", kind="no_schedule_published", now=now)
    kind = {DEAD: "unreachable", BLOCKED: "blocked",
            EMPTY: "no_dates_found", STALE: "stale_url"}.get(v, "other")
    return oh.record(ods, "fail", kind=kind, detail=p.get("detail"), now=now)


def cmd_probe(a):
    ods = a.ods.upper()
    _, _, o = find_org(ods)
    if o is None and not a.url:
        print("unknown ods_code %s (and no --url given)" % ods)
        return 2
    url = a.url or o.get(a.field) or o.get("schedule_url") or o.get("url")
    if not url:
        print("%s has no %s to probe" % (ods, a.field))
        return 2
    p = probe(url)
    print("%s  %s" % (ods, (o.get("names") or [ods])[0] if o else ""))
    print("  url     : %s" % url)
    print("  verdict : %s" % p["verdict"])
    print("  detail  : %s" % p["detail"])
    for s in p["steps"]:
        print("    ladder: %s" % s)
    if p.get("future_dates"):
        print("  future  : %s" % ", ".join(p["future_dates"]))
    if a.write and o is not None:
        apply_health(ods, p)
        print("  health record updated")
    return 0


def cmd_set(a):
    ods = a.ods.upper()
    f, recs, o = find_org(ods)
    if o is None:
        print("unknown ods_code %s" % ods)
        return 2
    old = o.get(a.field)
    if old == a.url:
        print("%s.%s already set to that URL" % (ods, a.field))
        return 0

    print("probing candidate before writing anything...")
    p = probe(a.url)
    print("  verdict : %s" % p["verdict"])
    print("  detail  : %s" % p["detail"])
    for s in p["steps"]:
        print("    ladder: %s" % s)

    if p["verdict"] not in GOOD and not a.force:
        print("")
        print("REFUSED — this URL does not yield board dates or documents, so storing it "
              "would replace one broken URL with another. Re-run with --force only if you "
              "know better than the probe.")
        return 1

    if a.compare and old:
        print("")
        print("probing the CURRENT url for comparison...")
        cur = probe(old)
        print("  current verdict: %s (%s)" % (cur["verdict"], cur["detail"]))
        rank = {DEAD: 0, BLOCKED: 1, EMPTY: 2, STALE: 3, NO_SCHEDULE: 4, OK: 5}
        if rank.get(p["verdict"], 0) < rank.get(cur["verdict"], 0) and not a.force:
            print("")
            print("REFUSED — the candidate is WORSE than what is already stored. "
                  "Use --force to override.")
            return 1

    o[a.field] = a.url
    stamp = datetime.date.today().isoformat()
    note = "[%s] %s set to %s (probe: %s). Previous: %s" % (
        stamp, a.field, a.url, p["verdict"], old or "none")
    o["notes"] = (note + " | " + (o.get("notes") or "")).strip(" |")
    json.dump(recs, io.open(os.path.join(HERE, f), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("")
    print("WROTE %s.%s -> %s   (%s)" % (ods, a.field, a.url, f))
    apply_health(ods, p)
    print("health record updated from the probe (no longer stuck on the old failure)")
    return 0


def cmd_recheck(a):
    sys.path.insert(0, HERE)
    import org_health as oh
    h = oh.load()
    want = set(x.strip() for x in a.status.split(","))
    todo = [r for r in h["orgs"].values() if r.get("status") in want]
    if a.ods:
        todo = [r for r in todo if r["ods_code"] in set(x.upper() for x in a.ods.split(","))]
    print("re-probing %d org(s) with status in %s" % (len(todo), sorted(want)))
    changed = []
    for r in sorted(todo, key=lambda x: x["ods_code"]):
        ods = r["ods_code"]
        _, _, o = find_org(ods)
        if o is None:
            continue
        url = o.get("schedule_url") or o.get("url")
        p = probe(url)
        was = r.get("status")
        print("  %-7s %-11s -> %-14s %s" % (ods, was, p["verdict"], p["detail"][:64]))
        if a.write:
            new = apply_health(ods, p)
            if new["status"] != was:
                changed.append((ods, was, new["status"], p["verdict"]))
    if a.write and changed:
        print("")
        print("STATUS CHANGED:")
        for ods, was, now, v in changed:
            print("  %-7s %s -> %s   (%s)" % (ods, was, now, v))
    elif not a.write:
        print("")
        print("(dry run — pass --write to update the health records)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("probe", help="run the full fetch ladder against an org's URL")
    p1.add_argument("--ods", required=True)
    p1.add_argument("--url", help="probe this candidate instead of the stored URL")
    p1.add_argument("--field", default="url", choices=FIELDS)
    p1.add_argument("--write", action="store_true", help="update the health record too")
    p1.set_defaults(fn=cmd_probe)

    p2 = sub.add_parser("set", help="validate a URL, then store it and clear the health record")
    p2.add_argument("--ods", required=True)
    p2.add_argument("--url", required=True)
    p2.add_argument("--field", default="url", choices=FIELDS)
    p2.add_argument("--compare", action="store_true",
                    help="also probe the stored URL and refuse a downgrade")
    p2.add_argument("--force", action="store_true", help="write even if the probe objects")
    p2.set_defaults(fn=cmd_set)

    p3 = sub.add_parser("recheck", help="re-probe every flagged org with the full ladder")
    p3.add_argument("--status", default="broken,degraded")
    p3.add_argument("--ods", help="limit to these ods_codes")
    p3.add_argument("--write", action="store_true")
    p3.set_defaults(fn=cmd_recheck)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""Track per-org scan health so persistent failures escalate instead of scrolling past.

The old `_scan_errors` list in state/meetings.json was append-only: no notion of whether a
failure had been fixed, no count of how long an org had been broken, and nothing that made a
three-month-old breakage look different from a one-off blip. It also stopped being written
reliably (last entry 2026-08-06, while later runs hit failures and recorded nothing).

This module keeps `state/org_health.json` - one record per org - and answers the only
questions that matter operationally:

  * which orgs failed THIS run
  * which have now failed enough times in a row to be considered broken
  * which have not been successfully scanned for a long time
  * which recovered since last run (so they stop being reported)

Usage
-----
  # during a run, after each org is scanned:
  python org_health.py record --ods RXA --result fail --kind unreachable \
      --detail "HTTP 403 via WebFetch and 0 links via requests"
  python org_health.py record --ods RA2 --result ok --dates 6

  # at the end of a run:
  python org_health.py report                 # human-readable operator report
  python org_health.py report --json          # same data as JSON
  python org_health.py report --markdown      # for pasting into the operator email
"""
import argparse, datetime, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "state", "org_health.json")

BROKEN_AFTER = 3          # consecutive failed runs before an org is called broken
STALE_DAYS = 28           # no successful scan in this long = needs attention
KINDS = ["unreachable", "blocked", "no_dates_found", "unparseable", "stale_url",
         "no_schedule_published", "other"]


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    if not os.path.exists(PATH):
        return {"_format_version": 1,
                "_description": "Per-org scan health. Written by org_health.py; read by "
                                "scan-boards Step 12b and the operator report in Step 13.",
                "orgs": {}}
    return json.load(io.open(PATH, encoding="utf-8"))


def save(h):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    json.dump(h, io.open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def record(ods, result, kind=None, detail=None, dates=None, now=None):
    """result: 'ok' | 'fail'. 'no schedule published' is an OK outcome, not a failure."""
    now = now or _now()
    h = load()
    r = h["orgs"].setdefault(ods, {
        "ods_code": ods, "last_attempt": None, "last_success": None,
        "consecutive_failures": 0, "first_failed": None, "last_error": None,
        "failure_kind": None, "status": "ok", "muted_until": None, "runs_seen": 0})
    r["last_attempt"] = now
    r["runs_seen"] = r.get("runs_seen", 0) + 1
    if result == "ok":
        r["last_success"] = now
        r["consecutive_failures"] = 0
        r["first_failed"] = None
        r["last_error"] = None
        r["failure_kind"] = kind if kind == "no_schedule_published" else None
        r["dates_found"] = dates
        r["status"] = "ok"
    else:
        r["consecutive_failures"] = r.get("consecutive_failures", 0) + 1
        r["first_failed"] = r.get("first_failed") or now
        r["last_error"] = (detail or "")[:400]
        r["failure_kind"] = kind or "other"
        r["status"] = "broken" if r["consecutive_failures"] >= BROKEN_AFTER else "degraded"
    save(h)
    return r


def _age_days(ts, today=None):
    if not ts:
        return None
    try:
        d = datetime.datetime.strptime(ts[:10], "%Y-%m-%d").date()
    except Exception:
        return None
    return ((today or datetime.date.today()) - d).days


def in_scope_codes():
    """Every org the sweep is supposed to cover: has a URL and a real correspondent."""
    out = set()
    for f in ("data/trust_urls.json", "data/icb_urls.json"):
        fp = os.path.join(HERE, f)
        if not os.path.exists(fp):
            continue
        for o in json.load(io.open(fp, encoding="utf-8")):
            c = o.get("correspondent")
            if (o.get("schedule_url") or o.get("url")) and c and c != "TBC":
                out.add(o["ods_code"])
    return out


def analyse(today=None, since=None):
    """since: ISO timestamp marking the start of this run. Any in-scope org whose
    last_attempt predates it was NOT CHECKED this run - which matters just as much as
    a failure, and is invisible unless something looks for it."""
    h = load()
    orgs = list(h["orgs"].values())
    today = today or datetime.date.today()
    broken, degraded, stale, muted = [], [], [], []
    for r in orgs:
        if r.get("muted_until") and r["muted_until"] >= str(today):
            muted.append(r); continue
        if r.get("status") == "broken":
            broken.append(r)
            continue
        if r.get("status") == "degraded":
            degraded.append(r)
            continue
        # only orgs that are NOT already reported above can be "stale"
        age = _age_days(r.get("last_success"), today)
        if age is None or age > STALE_DAYS:
            stale.append(r)
    unchecked = []
    if since:
        seen = {r["ods_code"]: r for r in orgs}
        for code in sorted(in_scope_codes()):
            r = seen.get(code)
            if r is None:
                unchecked.append({"ods_code": code, "last_attempt": None,
                                  "reason": "never tracked - no outcome has ever been recorded"})
            elif not r.get("last_attempt") or r["last_attempt"] < since:
                unchecked.append({"ods_code": code, "last_attempt": r.get("last_attempt"),
                                  "reason": "in scope but no outcome recorded this run"})
    key = lambda r: (-(r.get("consecutive_failures") or 0), r["ods_code"])
    return {"broken": sorted(broken, key=key), "degraded": sorted(degraded, key=key),
            "stale": sorted(stale, key=lambda r: r["ods_code"]),
            "unchecked": unchecked, "muted": muted, "total": len(orgs)}


def _names():
    out = {}
    for f in ("data/trust_urls.json", "data/icb_urls.json"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            for o in json.load(io.open(p, encoding="utf-8")):
                out[o["ods_code"]] = ((o.get("names") or [o["ods_code"]])[0],
                                      o.get("correspondent") or "-",
                                      o.get("schedule_url") or o.get("url") or "")
    return out


def report(fmt="text", today=None, since=None):
    a = analyse(today, since)
    nm = _names()
    L = []
    add = L.append
    tot = a["total"]
    hdr = "SCAN HEALTH — %d broken, %d degraded, %d stale, %d not checked (of %d orgs tracked)" % (
        len(a["broken"]), len(a["degraded"]), len(a["stale"]), len(a.get("unchecked") or []), tot)
    if fmt == "markdown":
        add("## " + hdr); add("")
    else:
        add(hdr); add("=" * len(hdr))
    if not (a["broken"] or a["degraded"] or a["stale"] or a.get("unchecked")):
        add("Nothing needs attention — every in-scope org was checked and scanned cleanly.")
        return "\n".join(L)

    def block(title, rows, why):
        if not rows:
            return
        add("")
        add(("### " + title) if fmt == "markdown" else title)
        add(why)
        add("")
        if fmt == "markdown":
            add("| Org | ODS | Correspondent | Failed runs | Since | Problem |")
            add("|---|---|---|---|---|---|")
        for r in rows:
            n, corr, url = nm.get(r["ods_code"], (r["ods_code"], "-", ""))
            since = (r.get("first_failed") or "")[:10] or "-"
            det = (r.get("last_error") or r.get("failure_kind") or "")[:90]
            if fmt == "markdown":
                add("| %s | %s | %s | %s | %s | %s |" % (n[:44], r["ods_code"], corr,
                                                         r.get("consecutive_failures", 0), since, det))
            else:
                add("  %-7s %-42s %-14s x%-2s since %s" % (
                    r["ods_code"], n[:42], corr, r.get("consecutive_failures", 0), since))
                add("          %s" % det)
                if url:
                    add("          %s" % url)

    block("BROKEN — failed %d+ runs running" % BROKEN_AFTER, a["broken"],
          "These need a human. They have failed every run for a while and are silently "
          "contributing nothing.")
    block("DEGRADED — failed this run", a["degraded"],
          "First or second consecutive failure. Often transient; watch rather than act.")
    block("STALE — no successful scan in %d+ days" % STALE_DAYS, a["stale"],
          "Not necessarily failing, but nothing has been confirmed from them in a long time.")
    unchecked = a.get("unchecked") or []
    if unchecked:
        add("")
        add(("### NOT CHECKED THIS RUN — %d org(s)" % len(unchecked)) if fmt == "markdown"
            else "NOT CHECKED THIS RUN — %d org(s)" % len(unchecked))
        add("In scope but no outcome was recorded. A skipped org is as invisible as a failed one.")
        add("")
        if fmt == "markdown":
            add("| Org | ODS | Correspondent | Last attempted | Why |")
            add("|---|---|---|---|---|")
        for r in unchecked:
            n, corr, url = nm.get(r["ods_code"], (r["ods_code"], "-", ""))
            la = (r.get("last_attempt") or "never")[:10]
            if fmt == "markdown":
                add("| %s | %s | %s | %s | %s |" % (n[:44], r["ods_code"], corr, la, r["reason"]))
            else:
                add("  %-7s %-42s %-14s last attempted %s" % (r["ods_code"], n[:42], corr, la))
    # An org that has failed repeatedly needs somebody to DO something, and until now the
    # report only ever described the problem. Alder Hey was reported as broken on six
    # consecutive runs and nothing happened, because nothing in the output said what to run
    # or asked for anything. Name the URL and the exact command.
    actionable = a["broken"] + a["degraded"]
    if actionable:
        add("")
        add(("### ACTION REQUIRED — %d org(s)" % len(actionable)) if fmt == "markdown"
            else "ACTION REQUIRED — %d org(s)" % len(actionable))
        add("Re-probe with the full fetch ladder first: a single failed fetch is not evidence "
            "an org is broken, and several orgs have sat on this list while their pages read "
            "perfectly under Playwright.")
        add("")
        add("    python org_urls.py recheck --write")
        add("")
        add("If a page really has moved, supply the replacement — it is validated before "
            "anything is written, so a wrong URL cannot quietly replace a broken one:")
        add("")
        for r in actionable:
            n, corr, url = nm.get(r["ods_code"], (r["ods_code"], "-", ""))
            add("    # %s (%s) — currently %s" % (n[:52], corr, url or "no URL stored"))
            add("    python org_urls.py set --ods %s --url <REPLACEMENT> --compare"
                % r["ods_code"])
        add("")
        add("`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is "
            "written unless the candidate actually yields board dates or documents.")
    if a["muted"]:
        add("")
        add("(%d org(s) muted and not reported)" % len(a["muted"]))
    return "\n".join(L)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--ods", required=True)
    r.add_argument("--result", required=True, choices=["ok", "fail"])
    r.add_argument("--kind", choices=KINDS)
    r.add_argument("--detail")
    r.add_argument("--dates", type=int)
    r.add_argument("--now")
    q = sub.add_parser("report")
    q.add_argument("--json", action="store_true")
    q.add_argument("--markdown", action="store_true")
    q.add_argument("--since", help="ISO timestamp for the start of this run. Any in-scope org "
                                   "with no outcome recorded since then is reported as NOT CHECKED.")
    m = sub.add_parser("mute")
    m.add_argument("--ods", required=True)
    m.add_argument("--until", required=True, help="YYYY-MM-DD")
    a = p.parse_args()
    if a.cmd == "record":
        out = record(a.ods, a.result, a.kind, a.detail, a.dates, a.now)
        print(json.dumps(out, ensure_ascii=False))
    elif a.cmd == "mute":
        h = load()
        h["orgs"].setdefault(a.ods, {"ods_code": a.ods, "status": "ok",
                                     "consecutive_failures": 0})["muted_until"] = a.until
        save(h)
        print("muted %s until %s" % (a.ods, a.until))
    else:
        since = getattr(a, "since", None)
        if a.json:
            print(json.dumps(analyse(since=since), ensure_ascii=False, indent=1))
        else:
            sys.stdout.write(report("markdown" if a.markdown else "text", since=since) + "\n")


if __name__ == "__main__":
    main()

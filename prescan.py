#!/usr/bin/env python3
"""Deterministic pre-scan: read every in-scope org's board page with no model at all.

Why this exists
---------------
The expensive part of a sweep was never the reading, it was that every org got its own
LLM subagent to look at a page that `extract_board_html.py` can already parse literally.
On the 2026-09-14 run that was ~40 Opus agents and two session-limit hits.

This script runs the same deterministic extractor across all orgs in a thread pool and
sorts them into two piles:

  resolved     — the raw HTML literally contained dates and/or document links. The scan
                 agent does not need to visit this org at all.
  needs_agent  — empty, blocked, JS-rendered, or two-hop. These get an agent.

**An empty deterministic result is never treated as "no meetings".** That is the single
most important property here: it is the rule the skill already states twice (Step 4
anti-omission, Step 7 cross-check) and it is what stops a cheaper sweep becoming a
lossier one. Empty means *escalate*, so a page this script cannot read costs recall
nothing — it just falls through to the agent path exactly as it does today.

Run artefacts are written to a RUN-STAMPED directory and every artefact carries the
`run_id`. Nothing here ever writes to a fixed path that a later run could mistake for
its own — that is what went wrong on 2026-09-14, when agents read `batch_00..11.json`
left in `tmp_scan/` from 1 July and scanned a stale org list for ~62m tokens.

Usage
-----
    python prescan.py                        # full sweep, both trusts and ICBs
    python prescan.py --ods RY6,RHQ          # just these orgs
    python prescan.py --trusts-only
    python prescan.py --workers 12
    python prescan.py --purge-days 3         # also delete run dirs older than N days
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import shutil
import sys
import time
from pathlib import Path

import extract_board_html as ex

REPO = Path(__file__).resolve().parent
TMP = REPO / "tmp_scan"

# Bias every judgement here toward "send an agent". A false `needs_agent` costs one
# cheap subagent; a false `resolved` silently drops an org from the sweep.
REASON_FETCH_FAILED = "fetch_failed"
REASON_BLOCKED = "blocked"
REASON_EMPTY = "empty_or_js"
REASON_TWO_HOP = "two_hop_landing"
REASON_NO_URL = "no_url"
REASON_NO_FORWARD = "no_forward_schedule"
REASON_UNRESOLVED = "unresolved_schedule_dates"
REASON_INFERRED_ONLY = "year_inferred_only"

# A weekday-prefixed day-month with no year — "Thursday 24 September". On a board
# page that shape is almost always a schedule entry rather than prose, so if one
# appears and the extractor did NOT resolve it to a date, there is something on
# the page we cannot read and the org must go to an agent.
#
# This is the safety net that lets the pre-scan be trusted: it does not need to
# parse every calendar format correctly, it only needs to KNOW when it hasn't.
_SCHEDULE_DM = re.compile(
    r"\b(?:mon|tues|wednes|thurs|fri|satur|sun)day\s+"
    r"(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\b"
    r"(?!\.?\s*,?\s*\d{4})",
    re.I)
_MONTH_NUM = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


def unresolved_schedule_dates(text: str, resolved: list[dict]) -> list[str]:
    """Weekday-prefixed day-months on the page that no pass turned into a date."""
    have = {(dt.date.fromisoformat(d["iso"]).day, dt.date.fromisoformat(d["iso"]).month)
            for d in resolved if d.get("iso")}
    out = []
    for m in _SCHEDULE_DM.finditer(text):
        day = int(m.group(1))
        mon = _MONTH_NUM[m.group(2).lower()[:3]]
        if (day, mon) not in have:
            out.append(m.group(0))
    return out[:12]

# Matches the Step 4 "After extraction" validation: a date more than 18 months out is
# rejected there, so counting it as forward coverage here would be a false `resolved`.
FORWARD_MONTHS = 18


def forward_dates(dates: list[dict], today: dt.date | None = None) -> list[dict]:
    """Dates that would actually survive the skill's own validation.

    `find_dates` returns every date literally on the page, history included. A page
    showing nothing but 2020-2023 archives has no forward schedule, and treating that
    as "resolved" would silently drop the org from the date sweep — the exact class of
    invisible miss this whole change is meant to remove.
    """
    today = today or dt.date.today()
    horizon = today + dt.timedelta(days=int(FORWARD_MONTHS * 30.44))
    out = []
    for d in dates:
        iso = d.get("iso")
        if not iso:
            continue
        try:
            when = dt.date.fromisoformat(iso)
        except ValueError:
            continue
        if today <= when <= horizon:
            out.append(d)
    return out


def load_orgs(trusts: bool = True, icbs: bool = True) -> list[dict]:
    orgs: list[dict] = []
    files = []
    if trusts:
        files.append(("trust", REPO / "data" / "trust_urls.json"))
    if icbs:
        files.append(("icb", REPO / "data" / "icb_urls.json"))
    for org_type, fp in files:
        if not fp.exists():
            continue
        for o in json.loads(fp.read_text(encoding="utf-8")):
            o = dict(o)
            o.setdefault("org_type", org_type)
            orgs.append(o)
    return orgs


def scan_url_for(org: dict) -> str | None:
    """Step 2 of the skill: schedule_url wins for date detection, else url."""
    return (org.get("schedule_url") or org.get("url") or "").strip() or None


def scan_one(org: dict, timeout_note: str = "") -> dict:
    ods = (org.get("ods_code") or "").upper()
    name = (org.get("names") or [org.get("name") or ods])[0]
    url = scan_url_for(org)
    out = {
        "ods_code": ods,
        "org_name": name,
        "org_type": org.get("org_type"),
        "correspondent": org.get("correspondent"),
        "scan_url": url,
        "dates": [],
        "forward_dates": [],
        "pdf_links": [],
        "rows": [],
        "landing_links": [],
        "fetched_via": None,
        "status": "needs_agent",
        "reason": None,
        "error": None,
    }

    if not url:
        out["reason"] = REASON_NO_URL
        return out

    # Honour the per-org fetch_mode hint the repo already maintains, so a host known to
    # 403 the requests path doesn't burn a doomed attempt first.
    use_pw = (org.get("fetch_mode") or "").lower() == "playwright"

    try:
        html, via = ex.fetch_html(url, use_playwright=use_pw)
    except Exception as e:  # noqa: BLE001 - we want every failure shape recorded, not raised
        msg = str(e)
        out["error"] = msg[:300]
        out["reason"] = REASON_BLOCKED if "403" in msg or "Forbidden" in msg else REASON_FETCH_FAILED
        return out

    out["fetched_via"] = via
    try:
        out["pdf_links"] = ex.find_pdf_links(html, url)
        out["dates"] = ex.find_dates(ex._visible_text(html))
        out["rows"] = ex.find_rows(html, url)
        out["landing_links"] = ex.find_landing_links(html, url)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"parse: {str(e)[:280]}"
        out["reason"] = REASON_FETCH_FAILED
        return out

    out["forward_dates"] = forward_dates(out["dates"])
    out["unresolved_dm"] = unresolved_schedule_dates(ex._visible_text(html), out["dates"])

    # `status` is about the DATE scan (Step 4) only. Document links are reported either
    # way, because Step 7's pack detection consumes them per-meeting regardless.
    if out["forward_dates"]:
        # Safety net 1 — the page carries schedule-shaped dates we could not parse.
        # Finding SOME dates is not good enough: a page can list four meetings in a
        # format we read and two in one we don't, and the two would vanish silently.
        if out["unresolved_dm"]:
            out["reason"] = REASON_UNRESOLVED
            return out
        # Safety net 2 — every forward date came from year inference. The day and
        # month are literal, but the year is not, so let an agent confirm rather
        # than let a guess decide what gets into someone's calendar.
        if all(d.get("year_inferred") for d in out["forward_dates"]):
            out["reason"] = REASON_INFERRED_ONLY
            return out
        out["status"] = "resolved"
        return out

    # No forward dates. Which of the several reasons it is decides where the skill
    # routes the org, so keep them distinct rather than collapsing to "empty".
    if out["landing_links"]:
        out["reason"] = REASON_TWO_HOP
    elif out["dates"] or out["pdf_links"]:
        # The page read fine and has real content — it just lists no future meetings.
        # That is the watchlist case (Step 7b), not a broken scrape.
        out["reason"] = REASON_NO_FORWARD
    else:
        out["reason"] = REASON_EMPTY
    return out


def new_run_dir(stamp: str | None = None) -> tuple[str, Path]:
    stamp = stamp or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"run-{stamp}"
    d = TMP / run_id
    d.mkdir(parents=True, exist_ok=True)
    return run_id, d


def purge_old_runs(days: int) -> list[str]:
    """Delete run dirs older than `days`. Stale scratch is what caused the 14 Sep waste."""
    if days <= 0 or not TMP.exists():
        return []
    cutoff = time.time() - days * 86400
    gone = []
    for d in TMP.iterdir():
        if not d.is_dir() or not d.name.startswith("run-"):
            continue
        if d.stat().st_mtime < cutoff:
            shutil.rmtree(d, ignore_errors=True)
            gone.append(d.name)
    return gone


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ods", help="Comma-separated ODS codes to limit the sweep to")
    ap.add_argument("--trusts-only", action="store_true")
    ap.add_argument("--icbs-only", action="store_true")
    ap.add_argument("--workers", type=int, default=8,
                    help="Parallel fetches (default 8). These are HTTP fetches, not models.")
    ap.add_argument("--purge-days", type=int, default=3,
                    help="Delete tmp_scan run dirs older than this many days (default 3)")
    ap.add_argument("--stamp", help="Override the run stamp (testing/regression use)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    orgs = load_orgs(trusts=not args.icbs_only, icbs=not args.trusts_only)

    if args.ods:
        want = {c.strip().upper() for c in args.ods.split(",") if c.strip()}
        orgs = [o for o in orgs if (o.get("ods_code") or "").upper() in want]

    # Mirror the skill's Step 2 filter so the counts here mean the same thing as the run's.
    skipped_no_url = [o for o in orgs if not scan_url_for(o)]
    corr_skip = [o for o in orgs if (o.get("correspondent") in (None, "", "TBC"))]
    in_scope = [o for o in orgs
                if scan_url_for(o) and o.get("correspondent") not in (None, "", "TBC")]

    purged = purge_old_runs(args.purge_days)
    run_id, run_dir = new_run_dir(args.stamp)

    if not args.quiet:
        print(f"run_id={run_id}", file=sys.stderr)
        print(f"orgs in scope: {len(in_scope)} "
              f"(skipped {len(skipped_no_url)} no-url, {len(corr_skip)} no-correspondent)",
              file=sys.stderr)
        if purged:
            print(f"purged stale run dirs: {', '.join(purged)}", file=sys.stderr)

    results: list[dict] = []
    started = time.time()
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(scan_one, o): o for o in in_scope}
        done = 0
        for fut in cf.as_completed(futs):
            org = futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001 - a crash here must not lose the org
                results.append({
                    "ods_code": (org.get("ods_code") or "").upper(),
                    "org_name": (org.get("names") or [""])[0],
                    "scan_url": scan_url_for(org),
                    "status": "needs_agent",
                    "reason": REASON_FETCH_FAILED,
                    "error": str(e)[:300],
                    "dates": [], "forward_dates": [], "pdf_links": [], "unresolved_dm": [],
                    "rows": [], "landing_links": [],
                })
            done += 1
            if not args.quiet and done % 25 == 0:
                print(f"  {done}/{len(in_scope)}", file=sys.stderr)

    results.sort(key=lambda r: r["ods_code"])
    resolved = [r for r in results if r["status"] == "resolved"]
    needs = [r for r in results if r["status"] != "resolved"]

    by_reason: dict[str, int] = {}
    for r in needs:
        by_reason[r["reason"] or "?"] = by_reason.get(r["reason"] or "?", 0) + 1

    manifest = {
        "run_id": run_id,
        "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time() - started, 1),
        "orgs_in_scope": len(in_scope),
        "resolved": len(resolved),
        "needs_agent": len(needs),
        "needs_agent_by_reason": by_reason,
        "forward_dates_found": sum(len(r.get("forward_dates") or []) for r in results),
        "doc_links_found": sum(len(r.get("pdf_links") or []) for r in results),
        "skipped_no_url": len(skipped_no_url),
        "skipped_no_correspondent": len(corr_skip),
        "argv": sys.argv[1:],
    }

    enc = dict(encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), **enc)
    (run_dir / "prescan.json").write_text(
        json.dumps({"run_id": run_id, "results": results}, indent=2), **enc)
    (run_dir / "needs_agent.json").write_text(
        json.dumps({"run_id": run_id, "orgs": needs}, indent=2), **enc)

    if not args.quiet:
        print(f"\nresolved deterministically : {len(resolved)}", file=sys.stderr)
        print(f"need an agent              : {len(needs)}  {by_reason}", file=sys.stderr)
        print(f"\nartefacts: {run_dir}", file=sys.stderr)

    # stdout is the machine-readable handle the skill consumes.
    print(json.dumps({"run_id": run_id, "run_dir": str(run_dir), **manifest}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Merge the 2026-09-14 sweep's agent output into state/meetings.json.

Reads:
  C:\\tmp\\bpm914\\dout_*.json   - date-scan results (one list per batch)
  C:\\tmp\\bpm914\\salvaged.json - date results recovered from the mis-pathed first dispatch
  C:\\tmp\\bpm914\\pout_*.json   - pack-detection results

Writes nothing on its own unless --write is passed; prints the diff so it can be
eyeballed first.
"""
import json, os, glob, datetime, argparse, sys

REPO = os.path.dirname(os.path.abspath(__file__))
RES = r"C:\tmp\bpm914"
TODAY = datetime.date(2026, 9, 14)
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_date_results():
    """Every org object from every date batch, plus the salvaged set.
    Later files never overwrite an org already seen (salvaged loaded last, so
    a fresh scan of the same org wins)."""
    out, seen = {}, set()
    files = sorted(glob.glob(os.path.join(RES, "dout_*.json")))
    files.append(os.path.join(RES, "salvaged.json"))
    for f in files:
        if not os.path.exists(f):
            continue
        try:
            rows = jload(f)
        except Exception as e:
            print(f"  !! unreadable {f}: {e}")
            continue
        if isinstance(rows, dict):
            rows = rows.get("results") or []
        for o in rows:
            c = o.get("ods_code")
            if not c or c in seen:
                continue
            seen.add(c)
            out[c] = o
    return out


def load_pack_results():
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, "pout_*.json"))):
        try:
            rows = jload(f)
        except Exception as e:
            print(f"  !! unreadable {f}: {e}")
            continue
        if isinstance(rows, dict):
            if rows.get("error"):
                print(f"  !! {os.path.basename(f)} is an ERROR record: {rows.get('error')}")
                continue
            rows = rows.get("results") or []
        for m in rows:
            if m.get("id"):
                out[m["id"]] = m
    return out


def state_meetings(state):
    ms = state["meetings"] if isinstance(state, dict) and "meetings" in state else state
    if isinstance(ms, dict):
        return list(ms.values())
    return ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    dates = load_date_results()
    packs = load_pack_results()
    print(f"date results: {len(dates)} orgs | pack results: {len(packs)} meetings")

    state = jload(os.path.join(REPO, "state", "meetings.json"))
    ms = state_meetings(state)
    by_id = {m.get("id") or f"{m.get('ods_code')}:{m.get('date')}": m for m in ms}

    scope = {o["ods_code"]: o for o in jload(os.path.join(RES, "bpm_scope.json"))}

    new_meetings, updated = [], 0
    for ods, r in sorted(dates.items()):
        org = scope.get(ods) or {}
        for mt in r.get("meetings") or []:
            d = mt.get("date")
            if not d:
                continue
            try:
                dd = datetime.date.fromisoformat(d)
            except Exception:
                continue
            if dd < TODAY:
                continue
            mid = f"{ods}:{d}"
            if mid in by_id:
                by_id[mid]["last_checked"] = NOW
                updated += 1
                continue
            new_meetings.append({
                "id": mid, "ods_code": ods,
                "org_name": org.get("name") or r.get("name"),
                "org_type": org.get("org_type"),
                "date": d, "title": mt.get("title") or "Board meeting",
                "status": "date_found",
                "source_url": r.get("scan_url_used") or org.get("scan_url"),
                "papers_url": mt.get("papers_url"),
                "pack_files": [], "alerts_sent": {},
                "first_seen": NOW, "last_checked": NOW,
                "detected_method": r.get("method"),
            })

    print(f"\nNEW meeting dates: {len(new_meetings)}   (existing refreshed: {updated})")
    from collections import Counter
    print(Counter(m["ods_code"] for m in new_meetings).most_common(15))

    new_packs = []
    for mid, p in sorted(packs.items()):
        nf = p.get("new_pack_files") or []
        if not nf:
            continue
        new_packs.append(p)
    print(f"\nMeetings with NEW pack files: {len(new_packs)}")
    for p in new_packs:
        print(f"  {p['ods_code']} {p['date']}  {len(p['new_pack_files'])} file(s)  {p.get('org_name','')[:45]}")

    json.dump(new_meetings, open(os.path.join(RES, "new_meetings.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(new_packs, open(os.path.join(RES, "new_packs.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\nwrote {RES}\\new_meetings.json and new_packs.json")

    if a.write:
        for m in new_meetings:
            ms.append(m)
        for p in new_packs:
            m = by_id.get(p["id"])
            if not m:
                continue
            m.setdefault("pack_files", []).extend(p["new_pack_files"])
            m["status"] = "papers_found"
            m["papers_url"] = p.get("papers_url_used") or m.get("papers_url")
        if isinstance(state, dict) and "meetings" in state:
            state["meetings"] = ms
        else:
            state = ms
        with open(os.path.join(REPO, "state", "meetings.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, indent=1, ensure_ascii=False)
        print("state/meetings.json UPDATED")
    else:
        print("(dry run - pass --write to apply to state)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Compose a sweep's alert emails and send_batch manifests.

Papers alerts: one per analysed pack, per recipient, with the FULL summary
inlined in the body (Henry's preference, set 2026-06-05) and attached.
Date alerts: one per recipient, grouped by org, with a delta .ics of this
run's new meetings only.

Everything is read and written as UTF-8 no-BOM. PowerShell 5.1 defaults to
Windows-1252 and garbled a live send on 2026-07-30 - do not route these files
through Get-Content/Set-Content.
"""
import json, os, glob, re, datetime, argparse

REPO = os.path.dirname(os.path.abspath(__file__))
RES = os.environ.get("BPM_RESULTS") or os.path.join(REPO, "tmp_scan", "run-20260917-162940")
RUNDATE = os.environ.get("BPM_RUNDATE") or datetime.datetime.now().strftime("%Y%m%d")
NOW = datetime.datetime.now(datetime.timezone.utc)
STAMP = NOW.strftime("%Y%m%dT%H%M%SZ")


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def readtext(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def writetext(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def slug(name):
    """Slugified FULL correspondent key. Never key on first name - there are
    two Matts and both shorten to 'matt' (worked failure 2026-08-17)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def human(d):
    dt = datetime.date.fromisoformat(d)
    return dt.strftime("%A %d %B %Y").replace(" 0", " ")


def first_name(full):
    return full.split()[0]


def ics_esc(s):
    return str(s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def vevent(ods, date, org_name, title, src):
    d = datetime.date.fromisoformat(date)
    return "\r\n".join([
        "BEGIN:VEVENT",
        f"UID:{ods}-{date}@board-paper-machine.hsj",
        f"DTSTAMP:{NOW.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{(d + datetime.timedelta(days=1)).strftime('%Y%m%d')}",
        f"SUMMARY:{ics_esc(org_name + ' — ' + (title or 'Board meeting'))}",
        f"DESCRIPTION:Detected by Board paper machine. Source: {ics_esc(src)}",
        f"URL:{ics_esc(src)}",
        "END:VEVENT",
    ])


def wrap_ics(events):
    return "\r\n".join(
        ["BEGIN:VCALENDAR", "VERSION:2.0",
         "PRODID:-//HSJ//Board paper machine//EN", "CALSCALE:GREGORIAN"]
        + events + ["END:VCALENDAR"]) + "\r\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="build manifests for a live send")
    a = ap.parse_args()

    corr = jload(os.path.join(REPO, "data", "correspondents.json"))
    cmap = corr["correspondents"]
    fullnames = corr.get("_full_names", {})
    tasks = {t["analysis_id"]: t for t in jload(os.path.join(RES, "analysis_tasks.json"))}

    # ---- papers alerts -------------------------------------------------
    papers, missing = [], []
    for aid, t in sorted(tasks.items()):
        rpath = os.path.join(RES, "analysis", aid + ".json")
        if not os.path.exists(rpath):
            missing.append(aid)
            continue
        r = jload(rpath)
        spath = os.path.join(REPO, r.get("summary_path", f"summaries/{aid}.md"))
        if not os.path.exists(spath):
            missing.append(aid + " (no summary file)")
            continue
        summary = readtext(spath)
        nl, nw, nf = r.get("lead", 0), r.get("watch", 0), r.get("foi", 0)
        for rec in t["recipients"]:
            email = cmap.get(rec)
            if not email:
                print(f"  [skip] {rec}: no email")
                continue
            fn = first_name(fullnames.get(rec, rec))
            body = (
                f"Hi {fn},\n\n"
                f"New papers detected for {t['org_name']}'s board meeting on {human(t['date'])}.\n"
                f"The pack-analyser found {nl} LEAD / {nw} WORTH WATCHING / {nf} FOI items.\n\n"
                "Full summary below (also attached as markdown).\n\n"
                "---\n\n"
                f"{summary}\n\n"
                "---\n\n"
                f"Pack source: {t.get('papers_url')}\n\n"
                "— Board paper machine\n"
            )
            bf = os.path.join(REPO, "outbox", f"{RUNDATE}_{slug(rec)}_papers_{aid}.md")
            writetext(bf, body)
            papers.append({
                "id": f"papers:{aid}:{slug(rec)}",
                "to": email,
                "subject": f"[PAPERS] {t['org_name']} board — {human(t['date'])} — {nl} leads",
                "body_file": bf.replace("\\", "/"),
                "attach": [spath.replace("\\", "/")],
                "_meeting_ids": [t["lead_id"]] + t.get("shared_with", []),
            })

    # ---- date alerts ---------------------------------------------------
    newm = jload(os.path.join(RES, "new_meetings.json"))
    scope = {o["ods_code"]: o for o in jload(os.path.join(RES, "bpm_scope.json"))}
    ov = jload(os.path.join(REPO, "data", "recipient_overrides.json"))
    TODAY = datetime.date.today().isoformat()

    def recips(ods, kind):
        o = scope.get(ods) or {}
        names = []
        p = o.get("correspondent")
        if p and p != "TBC":
            names.append(p)
        for n in o.get("additional_correspondents") or []:
            if n and n != "TBC" and n not in names:
                names.append(n)
        for r in ov.get("overrides", []):
            if kind not in r.get("applies_to", []):
                continue
            if not (r.get("start", "") <= TODAY <= r.get("expires", "")):
                continue
            if r.get("when_recipient") in names:
                for n in r.get("add_recipients", []):
                    if n and n != "TBC" and n not in names:
                        names.append(n)
        return [n for n in names if cmap.get(n)]

    bydest = {}
    for m in newm:
        for rec in recips(m["ods_code"], "date"):
            bydest.setdefault(rec, []).append(m)

    dates = []
    for rec, ms in sorted(bydest.items()):
        ms.sort(key=lambda x: (x["ods_code"], x["date"]))
        fn = first_name(fullnames.get(rec, rec))
        byorg = {}
        for m in ms:
            byorg.setdefault((m["ods_code"], m.get("org_name") or m["ods_code"]), []).append(m)
        lines = [f"Hi {fn},\n",
                 f"The board paper machine found {len(ms)} new meeting date(s) for orgs you cover.\n"]
        for (ods, name), group in sorted(byorg.items(), key=lambda kv: kv[0][1]):
            lines.append(f"\n## {name} ({ods})\n")
            lines.append("| Date | Meeting | Source |")
            lines.append("|---|---|---|")
            for m in group:
                lines.append(f"| {human(m['date'])} | {m.get('title') or 'Board meeting'} "
                             f"| [board page]({m.get('source_url')}) |")
        icsf = os.path.join(REPO, "subscriptions", "new", f"{slug(rec)}_{RUNDATE}.ics")
        writetext(icsf, wrap_ics([vevent(m["ods_code"], m["date"],
                                         m.get("org_name") or m["ods_code"],
                                         m.get("title"), m.get("source_url")) for m in ms]))
        lines.append(f"""
## Add to your calendar

A calendar file ({slug(rec)}_{RUNDATE}.ics) is attached containing the
{len(ms)} new date(s) above — nothing else.

**To add them:** open the attachment → Outlook → 'Save & Close' (once).
Import it only once: Outlook does not de-duplicate .ics file imports, so
re-opening the same file would add the events a second time.

— Board paper machine
""")
        bf = os.path.join(REPO, "outbox", f"{RUNDATE}_{slug(rec)}_dates.md")
        writetext(bf, "\n".join(lines))
        dates.append({
            "id": f"dates:{slug(rec)}",
            "to": cmap[rec],
            "subject": f"[Board paper machine] {len(ms)} new meeting date(s) detected",
            "body_file": bf.replace("\\", "/"),
            "attach": [icsf.replace("\\", "/")],
            "_meeting_ids": [m["id"] for m in ms],
        })

    json.dump(papers, open(os.path.join(REPO, f"papers_manifest_{RUNDATE}.json"), "w",
                           encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(dates, open(os.path.join(REPO, f"dates_manifest_{RUNDATE}.json"), "w",
                          encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"papers alerts: {len(papers)}   date alerts: {len(dates)}")
    if missing:
        print(f"\nANALYSES MISSING ({len(missing)}) - these will NOT be alerted:")
        for m in missing:
            print("  ", m)
    print("\nrecipients (papers):")
    from collections import Counter
    print(" ", Counter(p["to"] for p in papers).most_common())
    print("recipients (dates):")
    print(" ", [d["to"] for d in dates])


if __name__ == "__main__":
    main()

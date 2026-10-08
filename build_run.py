#!/usr/bin/env python
"""Consolidate a scan-boards sweep: merge agent scan output into state, write
.ics files, resolve recipients, and build send_batch manifests.

Run-parameterised: set BPM_TODAY (YYYY-MM-DD), BPM_RUNDATE (YYYYMMDD) and
BPM_RESULTS (this run's dir) in the environment. Defaults to today.
Everything is read/written as UTF-8 no-BOM.
"""
import json, os, re, glob, datetime, sys

REPO = os.path.dirname(os.path.abspath(__file__))
_today_env = os.environ.get("BPM_TODAY")
TODAY = datetime.date.fromisoformat(_today_env) if _today_env else datetime.date.today()
RUNDATE = os.environ.get("BPM_RUNDATE") or TODAY.strftime("%Y%m%d")
RESULTS = os.environ.get("BPM_RESULTS") or os.path.join(REPO, "tmp_scan")


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jdump(obj, p):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def slug(name):
    """Slugify a full correspondent key. NEVER key on first name alone -
    there are two Matts and both shorten to 'matt'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_orgs():
    orgs = {}
    for fn, kind in (("data/trust_urls.json", "trust"), ("data/icb_urls.json", "icb")):
        d = jload(os.path.join(REPO, fn))
        rows = d
        if isinstance(d, dict):
            for k in ("trusts", "icbs", "orgs", "organisations"):
                if k in d:
                    rows = d[k]
                    break
        for o in rows:
            o["org_type"] = kind
            orgs[o["ods_code"]] = o
    return orgs


def recipients_for(org, corr_map, overrides, kind):
    """Union of correspondent + additional_correspondents + live overrides,
    de-duplicated. `kind` is 'date' or 'papers'."""
    names = []
    primary = org.get("correspondent")
    if primary and primary != "TBC":
        names.append(primary)
    for n in org.get("additional_correspondents") or []:
        if n and n != "TBC" and n not in names:
            names.append(n)
    # live overrides
    for rule in overrides.get("overrides", []):
        if kind not in rule.get("applies_to", []):
            continue
        today = TODAY.isoformat()
        if not (rule.get("start", "") <= today <= rule.get("expires", "")):
            continue  # expired or not yet started
        if rule.get("when_recipient") in names:
            for n in rule.get("add_recipients", []):
                if n and n != "TBC" and n not in names:
                    names.append(n)
    # drop anyone with no email
    out = []
    for n in names:
        if corr_map.get(n):
            out.append(n)
        else:
            print(f"  [skip recipient] {n} has no email in correspondents.json")
    return out


VEVENT = """BEGIN:VEVENT
UID:{ods}-{date}@board-paper-machine.hsj
DTSTAMP:{stamp}
DTSTART;VALUE=DATE:{d0}
DTEND;VALUE=DATE:{d1}
SUMMARY:{summary}
DESCRIPTION:Detected by Board paper machine. Source: {src}
URL:{src}
END:VEVENT"""


def ics_escape(s):
    return str(s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def vevent(ods, date, org_name, title, src, stamp):
    d = datetime.date.fromisoformat(date)
    return VEVENT.format(
        ods=ods, date=date, stamp=stamp,
        d0=d.strftime("%Y%m%d"),
        d1=(d + datetime.timedelta(days=1)).strftime("%Y%m%d"),
        summary=ics_escape(f"{org_name} \u2014 {title or 'Board meeting'}"),
        src=ics_escape(src),
    )


def wrap_ics(events, method=None):
    head = ["BEGIN:VCALENDAR", "VERSION:2.0",
            "PRODID:-//HSJ//Board paper machine//EN", "CALSCALE:GREGORIAN"]
    if method:
        head.append("METHOD:" + method)
    return "\r\n".join(head + events + ["END:VCALENDAR"]) + "\r\n"


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


if __name__ == "__main__":
    print("helper loaded - import and call from the run driver")

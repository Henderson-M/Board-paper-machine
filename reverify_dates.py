#!/usr/bin/env python
"""Rolling re-verification of meeting dates ALREADY in state (scan-boards Step 5b).

Every anti-fabrication guard in the date scan fires only at the moment a date is first
detected. A date that was wrong when it went in stays wrong forever, keeps being emailed,
and sits in a correspondent's calendar until a human happens to notice. On 2026-08-17 a
one-off audit found 76 such dates across 33 orgs, 56 of them already emailed out.

This script makes that audit continuous. Each run it re-checks a slice of what is already
in state against the organisation's own published schedule, and writes back:

  * `last_verified` on the meetings it confirms
  * a `contradicted` list for the caller to retract (it does NOT retract by itself)
  * org health, via org_health.py

It deliberately does NOT retract or email. A retraction owes a withdrawal alert to whoever
was told about the meeting, and that judgement stays with the calling skill.

Usage
-----
  python reverify_dates.py --limit 120                  # normal rolling slice
  python reverify_dates.py --orgs RCB,RFR               # just these orgs
  python reverify_dates.py --all                        # everything (slow, the full audit)
  python reverify_dates.py --limit 120 --json out.json  # machine-readable result
"""
import argparse, datetime, gzip, io, json, os, re, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "meetings.json")
STALE_DAYS = 28          # re-verify anything not confirmed in this long
IMMINENT_DAYS = 21       # always re-verify anything due within this, however recently checked
HORIZON_DAYS = 548       # ~18 months; ignore page dates beyond this when judging

MON = ["January", "February", "March", "April", "May", "June", "July",
       "August", "September", "October", "November", "December"]
MONRE = "|".join(MON)
ABBR = "|".join(m[:3] for m in MON)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def _load(p):
    return json.load(io.open(p, encoding="utf-8"))


def orgs():
    out = {}
    for f in ("data/trust_urls.json", "data/icb_urls.json"):
        for o in _load(os.path.join(HERE, f)):
            out[o["ods_code"]] = o
    return out


def clean(s, is_html=True):
    if is_html:
        s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", s)
        s = re.sub(r"(?s)<!--.*?-->", " ", s)
        # ordinal superscripts split the date text: "16<sup>th</sup> September"
        s = re.sub(r"(?is)<sup>.*?</sup>", "", s)
        s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&#8211;", "-").replace("&amp;", "&")
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x11000 else " ", s)
    return re.sub(r"\s+", " ", s)


def fetch(url, cache_dir=None):
    """requests first (cheap), Playwright --html if that looks like a shell."""
    cp = None
    if cache_dir:
        import hashlib
        cp = os.path.join(cache_dir, hashlib.sha1(url.encode()).hexdigest()[:14] + ".txt")
        if os.path.exists(cp):
            return io.open(cp, encoding="utf-8", errors="replace").read()
    best = ""
    try:
        rq = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept-Encoding": "gzip"})
        resp = urllib.request.urlopen(rq, timeout=45)
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass
        best = clean(raw.decode("utf-8", "replace"))
    except Exception:
        pass
    if len(best) < 1200:                      # nav-only shell, JS page, or a block page
        try:
            r = subprocess.run([sys.executable, "fetch_with_playwright.py", url, "--html"],
                               cwd=HERE, capture_output=True, text=True, timeout=150,
                               encoding="utf-8", errors="replace")
            alt = clean(r.stdout or "")
            if len(alt) > len(best):
                best = alt
        except Exception:
            pass
    if cp:
        io.open(cp, "w", encoding="utf-8").write(best)
    return best


def date_patterns(iso):
    d = datetime.date.fromisoformat(iso)
    mn, ab = MON[d.month - 1], MON[d.month - 1][:3]
    # (?<!\d) rather than \b so a zero-padded "07 October" still matches
    return [r"(?<!\d)0?%d(?:st|nd|rd|th)?\s+%s\b" % (d.day, mn),
            r"(?<!\d)0?%d(?:st|nd|rd|th)?[-\s]+%s\b\.?" % (d.day, ab),
            r"\b%s\s+0?%d(?:st|nd|rd|th)?(?!\d)" % (mn, d.day),
            r"\b%s\.?\s+0?%d(?:st|nd|rd|th)?(?!\d)" % (ab, d.day),
            r"(?<!\d)0?%d[/\-.]0?%d[/\-.](?:%d|%02d)(?!\d)" % (d.day, d.month, d.year, d.year % 100),
            r"(?<!\d)%d[/\-.]0?%d[/\-.]0?%d(?!\d)" % (d.year, d.month, d.day),
            r"(?<!\d)0?%d[-\s]%s[-\s]%02d(?!\d)" % (d.day, ab, d.year % 100)]


def find_date(iso, text):
    if len(text) < 400:
        return "UNREADABLE", None
    yr = iso[:4]
    for p in date_patterns(iso):
        for m in re.finditer(p, text, re.I):
            near = text[max(0, m.start() - 300): m.end() + 200]
            ev = " ".join(text[max(0, m.start() - 90): m.end() + 90].split())
            # the year need not be adjacent: many pages carry one year heading over a bare list
            return ("CONFIRMED" if re.search(r"\b%s\b" % yr, near) else "DAYMONTH"), ev
    return "MISSING", None


def page_future_dates(text, today, horizon):
    out = set()
    pat = r"(\d{1,2})(?:st|nd|rd|th)?[-\s]+(%s|%s)[-\s]+(20\d\d|\d{2})" % (MONRE, ABBR)
    for m in re.finditer(pat, text, re.I):
        try:
            y = int(m.group(3))
            y = y + 2000 if y < 100 else y
            mo = [i for i, x in enumerate(MON, 1) if x.lower().startswith(m.group(2).lower()[:3])][0]
            d = datetime.date(y, mo, int(m.group(1)))
            if today <= d <= horizon:
                out.add(d.isoformat())
        except Exception:
            pass
    return sorted(out)


def pick_slice(meetings, today, limit, only=None, everything=False):
    live = []
    for m in meetings:
        if m.get("status") in ("retracted", "cancelled", "superseded"):
            continue
        if not m.get("date") or m["date"] < str(today):
            continue
        if only and m.get("ods_code") not in only:
            continue
        live.append(m)
    if everything or only:
        return live
    imminent, rest = [], []
    soon = str(today + datetime.timedelta(days=IMMINENT_DAYS))
    cutoff = str(today - datetime.timedelta(days=STALE_DAYS))
    for m in live:
        lv = (m.get("last_verified") or "")[:10]
        if m["date"] <= soon:
            imminent.append(m)              # always re-check what people are about to act on
        elif not lv or lv < cutoff:
            rest.append(m)
    rest.sort(key=lambda m: (m.get("last_verified") or "", m["date"]))
    return imminent + rest[:max(0, limit - len(imminent))]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--orgs", help="comma-separated ods_codes")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", help="write the full result here")
    ap.add_argument("--cache", help="directory to cache fetched page text")
    ap.add_argument("--no-write", action="store_true", help="do not touch state or org health")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=HORIZON_DAYS)
    O = orgs()
    st = _load(STATE)
    meetings = st["meetings"] if isinstance(st, dict) and "meetings" in st else st
    only = set(x.strip().upper() for x in a.orgs.split(",")) if a.orgs else None
    todo = pick_slice(meetings, today, a.limit, only, a.all)
    if a.cache:
        os.makedirs(a.cache, exist_ok=True)

    by_org = {}
    for m in todo:
        by_org.setdefault(m["ods_code"], []).append(m)
    print("re-verifying %d meeting(s) across %d org(s)" % (len(todo), len(by_org)), flush=True)

    def do_org(code):
        o = O.get(code) or {}
        url = o.get("schedule_url") or o.get("url")
        if not url:
            return code, "", []
        t = fetch(url, a.cache)
        return code, t, page_future_dates(t, today, horizon)

    texts = {}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for code, t, fut in ex.map(do_org, list(by_org)):
            texts[code] = (t, fut)

    res = {"confirmed": [], "contradicted": [], "unverifiable": [], "unreadable": []}
    for code, ms in by_org.items():
        t, fut = texts.get(code, ("", []))
        o = O.get(code, {})
        for m in ms:
            v, ev = find_date(m["date"], t)
            rec = {"id": m["id"], "ods_code": code, "date": m["date"],
                   "org": (o.get("names") or [code])[0],
                   "correspondent": o.get("correspondent"),
                   "alerted": bool((m.get("alerts_sent") or {}).get("date")),
                   "page_dates": fut[:10], "evidence": ev,
                   "url": o.get("schedule_url") or o.get("url")}
            if v in ("CONFIRMED", "DAYMONTH"):
                res["confirmed"].append(rec)
            elif v == "UNREADABLE":
                res["unreadable"].append(rec)
            elif fut:
                res["contradicted"].append(rec)       # page HAS a schedule and we are not in it
            else:
                res["unverifiable"].append(rec)       # page publishes nothing forward

    if not a.no_write:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        byid = {m["id"]: m for m in meetings}
        for r in res["confirmed"]:
            byid[r["id"]]["last_verified"] = now
        json.dump(st, io.open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        try:
            sys.path.insert(0, HERE)
            import org_health as oh
            bad = set(r["ods_code"] for r in res["unreadable"])
            nos = set(r["ods_code"] for r in res["unverifiable"]) - bad
            for code in by_org:
                if code in bad:
                    oh.record(code, "fail", kind="unparseable",
                              detail="re-verification could not read the schedule page", now=now)
                elif code in nos:
                    oh.record(code, "ok", kind="no_schedule_published", now=now)
                else:
                    oh.record(code, "ok", now=now)
        except Exception as e:
            sys.stderr.write("WARNING: could not update org health: %r\n" % (e,))

    print("  confirmed    %d" % len(res["confirmed"]))
    print("  CONTRADICTED %d   <- page publishes a schedule and our date is not in it"
          % len(res["contradicted"]))
    print("  unverifiable %d   (org publishes no forward schedule - not an error)"
          % len(res["unverifiable"]))
    print("  unreadable   %d" % len(res["unreadable"]))
    if res["contradicted"]:
        print("")
        print("NEEDS RETRACTION (and a withdrawal alert wherever alerted=True):")
        for r in sorted(res["contradicted"], key=lambda x: (x["org"], x["date"])):
            print("  %-7s %-40s %s  alerted=%s"
                  % (r["ods_code"], r["org"][:40], r["date"], r["alerted"]))
            print("          page says: %s" % (", ".join(r["page_dates"][:6]) or "-"))
    if a.json:
        json.dump(res, io.open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("")
        print("full result -> %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

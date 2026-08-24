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


# Heading-like phrases that mark a block of dates as historical. Deliberately narrow:
# a false positive here turns a real date into a retraction, which owes somebody a
# withdrawal email. "Minutes of the previous meeting" (an agenda line, not a heading)
# must NOT match, hence the requirement for the word "meetings"/"years" plural or "archive".
# Plural "meetings" throughout, deliberately: the singular forms match the ordinary agenda
# line "Minutes of the previous meeting", which appears on plenty of pages that DO publish a
# forward schedule. Treating that as a past-meetings heading suppressed the real dates below
# it, so the org looked like it published nothing forward and its wrong dates could never be
# contradicted — the same silent, reassuring-direction failure this whole fix is about.
PAST_HEADING = re.compile(
    r"(?i)\b(?:past\s+\w*\s*meetings|previous\s+meetings|earlier\s+meetings|"
    r"meetings?\s+archive|archived\s+meetings|previous\s+years?|"
    r"meetings?\s+held\s+in\s+20\d\d)\b")
FUTURE_HEADING = re.compile(
    r"(?i)\b(?:future\s+\w*\s*meetings?|forthcoming\s+meetings?|upcoming\s+meetings?|"
    r"next\s+meetings?|meeting\s+dates|dates\s+for\s+20\d\d|scheduled\s+meetings?)\b")


def _in_past_block(text, pos):
    """True if the nearest preceding heading-like marker says these dates are historical.

    Only consulted for bare day-month matches (no year next to them). A page like
    Kettering's lists "Future 2026 meetings" and "Past 2026 meetings" as separate blocks
    of bare day-months, and without this the two are indistinguishable.
    """
    back = text[max(0, pos - 1500):pos]
    lp = max((m.start() for m in PAST_HEADING.finditer(back)), default=-1)
    lf = max((m.start() for m in FUTURE_HEADING.finditer(back)), default=-1)
    return lp > lf


def _adjacent_year(text, start, end):
    """The year written next to this date ("7 October 2026"), or None if it is bare.

    Deliberately tight. An earlier version scanned a +/-120 character window, which on a
    long bare list reached forward into the NEXT section's year heading: Birmingham and
    Solihull's "Wednesday 7 October" picked up the "2025" of the archive block below it and
    was reported as an error against a date the page plainly publishes.
    """
    m = re.match(r"[\s,]{0,3}(20\d\d)\b", text[end:end + 10])
    if m:
        return int(m.group(1))
    m = re.search(r"\b(20\d\d)[\s,]{0,3}$", text[max(0, start - 10):start])
    return int(m.group(1)) if m else None


def _inherited_year(text, pos):
    """The nearest 4-digit year ABOVE this point — the heading that governs a bare list.

    Forward-only by design: "Trust board meeting 2026" applies to every day-month under it
    until the next year heading. This is the same rule page_future_dates uses, so the two
    functions agree about what year a bare date belongs to.
    """
    last = None
    for m in re.finditer(r"\b(20\d\d)\b", text[:pos]):
        last = m
    return int(last.group(1)) if last else None


def find_date(iso, text):
    """Look for this meeting's day+month on the page and judge how good the match is.

    Returns one of:
      CONFIRMED  - day+month found with the RIGHT year alongside it
      DAYMONTH   - day+month found with no year alongside, not under a "past" heading
                   (the legitimate "bare list under one year heading" pattern)
      WRONGYEAR  - day+month found, but every occurrence carries a DIFFERENT year, or sits
                   under a past-meetings heading. This is an archive row, not our meeting.
      MISSING    - not on the page at all
      UNREADABLE - we did not get enough page text to judge

    Scans EVERY match rather than returning on the first. Returning on the first is what
    let "3 September 2024", sitting in Birmingham Women's and Children's archive listing,
    confirm a "3 September 2026" meeting that the current schedule does not contain
    (found by hand on 2026-08-24). WRONGYEAR must not count as confirmation.
    """
    if len(text) < 400:
        return "UNREADABLE", None
    yr = int(iso[:4])
    best, best_ev = "MISSING", None
    rank = {"MISSING": 0, "WRONGYEAR": 1, "DAYMONTH": 2, "CONFIRMED": 3}
    for p in date_patterns(iso):
        for m in re.finditer(p, text, re.I):
            ev = " ".join(text[max(0, m.start() - 90): m.end() + 90].split())
            adj = _adjacent_year(text, m.start(), m.end())
            if adj is not None:
                verdict = "CONFIRMED" if adj == yr else "WRONGYEAR"
            elif _in_past_block(text, m.start()):
                verdict = "WRONGYEAR"           # bare day-month under a "Past meetings" heading
            else:
                inh = _inherited_year(text, m.start())
                if inh is None:
                    verdict = "DAYMONTH"        # no year anywhere above it; cannot judge
                else:
                    verdict = "CONFIRMED" if inh == yr else "WRONGYEAR"
            if verdict == "CONFIRMED":
                return verdict, ev
            if rank[verdict] > rank[best]:
                best, best_ev = verdict, ev
    return best, best_ev


# One pass, left to right, over every date shape a trust schedule page actually uses.
# Named alternatives so the handler can tell them apart.
_PFD = re.compile(
    # 4-digit years only. Allowing a bare \d{2} here made "8 January 10 March" parse as
    # "8 January '10" and swallow the next item's day, so a bare list under a year heading
    # collapsed to nothing. The hyphenated DD-Mon-YY short form gets its own alternative.
    r"(?P<dmy_named>(?P<dmy_d>\d{1,2})(?:st|nd|rd|th)?[-\s]+(?P<dmy_m>%s|%s)[-\s,]+(?P<dmy_y>20\d\d))"
    r"|(?P<dmy_short>(?<!\d)(?P<sh_d>\d{1,2})-(?P<sh_m>%s|%s)-(?P<sh_y>\d{2})(?!\d))"
    r"|(?P<mdy_named>(?P<mdy_m>%s|%s)\.?[-\s]+(?P<mdy_d>\d{1,2})(?:st|nd|rd|th)?[-\s,]+(?P<mdy_y>20\d\d))"
    r"|(?P<iso>(?<!\d)(?P<iso_y>20\d\d)-(?P<iso_m>\d{1,2})-(?P<iso_d>\d{1,2})(?!\d))"
    r"|(?P<num>(?<!\d)(?P<num_d>\d{1,2})[/.\-](?P<num_m>\d{1,2})[/.\-](?P<num_y>20\d\d|\d{2})(?!\d))"
    # No "not followed by a year" guard here: the dated alternatives above are tried first at
    # each position, so "3 September 2024" is consumed by dmy_named and never reaches `bare`.
    # A guard breaks consecutive bare lists ("9 September 5 November") because the next list
    # item's day digit follows the month.
    r"|(?P<bare>(?<!\d)(?P<bare_d>\d{1,2})(?:st|nd|rd|th)?[-\s]+(?P<bare_m>%s|%s)\b)"
    r"|(?P<yearhdr>(?<!\d)(?P<hdr_y>20\d\d)(?!\d))"
    % (MONRE, ABBR, MONRE, ABBR, MONRE, ABBR, MONRE, ABBR), re.I)


def _mon(name):
    n = name.lower()[:3]
    for i, x in enumerate(MON, 1):
        if x.lower().startswith(n):
            return i
    return None


def page_future_dates(text, today, horizon):
    """Every future date the page publishes, in any format a trust actually uses.

    Two gaps this closes, both of which made the audit fail silently in the reassuring
    direction (it reported "org publishes no forward schedule" for pages that plainly do,
    so a wrong date could never be contradicted):

      * numeric-only dates ("Date: 18/11/2026") — Greater Manchester ICB, found 2026-08-20
      * bare day-months inheriting a year from a heading above them ("Future 2026 meetings:
        10 September, 9 October, ...") — Kettering/Northampton, found 2026-08-24

    A bare day-month is only used when a 4-digit year has appeared earlier in the page, and
    it inherits the most recent one. Bare day-months under a "past meetings" heading are
    skipped: they are last year's list, not a forward schedule.
    """
    out = set()
    ctx_year = None
    for m in _PFD.finditer(text):
        g = m.groupdict()
        try:
            if g["yearhdr"]:
                ctx_year = int(g["hdr_y"])
                continue
            if g["dmy_named"]:
                y, day, mo = int(g["dmy_y"]), int(g["dmy_d"]), _mon(g["dmy_m"])
            elif g["dmy_short"]:
                y = 2000 + int(g["sh_y"])
                day, mo = int(g["sh_d"]), _mon(g["sh_m"])
            elif g["mdy_named"]:
                y, day, mo = int(g["mdy_y"]), int(g["mdy_d"]), _mon(g["mdy_m"])
            elif g["iso"]:
                y, mo, day = int(g["iso_y"]), int(g["iso_m"]), int(g["iso_d"])
            elif g["num"]:
                y = int(g["num_y"]); y = y + 2000 if y < 100 else y
                day, mo = int(g["num_d"]), int(g["num_m"])   # UK order: DD/MM/YYYY
            elif g["bare"]:
                if ctx_year is None or _in_past_block(text, m.start()):
                    continue
                y, day, mo = ctx_year, int(g["bare_d"]), _mon(g["bare_m"])
            else:
                continue
            if not mo:
                continue
            d = datetime.date(y, mo, day)
            if y >= 2000:
                ctx_year = y
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
            rec["match"] = v
            # Invariant: the two halves of this check must agree. If page_future_dates found
            # our date on the page, it cannot also be "not in the published schedule" — that
            # combination means the matcher failed, not the org. Retracting on it would send
            # a withdrawal for a meeting that is going ahead, so treat it as confirmed and
            # say so loudly instead.
            if v not in ("CONFIRMED", "DAYMONTH", "UNREADABLE") and m["date"] in fut:
                rec["match"] = v + "->OVERRIDDEN"
                rec["note"] = ("find_date said %s but page_future_dates found this exact date "
                               "on the page; treating as confirmed. Matcher bug — investigate."
                               % v)
                sys.stderr.write("WARNING: %s %s - %s\n" % (code, m["date"], rec["note"]))
                res["confirmed"].append(rec)
                continue
            if v in ("CONFIRMED", "DAYMONTH"):
                res["confirmed"].append(rec)
            elif v == "UNREADABLE":
                res["unreadable"].append(rec)
            elif fut:
                # page HAS a forward schedule and our date is not in it.
                # v is MISSING (not on the page at all) or WRONGYEAR (only in an archive row
                # for a different year, or under a past-meetings heading) — neither confirms.
                res["contradicted"].append(rec)
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

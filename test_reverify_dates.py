#!/usr/bin/env python
"""Regression tests for reverify_dates.py's date matching.

Every case here is a real failure the audit produced on a live run. The audit's failures
are dangerous precisely because they are silent and point the reassuring way: it says
"confirmed" or "the org publishes no forward schedule" when in fact our date is wrong.

Run:  python test_reverify_dates.py
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reverify_dates as R  # noqa: E402

TODAY = datetime.date(2026, 8, 24)
HORIZON = TODAY + datetime.timedelta(days=548)

# Enough prose to clear find_date's 400-char readability floor, and representative of the
# boilerplate that sits above a real schedule.
PAD = ("The Trust Board of Directors holds its meetings in public and welcomes observers. "
       "Papers are published on this page in advance of each meeting. Questions from members "
       "of the public should be submitted in writing to the Trust Secretary at least three "
       "working days before the meeting takes place so that a full response can be prepared. ")

CASES = [
    (
        "BWC: archive row for another year must not confirm (2026-08-24)",
        PAD + "Board meetings and minutes. 2026 meeting dates 8 January 10 March 7 May 2 July "
              "9 September 5 November. Previous meetings archive: 9 January 2024, 5 March 2024, "
              "2 May 2024, 2 July 2024, 3 September 2024, 5 November 2024. "
              "Meetings archive 2023: 1 February 2023.",
        [("2026-09-03", "contradict"),   # only "3 September 2024" exists — an archive row
         ("2026-09-09", "confirm"),      # the real September date
         ("2026-11-05", "confirm")],
    ),
    (
        "Kettering/UHN: bare day-months under Future vs Past headings (2026-08-24)",
        PAD + "Trust Board Meetings Meetings 2026 Future 2026 meetings 9.30am Thursday 10 September, "
              "at Kettering 9.30am Friday 9 October, at Northampton 9.30am Friday 6 November, at "
              "Northampton 9.30am Friday 4 December, at Northampton. Past 2026 meetings Thursday "
              "11 June agenda Friday 8 May Boards Public Meeting Friday 9 April Public Boards "
              "Friday 6 February Public Board",
        [("2026-10-08", "contradict"),   # page says 9 October
         ("2026-12-10", "contradict"),   # page says 4 December
         ("2026-11-06", "confirm"),
         ("2026-09-10", "confirm"),
         ("2027-02-05", "contradict"),   # "6 February" is under Past 2026, not a 2027 date
         ("2027-04-09", "contradict")],  # "9 April" likewise
    ),
    (
        "Greater Manchester ICB: numeric-only schedule (2026-08-20)",
        PAD + "Details Hide Board Meeting Date: 27/10/2026 Time: 10:00 Details Hide Committee "
              "Meeting Date: 18/11/2026 Time: 10:00 Details Hide Board Meeting Date: 18/01/2027",
        [("2026-08-25", "contradict"),   # the date wrongly held and withdrawn on 2026-08-20
         ("2026-11-18", "confirm")],
    ),
    (
        "An org that genuinely publishes no forward schedule stays unverifiable",
        PAD + "Board papers. Meetings archive 2026: 14 January 2026 papers, 11 March 2026 papers, "
              "13 May 2026 papers, 8 July 2026 papers. Meetings archive 2025.",
        [("2026-11-12", "unverifiable")],
    ),
    (
        "Formats that must keep working: zero-padded, DD-Mon-YY, numeric",
        PAD + "Board meeting dates 2026: Wednesday 07 October 2026, 17-Sep-26 Trust Board, "
              "12/11/2026 Board of Directors.",
        [("2026-10-07", "confirm"), ("2026-09-17", "confirm"), ("2026-11-12", "confirm")],
    ),
    (
        "Birmingham and Solihull: a long bare list must not pick up the NEXT block's year",
        PAD + "Trust board meeting 2026 Wednesday 4 February, 9am -12.30pm Wednesday 1 April, "
              "9am -12.30pm Wednesday 3 June, 10.30am -1pm Wednesday 5 August, 9am -12.30pm "
              "Wednesday 7 October, 9am-12.30pm Wednesday 2 December, 9am-12.30pm All meetings "
              "taking place in the Plymouth Room, Uffculme Centre. 2025 5 February (part one) "
              "2 April (part one) 4 June (part one) 6 August (part one)",
        # A +/-120 char window around "7 October" reaches the "2025" heading below it, which
        # made a date the page publishes look like an error (found 2026-08-24).
        [("2026-10-07", "confirm"), ("2026-12-02", "confirm")],
    ),
    (
        "'Minutes of the previous meeting' is an agenda line, not a past-meetings heading",
        PAD + "Forthcoming meetings 2026 Agenda: 1.2 Minutes of the previous meeting. "
              "The Board will next meet on 15 October and then on 10 December.",
        [("2026-10-15", "confirm"), ("2026-12-10", "confirm")],
    ),
]

# (case name, text, expected subset of page_future_dates). Guards the other half of the
# classifier: if page_future_dates comes back empty the org is called "publishes no forward
# schedule" and a wrong date can never be contradicted, however good find_date is.
PFD_CASES = [
    ("Bare list under a year heading",
     PAD + "2026 meeting dates 8 January 10 March 7 May 2 July 9 September 5 November.",
     ["2026-09-09", "2026-11-05"]),
    ("Numeric-only schedule",
     PAD + "Board Meeting Date: 27/10/2026 Board Meeting Date: 18/11/2026",
     ["2026-10-27", "2026-11-18"]),
    ("An agenda line must not suppress the schedule below it",
     PAD + "Forthcoming meetings 2026 Agenda: 1.2 Minutes of the previous meeting. "
           "The Board will next meet on 15 October and then on 10 December.",
     ["2026-10-15", "2026-12-10"]),
]


def verdict(iso, text, page_future):
    v, _ = R.find_date(iso, text)
    if v in ("CONFIRMED", "DAYMONTH"):
        return "confirm", v
    if v == "UNREADABLE":
        return "unreadable", v
    return ("contradict" if page_future else "unverifiable"), v


def main():
    failures = 0
    for name, text, checks in CASES:
        fut = R.page_future_dates(text, TODAY, HORIZON)
        print("== %s" % name)
        print("   page_future_dates: %s" % (fut or "[]"))
        for iso, expected in checks:
            got, raw = verdict(iso, text, fut)
            ok = got == expected
            failures += 0 if ok else 1
            print("   %s %s -> %-10s => %-12s expected %s"
                  % ("OK  " if ok else "FAIL", iso, raw, got, expected))

    for name, text, expected in PFD_CASES:
        fut = R.page_future_dates(text, TODAY, HORIZON)
        missing = [d for d in expected if d not in fut]
        failures += 0 if not missing else 1
        print("== page_future_dates: %s" % name)
        print("   %s got %s%s"
              % ("OK  " if not missing else "FAIL", fut or "[]",
                 "" if not missing else "  MISSING %s" % missing))
    print()
    if failures:
        print("*** %d CHECK(S) FAILED ***" % failures)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

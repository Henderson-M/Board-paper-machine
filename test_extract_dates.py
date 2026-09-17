#!/usr/bin/env python3
"""Regression tests for `extract_board_html.find_dates` year inference.

Run after touching `_YEAR_HEAD`, `_FY_HEAD`, `_BARE_DM` or `find_dates`:

    python test_extract_dates.py

These matter more than they used to. `extract_board_html.py` used to be a
cross-check that ran *after* the LLM date scan, so a gap in it was usually
masked. Since `prescan.py` made it the PRIMARY date source for most orgs, a
missed pattern here is a missed meeting, and a wrong inference here is a
fabricated one.
"""

from __future__ import annotations

import sys

import extract_board_html as ex

CASES: list[tuple[str, str, list[str]]] = [
    # --- pass 1: dates carrying their own year ---
    ("explicit years",
     "Meetings 2026 9 November 2026, 13 July 2026",
     ["2026-07-13", "2026-11-09"]),

    # --- HTML entities must decode before parsing ---
    # Live shape: Black Country Healthcare (TAJ) writes "6 Jan&nbsp;2027 (Wed)".
    ("non-breaking space between month and year",
     "Board dates: 6 Jan&nbsp;2027 (Wed), 3 Mar&nbsp;2027 (Wed)",
     ["2027-01-06", "2027-03-03"]),
    ("numeric entity separators",
     "23 July 2026 &#8211; 09:30 &#8211; Conference Room",
     ["2026-07-23"]),

    # --- pass 2: single-year list head ---
    ("single-year head, colon",
     "board dates 2026: 5 August, 7 October",
     ["2026-08-05", "2026-10-07"]),
    ("single-year head, keyword first",
     "Board meetings 2026 5 August, 7 October",
     ["2026-08-05", "2026-10-07"]),

    # --- pass 3: NHS financial-year head, month-aware split ---
    # Live page that exposed the gap: Buckinghamshire Healthcare (RXQ).
    ("financial-year head, year first (RXQ live shape)",
     "2026/27 schedule - dates and venues Thursday 24 September 9.45am "
     "Thursday 26 November 9.45am",
     ["2026-09-24", "2026-11-26"]),
    ("financial-year head splits across the year boundary",
     "Board dates 2026/27: 12 May, 14 July, 13 January, 10 March",
     ["2026-05-12", "2026-07-14", "2027-01-13", "2027-03-10"]),
    ("financial-year head, hyphen form",
     "2026-27 board meetings 5 August, 2 February",
     ["2026-08-05", "2027-02-02"]),
    ("financial-year head, four-digit second year",
     "Board meetings 2026/2027 7 October, 3 March",
     ["2026-10-07", "2027-03-03"]),
    ("April is the start of the NHS financial year, not the end",
     "2026/27 schedule 1 April, 31 March",
     ["2026-04-01", "2027-03-31"]),

    # --- things that must NOT produce an inferred date ---
    # A year next to a date is not a head. Guessing here fabricates meetings,
    # which is the one failure this tool must never make.
    ("a bare year with no schedule keyword is not a head",
     "Copyright 2024/25 all rights reserved 14 June",
     []),
    ("a year range with no keyword nearby is not a head",
     "Our 2026/27 annual report was published. Contact us on 14 June",
     []),

    # --- documented semantics, so a future change has to be deliberate ---
    # Two heads running together are genuinely ambiguous to a human reader too.
    # Nearest-preceding-head wins, matching pass 2. The `year_inferred: true`
    # flag is what protects this: the skill re-checks the literal day/month
    # before recording any inferred date.
    ("adjacent heads: nearest head wins",
     "2026/27 and 2027/28 schedule 5 April",
     ["2027-04-05"]),
]


def main() -> int:
    failures = 0
    for name, text, want in CASES:
        # Exercise the REAL call path. Every production caller reaches find_dates
        # through _visible_text or _clean, which is where HTML entities are
        # decoded — testing find_dates on raw text would pass a string no caller
        # ever passes, and would have hidden the &nbsp; bug rather than catching it.
        got = sorted({d["iso"] for d in ex.find_dates(ex._visible_text(text))})
        ok = got == sorted(want)
        if not ok:
            failures += 1
        print(f"{'OK  ' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"        text : {text!r}")
            print(f"        got  : {got}")
            print(f"        want : {sorted(want)}")

    # Every date produced by inference must be flagged, so the skill knows to
    # re-check the literal day/month before recording it.
    inferred = ex.find_dates(ex._visible_text("2026/27 schedule 24 September, 26 November"))
    unflagged = [d["iso"] for d in inferred if not d.get("year_inferred")]
    if unflagged:
        failures += 1
        print(f"FAIL  inferred dates must carry year_inferred=True: {unflagged}")
    else:
        print("OK    inferred dates carry year_inferred=True")

    print()
    print("all checks passed" if not failures else f"{failures} FAILURE(S)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

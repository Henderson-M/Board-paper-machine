# Pre-scan verification, 17 September 2026

Evidence that making `extract_board_html.py` the **primary** date source (via
`prescan.py`) does not cost recall. Run before the change was committed, against
the full 239-org list and the committed state from the 10 September sweep.

## Why this test exists

The change is a cost change: ~40 Opus scan agents per sweep down to roughly 18
Sonnet ones. The risk it carries is not a worse summary — pack *analysis* is
untouched and still runs on Fable — but a **missed pack**, which is invisible.
The skill already records why that matters:

> A dropped date is never detected, so no meeting is created and its pack is
> never scanned. Nothing in the run looks wrong.

So the test is: does the deterministic path still find everything the LLM-wide
sweep found?

## Method

1. `python prescan.py --workers 10` over all 239 in-scope orgs.
2. For every org the pre-scan marked `resolved`, compare its `forward_dates`
   against every future-dated, non-retracted meeting for that org in
   `state/meetings.json`.
3. For each apparent miss, fetch the live page and check whether the date is
   **literally present** — rather than assuming either side is right.

Step 3 is the part that matters. A diff against state alone cannot tell "the
extractor missed it" from "state is stale", and those need opposite fixes.

## Result

| | Before fixes | After fixes |
|---|---|---|
| Orgs resolved with no model at all | 186 | **168** |
| Orgs needing an agent | 53 | **71** |
| Known future dates re-found | 525 | **485** |
| New dates found, not yet in state | 85 | **91** |
| Resolved orgs missing a known date | 18 | **9** |
| — of those, genuinely on the page | 2 | **0** |

The resolved count went **down** deliberately: two safety nets moved 19 orgs from
"resolved" to "needs an agent" rather than let a guess stand. That is the trade
being made — slightly more agents, no silent misses.

All 9 residual mismatches were checked against the live page and the date is
**absent from it** in every case. Those are stale state entries, which is Step
5b's job (re-verify and retract), not a pre-scan failure.

Runtime for the full deterministic sweep: **under a minute**.

## Three real bugs this surfaced

Each was a live miss, each is now covered by `test_extract_dates.py`.

**1. NHS financial-year headings (`_FY_HEAD`, new pass 3).**
Buckinghamshire Healthcare (RXQ) publishes "2026/27 schedule – dates and venues /
Thursday 24 September / Thursday 26 November". Year inference only understood
`dates 2026` and `2026:` forms, so both meetings were dropped. The new pass
assigns the year by month — April-December to the first year, January-March to
the second — because attaching the head year to the whole run would date a bare
"28 January" twelve months early.

**2. HTML entities were never decoded (`_unescape`).**
Black Country Healthcare (TAJ) writes "6 Jan&nbsp;2027 (Wed)". `_visible_text`
stripped tags but left entities intact, so the date patterns never matched a
month and year separated by six literal characters. `reverify_dates.py` already
carried its own partial `&nbsp;`/`&#8211;` patch — the same bug, fixed in one
place and not the other. Now fixed in the extraction layer, where every caller
gets it.

**3. Past-only pages counted as "resolved".**
`find_dates` returns every date on the page, history included, so an org showing
nothing but a 2020-2023 archive looked resolved and would have been dropped from
the date sweep entirely. Classification now uses forward dates only.

## The two safety nets

These are what make the pre-scan trustworthy. It does not need to parse every
calendar format correctly — it needs to **know when it hasn't**.

- **`unresolved_schedule_dates`** (11 orgs). A weekday-prefixed day-month with no
  year — "Thursday 24 September" — is almost always a schedule entry on a board
  page. If one is present and no pass resolved it, the org goes to an agent even
  if other dates were found. Finding *some* dates is not good enough: a page can
  list four meetings in a format we read and two in one we don't.
- **`year_inferred_only`** (4 orgs). Where every forward date came from year
  inference, an agent confirms it. The day and month are literal; the year is
  not, and a guess should not decide what lands in someone's calendar.

## What this test does NOT cover

The analysis tier. Re-running a full pack-analysis comparison would cost the
quota this whole change exists to protect, so `/pack-analyser` was left exactly
as it is — Fable, per the 11 September three-way test. Unchanged is the strongest
guarantee available here, and the only claim made is that the *finding* of packs
is not degraded.

## Reproducing

```bash
python test_extract_dates.py      # date parsing regressions
python test_reverify_dates.py     # existing matcher suite, still green
python prescan.py --workers 10    # full deterministic sweep
```

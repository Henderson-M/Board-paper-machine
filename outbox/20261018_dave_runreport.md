Hi Dave,

Full sweep run from your machine on Sunday 18 October 2026, started 11:35. All 239 in-scope orgs scanned (one with no URL and three with no correspondent were skipped, as usual). 0 orgs broken, 1 degraded (Mid Cheshire, host not responding to any fetcher), 0 stale, 0 not checked.

The pre-scan resolved 174 of 239 orgs deterministically in 91 seconds. 15 known no-schedule orgs went straight to the watchlist; 50 went to four Sonnet date agents, alongside one Sonnet pack hunter and one Sonnet watchlist agent. 5 packs were analysed on Fable in two waves (3 + 2). Emails: 8 papers alerts, 4 date alerts, 0 withdrawals, plus this report.

## New dates (4 date alerts)

- Matt Discombe (Ella copied under the shadow rule): Central and North West London: 21 Oct 2026 (Board in Common with CLCH and West London), 10 Mar, 23 Jun, 29 Sep and 8 Dec 2027.
- Matt Mathers: University Hospitals Tees group board (South Tees and North Tees and Hartlepool): 3 Dec 2026, 7 Jan and 4 Mar 2027. Recorded against both trusts; sent once.
- Annabelle: University Hospitals of Leicester 10 Dec 2026 (Boards in Common with UH Northamptonshire) REINSTATED. We withdrew it on 17 Aug when the page showed only 3 Sep; the page now lists it literally ("Thursday 10 December 2026 9.30am Cumulus Room").

Re-verification: 120 checked, 95 confirmed, 14 unverifiable, 6 unreadable, 5 contradicted. All 5 contradictions are known matcher artefacts kept by earlier runs (Birmingham Women's and Children's year heading, Black Country ICB, Blackpool x2, Central East ICB's "19 March 2026" typo); none was ever alerted. No retractions this run.

Pre-scan false positives rejected again: print/review stamps (Royal Free, MK, CUH, Salisbury, Bristol x2), YAS job advert, UH Sussex question deadline, Central East ICB "papers published by", George Eliot registration deadline, Medway and UHB Council of Governors, mis-yeared tokens (BWC, LPT), and the Greater Manchester locality/committee dates.

## Packs analysed (8 papers alerts)

- East Sussex Healthcare, 20 Oct (Alison): 6 LEAD / 12 WATCH / 8 FOI. Route map to NHS England puts the most likely outturn at a £29.5m deficit (worst case £49.6m) against a breakeven plan; cash at the £3.1m minimum, about 13,500 invoices outstanding.
- North West London acute Board in Common, 20 Oct (Matt Discombe, Ella): 10 / 10 / 6. London North West drops from oversight segment 1 to 3 (71st); Chelsea and Westminster and Hillingdon to segment 2; £52.2m straight-line deficit offset by assumed mitigations; first MTFP finds a "significant underlying structural deficit".
- West and North London ICB, 21 Oct (Matt Discombe, Ella): 7 / 11 / 5. 10-year strategy projects a £1.8bn-plus annual deficit by 2035/36 on current course; elective clawback exposure £135m (2027/28) and £244.5m (2028/29).
- CNWL, CLCH and West London Board in Common, 21 Oct (Ella, Matt Discombe): 7 / 9 / 4. CLCH CEO James Benson says he has been appointed interim National Director for Neighbourhood Healthcare alongside his trust role; CNWL CMO Con Kelly retiring in December.
- Guy's and St Thomas', 21 Oct (Ella): 9 / 8 / 5. Out of segment 1 (12th to 25th of 134), seven never events in Q2, only £66.7m of a £124.5m savings target identified.

Headline figures and quotes spot-checked against pack text for every summary. GSTT blocks every direct fetch (403 to requests, Playwright and curl); its pack text came from a Wayback Machine save (sizes match the live files).

## Scan health

## SCAN HEALTH: 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED: failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Mid Cheshire Hospitals NHS Foundation Trust | RBT | Zoe | 1 | 2026-10-18 | WebFetch timeout, Playwright goto timeout x3 (two URLs), curl 000; host not responding fro |

### ACTION REQUIRED: 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement: it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Mid Cheshire Hospitals NHS Foundation Trust (Zoe): currently https://www.mcht.nhs.uk/about-us/board-directors/board-papers-and-minutes
    python org_urls.py set --ods RBT --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)


## Handed back / not resolved

- Mid Cheshire (RBT, Zoe) unreachable on every fetcher this run; it is also on the papers watchlist, so a new pack there would not have been seen.
- 6 in-window meetings have no papers yet: Lewisham and Greenwich 27 Oct, York and Scarborough 28 Oct, UH Plymouth 28 Oct, Mersey and West Lancashire 28 Oct, West Midlands Ambulance 28 Oct, South Central Ambulance 28 Oct.
- Hertfordshire Partnership: schedule_url now set to /about-us/our-board-of-directors/. That table also lists short (45-minute) slots on 22 Oct, 17 Dec and 25 Feb whose Public/Private labelling is ambiguous; not added. Worth a human look. The 24 Sep pack has still never been detected.
- Seed backlog: 267 future meetings in state (all first seen at the 27 May seed import) have never been date-alerted. Earlier runs have left these alone; it is a decision for you and Henry whether to send a one-off catch-up.
- Tooling note: the pack-text extraction loop wrote filenames with a trailing carriage return (Windows line endings in the job list); fixed by hand this run, and the agents coped.

Board paper machine

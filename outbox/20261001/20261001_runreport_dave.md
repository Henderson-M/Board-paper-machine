Run report, Thursday 1 October 2026. Operator: Dave

A full sweep of all 239 in-scope orgs, started 14:52. The deterministic pre-scan resolved 177 orgs from raw HTML in 91 seconds at no model cost. Of the other 62, 19 were known no-schedule orgs handled by the papers watchlist and 43 went to six Sonnet date-scan agents (one wave), plus one Sonnet agent to hunt packs on pages the stored URL does not reach. 20 packs were analysed on Fable in waves of three (96 LEAD, 229 WORTH WATCHING, 108 FOI). The account's session limit was hit during the sixth analysis wave; state had been pushed after every wave, nothing was lost, and the run resumed after the 20:00 reset. Emails went out in two batches for that reason.

**Scan health: 0 broken, 1 degraded (South West Yorkshire Partnership, RXG: every sub-page now returns 403), 0 stale, 0 not checked.**

## Packs analysed

| Meeting | Org | LEAD | WW | FOI | To |
|---|---|---|---|---|---|
| 2026-09-03 | Alder Hey Children's Foundation Trust (RBS) | 6 | 18 | 8 | Zoe |
| 2026-09-24 | Northamptonshire Healthcare Foundation Trust (RP1) | 2 | 7 | 1 | Annabelle |
| 2026-09-29 | Northamptonshire Healthcare Foundation Trust (RP1) | 2 | 6 | 2 | Annabelle |
| 2026-09-30 | North East and North Cumbria ICB (QHM) | 6 | 15 | 7 | Matt Mathers |
| 2026-09-30 | Mersey and West Lancashire Teaching Hospitals Trust (RBN) | 5 | 13 | 6 | Zoe |
| 2026-09-30 | York and Scarborough Teaching Hospitals Foundation Trust (RCB) | 5 | 16 | 7 | Henry |
| 2026-09-30 | Oxford University Hospitals Foundation Trust (RTH) | 8 | 16 | 8 | Mimi |
| 2026-09-30 | Central and North West London Foundation Trust (RV3) | 3 | 12 | 7 | Matt Discombe, Ella |
| 2026-09-30 | Avon and Wiltshire Mental Health Partnership Trust (RVN) | 3 | 11 | 4 | Joe |
| 2026-09-30 | Cheshire and Wirral Partnership Foundation Trust (RXA) | 3 | 13 | 6 | Zoe |
| 2026-09-30 | Derbyshire Healthcare Foundation Trust (RXM) | 4 | 16 | 8 | Annabelle |
| 2026-09-30 | Surrey and Sussex ICB (S9B9J) | 5 | 7 | 3 | Alison |
| 2026-10-01 | University Hospitals Coventry and Warwickshire Trust (RKB) | 5 | 15 | 9 | Caitlin |
| 2026-10-01 | Tameside and Glossop Integrated Care Foundation Trust (RMP) | 5 | 7 | 3 | Nick |
| 2026-10-01 | Hampshire Hospitals Foundation Trust (RN5) | 6 | 5 | 3 | Mimi |
| 2026-10-01 | Dartford and Gravesham Trust (RN7) | 7 | 8 | 6 | Alison |
| 2026-10-01 | The Princess Alexandra Hospital Trust (RQW) | 5 | 5 | 3 | Emily |
| 2026-10-01 | East Kent Hospitals University Foundation Trust (RVV) | 8 | 16 | 6 | Alison |
| 2026-10-01 | South East Coast Ambulance Service Foundation Trust (RYD) | 5 | 11 | 6 | Alison |
| 2026-10-01 | Birmingham Community Healthcare Foundation Trust (RYW) | 3 | 12 | 5 | Caitlin |

Notes on these:
- **Northamptonshire Healthcare 24 September was a missed pack.** The trust publishes each meeting in its own folder (`/board?smbfolder=...`) and the stored URL shows only the shell, so the 24 and 28 September runs never saw it. Found while locating the 29 September group board pack. Annabelle's alert says plainly that it is late. The folder IDs are now in the org notes.
- **Alder Hey 3 September** came from the papers watchlist: the trust posts packs weeks after the meeting. Zoe's alert flags the date.
- **Dartford and Gravesham 1 October** came from the papers watchlist too. The trust changed its document-library block ID today (58107 to 68487), which made the old folder URL return an empty shell.
- **Tameside and Glossop / Stockport** is one joint board pack, analysed once and sent to Nick once.
- Four multi-file packs were taken whole from their dated section rather than by filename match: NENC ICB (36 files), Surrey and Sussex ICB (20), Oxford University Hospitals (19), Northamptonshire Healthcare (16).

## New meeting dates

| Date | Org | Source | To |
|---|---|---|---|
| 2026-11-26, 2027-01-28, 2027-03-25 | Yorkshire Ambulance Service (RX8) | trust board page, 'Board Meeting Dates 2026-27' | Henry, Alison |
| 2026-12-03, 2027-02-04 | Dartford and Gravesham (RN7) | 1 October pack agenda, 'Dates of future meetings' | Alison |

Also recorded without a date alert because they are today or past: Dartford and Gravesham 1 October (from its pack), Alder Hey 3 September and 1 October (from the 3 September pack).

Pre-scan candidates rejected as not-a-meeting (all literally on the page): 'next review due' footers (RA7, RVJ), print or last-edited stamps (RAL, RD8, RGT, RN7), a site header that prints today's date (RNZ), council of governors and events listings (RRK), a questions deadline (RYR 10 Nov), a papers-by deadline (S1Y5D 12 Mar 2027), a year token belonging to the next list (RQ3), and one mis-yeared date (RT5).

## Retractions

- **Royal National Orthopaedic Hospital, 23 September 2027**: the page lists it as the Annual General Meeting, not a board. It was date-alerted on 29 June, so a withdrawal went to Matt Discombe and Ella with a cancellation .ics.
- **Barnsley 29 September 2026** and **Robert Jones and Agnes Hunt 30 September 2026**: both are AGMs. Already past, so no withdrawal owed.
- **Salisbury 23 July, 10 September and 24 September 2026**: all three were the site's header date widget, which prints today's date and was read as a meeting on whichever day the scan ran. Each had been date-alerted to Joe on the day. All past, so no withdrawal owed, but worth knowing that three false dates went out. The org notes now carry a warning; the extractor needs a guard for this (see below).
- Re-verification: 120 checked, 108 confirmed, 10 unverifiable, 1 unreadable, 1 contradicted. The contradiction (Walton Centre 1 October) is the known false positive from 28 September: the schedule shows 'Trust Board - October 2026' as a link, and the pack itself says 1 October. Not retracted.

## Needs your attention

1. **In-window meetings with no pack online when the scan ran.** These drop out of the detection window after 3 October, so a pack published late will be missed unless the next run is before then: Barnsley (1 Oct), Humber Teaching (30 Sep), South Tyneside and Sunderland (1 Oct, 3pm meeting), Great Ormond Street (30 Sep), Blackpool (1 Oct, see next item).
2. **Blackpool Teaching Hospitals (RXL)**: the 2026/27 papers folder served an Imperva/Incapsula challenge to curl, requests, headless Playwright and headed real Chrome, then HTTP 429. I could not check for the 1 October pack. Zoe has not been told anything about it.
3. **South West Yorkshire Partnership (RXG)**: every sub-page returned 403 (site root 200). Its 29 September pack was analysed last run, so nothing is outstanding, but the watchlist could not poll it.
4. **Dorset (RBD and RDY, Board in Common), dates look wrong but are not retracted.** RDY holds 1 October and 1 December 2026, both recorded as 'month only, verify day' and defaulted to the 1st. RBD holds 7 October 2026, but the only '7 October' on its page is 2025; the 2026 list stops at 11 August. Joe was date-alerted for all of them in June and July. The rule is not to retract when the org publishes no forward schedule, so I have left them, marked them unverified in notes, and put both trusts on the papers watchlist. **Your call whether to tell Joe the 7 October entry is unconfirmed.**
5. **Wirral University Teaching Hospital (RBL)**: the schedule's last line reads 'Wednesday 3 February 2026', out of order after November. 3 February is a Wednesday in 2027, so probably a typo for 2027. Not recorded.
6. **Sussex Partnership 8 October**: still agenda only (reissued as v2). Analysis deferred until the pack lands.
7. **7 to 9 October meetings**: no packs yet at Essex Partnership, Royal Free, Norfolk and Waveney group (QEH, James Paget, NNUH), Clatterbridge, South Warwickshire/George Eliot, Wrightington Wigan and Leigh, Pennine Care, County Durham and Darlington, Warrington and Halton/Bridgewater, UHNM, Birmingham and Solihull Mental Health, Shropshire Community, Lincolnshire Partnership, Midlands Partnership, Shrewsbury and Telford, NLAG/Hull, Kettering/Northampton. Expect most early next week.

## Tooling notes

- **Header date widgets.** The pre-scan accepts a date printed in a site header as a forward meeting when it happens to be today (Salisbury, three false alerts over three months). A guard that rejects a candidate equal to the run date unless it sits in a schedule list would stop it.
- **Pack pages the stored URL does not reach.** Eleven in-window meetings had a `url` that is a dates page with the papers elsewhere. Fixed in the data file this run for Avon and Wiltshire, Tameside and Glossop, Stockport (all now have `papers_url`), and documented in notes for Northamptonshire Healthcare, Surrey and Sussex ICB and Barnsley.
- **swpboard.nhs.uk (Devon and Cornwall ICBs), Royal Cornwall, Airedale, Ashford and St Peter's** all 403 Playwright but read with plain curl and a Chrome user agent. Guy's and St Thomas' reads with headed real Chrome. Notes updated.
- **Watchlist** now 22 orgs: added Christie, TEWV, NWAS, UHCW, Mid Cheshire, EEAST, Dorset County, Dorset Healthcare; removed Yorkshire Ambulance (schedule now published).
- **Budget.** The first fifteen Fable analyses plus seven Sonnet agents (and the orchestrating session) exhausted the session allowance before the sweep finished; the last five packs were analysed after the reset. Twenty packs in one sweep was more than one window held on this run.
- The Playwright MCP browser profile was locked by another live session all afternoon, so the MCP browser was unavailable; the scripts' own Chromium was unaffected.

## Scan health

## SCAN HEALTH: 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED: failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| South West Yorkshire Partnership NHS Foundat | RXG | Henry | 1 | 2026-10-01 | HTTP 403 from site WAF for requests, headless Playwright, headful real Chrome (root https: |

### ACTION REQUIRED: 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement: it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # South West Yorkshire Partnership NHS Foundation Trus (Henry): currently https://www.southwestyorkshire.nhs.uk/about-us-2/how-were-run/our-trust-board/meeting-papers/
    python org_urls.py set --ods RXG --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

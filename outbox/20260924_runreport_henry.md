Run report — Thursday 24 September 2026 — operator: Henry

A full sweep of all 239 in-scope orgs. The deterministic pre-scan resolved 179 orgs from raw HTML in 29 seconds at no model cost; 18 more were already-known no-schedule orgs routed to the papers watchlist, leaving 42 for 7 Sonnet date-scan agents. 17 board packs were analysed on Fable in waves of three — 96 LEAD, 113 WORTH WATCHING, 80 FOI. 14 new meeting dates were added and one date retracted. 31 correspondent emails went out, plus this report.

## Packs analysed

| Date | Org | LEAD | WW | FOI | To |
|---|---|---|---|---|---|
| 2026-09-23 | Royal Berkshire NHS Foundation Trust (RHW) | 5 | 4 | 1 | Mimi |
| 2026-09-24 | Bradford Teaching Hospitals NHS Foundation Trust (RAE) | 7 | 4 | 3 | Henry |
| 2026-09-24 | Leeds and York Partnership NHS Foundation Trust (RGD) | 7 | 4 | 3 | Henry |
| 2026-09-24 | Moorfields Eye Hospital NHS Foundation Trust (RP6) | 6 | 6 | 6 | Ella |
| 2026-09-24 | Leeds Teaching Hospitals NHS Trust (RR8) | 10 | 14 | 15 | Henry |
| 2026-09-24 | University College London Hospitals NHS Foundation Trust (RRV) | 4 | 5 | 1 | Matt Discombe, Ella |
| 2026-09-24 | Maidstone and Tunbridge Wells NHS Trust (RWF) | 5 | 9 | 7 | Alison |
| 2026-09-24 | East London NHS Foundation Trust (RWK) | 4 | 7 | 3 | Matt Discombe, Ella |
| 2026-09-24 | Yorkshire Ambulance Service NHS Trust (RX8) | 8 | 10 | 5 | Henry, Alison |
| 2026-09-24 | East Midlands Ambulance Service NHS Trust (RX9) | 5 | 7 | 4 | Annabelle, Alison |
| 2026-09-25 | West Suffolk NHS Foundation Trust (RGR) | 5 | 5 | 3 | James |
| 2026-09-29 | Countess of Chester Hospital NHS Foundation Trust (RJR) | 3 | 7 | 5 | Zoe |
| 2026-09-29 | Gateshead Health NHS Foundation Trust (RR7) | 6 | 7 | 6 | Matt Mathers |
| 2026-09-29 | Leicestershire Partnership NHS Trust (RT5) | 4 | 5 | 1 | Annabelle |
| 2026-09-29 | South West Yorkshire Partnership NHS Foundation Trust (RXG) | 5 | 7 | 6 | Henry |
| 2026-09-30 | North East London ICB (QMF) | 6 | 6 | 6 | Matt Discombe, Ella |
| 2026-09-30 | East of England Community Health and Care NHS Trust (RY3) | 6 | 6 | 5 | James |

## New meeting dates

| Date | Org | Found by | Correspondent |
|---|---|---|---|
| 2026-09-24 | Royal Free London NHS Foundation Trust (RAL) | prescan | Matt Discombe |
| 2026-09-24 | Milton Keynes University Hospital NHS Foundation Trust (RD8) | prescan | Emily |
| 2026-09-24 | Cambridge University Hospitals NHS Foundation Trust (RGT) | prescan | James |
| 2026-09-24 | Salisbury NHS Foundation Trust (RNZ) | prescan | Joe |
| 2026-09-24 | Moorfields Eye Hospital NHS Foundation Trust (RP6) | papers_watchlist | Ella |
| 2026-09-24 | Yorkshire Ambulance Service NHS Trust (RX8) | agent | Henry |
| 2026-09-25 | Bath and North East Somerset, Swindon and Wiltshire ICB (QOX) | prescan | Joe |
| 2026-09-25 | Somerset ICB (QSL) | prescan | Joe |
| 2026-09-25 | Dorset ICB (QVV) | prescan | Joe |
| 2026-09-29 | Gateshead Health NHS Foundation Trust (RR7) | prescan | Matt Mathers |
| 2026-09-29 | South West Yorkshire Partnership NHS Foundation Trust (RXG) | agent | Henry |
| 2026-10-06 | North London NHS Foundation Trust (G6V2S) | prescan | Matt Discombe |
| 2026-11-24 | South East London ICB (QKK) | prescan | Ella |
| 2026-12-15 | West Yorkshire ICB (QWO) | prescan | Henry |

## Rejected as not-a-meeting

The deadline-context and year-heading guards rejected these. All were literally on the page, which is why the plain literal-source check would have let them through:

- **RT5 2027-09-29** — context_states_year_2026: `he next public Trust Board meeting will be held on: Tuesday 29 September 2026 – 9.30am – 1pm`
- **RYR 2026-11-10** — deadline_context: `ise a question, please do so before 10:00am on Tuesday [[10 November 2026]] . However we would pleas`
- **S1Y5D 2027-03-12** — deadline_context: `r) 19 March 2026, Venue TBC (Papers to be published by [[12 March 2027]]) Attending a Board meeti`
- **RQ3 2027-11-05** — the year token belongs to the *next* list heading ("…5 November | 2027 meeting dates: 14 January…"); RQ3 2026-11-05 is already in state.

## Retraction

- **QKK South East London ICB, 14 October 2026** — the ICB's schedule page publishes 24 November 2026 and 27 January 2027 and does not list 14 October. Retracted. It had never been alerted, so no withdrawal notice was owed to anyone.

## Needs your attention

1. **swpboard.nhs.uk is hard-blocked (403).** It serves the South West Peninsula joint board for NHS Devon (QJK) and NHS Cornwall and IoS (QT6). It defeats plain requests, Playwright and a browser download alike, so neither their board dates nor their pack can be read. Joe has been sent the pack links unanalysed, with that stated plainly. Needs an alternative source.
2. **Guy's and St Thomas' (RJ1) is behind a Cloudflare bot challenge (403).** The date scan agent noted that WebFetch returned a plausible-looking JSON of three 2027 dates for a page that was actually an "Access forbidden" shell — the literal-source guard caught and discarded them. Worth a corrected URL.
3. **Pack detection under-captures multi-file packs.** At East of England (RY3) the scan found 3 of 18 files, and at Yorkshire Ambulance (RX8) 2 of 37, because both publish each paper as a separate file whose name does not carry the meeting date. The analysers recovered the rest themselves, but that only worked because they were told to go looking. The matcher should follow a dated per-meeting sub-page and take every document on it.
4. **Supplementary papers appeared at two already-alerted meetings** — Mid Cheshire (RBT, 24 Sep) and RDaSH (RXE, 24 Sep). Both packs were analysed and alerted on the 21 September run, so they were NOT re-analysed and no second email was sent; the new files are recorded in state. If you want the revised Mid Cheshire bundle (v3.0) read, say so and I will.

## Scan health

## SCAN HEALTH � 1 broken, 2 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### BROKEN � failed 3+ runs running
These need a human. They have failed every run for a while and are silently contributing nothing.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Guy's and St Thomas' NHS Foundation Trust | RJ1 | Ella | 3 | 2026-09-21 | scan_url (and the linked /about-us/our-board/agenda-and-papers) return HTTP 403 Forbidden  |

### DEGRADED � failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Devon ICB | QJK | Joe | 2 | 2026-09-24 | swpboard.nhs.uk returns HTTP 403 Forbidden. Confirmed on three independent attempts: (1) p |
| Cornwall and the Isles of Scilly ICB | QT6 | Joe | 2 | 2026-09-24 | swpboard.nhs.uk returns HTTP 403 Forbidden. Confirmed on three independent attempts: (1) p |

### ACTION REQUIRED � 3 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement � it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Guy's and St Thomas' NHS Foundation Trust (Ella) � currently https://www.guysandstthomas.nhs.uk/about-us/our-board/board-meetings
    python org_urls.py set --ods RJ1 --url <REPLACEMENT> --compare
    # Devon ICB (Joe) � currently https://swpboard.nhs.uk/board-meetings/
    python org_urls.py set --ods QJK --url <REPLACEMENT> --compare
    # Cornwall and the Isles of Scilly ICB (Joe) � currently https://swpboard.nhs.uk/board-meetings/
    python org_urls.py set --ods QT6 --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

— Board paper machine

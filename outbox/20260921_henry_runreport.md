# Board paper machine — run report

**Run:** run-20260921-151157 · started 21 September 2026 15:12 · operator Henry

## What ran

Full sweep of 239 in-scope orgs. The deterministic pre-scan resolved **178** of them with no model at all in 26.7s; **61** went to the agent ladder, of which 18 were already-known no-schedule orgs that went straight to the watchlist, leaving 43 for 7 Sonnet date-scan agents. Pack analysis ran on Fable in waves of three.

**The run hit the account session limit** on the final pack (Central East ICB) at about 20:00 on 21 September. State was already committed and pushed at that point, so nothing was lost; the pack was re-analysed on 22 September and is included below.

## New dates

| Date | Org | ODS |
|---|---|---|
| 2026-09-24 | Rotherham Doncaster and South Humber NHS Foundation Trust | RXE |
| 2026-11-05 | Lancashire and South Cumbria ICB | QE1 |
| 2026-11-12 | University Hospitals Sussex NHS Foundation Trust | RYR |

**2 candidate date(s) rejected** — literally on the page, but not meetings:

- `RYR:2026-11-10` — date appears in deadline/question context, not as a meeting
  > to raise a question, please do so before 10:00am on Tuesday 10 November 2026 . However we would please ask you to note: If the question
- `S1Y5D:2027-03-12` — date appears in deadline/question context, not as a meeting
  > cember) 19 March 2026, Venue TBC (Papers to be published by 12 March 2027) Attending a Board meeting You are welcome to attend any pu

## Packs analysed

| Org | Date | LEAD | WATCH | FOI | To |
|---|---|---|---|---|---|
| North London NHS Foundation Trust | 2026-09-22 | 7 | 5 | 3 | Matt Discombe, Ella |
| Tees, Esk and Wear Valleys NHS Foundation Trust | 2026-09-23 | 7 | 4 | 5 | Matt Mathers |
| Bolton NHS Foundation Trust | 2026-09-24 | 5 | 6 | 2 | Nick |
| The Christie NHS Foundation Trust | 2026-09-24 | 2 | 5 | 3 | Nick |
| Sussex Community NHS Foundation Trust | 2026-09-24 | 6 | 5 | 7 | Alison |
| Rotherham Doncaster and South Humber NHS Foundation Trust | 2026-09-24 | 6 | 5 | 8 | Henry |
| Mid Cheshire Hospitals NHS Foundation Trust | 2026-09-24 | 6 | 4 | 6 | Zoe |
| The Newcastle upon Tyne Hospitals NHS Foundation Trust | 2026-09-25 | 5 | 3 | 2 | Matt Mathers |
| Whittington Health NHS Trust | 2026-09-25 | 6 | 4 | 3 | Matt Discombe, Ella |
| Central East ICB | 2026-09-25 | 5 | 4 | 3 | Emily |
| **Total** | | **55** | **45** | **42** | |

## Emails sent

- 12 papers alerts
- 3 date alerts
- 1 operator run report (this email)

## Handed back — needs a human

- **RJ1 Guy's and St Thomas'** — every URL returns HTTP 403 to all three fetchers. First consecutive failure.
- **QMF North East London ICB** — has real upcoming dates but the page never prints a year, so they could not be safely year-stamped and were dropped. Needs a manual look.
- **RY2 Bridgewater** — merged into Warrington and Halton to form North Cheshire and Mersey on 1 April 2026. No longer exists as a reporting entity; needs removing or relabelling in the org list.
- **RRJ Royal Orthopaedic** — stored URL is a statutory-documents archive, not a meeting-dates page.
- **RCF Airedale** — the page reads "Wednesday 4 March 2027", but that date is a Thursday. Worth checking with the trust before the date is relied on.
- **Leeds Teaching (RR8)** and **EMAS (RX9)** — agendas published but no full pack yet; they will be picked up next run.
- **Royal Papworth (RGM)** — a candidate pack was dropped as a false positive (row-pairing matched an old item file); the trust has not published its 1 October pack.

## Tooling gap found this run

`extract_board_html.py` does not recognise two document-link formats, and real packs were missed until a raw anchor harvest caught them: Sussex Community publishes as `/documents/<slug>/file` and Whittington as `document.ashx?id=NNNNN`. Both are now in the alerts, but the extractor should learn these patterns or the same class of miss will recur silently.

## SCAN HEALTH — 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED — failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Guy's and St Thomas' NHS Foundation Trust | RJ1 | Ella | 1 | 2026-09-21 | Site returns HTTP 403 'Access forbidden' to automated fetchers on every URL tried: scan_ur |

### ACTION REQUIRED — 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement — it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Guy's and St Thomas' NHS Foundation Trust (Ella) — currently https://www.guysandstthomas.nhs.uk/about-us/our-board/board-meetings
    python org_urls.py set --ods RJ1 --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

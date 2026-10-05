Hi Henry,

Run report for the 5 October sweep (run-20261005-100838), run from your machine. All 239 in-scope orgs were scanned; 16 correspondent alerts go out in this batch (5 date alerts, 11 papers alerts across 10 packs).

Run from Henry's machine, started 10:08. All 239 in-scope orgs scanned.
**0 orgs broken, 1 degraded (RVN Avon and Wiltshire, SSL handshake fails on every fetcher), 0 stale, 0 not checked.**

**Pre-scan** resolved 177 of 239 orgs in 53 seconds. 19 known no-schedule orgs went to the
watchlist; 43 went to four Sonnet date agents in one wave, alongside one Sonnet pack hunter
and one watchlist agent. All 72 dates the agents read were already in state. Pre-scan false
positives rejected: print/review-date stamps (Royal Free, Milton Keynes, CUH, Bristol x2),
Salisbury's header date again, job-advert dates (YAS), an event (UHB), a question deadline
(UH Sussex), a "papers published by" date (Central East ICB), two mis-yeared tokens (St George's,
Leicestershire Partnership, BWC).

**Dates.** New: East London FT 3 Dec 2026, 20 May, 22 Jul, 30 Sep 2027; EEAST 11 Nov 2026,
10 Feb 2027 (first forward dates it has published); Sussex Community 30 Mar 2028; Surrey and
Sussex ICB 26 Feb 2027; Birmingham Women's and Children's 14 Jan, 11 Mar, 10 Jun, 9 Sep,
11 Nov 2027 (the year-inference missed its "2027 meeting dates" list).
Re-verification: 120 checked, 109 confirmed, 8 unverifiable, 2 unreadable, 1 contradicted.

**Retractions (none ever alerted, so no withdrawals owed).** ELFT 4 Dec (page says Thursday
3 Dec), Surrey and Sussex ICB 24 Feb (page says Friday 26 Feb), Norfolk and Suffolk ICB 25 Nov
(published schedule jumps from 23 Sep to 27 Jan).

**Packs.** 10 analysed on Fable in four waves: 71 LEAD, 63 WORTH WATCHING, 49 FOI.
George Eliot/SWFT joint board, UHNM, North Cheshire and Mersey (now one merged trust),
Norfolk and Waveney group, Royal Free, UHN Northants, SaTH/Shropshire Community Board in
Common, Clatterbridge, County Durham and Darlington, EPUT. County Durham and EPUT were found
by the pack hunter on pages the stored URL did not reach; papers_url corrected for RXP, R1L,
RL1, RP7, RJL, RWA, RTP. 21 other in-window meetings have no papers online yet.

**Standout leads.** UHNM: CQC inspection "triggered possible enforcement action", £60.4m
unmitigated deficit forecast, workforce reductions. Norfolk and Waveney: QEH negotiating NHSE
enforcement undertakings; JPUH and QEH 125th and 132nd of 134 on NOF. UHN: deficit "exceeding
£100 million", KGH "has stopped paying many NHS organisations". County Durham: supplier
payments "intentionally slowed". SaTH: deficit "could reach £40m", £20m recurring workforce
savings. EPUT: chair has died, interim chair and joint interim execs, CQC section 29A notice.
Cross-pack: George Eliot says Adam Carson is on a 12-month secondment as UHN interim CEO;
UHN's own minutes say "appointed as Chief Executive Officer" with no mention of interim.

**Not done / handed back:**
- Sussex Partnership 8 Oct still agenda only. County Durham's CEO report and IQPR are "to
  follow". Royal Papworth prints "Thursday 5 November" with no year (already in state).
- Watchlist: Mid Cheshire, EEAST, South Tees and North Tees baselined; no new packs.

## Scan health

## SCAN HEALTH — 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED — failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Avon and Wiltshire Mental Health Partnership | RVN | Joe | 2 | 2026-10-05 | SSL handshake failure on requests, curl, Playwright and WebFetch (ERR_SSL_VERSION_OR_CIPHE |

### ACTION REQUIRED — 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement — it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Avon and Wiltshire Mental Health Partnership NHS Tru (Joe) — currently https://www.awp.nhs.uk/about-us/our-trust-board
    python org_urls.py set --ods RVN --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

— Board paper machine

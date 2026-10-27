Hi Dave,

Full board paper machine sweep, run from Dave's machine on Tue 27 Oct 2026 (started 14:42 UTC). All 239 in-scope orgs scanned. Henry ran a full sweep yesterday, so the delta is small. Live sends: 2 papers alerts and this report. No new dates, no withdrawals.

**Scan health: 0 broken, 1 degraded (RJ1 Guy's and St Thomas', headless browser gets "Access forbidden"), 0 stale, 0 not checked.**

Pre-scan resolved 182 of 239 orgs in 61 seconds; 57 went to three Sonnet date agents. No new board dates anywhere: every pre-scan candidate was a known false positive (print/review stamps, question and registration deadlines, governors, ICP, mis-yeared tokens, YAS job advert), and Herts Partnership's extra dates are private sessions. Re-verification: 120 checked, 91 confirmed, 20 unverifiable, 4 unreadable, 5 contradicted (the same known matcher artefacts as 22 and 26 Oct: BWC, Black Country ICB, Blackpool x2, Central East ICB; none alerted, kept).

## Papers alerts sent

- Tees, Esk and Wear Valleys (RX3), 28 Oct, 221-page meeting book: 8 LEAD / 8 WW / 5 FOI, to Matt Mathers.
- Mersey and West Lancashire (RBN), 28 Oct, 223-page pack: 4 LEAD / 9 WW / 5 FOI, to Zoe.

Both analysed on Fable from pre-extracted text, quotes checked against the pack text.

## Window meetings still without papers (48 checked, 6 Oct-6 Nov)

- EMAS (RX9) 29 Oct: still the same 10 files; PB/26/192-196 (incl. Thirlwall, BAF) not linked. Supplementary alert still owed when they appear.
- Sheffield Teaching (RHQ) 3 Nov: Papers A-X still plain text, unlinked.
- WMAS (RYA) 28 Oct: agenda only, papers on request.
- SCAS (RYE): page says 28 Oct is the Annual Members Meeting and the next board is 5 Nov (both in state). 28 Oct may need retracting as a board entry; not changed this run.
- Sheffield Children's (RCU) 3 Nov: site timed out on repeat fetches; unconfirmed.
- Pennine (RT2) 7 Oct: still no pack, 20 days on; ages out of the window next week.
- All others: not yet published.

Watchlist: 18 orgs, no new files. Mid Cheshire's 2024-25 folder holds 8 historic bundles not in known_files (historic, not alerted).

## Aged out without papers

None newly aged out since 26 Oct.

## Scan health

## SCAN HEALTH: 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED - failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Guy's and St Thomas' NHS Foundation Trust | RJ1 | Ella | 1 | 2026-10-27 | GSTT site returns "Access forbidden" to headless Chromium on board-meetings and agenda-and |

### ACTION REQUIRED - 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement - it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Guy's and St Thomas' NHS Foundation Trust (Ella) - currently https://www.guysandstthomas.nhs.uk/about-us/our-board/board-meetings
    python org_urls.py set --ods RJ1 --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)


- Board paper machine

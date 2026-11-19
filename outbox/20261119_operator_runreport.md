Hi Henry,

Run report for the 19 Nov board paper machine sweep (live send).

**What ran:** 239 orgs in scope; 162 resolved deterministically by prescan, 77 needed an agent or were no-schedule orgs. 27 new meeting dates, 1 retraction (Gloucestershire 25 Nov 2026, never alerted), 15 packs analysed (16 summary files; Hull and NLAG share one pack). 6 date alerts and 15 papers alerts go to correspondents with this email.

## Needs a human check (correspondents have NOT been told separately)

- **WMAS (RYA) 25 Nov** - Caitlin, Alison. reverify has flagged it missing five times (events page lists 16 Dec, 27 Jan, 31 Mar). The trust's 28 Oct agenda item 14 says next meeting Wed 25 Nov 2026. No pack yet. Not retracted.
- **UHB (RRK) 18 Nov** - Caitlin. Calendar shows a cancer health and wellbeing event, not a board. Date looks wrong. Not retracted.
- **Salisbury (RNZ) 16 Nov** - Joe. Trust schedule page lists 2 Jul, 3 Sep, 10 Nov, 7 Jan 2027 only.
- **Cambridge (RGT) 10 and 16 Nov** - James. 2026 page shows 11 Mar, 10 Jun, 9 Sep, 9 Dec only.
- **Hertfordshire Partnership (RWR) 17 Dec 2026 and 25 Feb 2027** - Emily. Page lists 26 Nov, 28 Jan, 24 Mar; these two have no source.
- **Bridgewater (RY2)** - Zoe. Page does not name Bridgewater in the schedule.
- **South Central Ambulance (RYE) 28 Oct** - Mimi, Alison. Aged out with no papers; recorded date may be wrong.
- **Humber Teaching (RV9)** - you. Page says "Wednesday 25 July 2027", which is a Sunday. Left out; the other five 2027 dates were added.

## Analyser caveats
Several summaries contain figures read from low-resolution images or tracked-changes text and say "check against PDF" beside them (Countess of Chester, Devon Partnership, Surrey and Sussex, Derbyshire). Mersey Care's new-chair lead (Sheena Cumiskey) rests on her own "first 100 days as Chair" line (p.115); not checked against HSJ prior coverage.

## Scan health
## SCAN HEALTH — 0 broken, 2 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED — failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Guy's and St Thomas' NHS Foundation Trust | RJ1 | Ella | 2 | 2026-11-16 | GSTT /about-us/our-board serves Access forbidden even to headed Chrome (known; not re-trie |
| Dartford and Gravesham NHS Trust | RN7 | Alison | 2 | 2026-11-19 | Board minutes/agendas page and the 2026 year-folder navigate/68487/27541 return HTTP 500 ( |

### ACTION REQUIRED — 2 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement — it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Guy's and St Thomas' NHS Foundation Trust (Ella) — currently https://www.guysandstthomas.nhs.uk/about-us/our-board/board-meetings
    python org_urls.py set --ods RJ1 --url <REPLACEMENT> --compare
    # Dartford and Gravesham NHS Trust (Alison) — currently https://www.dgt.nhs.uk/about-us/trust-management/trust-boardmanagement/trust-board-minutesagendas
    python org_urls.py set --ods RN7 --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)


- Board paper machine

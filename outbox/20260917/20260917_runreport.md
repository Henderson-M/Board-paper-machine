Hi Dave,

Board paper machine run report, 17 September 2026.

This was a full sweep run on top of the earlier scan today (17:03), which had found
13 new dates but never sent the alerts or written the .ics files. Those went out in
this run. 239 orgs were pre-scanned deterministically (175 resolved with no model at
all, 64 needed an agent); 48 in-window meetings without a pack in state were checked;
seven packs were found and six analysed.

Emails this run: 7 date alerts, 6 papers alerts, 2 withdrawal alerts, 1 run report.

## New dates, by correspondent

- **Alison**: 3 date(s) - RYA:2027-01-27, RYA:2027-03-31, RYD:2027-02-04
- **Caitlin**: 2 date(s) - RYA:2027-01-27, RYA:2027-03-31
- **Ella**: 4 date(s) - QWE:2026-11-25, RJ6:2027-11-10, RJ6:2028-01-12, RJ6:2028-03-15
- **Emily**: 2 date(s) - S1Y5D:2026-09-25, S1Y5D:2026-12-18
- **Henry**: 2 date(s) - RJL:2026-10-09, RWA:2026-10-09
- **Joe**: 1 date(s) - RNZ:2026-09-17
- **Mimi**: 3 date(s) - RHM:2027-11-11, RHM:2028-01-20, RHM:2028-03-09

## Packs analysed

| Org | Date | To | LEAD | WATCH | FOI |
|---|---|---|---|---|---|
| Sandwell and West Birmingham Hospitals NHS Trust / The Dudley Group NHS Foundation Trust | 16 September 2026 | Caitlin | 10 | 10 | 9 |
| Greater Manchester ICB | 16 September 2026 | Nick | 7 | 7 | 5 |
| Norfolk and Suffolk ICB | 23 September 2026 | James | 8 | 17 | 3 |
| Central London Community Healthcare NHS Trust | 24 September 2026 | Ella | 5 | 8 | 3 |
| Royal Cornwall Hospitals NHS Trust | 17 September 2026 | Joe | 7 | 8 | 9 |
| Shropshire, Telford and Wrekin ICB / Staffordshire and Stoke-on-Trent ICB | 24 September 2026 | Caitlin | 6 | 14 | 5 |

## Withdrawals

- **Alison**: 7 withdrawn
- **Caitlin**: 7 withdrawn

All seven are West Midlands Ambulance. Its stored `url` was the publications archive,
which lists only papers already published, so the date scan never saw a forward
schedule and seven wrong dates accumulated and were emailed. `schedule_url` is now set
to the events page. Note the 29 October entry there is a Council of Governors meeting,
not a board: worth remembering when reading that page.

## Corrections and data fixes landed

- **RYA** West Midlands Ambulance: `schedule_url` set; 7 dates retracted, 2 real ones added.
- **RJL / RWA**: `cluster_id` HUMBER. One Board-in-Common, two ods codes, so Henry was
  about to get the same 9 October meeting twice in his calendar. Now de-duplicated.
- **RNA / RXK**: `cluster_id` DUD-SWB. Both published a byte-identical Group Board pack.
  The arrangement is NOT new: the pack calls it a Committee in Common whose first
  meeting was 20 May, and never uses the word merger. I had inferred it was new from
  the file alone; the analyser corrected that against the pack text.
- **RX3** Tees, Esk and Wear Valleys: `papers_url` 404'd; corrected (56 packs now visible).
- **RNZ** Salisbury: site restructured, `papers_url` corrected.
- **RWF** Maidstone and Tunbridge Wells: `papers_url` 404'd; corrected. The trust posts a
  bare agenda days before the full pack, so filename alone must not be read as published.
- **RR8** Leeds Teaching publishes packs as .zip, which the PDF-only extractor misses.
- **RXR** East Lancashire is now behind Incapsula for all automated traffic.

## Things I did NOT do, and why

- **REM / RBQ Liverpool, 17 Sep**: re-verification called these contradicted. They are
  real: the published pack is titled 'UHLG Board of Directors Public Pack - 17 September
  2026'. The shared page just drops a meeting on the day it happens. Not retracted, and
  annotated so a future run does not retract them either.
- **Medway 23 Sep**: a scan matched `meeting-papers-trust-board-in-public-september-2026.pdf`
  to it on the filename. The document is actually the 2 September board pack (its header
  reads DATE 02/09/2026) and had already been analysed and sent to Alison on 1 September.
  No alert sent; the 23rd is the Annual Members' Meeting and has no pack yet.
- **Shrewsbury and Telford 24 Sep**: Shropshire Community's page mentions an event that
  day, but RXW's own board page does not list it and it reads like an AGM. Not added.
- **Six candidate dates dropped** by the anti-fabrication guard: they were page metadata
  ('Next review due: 4 September 2027'), a news post date, a papers-publication deadline,
  and one bad year inference on a date already in state.

## Still open for a human

- **RXG South West Yorkshire Partnership is BROKEN.** Four routes (requests, Playwright,
  Playwright+landing, WebFetch) all return zero dates and zero documents. The URL has NOT
  moved. Needs an archive route or a manual look. The trust has also restyled itself
  'South West Yorkshire Partnership Teaching NHS Foundation Trust'.
- **Seven watchlist pages could not be read this run** (RJ1, RN7, RNZ, RRJ, RTR, RVW,
  RXG). They were readable on earlier runs, so this may be transient, but a new pack at
  any of them would currently go unnoticed.
- **Greater Manchester**: the NHSE 'at a glance' slide gives the ICB a £175m CIP and
  £42.5m deficit support; the ICB's own month 4 report says £150.0m and £17.7m. Flagged
  in the summary as needing a check with the ICB.
- **Norfolk and Suffolk**: neither published annual report contains the auditor's opinion,
  though both say one is included.
- **RYC East of England Ambulance**: the trust dates its board to 16 September and the AGM
  to the 17th. State holds both; worth reclassifying.

## Scan health

## SCAN HEALTH — 1 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### BROKEN — failed 3+ runs running
These need a human. They have failed every run for a while and are silently contributing nothing.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| South West Yorkshire Partnership NHS Foundat | RXG | Henry | 3 | 2026-09-17 | no dates and no documents |

### DEGRADED — failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| East Lancashire Hospitals NHS Trust | RXR | Zoe | 2 | 2026-09-17 | no dates and no documents |

### ACTION REQUIRED — 2 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement — it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # South West Yorkshire Partnership NHS Foundation Trus (Henry) — currently https://www.southwestyorkshire.nhs.uk/about-us-2/how-were-run/our-trust-board/meeting-papers/
    python org_urls.py set --ods RXG --url <REPLACEMENT> --compare
    # East Lancashire Hospitals NHS Trust (Zoe) — currently https://elht.nhs.uk/about-us/our-trust-board/board-meetings-including-agenda-and-papers
    python org_urls.py set --ods RXR --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

- Board paper machine

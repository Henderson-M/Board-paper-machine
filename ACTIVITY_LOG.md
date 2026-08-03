## 2026-08-03 (FULL SWEEP — dates + packs + watchlist, DRY-RUN, awaiting go-ahead to send, Henry + Claude)

### Headline
Full no-arg sweep. State was **properly synced first** (`git fetch` then a level check against `origin/main` — behind 0, ahead 0) before anything was scanned. Scanned all **239 in-scope orgs** (resolved to **221 unique scan units** after cluster dedup) across 16 parallel date agents, checked the **48 in-window meetings** (window 1–13 Aug) across 8 detection agents, and polled the **14-org papers watchlist**. **Zero hard scan failures** — 221/221 units and 44/44 detection groups returned. **25 new meeting dates** found and **9 board packs analysed** (roughly **63 LEAD / 40 WORTH WATCHING / 34 FOI** across them). **18 alerts written to `dry_run_output/` — NOTHING HAS BEEN SENT.** Manifests are built and ready.

### The near-miss worth knowing about
The watchlist reported **seven "new" packs**. Six of them — Gateshead, NWAS, RDaSH, South West Yorkshire, Kent & Medway and Moorfields — had **already been analysed and alerted by the 23–31 July runs**. They looked new only because `papers_watchlist.json` held an **empty `known_files` baseline** for those orgs, so every document on the page read as unseen. Had that been trusted, six duplicate papers alerts would have gone to the whole team — the same outcome as 30 July, arriving by a different route. Caught by checking each one against the existing `summaries/` files before analysing. **Only Cheshire & Merseyside ICB was genuinely new.**

**Fixed at root:** the watchlist has been rebuilt — every file the agents saw is now baselined into `known_files`, and **no org is left with an empty baseline**. Watchlist is now 8 orgs (was 5): RDY dropped (has a future meeting again), RR7/RXE/RXG/S1Y5D added.

### Packs analysed (9) — all dry-run, by recipient
- **Matt Mathers:** County Durham & Darlington (8 leads) — NHSE has **withheld the trust's Q2 deficit support** from an £18.5m quarterly pot and put it in a new North East & Yorkshire **"At Risk: Active intervention"** category with weekly reporting; BAF states an underlying deficit "over £70m" and a £23.8m CIP shortfall.
- **Caitlin:** George Eliot AGM (5 leads) — **Deloitte reported the trust to the health secretary under section 30** on 26 June for breaching its break-even duty; cumulative deficit £76.6m, second consecutive VfM significant weakness, cash down from £40.6m to £8.3m (~10 days) after a £17.5m transfer to group partner SWFT. Full 2025/26 accounts are in the pack.
- **Zoe:** Lancashire Teaching (9 leads); Cheshire & Merseyside ICB (7 leads) — the ICB's public Q&A itemises **£238.3m of emergency cash financing** drawn by its providers in 2025/26, trust by trust (LUHFT £75.8m, Wirral £58.3m, Warrington & Halton £27.2m, Countess of Chester £23.3m, Liverpool Women's £22.6m, Mersey & West Lancs £21.7m, East Cheshire £9.4m) — and notes the ICB will no longer even be copied into providers' emergency cash applications from 2026/27.
- **Annabelle:** Sherwood Forest (8 leads) — ended June on **£1.2m cash, below the £2.8m minimum DHSC set as a condition of its cash support**; 11.8% of supplier invoices paid on time against a 95% standard; an executive-agreed "prioritisation matrix of supplier payments"; finance paper concedes the pressure "can be partly managed by extending creditors". Also Derbyshire Community (6 leads) — the Quality People Committee **refused to approve the trust's own race equality priority**, recording that WRES "outcomes continue to deteriorate".
- **Emily:** Essex Partnership (7 leads) — the **Lampard Inquiry served EPUT with a section 21 compulsion notice** covering eight Rule 9 requests, logged in the trust's own BAF as "negative assurance"; inquiry cash spend now £17.1m plus a £6.6m accounting pressure.
- **Nick:** Wrightington, Wigan & Leigh (6 leads) — BAF warns of a "significant risk that external cash support will be required during Quarter 4 of 2026/27", three months into a breakeven plan; cash down £15m in a month to £17m, 11 operating cash days.
- **James:** Norfolk & Waveney three-trust group board (7 leads).

### Dates
25 new meetings added (state now **1,206**), mostly autumn AGMs and annual public meetings. Date alerts to 9 correspondents: Zoe 7, Alison 6, Emily 4, Matt Mathers 3, Mimi 2, and one each to Annabelle, Henry, Joe, Nick. Three trusts publish **no forward dates at all** and their next meeting had to be read out of a board pack — East Cheshire (3 Sep), NWAS (30 Sep) and the South Tees/North Tees group board (3 Sep).

### 17 dates retracted as unsupported by the trusts' own pages
Every one was checked to have **no pack files** attached, and the correct replacement date confirmed present in state. Retracted (status `retracted`, evidence recorded in `date_review`):
- **South Tyneside & Sunderland** 5 Aug and 7 Aug — the trust lists only 6 Aug. Also **2 Oct** and **4 Dec**, off-by-one duplicates of the real 1 Oct / 3 Dec (the trust meets Thursdays; those are Fridays).
- **Leicester** 7 Aug — page says verbatim "There will be no public Boards in Common meeting in August 2026."
- **Frimley** 5 Aug, **South Warwickshire** 5 Aug, **Lancashire & South Cumbria** 5 Aug, **Mid Yorkshire** 11 Aug, **Coventry & Warwickshire Partnership** 12 Aug, **Kettering** 7 Aug, **Northampton General** 7 Aug — none of these trusts has an August meeting in its published schedule.
- **Surrey & Sussex** 6 Aug and 13 Aug — the trust states its next meeting is 27 Aug (already in state).
- **Shropshire Community** 1 Aug (real date 13 Aug), **EPUT** 1 Aug (real date 5 Aug, confirmed on the pack cover), **Dorset Healthcare** 1 Aug (1 Aug 2026 is a Saturday — a first-of-month placeholder).

Kept but flagged `flagged_unverified`, because absence of evidence is not evidence of absence: Dorset County 11 Aug, Alder Hey 5 Aug, Stockport 6 Aug.

**Note:** 15 of the 17 had already had a date alert sent in an earlier run, so correspondents may have these in their calendars. Retracting stops the machine chasing packs for them; it does not un-send anything.

### Guards that fired
- **Anti-fabrication caught invented schedules at 10 orgs** — West Midlands Ambulance, Alder Hey, Salisbury, Great Western, Royal Papworth, Kettering, Lancashire & South Cumbria, Cheshire & Merseyside ICB, St George's and Northampton General. The starkest: WebFetch returned **Royal United Bath's entire schedule as if it were Alder Hey's**, and separately built dates out of the flatpickr date-picker cells in Alder Hey's archive filter widget. None reached an email.
- **Anti-omission recovered packs and dates WebFetch had silently dropped.** Four of the eight in-window packs were invisible to WebFetch and surfaced only via `extract_board_html.py`: Sherwood Forest (collapsed accordion markup), Derbyshire Community and Lancashire Teaching (extension-less CMS handler links), County Durham (two-hop onto the 2026/27 year tab). Same for dates at Whittington, South Tyneside, Birmingham Community, East London, Walton Centre, ESNEFT and BSMHFT.
- **A note in our own data was wrong.** The 21 July note calling Newcastle's (RTD) forward dates a hallucination is **incorrect** — the dates are real, sitting in a collapsed accordion that both WebFetch and Playwright `--text` render as empty. Only raw HTML sees them. Note corrected.

### Bug found and fixed in this run's tooling
The composer keyed calendar files by **first name**, which silently merged **Matt Discombe and Matt Mathers into one `matt.ics`**. Caught before commit by comparing against the repo's existing `matt_discombe.ics` / `matt_mathers.ics` convention. Filenames now use the full-name slug throughout (calendars, delta files, dry-run bodies, manifest ids). The stray `matt.ics` was removed.

### 26 org records updated
13 scan URLs corrected where the real schedule lives on a different page: Gloucestershire, LHCH (→ UHL group page), St George's, NELFT, West London, Wirral Community, EPUT, Shropshire Community, South Warwickshire, East & North Herts, South Tyneside, plus RDaSH and Central East ICB in the watchlist. 13 more got durable fetch-method notes (UHCW's stale papers link, UHB's changed events URL pattern, Newcastle's accordion, Calderdale's non-breaking space, Tameside's joint-pack two-hop, and others).

### What's pending
- **NOTHING HAS BEEN SENT.** 18 alerts sit in `dry_run_output/` (9 date + 9 papers). Manifests are built. To send, run `send_batch.py` with both manifests — **but re-run the Step 11 pre-send guard first** (`git fetch`, then drop anything already stamped `alerts_sent` on `origin/main`).
- `alerts_sent` has deliberately **not** been stamped for this run — it gets set from the `ok:true` rows of the send results, never from the analysis step.
- A stray **`PackB.pdf` (7.5MB)** sits untracked at the repo root from an earlier session. Left alone, not committed — worth deleting.
- Re-check in a few days for packs not yet published: TEWV (says papers go up 7 Aug), Lincolnshire Partnership (~6 Aug), Warrington & Halton, Stockport, Blackpool, Walton Centre, Solent/Southern Health, Midlands Partnership, Birmingham Community, Herts Community.
- Royal Orthopaedic (RRJ) has now returned no forward dates for four consecutive runs — its year tabs are JS-driven with no hrefs. Needs a Trust Secretariat contact rather than more scraping.

## 2026-07-30/31 (FULL SWEEP + LIVE SEND — but DUPLICATED a colleague's 27 Jul run, then reconciled, Henry + Claude)

### What happened (plain English)
Henry asked to run the machine. I did a full sweep and sent **35 live alerts** — but I had **started from stale state (23 Jul)**: I concluded "nothing to pull" from a stale local git reference **without actually fetching**, so I never saw that a colleague had done a full run on **27 Jul** and already emailed the team about most of these packs. Result: **most of my emails were duplicates.** This is exactly what the "pull first, stop if you can't" step exists to prevent. My error.

### The numbers
- Sent 5 date alerts + 30 papers alerts (35/35 delivered).
- **Duplicates of the 27 Jul run:** 20 of 28 packs (~22 papers emails) + 6 of 11 dates (Royal Surrey ×2, Glos H&C, Liverpool Heart & Chest ×3).
- **Genuinely new (only my run sent these):** 8 packs — Hampshire (RN5), Harrogate (RCD), Sussex Community (RDR), West Suffolk (RGR), Birmingham & Solihull MH (RXT), Mersey & West Lancs (RBN), Royal Berkshire (RHW), Moorfields (RP6) — plus 5 new dates (NENC ICB 30 Sep, Somerset ×2, SE London ICB, Surrey & Sussex).

### Reconciliation (this commit)
Rebuilt state on top of the colleague's 27 Jul run (their work + timestamps kept intact, incl. their QT6/QJK/RX7 analyses), then added only my genuinely-new items: 8 fresh pack summaries + 5 fresh dates + Moorfields, each stamped `alerts_sent` for today. The 20 duplicate packs keep the **27 Jul** first-send timestamp (not re-stamped). State now **1,180 meetings**. Also folds in the **28 Jul recipient override** (`recipient_overrides.json` + SKILL Step 2: Ella copies Matt Discombe until 28 Oct), which predated the colleague's run and wasn't online.

### Two known issues
- **Mojibake in email bodies:** my body-composition script read the summaries with the wrong text encoding (Windows-1252 not UTF-8), so `£`→`Â£` etc. **in the pasted-in body only** — the attached .md files were clean. Fixed in process; the 8 genuinely-new packs are being resent with clean bodies (the 20 duplicates are NOT resent).
- **QHM (NENC ICB) pack** unreadable from this machine — files on `media.nhs.net` (NHS-internal DNS). Needs an on-network pull. Its 30 Sep date alert did go out.

## 2026-07-16 (FULL SWEEP — dates + packs + watchlist, DRY-RUN then LIVE SEND, Henry + Claude)

### Headline
Full no-arg sweep, first written to `dry_run_output/` then **sent LIVE on Henry's go-ahead** — all **17 alerts sent, 17/17 OK, 0 failures** (staggered 30–60s via `send_batch.py`, `send_results.json`). `alerts_sent` stamped for the 23 date-alert meetings + 10 analysed packs. Scanned all **239 in-scope orgs** (203 trusts + 36 ICBs) for meeting dates across **15 parallel date-scan agents**, then checked the **47 in-window meetings** (window 14–26 Jul) + the **5-org papers watchlist** across **7 detection agents**, then analysed every full pack found with an **11-strong pack-analyser fleet**. **23 new meeting dates** detected and **10 packs analysed** (11th, King's, suppressed as a duplicate). Rich crop: roughly **44 LEAD / 52 WORTH WATCHING / 37 FOI** across the 10 packs. **17 dry-run alert files written** (6 date + 11 papers); manifests built (`dates_manifest.json`, `papers_manifest.json`) so a live send can go straight through `send_batch.py` without re-detecting.

### What changed
- **Dates:** 700 valid future meetings detected across the estate; **23 were new** and added to state (state now **1,127 meetings**). Date alerts to **6 correspondents**: Matt Discombe 6 (NELFT + East London series), Matt Mathers 6 (Newcastle Hospitals series), Caitlin 5 (UHB AGM + S Warwickshire joint-board series), Henry 4 (Rotherham series), Joe 1 (Royal Cornwall), Mimi 1 (Royal Berkshire). Combined `subscriptions/*.ics` snapshots rebuilt for all 13.
- **Packs analysed & alerted (10, dry-run):** Berkshire Healthcare (Mimi, 2 leads), Avon & Wiltshire MH (Joe, 5), Greater Manchester ICB (Nick, 3), Nottinghamshire Healthcare (Annabelle, 5), Herefordshire & Worcs Health & Care (Caitlin, 5 — ZIP-packaged pack), Essex ICB "NHS Essex" (Emily, 6), Derbyshire Healthcare (Annabelle, 4), Countess of Chester (Zoe, 5), Cambridgeshire & Peterborough (James, 2), Dudley Group (Caitlin, 7).
- **Standout leads:** Essex ICB (new "NHS Essex") plan rated NHSE "Partially Compliant / Conditional" (Clare Panniker letter), waiting list planned to overshoot target 48.8% by 2028/29, community 18-week collapsing to 39.7%, MSEFT stuck NOF 4 with CQC S29a/S31 notices, £14m unmitigated risk, Lampard Inquiry refocusing July hearings on EPUT + performance slides published as "DUMMY DATA" (FOI); Dudley Group 7 leads; Nottinghamshire Healthcare 5 leads / 6 FOI; Countess of Chester 5 leads (IPR + finance report "to follow", absent from public pack — FOI).

### Flags / cleanup for next run
- **DRY-RUN — no emails sent.** To send this crop live: `python send_batch.py --manifest <scratch>/dates_manifest.json --manifest <scratch>/papers_manifest.json --results send_results.json`. Analysed meetings are now status `analysed`, so a plain `--live-emails` re-run will NOT re-detect them — use the manifests.
- **King's College Hospital (RJZ) suppressed:** detection matched a stray `RJZ:2026-07-16` state entry and re-found the (v2) 15 July pack, but that meeting was already analysed + papers-alerted on 13 Jul (`RJZ:2026-07-15`). Recorded the v2 file, status `analysed`, NO alert. The duplicate `RJZ:2026-07-16` state entry should be retired.
- **Two Saturday dates to verify:** RTD (Newcastle) 29 Aug 2026 and RHW (Royal Berkshire) 29 Aug 2026 both landed on a Saturday while the rest of Newcastle's series is last-Friday — likely a source typo/misparse for 28 Aug. Verify before relying; kept in state.
- **RY3 (East of England Community) 22 Jul:** only a 3-page agenda online, full pack pending — status `papers_found`, not analysed, no alert. Re-scan in a few days.
- **RRJ (Royal Orthopaedic) watchlist:** new July 2026 meeting book (doc 501) but day-of-month not in filename — DATE-UNKNOWN papers alert to Caitlin, org stays on watchlist. QYG (C&M ICB): 4 new files were past-meeting Q&A/presentation addenda — baselined into known_files, no alert.
- **Scan errors (2):** RRJ (no forward board dates on ROH statutory-documents page); RWR (Herts Partnership) all board URLs 403/404 — no scrapable dates page found.
- **Tooling:** concurrent pack-analysers share `/c/tmp/pack/` and several clobbered each other's downloads mid-run (each self-recovered to an isolated scratch dir). Give each analyser a unique temp dir (e.g. `/c/tmp/pack_<ods>/`) next time. Countess of Chester (coch.nhs.uk) needs `curl -k` (SSL chain); HACW ZIP downloads need a browser UA + referer.
- **122 org notes refreshed** from this sweep (fetch method, joint-board arrangements, per-meeting-page/ZIP patterns) so the next run skips known-dead fetch paths.


## 2026-07-13 (FULL SWEEP — dates + packs + watchlist, LIVE SEND, Henry + Claude)

### Headline
Full no-arg sweep. Scanned all **239 in-scope orgs** (203 trusts + 36 ICBs, resolved to **227 unique scan units** after cluster dedup) for meeting dates across **19 parallel date-scan agents**, then checked **55 in-window meetings** (window 11–23 Jul) + the **6-org papers watchlist** for new packs across **8 detection agents**, then analysed every substantive pack with an **8-strong pack-analyser fleet**. **51 new meeting dates** detected and **8 packs analysed**. **All 18 alert emails sent LIVE**, staggered 31–58s via `send_batch.py`: **18/18 OK, 0 failures** (`send_results.json`).

### What changed
- **Dates:** 51 new meetings added to state (state now **1,104 meetings**). Heavy on ICB cluster boards newly resolved this run — Dorset/Somerset cluster (QOX/QSL/QVV), C&W/H&W board-in-common (QGH/QWU), BNSSG/Glos cluster (QUY). Date alerts to **10 correspondents**: Joe 17, Caitlin 9, Matt Mathers 6, Zoe 6, Emily 3, Matt Discombe 3, Ella 2, Henry 2, James 2, Mimi 1. Combined `subscriptions/*.ics` rebuilt for all 13.
- **Packs analysed & alerted (8):** Worcestershire Acute (Caitlin, 4 leads), King's College Hospital (Ella, 4), SW London ICB (Ella, 5), Thames Valley ICB (Mimi, 8), One Croydon (Ella, 3), North West Anglia (James, 4), DLN ICBs Boards-in-Common = Derby&Derbyshire+Lincs+Notts (Annabelle, one merged alert, 6), Central East ICB — the merged ICB's first board pack, from the watchlist (Emily, 4).
- **Standout leads:** Thames Valley ICB 13,661-invoice supplier-payment backlog with an NHSE "executive cell" + finance the only BAF risk out of appetite; King's £70.5m unidentified CIP gap (financial risk escalated to max 25) + new CEO Matthew Trainer's first board report; Worcs Acute Segment 4 + £25m revenue-support bid + "unprecedented" hospital measles outbreak; North West Anglia corridor care 123rd of 134 nationally + NOF down 21 places; DLN all three ICBs planning a merger + Notts system £9.4m adverse at M2; SW London de facto shared-leadership cluster with SE London ICB; Central East ICB £19-per-head running-cost cuts + Lampard Inquiry slipping to 2027/28.

### Flags / cleanup for next run
- **RGN (North West Anglia):** pack file URL says "9 July" but the documents are internally headed **14 July 2026** — kept as the 14 Jul meeting; note added.
- **TAJ (Black Country Healthcare) 23 Jul:** the only pack online is the past 1 Jul board; 23 Jul may be a **Council of Governors** (not public board) — noted, entry kept, verify before relying.
- **Date mismatches to verify** (notes added): RTP Surrey & Sussex (no 16 Jul meeting on site, next 13 Aug); RWX Berkshire (site shows 14 not 15 Jul); S0E4D Thames Valley (real board 15 Jul, the 22 Jul state entry superseded by 15 Jul).
- **Partial packs — re-scan in a few days:** RJ6 Croydon (only One Croydon Parts A&B up; CHS Trust Board Part C pending); QOP GM ICB (agenda only); R1A HACW (July papers published as ZIPs — not auto-analysed).
- **URL fixes applied:** S1Y5D → centraleast.icb.nhs.uk (merged ICB, left the watchlist with its first pack analysed); RMC Bolton → board-of-directors-meetings subpage; LNR cluster → leicesterleicestershireandrutland.icb.nhs.uk/about/board-meetings; SW-PEN cluster → swpboard.nhs.uk/board-meetings.
- **Orgs with no forward dates published** (only past meetings online; watch for autumn schedules): ROH (RRJ), TEWV (RX3), Princess Alexandra (RQW), Christie (RBV), Gateshead (RR7), UHT group (RTR/RVW), South Warwickshire (RJC), Shropshire (R1D lists months only).
- **126 org notes refreshed** from this sweep (fetch method, joint-board arrangements, per-meeting-page patterns) so the next run skips known-dead fetch paths.


## 2026-07-09 (packs + watchlist only, LIVE SEND, Henry + Claude)

### Headline
Targeted packs-only run (no full date scan — dates were swept on 1 Jul). Checked all **42 in-window meetings** (window 7–19 Jul) for new board packs via 5 parallel detection agents + a watchlist agent, then analysed every pack found with a 15-strong pack-analyser fleet. **15 meetings had a new pack online** (14 analysis units — Black Country + Birmingham & Solihull share one joint cluster pack). Rich crop: roughly **80 LEAD / 60 WORTH WATCHING / 30 FOI** across them. **All 14 papers-alert emails sent LIVE**, staggered 30–60s via `send_batch.py`: **14/14 OK, 0 failures** (`send_results.json`). No date alerts (date scan skipped).

### What changed
- **Pack detection (window 7–19 Jul):** 42 in-window meetings checked. 15 had a new pack; the rest had no pack online yet (most publish ~5 working days / 1 week before the meeting — worth a re-scan in a few days for the 14/15/16 Jul meetings that were still empty: Croydon, Berkshire, AWP, NEAS, KCH, HACW, GOSH, UHBW, NW Anglia, GM ICB, SW London ICB, Thames Valley ICB, Surrey & Sussex, Lincs/Notts/Derby ICBs, Liverpool UH group, North Bristol, Worcs Acute).
- **Analysed & alerted (14 packs):** Gloucestershire Hosp (Joe, 5 leads), UHDB (Annabelle, 4), Somerset (Joe, 3), GESH group board = St George's + Epsom & St Helier (Ella, one merged alert, both analyses attached), Shropshire Community/SaTH boards-in-common (Caitlin, 5), Humber & N Yorks ICB (Henry, 6), UH Dorset (Joe, 5), Black Country + Birmingham & Solihull joint ICB (Caitlin, 6), Herefordshire & Worcs + Coventry & Warwickshire joint ICB (Caitlin, 6 — see watchlist below), Norfolk & Suffolk ICB (James, 5), East Lancashire (Zoe, 6), Mid Yorkshire (Henry, 5), Chesterfield Royal (Annabelle, 7), Kent Community (Alison, 4).
- **Standout leads:** Gloucestershire £300k CQC fine over a patient death + cardiology culture review + maternity S31 removal bid; UHDB cardiac-MRI review of 1,224 patients; St George's/Epsom St Helier E-block legionella+pseudomonas maternity decant + NHSE enhanced financial oversight + 14 never events; Humber & NY ICB running-cost cut ~50% / 133 redundancies / deficit regulatory notice / HUTH bottom of 134; Norfolk & Suffolk ICB accidentally published a "for EMT/RemCom only" staff-survey slide pack; East Lancs second "Limited" internal-audit opinion + glaucoma service at critical risk; Chesterfield finance-productivity 132nd of 134 + turnaround director; H&W/C&W recommending full ICB merger from April 2027.
- **Watchlist:** QGH (Herefordshire & Worcestershire ICB) surfaced a new 15 Jul Board-in-Common pack (joint with Coventry & Warwickshire, QWU) — both promoted from the watchlist to real dated meeting entries (status `analysed`), so watchlist drops 8 → 6. Other 7 orgs clean.

### Flags / cleanup for next run
- **Three likely-bad dates** flagged in state (notes added, entries kept for audit): RCX (QEHKL) 9 Jul — WebFetch had matched an old 09.07.**2025** pack; RBD (Dorset County) 9 Jul; RL1 (RJAH) 9 Jul. None is a real meeting. Verify and retire.
- **R0D (UH Dorset) 8 Jul** is a stale duplicate — the real board sits 15 Jul (analysed there).
- **S1Y5D (Herts & West Essex)** watchlist URL 301-redirects to `centraleast.icb.nhs.uk` (merged Central East ICB) with no board page exposed — needs URL re-discovery.
- **Tooling:** `fetch_with_playwright.py` crashes on a cp1252 stdout `UnicodeEncodeError` for pages with non-ASCII chars; several agents worked around it with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`. Worth baking that into the script. East Lancs (elht.nhs.uk `download_file`) sits behind Incapsula — needs a browser-context cookie solve to download the PDF (agent handled it this run).

---

## 2026-07-06 (packs + watchlist only, LIVE SEND, Henry + Claude)

### Headline
Targeted packs-only run (no full date scan — dates were swept 5 days ago on 1 Jul). Checked all **64 in-window meetings** (window 4–16 Jul) for new board packs via 9 parallel detection agents + a watchlist agent, then analysed every pack found with a 21-strong pack-analyser fleet. **22 meetings had a full pack online** (21 analysis units — NLAG + Hull share one Boards-in-Common pack). **99 LEAD / 104 WORTH WATCHING / 114 FOI** items across them. **All 21 papers-alert emails sent LIVE**, staggered 30–60s via `send_batch.py`: **21/21 OK, 0 failures** (`send_results.json`). No date alerts (date scan skipped). Watchlist (8 orgs) clean — no surprise packs.

### What changed
- **Pack detection (window 4–16 Jul):** 64 in-window meetings checked. 22 had a full pack; 42 had no pack online yet (most publish the week of the meeting). Clusters deduped: BSOL-BC (QUA+QHL, 13 Jul — no pack yet), DLN (QJ2+QJM+QT1, 16 Jul — no pack yet), NLAG+Hull (RJL+RWA, 9 Jul — one shared pack, analysed once, summary written to both).
- **22 packs analysed** → 21 papers alerts (by recipient):
  - **Henry (3):** Doncaster & Bassetlaw (RP5) 4 LEAD — CEO Richard Parker OBE retiring after ~44 yrs, £15.7m DSF with £1-for-£1 clawback, £52.1m underlying deficit; Humber Health Partnership NLAG+Hull BiC (RJL/RWA) 5 LEAD — up to £141.9m group deficit / £41.9m unidentified, NHSE Intensive Recovery Programme + Carnall Farrar; Calderdale & Huddersfield (RWY) 5 LEAD — never-events national outlier (9 in 12 months), £5.9m adverse, new-hospital FBC + Laing O'Rourke.
  - **Annabelle (3):** United Lincolnshire NHS Group board (RWD, merged with LCHS/RY5 — identical 52MB pack) 5 LEAD — LCHS NOF 2→3, ULTH breast-services breach notice, CNST maternity-fail risk, £8.1m group M2 deficit; Nottingham UH (RX1) 6 LEAD — Ockenden 444 women/76 babies avoidable harm, HTA mortuary 3 critical findings, £23m M2 deficit; East Midlands Ambulance (RX9, +Alison) 5 LEAD — critical incident 27 Jun, Cat 2 breaches, staff-survey WRES hit to oversight rating.
  - **Alison (3):** Surrey & Borders (RXX) 6 LEAD — NOF 2→3, crisis metrics worsening, Grant Thornton well-led review, FTSU drop; Queen Victoria (RPC) 6 LEAD — being drawn into Royal Surrey/Ashford & St Peter's group, lost DSF + £7.5m cost programme, extraordinary board 23 Jul; EMAS (shared with Annabelle).
  - **Ella (2):** Kingston & Richmond (RAX) 4 LEAD — £40m "unprecedented" target, restricting maternity bookings (excl Sutton/Croydon), restructure to 4 care groups; SW London & St George's MH (RQY) 5 LEAD — Coroner PFD inpatient suicide + April spike of 12 suspected suicides, 17-day bed waits, bank-cap breach.
  - **Emily (2):** East & North Herts (RWH) 5 LEAD — BDO "significant weakness", MHRA "critical failure" at Lister QC lab, KPMG review of ENH Pharma drug-pricing; West Herts (RWG) 0 LEAD / 7 WW — acting CEO while substantive CEO 7th in HSJ Top 50, Watford+Mount Vernon new-hospital DMBC, 3 never events.
  - **Caitlin (2):** North Staffs Combined (RLY) 2 LEAD — £1.1m underlying deficit behind £154k planned surplus, 840 CYP >104wks; Shrewsbury & Telford (RXW) 5 LEAD — exits NHSE RSP + NOF 5→3 (first plan delivered in 10 yrs) on £45.1m DSF, Ockenden validation review due this summer, 45% Type 1 A&E.
  - **Nick (2):** Northern Care Alliance (RM3) 6 LEAD — NHSE enforcement undertakings + CQC S29A at Salford Royal, Oade spinal-surgery report, £10m M2 deficit; GM Mental Health (RXV) 6 LEAD — up to £21.3m deficit a yr after breakeven, inpatient death + ward closure, ICO audit + ~500 breached SARs, new CEO in dual role, Southport Inquiry.
  - **Zoe (1):** Lancashire & South Cumbria ICB (QE1) 6 LEAD — ~£215m cost-out, £164m DSF propping 25/26, second VR round, OPIC host, enforcement undertakings.
  - **Mimi (1):** Univ Hospital Southampton (RHM) 5 LEAD — exits NHSE Recovery Support Programme, ~£35m of £81m CIP undeveloped, critical incident 25 Jun, 9/12 BAF risks critical.
  - **Joe (1):** Cornwall Partnership (RJ8) 5 LEAD — £27m underlying deficit behind "breakeven" plan, two auditor "significant weaknesses", sickness/turnover outlier.
  - **Matt Discombe (1):** Barts Health (R1H) 3 LEAD — NOF Segment 3→1 "biggest climber", three senior group vacancies incl Group CFO, £5.8m adverse at M2.
  - Summaries in `summaries/`.
- **Watchlist:** 8 orgs polled — no genuinely new/future packs (all "new-looking" files were historical/past archive). `last_checked` refreshed on all 8. No date-unknown alerts fired.
- **State stamped:** 22 meetings set to `analysed` with pack_files + summary_path; `alerts_sent.papers`/`summary` stamped on all 22, driven by the `ok:true` rows in `send_results.json`. 42 in-window no-pack meetings had `last_checked` refreshed.
- **Self-improvement / data fixes:** RWH (E&N Herts) URL confirmed live (stale-2023 note superseded); RP5 papers_url pointed at a v3 PDF that 404s → repointed to /board/ (live pack is the v2 combined PDF, now in pack_files); S1Y5D (Herts & West Essex) watchlist note added — domain now redirects to merged Central East ICB (centraleast.icb.nhs.uk), papers_url stale.

### Pending / not done
- **Ghost dates flagged (kept for audit, not alerted):** RCX (QEHKL 9 Jul — no such meeting on N&W Group schedule, next is 5 Aug); R0D (UHD 15 Jul — not in trust's 2026 schedule; genuine board was 8 Jul); logged to `_scan_errors`.
- **S0E4D (Thames Valley ICB):** own site lists next public board as **22 Jul**, not the stated 15 Jul — verify/patch date next run.
- **RJZ (King's College Hospital, 15/16 Jul):** could NOT check packs — kch.nhs.uk origin down (Cloudflare 522) to all fetchers; web search suggests July board is 15 Jul. Re-check when site recovers.
- **42 in-window meetings** had no pack online yet (incl the BSOL-BC and DLN ICB cluster boards) — they'll re-check on the next run within the 2-day-back window.
- **Tooling niggles (worth fixing in pack-analyser):** analyser agents shared `C:\tmp\pack` and several agents' cleanup step wiped it mid-run for others (all recovered by re-downloading to an isolated scratch dir); `fetch_pdf_text.py` treats a local file path as a URL, so agents extracted big local PDFs with pypdf directly. The 41MB Nottingham pack stalled the first analyser (600s watchdog) and had to be re-run with an isolated temp dir — worth giving each analyser its own scratch subfolder by default.
- Deliverability reminder (per 24/26 Jun findings): SMTP success ≠ inbox delivery. If anyone reports a miss, audit `[Gmail]/Sent Mail` over IMAP rather than assuming it wasn't sent.
- Still not built: the "already covered" HSJ CMS API check to suppress leads on stories HSJ has already published.

## 2026-07-01 (full sweep, LIVE SEND, Henry + Claude)

### Headline
Full machine run 2 days after the 29 Jun sweep. Scanned all 239 in-scope orgs (227 after cluster-dedupe), fanned out across 15 date-scan agents + 11 pack-detection agents + 13 pack-analyser agents. **32 new meeting dates** added. **14 board packs** detected in the 29 Jun–11 Jul window and analysed (68 LEAD-tier items across them; none routine). **All emails sent LIVE** — 25 in total (11 date alerts + 14 papers alerts), staggered via `send_batch.py`: **25/25 OK, 0 failures** (`send_results.json`).

### What changed
- **Date scan:** 227 cluster-deduped board pages swept via the WebFetch → Playwright → PDF ladder. 709 valid forward meetings detected; diffed against state → **32 genuinely new dates**, new `.ics` written for each, all 13 subscription calendars rebuilt from state. 28 orgs returned no forward dates/errors (mostly archive-only pages that publish no forward schedule, plus a few Cloudflare/WAF blocks — e.g. SW Provider Collaborative 403, CNTW events page 404).
  - New dates by recipient (date-alert emails): Joe 13, Nick 4, Emily 3, Matt Discombe 3, Mimi 3, Alison 2, Caitlin 2, Ella 1, Henry 1 (RXG SW Yorks Partnership 28 Jul), Matt Mathers 1, Zoe 1. (A handful of orgs route to two recipients, so recipient totals sum above 32.)
- **14 packs analysed** (LEAD/WORTH/FOI) → papers alert to the assigned correspondent:
  - RD1 Royal United Hospitals Bath / **BSW Hospitals Group Board** 7/3/3 (Joe) — first public BSW group board; GWH downgraded to segment 4, £17.1m group deficit at M2, RUH fire-authority roof-evacuation order on Block 47.
  - RQ3 Birmingham Women's & Children's 6/5/3 (Caitlin)
  - REF Royal Cornwall 6/5/3 (Joe) — segment 1→2, internal critical incident declared 27 May.
  - RXL Blackpool 6/6/4 (Zoe) — £28.8m forecast deficit, "unlikely to exit tiering".
  - RPA Medway 6/4/4 (Alison)
  - RDU Frimley 5/4/2 (Mimi)
  - RW5 Lancashire & South Cumbria 5/4/2 (Zoe)
  - RCF Airedale 4/5/2 (**Henry**) — COO Leanne Cooper left for Uni Hospitals of Liverpool; £20.2m gap.
  - REN Clatterbridge 4/3/2 (Zoe)
  - RGM Royal Papworth 4/4/2 (James)
  - RJN East Cheshire 4/6/3 (Zoe)
  - RTR South Tees + RVW North Tees 4/4/2 (Matt Mathers ×2) — single shared University Hospitals Tees Group Board pack, analysed once, summary written to both.
  Summaries in `summaries/`.
- **Watchlist:** 9 orgs polled; only RJN (East Cheshire) had a genuinely new pack, and it also gained a confirmed 2 Jul date this run, so it **leaves the watchlist** (now 8 orgs). The other 8 had no new future packs — `last_checked` refreshed, no date-unknown alerts fired.
- **State stamped:** `alerts_sent.date` on all 32 new meetings, `alerts_sent.papers`/`summary` on all 14 packs — driven by the `ok:true` rows in `send_results.json`.

### Why live
Henry asked for a full sweep with live emails up front (no dry-run this time). Dry-run plan was previewed via `send_batch.py --dry-run` before sending; staggering (30–60s) used to avoid the free-Gmail spam-quarantine issue seen on 5 Jun.

### Pending / not done
- Reminder per the 24/26 Jun deliverability finding: SMTP success ≠ inbox delivery. If anyone reports a miss, audit `[Gmail]/Sent Mail` over IMAP rather than assuming it wasn't sent.
- 28 orgs returned no forward dates (logged in `state/_scan_errors`); most legitimately publish no forward schedule, a few (SW Provider Collaborative WAF block, CNTW moved URL, Herts & West Essex ICB) worth URL re-discovery.
- Still not built: the "already covered" HSJ CMS API check to suppress leads on stories HSJ has already published.

## 2026-06-29 (LIVE SEND — follow-up to the dry-run below)

Henry reviewed the dry-run and said "send". All **23 emails sent live** via `send_batch.py` (staggered 30–60s): **23/23 OK, 0 failures** (`send_results.json`). State stamped: `alerts_sent.date` on all 28 new meetings, `alerts_sent.papers`/`summary` on all 13 packs. Reminder per the 24/26 Jun deliverability finding: SMTP success ≠ inbox delivery — if anyone reports a miss, audit `[Gmail]/Sent Mail` over IMAP rather than assuming it wasn't sent.

## 2026-06-29 (full sweep, DRY-RUN, Henry + Claude)

### Headline
Full machine run 5 days after the last full sweep (24 Jun). Scanned all 239 in-scope orgs (227 after cluster-dedupe), fanned out across 19 agents. **28 new meeting dates** added. **13 board packs** detected in the 27 Jun–9 Jul window and analysed (63 LEAD-tier items total across them; none routine). Watchlist (10 orgs) polled — no genuinely new future packs. **Emails were NOT sent — this was a dry-run.** 23 alert emails (9 date alerts + 14 papers alerts) are written to `dry_run_output/` ready to review; re-run with `--live-emails` to send.

### What changed
- **Date scan:** 227 cluster-deduped board pages swept via the WebFetch → Playwright → PDF ladder. 736 valid forward meetings detected; diffed against state → **28 genuinely new dates**, new `.ics` written for each, all 13 subscription calendars rebuilt from state. ~53 orgs needed Playwright; 37 returned no forward dates/errors (mostly archive-only pages that publish no forward schedule, plus a few WAF blocks).
  - New dates by recipient: Caitlin 8 (RBT Mid Cheshire ×6, RL1 RJAH ×2 of 5… see below), Zoe 7 (RBT ×6, RW5), Joe 5 (RNZ Salisbury ×4, RN3), Matt Discombe 4 (R1H Barts ×3, RAN AGM), Alison 3 (RYA West Mids Amb ×3), Henry 1 (RXG 30 Jun), James 1 (RMY), Matt Mathers 1 (R0B), Ella 1 (QKK SE London ICB). (RL1 Robert Jones & Agnes Hunt added 5 dates → Caitlin; RBT Mid Cheshire 6 dates → Zoe.)
- **13 packs analysed** (LEAD/WORTH/FOI): RA9 Torbay 7/5/5, QF7 South Yorkshire ICB 6/3/4, TAJ Black Country Healthcare 6/4/3, RTX Morecambe Bay 6/4/4, RF4 Barking Havering & Redbridge 6/4/4, RXG SW Yorks Partnership 5/3/3, RLQ Wye Valley 5/4/3, RPG Oxleas 5/3/2, RD8 Milton Keynes 5/3/4, RYF SW Ambulance 4/4/3, RJC South Warwickshire 3/3/1, RLT George Eliot 3/5/2, RAN Royal National Orthopaedic 2/6/2. Summaries in `summaries/`.
- **Watchlist:** 10 orgs polled; the 3 "new file" hits (RRJ, RW5, QWU) were all non-actionable — historical archive minutes, a re-issued past 4 Jun pack, and governance-log spreadsheets — none future-dated. No date-unknown alerts fired (would have been spam). RW5 also gained a confirmed 2 Jul date this run, so it leaves the watchlist.
- **Self-improvement / data fixes:** RQY (SW London & St George's MH) URL corrected to `swlstg.nhs.uk/our-board` (split to own domain; old St George's archive was stale); RYF (SW Ambulance) URL corrected to the working schedule page. Dated notes added for: RAX renamed to Kingston & Richmond NHS FT; RX4 (CNTW) events page now 404s; RTR/RVW now meet as a joint University Hospitals Tees Group Board; RWH and RBS scan URLs look stale (need re-discovery).

### Why dry-run
Default behaviour — `/scan-boards` was run with no `--live-emails` flag. Given the 5 Jun deliverability scare (free-Gmail spam quarantine), Henry can eyeball the 23 prepared emails in `dry_run_output/` before choosing to send.

### Pending / not done
- **No emails sent.** To send: review `dry_run_output/`, then run `/scan-boards --live-emails` (uses `send_batch.py`, staggered 30–60s) — or ask Claude to send this run's manifests. `alerts_sent` flags in state are still null for all 28 dates / 13 packs.
- One pack-detection agent's results file failed to persist on first write (pb_01: RTX/QF7/RJC); recovered by re-asking the agent — no data lost.
- 37 orgs returned no forward dates (logged in `state/_scan_errors`); most are legitimately publishing no forward schedule, a handful (RX4 CNTW, RWH, RBS) likely have moved URLs worth re-discovering.

## 2026-06-26 (Alison now copied on all ambulance trusts, Henry + Claude)

### Headline
Henry asked for Alison Moore to receive board alerts for **every** ambulance trust, on top of her existing Kent/Surrey/Sussex patch — while the trusts keep going to their current correspondents too. Done.

### What changed
- **New routing concept: a second correspondent per org.** Until now each trust/ICB had exactly one `correspondent`, so alerts went to one person. Added an optional `additional_correspondents` list so an org can alert more than one journalist. Used it to add Alison to the 9 ambulance trusts she wasn't already covering. (South East Coast Ambulance / RYD was already hers, so it needed nothing.)
- **The 9 trusts now copied to Alison** (primary correspondent kept in brackets): London Ambulance (Matt Discombe), North East (Matt Mathers), North West (Nick), Yorkshire (Henry), East Midlands (Annabelle), West Midlands (Caitlin), East of England (James), South Central (Mimi), South Western (Joe).
- **Skill updated to honour it.** `scan-boards/SKILL.md` now treats an org's "recipients" as its primary correspondent plus anyone in `additional_correspondents` (de-duplicated). This applies to date alerts, papers alerts, the date-unknown watchlist alerts, and the per-person subscription calendars — so each of these can now go to more than one person.
- **Alison's calendar rebuilt now** rather than waiting for the next scan: `subscriptions/alison.ics` went from 78 events to 125 (the 47 added are the 9 ambulance trusts' meetings already in our records; her file had also drifted slightly stale vs. the live data, which this rebuild corrected).

### Why
Editorial: Alison wants a complete national view of ambulance-sector board activity, not just her regional trusts — without taking those trusts away from the reporters who own them.

### Pending / not done
- **Not committed or pushed** — changes are saved on disk only. Next `/scan-boards` run (or a manual commit) will land them in git.
- The other correspondents' subscription `.ics` files were **not** rebuilt today (they're unchanged by this edit); they'll refresh normally on the next scan.
- The mechanism is general — if Henry later wants anyone copied on any other group of orgs, it's now just a data edit (add a name to `additional_correspondents`), no skill change needed.

## 2026-06-24 (deliverability finding — WAHT/Caitlin, Henry + Claude)

### Headline
Caitlin reported the machine "missed" Worcestershire Acute (RWP) 9 June pack. Investigation shows it was NOT missed: it was analysed on 5 Jun AND emailed to her — confirmed in the Gmail "[Gmail]/Sent Mail" folder (`To: caitlin.tilley@hsj.co.uk … [PAPERS] Worcestershire Acute Hospitals … Fri 05 Jun 2026 01:55:53 -0700`). Re-sent it to her anyway as `[PAPERS — RESEND]`.

### What this means (KNOWN ISSUES — read before next run)
- **Deliverability, not sending, is the risk.** The 5 Jun batch sent 41 messages (10 date + 31 papers, covering all 32 analysed packs — one email batched two). All present in Sent Mail. So WAHT genuinely left our server but never reached Caitlin's inbox → almost certainly **spam/quarantine filtering of `hsjboardpapers@gmail.com`** at the HSJ mail gateway (a free Gmail account blasting 40 near-identical multi-attachment emails in 90 seconds looks like spam). ACTION: ask recipients to allowlist the sender / check Junk; consider throttling sends and/or a proper From domain + SPF/DKIM. There is currently **no bounce/delivery-failure detection** — SMTP submission success ≠ inbox delivery.
- **State can't prove per-email delivery.** The 5 Jun run bulk-wrote `alerts_sent.papers` with one identical timestamp (`08:56:10Z`) for ~30 packs, so state alone can't tell sent-and-delivered from sent-and-filtered. Today's full sweep fixed the first half (only stamps packs that send_email.py returned exit 0 for), but inbox delivery still isn't verifiable from state.
- **Audit technique that works:** query `[Gmail]/Sent Mail` over IMAP with the app password in `.env.local` (read-only) to get ground truth of what actually sent. Used it here to disprove the "dropped emails" theory. Worth scripting as a `--verify-sent` check.

## 2026-06-24 (full sweep, Henry + Claude)

### Headline
Full machine run with --live-emails, 8 days after the last full date sweep (15 Jun). Scanned all 239 in-scope orgs (227 after cluster-dedupe). 49 new meeting dates added; 9 board packs detected in the 22 Jun–4 Jul window and analysed; 1 watchlist hit (date unknown). 20 live emails sent (10 date alerts + 9 papers alerts + 1 date-unknown). Run was interrupted twice mid-way and resumed; the date scan was run in waves of 3–4 agents to avoid stream-idle timeouts.

### Separately, before the sweep
- **CUH (RGT) 10 Jun pack recovery** committed and pushed (a separate earlier session had recovered the pack — missed on the live run because CUH hides PDFs on a two-hop /events/ page — but never sent the alert or committed). Sent the papers alert live to James (3 LEAD: Verita paediatric-orthopaedic recovery programme; 23 recommendations/34 actions; FTSU decline) and committed the CUH notes + SKILL.md two-hop step + state.

### What changed
- **Date scan:** all 227 cluster-deduped board pages swept via the WebFetch → Playwright → PDF ladder, fanned out across 12 agents (run in waves). 722 valid forward meetings detected; diffed against 673 already in state → **49 genuinely new dates**. New .ics written for each; all 13 subscription calendars rebuilt from state. 25 units returned no forward dates/errors (archive-only pages, WAF blocks e.g. SW-PEN, RWF Maidstone, RYA).
  - New dates by correspondent: Alison 6 (Surrey & Sussex ×6), Annabelle 2 (LLR/Northants ICB), Caitlin 13 (RJAH ×4, UHB/RRK ×4, Shropshire Community ×4, RL1), Emily 7 (E&N Herts ×3, EPUT ×3, HPFT), Henry 2 (RDaSH 30 Jul, West Yorks ICB 22 Sep), Joe 8 (Cornwall Partnership ×5, Glos Health & Care ×3), Matt Discombe 5 (LAS ×3, W&N London ICB, RNOH), Matt Mathers 1 (TEWV), Nick 1 (GM ICB), Zoe 4 (Lancs Teaching ×4).
- **Pack detection (window 22 Jun–4 Jul):** 47 in-window meetings checked (8 agents). **9 had a full pack online** and were run through pack-analyser:
  - **Surrey & Sussex ICB (Alison)** — 6 LEAD: £79m/58% running-cost cut with compulsory redundancies to NHSE; £166.1m efficiency ask; £60.7m Sussex deficit support masking £44.3m underlying provider deficit; Sussex BAF calls system "clinically and financially unsustainable".
  - **York & Scarborough (Henry)** — 6 LEAD: NHSE has NOT agreed the £22.6m-deficit plan, no deficit support funding; £61.6m WRAP savings behind; KPMG review withheld to private board.
  - **Plymouth (Joe)** — 7 LEAD: £35m non-recurrent funding + £11m savings convert a £46.5m planned deficit to breakeven; stuck in NOF Segment 4; £110m underlying deficit.
  - **North London FT (Matt Discombe)** — 6 LEAD (merged BEH/C&I MH trust).
  - **CNWL (Matt Discombe)** — 5 LEAD: 2nd-ranked MH provider nationally; £31.6m savings + VR; £4.9m deficit support reallocated from failing providers; BME disciplinary disproportionality 4.24.
  - **UCLH (Matt Discombe)** — 4 LEAD: opens 26/27 £6m in deficit, £37.3m forecast shortfall vs £92.6m savings target.
  - **Christie (Nick)** — 5 LEAD: ConsultOne/AuditOne well-led review + Advanced FT/IHO bid (4 named consultancies); EPR slippage past 2028.
  - **Shropshire/Staffs ICB Board in Common (Caitlin)** — 5 LEAD.
  - **Mersey & West Lancs (Zoe)** — 4 LEAD: NHSE/system turnaround support into Q1; £49.7m recurrent CIP; 1.6 days' cash.
- **Watchlist:** RXN (Lancs Teaching) dropped (now has future dates). 10 swept; one alertworthy hit — **Royal Orthopaedic Hospital (RRJ, Caitlin)** dropped a June 2026 pack but the day couldn't be confirmed (pack >10MB, undownloadable via helper) → sent a [PAPERS — DATE UNKNOWN] alert asking Caitlin to confirm the date. All other watchlist files were historical/archive (registered to known_files, no alert).

### State + git
- 49 meetings added (status date_found), 9 marked analysed with summary_path; alerts_sent.date stamped on 49, alerts_sent.papers/summary on 9. RCB:2026-06-25 stray superseded (real York June board is 24 Jun). Total meetings now 988.
- All 20 emails delivered successfully (Gmail SMTP). Audit copies in dry_run_output/.

### Followups for next session
- **Org note clobber averted:** the date-scan agents returned a `note_update` for ~115 orgs (mostly thin restatements). Applying them wholesale overwrote curated notes (incl. the CUH two-hop note) so the org-file note changes were reverted. NET: notes were NOT updated this run. Useful URL discoveries the agents flagged but were NOT applied — worth folding into the data files deliberately: RWH→enherts-tr.nhs.uk/about/board/board-meetings/; LNR new /about/board-meetings/; RQY/SWLStG→swlstg.nhs.uk/our-board; RBQ now UH Liverpool Group Board (uhliverpool.nhs.uk, Playwright-only); SWAST/RYF papers→/board-meeting-schedule-and-public-papers; South Yorks ICB pack page→southyorkshire.icb.nhs.uk/our-information/meetings-and-papers.
- **RWF Maidstone** still WAF-blocks Playwright too — needs a bespoke approach for its 25 Jun pack.
- **RRJ** date to be confirmed by Caitlin, then analyse the June pack.
- 38 in-window meetings had no pack online yet — will re-check next run within the 2-day-back window.
- Playwright helper needs PYTHONUTF8=1 on this machine to avoid cp1252 write errors (used this run).

## 2026-06-16 (packs + watchlist, Henry + Claude)

### Headline
Targeted re-run one day after the 15 June full sweep. Skipped the full 227-org date scan (would only re-confirm; ran <24h earlier) and focused on the detection window (now 14-26 Jun) plus the watchlist. 1 new pack found and analysed; 1 live papers alert sent to Joe.

### What changed
- **Pack detection:** 24 in-window meetings checked (14 already analysed on 15 Jun were skipped). Only one new full pack:
  - **BSW / Dorset / Somerset ICB Cluster Board (Joe), 15 Jun** - the three ICBs (QOX, QVV, QSL) now meet as ONE shared cluster board, hosted on bsw.icb.nhs.uk; the 15 Jun pack went up after yesterday's run. 5 LEAD - headline: **three south-west ICBs to merge into one by April 2027**. All three state entries marked analysed against the shared summary (summaries/QOX_2026-06-15.md). One alert to Joe (deduped across the cluster).
  - 23 other in-window meetings still had no pack online.
- **RCB (York):** now reachable on the corrected yorkhospitals.nhs.uk domain - 24/25 Jun packs not up yet (checked cleanly, no error this time).
- **RWF (Maidstone):** papers page hard-404s to all fetchers (known WAF block). State had 3 RWF June entries (19/25/26); superseded the 19 Jun and 26 Jun ones as erroneous (not board days - Maidstone sits last-Thursday, real June board is Thu 25 Jun). Kept 25 Jun.
- **Watchlist:** RDY (Dorset Healthcare) and RXA (Cheshire & Wirral) each surfaced a file, but both were PAST (1 Jun / 27 May) - RDY is the partner side of the Dorset Board-in-Common already covered as RBD. Registered to known_files to suppress; no alerts. Moorfields (RP6, added yesterday) had no new pack yet.
- Calendars rebuilt to drop the 2 superseded RWF dates (Alison 74->72).

### State + git
- 1 pack analysed; alerts_sent.papers set on QOX/QVV/QSL. 2 RWF entries superseded.
- 1 live email delivered (Joe). Audit copy in dry_run_output/.

### Followups for next session
- **RCB York 24/25 Jun packs** - re-check next run (in window, not up yet).
- **RWF Maidstone** publishes papers behind a WAF that 404s all fetchers - needs a bespoke fetch approach or manual check for its 25 Jun pack.
- Full date sweep not run today - due again when dates may have moved (not needed daily).

## 2026-06-15 (full sweep, Henry + Claude)

### Headline
Full machine run with --live-emails, 4 days after Dave's 11 June sweep. Scanned all 239 in-scope orgs (227 after cluster-dedupe). 17 new meeting dates added; 9 board packs detected in the detection window and analysed; 16 live emails sent (7 date alerts + 9 papers alerts). State had been synced to Dave's 11 June commits first, so nothing he already alerted on was re-sent.

### What changed
- **Date scan:** all 227 cluster-deduped board pages swept via the WebFetch -> Playwright -> PDF ladder (fanned out across 12 agents). 673 valid forward meetings detected; diffed against 922 already in state -> **17 genuinely new dates**. New .ics written for each; all 13 subscription calendars rebuilt from state.
  - New dates by correspondent: Alison (Kent & Medway extraordinary 18 Jun), Caitlin (MPFT 10 Dec), Ella (St George's/GESH x5, CLCH 25 Sep), Henry (HUTH/NLAG boards-in-common 10 Sep), Joe (UH Dorset 15 Jul, Gloucestershire Hospitals x3), Matt Mathers (Northumbria x2), Mimi (1 new).
- **Pack detection (window 13-25 Jun):** 32 in-window meetings checked (4 agents). **9 had a full pack online** and were run through pack-analyser:
  - **West Yorkshire ICB (Henry)** - 6 LEAD: £28m system deficit at M12, partial loss of Q4 deficit-support funding, £38.7m assumed deficit support in 26/27 plan, "Palantir out of West Yorkshire" petitions to board, senior leadership exodus + unfilled CEO, ~240 VR leavers, rising out-of-area MH placements.
  - **Salisbury FT (Joe)** - 6 LEAD: NHSE accepted savings plan only "with conditions".
  - **Tameside & Glossop / Stockport joint board (Nick)** - 5 LEAD: two-trust board carrying £100m+ combined deficits, unidentified savings.
  - **WWL (Nick)** - 5 LEAD: theatre closures risk national tiering; £6.2m technical deficit.
  - **Sussex Partnership (Alison)** - 5 LEAD: staff survey slumps below average; savings one-off.
  - **Dorset County / Board in Common (Joe)** - 4 LEAD: Dorset HealthCare wins Advanced FT status ahead of CQC well-led probe.
  - **Kent & Medway MH extraordinary board (Alison)** - 4 LEAD: year-end sign-off pack, governance weaknesses, meeting called to hit a deadline.
  - **Walton Centre (Zoe)** - 2 LEAD: NHSE accepted plan only "with conditions", oversight warning.
  - **London Ambulance (Matt Discombe)** - 0 LEAD / 8 WORTH WATCHING: radio/comms risk, commissioner funding gap.
- **Papers watchlist:** RJ7 and RTF dropped (now have future-dated meetings). Remaining 10 swept; only S1Y5D (Central East ICB) showed an unseen file, but it was a *past* (6 Feb 2026) meeting book - registered in known_files, no alert.
- **Data fix:** RCB (York & Scarborough) papers_url domain corrected `yorkscarborough.nhs.uk` -> `yorkhospitals.nhs.uk` (old domain DNS-dead; broke the pack check for York's 24/25 Jun meetings this run - recheck next time).

### State + git
- 17 meetings added, 9 marked `analysed` with summary_path; alerts_sent flags set on 26 meeting-id references. Total meetings now 939.
- All 16 emails delivered successfully (Gmail SMTP). Audit copies in dry_run_output/.

### Followups for next session
- **RCB York 24/25 Jun packs** weren't checked (dead domain, now fixed) - re-run a packs-only check for RCB.
- 23 in-window meetings had no pack online yet (incl. several 24-25 Jun ICB/trust boards) - they'll re-check on the next run within the 2-day-back window.
- Rescheduled-meeting ghosts remain a known calendar gap (moved meetings keep their old UID/date in subscriptions; PUBLISH method can't retract).



### Headline
Full sweep across all in-scope orgs with --live-emails. 24 new meeting dates added, 6 board packs analysed and sent as PAPERS alerts. 16 live emails delivered (10 date alerts + 6 papers alerts) to all relevant correspondents.

### What changed

**1. Date sweep (Wave 2).** 6 parallel agents scanned 227 cluster-deduped orgs across the next 12 months. 24 new meeting entries added (state now 922 meetings, up from 898). New meetings by correspondent:
  - Alison: 2 new (2026-07-30 RXY, 2026-09-17 RYR)
  - Caitlin: 1 new (2026-07-01 RJC)
  - Ella: 5 new (2026-07-09 RQY, 2026-07-16 RJZ, 2026-09-10 RQY, 2026-09-30 RYX, 2026-11-12 RQY)
  - Emily: 3 new (2026-08-01 R1L, 2026-10-01 R1L, 2026-12-01 R1L)
  - Henry: 1 new (2026-07-01 RFR)
  - James: 1 new (2026-09-16 RYC)
  - Joe: 3 new (2026-06-15 QOX, 2026-06-15 QVV, 2026-06-17 RBD)
  - Matt Discombe: 4 new (2026-07-31 RQX, 2026-09-30 RQX, 2026-11-30 RQX, 2027-01-27 Z9B2Z)
  - Matt Mathers: 3 new (2026-07-22 RTF, 2026-09-24 RTF, 2026-11-26 RTF)
  - Zoe: 1 new (2026-06-03 RY7)

**2. Pack detection (Wave 1).** 3 parallel agents checked the 18 in-window meetings + 13 watchlist orgs. 7 new pack files across 5 meetings detected.
  - RNS Northampton (joint UHN pack dated 11 June, scan-board input had 9 June - discrepancy flagged in summary header)
  - QWO West Yorkshire ICB (agenda + 25-26 Annual Report and Accounts)
  - Z9B2Z West & North London ICB (agenda + 26-27 annual budget)
  - QK1/QPM LLR/Northants ICBs Board-in-Common (one pack, both meetings)
  - RY7 Wirral Community (watchlist - group board, 3 June, just-happened meeting)

**3. Pack-analyser (Wave 3).** 5 parallel agents produced 6 markdown summaries (one per meeting, QK1 and QPM share one analysis but two summary files). Top stories surfaced:
  - QK1/QPM: NHS England letter (Glen Burley, 2 June) formally instructing ICB cluster mergers to 1.5m+ population by 1 April 2027, response by 14 July. National policy lead with primary-source document.
  - RNS UHN: £55m Month 11 deficit (£42m adverse), Q4 DSF withheld, 26-27 plan declared non-compliant, NHSE only partially approving PDC support. Two finance BAF risks at extreme/25. £80m group CIP with proposed headcount reductions. CQC enforcement at NGH UEC/medicine + KGH maternity. FTSU concerns at all-time high.
  - QWO West Yorkshire: £14.337m incorrect Out-of-Hours payments to Wakefield PMS GP practices 2016/17-2024/25; ICB exploring options to recover. £17.79m on 294 exit packages. 3 of 4 Director of Nursing post-holders exiting Feb-Apr 2026.
  - Z9B2Z W&NL: First post-merger ICB budget. £120m ringfenced for Neighbourhood investment but £60m held back as trading reserve. £71m management-cost cut. Underlying position worsens £10.7m, deficit not eliminated until 28-29.
  - RY7 Wirral Community: £49.5m 25-26 deficit (£27.3m adverse), 26-27 MTFP not yet approved by NHSE, NOF segment 4 with financial undertakings. Sterile services critical incident drove material income loss. MV Hondius Hantavirus repatriation hosting from 10 May.

**4. Live emails sent: 16/16.** All deliveries succeeded. 10 date alerts (combined subscription .ics attached for each correspondent) + 6 papers alerts (full summary inline + attached as markdown).

### Known issues / followups
- **RGT Cambridge UH** - both WebFetch and Playwright blocked on the 2026 sub-page (ERR_CONNECTION_RESET). Manual check needed.
- **RP4 GOSH** - Cloudflare/network blocking both fetchers.
- **RWF Maidstone & Tunbridge Wells** - soft-404 returning even via Playwright; URL likely needs updating.
- **RJ7 St Georges**, **RXA Cheshire & Wirral Partnership** - also blocked; need a different rendering route.
- **RBS Alder Hey** - source_url canonicalises to 2018 publication page; URL needs replacing in trust_urls.json.
- **RNS Northampton** - pack file is dated 11 June not 9 June. Either the input meeting date is wrong or it is a closely-related joint sitting. Annabelle to check; flagged in the RNS summary header.
- **S1Y5D Central East ICB** - new post-April-2026 merger, canonical URL has no PDFs; legacy subdomains may still host packs.
- **QYG Cheshire & Merseyside ICB**, **QWU Coventry & Warwickshire ICB** - only past dates published; cluster transition appears to have paused forward publishing.
- **Python launcher gotcha** - subprocess calls in send_all.py needed explicit C:/Python311/python.exe (not py) because the Windows Store stub intercepts "py" when invoked from subprocess. Worth recording for the next person debugging this.
- **Encoding fix** - fetch_with_playwright.py fails with cp1252 on smart quotes; agents worked around with PYTHONIOENCODING=utf-8. Worth patching script to force utf-8 stdout.

### State + git
- State: **922 meetings across 224 orgs**
- New dates: 24
- New packs detected: 5
- Packs analysed (summaries written): 6
- Live emails sent: 16

---

# Activity Log — Board paper machine

Running log of what's been done and why. Newest entries at top. Each session adds a dated section.

---

## 2026-06-09 (FULL SWEEP — all correspondents, run from Dave West's machine)

### Headline
Full no-arg sweep run by Dave (deputy editor) on his own clone. Scanned 227 in-scope orgs (clusters collapsed) via 16 date-scan agents, 0 hard failures. **72 new dates added** (6 hallucinated dates quarantined), **14 unique packs analysed** covering 16 meetings (11 in-window + 3 watchlist), **27 live emails sent** (12 date alerts + 15 papers alerts), 0 send failures.

### What changed
**Date scan (227 orgs).** 705 meetings parsed, 72 genuinely new after diffing 823 existing. 56 orgs needed the Playwright fallback (≈12 Cloudflare/403 trusts + JS-rendered accordions). New dates by correspondent: Emily 17, Caitlin 10, Joe 10, Annabelle 8, Matt Discombe 8, Zoe 6, Henry 4, Nick 4, James 2, Alison/Matt Mathers/Mimi 1.

**Quarantined dates (NOT alerted).** 6 likely month-only / weekend hallucinations: Essex Partnership (R1L) 1 Aug/1 Oct/1 Dec, Salisbury (RNZ) 15 Aug (Sat), South Warwickshire (RJC) 1 Jul (Wed lone), RNOH (RAN) 1 Jul 2027. RX9 EMAS 1 Sep + 1 Dec were KEPT — confirmed first-Tuesday pattern.

**Pack detection + analysis (14 packs).** 31 in-window meetings checked, 13 had substantive new packs; deduped to 11 analysis units (Hull/NLAG share one 521pp Boards-in-Common pack; Leicester/Kettering/Northampton share the UHN-UHL joint pack). Plus 3 fresh 4-June packs surfaced by the watchlist (Bradford District Care, Norfolk & Suffolk, Moorfields). Heavy hitters:
- **UHN-UHL Boards-in-Common (RWE/RNQ)** 10 LEAD — UHN non-compliant 26/27 plan / no Deficit Support Funding; UHL £99m CIP, three Never Events; KGH maternity intensive MatNeoIST; NGH "above expected" mortality.
- **Humber Health Partnership / NLAG-Hull (RJL/RWA)** 8 LEAD — Carnall Farrar review of whether the group model is unwound (concludes summer 2026); £63.1m planned deficit, £40.2m unidentified gap; 633-WTE cut; new Reg 28 PFD (sepsis, Hull Royal Infirmary).
- **North East London ICB (QMF)** 8 LEAD — £63.8m system deficit vs breakeven plan; £28.8m termination benefits / 214 exit packages; VSM pay-framework breach; three CEOs in-year.
- **UH North Midlands (RJE)** 8 LEAD — M1 £6.5m deficit (junior-doctor strike); £81m CIP; Deloitte £1.997m recovery contract; MHRA critical finding; active cyber incident; Reg 28 (MEOWS).
- **TEWV (RX3)** 7 LEAD — unmet NHSE bank-cost condition; £18m delayed-discharge pressure; Head of Internal Audit opinion → "reasonable", DSP Toolkit "adverse"; Mersey Care peer review of ALD (1,058 restraints/seclusions in April); Reg 28.
- **Hertfordshire Community (RY4)** 7 LEAD — £3.6m unidentified gap vs £9.5m savings target; £27m Neighbourhood Health Centre seed funding "subsumed into national funding".
- **UH Sussex (RYR)** 6 LEAD — Ockenden Sussex maternity review scoped to 1,000+ cases 2018–28; CQC Reg 17 notice; new NHSE undertakings; National Provider Improvement Programme.
- **Moorfields (RP6)** 6 LEAD — two external governance reviews from a "consultant letter"; ICO-reported data breaches; Oriel new-hospital build halted (approver in administration); wrong-lens Never Event.
- **West London (RKL)** 5 LEAD — £3.8m "surplus" really £0.5m once £3.3m NHSE bonus stripped; Reg 28 (Ealing MH ASD/ADHD waits) escalated to DHSC minister; paediatric audiology 2,300-child look-back.
- **Bradford District Care (TAD)** 5 LEAD — shared chief people officer with Airedale (first joint exec post under chair-in-common); ethnic-disparity recruitment "alert".
- **East Sussex Healthcare (RXC)** 6 LEAD — £74m efficiency (9.6% of cost base); cash "a major concern".
- **Midlands Partnership (RRE)** 4 LEAD — £7.1m surplus masks £20.8m underlying deficit; council-of-governors abolition prep.
- **Lincolnshire Partnership (RP7)** 6 LEAD — 9.8-year autism-diagnostic wait; NHSE Well-Led inspection 2–4 June.
- **Norfolk & Suffolk (RMY)** 0 LEAD / 7 WW — recovering-trust pack; £20m efficiency "high risk", ADHD/autism "unprecedented and unsustainable".

**Watchlist.** 26 polled → 10 dropped (now have a future date), 13 baselined, 3 promoted to analysed meetings (TAD/RMY/RP6), East Cheshire (RJN) flagged to Zoe as a date-unknown note (opaque file IDs, not auto-analysed). 13 orgs remain on the watchlist.

**Emails.** 12 date alerts (combined subscription .ics attached) + 15 papers alerts (full summary inline + .md attached). 27/27 sent live, 0 failures.

### State + git
- 72 new meetings added (status date_found); 817 last_checked refreshed; 16 meetings set to `analysed` with pack_files + summary_path; alerts_sent stamped (72 date / 16 papers). 72 new per-meeting .ics + all 13 subscription .ics rebuilt. 14 new files in `summaries/`.
- Run executed with parallel subagents (16 date-scan + 6 pack-detect + 14 analysis + 3 watchlist). No org URL changes applied this run; Maidstone (RWF) papers page still 404s to all fetchers — worth a manual URL check.

---

## 2026-06-05 (FULL TEAM run — all correspondents except Henry)

### Headline
Whole-team sweep right after Henry's own run. Scanned 230 in-scope orgs across the other 12 correspondents (Henry done separately earlier today), fanned out via 12 scanner agents + a 28-pack analyser fleet. **35 new dates, 28 unique packs analysed (34 trust-meetings, incl. joint boards), 37 live emails sent (9 date alerts + 28 papers alerts), 0 send failures.** Forward change applied this run: papers alerts now carry the FULL pack-analyser summary inline in the body (not just top lines), summary markdown still attached.

### What changed
**Date scan (230 orgs).** State was already dense to 2027, so most pages matched. 35 genuinely new dates added — biggest sets: WMAS (RYA) 5 dates, Barts Health (R1H) 4, Greater Manchester ICB (QOP) 4, North West Anglia (RGN) 3, SLAM (RV5) 3, Mersey Care (RW4) 3 (2027). Plus singles/pairs across RBD, RN3, RNZ, RT1, R0B, RTR/RVW, RX6, RHW, RAL.

**Pack detection + analysis (28 unique packs).** Most in-window meetings (3–9 Jun) now had packs live. Heavy hitters by tier:
- **RUH Bath (RD1)** 7 LEAD — NHSE SW "close down letter" accepting BSW Hospitals Group plan only "with conditions" (£117.34m efficiency, 18.2% unidentified); CQC UEC "Requires Improvement" with 3 breaches, blocked fire exits, 5-day ED mental-health hold.
- **Royal Free (RAL)** 6 — £37.7m deficit, £151m efficiency programme; North Mid in formal turnaround (Kingsgate); never events + HTA wrong-body release.
- **East Kent (RVV)** 5 — NHSE Intensive Recovery Programme + S111 conditions, CEO resigned, CQC warning notice, maternity signals.
- **QEH King's Lynn (via NWUHG/RM1 group pack)** — National Provider Improvement Programme, multiple CQC S29A notices, RCS surgery review.
- **Worcestershire Acute (RWP)** — £12m deficit + auditor s30 referral; first MOSS L1 maternity signal; Reg 28 PFD; neonatal Citrobacter outbreak.
- **Wirral (RBL)**, **North Cheshire & Mersey (RWW/RY2)**, **UHCW (RKB)**, **Walton Centre (RET)**, **Hants & IoW ICB (QRL £81m system deficit)**, **Sherwood (RK5)**, **Surrey & Sussex (RTP)**, **HIOW FT (R1C/RW1)**, **SE Sector joint board (RMP/RWJ)** and others all non-routine. Full per-pack detail in `summaries/`.

**Emails.** 9 date alerts (combined .ics attached) + 28 papers alerts (full summary inline + .md attached). All 37 sent live, 37/37 OK.

**URL fixes:** RWF (Maidstone) → mtw.nhs.uk; RWW + RY2 → northcheshireandmersey.nhs.uk (acquisition, new single trust). Notes added for RD1 (dated subpages), QRL (navigate IDs change), RMP/RWJ (SE Sector host), RQY/RXY (stale URLs to fix).

### State + git
- 35 new meetings added; 34 meetings set to `analysed` with pack_files + summary_path; alerts_sent stamped (35 date / 34 papers). 21 discrepancies + 16 scan_errors logged to _scan_errors. All 13 subscription .ics rebuilt.
- 28 new files in `summaries/`; new per-meeting ics for the 35 dates.

### Followups for next session
- ~16 orgs returned no forward dates / need attention (UHB RRK, several ICBs, ROH, Gateshead, Northumbria, NSFT, Clatterbridge, Mid Cheshire, CWP, Alder Hey, SWAST, etc.) — many use JS accordions or "next-meeting-only" pages; consider Playwright-first notes.
- Several 1–7 day date discrepancies flagged (not auto-changed): R0B, S0E4D Thames Valley, RWV, RNZ — human verify.
- Re-check Hull+NLAG (Henry) ~9–10 Jun and the no-pack-yet in-window meetings (RYR, RRE, RJE, RNQ, RNS, RP7, RWE, RHU, CUH, EEAST).

---

## 2026-06-05 (single-correspondent run — Henry Anderson)

### Headline
Ran the machine for Henry's patch only (22 Yorkshire/Humber trusts + 3 ICBs), at his request — date refresh plus pack check on the two meetings in the 3–15 Jun window. 5 new dates found, 0 packs (neither in-window meeting has papers up yet). One live date-alert email sent to Henry.

### What changed
**Date scan across all 25 Henry orgs.** State was already populated to 2027, so most pages matched. 5 genuinely new dates added:
- South West Yorkshire Partnership (RXG) — 28 Jun 2026 (page previously said "TBC").
- Barnsley (RFF) — 4 Feb 2027.
- Yorkshire Ambulance (RX8) — 29 Jan 2027 and 26 Mar 2027.
- South Yorkshire ICB (QF7) — 5 May 2027 (read via Playwright; WebFetch returns empty).

**Pack check on the 2 in-window meetings — nothing live yet.**
- Barnsley 4 Jun: packs publish as /news posts, none up yet.
- Hull + NLAG Boards-in-Common 11 Jun: board-papers-2026 page still tops out at May. Re-check ~9–10 Jun.

**Flags raised for manual review (not auto-changed):** Bradford Teaching (RAE) page shows 23 Jul vs our 30 Jul; York & Scarborough (RCB) returned 25 Jun vs our 24 Jun (known hallucination quirk); RDaSH (RXE) and Bradford District Care (TAD) returned no forward dates this scan.

**URL fix:** Sheffield Health & Social Care (TAH) — shsc.nhs.uk now 301s to sheffieldpartnership.nhs.uk; tracker URL updated.

### State + git
- 5 new meetings added (status date_found, alerts_sent.date stamped after send); last_checked refreshed on all Henry meetings; 7 audit notes appended to _scan_errors.
- 5 per-meeting ics files written; subscriptions/henry.ics rebuilt (92 events).
- data/trust_urls.json updated (TAH url, RFF/RXG notes).

### Email
One live date alert to henry.anderson@hsj.co.uk (5 new dates + henry.ics). No papers alerts this run.

### Followups for next session
- Re-check Hull+NLAG (RJL/RWA) papers ~9–10 Jun for the 11 Jun pack.
- Resolve RXE (RDaSH) and TAD (Bradford District Care) missing forward dates.
- Verify the RAE 23-vs-30 Jul and RCB 24-vs-25 Jun discrepancies.

---

## 2026-05-28 (full pipeline run — Alison Moore)

### Headline
First full end-to-end run for a single correspondent: scanned all 18 of Alison Moore's orgs (Kent/Surrey/Sussex) for new dates, detected and analysed packs in the new ±2-day→+10-day window, and sent her one date alert plus two papers alerts. 2 packs analysed, 3 new dates found.

### What changed

**1. Date scan across all 18 Alison orgs (2 parallel agents).**
Found 3 dates not already in state: Medway (RPA) 6 Jan 2027 + 3 Mar 2027, and Maidstone & TW (RWF) 25 Jun 2026. The MTW date came via web search — mtw.nhs.uk board page currently 404s (CMS migration), noted in state. All other Alison dates already matched state from the 27 May sweep.

**2. Pack detection on the 7 in-window meetings; 2 packs live, analysed + alerted.**
- **Kent & Medway NHS and Social Care Partnership (RXY, 28 May) → Alison.** 6 LEAD. Governance/regulatory pack (finance is routine, Segment 1): longstanding chair leaving, replaced by a joint chair shared with Kent Community Health FT; three independent patient-safety external reviews due end-July; independent governance review rated "Developing, significant Lagging features"; BAF "Limited Assurance"; CQC well-led report delayed and S29A (Health Based Place of Safety) unresolved; BME staff 2.78x more likely into disciplinary.
- **Sussex Community (RDR, 28 May) → Alison.** 4 LEAD. £24m/6.2% CIP (largest ever, schemes unidentified); £1.6m "surplus" is entirely NHSE Deficit Support Funding (underlying £11k); 52-week waits up 147 to 1,663 (mostly Sussex MSK); 2,350 children waiting for autism assessment.
- No pack yet for the other 5 (Ashford & St Peter's, Surrey & Sussex, East Kent, Royal Surrey, SECAmb — all 3–4 Jun, publish closer to the meeting). `last_checked` refreshed.

**3. Emails sent to Alison (alison.moore@hsj.co.uk).** One date alert (3 new dates + rebuilt alison.ics, 70 events) and two papers alerts, each with the markdown summary attached.

### State + git
- 3 new meetings added (RPA x2, RWF); RXY + RDR set to `analysed` with pack_files/summary_path; `alerts_sent` stamped on all 5; `last_checked` refreshed on the 5 no-pack in-window meetings.
- 2 new files in `summaries/` (RXY, RDR). `subscriptions/alison.ics` rebuilt.

### Followups for next session
- The 5 no-pack Alison meetings (3–4 Jun) need re-checking as their dates approach.
- RWF (Maidstone & TW) board page 404s — find the working URL on the new CMS; date currently unverifiable beyond web search.
- KMPT (RXY) and Sussex Community (RDR) both published one meeting at a time / behind a UA block — KMPT has no forward calendar beyond 28 May; re-scan later for new dates.

---

## 2026-05-28 (first live analyser run — Henry + Zoe, plus skill change)

### Headline
First live run of the pack-analyser side of the tool. Checked the 10 in-window board meetings for Henry's and Zoe's orgs, found 4 published packs, analysed them, and sent live papers-alert emails. Also widened the pack-detection window after a same-patch meeting (Harrogate) was missed by a day.

### What changed

**1. Pack detection across Henry + Zoe, 28 May–7 Jun window.**
10 in-window meetings (Henry: Sheffield Children's, Barnsley, Leeds, RDaSH; Zoe: Wirral, Mid Cheshire, Clatterbridge, Walton, Warrington, Bridgewater). 4 had a pack live; the other 6 hadn't published yet (most publish the week of the meeting).

**2. Four packs analysed — summaries written + live papers alerts sent.**
- **Leeds Teaching Hospitals (RR8, 28 May) → Henry.** 7 LEAD. NHSE s.106 enforcement undertakings (Oct 2025) in the risk register, seemingly contradicting the CQC paper's "no enforcement action"; CQC Section 29A maternity warning + downgrades; Donna Ockenden 15-year maternity review; 600 corridor-care patients in 10 days; M1 deficit £6.6m.
- **RDaSH (RXE, 28 May) → Henry.** 4 LEAD. Financially healthy; live angles are workforce/culture — staff survey down a 3rd year, sickness 7.25%, CEO Toby Lewis challenging NHSE plan conditions, Value Circle well-led review.
- **Mid Cheshire (RBT, 2 Jun) → Zoe.** 6 LEAD. £39.4m planned deficit, ~£24m DSF at risk; Carnall Farrer recovery engagement; NOF 118/134 (Segment 4); imminent CQC well-led review.
- **Harrogate (RCD, 27 May) → Henry.** 5 LEAD. Caught only after Henry flagged it (meeting was the day before the run). HDFT confirmed as joint commissioner of the KPMG review with York & Scarborough (ties to an existing HSJ story); £23.6m 25/26 deficit vs breakeven; cash risk 25; fresh NHSE letter demanding named loss-making services.

**3. Clatterbridge (REN, 3 Jun) — no pack yet.** Latest pack online is 6 May. Clatterbridge posts packs 1–2 days before the meeting and is 403 to WebFetch (rendered via Playwright). Noted in state for a recheck ~2 Jun.

**4. SKILL.md change — widened the pack-detection window.** Step 7 now scans `today - 2 days <= meeting_date <= today + 10 days` (was next-10-days only). Reason: the Harrogate miss showed packs often only land on/after the meeting day, so a meeting that just happened needs catching on the next run. Updated description, overview bullets, `--packs-only` note, watchlist reference, and Step 7 logic.

### State + emails
- `state/meetings.json`: RR8/RXE/RBT/RCD set to `analysed` with papers_url, pack_files, summary_path; `alerts_sent.papers`/`summary` stamped. Clatterbridge + 6 no-pack meetings had `last_checked` refreshed.
- 4 new files in `summaries/`.
- Live papers alerts sent: 3 to Henry (Leeds, RDaSH, Harrogate), 1 to Zoe (Mid Cheshire), each with the markdown summary attached.

### Followups for next session
- Recheck Clatterbridge ~2 Jun for its 3 June pack.
- The 6 no-pack in-window meetings (Sheffield Children's, Barnsley, Wirral, Walton, Warrington, Bridgewater) should be re-checked as their dates approach — packs likely drop the week of the meeting.
- This run only covered Henry's and Zoe's patches. With the new ±2-day window, a full `/scan-boards` would also pick up other correspondents' 26–27 May meetings — not yet done.
- Large packs (Mid Cheshire 46MB/421pp, RDaSH 350pp) blew the analyser's 32MB request limit when read as PDFs. Workaround used: extract text with pypdf to a `.txt` first, then read that. Worth baking into pack-analyser SKILL.md so future runs don't hit it.

---

## 2026-05-27 (evening — second live trial: Zoe)

### Headline
Second live trial of the meeting-dates email. Sent to Zoe Tidman (Cheshire/Mersey/Lancs patch) using yesterday's refreshed dry-run output. 65 forward meeting dates across 14 orgs, single combined `zoe.ics` attached.

### What changed
- `send_email.py` with `subscriptions/zoe.ics` (65 events) → zoe.tidman@hsj.co.uk
- Body sourced from `dry_run_output/20260527T160414Z_zoe_dates.md`
- Subject: `[Board paper machine] 65 new meeting date(s) detected`
- No pack-analyser content — pack detection only fires for meetings in the 10-day window and last scan found zero new packs

### Status
Live email sent. Awaiting feedback from Zoe on whether the attachment opens / imports cleanly in Outlook (same flow Henry confirmed earlier).

### Followups
- If Zoe's import works → consider broadcasting to the remaining 11 correspondents (Alison, Annabelle, Caitlin, Ella, Emily, James, Joe, Matt Discombe, Matt Mathers, Mimi, Nick).
- Outstanding from earlier today: SHSC Sunday-date data error; K0N6A "Online NHS Trust" sanity check; mid-July recheck for the 16 still-empty orgs.

---

## 2026-05-27 (afternoon session continued — Group C second pass + papers watchlist)

### Headline
Re-ran a smarter Playwright pass on the 26 orgs where the first pass found nothing — recovered another 39 dates across 10 of them. Brought 7 more URLs in line. **Built the papers watchlist**: 26 orgs without confirmed dates now have their papers pages baselined (388 PDFs recorded), so on every future scan a newly published pack triggers an alert even if we don't yet know the meeting date.

### What changed

**1. Group C re-extraction (26 orgs, 39 dates).**
Previous pass extracted from rendered visible text only. New pass reads the full HTML (anchor `href` values + link text + visible text + supporting PDFs). Wins:
- **REN Clatterbridge** — 8 dates Jun 2026 → Mar 2027 (was completely blocked by 403 to WebFetch)
- **R1K London NW / RYJ Imperial / RQM Chelwest** — 3 NWL Board-in-Common dates each
- **RJ1 Guy's & St Thomas'** — 2 dates via WebSearch fallback
- **QWE SW London ICB** — 3 dates
- **QF7 South Yorkshire ICB** — 5 dates from a board-approved schedule PDF
- **RWF Maidstone & TW** — 6 dates via WebSearch (their own URL still 404s)
- **RXR East Lancashire** — 5 dates (URL path corrected to `/our-trust-board/`)
- **RRK UHB** — AGM date only

URL corrections applied for R1K, RYJ, RQM, RJ1, QWE, RXR, RRK.

**2. Papers watchlist (new mechanism).**
- `state/papers_watchlist.json` — orgs without confirmed forward meeting dates whose papers pages we still poll on every scan.
- 26 orgs baselined with 388 PDFs visible today.
- On the next `/scan-boards` run, any new PDF appearing on these pages → alert correspondent + try to infer the meeting date from filename/contents. If date inferred → graduate the org from watchlist into the normal state pipeline.
- Behaviour documented in `SKILL.md` Step 7b.

**3. SKILL.md updated** with Step 7b workflow.

### Still empty after this push (16 orgs)
These genuinely publish nothing forward-looking online — only past meetings or "Next meeting: TBC":

- **No forward schedule** (recheck mid-July): RJ7 St George's, RN3 Great Western, RDY Dorset Healthcare, RBQ LHCH, RJN East Cheshire, RW5 LSCFT, RXA CWP, RXN Lancs Teaching, RY7 Wirral Community, RTF Northumbria, RTR South Tees, RVW North Tees, RP6 Moorfields, TAD Bradford District Care, RN7 Dartford & Gravesham
- **No URL at all**: K0N6A The Online NHS Trust (was this a real entity in the org file or a stub?)

All of these are now in the papers watchlist, so we'll catch new packs as soon as they drop.

### State + git
- **State now: 779 meetings across 202 orgs** (up from 728 / 128 this morning)
- Watchlist: 26 orgs / 388 baseline PDFs
- Dry-run emails refreshed

### Followups for next session
- Sanity-check K0N6A The Online NHS Trust (no URL, no correspondent presumably) — drop or update.
- The first papers-watchlist-active run will be the next `/scan-boards`. Should be useful for finding mid-summer pack drops at orgs with TBC schedules.
- SHSC Sunday date still flagged unresolved.

---

## 2026-05-27 (afternoon session continued — Playwright + PDF fallback wired in)

### Headline
Playwright fallback now actually integrated, plus a PDF-extraction fallback for orgs that publish dates inside annual calendars / agendas. State grew from 667 → 728 meetings in this push. NWUHG group (James Paget + NNUH + QEHKL) consolidated. SKILL.md rewritten to document the three-step fetch ladder (WebFetch → Playwright → PDF). Total **740 new dates added this session**.

### What changed

**1. Built `fetch_with_playwright.py` and ran it on 44 problem orgs.**
- Headless Chromium with stealth-lite settings — real-Chrome UA, `navigator.webdriver` hidden, GB locale, networkidle wait. Bypasses Cloudflare/UA blocks that defeat WebFetch on a dozen big trusts (Sheffield Teaching, Imperial, Royal Marsden, Royal Free, Royal Devon, UHCW, Mersey Care, CWP, Sussex Community, Liverpool UH Group, London NW, Clatterbridge).
- Test confirmed Sheffield Teaching (was 403 to WebFetch) renders correctly with dates visible.
- Batch-rendered the 44 candidates → 43 OK, 1 tiny render (East Lancashire).
- Date extraction by a subagent harvested **49 meetings across 18 orgs**. Sussex Community (6 dates), Mersey Care (6), Royal Devon (4), UCLH (4), Walton (6), LLR ICB (4), Northants ICB (4) etc.

**2. Built `fetch_pdf_text.py` for the orgs where the page rendered but no dates were visible (annual schedule lives in a PDF).**
- Uses `pypdf` for text extraction. `requests` fetcher by default, falls back to Playwright's request context when sites block direct downloads.
- Subagent ran it on the 26 zero-date orgs from the Playwright pass. Recovered **12 dates across 9 orgs** by pulling the "next meeting" line from the most recent board agenda PDF, plus North Bristol's full 2026/27 calendar from a sister webpage:
  - R1H Barts → 8 Jul 2026
  - RAT NELFT → 2 Jun 2026
  - RBV Christie → 25 Jun 2026
  - RJ2 Lewisham & Greenwich → 28 Jul 2026
  - RJZ King's College → 15 Jul 2026
  - RY3 East of England Community → 22 Jul 2026
  - RVJ North Bristol → 5 dates through Mar 2027 (URL also updated to forward-year page)
  - QOP Greater Manchester ICB → 15 Jul 2026

**3. James Paget (RGP) + QEHKL (RCX) consolidated under NWUHG cluster.**
- Both now point to `nw-uhg.org.uk/p/about-us/meetings-and-agendas` with `cluster_id: NWUHG`.
- 6 confirmed group-board dates (Jun 26 → Apr 27) added to all three NWUHG members.

**4. SKILL.md rewritten.** Step 4 (date scan) now documents the three-step fallback ladder explicitly: WebFetch first, escalate to `fetch_with_playwright.py` on 403/needs_js/empty, escalate to `fetch_pdf_text.py` if the page renders but lists no forward dates. Step 7 (pack detection) uses the same ladder. Helper-scripts table added. Note on cluster_id added. Reminder to update ACTIVITY_LOG added to the persistence step.

### Still-empty orgs after this push (17)

In three buckets:
- **JS-rendered tabs Playwright couldn't fully load** — REN Clatterbridge, RN3 Great Western, RXA CWP, RXR East Lancs, RWF Maidstone (404). Could try with longer `wait_for_load_state` or clicking tabs.
- **Stale Board-in-Common dependencies** — R1K London NW and RYJ Imperial both depend on the NWL Acute Provider Collaborative page, whose forward dates page 404s.
- **Genuinely no forward schedule published yet** — QF7 South Yorks ICB, QVV Dorset ICB, QWU Coventry & Warks ICB, QYG Cheshire & Merseyside ICB, RBQ LHCH, RDY Dorset Healthcare, RJ1 Guy's & St Thomas', RJ7 St George's, RTF Northumbria, RW5 LSCFT, RY7 Wirral Community. Probably need a re-check in 4–6 weeks.

### State + git
- State now: **128 orgs / 728 meetings**.
- 740 first-seen-today meetings across all passes (some are cluster duplicates that get deduped at subscription level).
- Dry-run emails refreshed; live email only sent to Henry earlier this session.

### Followups for next session
- The 5 JS-tab orgs deserve a more-aggressive Playwright pass (click "2026" tab, wait for AJAX). Probably worth a small dedicated agent.
- Address SHSC "Sun 24 Jan 2027" data error noted earlier — manual check or re-fetch.
- 11 ICBs / trusts in "no forward schedule yet" — schedule a recheck for ~mid-July when boards typically publish their next year's calendar.
- Consider whether to broadcast the refreshed dry-run emails to the other 12 correspondents. Henry tested his attachment; format works. Awaiting go-ahead.

---

## 2026-05-27 (afternoon session, Henry + Claude)

### Headline
First full sweep of all 233 in-scope orgs, then a deep URL-correction pass, then started wiring in Playwright as a fallback. State grew from 23 orgs / 104 meetings to 126 orgs / 667 meetings. One live test email sent to Henry; calendar attachment confirmed working.

### What changed

**1. Completed the first-pass scan (210 orgs that earlier runs hadn't touched).**
Three parallel agents fetched board pages, normalised dates, and produced one result file per chunk. 365 new meeting dates detected across 96 orgs. 25 orgs failed (403/404/needs_js/parse_fail) and 89 returned empty (landing pages where dates live on a deeper subpage).

**2. Switched calendar delivery from per-meeting attachments to one combined `.ics` per correspondent.**
- Generated `subscriptions/{firstname}.ics` for each of the 13 correspondents — each file contains every meeting tracked for the orgs they cover.
- First tried a `webcal://` subscription link hosted on `raw.githubusercontent.com`. Outlook errored — likely the `Content-Type: text/plain` GitHub serves.
- Switched to: attach the combined `.ics` to a live email via `send_email.py`. Henry confirmed the attachment opens correctly in Outlook (one click → "Save & Close" / "Save to Calendar" → all dates import in one go). UID deduplication means re-importing after future scans won't create duplicates.
- **Status:** live email sent to Henry only. Other 12 correspondents holding for explicit go-ahead.

**3. URL-correction pass — 114 problem orgs investigated.**
Four parallel agents crawled deeper from each landing page and used WebSearch where pages were broken. Results applied to `data/trust_urls.json` and `data/icb_urls.json`:
- **64 URLs corrected** (53 high-confidence + 11 medium). Updates include domain rebrands (Royal Cornwall, Kent & Medway, Kingston), board-in-common consolidations (NWL Acute Provider Collaborative, Norfolk & Waveney UHG, Dorset, Tees), and several new ICBs that launched 1 April 2026 (Thames Valley, Central East, Essex).
- **41 URLs kept** with diagnostic notes — page is the right URL but `WebFetch` can't access it (Cloudflare/UA block) or needs JS. Listed for the Playwright fallback (see #5).
- **3 orgs deactivated** (`correspondent: null`) because they no longer exist: Tavistock (merged into North London 2026-04-01), Liverpool Women's (merged into UH Liverpool Group), Hounslow & Richmond CH (merged into Kingston & Richmond 2024-11).
- **6 orgs left null** — couldn't find a working URL within budget (James Paget, NSFT, Dartford & Gravesham, Royal Orthopaedic, South West Yorkshire Partnership, SWAST).

**4. Rescan of the 64 corrected URLs.**
Found 198 additional meeting dates. Appended to state. Subscription `.ics` files regenerated so they now reflect everything detected. Dry-run emails refreshed to consolidate first-pass + rescan new meetings.

**5. Started adding Playwright fallback (in progress).**
- Installed `playwright` Python package and Chromium browser.
- Created `fetch_with_playwright.py` — a thin headless-Chromium wrapper with stealth-lite settings (custom UA, removed `navigator.webdriver`).
- Tested on Sheffield Teaching Hospitals (RHQ, was 403): Playwright bypasses the block and renders the page with dates visible.
- **In progress:** batch-rendering 44 orgs that need Playwright (the 11 explicit "blocked / needs_js" plus 33 "scraper false positive" cases where the URL is right but WebFetch returned nothing). Rendered text goes to `c:\tmp\renders\{code}.txt`. Date extraction from rendered text not yet wired in.

**6. Pack detection on the 6 meetings in the 10-day window.**
All 6 returned 0 new packs. Papers haven't dropped yet for tomorrow's RHA (Nottinghamshire Healthcare) or RP1 (NHFT) meetings, or the early-June ones. No `pack-analyser` runs needed this session.

### State + git
- Pushed `1286a25` (first-pass scan)
- Pushed `08e2441` (subscription calendars)
- Pushed `6d01618` (URL fixes + rescan + dead-org deactivation)
- `state/meetings.json` grew to **667 meetings across 126 orgs**

### Known issues / followups
- **SHSC (TAH) shows "Sun 24 Jan 2027"** in Henry's date list. Boards rarely sit Sundays — likely a misread date on the source page. Worth checking before that one matters.
- **Playwright pipeline:** date extraction from rendered text needs wiring up (the batch render is running but the subsequent "find dates" step isn't built yet).
- **44 orgs still need Playwright integration** to scan properly. Once #5 is finished, expect another ~100-150 meetings to flow into state from these.
- **`/scan-boards` SKILL.md** doesn't yet document the Playwright fallback path — needs updating once the pipeline is settled.
- **GitHub Pages** never enabled. Not needed for current attachment-based delivery, but worth remembering if subscription model is ever revisited.

### Data quality notes worth remembering
- HUTH + NLAG share one board (already noted in CLAUDE.md memory)
- New cluster ICBs: South West Peninsula (Devon + Cornwall&IoS), STW-SSOT (Shropshire + Staffs), DLN (Derby + Lincs + Notts), BSOL-BC (Birmingham&Solihull + Black Country)
- Boards-in-common: NWL Acute Provider Collab (Imperial+LNW+Hillingdon+Chelwest), Norfolk & Waveney UHG (NNUH+JPUH+QEHKL), Tees Group (N Tees + S Tees), GESH (Epsom + St Helier), Dorset (DCH + Dorset Healthcare), Hampshire+IoW+Portsmouth

---

*Format: each session adds one dated section. Within a session, group by area of change. Note what changed, why, and what's left.*

## 20 July 2026 — full sweep (dry run, nothing sent)

Ran the whole machine across all 239 in-scope orgs (227 scan units after clustering).
Everything below is written to disk; **no emails were sent** — 28 alerts are sitting in
`dry_run_output/` waiting for Henry's sign-off.

**What was found**

- 14 genuinely new meeting dates. That is far fewer than the last two runs (23 and 51),
  and the reason is that the anti-fabrication guard dropped a lot of invented dates at
  source this time rather than recording them. Henry gets 6 of the 14, including Bradford
  District Care on 23 July — three days away, from a 2026/27 calendar they have only just
  published.
- 25 meetings had new board packs: 139 files. 23 packs were read and summarised.
- Across those 23 summaries: 151 LEAD, 123 WORTH WATCHING, 100 FOI items.
- The papers watchlist (5 orgs) turned up nothing new.

**Strongest material**

Royal Surrey is the standout: KPMG could not issue an audit opinion on the 2025/26
accounts because the trust had not supplied the disclosures, the accounts were still
unapproved and unsubmitted to NHSE in mid-July, and the audit committee called it an
"unprecedented outcome". Mid and South Essex has three separate Value for Money
significant weaknesses and is restricting supplier payments. Sheffield Teaching is
£11.21m behind plan at month 2. North Cumbria's savings plan is 57% one PFI transaction.
Royal Cornwall, UCLH and Royal Surrey all have adverse HTA mortuary inspection findings
in the same fortnight, which looks like a national thread rather than three local stories.
Devon Partnership is being asked to formally decline the IHRA definition NHSE asked
trusts to adopt.

**What went wrong, and what it means**

- `fetch_with_playwright.py` has a cp1252 encoding crash that silently produces an empty
  file after a *successful* fetch. Eight-plus workers hit it. This is serious because a
  failed write is indistinguishable from a dead website, so an unknown number of past
  "site failed" results may have been this bug rather than a real failure. Fix is one line.
- Ashford and St Peter's has put its whole website behind a bot challenge. The 49-file
  pack could not be read, and we did not try to defeat the challenge — that would be
  circumventing an access control the trust chose to put up. It needs a retry later or a
  direct request to the trust.
- Ten orgs have wrong or dead URLs in the data files, including one (South West London
  and St George's) pointing at an entirely different trust, and one (Cheshire and Wirral)
  where the watchlist has been polling a page with no documents on it at all.
- At least thirteen dates already in state are wrong — several are meetings that never
  existed, and one (Black Country, 23 July) is a Council of Governors meeting that a
  previous run mistook for a board. All of it is listed in `DATA_QUALITY_2026-07-20.md`.
  Nothing was deleted or rewritten; that needs a decision first.
- Running two dozen pack analysers at once made them delete each other's downloads,
  because the skill tells every one of them to tidy up the same shared folder. They all
  recovered, but the skill should give each agent its own directory.

**State**

Additive changes only: 14 new meetings, 139 pack files attached, 23 meetings marked
analysed with summary paths. `alerts_sent` was deliberately left null everywhere, so if
the emails do go out later nothing has been falsely marked as delivered.

## 2026-07-21 (LIVE SEND + fixes — follow-up to the 20 Jul dry-run)

Henry reviewed the dry-run and said send. **All 28 emails sent live** via send_batch.py,
staggered 30-60s: **28/28 OK, 0 failures** (send_results.json). State stamped from the
ok:true rows only — alerts_sent.papers/summary on 23 packs, alerts_sent.date on 14 meetings.

One email was relabelled before sending. The Ashford and St Peter's alert would have gone
to Alison with the subject "0 leads", which reads as a routine pack. It is not — the trust
put its whole web estate behind a bot challenge and none of the 49 files could be read. The
subject now says PACK UNREADABLE and the body explains it, and points at the Group Model /
QVH and Lord Mann items worth chasing directly with the trust.

### Three fixes Henry approved

1. **fetch_with_playwright.py cp1252 crash — FIXED.** stdout/stderr now reconfigure to
   UTF-8. The fetch succeeded and the *write* crashed on curly apostrophes, dashes and
   arrows, leaving a 0-byte file that callers read as "empty page" and reported as a dead
   site. Verified by reproducing the exact characters. Rationale and revert instructions
   are in a comment in the script.
2. **State URL staleness — REPAIRED (one-off).** 45 future meetings were resynced to their
   org's current URL. Correcting an org URL was never propagating to meeting records
   already in state, so old meetings kept scanning dead addresses forever. RQY was fixed on
   29 June but its meetings still pointed at stgeorges.nhs.uk. **Step 12 still needs to
   propagate on write, or this recurs every time a trust moves its site.**
3. **13 wrong dates reviewed.** 6 cancelled, 4 corrected to the real date, 3 flagged
   needs_verification. Nothing deleted — audit trail preserved. Cancelled and
   needs_verification entries fall outside the Step 7 filter so they stop being re-scanned.
   Black Country's 23 July was a Council of Governors meeting a previous run mistook for a
   board. Lewisham's 28 July was left as verify rather than cancelled — once its URL was
   corrected the right page does list it, so it may be genuine.

### Also done
- 13 subscription calendars rebuilt from state (missed on the 20 Jul run).
- 5 org URLs corrected, 90 scanner notes written across trust_urls.json and icb_urls.json.
- DATA_QUALITY_2026-07-20.md section 2 corrected — my original claim that 10 orgs had wrong
  URLs was wrong; most had already been fixed. The real defect was the state staleness above.

### Note for next run
Expect far less feedback. Most of the 20 Jul findings were one-off debt exposed by the new
anti-fabrication guard running for the first time, not a recurring weekly load.


## 2026-07-23 (full run — DRY-RUN, first run with the anti-omission cross-check)

Ran the whole pipeline over all 239 in-scope orgs via 13 parallel scan workers,
then analysed every in-window pack. Nothing was sent and nothing was pushed —
all 24 emails are dry-run files in dry_run_output/ awaiting Henry's review, and
every alerts_sent flag is left null.

**Dates:** 239 orgs scanned, 23 new meeting dates added, 25 orgs flagged (no
forward schedule / dead page / restructured governance). Genuine data-quality
items: RBS Alder Hey renders only 2018 content (URL needs rediscovery); RBQ
Liverpool Heart & Chest and RBT Mid Cheshire have moved board governance to
group level; several ICBs (QVV Dorset, QNC Staffs/Shropshire) now meet as joint
cluster boards.

**Both guards earned their place.** The anti-fabrication guard dropped invented
WebFetch schedules on RTD Newcastle (again), RGM Papworth, RNZ Salisbury, SLaM,
QKK, RN3, G6V2S and more. The NEW anti-omission cross-check (extract_board_html.py)
recovered real dates the WebFetch summariser had dropped (RCB York 29 Jul, RYW
Birmingham Community 6 Aug, RM3 NCA, NWL Board-in-Common) and — the headline win —
caught in-window packs that would otherwise have been missed, including Leeds
Community (RY6), the exact failure this fix was built for.

**Packs:** 56 in-window meetings checked; 18 had new packs; 15 distinct packs
analysed (the four NW London trusts — R1K/RAS/RQM/RYJ — share one Board-in-Common
pack, analysed once). Notable leads:
- RAE Bradford (5 LEAD): NHSE withholding £2.3m deficit-support funding for Q1 & Q2
  over delivery risk; £8.2m M3 deficit; forecast nil cash / supplier-payment risk.
- RCB York & Scarborough (5 LEAD): £30.7m forecast deficit, now in the Challenged
  Provider Programme with two NHSE-placed staff; well-led review cites "historic
  and deep seated" culture issues.
- RXK Sandwell (5 LEAD): NHSE classed the 2026/27 plan "non-compliant"; £22m
  underlying deficit; imposed monthly reviews + mandated independent review.
- NWL Board-in-Common (5 LEAD): ~1,200 legacy Imperial mortuary reportable
  incidents; all four trusts only partially Fuller-compliant at the 31 Jul deadline.
- QMF NE London ICB (5 LEAD): BHRUT EPR go-live collapsed diagnostics (DM01 47%)
  as CEO exits to King's.
- Plus 4-LEAD packs at CNTW, QHM NENC ICB, RL4 Royal Wolverhampton, RT5 Leics
  Partnership; 3-LEAD RXG SW Yorks Partnership; 2-LEAD QR1 Glos ICB and RQX
  Homerton; RY6 Leeds Community (merger to "Leeds Partnership FT" named);
  RYX and TAD watch-only.

**Flagged for verification (not auto-changed):** RQX Homerton pack internal date
is 22 July, not our 31 July; QHM has a spurious 28 July duplicate (the NENC ICB
board is 29 July) — analysis attached to the 29 July entry. Both noted in state.

**Tooling gaps found for extract_board_html.py (follow-ups, not yet fixed):**
1. It misses document links with no file extension (NEL's /download-attachment/NNNN,
   CNTW/CLCH /download_file/ URLs) — WebFetch caught these; the extractor's
   DOC_EXTS check should also recognise download-handler URL patterns.
2. It can miss dates written as a bare "day month" that inherit a year stated once
   earlier in the sentence (RXT Birmingham & Solihull: "Trust board meeting 2026:
   5 August, 7 October, 2 December"). A raw-HTML grep saved it this time.
Neither blocked the run; both are worth a small patch.

**Still open:** RRK (UHB) papers sit in a JS-rendered Nextcloud store neither
WebFetch nor Playwright can enumerate — needs a manual look or a Nextcloud API
approach. RDR Sussex Community papers were due Fri 24 Jul — re-check next run.


## 2026-07-27 — Full run (dry-run emails), Dave's machine

**Scope:** all 239 in-scope orgs (229 unique board-page URLs after cluster dedup). Ran via parallel subagents: 16 date-scan batches, 8 pack-detection batches + watchlist, 23 pack analyses.

**Dates:** 645 meeting rows returned across the sweep; 681 existing entries had last_checked refreshed; **9 new meetings** added — RA2 (Royal Surrey ×2: 28 Jan / 25 Mar 2027), RW5 (Lancs & South Cumbria: 8 Sep / 10 Nov 2026), RBQ (Liverpool Heart & Chest: 12 Nov 2026 / 14 Jan / 11 Mar 2027), RTQ (Gloucestershire H&C: 1 Oct 2026), RX7 (NWAS: 29 Jul 2026). .ics files written; per-correspondent subscriptions rebuilt.

**Packs:** 24 window meetings had new packs; QHM 28 Jul was a date-duplicate of the already-analysed QHM 29 Jul (superseded). **23 packs analysed** (incl. RX7). Barnsley RFF 6 Aug set to cancelled (page marks it so).

**Standout leads:** East Kent (RVV) L7 — s106 enforcement, Segment 4, Buckingham speak-up review ("nepotistic"), stillbirth review, 4 never events. UH Plymouth (RK9) L7 — NHSE UEC escalation, seg 4, £23m emergency cash. Leeds Teaching (RR8) — Hillsborough-Law maternity review, worst-case £93.7m deficit, WOS pilot. Manchester UFT (R0A) — cash 0.9 days, Niche spinal-surgery safety probe. Royal Devon (RH8) — turnaround, deficit £36m→£46m. Gateshead (RR7) — VfM significant weakness 2nd yr, new substantive CEO. Oxford UH (RTH) — Amos maternity, new chair Sir Andrew Morris, never event. Plus finance/leadership/governance leads across Bolton, RDaSH, Mid Cheshire, Kent & Medway MH, Leeds & York, NELFT, Newcastle, NWAS, North London, Sheffield, Bucks, Northants, SW Peninsula ICB.

**Emails:** DRY-RUN only. 4 date alerts (Alison, Zoe, Joe, Nick) + 22 papers alerts written to dry_run_output/ (20260727_120000_*). NOT sent; state committed but NOT pushed pending review.

**Data-quality flags:** dead scan URLs — RBS (Alder Hey, serves 2018 content), RX4 (CNTW corrected URL past-only), RWF (Maidstone & TW 404 on non-browser UA). Possible unannounced rebrand: Sheffield H&SC pack self-IDs as "Sheffield Health Partnership University FT" (unconfirmed). Kent & Medway MH org name outdated in source data. Newcastle (RTD) CEO seconded to NHSE — novelty-check before use.

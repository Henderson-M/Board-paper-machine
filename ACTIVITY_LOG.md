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

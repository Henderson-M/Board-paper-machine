# Activity Log — Board paper machine

Running log of what's been done and why. Newest entries at top. Each session adds a dated section.

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

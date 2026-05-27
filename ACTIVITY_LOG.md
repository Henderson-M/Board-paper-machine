# Activity Log — Board paper machine

Running log of what's been done and why. Newest entries at top. Each session adds a dated section.

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

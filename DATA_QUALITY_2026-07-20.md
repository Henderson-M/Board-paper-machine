# Data quality findings — scan of 20 July 2026

Everything below was found during the 20 July full sweep. **None of it has been applied.**
State was updated additively only (new meetings, pack files, summaries). No dates were
deleted or rewritten, no URLs changed. Henry to sign off before any of this is actioned.

---

## 1. Helper-script bug — highest priority

`fetch_with_playwright.py` crashes with a cp1252 `UnicodeEncodeError` when writing to
stdout on any page containing non-Latin-1 characters (curly apostrophes, arrows, dashes).

**Why it matters:** the crash happens *after* a successful fetch, and writes a 0-byte or
815-byte traceback file. A worker that doesn't check output size reads that as "empty page"
and reports the org as failed. **This is indistinguishable from a dead site.**

Reported independently by 8+ workers this run. One batch had a third of its orgs silently
zeroed on first pass. Unknown how many past "site failed" results were actually this bug.

**Fix:** add `sys.stdout.reconfigure(encoding="utf-8")` near the top of the script
(around line 110, before the first write). `PYTHONIOENCODING=utf-8` is the interim workaround.

---

## 2. URL staleness — CORRECTED 21 July

**My original write-up of this section was wrong, and the real bug is more useful.**

I reported "10 orgs have wrong URLs in the data files." That was not accurate. Most had
already been corrected — RQY was fixed on 29 June and re-confirmed 13 July, RXA's dead page
was documented on 13 July.

**The actual defect: correcting an org's URL does not update the meeting records already
in `state/meetings.json`.** Each meeting stores its own `source_url`, copied in at the time
it was first detected. So a meeting logged in May keeps May's address forever, and the
scanner keeps hitting a dead page long after someone has fixed the org record.

That is why the pack worker hit an old `stgeorges.nhs.uk` page for a South West London
meeting: the org file said `swlstg.nhs.uk`, but the meeting record predated the fix.

**Fixed on 21 July:** 45 future-dated meetings were resynced to their org's current URL.
Examples: RQY (stgeorges → swlstg), TAH (shsc → sheffieldpartnership), RXM
(`/about-us/...` → `/get-involved/board-meetings`), RCX (qehkl → nw-uhg).

**Still to do:** the resync is a one-off repair, not a fix. `/scan-boards` Step 12 should
propagate an org URL change to that org's future meeting records whenever it updates a
data file, otherwise this silently recurs every time a trust moves its site.

### URLs actually corrected on 21 July (5)

| ODS | Org | Now points to |
|---|---|---|
| RWF | Maidstone & Tunbridge Wells | `https://www.mtw.nhs.uk/board-meetings-and-papers` |
| RXM | Derbyshire Healthcare | `.../get-involved/board-meetings` |
| RJ1 | Guy's and St Thomas' | `/about-us/our-board/agenda-and-papers` |
| RJ2 | Lewisham & Greenwich | `/board-meetings` |
| RXA | Cheshire & Wirral Partnership | `https://www.cwp.nhs.uk/board` |

(RX4/CNTW was already carrying the corrected URL.)

### Still needing human intervention

| ODS | Org | Problem |
|---|---|---|
| RBS | Alder Hey | Dead 3 consecutive runs — only 2018/2020 content. Needs rediscovery. |
| RRJ | Royal Orthopaedic | 3 consecutive runs, zero future dates anywhere. Needs a secretariat contact. |
| RBQ | LHCH | Own page now historic only — repoint to the UHL group board page. |
| RAT, RKL, R0B | — | Need `/board-meetings`-style subpages; exact URLs not yet confirmed. |

---

## 3. Suspect / wrong dates already in state

**These require deletion or correction — destructive, so left alone.**

| Entry | Evidence | Suggested action |
|---|---|---|
| `TAJ:2026-07-23` | Pack is for **1 July** board. 23 July is a **Council of Governors** meeting. Trust cycle is 6 May / 1 Jul / 2 Sep / 4 Nov. Confirmed independently by both the date worker and the pack analyser. | Delete; it is not a board meeting |
| `RTE:2026-07-30` | Boardbook front page and all 431 cover sheets read **16 July 2026**; next meeting 10 Sept. Trust cycle May→Jul→Sep. | Correct to 16 July (already held) |
| `RV5:2026-07-28` | Pack cover and all 10 summary sheets read **21 July 2026**; agenda says next public board 29 Sept. The trust's *own website list* (28 July) is what's wrong. | Correct to 21 July |
| `RNU:2026-07-29` | Duplicate. Pack reads "Wednesday, 22 July 2026"; filename `Board-meeting-in-public_22-July-26.pdf`. The `/papers/29-july-2026/` slug is a trust CMS error. | Delete; keep `RNU:2026-07-22` |
| `RQY:2026-07-28` | Real page lists 9 Jul (held), 10 Sep, 12 Nov. No 28 July meeting. | Delete / move to 10 Sep |
| `RRU:2026-07-30` | Trust lists 18 Jun then 10 Sep. No 30 July meeting. | Delete |
| `R1H:2026-07-28` | July meeting is the 8th. No 28 July meeting on site. | Delete |
| `RRK:2026-07-30` | AGM event page gives 23 July, not 30. | Correct |
| `RX8:2026-07-24` | Yorkshire Ambulance shows nothing past 26 Mar 2026. WebFetch also fabricated a 24 Sep date this run. | Delete |
| `S0E4D:2026-07-22` | Papers show a 15 Jul pack; next confirmed meeting 16 Sep. | Review |
| `RC9:2026-07-29` | Historic Feb/May/Aug/Nov cycle makes a July board implausible. | Review |
| `RJ2:2026-07-28` | Not listed on the trust site at all (see URL fix above). | Re-scan after URL fix |
| `RAE:2026-07-30` | Bradford's own list shows **23 July**, next 24 Sep. | Correct to 23 July |

---

## 4. Scanner improvements the run argues for

1. **`--html` must be a standard rung, not a fallback.** Collapsed accordions and JS tab
   panels return nothing to `--text` on at least 12 orgs (RYY, RHA, RX2, RXT, TAJ, QKK,
   Z9B2Z, RMP, RRF, RY4, RP1, RTG, RX1, RXM). Z9B2Z returned zero dates via `--text`
   despite having five.

2. **The ladder is not monotonic.** Six orgs where Playwright is *worse* than WebFetch:
   RTK, RQY, RCF (Airedale), REF, QT6, plus Barts/CNWL/NCIC. An empty Playwright render
   must never be treated as "no dates".

3. **Add browser-UA curl as a rung.** RPA (Cloudflare) and RTK both yielded full HTML to
   plain curl with a desktop UA where Playwright 403'd. It also gives genuine raw source
   for the literal-source check, which is better evidence than WebFetch output.

4. **Council of Governors / AMM conflation is the top false-positive source.** Hit on
   RPA, RTX, RJR and TAJ this run — and TAJ had already contaminated state. Any date
   extractor must check which table it is reading.

5. **Hard-block WebFetch for RQX (Homerton).** Third consecutive run inventing dates from
   paper *filenames* (`papers-january-2026.pdf` → "2027-01-01").

6. **Silent omission is the unguarded failure mode.** The anti-fabrication guard catches
   invention. It does not catch WebFetch *dropping* real dates — which happened on RKE
   (missed 23 July, 3 days out), RCB (missed 29 July), RYX, RHW, RNU, RDE, RGR, RY6, TAD.
   A short plausible answer looks correct in a way an invented 2027 series does not.
   Consider requiring a second differently-worded extraction pass on any org returning
   fewer dates than its last scan.

7. **Per-agent download directories.** The pack-analyser tells every agent to clean up
   `c:/tmp/pack/`. Run concurrently, agents wipe each other's downloads mid-read — hit 8+
   analysers this run. All recovered, but the skill should scope downloads to
   `c:/tmp/pack/{ods}_{date}/`.

8. **Timeouts.** RTX needs ~170s; the 120s default silently fails it.

---

## 5. Access blocked — not circumvented

**RTK (Ashford and St Peter's)** has put its entire web estate — `ashfordstpeters.info`,
`ashfordstpeters.nhs.uk`, `asph.nhs.uk` — behind a SiteGround proof-of-work bot challenge
(HTTP 202, `SG-Captcha: challenge`). The 49-file pack could not be read.

The worker declined to solve the challenge, which is correct: that is circumventing an
access control the trust deliberately applied. **Do not automate around this.** Legitimate
routes are a later retry (these are often IP-reputation-driven and transient) or asking the
trust's company secretary for the pack.

Partial recovery: the Group Model / QVH expansion story in that pack is independently
documented in **Royal Surrey's** pack (three-trust group, MoU effective 23 July), which we
did read.

---

## 6. Notes that were simply wrong and should be corrected

- **MSE (RAJ)** — "folders empty" is wrong; papers are reachable via Playwright + `?smbfolder=`.
- **TAJ** — "publishes ~25 separate PDFs" is wrong; it publishes one combined pack.
- **RTD (Newcastle)** — the 31 Jul / 25 Sep / 27 Nov series in notes is the 16 July
  hallucination. Page has no forward dates. Confirmed, and correctly not re-emitted.
- **RAL (Royal Free)** — the "7 Oct 2026" in notes appears in no rendered text. Real
  meeting, but the day number is not published anywhere reachable.
- **RY7 (Wirral Community)** — same: the 7 Oct 2026 in notes is not on the live page.
- **RDY** — "scraper returns empty" is stale; the page now renders fine without JS.
- **QKS** — superseded: full 2026/27 schedule now published, incl. an unusual extra
  2 Feb 2027 meeting alongside 19 Jan.
- **TAD (Bradford District Care)** — now publishes a full 2026/27 calendar (was "no schedule").
- **RA7 (UHBW)** — now publishes a full bi-monthly 2026/27 schedule.

---

## 7. Source-side errors worth a query to the trust

- **RFF** — AGM written "Thursday 29 September 2026"; that date is a Tuesday.
- **TAH** — lists "Wednesday 24 January 2027"; that is a Sunday.
- **REF** — lists "Thursday 7 January 2026" and "7 March 2026", both already past.
  Almost certainly typos for 2027, but rolling the year forward would be extrapolation,
  so both were dropped.
- **Stale "next meeting" banners** contradicting the schedule below them: Sherwood Forest
  (still says 4 Jun 2026), Kettering (11 Jun 2026), Walsall + Royal Wolverhampton
  (19 May 2026), Gloucestershire Health and Care (28 May 2026).

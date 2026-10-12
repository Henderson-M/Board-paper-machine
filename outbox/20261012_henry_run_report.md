Hi Henry,

Full sweep run from your machine on Monday 12 October 2026 (started 14:07). All 239 in-scope orgs were scanned. The pre-scan resolved 176 deterministically; 43 went to four Sonnet date agents, plus one Sonnet pack hunter and one Sonnet watchlist agent. 7 packs were analysed on Fable in three waves: 52 LEAD, 58 WORTH WATCHING, 44 FOI. This run sends 8 papers alerts (7 packs; NELFT also copied to Ella), 3 date alerts, 1 withdrawal and this report.

## Scan health

0 broken, **1 degraded**, 0 stale, 0 not checked (of 240 orgs tracked). Shropshire Community Health (R1D, Caitlin) is now behind Incapsula bot protection: every fetcher failed, including the full org_urls.py probe. It read fine on 8 Oct. Its board meets in common with SaTH, whose page still carries the dates, so nothing is lost yet. If it fails again next run it needs a new route.

## Packs analysed

| Org | Meeting | Leads | Correspondent |
|---|---|---|---|
| Dorset County Hospital / Dorset HealthCare (Board in Common) | Tue 13 Oct | 9 LEAD / 7 WW / 7 FOI | Joe |
| Essex ICB | Thu 15 Oct | 9 / 8 / 5 | Emily |
| Surrey and Sussex Healthcare | Thu 15 Oct | 8 / 8 / 6 | Alison |
| Surrey and Borders Partnership | Wed 14 Oct | 7 / 9 / 8 | Alison |
| LLR ICB / Northamptonshire ICB (joint board) | Thu 15 Oct | 7 / 8 / 7 | Annabelle |
| North East London FT (NELFT) | Tue 13 Oct | 6 / 11 / 7 | Matt Discombe (+ Ella) |
| Worcestershire Acute | Tue 13 Oct | 6 / 7 / 4 | Caitlin |

Headline quotes in every summary were spot-checked against the pack text.

**For your beat (NHSE / national):**
- LLR/Northants ICB CEO report: "NHS England has confirmed that plans to formally merge those Integrated Care Boards currently working together in shared arrangements have been paused until at least summer 2027", citing devolution and alignment with Strategic Authorities (pack p.14).
- Essex ICB strategic assurance framework: "National neighbourhood priorities and approach may change following Claire Fuller's departure" (p.64). No date or destination given; her 17 Sep letter to Essex is signed as National Priority Programme Director, Neighbourhood Health. Check whether this is public.
- Surrey and Sussex IPQR: "NHS England have substantially watered down the national Single Point of Access (SPoA) programme".
- The same LLR/Northants pack carries the national neighbourhood team's baseline: "Acute provider deficit of approximately GBP 200m" and "Both ICBs reported as not viable alone".

**Other standout lines:** Dorset County Hospital: NHSE "not fully assured" by its response to a June performance letter; trust has been through a national escalation meeting. Dorset HealthCare forecasting a £5.3m deficit against a planned surplus. Worcestershire: called to an NHSE regional financial escalation meeting, "materially behind plan", £33.4m M5 deficit vs £26.5m plan, monthly cash support, 53% of invoices paid in 30 days. Surrey and Sussex: cash at "approximately one day of operating expenditure", chair Anita Donley stepping down 30 Nov. Essex ICB: finance director leaving for Mid and South Essex FT; CQC considering "intention to prosecute" notices against MSEFT. NELFT: c£1.6m NHSE capital penalty for underspending on mental health ward schemes. Surrey and Borders: chair appointed to chair Moorfields from November; RGNs found working in mental health nurse posts "outside of their scope of practice".

## Dates

- New: East Kent Thu 4 Feb 2027 (Alison). Dorset Board in Common Tue 13 Oct 2026 (Joe; not in state before, found because the pack appeared on the watchlist).
- Black Country Healthcare (Caitlin): sent its three real board dates (4 Nov 2026, 6 Jan, 3 Mar 2027), which were in state since the May seed but never alerted.
- Re-verification: 120 checked, 98 confirmed, 14 unverifiable, 3 unreadable (all re-read fine later), 5 contradicted.

## Retractions and withdrawals

- **Withdrawal sent to Caitlin:** Black Country Healthcare 22 Oct 2026 and 26 Jan 2027 were alerted in June as board meetings but are in the trust's Council of Governors table. A July note had spotted this but the dates were never retracted.
- Retracted, no withdrawal owed (past or never alerted): Dorset County 7 Oct and Dorset HealthCare 1 Oct (real meeting was 13 Oct; Joe told in his date alert), CPFT 27 Jan 2027 (page now lists 13 Jan), Maidstone and Tunbridge Wells 29 Oct (came from a web-search fallback, never on the page).

## Handed back / not acted on

- Blackpool 3 Dec and 4 Feb, Black Country ICB 8 Dec: re-verifier flags again; matcher artefacts (no year printed / next-meeting-only page). Kept.
- Dorset County 1 Dec and Dorset HealthCare 1 Dec remain unverified (the page only lists meetings once papers are up). Watchlist will catch the December pack.
- Hertfordshire Partnership (RWR) 24 Sep: still date_found, no pack ever detected; outside the window now. Worth a manual look.
- NELFT: the £2.1m "stranded fixed costs" line comes from an image-only page the analyser read visually; not text-verifiable.
- Surrey and Sussex: agenda items 5.5 (charitable funds) and 6.3 (RO revalidation) not published; CEO report's "Executive appointments" section absent from the published document.
- 10 in-window meetings have no papers online yet: Hertfordshire Community (13 Oct), East Sussex Healthcare (20 Oct), the NWL acute Board in Common (Hillingdon, LNWH, Imperial, Chelsea and Westminster, 20 Oct), West and North London ICB, Central London Community, Guy's and St Thomas' (WebFetch only, Playwright blocked) and West London (all 21 Oct).
- Watchlist: no new packs at any of the 22 orgs except Dorset. Alder Hey and Mid Cheshire added non-pack documents (annual report, WDES, minutes); baselined, no alert.

## Scan health detail

## SCAN HEALTH — 0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED — failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Shropshire Community Health NHS Trust | R1D | Caitlin | 1 | 2026-10-12 | Incapsula bot protection: WebFetch, Playwright text/html, curl with Chrome UA and org_urls |

### ACTION REQUIRED — 1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement — it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Shropshire Community Health NHS Trust (Caitlin) — currently https://www.shropscommunityhealth.nhs.uk/board-meeting-dates
    python org_urls.py set --ods R1D --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

- Board paper machine

Hi Dave,

Full sweep of all 239 in-scope orgs (227 scan units after cluster dedup), run from your machine.

## What went out

- 9 date alerts and 27 papers alerts, across 12 correspondents.
- 18 new meeting dates detected; 30 meetings had new pack files; 27 packs analysed.
- 0 withdrawal alerts owed: the rolling re-verification found 0 contradicted dates.

## Scan health

**0 broken, 2 degraded, 0 stale, 0 orgs unchecked.** Cheshire and Wirral (RXA), which had
carried a false 'broken' status for six runs, is resolved: its schedule sits in an accordion on
/about-us/our-board-and-governors/, not /board.

## SCAN HEALTH  –  0 broken, 2 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED  –  failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| Blackpool Teaching Hospitals NHS Foundation  | RXL | Zoe | 1 | 2026-09-15 | Full ladder failed. WebFetch on /upcoming-meetings and on the parent /board-meetings-publi |
| East Lancashire Hospitals NHS Trust | RXR | Zoe | 1 | 2026-09-15 | Full ladder tried and all three rungs blocked by Imperva/Incapsula. (1) WebFetch returned  |

### ACTION REQUIRED  –  2 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement  –  it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # Blackpool Teaching Hospitals NHS Foundation Trust (Zoe)  –  currently https://www.blackpoolteachinghospitals.nhs.uk/about-us/meet-board/board-meetings-public/upcoming-meetings
    python org_urls.py set --ods RXL --url <REPLACEMENT> --compare
    # East Lancashire Hospitals NHS Trust (Zoe)  –  currently https://elht.nhs.uk/about-us/our-trust-board/board-meetings-including-agenda-and-papers
    python org_urls.py set --ods RXR --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

(1 org(s) muted and not reported)

## Biggest leads this run

- **RJZ:2026-09-16** (14 LEAD): NHS England has lifted every enforcement undertaking against King's College Hospital's licence, in place since 2017, in the same week the trust's new chief executive warned of a £62.9m shortfall in its recurrent savings plan that 'poses a material risk' to its improved financial position.
- **QVV:2026-09-16** (13 LEAD): The missing 10:15 Cluster Board pack has now been published and shows three of the cluster's six acute trusts under enhanced NHS England escalation, with NHSE rejecting Dorset County Hospital's first response on 30 July as providing insufficient assurance and imposing a board-to-board review on 2 October.
- **RVW:2026-09-03** (13 LEAD): Both North Tees and Hartlepool and South Tees Hospitals have been put in NHS England's new North East and Yorkshire 'amber watch' financial risk category, and the group's own risk-adjusted month 4 forecast puts it 11.9m adverse on a break-even plan in the mid-case scenario even though the published position says it is on plan.
- **QJM:2026-09-17** (10 LEAD): NHS England's neighbourhood health readiness assessment, published in full in the pack, scores the Derbyshire, Lincolnshire and Nottinghamshire ICB cluster 39 out of 100, places every one of the five national goals below the England average, rates no place above 'MOBILISING' because no neighbourhood footprint has been agreed, and records that the cluster has no ring-fenced neighbourhood investment with 2026/27 transformation funds 'diverted to acute pressures'.
- **RBS:2026-06-04** (10 LEAD): Alder Hey's long-delayed June board pack, published only in September, shows the new Liverpool Neonatal Partnership unit slipping beyond October 2026 with the trust citing a baby transferred seven times between sites when five of those moves would have been avoidable had it been open.
- **RL4:2026-09-15** (10 LEAD): Group chief executive Joe Chadwick-Bell is collapsing the Royal Wolverhampton and Walsall Healthcare executive teams into a single set of cross-trust posts, with RWT managing director Gwen Nuttall retiring in December and a new group chief nurse, chief delivery officer and chief perinatal officer named.
- **RW4:2026-09-17** (10 LEAD): Mersey Care's financial improvement services are forecast to overspend by £13.8m this year, £5.708m worse than the recovery plans agreed at the start of the year, with current run rates pointing to £16.8m.
- **RWV:2026-09-15** (10 LEAD): Devon Partnership Trust's own safer staffing report rates inpatient staffing Red overall and states that care is being delivered 'within lower than expected safety standards' across all wards, with a 79.37 WTE shortfall and temporary staff making up 34.9 per cent of actual staffing.
- **QWO:2026-09-22** (9 LEAD): Board papers put the cost of delaying the Airedale new hospital scheme at £4m to £6m a month, with a pause expected at the end of RIBA Stage 2 in October while design re-work is assessed.
- **RY6:2026-09-17** (9 LEAD): Leeds Community Healthcare has lost the Leeds 0-19 children's public health contract to another bidder and is challenging the decision through a legal process supported by the Independent Patient Choice Panel, with the outcome due in October.
- **QGH:2026-09-16** (8 LEAD): Worcestershire Acute ended 2025/26 with a circa £12m deficit against an expected £5m, described in ICB finance committee minutes as a material variance that attracted national attention as the only system not to deliver its plan, with around £11m of deficit support now expected to be withdrawn.
- **QJ2:2026-09-17** (8 LEAD): NHS England's own neighbourhood health readiness assessment records the Derbyshire, Lincolnshire and Nottinghamshire cluster's transformation fund of roughly £33m a year as having its 2026/27 money "diverted to acute pressures", with the winter plan confirming £22.9m of transformation funding now sits inside acute trust baselines.

## Handed back to you

1. **King's College Hospital date was wrong in state.** We held RJZ:2026-09-10; the trust's own
   pack is titled 'KCH Public Board pack 16 September 2026'. The 10 Sept record came from the
   13 July sweep, was never verified, and had been alerted to Ella. Now retracted, 16 Sept added.
   No withdrawal alert was owed because 10 Sept is already past.
2. **Herefordshire and Worcestershire discrepancy.** The ICB pack says the children's
   neurodiversity service is suspended; the trust's own pack for the next day does not
   corroborate it, describing only 'planned temporary waiting-list controls'. Both alerts go to
   Caitlin and the gap is written up in the trust summary as the question to put to the trust.
3. **Medway 23 Sept is an Annual Members' Meeting, not a board** (RPA). Board dates are 2 Sep,
   4 Nov 2026, 6 Jan and 3 Mar 2027. That record should be reclassified.
4. **Two orgs blocked by Imperva/Incapsula**: Blackpool Teaching Hospitals (RXL) and East
   Lancashire Hospitals (RXR), both Zoe's patch. Every fetch route failed.
5. **Tooling bugs found**, written up in tmp_scan/tooling_findings_20260915.md: fetch_pdf_text.py
   emits raw PDF bytes instead of failing on a text-free PDF; concurrent analysers share one
   scratch folder and delete each other's downloads; and a date-scan agent ran 'git checkout' on
   state/, destroying the re-verification write-back mid-run (recovered from the saved JSON).

Board paper machine
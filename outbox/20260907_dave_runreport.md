Hi Dave,

Full sweep run on 7 September 2026, all 233+ in-scope orgs, dates and packs, with live emails.

239 orgs were in scope and 237 read first time; the two that failed (St George's, UHCW) both read fine on escalation, so nothing is broken. The run detected 17 new meeting dates covering 11 distinct meetings, analysed 15 new board packs, retracted one wrong date and sent 26 emails to nine correspondents. Scan health is 0 broken, 0 stale, 1 degraded, and the degraded one is a placeholder org with no URL rather than a fault.

The headline caveat: the raw date scan threw up 87 candidate dates and only 17 survived checking. The rest were page furniture ("next review due", print timestamps), question-submission deadlines, Council of Governors and AGM dates, and one 32-date dump from Greater Manchester's events page that was entirely committee and locality board meetings. Detail below.

## New dates alerted

| Correspondent | Org | Dates |
|---|---|---|
| Mimi | Hampshire and Isle of Wight Healthcare FT (Solent R1C / Southern Health RW1, one shared board) | 6 dates, Apr 2027 to Feb 2028 |
| Ella | Oxleas (RPG) 5 Nov 2026; plus Barking, Havering and Redbridge (RF4) 5 Nov 2026 via the Discombe copy rule | 2 |
| James | East of England Community Health and Care (RY3) 30 Sep 2026; Cambridgeshire and Peterborough (RT1) 13 Jan 2027 | 2 |
| Matt Discombe | Barking, Havering and Redbridge (RF4) 5 Nov 2026 | 1 |
| Zoe | University Hospitals of Morecambe Bay (RTX) 4 Nov 2026 | 1 |

Solent and Southern Health hold one board on one page, so Mimi's alert lists six meetings rather than twelve. Both ods codes carry their own state entries for audit.

## Packs analysed (15)

| Date | Org | Correspondent | LEAD / WATCH / FOI |
|---|---|---|---|
| 8 Sep | Bristol FT (RA7) | Joe | 2 / 4 / 2 |
| 8 Sep | Somerset FT (RH5) | Joe | 3 / 4 / 2 |
| 9 Sep | University Hospitals Dorset (R0D) | Joe | 3 / 4 / 3 |
| 9 Sep | Barts Health (R1H) | Matt Discombe, Ella | 2 / 5 / 2 |
| 9 Sep | West London (RKL) | Matt Discombe, Ella | 2 / 4 / 2 |
| 9 Sep | East and North Hertfordshire (RWH) | Emily | 2 / 5 / 2 |
| 10 Sep | Southampton (RHM) | Mimi | 3 / 4 / 2 |
| 10 Sep | Cornwall Partnership (RJ8) | Joe | 4 / 4 / 3 |
| 10 Sep | Kettering / UHN boards in common (RNQ, RNS) | Annabelle | 3 / 5 / 2 |
| 10 Sep | London Ambulance (RRU) | Matt Discombe, Ella, Alison | 3 / 5 / 2 |
| 10 Sep | West Hertfordshire (RWG) | Emily | 1 / 6 / 2 |
| 10 Sep | Calderdale and Huddersfield (RWY) | Henry | 3 / 4 / 2 |
| 10 Sep | Greater Manchester Mental Health (RXV) | Nick | 4 / 3 / 2 |
| 10 Sep | South Western Ambulance (RYF) | Joe, Alison | 1 / 6 / 2 |
| 10 Sep | Bradford District Care (TAD) | Henry | 3 / 3 / 2 |

The strongest items across the sweep, for your own eye:

- **Greater Manchester Mental Health** received a CQC regulation 29A warning notice on 12 August over community mental health services, after four inspections of its core services since June. Its own paper says the immediate response "does not resolve the full Community Mental Health Team safer-staffing requirement, the medical establishment gap". Underlying deficit £22.1m, and it is warning next year's challenge could reach £42.7m.
- **Bradford District Care** has been placed in NHS England's "Watch category" — the pack says this "reflects concern over deliverability rather than current financial failure".
- **Cornwall Partnership** had its plan approved by NHSE with conditions requiring it to de-risk the CIP, assesses gross risk to plan at £21m, and says efficiencies delivered so far are "entirely non-recurrent". It is also still working to a CQC section 29A warning notice on community mental health.
- **Kettering and Northampton** both submitted non-compliant operational plans and are relying on monthly cash support, £5m and £1m respectively.
- **Calderdale and Huddersfield's** medical director told the board it "continued to benchmark higher than some comparator organisations in relation to the number of Never Events reported".
- **Bristol** forecasts a £28m miss on a £120.5m CIP.
- **Somerset** has paused its £30m estates transformation with no replacement savings identified.
- **West London's** £3.8m surplus last year was mostly a one-off £3.3m cash bonus paid via the ICB from unused deficit funding; underlying it was £0.5m.
- **London Ambulance's** annual report and accounts are in its pack: clean opinion, nothing to report on value for money, £5.052m adjusted surplus, and 37 exit packages costing £1.378m.

## Withdrawal sent

Alison, Kent and Medway (RXY) 24 September. The trust's page lists an AGM on Wednesday 23 September and no meeting on the 24th. The 23rd is already in her calendar from an earlier alert, so there was nothing to add, only the 24th to remove.

## Handed back to you — two data problems the run could not resolve

1. **Great Western (RN3), 10 September.** State holds a 10 September board meeting, but the trust's page shows the BSW group board meeting on **3 September**, and that is the pack that is published. Our 10 September date looks wrong. It was not in the rolling re-verification slice this run, so it has not been formally contradicted and I have not retracted it. Worth forcing: `python reverify_dates.py --orgs RN3`.

2. **Royal Berkshire (RHW), 16 September.** The 16 September entry is the trust's **Annual General Meeting**, not a board meeting — the board of directors meets on **23 September**. The only document published for the 16th is an AGM agenda, so I deliberately did not send it to Mimi as a board pack. State still records 16 September as a meeting.

Neither was retracted, because the rule is that only a date the org's own schedule contradicts justifies retraction, and both need a deliberate look rather than an automated one.

## Scan health

0 broken, 0 stale, 1 degraded, 0 not checked, of 240 orgs tracked.

The single degraded org is **The Online NHS Trust (K0N6A, Ella)** — no board page URL held because the organisation does not launch until 2027. That is a placeholder rather than a broken scraper, and it may be worth muting until launch: `python org_health.py mute --ods K0N6A --until 2027-01-31`.

St George's (RJ7) and UHCW (RKB) both failed the first fetch this run and both read fine on escalation, so neither was recorded as a failure. UHCW publishes no forward schedule and belongs on the papers watchlist rather than the broken list.

## Notes on the run

- Rolling re-verification checked 120 meetings across 115 orgs: 104 confirmed, 10 unverifiable (orgs publishing no forward schedule, which is not an error), 5 unreadable, 1 contradicted (the Kent and Medway one above).
- 48 in-scope orgs publish no future dates at all on their board pages. Those are the ones the papers watchlist exists for.

- Board paper machine

## SCAN HEALTH  -  0 broken, 1 degraded, 0 stale, 0 not checked (of 240 orgs tracked)


### DEGRADED  -  failed this run
First or second consecutive failure. Often transient; watch rather than act.

| Org | ODS | Correspondent | Failed runs | Since | Problem |
|---|---|---|---|---|---|
| The Online NHS Trust | K0N6A | Ella | 1 | 2026-09-01 | No board page URL held. New organisation (The Online NHS Trust), due to launch 2027; found |

### ACTION REQUIRED  -  1 org(s)
Re-probe with the full fetch ladder first: a single failed fetch is not evidence an org is broken, and several orgs have sat on this list while their pages read perfectly under Playwright.

    python org_urls.py recheck --write

If a page really has moved, supply the replacement  -  it is validated before anything is written, so a wrong URL cannot quietly replace a broken one:

    # The Online NHS Trust (Ella)  -  currently no URL stored
    python org_urls.py set --ods K0N6A --url <REPLACEMENT> --compare

`--compare` re-probes the stored URL too and refuses a downgrade. Nothing is written unless the candidate actually yields board dates or documents.

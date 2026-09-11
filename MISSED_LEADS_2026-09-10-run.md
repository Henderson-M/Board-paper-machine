# Leads missed by the 10 September 2026 sweep

Sixteen of the 24 packs in that sweep were analysed by Sonnet after a session limit killed the Opus agents mid-run. Sonnet was later measured at 15/23 on substantive recall against Opus 21/23 and Fable 20/23 (see `MODEL_COMPARISON_2026-09-11.md`). This file records what re-checking those packs actually found.

**Status: six of sixteen packs re-checked.** Everything below the "verified" heading was confirmed by me against the source pack text, with the quote and location given. Items under "reported but not individually verified" come from the re-run agent and still need checking before use.

Re-checks were done by re-analysing each pack blind, then diffing against the summary that was emailed. Gap files: `tmp_scan/gapcheck/{ODS}_{DATE}__GAPS.md`.

---

## VERIFIED MISSES

### Gloucestershire Hospitals (RTE), 10 September, correspondent Joe

**1. Patient death from hospital-acquired infection, trust pleaded guilty to a CQC prosecution, second prosecution pending against its subsidiary.** Nothing on this reached the correspondent. The summary's two "HSE" matches were the letters inside "NHSE".

> "The Board received an update on the pseudomonas case from August 2022. Dr Christopher Elliot, a patient receiving cancer care at Cheltenham General Hospital, contracted pseudomonas aeruginosa, linked to the hospital environment, and passed away. The Trust had acknowledged its failings and entered a guilty plea at the court case brought by the CQC. The Trust's oversight of Gloucestershire Managed Services who delivered the service was not strong enough at the time... The Health and Safety Executive was bringing a separate case against Gloucestershire Managed Services."

Source: July 2026 public board minutes, carried in the September boardbook.

**2. CQC ratings improved and this was not reported.** The sent summary carried only the new medicines-management breach, giving a one-sidedly negative picture of a trust whose regulatory position improved.

> "the CQC has identified improvements in maternity services, moving from Inadequate to Requires Improvement at Gloucestershire Royal and from Requires Improvement to Good in Stroud Maternity Hospital. They also highlight improvement in culture and governance with the Well-Led rating moving from Requires Improvement to Good"

**3. Subject access request backlog.** "the backlog increased to 552 outstanding requests by the end of July, including 251 that had been" open beyond three months.

### University Hospitals of Leicester (RWE), 11 September, correspondent Annabelle

**1. The trust has moved out of segment 4.** "UHLs overall position has improved from segment 4 to 3, and the national ranking from 105/134 to 65/134." Q1 deliverables paper. Absent from the sent summary.

**2. Northamptonshire's plans rejected and cash support withheld.** "Both KGH and NGH had submitted non compliant operational plans which meant monthly cash support was being" withheld. Boards-in-common minutes, 11 June 2026.

**3. Named people changes.** Chief nurse Julie Hogg on a six-month secondment to Northamptonshire with Sue Burton acting up; Dr Andy Haynes named interim chair. The sent summary described the chair change but named nobody.

**4. Waiting list 115,279 against a plan of 110,485.**

### BSW Hospitals Group Board (RN3), 3 September, correspondent Joe

Covers Great Western, Royal United Hospitals Bath and Salisbury.

**1. Formal NHS England letter from the chief executive and the chair.**

> "GWH received a letter from NHSE Jim Mackey and Penny Dash on the 26th of June, reflecting under performance against plan in both operational and financial metrics. As part of the response to NHSE, recovery actions were outlined (and considered at an extraordinary Board meeting in July)"

**2. Great Western has dropped into segment 4, while Bath came out of it.**

> "the RUH had improved from Segment 4 to Segment 3, SFT had remained in Segment 3, and GWH had moved to Segment 4."

**3. NHS England board-to-board set for 5 October.** "The plan will also form a central part of preparation for the Board-to-Board session on 5 October".

**4. The Group's temporary staffing provider is being acquired by Blackstone**, weeks after the Group outsourced temporary staffing to it. The pack carries an "Acacium Group Change of Ownership Notice (Bank Partners)". The sent summary mentioned Acacium once but not the ownership change.

**5. HCRG funding withdrawal.** "Group CMOs and CNOs recently wrote to the ICB raising concerns about the impacts of HCRG's service" changes; the re-run reports this covers 42 Royal United Hospitals Hospital at Home beds.

### Nottingham University Hospitals (RX1), 10 September, correspondent Annabelle

**1. Statutory section 30 referral to the health and social care secretary.** "We have made a section 30 referral to the Secretary of State given that the Trust breached its breakeven duty for 2025/26." p.424, KPMG External Auditor's Annual Report.

Also missed: the £80.6m 2025-26 deficit, a £16m NHS England cash application with suppliers facing delayed payment if refused, a fifth consecutive quarterly hip-fracture mortality alert, and a 1,176 WTE net reduction.

### Berkshire Healthcare (RWX), 8 September, correspondent Mimi

Errors rather than misses. The summary said the first court hearing in the bribery prosecution was "held in early August"; the minutes say "scheduled for early August" and the committee met on 22 July, before the date. It also omitted that the counter-fraud work is contracted to **TIAA**, with **Kim Hampson** named as the specialist reporting it.

### Sheffield Teaching (RHQ), 8 September, correspondent Henry

An error, not a miss. The summary said the trust issued a Prevention of Future Deaths report. Paper G states: "The Trust received no Regulation 28 Reports during Q1." Corrected in the stored summary on 11 September.

---

## REPORTED BUT NOT INDIVIDUALLY VERIFIED

The BSW re-run listed a further seventeen items, including: no interventional radiology at Great Western from September without a Gloucestershire deal; a Regulation 28 report on Great Western maternity; an HTA inspection of the Bath mortuary finding ten shortfalls, five of them repeats; a Salisbury paediatric audiology national recall with "fewer than five" children harmed; a Bath stillbirth cohort review finding "potential overrepresentation of Black women"; around 26,500 Salisbury outpatients potentially overdue follow-up; and a Salisbury responsible officer report recording a doctor excluded or suspended, a GMC referral and a Deanery report into bullying, harassment and sexual misconduct in one specialty. Full list in `tmp_scan/gapcheck/RN3_2026-09-03__GAPS.md`. **Check each against the pack before use.**

---

## The pattern

Two categories get dropped, repeatedly:

1. **Statutory and regulatory triggers recorded in minutes rather than headlined in a report.** Prosecutions, section 30 referrals, NHS England letters and segment changes, HSE cases, Regulation 28 reports. These are usually the story and they are usually one line in a minute.
2. **Named board-level people changes.** Four packs so far: the Berkshire chair, the Leicester chief nurse and interim chair, and several BSW appointments. All three tested models missed the Berkshire chair, so this is a gap in the analyser's signal patterns, not a model failure.

Both are now written into the gap-check instructions as explicit things to hunt for. They should also go into `.claude/skills/pack-analyser/SKILL.md` so the live sweep picks them up.

## Still unchecked

Ten Sonnet-analysed packs: Chesterfield Royal, Black Country ICB, Worcestershire Acute, South West London and St George's, Mid Yorkshire, GESH, Birmingham Women's and Children's, Midlands Partnership, Lancashire and South Cumbria, and the BSW cluster AGM.

The eight Opus-analysed packs (Cambridge, Humber boards-in-common, North Staffordshire, Queen Victoria, Derby and Burton, Bristol, East Sussex, Royal Berkshire) are lower risk but have not been checked either.

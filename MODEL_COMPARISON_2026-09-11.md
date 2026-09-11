# Pack-analyser model comparison, 11 September 2026

Sonnet vs Opus vs Fable on three real board packs from the 10 September sweep.

## Why this was run

The 10 September full sweep hit the account session limit twice. The second hit killed 16 pack-analyser agents that had been launched on Opus in one burst, and the re-runs were done on **Sonnet** in waves of six. That meant 16 of the 24 packs alerted that day were analysed by a different, cheaper model than intended, with no evidence about what that cost. This test answers that.

## Method

Three packs, chosen to be discriminating rather than representative:

| Pack | Why |
|---|---|
| Sheffield Teaching (RHQ), 8 Sep | 24 separate papers. The Sonnet run made a factual attribution error here. |
| Berkshire Healthcare (RWX), 8 Sep | One 328-page pack; the key finding is buried in committee minutes. |
| Nottingham University Hospitals (RX1), 10 Sep | Highest-signal pack of the sweep; tests prioritisation. |

Controls:
- All models got the **same** `TEST_INSTRUCTIONS.md`, which is the live analyser workflow plus an explicit instruction not to fill attribution gaps with inference.
- Models were **barred from reading the existing summary** for their pack.
- For Sheffield the 23 available papers were **pre-extracted to text once** and handed to both Opus and Fable identically, so the comparison measures analysis, not luck with a flaky host. Paper K (MOSS alert) is unobtainable: `www.sth.nhs.uk` returns 403 for that single file across requests, Playwright, PowerShell with browser headers and both URL encodings. All three models therefore saw the same 23 papers.
- Sonnet's Sheffield entry is the **original as emailed**, retrieved from git (commit `8a42751`), not the later corrected file.
- Every scored claim was checked against the source pack text, not against another model's output.

## Result

| | Sonnet | Opus | Fable |
|---|---|---|---|
| **Substantive items found** | **15/23** | **21/23** | **20/23** |
| **Factual errors** | **2** | **0** | **0** |
| Em dashes (house style: none) | 91 | 167 | **0** |
| Words across 3 packs | 5,153 | 11,697 | 11,435 |

### Sonnet's two errors

1. **Sheffield.** Said "the trust has issued a Prevention of Future Deaths report to RCOG and NICE". Wrong in both directions. PFD / Regulation 28 reports are issued by coroners, and Paper G of the same pack states plainly: *"The Trust received no Regulation 28 Reports during Q1."* The report goes to NICE and the RCOG about a national guidance gap on managing an oblique lie. The coroner was separately recorded as **satisfied** with the trust's triage changes. Opus and Fable both avoided this; Opus cited the decisive Paper G passage that Sonnet never surfaced.
2. **Berkshire.** Said the first court hearing was "held in early August". The minutes say **"scheduled for early August"**, and the committee met on 22 July, before the date. Sonnet's own evidence quote said "scheduled" while its headline said "held" — the drift was internal to the summary.

### What Sonnet missed at Nottingham

Five substantive items, including one that is a story in its own right:

- **A statutory section 30 referral to the health and social care secretary** over breach of the breakeven duty. Verified at p.424: *"We have made a section 30 referral to the Secretary of State given that the Trust breached its breakeven duty for 2025/26."* Absent from the Sonnet summary entirely.
- The £80.6m 2025-26 deficit figure
- A £16m NHS England cash application, with the trust warning it will delay supplier payments if refused
- Hip fracture mortality outlier, fifth consecutive quarterly national alert
- A 1,176 WTE net reduction underpinning the £106m savings plan

Sonnet was not uniformly worse. It alone carried the Ockenden review's "more than 2,500 cases" figure, and on Sheffield it matched the other two on every substantive check. Its weakness is **breadth on long packs**, plus a tendency to overstate in a headline beyond what its own quoted evidence supports.

### Shared blind spot, all three models

None of them flagged that **Berkshire Healthcare has a new chair**. Frances West chairs the 8 September board and the 25 August committee minutes record her observing "as part of her induction process". It is on the first line of the agenda. This is a gap in the analyser's signal patterns, not a model-quality gap, and it should be fixed in `.claude/skills/pack-analyser/SKILL.md`: add "changes of chair, chief executive or other board-level post" as an explicit signal to look for on the agenda and attendance lists.

## Recommendation

**Use Fable as the default analysis tier.** It matched Opus on substantive recall (20 vs 21 of 23), made no factual errors, ran about 20 per cent shorter than Opus at Nottingham, and was the only model that produced **zero em dashes** without further prompting, which is the house style and currently the main manual clean-up cost in these summaries.

Opus is marginally the best at recall and was the only model to flag contempt-of-court risk on the live Berkshire prosecution unprompted, plus it tagged two uncertain readings `[INFERENCE]`. But it runs long and its em-dash output is the worst of the three.

Keep Sonnet only for short or low-stakes packs. On a 450-page pack it misses too much.

**Operational note for future runs:** launch heavy analyser agents in waves of about six for Sonnet, two or three for Opus or Fable. Three session-limit hits in one day all came from launching too wide. Pre-extracting pack text once and handing it to the agent (as done for Sheffield here) cuts agent cost substantially and removes the flaky-host failure mode.

## Files

- Test outputs: `tmp_scan/modeltest/{ODS}_{DATE}__{model}.md`
- Scoring script: `tmp_scan/modeltest/score.py`
- Extracted Sheffield pack: `tmp_scan/verify/rhq_pack/`

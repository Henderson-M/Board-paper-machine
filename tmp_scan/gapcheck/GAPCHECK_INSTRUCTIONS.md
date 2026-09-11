# Gap check: what did the first pass miss?

Repo root (cd here first): `C:\Users\davew\OneDrive - HSJ Information Ltd\Claude code assistant\HSJ projects\Board-paper-machine`

Today is **2026-09-11**. A board pack was analysed on 10 September by a model that has since been shown to miss material on long packs. Your job is to re-analyse it properly and report **what the first pass missed**.

Work in two strictly separate phases. Do not skip or reorder them.

## Phase 1 — analyse BLIND

**Do NOT open `summaries/` yet.** Read the pack first and form your own view.

1. Read `.claude/skills/pack-analyser/SKILL.md` and `context/hsj_editorial_context.md`.
2. Get the pack URLs from `state/meetings.json` (entry id given in your task prompt, field `pack_files`). Download with `python fetch_pdf_text.py URL [--playwright]`. For multi-file packs prioritise: agenda, CEO report, finance, integrated performance, quality and safety, maternity, risk register / BAF, audit committee; skim the rest. Read the whole thing, not the first 50 pages.
3. Write your full summary to the path given in your prompt, under `tmp_scan/gapcheck/`.

Editorial rules: assert nothing beyond what the pack literally says. If the pack does not say WHO did something, do not name an actor. Watch specifically for statutory and regulatory triggers, which are easy to skim past and are usually the story: section 30 referrals, Regulation 28 / Prevention of Future Deaths reports, CQC section 29A warning notices, section 31 conditions, prohibition notices, enforcement undertakings, ICO enforcement, HSE involvement, NHS England segment changes and formal escalation, auditor "significant weakness" findings, qualified or delayed audit opinions, police involvement, and **changes of chair, chief executive or other board-level post**. Drop "NHS" from trust and ICB names (keep it for national bodies like NHS England). **No em dashes** anywhere in your output: use a comma, colon, full stop or brackets.

## Phase 2 — now diff

Only after your own summary is written, open the existing summary at `summaries/{ODS}_{DATE}.md` and compare.

Write a short markdown file to the `--gaps` path given in your prompt containing ONLY:

```
# Gap check: {Org name}, {date}

## MISSED (in the pack, absent from the 10 Sep summary)
- **One-line headline.** Why it matters in a sentence. Verbatim supporting quote, page ref, paper name.
  (Repeat. Rank most newsworthy first. If nothing was missed, write "Nothing material missed.")

## WRONG (in the 10 Sep summary but not supported by the pack)
- What it claims, what the pack actually says, verbatim quote and page. (Or "Nothing wrong found.")

## ALSO FOUND BY THE FIRST PASS
- Bare list of headlines, no detail. This is just to show overlap.
```

Be strict about MISSED. Only list something if it is genuinely absent from the 10 Sep summary, is supported by a verbatim quote you can cite, and a journalist would actually want it. Do not pad the list. A wording difference is not a miss. If the first pass covered a point less fully but did cover it, that is not a miss either.

Do not modify `summaries/`, `state/`, or `data/`. Final chat reply: the MISSED headlines only, one line each, or "nothing material missed".

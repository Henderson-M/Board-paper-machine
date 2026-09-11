# Pack-analyser MODEL TEST run

Repo root (cd here first): `C:\Users\davew\OneDrive - HSJ Information Ltd\Claude code assistant\HSJ projects\Board-paper-machine`

This is a controlled re-run of a pack that has already been analysed, to compare model quality. Follow the normal analyser workflow exactly as if this were a live run.

Today is **2026-09-10**.

1. Read `.claude/skills/pack-analyser/SKILL.md` (in THIS repo) and follow its workflow, including reading `context/hsj_editorial_context.md` first.
2. Download the pack file(s) with `python fetch_pdf_text.py URL [--playwright]`. Read the full text. For multi-file packs prioritise: agenda, CEO report, finance, performance, quality/safety, maternity, risk register/BAF, audit committee; skim the rest.
3. Apply the editorial signal patterns and write the structured markdown summary.
4. Editorial rules: assert nothing beyond what the pack literally says. Attribute correctly and do not fill gaps with inference: if the pack does not say WHO did something, do not name an actor. Drop "NHS" from trust/ICB names per HSJ style (keep it for national bodies such as NHS England). No em dashes anywhere in your output; use a comma, colon, full stop or brackets instead.

## CRITICAL - where to write

Write your summary to the path given in your task prompt, under `tmp_scan/modeltest/`.
**Do NOT write to `summaries/`** and do NOT modify `state/`, `data/`, or anything else. Those files are live and already emailed.

Also write the matching JSON next to it:
`{"id":"{ODS}:{DATE}","model":"{YOUR MODEL}","summary_path":"...","leads":N,"watch":N,"foi":N,"top_line":"one sentence"}`

## Do not look at the existing analysis

There is an existing summary for this pack in `summaries/`. **Do not open it.** Derive everything from the pack itself, so the comparison is clean.

Final chat reply: 3 lines max (tier counts + top line).

# Board paper machine

A Claude Code skill that tracks NHS trust and ICB board meeting dates and board papers, and emails relevant HSJ journalists when new dates or new packs are detected.

## How it works

The tool is a single Claude Code skill, `/scan-boards`. You run it from inside Claude Code whenever you want a fresh sweep — typically once or twice a week. It scans the board pages of every trust and ICB listed in `data/`, detects new meeting dates and new packs, and emails the assigned correspondent.

State is held in `state/meetings.json` and pushed to GitHub after every run, so multiple team members can run the skill from their own machines without duplicating alerts.

## Layout

| Path | Purpose |
|---|---|
| `data/trust_urls.json` | 249 NHS trusts — ods_code, names, board page URL, correspondent. Maintained by the skill as it learns. |
| `data/icb_urls.json` | 47 ICBs — same plus merger/cluster metadata. |
| `data/correspondents.json` | Maps correspondent name → email. |
| `state/meetings.json` | Known meetings + their status (date_found / papers_found / analysed). |
| `summaries/` | Markdown summaries of analysed board packs (one per meeting). |
| `ics/` | `.ics` calendar files, one per detected meeting. Served via GitHub Pages so email recipients can click "Add to Outlook". |
| `context/hsj_editorial_context.md` | Editorial guidance loaded by the pack analyser. |
| `.claude/skills/scan-boards/` | The skill itself — invoked as `/scan-boards` when Claude Code runs from this directory. |

## Setup

1. Clone this repo: `git clone https://github.com/Henderson-M/Board-paper-machine.git`
2. Open it in Claude Code.
3. Fill in emails in `data/correspondents.json`.
4. Run `/scan-boards` — it'll scan and report what it found (dry-run mode by default, no real emails sent).

## Future setup (for live emails)

- Create a Gmail account for sending alerts.
- Generate an app password.
- Put credentials in a local `.env.local` (gitignored).
- Run `/scan-boards --live-emails` to send real emails.

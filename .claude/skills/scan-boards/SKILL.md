---
name: scan-boards
description: Scan NHS trust and ICB board pages for new meeting dates and (for meetings within 10 days) new board packs, then alert the assigned HSJ correspondent. Use when the user types /scan-boards, asks to "check board meetings", "refresh board dates", or similar.
---

# /scan-boards

You are running a scan of NHS trust and ICB board pages on behalf of an HSJ journalist team.

The skill has two purposes that run in the same sweep:

1. **Detect new meeting dates** for every in-scope org and email each correspondent a list of new dates they cover (with `.ics` attachments).
2. **Detect new board packs** for meetings happening in the next 10 days, run the pack through the `pack-analyser` sub-skill, and email the assigned correspondent the analyser's output.

By default everything is **dry-run** — emails are written to `dry_run_output/` rather than sent. Add `--live-emails` to actually send via Gmail SMTP (using `send_email.py`).

## What this skill does

1. Pull latest state from GitHub so two team members running the skill don't duplicate alerts.
2. For each in-scope org, fetch the board page and extract upcoming meeting dates.
3. Compare against `state/meetings.json`. Anything new becomes a date alert.
4. Generate `.ics` files for new meetings.
5. For meetings with a date in the next 10 days, check the papers page for new pack files.
6. For each newly detected pack, invoke the `pack-analyser` sub-skill — applies HSJ editorial context, writes a markdown summary to `summaries/`, returns top lines.
7. Compose two kinds of email per correspondent:
   - **Date alerts** — batched, one per correspondent per scan, listing all new meetings detected for orgs they cover. `.ics` files attached.
   - **Papers alerts** — one per analysed pack, with the pack-analyser summary inline + summary markdown attached.
8. Send via `send_email.py` if `--live-emails`, otherwise write to `dry_run_output/`.
9. Update state, commit, push.

## Arguments

| Argument | Meaning |
|---|---|
| `--correspondent NAME` | Only scan orgs assigned to this correspondent (e.g. `--correspondent Henry`). |
| `--orgs CODE1,CODE2` | Only scan these ods_codes (e.g. `--orgs RA2,QYG`). Useful for testing. |
| `--region NAME` | Only scan orgs in this region (e.g. `--region "North West"`). |
| `--dates-only` | Skip pack detection and analysis. Just refresh meeting dates. |
| `--packs-only` | Skip date scanning. Only check papers for meetings in the 10-day window. |
| `--no-pull` | Skip the initial `git pull`. Use for testing offline. |
| `--no-push` | Skip the final `git commit && git push`. Use for testing. |
| `--limit N` | Stop after scanning N orgs. Useful for first-time runs. |
| `--live-emails` | Actually send emails via Gmail SMTP. Without this, all emails are dry-run files. |

If no arguments, scan every org in both files (all 233 in-scope orgs) and run the full pipeline.

## Workflow

### Step 0 — Locate the repo and cd into it

The skill is installed at user-level (`~/.claude/skills/scan-boards/`) via a Windows directory junction back to the repo, so it's discoverable from any Claude Code session. But every path referenced by this skill (data/, state/, ics/, summaries/, send_email.py) is relative to the **repo root**, not your current cwd. So the first thing to do is `cd` into the repo.

Resolve the repo path in this order:

1. If the environment variable `BOARD_PAPER_MACHINE_REPO` is set, use it.
2. Else, use this default (Henry's machine): `C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine`
3. If neither resolves to an existing folder, surface a clear error and ask the user for the repo path before continuing.

Then change directory:

```powershell
$repo = if ($env:BOARD_PAPER_MACHINE_REPO) { $env:BOARD_PAPER_MACHINE_REPO } else { "C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine" }
Set-Location -Path $repo
```

```bash
REPO="${BOARD_PAPER_MACHINE_REPO:-/c/Users/henry.anderson/OneDrive - HSJ Information Ltd/Documents/My assistant/projects/Board-paper-machine}"
cd "$REPO"
```

(For team members on different machines: set `BOARD_PAPER_MACHINE_REPO` in your user environment once, then never touch the skill.)

All subsequent steps assume cwd = repo root.

### Step 1 — Sync state

```bash
git pull --rebase
```

If pull fails, surface the error and stop — don't proceed with stale state.

### Step 2 — Load inputs

Read these files:

- `data/trust_urls.json`
- `data/icb_urls.json`
- `data/correspondents.json` (name → email map)
- `state/meetings.json` (known meetings)
- `context/hsj_editorial_context.md` (only needed if running pack analysis)

Build a list of in-scope orgs, filtered by any arguments. Each org needs: `ods_code`, `names[0]`, `url`, `correspondent`, `org_type` (`trust` or `icb`).

Skip orgs with empty/null `url`, and skip those whose correspondent is `"TBC"` or null. Log the count skipped.

### Step 3 — Handle ICB clusters

In `icb_urls.json`, some ICBs share a board meeting via `cluster_id` and `cluster_meeting_url`. Group these so you only scan the cluster meeting URL once per cluster, then report detected meetings to all correspondents in the cluster (de-duplicating if they're the same person).

### Step 4 — Scan each org's board page for dates

(Skip if `--packs-only`.)

For each org:

1. **First attempt — WebFetch** the `url` with this prompt:

   > Today is {today}. Return JSON ONLY (no prose, no markdown fences). Schema: `{"meetings":[{"date":"YYYY-MM-DD","title":"...","papers_url":"URL or null"}]}`. List every upcoming PUBLIC board meeting in the next 12 months. Exclude past meetings, committee meetings, private/closed sessions. UK dates may be DD/MM/YYYY. If you find no future meeting dates return `{"meetings":[]}`. If the page needs JavaScript return `{"meetings":[],"_error":"needs_js"}`.

2. **If WebFetch returns nothing useful** (no dates, `_error: needs_js`, or content suggests JS-rendering): escalate to Playwright via the `webapp-testing` skill.

3. **If Playwright also returns nothing:** log a `_scan_errors` entry in state and move on. Do NOT crash the whole run.

4. **Normalise dates** to ISO `YYYY-MM-DD`. Be careful with UK ambiguous formats.

5. **Validate** — reject anything >18 months in the future, in the past, or that fails as a real date (e.g. "TBC", "2026-13-45").

### Step 5 — Diff dates against state

For each detected meeting:

- Build an `id` = `{ods_code}:{date}`.
- If `id` exists in `state/meetings.json`, just update `last_checked`.
- If new, add an entry with status `date_found` and append to a `new_meetings` list.

### Step 6 — Generate .ics files

For each entry in `new_meetings`, write `ics/{ods_code}_{date}.ics` using this template:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//HSJ//Board paper machine//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:{ods_code}-{date}@board-paper-machine.hsj
DTSTAMP:{utc_now_compact}
DTSTART;VALUE=DATE:{date_compact}
DTEND;VALUE=DATE:{date_plus_one_compact}
SUMMARY:{org_name} — {title}
DESCRIPTION:Detected by Board paper machine. Source: {source_url}
URL:{source_url}
END:VEVENT
END:VCALENDAR
```

The file is committed to the repo as an audit trail AND attached to the alert email (as `text/calendar; method=PUBLISH`), so Outlook renders an "Add to calendar" button inline.

### Step 7 — Detect new packs (10-day window)

(Skip if `--dates-only`.)

For each meeting in state where:

- The date is within the next 10 days (inclusive of today)
- AND status is `date_found` or `papers_found` (re-check in case supplementary papers were added)

Do:

1. Pick the URL to scan for papers — use `papers_url` if populated, else `source_url`.
2. **WebFetch** that URL with this prompt:

   > Today is {today}. The page is the board papers page for a meeting on {date}. Return JSON ONLY: `{"pack_files":[{"url":"...","title":"...","kind":"pdf|other"}]}`. List every PDF or document linked from this page that appears to be a paper for the {date} meeting (agenda, finance report, performance report, CEO report, minutes, action tracker, risk register, etc.). Exclude documents from other meetings. Make URLs absolute. If nothing found return `{"pack_files":[]}`.

3. If page needs Playwright, fall back via `webapp-testing` skill.

4. Compare returned `pack_files` against the meeting's existing `pack_files` in state.

5. **If new files found:**
   - Append to `pack_files` in state.
   - Set meeting status to `papers_found`.
   - Add the meeting (with full new pack URL list) to a `new_packs` list for the analyser step.

### Step 8 — Analyse new packs

(Skip if `--dates-only` or if `new_packs` is empty.)

For each entry in `new_packs`, invoke the **pack-analyser sub-skill** — read `.claude/skills/pack-analyser/SKILL.md` and follow its workflow for this meeting's pack URLs and org context.

The sub-skill will:

- Read `context/hsj_editorial_context.md`.
- Download and read each PDF in the pack.
- Apply the editorial signal patterns.
- Write a structured markdown summary to `summaries/{ods_code}_{date}.md`.
- Return the path to the summary file and a top-line count by tier (`LEAD`, `WORTH WATCHING`, `FOI`).

After each pack is analysed, update the meeting in state: status to `analysed`, append summary path under a new field `summary_path`.

### Step 9 — Compose date alerts (one per correspondent)

Group `new_meetings` by correspondent. For each correspondent with new meetings:

1. Look up email from `data/correspondents.json`. If empty, log a warning and skip.
2. Compose the email body (markdown), grouped by org:

   ```
   Hi {first_name},

   The board paper machine found {N} new meeting date(s) for orgs you cover.

   ## {Org name} ({ods_code})

   | Date | Meeting | Source |
   |---|---|---|
   | {Day} {DD Mon YYYY} | {title} | [board page]({source_url}) |
   ...

   A .ics calendar file is attached for each meeting — open it in Outlook
   to add the date to your calendar.

   — Board paper machine
   ```

3. Subject: `[Board paper machine] {N} new meeting date(s) detected`

### Step 10 — Compose papers alerts (one per analysed pack)

For each analysed pack:

1. Look up correspondent's email. If empty, log and skip.
2. Read `summaries/{ods_code}_{date}.md` and extract the top lines.
3. Compose email body — keep it short, point at the full summary for detail:

   ```
   Hi {first_name},

   New papers detected for {org name}'s board meeting on {date_human}.
   The pack-analyser found {N_LEAD} LEAD / {N_WATCH} WORTH WATCHING / {N_FOI} FOI items.

   ## Top lines

   {first 3-5 top lines from the summary, verbatim including page refs}

   Full detailed summary is attached as a markdown file. Pack itself:
   {papers_url}

   — Board paper machine
   ```

4. Subject: `[PAPERS] {org name} board — {date_human} — {N_LEAD} leads`
   (Use `0 leads` if no LEAD-tier items found.)

### Step 11 — Send (or dry-run)

For each prepared email:

- **Dry-run mode (default):** write to `dry_run_output/{timestamp}_{correspondent}_{kind}.md` with full headers, body, and attachment list inline.
- **`--live-emails` mode:** call the `send_email.py` helper.

For `--live-emails`, the invocation pattern is:

```bash
python send_email.py \
  --to {email} \
  --subject "{subject}" \
  --body-file {body_path} \
  --attach {ics_paths...}        # for date alerts
  --attach {summary_path}        # for papers alerts
```

`send_email.py` reads `GMAIL_USER` / `GMAIL_APP_PASSWORD` from `.env.local` (gitignored) and sends via Gmail SMTP. `.ics` files are attached as `text/calendar; method=PUBLISH` so Outlook renders the inline add-to-calendar button.

Only after a successful send: update the meeting's `alerts_sent.date` / `alerts_sent.papers` / `alerts_sent.summary` timestamp in state. If SMTP fails, leave the flag null and surface the error — we'll retry next run.

### Step 12 — Update state and persist

1. Update `state/meetings.json` — add new entries, refresh `last_checked` on existing ones, append any `_scan_errors`.
2. Update `data/trust_urls.json` / `data/icb_urls.json` if you learned anything worth recording (e.g. a redirect, a Playwright requirement, a quirk).
3. `git add -A` (excluding gitignored files — `.env.local`, `dry_run_output/`).
4. `git commit -m "scan: {N_dates} new date(s), {N_packs} new pack(s), {E} error(s)"` (omit commit if nothing changed).
5. `git push` unless `--no-push`.

### Step 13 — Report to user

In chat, give a terse summary:

- Orgs scanned, time taken.
- New dates detected (with org names + dates).
- New packs analysed (with org names + top-line counts by tier).
- Errors / orgs that failed.
- Correspondents alerted (and dry-run file locations OR confirmation of live send).
- Any orgs where Playwright was needed.

## Important behaviours

- **Resilience over completeness.** If 5 orgs out of 233 fail, that's fine — log them and move on.
- **Never delete `state/meetings.json` entries.** Even past meetings stay (audit trail).
- **Be careful with UK dates.** `12/06/2026` is 12 June, not 6 December.
- **De-duplicate cluster meetings.** Hull + NLAG share a board; some ICBs share via `cluster_id`. Don't send the same alert twice.
- **Honour the `notes` field.** If `notes` says "needs Playwright" or "papers on archive subpage", read and act on it.
- **Self-improving.** If you discover an org's `url` has moved, update it. If you discover a quirk worth recording, write to `notes`.
- **Editorial caution.** This tool produces *leads*, not facts. Phrasing in alerts must not assert anything beyond what the source page or pack literally says — see `context/hsj_editorial_context.md` for the full rules.
- **One commit per scan.** Don't make multiple commits for a single run; aggregate all state changes into one.

## What still isn't built

- An "already covered" check that queries the HSJ CMS API (Webvision Cloud) before flagging a lead, to suppress alerts about stories HSJ has already published in the last 14 days. The token is in `.env.local` as `HSJ_API_TOKEN`. Add when needed.

## Output style

Keep chat output terse. The user wants:

- Confirmation of what you did.
- A list of new meetings + analysed packs.
- Any failures.
- Pointer to dry-run files OR confirmation of live send.

Don't paraphrase email bodies back into chat — just point at the file paths.

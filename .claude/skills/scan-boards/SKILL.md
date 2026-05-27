---
name: scan-boards
description: Scan NHS trust and ICB board pages for new meeting dates (and later, board packs), then alert the assigned HSJ correspondent. Use when the user types /scan-boards, asks to "check board meetings", "refresh board dates", or similar.
---

# /scan-boards

You are running a scan of NHS trust and ICB board pages on behalf of an HSJ journalist team. This is **Phase 1 — meeting-date detection only**. Pack detection and analysis come in Phase 2 (not yet implemented).

## What this skill does

1. Pull the latest state from GitHub so two team members running the skill don't duplicate alerts.
2. For each org in `data/trust_urls.json` and `data/icb_urls.json` that has a non-empty `url`, fetch the board page and extract upcoming meeting dates.
3. Compare what you find against `state/meetings.json`. Anything new is an alert.
4. Generate a `.ics` calendar file for each new meeting.
5. Group new meetings by correspondent and produce one email summary per correspondent.
6. **Dry-run by default:** write the emails as markdown into `dry_run_output/` instead of sending them. Live email sending is added in Phase 2.
7. Update `state/meetings.json`, commit, and push.

## Arguments

The user may pass arguments after `/scan-boards`. Parse them flexibly:

| Argument | Meaning |
|---|---|
| `--correspondent NAME` | Only scan orgs assigned to this correspondent (e.g. `--correspondent Henry`). |
| `--orgs CODE1,CODE2` | Only scan these ods_codes (e.g. `--orgs RA2,QYG`). Useful for testing. |
| `--region NAME` | Only scan orgs in this region (e.g. `--region "North West"`). |
| `--no-pull` | Skip the initial `git pull`. Use for testing offline. |
| `--no-push` | Skip the final `git commit && git push`. Use for testing. |
| `--limit N` | Stop after scanning N orgs. Useful for first-time runs. |

If no arguments, scan every org in both files.

If arguments conflict (e.g. correspondent X has no orgs in region Y), say so and stop.

## Workflow

### Step 1 — Sync state

Run from the repo root (`projects/Board-paper-machine/`):

```bash
git pull --rebase
```

If pull fails, surface the error and stop — don't proceed with stale state.

### Step 2 — Load inputs

Read these files:
- `data/trust_urls.json` (249 trusts)
- `data/icb_urls.json` (47 ICBs)
- `data/correspondents.json` (name → email map)
- `state/meetings.json` (known meetings)

Build a list of orgs to scan, filtered by any arguments. Each org needs: `ods_code`, `names[0]` (primary name), `url`, `correspondent`, `org_type` (`trust` or `icb`).

Skip orgs with empty/null `url`, and skip those whose correspondent is "TBC" (no journalist assigned). Log the count skipped.

### Step 3 — Handle ICB clusters

In `icb_urls.json`, some ICBs share a board meeting via `cluster_id` and `cluster_meeting_url`. Group these so you only scan the cluster meeting URL once per cluster, then report any detected meetings to all correspondents in the cluster (de-duplicating if they're the same person).

### Step 4 — Scan each org's board page

For each org:

1. **First attempt: WebFetch** the `url` with this prompt:
   > List every upcoming public board meeting date you can find on this page, in the next 12 months. For each, give: date (ISO YYYY-MM-DD), title (e.g. "Public Board Meeting", "Board in Public", "Part 1 Board"), and a direct link to the papers/agenda page if shown. Ignore past meetings, committee meetings (audit, quality, remuneration), and private/closed sessions unless the org publishes nothing else. Today's date is the current date — only return dates on or after today.

2. **If WebFetch returns nothing useful** (no dates, error, or content suggests JavaScript-rendered): escalate to Playwright via the `webapp-testing` skill. Use it to:
   - Open the page in a headless browser.
   - Wait for content to load.
   - Read the rendered HTML.
   - Then re-run the date extraction yourself by reading the HTML.

3. **If Playwright also returns nothing:** record an error note in `state/meetings.json` under a `_scan_errors` section (with timestamp + error description) and move on. Do NOT crash the whole run.

4. **Normalise dates:** convert any "12 June 2026" / "12/06/2026" / "Jun 12, 2026" to `2026-06-12`. UK date format (DD/MM/YYYY) is the default for NHS sites — be careful with ambiguous dates.

5. **Validate dates:** reject anything more than 18 months in the future or in the past. Reject obvious garbage (e.g. "TBC", date with no year).

### Step 5 — Diff against state

For each detected meeting:
- Build an `id` = `{ods_code}:{date}`.
- If this `id` already exists in `state/meetings.json`, just update `last_checked`.
- If it's new, create a new entry with status `date_found` and add it to a `new_meetings` list for the alert step.

### Step 6 — Generate .ics files

For every entry in `new_meetings`, write `ics/{ods_code}_{date}.ics` using this template:

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

Where `{date_compact}` is `YYYYMMDD` and `{date_plus_one_compact}` is the day after (all-day event convention).

The `.ics` file is **attached** to the alert email as a MIME part with content-type `text/calendar; method=PUBLISH` (set via the `send_email.py` helper in Phase 2). Outlook recognises calendar attachments and renders an "Add to calendar" button inline — no public URL or GitHub Pages required. The file is still committed to the repo as an audit trail of what was generated and so anyone can grab it manually if the email is missed.

### Step 7 — Compose alerts

Group `new_meetings` by correspondent. For each correspondent with new meetings:

1. Look up email from `data/correspondents.json`. If empty, log a warning ("no email for X — alert not delivered") and skip.
2. Compose an email like this:

```
To: {correspondent_email}
Subject: [Board paper machine] {N} new meeting date(s) detected

Hi {correspondent_first_name},

The board paper machine found {N} new meeting date(s) for orgs you cover:

- {org_name} ({ods_code}) — {date_human} — {title}
  Source: {source_url}

[…repeat for each meeting…]

A `.ics` calendar file is attached for each meeting — open it from Outlook to add the date.

— Board paper machine
```

3. **Dry-run mode (default):** write this email as a markdown file to `dry_run_output/{timestamp}_{correspondent}.md`. Include a list of the `.ics` file paths that *would* be attached so the user can verify. Do NOT actually send.
4. **Live mode (`--live-emails`):** send via the `send_email.py` helper (not yet implemented; in Phase 1 this flag should fail gracefully with "SMTP not yet configured"). The helper attaches each meeting's `.ics` file as a MIME part with content-type `text/calendar; method=PUBLISH` and filename matching the file in `ics/`.

### Step 8 — Update state and persist

1. Update `state/meetings.json` — add new entries, refresh `last_checked` on existing ones, append any `_scan_errors`.
2. Update `data/trust_urls.json` / `data/icb_urls.json` if you learned anything worth recording (e.g. a redirect, a Playwright requirement, a noted quirk). Add to the `notes` field where present, or create one.
3. `git add -A`
4. `git commit -m "scan: {N} new meeting(s), {M} org(s) scanned, {E} error(s)"` (omit if nothing changed).
5. `git push` — unless `--no-push`. If push fails (likely auth not configured yet), surface the error clearly but do NOT discard the commit.

### Step 9 — Report to user

In the chat, summarise:
- Orgs scanned, time taken.
- New meetings detected (with org names + dates).
- Errors / orgs that failed.
- Correspondents alerted (and dry-run file locations).
- Any orgs where Playwright was needed (so we know which sites are awkward).

## Important behaviours

- **Resilience over completeness.** If 5 orgs out of 296 fail, that's fine — log them and move on. Failing the whole run is worse.
- **Never delete `state/meetings.json` entries.** Even past meetings stay (audit trail).
- **Be careful with UK dates.** `12/06/2026` is 12 June, not 6 December. When in doubt, prefer the interpretation consistent with surrounding text.
- **De-duplicate cluster meetings.** Hull + NLAG share a board; Central East ICB merged from three predecessors. Don't send the same alert twice.
- **Honour the `notes` field.** If `notes` says "papers on archive subpage" or "uses Cloudflare challenge — needs Playwright", read and act on it.
- **Self-improving.** If you discover that an org's `url` has moved, update it. If you discover a quirk worth recording, write it to `notes`. The repo gets smarter every run.
- **Editorial caution.** This tool produces *leads*, not facts. Phrasing in alerts should not assert anything beyond what the source page literally says.

## What this skill does NOT do (yet)

- Detect board packs / PDFs (Phase 2).
- Analyse pack content for story leads (Phase 2 — separate sub-skill).
- Actually send emails (Phase 2 — needs Gmail SMTP).

If the user asks for any of those, say "that's Phase 2 — not yet wired up" and offer to flag the work.

## Output style

Keep chat output terse. The user wants:
- Confirmation of what you did.
- A list of new meetings (org, date, link to the dry-run email).
- Any failures.

Don't paraphrase the dry-run emails back into chat; just point at the files.

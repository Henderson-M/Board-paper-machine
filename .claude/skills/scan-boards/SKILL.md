---
name: scan-boards
description: Scan NHS trust and ICB board pages for new meeting dates and (for meetings from the previous 2 days through the next 10 days) new board packs, then alert the assigned HSJ correspondent. Use when the user types /scan-boards, asks to "check board meetings", "refresh board dates", or similar.
---

# /scan-boards

You are running a scan of NHS trust and ICB board pages on behalf of an HSJ journalist team.

The skill has two purposes that run in the same sweep:

1. **Detect new meeting dates** for every in-scope org and email each correspondent a list of new dates they cover (with `.ics` attachments).
2. **Detect new board packs** for meetings in the detection window (the previous 2 days through the next 10 days, inclusive of today), run the pack through the `pack-analyser` sub-skill, and email the assigned correspondent the analyser's output.

By default everything is **dry-run** — emails are written to `dry_run_output/` rather than sent. Add `--live-emails` to actually send via Gmail SMTP (using `send_email.py`).

## What this skill does

1. Pull latest state from GitHub so two team members running the skill don't duplicate alerts.
2. For each in-scope org, fetch the board page and extract upcoming meeting dates.
3. Compare against `state/meetings.json`. Anything new becomes a date alert.
4. Generate `.ics` files for new meetings.
5. For meetings with a date in the detection window (previous 2 days through next 10 days, inclusive of today), check the papers page for new pack files.
6. For each newly detected pack, invoke the `pack-analyser` sub-skill — applies HSJ editorial context, writes a markdown summary to `summaries/`, returns top lines.
7. Rebuild `subscriptions/{firstname}.ics` for each correspondent — one combined `.ics` per person, containing every meeting tracked for the orgs they cover (not just the new ones from this scan).
8. Compose two kinds of email per correspondent:
   - **Date alerts** — batched, one per correspondent per scan, listing the new meetings detected this run for orgs they cover. The combined `subscriptions/{firstname}.ics` is attached. The recipient clicks the attachment → Outlook opens → "Save & Close" / "Save to Calendar" imports all events. Outlook deduplicates by UID, so re-importing on later scans only adds the new ones.
   - **Papers alerts** — one per analysed pack, with the pack-analyser summary inline + summary markdown attached.
9. Send via `send_email.py` if `--live-emails`, otherwise write to `dry_run_output/`.
10. Update state, commit, push.

## Helper scripts in the repo

| Script | Purpose |
|---|---|
| `send_email.py` | Send Gmail SMTP alerts. Reads `GMAIL_USER`/`GMAIL_APP_PASSWORD` from `.env.local`. Handles `.ics` attachments with `text/calendar; method=PUBLISH` so Outlook recognises them. |
| `fetch_with_playwright.py` | Headless Chromium fetcher with stealth-lite. Used as the fallback when WebFetch hits Cloudflare/UA blocks or JS-rendered pages. `--text` for visible text, `--html` for full DOM, `--download --out FILE` for binary downloads. |
| `fetch_pdf_text.py` | Download a PDF and extract its text with pypdf. Use when an org publishes board dates inside an annual calendar PDF rather than on a webpage. Try `requests` mode first; pass `--playwright` if the host blocks direct downloads. |

## Arguments

| Argument | Meaning |
|---|---|
| `--correspondent NAME` | Only scan orgs assigned to this correspondent (e.g. `--correspondent Henry`). |
| `--orgs CODE1,CODE2` | Only scan these ods_codes (e.g. `--orgs RA2,QYG`). Useful for testing. |
| `--region NAME` | Only scan orgs in this region (e.g. `--region "North West"`). |
| `--dates-only` | Skip pack detection and analysis. Just refresh meeting dates. |
| `--packs-only` | Skip date scanning. Only check papers for meetings in the detection window (previous 2 days → next 10 days, inclusive of today). |
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

There is a **three-step fallback ladder**. Try cheap fetchers first, escalate only on failure.

#### 4a — WebFetch (default)

For each org, **WebFetch** the `url` with this prompt:

> Today is {today}. Return JSON ONLY (no prose, no markdown fences). Schema: `{"meetings":[{"date":"YYYY-MM-DD","title":"...","papers_url":"URL or null"}]}`. List every upcoming PUBLIC board meeting in the next 12 months. Exclude past meetings, committee meetings, private/closed sessions. UK dates may be DD/MM/YYYY. If you find no future meeting dates return `{"meetings":[]}`. If the page needs JavaScript return `{"meetings":[],"_error":"needs_js"}`.

A WebFetch is considered to have **failed** when:
- It returns `_error: needs_js`
- It returns HTTP 403 (Cloudflare / UA block — affects ~12 big trusts including Sheffield Teaching, Imperial, Royal Marsden, Royal Free, Royal Devon, UHCW, Mersey Care, CWP, Sussex Community, Liverpool UH group, London North West, Clatterbridge)
- It returns HTTP 404 (do NOT assume the URL is dead — many sites serve a **soft-404 to non-browser user agents** while rendering fine in a real browser; e.g. Maidstone & Tunbridge Wells / RWF. Escalate to Playwright before concluding the URL has moved. Only treat a 404 as a genuinely dead URL if Playwright (4b) ALSO returns nothing.)
- It returns content that looks like a cookie banner or nav-only shell (<200 chars after stripping)
- It returns valid JSON with `meetings: []` AND the org's notes field flags "needs Playwright" or similar

#### 4b — Playwright fallback (escalation 1)

When WebFetch fails, escalate to `fetch_with_playwright.py`:

```bash
python fetch_with_playwright.py URL --text > c:/tmp/render.txt
```

This launches headless Chromium with stealth-lite settings (real Chrome UA, `navigator.webdriver` hidden, GB locale). It bypasses the WAF/UA blocks that defeat WebFetch.

Then process the rendered text the same way (extract dates manually or via a subagent with the same prompt as 4a).

Record in the org's `notes` that Playwright was used (e.g. `"detected via playwright"`) so future runs go straight to step 4b instead of wasting a WebFetch call.

#### 4c — PDF fallback (escalation 2)

When both 4a and 4b return no dates (the page renders but lists no forward schedule — common when the trust publishes an annual board calendar PDF rather than HTML dates), escalate to `fetch_pdf_text.py`:

1. Look in the rendered HTML (from 4b) for PDF links whose text suggests forward dates: "Schedule of meetings", "Annual board calendar", "Board dates 2026/27", "Forward plan". Or pick the most recent board agenda PDF — it usually states the next meeting date on page 1. AGM packs often list the year's full schedule.
2. Download + extract: `python fetch_pdf_text.py PDF_URL [--playwright] > c:/tmp/pdf.txt`. Use `--playwright` if the host blocks requests-based downloads.
3. Process the extracted text the same way (find dates 2026–2027, normalise to ISO).

Time-box: 1–2 candidate PDFs per org. Don't drain the budget on speculative downloads.

#### 4d — Give up gracefully

If all three steps fail, log a `_scan_errors` entry in state and move on. Do NOT crash the whole run. Update the org's `notes` field with what was tried so the next session knows.

#### After extraction

- **Normalise dates** to ISO `YYYY-MM-DD`. UK ambiguous formats (DD/MM/YYYY vs MM/DD/YYYY) — always interpret as DD/MM/YYYY for NHS sites.
- **Validate** — reject anything >18 months in the future, in the past, or that fails as a real date (e.g. "TBC", "2026-13-45").

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

### Step 7 — Detect new packs (detection window: previous 2 days → next 10 days)

(Skip if `--dates-only`.)

For each meeting in state where:

- The date falls in the detection window: from **2 days before today** through **10 days after today**, inclusive of today (i.e. `today - 2 days <= meeting_date <= today + 10 days`)
- AND status is `date_found` or `papers_found` (re-check in case supplementary papers were added)

The window reaches back 2 days because many trusts publish (or only finish uploading) the board pack on the morning of the meeting or the day after, so a meeting that has just happened often only now has papers online. Treat a meeting from the last 2 days exactly like an upcoming one — detect, analyse, and alert. (Example: a scan on Thu 28 May picks up a pack for a Wed 27 May meeting that wasn't online when the previous scan ran.)

Do:

1. Pick the URL to scan for papers — use `papers_url` if populated, else `source_url`.
2. **WebFetch** that URL with this prompt:

   > Today is {today}. The page is the board papers page for a meeting on {date}. Return JSON ONLY: `{"pack_files":[{"url":"...","title":"...","kind":"pdf|other"}]}`. List every PDF or document linked from this page that appears to be a paper for the {date} meeting (agenda, finance report, performance report, CEO report, minutes, action tracker, risk register, etc.). Exclude documents from other meetings. Make URLs absolute. If nothing found return `{"pack_files":[]}`.

3. If WebFetch fails (same conditions as Step 4a — 403, needs_js, empty), fall back to `python fetch_with_playwright.py URL --html` and parse the HTML for `<a href="*.pdf">` links yourself. Apply the same "is this for the {date} meeting?" filter.

4. When downloading the actual PDFs (for the pack-analyser sub-skill), use `python fetch_pdf_text.py PDF_URL [--playwright]` — many trust sites that allow WebFetch on HTML still block direct PDF GETs from non-browser UAs.

5. **Two-hop papers pages — follow the per-meeting link before concluding "no papers".** Some trusts publish a board-meetings *listing* page (just a list of dates, often year-tabbed) where the actual pack PDF lives one click deeper, on a per-meeting page. If the `papers_url` returns meeting dates/titles but **zero PDF links**, do not record "no papers yet" — look for an anchor whose text or href matches the target meeting `{date}` (e.g. CUH: `/events/board-of-directors-meeting-10-june-2026/`), fetch THAT page, and extract the PDFs from it. With Playwright, parse anchor `href`s (`--html`), not just the `--text` dump, because these links are frequently absent from rendered text. Honour the org `notes` field — if it documents a per-meeting/event-page pattern, go straight there. (CUH/RGT is the worked example; the same shape recurs on other trusts using an events-calendar CMS.)

6. **Do not infer pack completeness from filenames.** A title like "Agenda" can mean either an agenda-only file *or* a full combined pack — trusts use inconsistent naming. Before deciding a meeting "has no papers yet", download the candidate file and check its size and page count. Full packs are typically >5MB and >100 pages; agendas-only are <1MB and <20 pages. If a file the same size as previous months' packs exists, treat it as the pack regardless of what its filename says.

7. Compare returned `pack_files` against the meeting's existing `pack_files` in state.

8. **If new files found:**
   - Append to `pack_files` in state.
   - Set meeting status to `papers_found`.
   - Add the meeting (with full new pack URL list) to a `new_packs` list for the analyser step.

### Step 7b — Papers watchlist (orgs with no confirmed date)

(Skip if `--dates-only`.)

A trust can publish a new board pack before we've recorded the meeting date. The detection-window pack scan (Step 7) would miss it. So on every run we also poll the papers/board page of every in-scope org **that has no future-dated meeting in state**. If a new pack appears, we alert immediately and try to backfill the date from the pack filename or contents.

State for this lives in `state/papers_watchlist.json`:

```json
{
  "_format_version": 1,
  "orgs": [
    {
      "ods_code": "RXG",
      "papers_url": "https://...",
      "last_checked": "ISO timestamp",
      "known_files": [
        {"url": "...", "title": "...", "first_seen": "ISO"}
      ],
      "notes": "what we know about how this org publishes papers"
    }
  ]
}
```

For each org in the watchlist:

1. Fetch the papers/board URL (ladder: WebFetch → Playwright → PDF metadata as in Step 4).
2. Extract every PDF link visible on the page (regardless of whether we can identify the meeting date for it).
3. Compare against `known_files`. Anything new is the trigger.
4. **If new files**:
   - Append to `known_files` with `first_seen` = now.
   - Try to infer a meeting date from the new filename or first page: titles like `Trust Board 8 July 2026.pdf` or `Board pack 2026-07-08.pdf` are common. If you find a date and it's future, **add a real meeting entry** to `state/meetings.json` with `status: papers_found`, source `source_url = papers_url`, and the new pack already in `pack_files`. The org now leaves the watchlist (it has a dated meeting in state).
   - If you can't infer the date, still alert the correspondent: subject `[PAPERS — DATE UNKNOWN] {org name} board — new pack detected`, body lists the file(s) and asks the journalist to confirm the date manually. Keep the org on the watchlist with the new files added to `known_files`.

A watchlist org is **removed** the moment it has any future-dated meeting in state (its papers will be checked through the normal Step 7 path going forward).

A watchlist org is **added** the first time the scanner runs after the org's last future meeting passes (or — for first-time-added orgs — the first time the date scan returns empty for it).

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

   ## Add to your calendar

   A calendar file ({firstname}.ics) is attached. It contains every board
   meeting the tool has detected for the orgs you cover ({total} events).

   **To import all dates at once:** click the attachment → Outlook opens →
   'Save & Close' or 'Save to Calendar'. Re-importing on later scans
   doesn't duplicate (Outlook dedupes by UID).

   — Board paper machine
   ```

3. Subject: `[Board paper machine] {N} new meeting date(s) detected`
4. Attach `subscriptions/{firstname}.ics` (the single combined file rebuilt in Step 9, not the per-meeting `ics/*.ics` files).

Note on the calendar file: a combined `subscriptions/{firstname}.ics` is rebuilt from state on every scan (see Step 9). Per-meeting `ics/{ods_code}_{date}.ics` files are still written for audit but no longer attached to alert emails.

### Step 10 — Compose papers alerts (one per analysed pack)

For each analysed pack:

1. Look up correspondent's email. If empty, log and skip.
2. Read `summaries/{ods_code}_{date}.md` — the FULL summary goes in the body.
3. Compose email body — paste the entire summary inline (Henry's preference, set 2026-06-05), and still attach the same markdown file:

   ```
   Hi {first_name},

   New papers detected for {org name}'s board meeting on {date_human}.
   The pack-analyser found {N_LEAD} LEAD / {N_WATCH} WORTH WATCHING / {N_FOI} FOI items.

   Full summary below (also attached as markdown).

   ---

   {ENTIRE contents of summaries/{ods_code}_{date}.md, verbatim}

   ---

   Pack source: {papers_url}

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
  --attach subscriptions/{firstname}.ics    # for date alerts (one combined file)
  --attach {summary_path}                   # for papers alerts (the markdown summary)
```

Also remember to update `ACTIVITY_LOG.md` at the repo root with a plain-English entry covering what changed this run — what was scanned, what was found, what failed, what's still pending. This log is for Henry to skim across sessions; treat it like commit notes but in non-technical language.

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
- **Honour the `notes` field.** If `notes` says "needs Playwright" or "papers on archive subpage" or "PDF schedule", read it and skip cheaper fetchers that have already failed. Don't burn budget re-discovering known failures.
- **Trust `cluster_id`.** Trust and ICB records can both carry `cluster_id` (e.g. `NWUHG`, `DLN`, `STW-SSOT`). When set, all members share the same `url` and meeting dates. Dedupe at the email/subscription layer, but keep one state entry per ods_code for audit.
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

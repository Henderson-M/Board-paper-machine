---
name: scan-boards
description: Scan NHS trust and ICB board pages for new meeting dates and (for meetings from the previous 2 days through the next 10 days) new board packs, then alert the assigned HSJ correspondent. Use when the user types /scan-boards, asks to "check board meetings", "refresh board dates", or similar.
---

# /scan-boards

You are running a scan of NHS trust and ICB board pages on behalf of an HSJ journalist team.

The skill has two purposes that run in the same sweep:

1. **Detect new meeting dates** for every in-scope org and email each correspondent a list of new dates they cover (with `.ics` attachments).
2. **Detect new board packs** for meetings in the detection window (the previous 2 days through the next 10 days, inclusive of today), run the pack through the `pack-analyser` sub-skill, and email the assigned correspondent the analyser's output.

By default everything is **dry-run** — emails are written to `dry_run_output/` rather than sent. Add `--live-emails` to actually send via Gmail SMTP, staggered 30–60s apart (using `send_batch.py`).

## What this skill does

1. Pull latest state from GitHub so two team members running the skill don't duplicate alerts.
2. For each in-scope org, fetch the board page and extract upcoming meeting dates.
3. Compare against `state/meetings.json`. Anything new becomes a date alert.
4. Generate `.ics` files for new meetings.
5. For meetings with a date in the detection window (previous 2 days through next 10 days, inclusive of today), check the papers page for new pack files.
6. For each newly detected pack, invoke the `pack-analyser` sub-skill — applies HSJ editorial context, writes a markdown summary to `summaries/`, returns top lines.
7. Rebuild `subscriptions/{firstname}.ics` for each correspondent — one combined `.ics` per person, containing every meeting tracked for the orgs they cover (not just the new ones from this scan). "Orgs they cover" means every org for which the person is a **recipient** — primary `correspondent` *or* listed in `additional_correspondents` (see Step 2). So an org's meetings appear in the calendars of all its recipients. This full snapshot is kept for audit / re-seeding a fresh calendar but is **NOT** attached to routine date alerts (see Step 9).
8. Compose two kinds of email per correspondent:
   - **Date alerts** — batched, one per correspondent per scan, listing the new meetings detected this run for orgs they cover. A **delta** `.ics` containing ONLY this run's new meetings for that person is attached (`subscriptions/new/{firstname}_{rundate}.ics`). The recipient opens the attachment → Outlook → "Save & Close" to add just those new dates. **Do NOT attach the full snapshot.** Outlook does NOT dedupe `.ics` *file* imports by UID (it only dedupes subscribed calendar feeds and meeting invites) — attaching the full meeting list every run is what created duplicate calendar entries. Attaching only the new dates avoids duplicates at the source.
   - **Papers alerts** — one per analysed pack, with the pack-analyser summary inline + summary markdown attached.
   - **Withdrawal alerts** — one per correspondent, listing meetings we previously alerted that are now `cancelled` or `retracted`, with a `METHOD:CANCEL` `.ics` attached (`subscriptions/withdrawn/{firstname}_{rundate}.ics`). See Step 8b. Without this the correspondent's calendar keeps a meeting that will not happen.
9. Send via `send_batch.py` (staggered, 30–60s apart) if `--live-emails`, otherwise write to `dry_run_output/`.
10. Update state, commit, push.

## Helper scripts in the repo

| Script | Purpose |
|---|---|
| `send_batch.py` | **Preferred for live sends.** Sends a manifest of alerts one at a time with a randomised 30–60s gap (anti-spam staggering) and writes a per-email results JSON. Wraps `send_email.py`. |
| `send_email.py` | Send a SINGLE Gmail SMTP alert (ad-hoc/resend). Reads `GMAIL_USER`/`GMAIL_APP_PASSWORD` from `.env.local`. Handles `.ics` attachments with `text/calendar; method=PUBLISH` so Outlook recognises them. |
| `fetch_with_playwright.py` | Headless Chromium fetcher with stealth-lite. Used as the fallback when WebFetch hits Cloudflare/UA blocks or JS-rendered pages. `--text` for visible text, `--html` for full DOM, `--download --out FILE` for binary downloads. |
| `fetch_pdf_text.py` | Download a PDF and extract its text with pypdf. Use when an org publishes board dates inside an annual calendar PDF rather than on a webpage. Try `requests` mode first; pass `--playwright` if the host blocks direct downloads. |
| `reverify_dates.py` | **Runs Step 5b for you.** `--limit 120` picks the rolling slice (nothing verified in 28 days, oldest first, plus everything due within 21 days regardless), re-checks each against the org's `schedule_url`, writes `last_verified` on what it confirms, updates org health, and prints a CONTRADICTED list. It deliberately does NOT retract or email — retraction owes a withdrawal alert, and that judgement stays with this skill. `--orgs`, `--all`, `--json`, `--no-write` for testing. |
| `org_health.py` | **Per-org scan health.** `record --ods X --result ok\|fail [--kind K] [--detail "..."]` after each org; `report [--markdown]` at the end. Keeps `state/org_health.json` with consecutive-failure counts, last success, and a broken/degraded/stale classification. This is what makes a persistent failure escalate instead of scrolling past. |
| `extract_board_html.py` | **Deterministic (no-LLM) cross-check.** Fetches raw HTML (`requests` → Playwright fallback) and reports, verbatim, every date and every document link actually present, plus a table-row pairing (date ↔ its papers link / "unavailable" cell). Use it to catch content the WebFetch summariser silently *dropped* — see the anti-omission cross-check in Step 4 and Step 7. Also recognises **extension-less CMS download-handler links** (`/download-attachment/NNNN`, `/download_file/…`, `/seecmsfile/?id=…`) that have no `.pdf` suffix, and recovers **year-headed date lists** ("board dates 2026: 5 August, 7 October, 2 December") — those come back with `year_inferred: true`, so still run the literal day/month check before recording them. `--html-file FILE` parses HTML you already fetched (e.g. a Playwright `--html` dump) so no page is fetched twice; `--pretty` indents the JSON. |

## Arguments

| Argument | Meaning |
|---|---|
| `--correspondent NAME` | Only scan orgs assigned to this correspondent (e.g. `--correspondent Henry`). |
| `--orgs CODE1,CODE2` | Only scan these ods_codes (e.g. `--orgs RA2,QYG`). Useful for testing. |
| `--region NAME` | Only scan orgs in this region (e.g. `--region "North West"`). |
| `--dates-only` | Skip pack detection and analysis. Just refresh meeting dates. |
| `--packs-only` | Skip date scanning. Only check papers for meetings in the detection window (previous 2 days → next 10 days, inclusive of today). |
| `--no-reverify` | Skip Step 5b, the rolling re-verification of dates already in state. Faster, but stale bad dates survive. |
| `--no-pull` | Skip the initial `git pull`. Use for testing offline. |
| `--no-push` | Skip the final `git commit && git push`. Use for testing. |
| `--limit N` | Stop after scanning N orgs. Useful for first-time runs. |
| `--live-emails` | Actually send emails via Gmail SMTP. Without this, all emails are dry-run files. |
| `--operator NAME` | Who is running this sweep (`Henry`, `Dave`, or an email address). Determines who gets the run report. If omitted, resolve from `git config user.email`; if that fails, ASK before sending anything live. |

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

> **Run every `git` command through the Bash tool, never PowerShell.** The user's
> `~/.claude/settings.json` allows `Bash(git:*)`, and permission rules are keyed by
> tool name — a `Bash(...)` rule does **not** match a PowerShell call. Running
> `git push` via PowerShell gets blocked by the auto-mode classifier and the run
> stalls at the last step with everything committed but unpushed (this happened on
> 2026-08-03). Bash syntax for the repo path:
> `cd "/c/Users/henry.anderson/OneDrive - HSJ Information Ltd/Documents/My assistant/projects/Board-paper-machine" && git push origin main`

### Step 1 — Sync state (HARD GATE — do not skip, do not proceed on stale state)

**This is the single most important step. Skipping or faking it causes duplicate alerts to the whole team** (this happened on 2026-07-30: a run started from 3-day-stale state, never saw a colleague's 27 Jul sweep, and re-emailed ~22 packs the team had already received). Two people cover different patches and both run this tool, so the GitHub copy is the only source of truth for "what's already been alerted."

**You MUST actually fetch — never trust the local `origin/*` ref, it can be stale.** A `git status` that says "up to date with origin/main" proves nothing until you have fetched.

```bash
git fetch origin                                   # REQUIRED first — refreshes origin/main
git rev-list --left-right --count HEAD...origin/main   # -> "<ahead> <behind>"
```

Then:

- **behind = 0, ahead = 0** → in sync. Proceed.
- **behind > 0** → the remote has newer work (another run). You MUST integrate it before scanning: `git pull --rebase` (working tree must be clean; commit or stash local changes first). Re-run the `rev-list` check until behind = 0.
- **fetch or pull FAILS, is blocked (sandbox/permission), times out, or you cannot reach GitHub for any reason** → **STOP THE ENTIRE RUN. Do not scan. Do not analyse. Do not send a single email.** Surface the exact error to the user and say you cannot run safely without a synced state. Running blind on stale state is never acceptable — a missed run is recoverable next time; duplicate alerts to the team are not. (If the user explicitly says "run anyway, dry-run only, I accept it may duplicate", you may proceed **but must force `--live-emails` OFF** and label every output as UNVERIFIED-STALE.)

Only once `behind = 0` may you continue to Step 2.

### Step 2 — Load inputs

Read these files:

- `data/trust_urls.json`
- `data/icb_urls.json`
- `data/correspondents.json` (name → email map)
- `data/recipient_overrides.json` (temporary recipient overrides — optional; absent/empty is fine)
- `state/meetings.json` (known meetings)
- `context/hsj_editorial_context.md` (only needed if running pack analysis)

Build a list of in-scope orgs, filtered by any arguments. Each org needs: `ods_code`, `names[0]`, `url`, `schedule_url`, `correspondent`, `org_type` (`trust` or `icb`).

Skip orgs with empty/null `url`, and skip those whose correspondent is `"TBC"` or null. Log the count skipped.

**Which URL to scan for DATES — `schedule_url` wins.** Many orgs put their board *papers* on one page and their forward *schedule* on another (a "Future meetings" subpage, a year subpage, an events calendar). The `schedule_url` field records that page explicitly. For the date scan (Step 4) the precedence is:

1. `schedule_url` if set — this is the maintained field and it always wins
2. else `url`

Never rely on free-text `notes` to carry this. Notes are for humans; `schedule_url` is what the run reads. If you discover an org's dates live somewhere other than `url`, **set `schedule_url`** — do not just write it in `notes`.

Worked failure (2026-08-17): EMAS/RX9's `url` is `/next-board-meeting`, a page that by design shows only the single next meeting, while its notes recorded that the full schedule was at `/next-board-meeting/future-meetings`. A verification pass that read only `url` concluded 14 of EMAS's dates were fabricated; 7 of them were real and on the subpage. Half a day of retractions was nearly sent on that basis. The same shape covers roughly half the orgs flagged in that pass.

**Recipients per org.** An org may also carry an optional `additional_correspondents` array (e.g. all ambulance trusts also go to `"Alison"` as well as their primary correspondent). Throughout this skill, the **recipients** of an org's alerts are the union of its `correspondent` and every name in `additional_correspondents`, **de-duplicated** (if a name appears as both, it's one recipient). A name in `additional_correspondents` that is `"TBC"`/null or has no email in `correspondents.json` is logged and skipped, exactly like a primary. Wherever a later step says "group/route by correspondent", it means **by recipient** in this sense — a single org's meeting or pack can therefore produce an alert for more than one person.

**Never key a file, a manifest `id`, or anything else per-recipient on the recipient's FIRST NAME.** There are two Matts (`Matt Discombe` and `Matt Mathers`) and both shorten to `matt`. Use the full correspondent key, slugified — `matt-discombe`, `matt-mathers`. Worked failure (2026-08-17): a withdrawal run wrote both Matts' bodies to `20260817c_Matt_withdrawn.md` and both `.ics` files to `matt_20260817c.ics`; the second overwrote the first, and Matt Discombe was sent an email headed "6 incorrect meeting date(s)" whose body and attachment contained Matt Mathers' single unrelated date. A correction had to be sent. The `{firstname}` in the subscription paths below is a legacy shorthand — read it as "slugified full correspondent key" and it is safe.

**Temporary recipient overrides.** After building an org's base recipient set (above), apply any live rules in `data/recipient_overrides.json` (skip this if the file is absent or has no `overrides`). For each rule:

- **Expiry gate.** The rule is **live** only when `start <= today <= expires` (ISO date strings compare correctly as text; `today` is the run date). If `today > expires`, the rule has **expired — ignore it entirely** (do not add anyone). Log expired rules you skipped so it's visible they lapsed.
- **Match.** If the rule's `when_recipient` is in this org's recipient set, add every name in `add_recipients` to the recipient set, **de-duplicated**, with the same `"TBC"`/no-email handling as a primary (a rule name with no email in `correspondents.json` is logged and skipped).
- **Kind filter.** `applies_to` limits which alert kinds the added name receives: `"date"` covers date alerts (Step 9) and the delta `.ics`; `"papers"` covers papers alerts (Step 10) and the DATE-UNKNOWN watchlist alert (Step 7b). Only treat the added name as a recipient for the kinds listed. A rule listing both makes the added name a full co-recipient of that org, exactly as if they were in `additional_correspondents` — including their subscription `.ics` snapshot (Step 7) and their delta `.ics` for date alerts.

An override never *removes* a recipient and never changes who the primary correspondent is — it only adds shadow recipients for a bounded window. (Current live rule: copy **Ella** on everything that goes to **Matt Discombe** until 2026-10-28.)

### Step 3 — Handle ICB clusters

In `icb_urls.json`, some ICBs share a board meeting via `cluster_id` and `cluster_meeting_url`. Group these so you only scan the cluster meeting URL once per cluster, then report detected meetings to all correspondents in the cluster (de-duplicating if they're the same person).

### Step 4 — Scan each org's board page for dates

(Skip if `--packs-only`.)

There is a **three-step fallback ladder**. Try cheap fetchers first, escalate only on failure.

#### 4a — WebFetch (default)

For each org, **WebFetch** its date-scan URL (`schedule_url` if set, else `url` — see Step 2) with this prompt:

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

- **Anti-fabrication guard (MANDATORY — run on every detected date, WebFetch and Playwright alike).** WebFetch extracts dates with a small fast model that will sometimes **project or hallucinate a schedule that is not on the page** (e.g. "completing" a cadence, or inventing next-year dates). Before a detected date is allowed to become a `new_meeting`:
  1. **Literal-source check.** The date MUST appear as literal text in the fetched page / rendered output. Re-fetch the source text if needed (Playwright `--text`) and confirm the day/month (in any common format — `27 November`, `27/11/2026`, `2026-11-27`, `Fri 27 Nov`) is actually present. If a returned date does not appear in the source text, **DROP it** — do not record it. Never trust the extractor's JSON on its own.
  2. **No cadence extrapolation.** Only record dates the source literally lists. **Never** infer "missing" meetings, complete an alternating-month or last-Friday pattern, or project into a calendar year the page does not display. If the page's schedule header/tabs stop at the current year, do not emit any next-year dates.
  3. **Weekday sanity.** NHS public boards almost always meet **Monday–Friday**. Flag and drop any Saturday/Sunday date unless the page explicitly shows that weekend day for that meeting.
  4. **Whole-series smell test.** If the *only* new dates for an org are ones that extend beyond the schedule the page actually shows (e.g. the page lists 2026 but you're about to add 2027 dates), treat the whole set as suspect and re-derive from the raw text before recording anything.
  Worked failure (2026-07-16 run, RTD Newcastle): the extractor returned six even-month/2027 Fridays (plus one Saturday) that were **nowhere on the page** — the trust actually meets bi-monthly in odd months and publishes 2026 only. All six passed the old date-range/real-date validation and were alerted in error. The literal-source check above would have dropped every one.

- **Anti-omission cross-check (MANDATORY — the mirror image of the guard above).** The anti-fabrication guard catches dates the extractor *invented*. The opposite failure is just as damaging and is **invisible** without a check: WebFetch (and Playwright `--text`) summarise with a small model that sometimes **drops real dates that ARE on the page** — most often on long, non-chronological tables where most rows say "Currently unavailable" or "papers to follow". A dropped date is never detected, so no meeting is created and its pack is never scanned. Nothing in the run looks wrong.
  1. **Run the deterministic extractor** on the same URL and reconcile:
     ```bash
     python extract_board_html.py URL --pretty > c:/tmp/deterministic.json
     ```
     It does no summarising — it regexes every date and every document link literally present in the raw HTML, and pairs them by table row. If you already fetched the page with Playwright `--html`, pass `--html-file` to avoid a second fetch.
  2. **Recover the difference.** Any date in `deterministic.json.dates` that is a valid future public board date (apply the *same* validation and anti-fabrication literal-source rules as above — these recovered dates are literal by construction, so they pass trivially) but is **missing** from the WebFetch/Playwright extraction MUST be added as a `new_meeting`. Use the `rows` pairing to attach the right `papers_url`/pack link where the date shares a table row with a document link.
  3. **Empty is not a veto.** If the deterministic extractor returns no dates via `requests` (JS-rendered or two-hop pages — e.g. Bradford/RAE, whose landing page needs Playwright or a year-subpage hop), that is NOT evidence the page is empty. Escalate it with `--playwright`, or fall back to the WebFetch/Playwright result you already have. This check only ever **adds** dropped items back — it never removes what WebFetch found.
  Worked failure (2026-06-24, Leeds Community Healthcare / RY6): the WebFetch date-scan dropped the 23 July + 24 June rows from a single non-chronological table (September was listed above July above June; most cells read "Currently unavailable"). Both were real and had to be hand-added, and the 23 July pack was then missed on the 20 July run. `extract_board_html.py` returns both dates via plain `requests` and pairs 23 July directly to `LCH-Public-Board-meeting-papers-July-2026.pdf` — this check would have caught it automatically.

### Step 5 — Diff dates against state

For each detected meeting:

- Build an `id` = `{ods_code}:{date}`.
- If `id` exists in `state/meetings.json`, just update `last_checked`.
- If new, add an entry with status `date_found` and append to a `new_meetings` list.

### Step 5b — Re-verify dates ALREADY in state (rolling audit)

(Skip if `--packs-only`. Skip with `--no-reverify` if you need a fast run.)

**Detecting a date correctly once is not enough — this step re-checks dates we recorded on earlier runs.** Every guard in Step 4 only ever fires at the moment a date is first detected. A date that was wrong when it went in stays wrong forever, keeps being emailed out, and sits in a correspondent's calendar until a human happens to notice. On 2026-08-17 a full audit found **76 such dates across 33 orgs, 56 of them already emailed** — some recorded as far back as June, several at orgs whose `notes` already described the exact fabrication.

On every full run, run the script — do not do this by hand:

```bash
python reverify_dates.py --limit 120 --json c:/tmp/bpm_reverify.json
```

It picks the slice, fetches, checks and writes `last_verified` itself. **Your job is only to act on what it prints as CONTRADICTED** — retract those meetings, and where `alerted=True` and the date is still future, they owe a withdrawal alert under Step 8b. The script never retracts or emails on its own, because a retraction has a human cost and needs this skill's judgement.

What it does, for reference:

1. **Choose the slice.** All future-dated meetings whose `last_verified` is absent or older than **28 days**, capped at ~120 meetings per run so the sweep stays affordable. Oldest `last_verified` first. Always include every meeting dated in the **next 21 days** regardless of when it was last verified — those are the ones people are about to act on.
2. **Fetch the org's date-scan URL** (`schedule_url` if set, else `url`), Playwright `--html` preferred so collapsed accordions and tab panels are included.
3. **Literal check.** The meeting's day+month must appear as literal text, in any common UK format. Accept zero-padded days (`07 October`), `DD-Mon-YY` (`17-Sep-26`), and ordinals. **Do not** require the year to be adjacent — many pages carry a year heading above a bare day/month list.
4. **Classify, and only act on the unambiguous case:**
   - **found** → set `last_verified` to now. Done.
   - **not found, and the page publishes no future dates at all** → `unverifiable`. Set `last_verified` and move on. This is NOT an error — plenty of orgs publish no forward schedule. Never retract on this.
   - **not found, and the page DOES publish a future schedule** → the page contradicts us. Retract it, and if `alerts_sent.date` is set and the date is still in the future, it owes a withdrawal under Step 8b.
5. **Record what the page said** in the meeting's `notes` when you retract, so the next person can see the basis without re-fetching.

Three failure modes this catches, all seen in real state:

- **Month shift** — right day number, wrong month (a real "Wednesday 29 July 2026" recorded as 29 August, at two unrelated trusts in the same week).
- **Day default** — a month-only heading ("November 2026 Board Meeting") becoming the 1st of that month.
- **Cadence projection** — a plausible series (every first Tuesday) invented past whatever the page actually lists.

**Two traps to avoid — both were hit while building this step:**

- **Check the right page.** Reading `url` when the schedule lives at `schedule_url` makes real meetings look fabricated. Half of one audit's "errors" were this. Always resolve the URL as in Step 2.
- **Your matcher is a suspect too.** The first version of this audit missed zero-padded days, so `Wednesday 07 October 2026` read as absent and 19 real dates were flagged. Before trusting a large batch of "missing" results, hand-check several against the page text, and be suspicious of any org where *every* date is missing — that is far more likely a bad fetch than a bad org.

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

1. Pick the URL to scan for papers, in this order: the meeting's `papers_url` if populated, else the **org record's** current `papers_url`, else the **org record's** current `url`, else the meeting's `source_url`.

   **Never reach for a meeting's `source_url` before checking the org record.** A meeting's `source_url` is a snapshot of where that date was found, sometimes months ago; the org record's `url` is the *maintained* field and is what earlier runs correct when they discover a URL has moved. Preferring the stale snapshot silently re-scans a page a previous run already declared dead — the scan "fails", the org gets logged as broken, and the fix that was already made is invisible.

   Worked failure (2026-08-06, RBS Alder Hey): the 3 Aug run had already corrected the org `url` to the working publications archive, but the 6 Aug packs-only run read the meeting's `source_url` — the dead `/about-us/trust-board/` page that serves 2018 content — concluded the org was still unscannable, and reported "needs a corrected URL" for a URL that had already been corrected. If the meeting `source_url` and the org `url` disagree, the org record wins; update the meeting's `source_url` to match so the divergence does not persist.
2. **WebFetch** that URL with this prompt:

   > Today is {today}. The page is the board papers page for a meeting on {date}. Return JSON ONLY: `{"pack_files":[{"url":"...","title":"...","kind":"pdf|other"}]}`. List every PDF or document linked from this page that appears to be a paper for the {date} meeting (agenda, finance report, performance report, CEO report, minutes, action tracker, risk register, etc.). Exclude documents from other meetings. Make URLs absolute. If nothing found return `{"pack_files":[]}`.

3. If WebFetch fails (same conditions as Step 4a — 403, needs_js, empty), fall back to `python fetch_with_playwright.py URL --html` and parse the HTML for `<a href="*.pdf">` links yourself. Apply the same "is this for the {date} meeting?" filter.

4. When downloading the actual PDFs (for the pack-analyser sub-skill), use `python fetch_pdf_text.py PDF_URL [--playwright]` — many trust sites that allow WebFetch on HTML still block direct PDF GETs from non-browser UAs.

5. **Two-hop papers pages — follow the per-meeting link before concluding "no papers".** Some trusts publish a board-meetings *listing* page (just a list of dates, often year-tabbed) where the actual pack PDF lives one click deeper, on a per-meeting page. If the `papers_url` returns meeting dates/titles but **zero PDF links**, do not record "no papers yet" — look for an anchor whose text or href matches the target meeting `{date}` (e.g. CUH: `/events/board-of-directors-meeting-10-june-2026/`), fetch THAT page, and extract the PDFs from it. With Playwright, parse anchor `href`s (`--html`), not just the `--text` dump, because these links are frequently absent from rendered text. Honour the org `notes` field — if it documents a per-meeting/event-page pattern, go straight there. (CUH/RGT is the worked example; the same shape recurs on other trusts using an events-calendar CMS.)

6. **Do not infer pack completeness from filenames.** A title like "Agenda" can mean either an agenda-only file *or* a full combined pack — trusts use inconsistent naming. Before deciding a meeting "has no papers yet", download the candidate file and check its size and page count. Full packs are typically >5MB and >100 pages; agendas-only are <1MB and <20 pages. If a file the same size as previous months' packs exists, treat it as the pack regardless of what its filename says.

7. **Anti-omission cross-check (MANDATORY — same failure mode as Step 4, applied to pack links).** The WebFetch pack prompt is summarised by the same small model and will silently drop PDF links on a cluttered or non-chronological papers table — exactly how the Leeds Community (RY6) 23 July pack was missed even though the meeting date was known. Before concluding a meeting has "no new papers", run the deterministic extractor and **union** its document links with WebFetch's:
   ```bash
   python extract_board_html.py {papers_or_source_url} --pretty > c:/tmp/deterministic.json
   ```
   Use the `rows` pairing to keep only links that share a table row with the target `{date}` (or whose anchor text/filename names that meeting), then merge them into `pack_files`. A document link present in the raw HTML for this meeting must not be dropped just because the summariser omitted it. As in Step 4: an empty `requests` result is not a veto — escalate with `--playwright` or keep the WebFetch result; the cross-check only ever adds links back, never removes them.

8. Compare the reconciled `pack_files` against the meeting's existing `pack_files` in state.

9. **If new files found:**
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

   **`known_files` is only trustworthy if it was ever populated.** An org whose `known_files` is EMPTY makes every document on its page look new, including packs earlier runs already analysed and alerted. Before analysing or alerting ANY watchlist pack, confirm it is genuinely new by both:
   - checking whether `summaries/{ods_code}_{inferred_date}.md` already exists (if it does, an earlier run analysed it — do NOT re-alert, just baseline the files into `known_files`); and
   - checking `state/meetings.json` for that org/date.

   Worked failure (2026-08-03): the watchlist reported 7 "new" packs; 6 of them — RR7, RX7, RXE, RXG, RXY, RP6 — had already been analysed and alerted by the 23–31 Jul runs and only looked new because their `known_files` was `[]`. Alerting them would have repeated the 30 July duplicate incident by a different route. After each poll, ALWAYS write every file you saw back into `known_files`, even when you raise no alert — an empty baseline is the bug.
4. **If new files**:
   - Append to `known_files` with `first_seen` = now.
   - Try to infer a meeting date from the new filename or first page: titles like `Trust Board 8 July 2026.pdf` or `Board pack 2026-07-08.pdf` are common. If you find a date and it's future, **add a real meeting entry** to `state/meetings.json` with `status: papers_found`, source `source_url = papers_url`, and the new pack already in `pack_files`. The org now leaves the watchlist (it has a dated meeting in state).
   - If you can't infer the date, still alert **each recipient** of the org (see Step 2): subject `[PAPERS — DATE UNKNOWN] {org name} board — new pack detected`, body lists the file(s) and asks the journalist to confirm the date manually. Keep the org on the watchlist with the new files added to `known_files`.

A watchlist org is **removed** the moment it has a future-dated meeting in state that is actually **verified** — i.e. one whose date was found as literal text on the org's schedule page (Step 5b sets `last_verified`). Holding an *unverified* future date is not enough.

**Why the stricter test.** The old rule dropped an org from the watchlist as soon as state held any future date, verified or not. On 2026-08-17 that left 16 orgs in a dead zone: they publish no forward schedule we can read, so their dates could be neither confirmed nor refuted, yet those same unverifiable dates kept them off the watchlist. They were neither reliably date-tracked nor pack-tracked, and a new pack at any of them would have gone unnoticed. Eleven were added to the watchlist that day; the other five turned out to be readable after all once the right source was found (see `schedule_url`).

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

### Step 8b — Compose WITHDRAWAL alerts (meetings that have gone away)

**A meeting you have already told someone about, and which then disappears, MUST be withdrawn. Silently changing its status in state is not enough — the correspondent's calendar still has it.** This step is the mirror of Step 9: Step 9 tells people a meeting exists, this one tells them it doesn't.

Historically this step did not exist, and by 2026-08-06 **33 meetings had been alerted and then cancelled or retracted with no follow-up — 19 of them still in the future, sitting in correspondents' calendars as meetings that will not happen.** Henry found it because his Barnsley 6 Aug entry was marked CANCELLED on the trust's own page on 27 July and nobody told him. A one-off catch-up was sent on 2026-08-06; from then on this step handles it.

A meeting needs a withdrawal alert when **all** of these hold:

- its `status` is now `cancelled` or `retracted`; **and**
- `alerts_sent.date` is set (we did tell someone it was happening); **and**
- its `date` is **today or later** (a past meeting needs no calendar correction); **and**
- `alerts_sent.withdrawn` is **not** set (we have not already withdrawn it); **and**
- no prior correction is recorded for it — check `notes` / `date_review` for "correction sent". If one exists, **do not re-report it as news**; it may still go in the `.ics` (below), listed under a short "already flagged to you" heading.

Group by **recipient** (Step 2 rules — primary + `additional_correspondents` + live overrides, `applies_to: "date"`). For each recipient:

1. Build a **cancellation `.ics`** at `subscriptions/withdrawn/{firstname}_{rundate}.ics` containing one VEVENT per withdrawn meeting, with:
   - `METHOD:CANCEL` on the VCALENDAR
   - the **same `UID`** as the original event — `{ods_code}-{date}@board-paper-machine.hsj`. This is what lets a client match and remove it; a new UID does nothing.
   - `STATUS:CANCELLED` and `SEQUENCE:1` on the VEVENT
2. Compose the body: say plainly what is being withdrawn and **why, per meeting** — "cancelled by the trust" vs "was never a real date" are different messages and correspondents need to know which. Give the trust's own wording where it cancelled the meeting.
   **Write the reason for a colleague, not for the repo.** The raw `date_review.evidence` is written for auditability and is often a wall of technical detail; summarise it into a sentence or two of plain English. Also strip any double-encoded UTF-8 (`Ã¢â‚¬â€`) that older state entries carry, or it will land in someone's inbox.
3. Be honest about the `.ics` limitation: a `METHOD:CANCEL` file reliably withdraws events the client accepted as invitations, but **Outlook treats hand-imported `.ics` events as the user's own and may not remove them**. Always include the human-readable list and tell the recipient to delete manually if the file does not take. The list is the reliable part, not the attachment.
4. Subject: `[Board paper machine] {N} meeting(s) withdrawn — please delete from your calendar`

After a successful send, set `alerts_sent.withdrawn` to the timestamp on each withdrawn meeting (same `ok:true`-driven rule as Step 11) so it is never withdrawn twice.

### Step 9 — Compose date alerts (one per correspondent)

Group `new_meetings` by **recipient** (see Step 2 — a meeting for an org with `additional_correspondents` lands in the group of its primary correspondent *and* each additional one). For each recipient with new meetings:

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

   A calendar file ({firstname}_{rundate}.ics) is attached containing the
   {N} new date(s) above — nothing else.

   **To add them:** open the attachment → Outlook → 'Save & Close' (once).
   Import it only once: Outlook does not de-duplicate .ics file imports, so
   re-opening the same file would add the events a second time.

   — Board paper machine
   ```

3. Subject: `[Board paper machine] {N} new meeting date(s) detected`
4. Build and attach the delta file `subscriptions/new/{firstname}_{rundate}.ics` — a VCALENDAR containing ONLY this run's `new_meetings` for this recipient (reuse the exact VEVENT blocks written in Step 6, same UIDs). Create the `subscriptions/new/` dir if needed. **Do NOT attach the full `subscriptions/{firstname}.ics` snapshot** — attaching the whole meeting list every run is what created duplicate calendar entries, because Outlook re-adds every event in an imported file rather than deduping by UID.

Note on the calendar files: the **delta** `subscriptions/new/{firstname}_{rundate}.ics` (this run's new meetings only) is what gets attached to date alerts. The full combined `subscriptions/{firstname}.ics` is still rebuilt from state each run (Step 7) but only for audit / re-seeding a calendar from scratch — it is **not** attached to routine alerts. Per-meeting `ics/{ods_code}_{date}.ics` files are also still written for audit.

### Step 10 — Compose papers alerts (one per analysed pack)

For each analysed pack, send one alert to **each recipient** of the pack's org (see Step 2 — primary correspondent plus any `additional_correspondents`, de-duplicated):

1. Look up each recipient's email from `data/correspondents.json`. For any recipient with no email, log and skip that recipient (still send to the others). The email body/subject are identical for each recipient.
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

**Pre-send re-sync guard (MANDATORY before any `--live-emails` send).** A full sweep can take 30+ minutes, during which another team member's run may have pushed and alerted some of the same packs/dates. Immediately before sending, re-check the remote so you don't send what's already been sent:

```bash
git fetch origin
```

Then, for every meeting you are about to alert, compare against `origin/main`'s `state/meetings.json` (`git show origin/main:state/meetings.json`): **drop from the send any meeting whose `alerts_sent.date` (for date alerts) or `alerts_sent.papers` (for papers alerts) is already set on the remote.** Those were alerted by another run — sending again is a duplicate. Log what you dropped. If the remote has moved on (behind > 0), integrate it (`git pull --rebase`) and re-diff before sending. Only send the survivors.

- **Dry-run mode (default):** for each prepared email, write `dry_run_output/{timestamp}_{correspondent}_{kind}.md` with full headers, body, and attachment list inline.
- **`--live-emails` mode:** send via **`send_batch.py`** — a STAGGERED batch sender. **Do not fire all the emails at once.** A free Gmail account sending 40 near-identical multi-attachment messages in a couple of minutes gets quarantined as spam by the recipients' mail gateway (this happened on the 5 Jun 2026 run — emails sent successfully but never reached inboxes). `send_batch.py` sends one at a time with a randomised 30–60s gap so delivery looks human.

Build a **manifest** — a JSON array of `{to, subject, body_file, attach:[...], id}` (one object per email; reuse the same objects you wrote the dry-run files from), then:

```bash
python send_batch.py \
  --manifest {dates_manifest.json} \
  --manifest {papers_manifest.json} \
  --manifest {withdraw_manifest.json} \
  --results {results.json}
  # optional: --min-gap 30 --max-gap 60  (these are the defaults)
  # add --dry-run to preview the plan with no SMTP and no sleeps
```

Each manifest object's `attach` holds the file(s): `subscriptions/new/{firstname}_{rundate}.ics` for a date alert (this run's new-meetings delta — NOT the full snapshot), or `{summary_path}` for a papers alert. A full sweep (~40 emails) takes ~20–40 min to finish sending — that's expected and is the point. `send_batch.py` reconnects per email, keeps going if one fails, and writes `{results.json}` listing per-email `{to, subject, id, ok, err}`.

(For a one-off ad-hoc send — e.g. a single `/pack-analyser` resend — `send_email.py` is still fine; `send_batch.py` just wraps it with staggering for the multi-email sweep.)

Also remember to update `ACTIVITY_LOG.md` at the repo root with a plain-English entry covering what changed this run — what was scanned, what was found, what failed, what's still pending. This log is for Henry to skim across sessions; treat it like commit notes but in non-technical language.

Both senders read `GMAIL_USER` / `GMAIL_APP_PASSWORD` from `.env.local` (gitignored) and send via Gmail SMTP. `.ics` files are attached as `text/calendar; method=PUBLISH` so Outlook renders the inline add-to-calendar button.

Only after a successful send: update the meeting's `alerts_sent.date` / `alerts_sent.papers` / `alerts_sent.summary` timestamp in state — driven by the `ok:true` rows in the `send_batch.py` results JSON, NOT by the analysis step. If a send failed (`ok:false`), leave the flag null and surface the error — we'll retry next run. (Bulk-stamping every analysed pack with one timestamp regardless of send result hides exactly this kind of failure.)

### Step 12 — Update state and persist

1. Update `state/meetings.json` — add new entries, refresh `last_checked` on existing ones, append any `_scan_errors`.
2. Update `data/trust_urls.json` / `data/icb_urls.json` if you learned anything worth recording (e.g. a redirect, a Playwright requirement, a quirk).
3. `git add -A` (excluding gitignored files — `.env.local`, `dry_run_output/`).
4. `git commit -m "scan: {N_dates} new date(s), {N_packs} new pack(s), {E} error(s)"` (omit commit if nothing changed).
5. `git push` unless `--no-push`. **Use the Bash tool** (see the note at the top of this Workflow) — a PowerShell `git push` is blocked by the permission classifier. Do not treat the run as finished until the push has actually landed: re-run `git fetch origin` and `git rev-list --left-right --count HEAD...origin/main` and confirm `0 0`. A committed-but-unpushed run leaves the shared state invisible to the rest of the team, which is exactly the condition that causes duplicate alerts on the next person's run.

### Step 12b — Record scan health for EVERY org (do not skip on failures)

**The whole point of this step is that a failure must not be able to disappear quietly.** Record an outcome for every org you attempted, success or failure, via `org_health.py`:

```bash
python org_health.py record --ods RA2 --result ok --dates 6
python org_health.py record --ods RXA --result fail --kind blocked \
    --detail "HTTP 403 from WebFetch and 0 links via requests/Playwright"
```

- `--result ok` — you read the page. **An org that publishes no forward schedule is `ok`**, with `--kind no_schedule_published`. That is the org's editorial choice, not a fault of ours, and calling it a failure buries the real ones.
- `--result fail` — you could NOT read the page, or could not parse what you did read. Kinds: `unreachable`, `blocked`, `unparseable`, `stale_url`, `no_dates_found`, `other`.

`org_health.py` keeps consecutive-failure counts and classifies each org:

| Status | Meaning |
|---|---|
| `ok` | Last attempt succeeded |
| `degraded` | 1–2 consecutive failures — often transient |
| `broken` | 3+ consecutive failures — needs a human |
| `stale` | No *successful* scan in 28+ days, even if not currently failing |

Use `python org_health.py mute --ods X --until YYYY-MM-DD` for a known, accepted outage so it stops crowding the report — but mute deliberately, never to make a number look better.

**Why this exists.** Failures used to be appended to a `_scan_errors` list in `state/meetings.json`. That list had no notion of whether a failure had been fixed, no count of how long an org had been broken, and no escalation — a three-month-old breakage looked exactly like a one-off blip. It also quietly stopped being written: its last entry was 2026-08-06, while later runs hit real failures (RXA 403, RTE DNS) and recorded nothing at all. Alder Hey served 2018 content for two months before anyone noticed. Cheshire and Wirral had failed on three separate runs across ten weeks with no one told.

### Step 13 — Report to the operator (chat AND email)

There are two audiences and they need different things. **Correspondents** get dates and packs for their own patch — that is Steps 9/10. **The person who ran the sweep** — Henry or Dave — is the only one who can fix a broken scraper, and until now got nothing but a chat message that scrolled away. This step fixes that.

**Identify the operator** in this order:

1. `--operator NAME` if given
2. `git config user.email`, mapped through `_operator_git_identities` in `data/correspondents.json`
3. Otherwise **ask the user** — do not guess

Then look the name up in `operators` in the same file. **`Dave` is currently `null` — his address has not been confirmed.** If the operator resolves to a name with no address, say so plainly in the chat summary and ask for it once; do not invent one, and do not silently skip the run report. Everything else about the sweep proceeds normally — a missing operator address blocks only the report email, never the correspondent alerts.

Capture a `RUN_START` ISO timestamp at the beginning of the sweep and pass it to the health report so orgs that were **never attempted** are caught, not just those that failed:

```bash
python org_health.py report --since "$RUN_START"              # chat
python org_health.py report --since "$RUN_START" --markdown   # operator email
```

An org that was silently skipped is exactly as invisible as one that failed, and before this existed neither showed up anywhere.

**A. Always print in chat**, terse:

- Orgs scanned, time taken, arguments used
- New dates detected (org names + dates)
- New packs analysed (org names + tier counts)
- Correspondents alerted — dry-run paths, or confirmation of live send with the ok/total count
- **The scan-health block**, verbatim from `python org_health.py report`

**B. When `--live-emails`, ALSO email the operator a run report.** Subject: `[Board paper machine] Run report — {date} — {N} dates, {M} packs, {K} orgs need attention`. Body:

1. One-paragraph summary of what ran and what went out
2. New dates and analysed packs, by correspondent
3. `python org_health.py report --markdown` output — the broken/degraded/stale tables
4. Anything the run could not resolve and is handing back: unverifiable dates, orgs needing a new `schedule_url`, packs that failed to download

Send it through `send_batch.py` in the same batch as everything else, so a failure to send it is visible in the same results JSON.

**Never let the run finish "clean" while orgs are broken.** If any org is `broken` or `stale`, say so explicitly in the chat summary — as a numbered count in the first three lines, not buried at the end. A sweep that alerted 40 packs and silently failed on 12 orgs is not a successful run, and reporting it as one is how Alder Hey went unnoticed for two months.

## Important behaviours

- **Resilience over completeness.** If 5 orgs out of 233 fail, that's fine — log them and move on.
- **Never delete `state/meetings.json` entries.** Even past meetings stay (audit trail).
- **A withdrawn meeting is an alert, not just a state change.** If you mark a meeting `cancelled` or `retracted` and its date alert already went out, you owe the correspondent a withdrawal (Step 8b). Quietly fixing state leaves a meeting in their calendar that will not happen, and they will plan around it — this went unnoticed for months and reached 19 live stale entries before anyone spotted it. The same applies whenever the anti-fabrication guard drops a date that a previous run already alerted.
- **Be careful with UK dates.** `12/06/2026` is 12 June, not 6 December.
- **Never fabricate dates.** Only record meeting dates that appear as literal text in the fetched page (see the anti-fabrication guard in Step 4). The date extractor can hallucinate a plausible schedule; do not extrapolate cadence, complete patterns, or invent next-year dates. A dropped-but-real date is recoverable next run; a fabricated date emailed to a correspondent is not.
- **Never silently drop what IS on the page (anti-omission).** The WebFetch/Playwright summariser omits real dates and PDF links on cluttered or non-chronological tables, and unlike a fabrication this leaves no trace. Always reconcile against the deterministic `extract_board_html.py` in Step 4 (dates) and Step 7 (pack links) before concluding "no meetings" or "no papers yet". This is what caused the Leeds Community 23 July pack to be missed. The cross-check only ever adds dropped items back — it never removes a WebFetch find, so it is safe to run everywhere.
- **De-duplicate cluster meetings.** Hull + NLAG share a board; some ICBs share via `cluster_id`. Don't send the same alert twice.
- **Honour the `notes` field.** If `notes` says "needs Playwright" or "papers on archive subpage" or "PDF schedule", read it and skip cheaper fetchers that have already failed. Don't burn budget re-discovering known failures.
- **The org record is the source of truth for URLs, not the meeting.** A meeting's `source_url` records where a date was found at the time; the org's `url` / `papers_url` are the maintained fields that previous runs correct. Always prefer the org record (see Step 7.1). Scanning a stale `source_url` re-breaks orgs that were already fixed and hides the fix — it cost a wasted "needs a corrected URL" report on Alder Hey on 2026-08-06.
- **Trust `cluster_id`.** Trust and ICB records can both carry `cluster_id` (e.g. `NWUHG`, `DLN`, `STW-SSOT`). When set, all members share the same `url` and meeting dates. Dedupe at the email/subscription layer, but keep one state entry per ods_code for audit.
- **Self-improving.** If you discover an org's `url` has moved, update it. If you discover a quirk worth recording, write to `notes`. **If you discover the dates live on a different page from `url`, set `schedule_url`** — a note alone does not change what the next run reads.
- **Verify old dates, not just new ones.** Step 5b re-checks a rolling slice of what is already in state. Every anti-fabrication guard fires only at first detection, so without this a date that was wrong on the day it was recorded stays wrong, keeps being emailed, and lives in someone's calendar indefinitely. A 2026-08-17 audit found 76 such dates, 56 already sent.
- **A date the page does not mention is not automatically wrong.** Distinguish "the org publishes a schedule and this date is not in it" (an error) from "the org publishes no forward schedule at all" (unverifiable, and common). Only the first justifies a retraction.
- **Editorial caution.** This tool produces *leads*, not facts. Phrasing in alerts must not assert anything beyond what the source page or pack literally says — see `context/hsj_editorial_context.md` for the full rules.
- **One commit per scan.** Don't make multiple commits for a single run; aggregate all state changes into one.
- **A failure must never be able to vanish.** Record an outcome for EVERY org in `org_health.py` (Step 12b), success or failure, and surface the broken/degraded/stale counts in the first three lines of the chat summary. An org that cannot be read contributes nothing and nobody finds out unless the run says so. Alder Hey served 2018 content for two months, and Cheshire and Wirral failed on three runs across ten weeks, before either was noticed.
- **Report to the operator, not just the correspondents.** Correspondents get their own patch; only the person running the sweep can fix a broken scraper. With `--live-emails` they get a run report by email (Step 13B) as well as the chat summary. Resolve who they are from `--operator` or `git config user.email` — and if you cannot, ask before sending anything live.
- **'Publishes no forward schedule' is not a failure.** Record it as `ok --kind no_schedule_published`. Counting it as a failure buries the orgs that are genuinely broken. Those orgs belong on the papers watchlist instead (Step 7b).
- **Never run on unsynced state.** See Step 1 — a `git status` "up to date" is meaningless without a fresh `git fetch`. If you can't confirm the local repo is level with `origin/main`, STOP; don't scan or send. Stale state = duplicate alerts to the whole team. Also re-fetch and drop already-alerted meetings immediately before a live send (Step 11 pre-send guard).
- **UTF-8 everywhere (Windows/PowerShell gotcha that garbled a live send on 2026-07-30).** Board packs are full of `£` and `—`. Any file the emailer reads — the summary being inlined, the composed body, the manifest — MUST be read and written as UTF-8. On PowerShell 5.1, `Get-Content`/`Set-Content` default to the ANSI code page (Windows-1252), not UTF-8: `Get-Content summary.md` reads a UTF-8 `£` as `Â£`, and `Set-Content -Encoding utf8` writes a BOM that breaks `json.loads` and Outlook `.ics` parsing. Always use `Get-Content -Encoding utf8` (or `[System.IO.File]::ReadAllText`) to read, and write with a **no-BOM** UTF-8 encoder (`New-Object System.Text.UTF8Encoding($false)` via `[System.IO.File]::WriteAllText`). `send_email.py`/`send_batch.py` themselves read `body_file` as UTF-8 and set the MIME charset correctly — the danger is only in how the calling steps build those files.

## What still isn't built

- An "already covered" check that queries the HSJ CMS API (Webvision Cloud) before flagging a lead, to suppress alerts about stories HSJ has already published in the last 14 days. The token is in `.env.local` as `HSJ_API_TOKEN`. Add when needed.

## Output style

Keep chat output terse. The user wants:

- Confirmation of what you did.
- A list of new meetings + analysed packs.
- Any failures.
- Pointer to dry-run files OR confirmation of live send.

Don't paraphrase email bodies back into chat — just point at the file paths.

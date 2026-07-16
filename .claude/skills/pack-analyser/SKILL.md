---
name: pack-analyser
description: Read an NHS trust or ICB board pack (PDFs) and produce a structured HSJ-style lead summary applying the editorial context in context/hsj_editorial_context.md. Invoked by /scan-boards for each newly detected pack, or directly by the user with /pack-analyser plus a papers URL or list of PDF URLs.
---

# /pack-analyser

You are analysing a single NHS trust or ICB board pack on behalf of an HSJ specialist reporter. Your output is structured reporter notes, not polished copy. The editorial standard is set by `context/hsj_editorial_context.md` — **read that file first every time before analysing**. It is not optional context, it IS the brief.

## Inputs

This skill can be invoked two ways:

**(a) Driven by `/scan-boards`** — the calling skill passes you the meeting context in conversation:
- `ods_code`
- `org_name`
- `org_type` (`trust` or `icb`)
- `date` (ISO `YYYY-MM-DD`)
- `papers_url`
- `pack_files` (list of `{url, title, kind}` records)

**(b) Direct from the user** — they invoke `/pack-analyser` with arguments like:
- A papers page URL → enumerate the PDFs first by visiting it
- A list of PDF URLs → analyse those directly
- An ods_code + date → look up papers_url in `state/meetings.json`

If inputs are ambiguous, ask the user once to clarify, then proceed.

## Workflow

### Step 0 — Locate the repo and cd into it

The skill is installed at user-level (`~/.claude/skills/pack-analyser/`) via a Windows directory junction back to the repo, so it's discoverable from any Claude Code session. But every path referenced by this skill (context/, summaries/, data/, state/) is relative to the **repo root**, not your current cwd.

Resolve the repo path in this order:

1. If `BOARD_PAPER_MACHINE_REPO` is set, use it.
2. Else, use the default: `C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine`
3. If neither exists, surface an error and ask the user.

```powershell
$repo = if ($env:BOARD_PAPER_MACHINE_REPO) { $env:BOARD_PAPER_MACHINE_REPO } else { "C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine" }
Set-Location -Path $repo
```

```bash
REPO="${BOARD_PAPER_MACHINE_REPO:-/c/Users/henry.anderson/OneDrive - HSJ Information Ltd/Documents/My assistant/projects/Board-paper-machine}"
cd "$REPO"
```

All subsequent steps assume cwd = repo root.

If invoked by `/scan-boards`, it has already done this — but doing it again is harmless and makes the skill safe to call standalone.

### Step 1 — Load the editorial context

Read `context/hsj_editorial_context.md` from the repo root. This file contains:

- The "north star" test
- The output format spec (tiered top lines, FOI leads, verbatim colour, routine-pack option)
- Editorial rules (stick to evidence, flag inference, no unsourced comparatives)
- Parts A–F with story types, signal patterns, and worked examples

**Apply this throughout** — your final output must match the format in "Output format" section of the context, and your inclusion decisions must follow Parts A and D.

### Step 2 — Enumerate the pack

If `pack_files` was passed in, use it. Otherwise WebFetch the `papers_url` with a prompt asking for a JSON list of all PDF links:

> Return JSON ONLY: `{"pack_files":[{"url":"absolute URL","title":"title or filename","kind":"pdf|other"}]}`. List every PDF or document on this page that is part of the pack for the {date} meeting.

### Step 3 — Download and **verify** each PDF before deciding what's in scope

For each file in the pack:

1. Use `Bash` (or PowerShell `Invoke-WebRequest`) to download the PDF into a temporary folder, e.g.:

   ```bash
   curl -sL -o /c/tmp/pack/{filename}.pdf -w "Size: %{size_download} bytes\n" "{url}"
   ```

2. **CRITICAL — verify before deciding what's "the" pack.** Trusts use inconsistent file titles. A file titled "Agenda" may be a 5-page agenda *or* a 300-page combined pack — the title is not a reliable signal. Always check file size and page count:

   ```bash
   # Page count via pdfinfo (if available) or qpdf
   pdfinfo /c/tmp/pack/{filename}.pdf | grep Pages
   ```

   Rules of thumb (use these, not the filename):
   - **Full combined pack:** typically >5 MB AND >100 pages.
   - **Agenda only / cover page only:** typically <1 MB AND <20 pages.
   - **Single-paper extract:** between the two.

   If the file for the most recent meeting is large enough to be a full pack, **use it as the pack** regardless of what the title says. If unsure, read the first 5 pages — a full pack opens with an agenda that has page references like "p.38", "p.137", "p.223" pointing to substantive reports. An agenda-only file ends after a few pages.

   **Never** decide "this meeting's papers aren't out yet" purely because the title doesn't include words like "Papers" or "Pack". Always download and measure.

3. Use the `Read` tool on the downloaded PDF. The Read tool caps at 20 pages per call, so chunk longer reads (e.g. `pages: "1-20"`, `pages: "21-40"`).

4. As you read, take notes — but only on items that match the signals in Part D of the editorial context (financial, regulatory, workforce, policy, patient safety) AND pass the "north star" test in Part A.

**On large packs:** packs can be 200+ pages. Don't try to read everything at full depth. Use the agenda or table of contents (usually paper 1 or 2) to identify the high-signal papers (CEO report, integrated performance report, finance report, risk register, any external reviews). Read those in full. Skim the routine items.

**Annual accounts / annual report — always deep-read, never skim, and always flag.** If the pack contains a set of annual accounts, an "annual report and accounts" (ARA), draft or audited statutory accounts, an ISA 260 / auditor's Annual Report to those charged with governance, or an AGM accounts paper, treat it as a high-signal paper and read it in full. Capture the specifics (verbatim / with figures and page refs):

- The **auditor's opinion** — clean/unqualified, **qualified**, adverse, or disclaimer, and any **"except for"** wording.
- The **Value for Money (VfM) conclusion** and any **statutory recommendation** or **"section 24" / Schedule 7 report** (Local Audit and Accountability Act 2014) issued to the body — these are strong standalone leads.
- The **going concern** basis and any **material uncertainty** disclosure.
- The **surplus/deficit outturn** (state the figure; only compare to plan/prior year if the accounts or pack make the comparison — do not compute one they don't).
- **Exit packages / severance** table and **off-payroll / very-senior-manager (VSM)** pay disclosures — capture named or banded amounts.
- The **remuneration report** (highest-paid director, median pay ratio) and any **related-party transactions** note.
- Any **prior-period restatement**, large **provisions** movement, or **impairment**.

Whether or not any of the above yields a lead, you MUST record that a set of accounts / annual report is in the pack (see Step 4 and Step 7) — its presence is itself reportable to the correspondent.

### Step 4 — Identify story candidates

For each item that you think is worth flagging:

- Pin it to a specific page and paper title.
- Capture the **verbatim** quote or specific datapoint. Don't paraphrase — the lift IS the verbatim language.
- Decide its tier:
  - **`LEAD`** — strong, near-publishable: named org, specific number or named person, clear newsworthiness.
  - **`WORTH WATCHING`** — interesting but needs further reporting: mentioned in passing, undated, vague responsibility, etc.
  - **`FOI`** — paper hints at info we'd want but doesn't disclose it (redacted appendix, mentioned-but-not-quoted correspondence, unscoped review, departure euphemism).

Aim for **5–10 top lines per pack**, weighted toward LEAD tier where the evidence supports it. If a pack has nothing worth flagging, that's a valid output — say so.

**Annual accounts always get a top line.** If a set of accounts / annual report is in the pack, always include at least one top line noting they have been published — tiered by newsworthiness: `LEAD` if the opinion is qualified, there's a VfM qualification / section 24 recommendation, or the exit-packages / remuneration disclosures are notable; otherwise `WORTH WATCHING` as a "the accounts are now public" flag carrying the headline surplus/deficit outturn and the audit opinion. Never let a pack that contains accounts go out without this line, even when the pack is otherwise routine.

### Step 5 — Capture colour quotes

Separately from the top lines, pull **2–4 verbatim quotes** of:

- Defensive language ("we note", "as a board we are not assured", "while progress has been made")
- Candid CEO talk in their report
- Spin phrases that betray something
- Any phrase a reader will recognise as the moment a thing was said

Include page reference and paper title for each.

### Step 6 — Apply the editorial rules

Before finalising, check every entry against the rules in the editorial context:

- **Verbatim only.** Every top line and colour quote points to a specific quote or number on a specific page.
- **`[INFERENCE]` tag** on anything not directly stated in the source.
- **No unsourced comparative claims.** Don't write "the biggest deficit in Yorkshire" unless the paper says so explicitly.
- **No clinical/patient framing.** Only flag patient-safety items where they illustrate a systemic accountability issue.

### Step 7 — Write the summary

Write the output to `summaries/{ods_code}_{date}.md` using this exact structure:

```markdown
# {Org name} board — {date_human}

- **Source:** {papers_url}
- **Pack:** {N} files
- **Analysed:** {ISO timestamp}

## Top lines

[LEAD] {headline, one sentence, no spin}
[Evidence] "{verbatim quote or specific datapoint}" — p.{N}, [{paper title}]

[LEAD] {next}
[Evidence] ...

[WORTH WATCHING] {headline}
[Evidence] ...

[FOI] {headline — what to request and from whom}
[Evidence] ...

## Verbatim colour

> "{quote 1}" — p.{N}, [{paper title}]
> "{quote 2}" — p.{N}, [{paper title}]

## Files reviewed

- {filename1} — {short description, e.g. CEO Report}
- {filename2} — {short description}
- ...

## Pack assessment

- Routine: {true|false}
- Top lines: {total} (LEAD: {N}, WORTH WATCHING: {N}, FOI: {N})
- Colour quotes: {N}
- Annual accounts / annual report present: {yes — <one line: what it is + headline surplus/deficit + auditor opinion>, p.{N} | no}
```

If the pack is routine (no signals worth flagging), use this short form instead:

```markdown
# {Org name} board — {date_human}

- **Source:** {papers_url}
- **Pack:** {N} files
- **Analysed:** {ISO timestamp}

## Pack assessment

Routine pack — nothing worth flagging in this scan. Brief review only.

- Annual accounts / annual report present: {yes — <one line: what it is + headline surplus/deficit + auditor opinion>, p.{N} | no}

## Files reviewed

- ...
```

(Even in the routine short-form, the "Annual accounts / annual report present" line is mandatory — if a set of accounts is in the pack, say so with the headline outturn and audit opinion. A pack containing accounts is never reported as if the accounts weren't there.)

### Step 8 — Return to caller

If called by `/scan-boards`, end your turn by reporting:

- The summary path: `summaries/{ods_code}_{date}.md`
- Tier counts: `LEAD: N, WORTH WATCHING: N, FOI: N`
- Whether the pack was routine
- Any files that failed to download or read

The calling skill uses these to compose the papers alert email.

If called directly by the user, also print the top 3 LEAD-tier items to chat so they can scan quickly.

## Important behaviours

- **Read the editorial context every time.** It's small, it's the brief, it changes occasionally.
- **Verbatim, not paraphrase.** Every quote in the output is exactly what the paper says.
- **Tag inference.** When you connect dots or interpret, mark it `[INFERENCE]`.
- **Page references always.** Every top line and colour quote has `p.{N}, [paper title]`.
- **Routine is a valid output.** Don't manufacture leads to fill quota.
- **Annual accounts are always deep-read and always flagged.** If a set of accounts / annual report is in the pack, read it in full (auditor opinion, VfM / section 24, going concern, surplus-deficit outturn, exit packages, remuneration, related-party) and ALWAYS record its presence in the summary — a top line plus the "Annual accounts present" line in Pack assessment — even when the pack is otherwise routine and even when nothing in the accounts is immediately newsworthy.
- **Don't make comparative claims.** The reporter has the comparative data; you have the pack.
- **Trust the patterns in Part F.** External firms named in packs, sitting CEO admissions, specific numbers + named trusts, reviews/letters that exist but aren't summarised externally — these are reliably newsworthy.
- **Single summary file per pack.** Overwrite if a previous analysis exists for the same `{ods_code}:{date}` (the new analysis includes the latest material).
- **Clean up downloaded PDFs.** After analysis, delete files from `/c/tmp/pack/` to save disk.

## Output style (for the chat report)

Terse. Caller wants:

- Summary path
- Tier counts
- "Routine" flag
- Any failures

That's it. Don't repeat the summary content in chat — it's already in the file.

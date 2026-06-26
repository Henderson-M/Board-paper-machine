#!/usr/bin/env python3
"""
send_batch.py — send a batch of board-paper-machine alerts with a randomised
                delay between each one, so a full sweep doesn't go out as a
                40-message blast that mail gateways quarantine as spam.

Wraps send_email.py's message-building + Gmail SMTP send. Reconnects per email
(rather than holding one connection open for the whole, possibly 40-minute,
run) which is both robust against idle-timeout and gentler on the gateway.

Reads a MANIFEST: a JSON array of objects, each with at least:
    {"to": "...", "subject": "...", "body_file": "path", "attach": ["path", ...]}
Extra keys (kind, corr, id, ...) are ignored, so the manifests the
/scan-boards skill already builds can be passed straight in.

Usage:
    python send_batch.py --manifest emails.json
    python send_batch.py --manifest emails.json --min-gap 30 --max-gap 60
    python send_batch.py --manifest a.json --manifest b.json --results out.json
    python send_batch.py --manifest emails.json --dry-run     # no SMTP, no sleeps

Default gap is 30–60s (randomised per email, with the wait skipped after the
last message). The first email goes out immediately.

Writes a results JSON (--results, default send_results.json next to the first
manifest) listing per-email {to, subject, id, ok, err} so the caller can stamp
alerts_sent ONLY for messages that actually sent (exit 0), per the skill.

Exit code: 0 if every email sent, 1 if any failed (the rest are still attempted).
"""

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# Reuse the single source of truth for message construction + SMTP + creds.
from send_email import build_message, load_env, send_via_gmail, ENV_LOCAL, DEFAULT_FROM_NAME


def main():
    ap = argparse.ArgumentParser(description="Send a batch of alerts with staggered timing")
    ap.add_argument("--manifest", action="append", required=True,
                    help="Path to a manifest JSON array. Repeatable; manifests are concatenated in order.")
    ap.add_argument("--min-gap", type=float, default=30.0, help="Minimum seconds between sends (default 30)")
    ap.add_argument("--max-gap", type=float, default=60.0, help="Maximum seconds between sends (default 60)")
    ap.add_argument("--results", help="Where to write the per-email results JSON (default: send_results.json beside the first manifest)")
    ap.add_argument("--from-name", default=DEFAULT_FROM_NAME, help="Display name for From: header")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan; don't connect to SMTP and don't sleep")
    ap.add_argument("--env-file", default=str(ENV_LOCAL), help="Path to .env.local")
    args = ap.parse_args()

    if args.min_gap > args.max_gap:
        args.min_gap, args.max_gap = args.max_gap, args.min_gap

    emails = []
    for mpath in args.manifest:
        items = json.loads(Path(mpath).read_text(encoding="utf-8"))
        if not isinstance(items, list):
            print(f"ERROR: manifest {mpath} is not a JSON array", file=sys.stderr)
            return 2
        emails.extend(items)

    if not emails:
        print("Nothing to send (manifest empty).")
        return 0

    env = load_env(Path(args.env_file))
    user = env.get("GMAIL_USER") or os.environ.get("GMAIL_USER")
    password = env.get("GMAIL_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")
    if not args.dry_run and (not user or not password):
        print("ERROR: GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env.local or environment.", file=sys.stderr)
        return 2
    from_addr = user or "hsjboardpapers@gmail.com"

    results = []
    n = len(emails)
    n_ok = 0
    print(f"Staggered send: {n} email(s), gap {args.min_gap:.0f}-{args.max_gap:.0f}s"
          f"{' (DRY RUN)' if args.dry_run else ''}")
    for i, e in enumerate(emails):
        to = e["to"]; subject = e["subject"]
        body = Path(e["body_file"]).read_text(encoding="utf-8")
        attach = e.get("attach") or []
        rec = {"to": to, "subject": subject, "id": e.get("id") or e.get("corr"), "ok": False, "err": ""}
        if args.dry_run:
            print(f"  [{i+1}/{n}] DRY would send -> {to} | {subject[:60]} | attach={len(attach)}")
            rec["ok"] = True
        else:
            try:
                msg = build_message(from_name=args.from_name, from_addr=from_addr, to=to,
                                    subject=subject, body=body, attachments=attach)
                send_via_gmail(msg, user=user, password=password)
                rec["ok"] = True
                print(f"  [{i+1}/{n}] sent -> {to} | {subject[:60]}")
            except Exception as ex:  # keep going; one bad send must not abort the batch
                rec["err"] = repr(ex)[:300]
                print(f"  [{i+1}/{n}] FAILED -> {to} | {subject[:60]} | {rec['err']}", file=sys.stderr)
        if rec["ok"]:
            n_ok += 1
        results.append(rec)
        # stagger: wait before the NEXT email (skip after the last, and in dry-run)
        if not args.dry_run and i < n - 1:
            gap = random.uniform(args.min_gap, args.max_gap)
            print(f"      … waiting {gap:.0f}s")
            time.sleep(gap)

    out = args.results or str(Path(args.manifest[0]).with_name("send_results.json"))
    Path(out).write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nSent {n_ok}/{n}. Results -> {out}")
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    sys.exit(main())

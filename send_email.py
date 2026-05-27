#!/usr/bin/env python3
"""
send_email.py — send a board-paper-machine alert via Gmail SMTP with optional
                .ics calendar attachments.

Called by the /scan-boards skill when --live-emails is passed.
Reads credentials from .env.local at the repo root (gitignored).

Usage:
    python send_email.py \\
        --to henry.anderson@hsj.co.uk \\
        --subject "[Board paper machine] 3 new meeting date(s)" \\
        --body-file path/to/email.md \\
        --attach ics/RAE_2026-07-30.ics ics/RAE_2026-09-24.ics

Dry-run (prints the message, does not connect to SMTP):
    python send_email.py --to ... --subject ... --body-file ... --dry-run
"""

import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ENV_LOCAL = REPO_ROOT / ".env.local"
DEFAULT_FROM_NAME = "Board paper machine"


def load_env(path):
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def build_message(*, from_name, from_addr, to, subject, body, attachments):
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    for att_path in attachments:
        p = Path(att_path)
        if not p.exists():
            print(f"WARNING: attachment not found, skipping: {p}", file=sys.stderr)
            continue
        data = p.read_bytes()
        if p.suffix.lower() == ".ics":
            # Outlook recognises text/calendar with method=PUBLISH for one-click add
            msg.add_attachment(
                data,
                maintype="text",
                subtype="calendar",
                params={"method": "PUBLISH", "name": p.name},
                filename=p.name,
            )
        elif p.suffix.lower() == ".pdf":
            msg.add_attachment(data, maintype="application", subtype="pdf", filename=p.name)
        else:
            msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=p.name)
    return msg


def send_via_gmail(msg, *, user, password):
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)


def main():
    ap = argparse.ArgumentParser(description="Send a board paper machine alert email")
    ap.add_argument("--to", required=True, help="Recipient email address")
    ap.add_argument("--subject", required=True, help="Email subject")
    ap.add_argument("--body-file", help="Path to plain-text/markdown body. If omitted, reads stdin.")
    ap.add_argument("--attach", nargs="*", default=[], help=".ics or other files to attach")
    ap.add_argument("--from-name", default=DEFAULT_FROM_NAME, help="Display name for From: header")
    ap.add_argument("--dry-run", action="store_true", help="Print the message instead of sending")
    ap.add_argument("--env-file", default=str(ENV_LOCAL), help="Path to .env.local")
    args = ap.parse_args()

    env = load_env(Path(args.env_file))
    user = env.get("GMAIL_USER") or os.environ.get("GMAIL_USER")
    password = env.get("GMAIL_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")
    if not args.dry_run and (not user or not password):
        print("ERROR: GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env.local or environment.", file=sys.stderr)
        return 2

    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else sys.stdin.read()

    # In dry-run mode the from_addr might be missing; fall back to a placeholder
    from_addr = user or "hsjboardpapers@gmail.com"

    msg = build_message(
        from_name=args.from_name,
        from_addr=from_addr,
        to=args.to,
        subject=args.subject,
        body=body,
        attachments=args.attach,
    )

    if args.dry_run:
        print("=== DRY RUN — would send ===")
        print(f"From:    {msg['From']}")
        print(f"To:      {msg['To']}")
        print(f"Subject: {msg['Subject']}")
        attached = [p.get_filename() for p in msg.iter_attachments()]
        print(f"Attachments ({len(attached)}): {attached}")
        print("--- body ---")
        print(body)
        return 0

    try:
        send_via_gmail(msg, user=user, password=password)
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP send failed: {e}", file=sys.stderr)
        return 1

    print(f"Sent: to={args.to} subject={args.subject!r} attachments={len(args.attach)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

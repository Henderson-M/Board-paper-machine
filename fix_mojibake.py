#!/usr/bin/env python3
"""Repair double/triple-encoded UTF-8 ("mojibake") in the repo's JSON state.

The bug it cleans up
--------------------
PowerShell 5.1 reads and writes files in the Windows-1252 ANSI code page unless
told otherwise. When a step of a run read a UTF-8 file with `Get-Content` and
wrote it back, every non-ASCII character was re-encoded one level deeper:

    —  ->  â€"  ->  ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â  (an em dash, mangled twice over)

`state/meetings.json` carries these in `notes` and `title` fields. They are not
cosmetic: notes are read by later runs and pasted into alert emails, so a
mangled note reaches a correspondent's inbox.

The skill's UTF-8 rule (see "Important behaviours") stops NEW ones appearing.
This repairs the ones already in state.

How it decides
--------------
A string is repaired only when EVERY step holds:

  1. It contains a mojibake marker (Ã, Â, â‚¬, â€ ...). Clean strings are
     never touched.
  2. Re-encoding it byte-for-byte yields valid UTF-8 that differs from the input.
  3. The result has strictly fewer mojibake markers than the input.
  4. The result introduces no replacement chars (\\ufffd) or new control chars.

If any check fails the original is kept. A string this cannot confidently fix is
left alone and listed, rather than guessed at.

Usage
-----
    python fix_mojibake.py                    # dry run, shows what it would change
    python fix_mojibake.py --write            # apply
    python fix_mojibake.py --write --path state/org_health.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

DEFAULT_PATHS = [
    "state/meetings.json",
    "state/org_health.json",
    "state/papers_watchlist.json",
    "data/trust_urls.json",
    "data/icb_urls.json",
]

# The tell-tale sequences left behind when UTF-8 bytes are read as Windows-1252.
_MARKER = re.compile(r"[ÃÂ]["
                     r"-¿ƒ†…‰‹›"
                     r"€‚„‘’“”•–—"
                     r"]"
                     r"|â€|â‚¬|Ã¢|Â ")

MAX_ROUNDS = 4


def _detect_indent(raw: str, default: int = 1) -> int:
    """Match the file's existing indent so the diff shows only the repaired strings.

    These state files are written with indent=1. Re-dumping at a different width
    rewrites every line, which buries a 43-string fix in a 40,000-line diff and
    makes it unreviewable — and unreviewable is how a bad state write gets pushed.
    """
    for line in raw.split("\n")[1:4]:
        stripped = line.lstrip(" ")
        if stripped and stripped[0] in "\"'{[}]":
            return len(line) - len(stripped) or default
    return default


def _markers(s: str) -> int:
    return len(_MARKER.findall(s))


def _to_bytes(s: str) -> bytes | None:
    """Reverse a cp1252 mis-decode, falling back to latin-1 for cp1252's holes.

    cp1252 leaves 0x81/0x8d/0x8f/0x90/0x9d undefined, and mangled text routinely
    contains exactly those, so a plain `.encode('cp1252')` throws on the very
    strings we are trying to fix.
    """
    out = bytearray()
    for ch in s:
        try:
            out += ch.encode("cp1252")
        except UnicodeEncodeError:
            o = ord(ch)
            if o < 256:
                out.append(o)
            else:
                return None
    return bytes(out)


def repair(s: str) -> str:
    """Best-effort un-mangle. Returns the input unchanged if unsure."""
    if not isinstance(s, str) or not _MARKER.search(s):
        return s

    cur = s
    for _ in range(MAX_ROUNDS):
        b = _to_bytes(cur)
        if b is None:
            break
        try:
            nxt = b.decode("utf-8")
        except UnicodeDecodeError:
            break
        if nxt == cur:
            break
        cur = nxt

    if cur == s:
        return s
    # Only accept a strict improvement that introduced nothing nasty.
    if _markers(cur) >= _markers(s):
        return s
    if "�" in cur:
        return s
    if any(ord(c) < 32 and c not in "\t\n\r" for c in cur):
        return s
    return cur


def walk(node, path="", changes=None):
    """Repair strings in place throughout a nested structure."""
    if changes is None:
        changes = []
    if isinstance(node, dict):
        for k, v in node.items():
            node[k] = walk(v, f"{path}.{k}" if path else k, changes)[0]
        return node, changes
    if isinstance(node, list):
        for i, v in enumerate(node):
            node[i] = walk(v, f"{path}[{i}]", changes)[0]
        return node, changes
    if isinstance(node, str):
        fixed = repair(node)
        if fixed != node:
            changes.append((path, node, fixed))
        return fixed, changes
    return node, changes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="Apply the fixes (default: dry run)")
    ap.add_argument("--path", action="append", help="File(s) to process; repeatable")
    ap.add_argument("--show", type=int, default=20, help="How many examples to print")
    args = ap.parse_args()

    paths = args.path or DEFAULT_PATHS
    total = 0
    unfixed_files = []

    for rel in paths:
        fp = REPO / rel
        if not fp.exists():
            print(f"skip (absent): {rel}")
            continue

        raw = fp.read_text(encoding="utf-8")
        data = json.loads(raw)
        indent = _detect_indent(raw)
        data, changes = walk(data)

        # Anything still carrying a marker after the pass: report, never guess.
        leftover = len(_MARKER.findall(json.dumps(data, ensure_ascii=False)))

        print(f"\n{rel}: {len(changes)} string(s) repaired"
              + (f", {leftover} marker(s) still unresolved" if leftover else ""))
        for p, before, after in changes[:args.show]:
            print(f"  {p}")
            print(f"    - {before[:110]}")
            print(f"    + {after[:110]}")
        if len(changes) > args.show:
            print(f"  ... and {len(changes) - args.show} more")

        total += len(changes)
        if leftover:
            unfixed_files.append(rel)

        if args.write and changes:
            # Write UTF-8 with no BOM and a trailing newline, matching the repo's
            # existing files — a BOM here breaks json.loads on the next run.
            fp.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n",
                          encoding="utf-8")

    print(f"\n{'APPLIED' if args.write else 'DRY RUN'}: {total} string(s)")
    if not args.write and total:
        print("re-run with --write to apply")
    if unfixed_files:
        print(f"still carrying markers (inspect by hand): {', '.join(unfixed_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

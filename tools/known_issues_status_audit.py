#!/usr/bin/env python3
"""Audit docs/KNOWN_ISSUES.md for entries marked OPEN whose described fix may
already exist in the codebase -- the "fix shipped but entry never updated" gap.

WHY THIS EXISTS (real incident, 2026-09-10): F43 documented that
blackout_conflict/recent_send_conflict were pure self-attestation with no
mechanical check. The real fix shipped 2026-08-19 (tools/conflict_check.py,
wired into the validator with three fail-closed paths and 36 tests). F43's
Status line still read "OPEN -- findings record only, no fix written" 22 days
later. It was found only because an assumption about the repo's state was
deliberately re-verified rather than carried forward. Nothing in the pipeline
couples "fix shipped" to "entry updated", so nothing would have caught it.

WHY THIS IS A REPORT, NOT A VALIDATOR GATE -- deliberate, not a shortcut:
KNOWN_ISSUES.md carries 66 entries whose Status lines are freeform prose
("OPEN", "OPEN (design question) / MECHANICAL RISK CLOSED", "Logged only",
"FIXED same night", "Informational scope note, not a bug", and many more).
Any automated attempt to decide whether such an entry is "really" still open
would produce false positives at a rate that trains people to ignore it --
the exact failure this repo has repeatedly documented about checks nobody
trusts. Instead this surfaces CANDIDATES for a human to judge, and says
plainly that a hit is not evidence of staleness by itself.

Usage:
    python3 tools/known_issues_status_audit.py [--tree PATH] [--verbose]

Exit codes:
    0  always (this is a report; it never blocks anything)
"""

from __future__ import annotations

import argparse
import os
import re
import sys

_REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# An entry is a CANDIDATE for review when its status looks unresolved. These
# are matched case-insensitively against the status line only.
_OPEN_MARKERS = ("open", "logged only", "not fixed", "no fix written",
                 "findings record only", "documented, not fixed")

# ...unless the status ALSO carries an explicit resolution marker, which is
# common in this file (e.g. "OPEN (design question) / MECHANICAL RISK CLOSED").
# Those are deliberate mixed states, not staleness.
_RESOLVED_MARKERS = ("resolved", "fixed", "closed", "superseded")

# Code-reference shapes that appear in entry bodies. A hit means the entry
# names a concrete artifact whose existence can be checked directly.
_CODE_REF_RE = re.compile(
    r"`(tools/[\w./]+\.py|validators/[\w./]+\.py|[\w]+\.py)`"
    r"|`([a-z_]+\(\))`"
)


def _split_entries(text: str) -> list[tuple[str, str]]:
    """Return [(heading, body), ...] for each '## F<n>: ...' entry."""
    parts = re.split(r"^(## F\d+[^\n]*)$", text, flags=re.MULTILINE)
    entries = []
    for i in range(1, len(parts), 2):
        entries.append((parts[i].strip(), parts[i + 1]))
    return entries


def _status_line(body: str) -> str:
    m = re.search(r"^\*\*Status:\*\*(.+?)(?=\n\n|\n\*\*)", body,
                  flags=re.MULTILINE | re.DOTALL)
    return " ".join(m.group(1).split()) if m else ""


def _looks_open(status: str) -> bool:
    s = status.lower()
    if not any(marker in s for marker in _OPEN_MARKERS):
        return False
    # A status that already names its own resolution is not stale -- it is an
    # honestly-recorded mixed or resolved state.
    return not any(marker in s for marker in _RESOLVED_MARKERS)


def _referenced_artifacts(body: str) -> list[str]:
    found = []
    for m in _CODE_REF_RE.finditer(body):
        ref = m.group(1) or m.group(2)
        if ref and ref not in found:
            found.append(ref)
    return found


def _artifact_exists(ref: str, tree: str) -> bool | None:
    """True if present, False if genuinely absent, None if not checkable."""
    if ref.endswith("()"):
        name = ref[:-2]
        for sub in ("tools", "validators"):
            d = os.path.join(tree, sub)
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                if not fn.endswith(".py"):
                    continue
                try:
                    with open(os.path.join(d, fn), encoding="utf-8") as fh:
                        if re.search(rf"^def {re.escape(name)}\(", fh.read(),
                                     flags=re.MULTILINE):
                            return True
                except OSError:
                    continue
        return False
    if "/" in ref:
        return os.path.isfile(os.path.join(tree, ref))
    return None  # bare filename, too ambiguous to resolve honestly


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree", default=_REPO_ROOT)
    ap.add_argument("--verbose", action="store_true",
                    help="also list open entries with no checkable code reference")
    args = ap.parse_args(argv)

    path = os.path.join(args.tree, "docs", "KNOWN_ISSUES.md")
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        print(f"[ERROR] cannot read {path}: {e}", file=sys.stderr)
        return 0  # still never blocks

    entries = _split_entries(text)
    candidates, unresolvable, open_total = [], [], 0

    for heading, body in entries:
        status = _status_line(body)
        if not _looks_open(status):
            continue
        open_total += 1
        refs = _referenced_artifacts(body)
        present = [r for r in refs if _artifact_exists(r, args.tree) is True]
        if present:
            candidates.append((heading, status, present))
        else:
            unresolvable.append((heading, status))

    print("=" * 72)
    print("KNOWN_ISSUES.md STATUS AUDIT")
    print("=" * 72)
    print(f"Entries scanned:            {len(entries)}")
    print(f"Status reads as unresolved: {open_total}")
    print(f"Naming code that EXISTS:    {len(candidates)}  <- review these")
    print()

    if candidates:
        print("REVIEW CANDIDATES -- an unresolved-looking entry that names code")
        print("already present in the tree. This is NOT proof the entry is stale:")
        print("an entry can legitimately cite existing code while describing a")
        print("real remaining gap in it (F42 and F43 both did, before and after")
        print("their fixes). A human decides; this only narrows where to look.")
        print("-" * 72)
        for heading, status, present in candidates:
            print(f"\n{heading}")
            print(f"  status: {status[:150]}")
            print(f"  names existing: {', '.join(present[:5])}")
    else:
        print("No review candidates -- no unresolved-looking entry names code that")
        print("already exists in the tree.")

    if args.verbose and unresolvable:
        print()
        print("-" * 72)
        print("OPEN, NO CHECKABLE CODE REFERENCE (listed for completeness; this")
        print("tool cannot say anything about these either way):")
        for heading, status in unresolvable:
            print(f"  {heading[:100]}")

    print()
    print("Report only -- exit 0 always, blocks nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

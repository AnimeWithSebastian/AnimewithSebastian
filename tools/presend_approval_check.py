#!/usr/bin/env python3
"""PRE-SEND approval gate (F87 fix, added 2026-09-12).

Runs the exact same Law #173 schema pre-check + core-aware unsupported-claim
gate as tools/append_send_batch.py's STEP 8 log-append check
(tools/approval_gate.check_fetch_review_gate) -- but BEFORE STEP 7 sends any
email, not after. Same gate, moved earlier, per the user's Fix 3 instruction
("Law #173's shape: run the approval.json validation BEFORE the send step,
not at log-append").

WHY A SEPARATE SCRIPT INSTEAD OF JUST MOVING THE CHECK: append_send_batch.py's
gate call happens to have manifest re-validation, --emails-sent bookkeeping,
and state.json writing bolted on around it -- none of that makes sense before
a send has happened (there's no "send" to assert yet, no state to write about
a completed run). This script does exactly one thing: load an approval.json
and report whether its fetch_review would pass the gate, with no other
side effects. It is meant to be run interactively at STEP 6.5, by the person
approving the batch, immediately after approval.json is written and before
STEP 7's send.

THIS DOES NOT REPLACE STEP 8's CHECK. append_send_batch.py keeps calling
check_fetch_review_gate() too, unchanged -- defense in depth. A pre-send
pass here does not guarantee approval.json can't be edited (or a different,
unchecked approval.json substituted) between this check and the actual send;
STEP 8 remains the last-line, authoritative gate that decides whether a send
gets logged as successful. This script only tries to catch the problem at
the point where catching it still matters -- before sending, not just before
logging.

Exit codes: 0 = gate passes (safe to proceed to STEP 7). 1 = gate fails
(fix approval.json before sending -- see AUTHORING CONVENTION below). 2 =
could not even load/parse the approval file (distinct from a real gate
failure, so a missing path isn't mistaken for a content problem).

AUTHORING CONVENTION (the other half of F87 -- the check working correctly
was never the problem; nothing marked genuine negative controls as non-core
at draft time): when writing a fetch_review entry for a claim that is a
NEGATIVE CONTROL (the claim text asks "does any source support the WRONG
framing," where fetched_content_supports_claim=False is the CORRECT,
expected result -- not a failed verification), set "core": false on that
entry explicitly, plus a real, non-empty "note" explaining what the control
checked and why False is the right answer. Do not leave "core" absent and
rely on the default; the default is core=True specifically because an
undisclosed missing marker must fail closed, not pass silently. This is a
drafting-time convention (STEP 6.5's approval.json authoring), not something
this script can infer on its own -- it can only check that whatever a human
already marked is self-consistent (unsupported-and-undisclosed still blocks
even when core=False, unsupported-and-disclosed passes, unsupported-and-
core-true always blocks). It cannot know a control is a control unless it's
told.

Usage:
    python3 tools/presend_approval_check.py <approval.json>
"""

from __future__ import annotations

import json
import sys

from approval_gate import check_fetch_review_gate


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 tools/presend_approval_check.py <approval.json>",
              file=sys.stderr)
        return 2

    approval_path = argv[1]
    try:
        with open(approval_path, encoding="utf-8") as fh:
            approval = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[ERROR] could not load {approval_path!r}: {e}", file=sys.stderr)
        return 2

    if not isinstance(approval, dict):
        print(f"[ERROR] {approval_path!r} did not parse to a JSON object", file=sys.stderr)
        return 2

    fetch_review = approval.get("fetch_review")
    result = check_fetch_review_gate(fetch_review)

    if result.ok:
        n = len(fetch_review) if isinstance(fetch_review, list) else 0
        print(f"[PASS] pre-send check: {n} fetch_review entries clear the "
              f"Law #173/#165 gate. Safe to proceed to STEP 7's send.")
        return 0

    print(f"[BLOCKED] pre-send check failed -- DO NOT SEND: {result.error}",
          file=sys.stderr)
    print("Fix approval.json (see AUTHORING CONVENTION in this script's "
          "docstring for negative-control entries) and re-run this check "
          "before STEP 7.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

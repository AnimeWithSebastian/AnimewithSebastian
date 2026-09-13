#!/usr/bin/env python3
"""Shared Law #165/#173 fetch_review gate (F87 fix, added 2026-09-12).

EXTRACTED FROM tools/append_send_batch.py, NOT REWRITTEN: this module holds
the exact schema pre-check (Law #173) and core-aware unsupported-claim gate
that append_send_batch.py ran at STEP 8 (post-send, log-append time) before
2026-09-12. The logic, the precedence rules, and the error-message wording
are unchanged from that version -- only the location moved, from being
inlined in append_send_batch.py's main() to a standalone, importable
function both a pre-send check and the post-send logger can call.

WHY THIS EXISTS (F87): a recent batch (d0385ca7, source repo, 2026-09-12)
sent an email whose approval.json had 3 fetch_review entries that were
genuine negative controls (claim text asking "does any source support the
WRONG framing," where fetched_content_supports_claim=False is the CORRECT
answer) but carried no "core": false marker at authoring time. The gate
below caught this and worked exactly as designed -- but it only ran at
STEP 8, after STEP 7 had already sent the email. The check was correct; its
position was not. See docs/KNOWN_ISSUES.md F87 for the full incident and the
chosen fix (this module, plus tools/presend_approval_check.py calling it
before STEP 7).

This module has NO side effects: it does not read files, write files, or
call sys.exit. It takes an already-parsed fetch_review list and returns a
result object. Callers (append_send_batch.py's main(), and the new
presend_approval_check.py) are responsible for loading approval.json,
interpreting the result, and doing their own I/O / exit-code handling --
this keeps the gate testable in isolation and usable from two different
call sites without duplicating the checking logic itself.
"""

from __future__ import annotations

import re
from typing import Any

# --- SCHEMA PRE-CHECK (Law #173, added 2026-09-10 -- directly addresses the
# F78 finding, an approval.json built with a "verdict" string field instead
# of the "fetched_content_supports_claim" boolean the logger requires).
_VERDICT_SUBSTITUTE_KEYS = ("verdict", "supported", "confirmed", "status", "result")

# --- CORE-AWARE GATE (2026-08-19, narrow fix for the false-positive block on
# honestly-disclosed non-core claims). See _is_core()'s docstring below for
# the full precedence rule; unchanged from the original inline version.
_NON_CORE_PREFIX_RE = re.compile(r"^\s*\[NON-CORE\b", re.IGNORECASE)


class ApprovalGateResult:
    """Result of check_fetch_review_gate(). `ok` is True iff the fetch_review
    list clears both the Law #173 schema pre-check and the core-aware
    unsupported-claim gate. `error` is None when ok=True, else a
    human-readable message identical in wording to what
    append_send_batch.py has always written to state.json's "error" field
    and printed to stderr -- callers should not need to reformat it."""

    def __init__(self, ok: bool, error: str | None = None):
        self.ok = ok
        self.error = error

    def __repr__(self) -> str:
        return f"ApprovalGateResult(ok={self.ok!r}, error={self.error!r})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ApprovalGateResult)
            and self.ok == other.ok
            and self.error == other.error
        )


def _is_core(entry: dict) -> bool:
    """core/non-core detection precedence (explicit, in order):
      1. A structured "core" key present on the entry (True or False) is
         authoritative. If present, the legacy text-prefix convention below
         is IGNORED for that entry -- the two signals never get a chance to
         silently disagree.
      2. Else, a claim string starting with a case-insensitive, start-
         anchored NON-CORE marker (in square brackets) is treated as
         core=False. This is the LEGACY path: pre-2026-08-19 approval.json
         files encode non-core claims this way.
      3. Else (no structured field, no text-prefix match): default to
         core=True -- the safe, strict default.
    """
    if "core" in entry and entry["core"] is not None:
        return entry["core"] is not False
    claim = entry.get("claim")
    if isinstance(claim, str) and _NON_CORE_PREFIX_RE.match(claim):
        return False
    return True


def _has_real_note(entry: dict) -> bool:
    note = entry.get("note")
    return isinstance(note, str) and note.strip() != ""


def check_fetch_review_gate(fetch_review: Any) -> ApprovalGateResult:
    """Run the Law #173 schema pre-check, then the core-aware unsupported-
    claim gate, against an already-parsed fetch_review value (whatever
    approval.json["fetch_review"] deserialized to -- may not even be a
    list, callers must not assume valid shape before calling this).

    Returns ApprovalGateResult(ok=True) only if the value is a non-empty
    list, every entry uses the real "fetched_content_supports_claim" field
    (not a verdict/supported/confirmed/status/result substitute), and every
    CORE entry (see _is_core()) has fetched_content_supports_claim=True --
    non-core entries may be False, but only with a real, non-empty "note"
    explaining the gap (honest disclosure, not a free pass to skip it).

    This is the exact logic tools/append_send_batch.py ran inline before
    2026-09-12 (F87) -- same checks, same precedence, same message wording,
    now callable from more than one place.
    """
    if not isinstance(fetch_review, list) or not fetch_review:
        return ApprovalGateResult(
            False,
            "approval.json has no non-empty fetch_review list (Law #165) "
            "— an approval with no fetch record is not a completed review",
        )

    schema_suspects = []
    for e in fetch_review:
        if not isinstance(e, dict):
            continue
        if "fetched_content_supports_claim" in e:
            continue  # real field present (whatever its value) -- not a schema issue
        found = [k for k in _VERDICT_SUBSTITUTE_KEYS if k in e]
        if found:
            schema_suspects.append((e, found))

    if schema_suspects:
        detail = "; ".join(
            f"claim={e.get('claim', '<no claim>')!r} has field(s) {found!r} but not "
            f"'fetched_content_supports_claim'"
            for e, found in schema_suspects[:5]
        )
        more = "" if len(schema_suspects) <= 5 else f" (+{len(schema_suspects) - 5} more)"
        return ApprovalGateResult(
            False,
            f"approval.json schema mismatch (Law #173): "
            f"{len(schema_suspects)} fetch_review entr"
            f"{'y' if len(schema_suspects) == 1 else 'ies'} use a "
            f"different field name instead of the required boolean "
            f"'fetched_content_supports_claim' -- this looks like a "
            f"field-naming mistake, not a content-verification "
            f"failure (see F78). {detail}{more}",
        )

    unsupported = []
    for e in fetch_review:
        if not isinstance(e, dict):
            unsupported.append(e)
            continue
        if e.get("fetched_content_supports_claim") is True:
            continue
        # fetched_content_supports_claim is False/missing/malformed from here.
        if _is_core(e):
            unsupported.append(e)
        elif not _has_real_note(e):
            # Non-core but undisclosed (no real note) -- still blocks. A
            # non-core claim isn't a free pass to skip disclosure entirely.
            unsupported.append(e)
        # else: non-core, unsupported, but honestly disclosed via a real
        # note -- allowed through, does not block.

    if unsupported:
        detail = "; ".join(
            (str(e.get("claim", e)) if isinstance(e, dict) else repr(e))
            for e in unsupported[:5]
        )
        return ApprovalGateResult(
            False,
            f"approval.json contains {len(unsupported)} unsupported/malformed "
            f"core claim(s), cannot log as approved send (Law #165): {detail}",
        )

    return ApprovalGateResult(True, None)

#!/usr/bin/env python3
"""Append-only observability log for the Perplexity -> Claude VO handoff.

WHAT THIS IS
------------
Under the VO-handoff workflow, Perplexity no longer writes VO text. It does the
research and sourcing, proposes a draft hook/opening line, and hands off a validated
package plus a word-count band and closing structure. Claude writes the actual VO,
which is then inserted and re-validated.

That is a multi-step, multi-actor sequence, and previously nothing recorded it. This
module records four events so the sequence is auditable after the fact:

    vo_requested  -- handoff sent to the writer (package staged with vo_status=pending)
    vo_received   -- a VO came back from the writer
    vo_inserted   -- the VO was written into the manifest AND re-validation passed
    vo_rejected   -- a returned VO failed re-validation and was not accepted

WHAT THIS IS NOT
----------------
PURE OBSERVABILITY. This log is deliberately NOT an input to any gate:

  * Law #166's pending-batch check does NOT read it. That check reads state.json's
    `status` field, and it must keep doing so -- a batch's blocking state lives in
    state.json, not here.
  * No blackout, cooldown, recent-send, or overlap check reads it.
  * Nothing in the send path reads it.

The reason is a failure mode this project has already hit: a log that starts as a
record and quietly becomes a source of truth. If this file were consulted by a gate,
a missing or malformed line would change production behavior. Deleting this entire
file must never change what the pipeline decides -- only what can be reconstructed
about what happened. Keep it that way.

THE ONE HARD GUARD
------------------
`log_vo_inserted` REFUSES to write unless validator_exit_code == 0. This is enforced
in code, not documented as a convention, because "the VO went in" is exactly the claim
someone would later trust without re-checking. Exit code 0 is fully_passed (zero FAILs
AND zero SKIPs); exit 3 (PARTIAL, VO still pending) and exit 1 (real failures) both
raise. See validators/validate_dual_package.py's main() for the code contract.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any

# Path is relative to the repo root, matching how cron_tracking/ is addressed elsewhere.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(_REPO_ROOT, "cron_tracking", "daily_combined", "vo_handoff_log.jsonl")

# The four event types. Anything else is rejected -- a typo'd event name in an
# append-only log is unfixable after the fact without rewriting history.
EVENT_VO_REQUESTED = "vo_requested"
EVENT_VO_RECEIVED = "vo_received"
EVENT_VO_INSERTED = "vo_inserted"
EVENT_VO_REJECTED = "vo_rejected"

EVENT_TYPES = (
    EVENT_VO_REQUESTED,
    EVENT_VO_RECEIVED,
    EVENT_VO_INSERTED,
    EVENT_VO_REJECTED,
)

# Exit code that means "every check evaluated and passed" (see the validator's main()).
VALIDATOR_EXIT_FULLY_PASSED = 0


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _append_line(record: dict[str, Any], path: str | None = None) -> str:
    """Append one JSON object as a line. Creates the file/dir if absent.

    Append-only by construction: opened in "a" mode, never "w". Nothing in this module
    rewrites or deletes an existing line.
    """
    target = path or LOG_PATH
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return target


def _base_record(event: str, batch_id: str, package_id: str,
                 **extra: Any) -> dict[str, Any]:
    if event not in EVENT_TYPES:
        raise ValueError(f"unknown event type {event!r}; expected one of {EVENT_TYPES}")
    if not isinstance(batch_id, str) or not batch_id.strip():
        raise ValueError(f"batch_id must be a non-empty string, got {batch_id!r}")
    if not isinstance(package_id, str) or not package_id.strip():
        raise ValueError(f"package_id must be a non-empty string, got {package_id!r}")
    rec = {
        "event": event,
        "ts": _now_iso(),
        "batch_id": batch_id,
        "package_id": package_id,
    }
    rec.update(extra)
    return rec


def log_vo_requested(batch_id: str, package_id: str, *, word_band: str = "",
                     note: str = "", path: str | None = None) -> str:
    """Record that a handoff was sent to the writer.

    `word_band` is the target the writer must hit (e.g. "200-216"), carried here so the
    request is reconstructable without re-deriving it from the manifest's edit length.

    Deliberately logged ONCE per handoff. A redo after a rejected VO reuses the same
    batch_id/package_id and does NOT log a second vo_requested -- see the
    failed-revalidation path in cron_daily_runtime.txt STEP 4.7.
    """
    return _append_line(
        _base_record(EVENT_VO_REQUESTED, batch_id, package_id,
                     word_band=word_band, note=note), path)


def log_vo_received(batch_id: str, package_id: str, *, vo_word_count: int | None = None,
                    note: str = "", path: str | None = None) -> str:
    """Record that a VO came back from the writer.

    Logged BEFORE re-validation, and logged regardless of whether the VO turns out to
    be acceptable. A received-then-rejected VO leaves both a vo_received and a
    vo_rejected line, which is what makes a retry loop legible after the fact.
    """
    return _append_line(
        _base_record(EVENT_VO_RECEIVED, batch_id, package_id,
                     vo_word_count=vo_word_count, note=note), path)


def log_vo_inserted(batch_id: str, package_id: str, *, validator_exit_code: int,
                    note: str = "", path: str | None = None) -> str:
    """Record that a VO was inserted AND the manifest re-validated clean.

    HARD GUARD: raises ValueError unless validator_exit_code == 0.

    This is enforced rather than documented because this specific line is the one a
    later reader would trust as "the VO is in and the package is good." Exit 3 means
    PARTIAL -- checks are still skipped, the VO is not actually complete. Exit 1 means
    real failures. Neither may be recorded as an insertion; the correct call in those
    cases is log_vo_rejected.
    """
    if validator_exit_code != VALIDATOR_EXIT_FULLY_PASSED:
        raise ValueError(
            f"refusing to log {EVENT_VO_INSERTED}: validator_exit_code="
            f"{validator_exit_code!r}, expected {VALIDATOR_EXIT_FULLY_PASSED} "
            f"(fully_passed: zero FAILs and zero SKIPs). Exit 3 means checks are still "
            f"skipped and the VO is not complete; exit 1 means real failures. "
            f"Use log_vo_rejected instead."
        )
    return _append_line(
        _base_record(EVENT_VO_INSERTED, batch_id, package_id,
                     validator_exit_code=validator_exit_code, note=note), path)


def log_vo_rejected(batch_id: str, package_id: str, *, validator_exit_code: int | None = None,
                    reason: str = "", failed_checks: list[str] | None = None,
                    note: str = "", path: str | None = None) -> str:
    """Record that a returned VO failed re-validation and was NOT accepted.

    The batch stays at AWAITING_VO after this -- a rejection does not close the batch,
    it returns it to the writer. `failed_checks` carries the specific check names so the
    redo request can be concrete instead of "it failed".
    """
    return _append_line(
        _base_record(EVENT_VO_REJECTED, batch_id, package_id,
                     validator_exit_code=validator_exit_code,
                     reason=reason,
                     failed_checks=list(failed_checks or []),
                     note=note), path)


def read_events(path: str | None = None) -> list[dict[str, Any]]:
    """Read every logged event. Convenience for inspection and tests ONLY.

    Nothing in the production path calls this, and nothing should start: see the
    "WHAT THIS IS NOT" note at the top of this module. Malformed lines are skipped
    rather than raising, so one bad line cannot make the whole log unreadable.
    """
    target = path or LOG_PATH
    if not os.path.exists(target):
        return []
    out: list[dict[str, Any]] = []
    with open(target, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out

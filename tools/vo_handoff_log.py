#!/usr/bin/env python3
"""Append-only observability log for the Claude-writes-VO handoff workflow
(standing process change, 2026-08-19).

Distinct from sent_scripts_log.json / sent_scripts_events.jsonl (which record
CONFIRMED SENDS and are read by Law #166's blackout/recent-send-conflict checks).
This file is PURE OBSERVABILITY: it is explicitly NEVER read by Law #166's
pending-batch check, NEVER read by any blackout/recent-send/overlap check, and
NEVER used as a gating input anywhere in validate_dual_package.py,
validate_longform_flagship.py, or append_send_batch.py. Its only purpose is
reconstructing the real handoff timeline for a batch/package after the fact
(e.g. "did we ask Claude twice for this package, and why").

Location: cron_tracking/daily_combined/vo_handoff_log.jsonl (one JSON object
per line, append-only, safe under concurrent git rebases the same way
sent_scripts_events.jsonl is).

Four event types, in the state-machine sequence a package moves through:

  vo_requested  -- draft/email stage: the package was emailed to Sebastian with
                   VO: [PENDING -- Claude to write]. Written when state.json
                   transitions a package's status to AWAITING_VO.
                   Fields: batch_id, package_id, slot, show, timestamp,
                            vo_status ("pending").

  vo_received   -- Sebastian pasted Claude's VO text back for this package.
                   Written BEFORE the full validator re-run, regardless of
                   whether that re-run will pass or fail -- this event fires
                   on receipt of the text, not on a passing outcome.
                   Fields: batch_id, package_id, slot, show, timestamp,
                            vo_word_count.

  vo_inserted   -- the pasted VO was inserted into the manifest AND the full,
                   unskipped validator re-run came back fully_passed=True.
                   This is the ONLY event that accompanies an AWAITING_VO ->
                   AWAITING_APPROVAL transition. A vo_received event with no
                   matching vo_inserted event means that attempt did not clear
                   validation (see vo_rejected).
                   Fields: batch_id, package_id, slot, show, timestamp,
                            validator_exit_code (must be 0 for this event to
                            be written at all -- 0 is the only fully_passed
                            exit code).

  vo_rejected   -- the pasted VO was inserted into the manifest but the full
                   validator re-run came back with a real FAIL (exit code 1)
                   or is still PARTIAL (exit code 3, e.g. a residual skip).
                   The batch/package stays at AWAITING_VO (no transition).
                   A NEW vo_requested event is NOT logged for the redo round
                   trip -- the existing vo_requested for this package_id still
                   stands, and the corrected VO that comes back next is just
                   another vo_received for the SAME batch_id/package_id.
                   Fields: batch_id, package_id, slot, show, timestamp,
                            validator_exit_code, failed_checks (list of check
                            names with status FAIL, from Result.failures()).

Explicit failed-revalidation case (per user's confirmed design, answered
2026-08-18): if Sebastian's VO is pasted back and the full validator run
comes back with a real FAIL:
  - the batch stays at AWAITING_VO (never transitions to AWAITING_APPROVAL)
  - vo_received is logged (receipt is unconditional)
  - vo_inserted is NOT logged (only a fully_passed re-run logs it)
  - vo_rejected IS logged, carrying the failed check names
  - the redo round trip reuses the SAME batch_id and package_id; the ORIGINAL
    vo_requested event stands -- no second vo_requested is written when the
    corrected VO comes back. That corrected text is simply a second
    vo_received event for the same package_id, and if it passes, the
    (only) vo_inserted event follows it.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any

LOG_RELATIVE_PATH = os.path.join("cron_tracking", "daily_combined", "vo_handoff_log.jsonl")

EVENT_TYPES = ("vo_requested", "vo_received", "vo_inserted", "vo_rejected")

# Fields required on every event regardless of type.
_COMMON_REQUIRED = ("batch_id", "package_id", "slot", "show")

# Type-specific required fields, per the schema documented in the module
# docstring above.
_TYPE_REQUIRED: dict[str, tuple[str, ...]] = {
    "vo_requested": ("vo_status",),
    "vo_received": ("vo_word_count",),
    "vo_inserted": ("validator_exit_code",),
    "vo_rejected": ("validator_exit_code", "failed_checks"),
}


def _log_path(tree: str) -> str:
    return os.path.join(tree, LOG_RELATIVE_PATH)


def build_event(event_type: str, *, batch_id: str, package_id: str, slot: str,
                 show: str, timestamp: str | None = None, **fields: Any) -> dict[str, Any]:
    """Construct one schema-valid event dict. Raises ValueError if the event
    type is unknown or a type-specific required field is missing -- this
    keeps a malformed event from ever reaching the log file."""
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown vo_handoff event type: {event_type!r}; expected one of {EVENT_TYPES}")
    required = _TYPE_REQUIRED[event_type]
    missing = [f for f in required if f not in fields]
    if missing:
        raise ValueError(f"{event_type} event missing required field(s): {missing}")
    if event_type == "vo_inserted" and fields.get("validator_exit_code") != 0:
        raise ValueError(
            "vo_inserted must only be logged when the full validator re-run is "
            f"fully_passed (exit code 0); got validator_exit_code={fields.get('validator_exit_code')!r}. "
            "A non-zero exit code belongs to a vo_rejected event instead.")
    event = {
        "event": event_type,
        "batch_id": batch_id,
        "package_id": package_id,
        "slot": slot,
        "show": show,
        "timestamp": timestamp or dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    event.update(fields)
    return event


def append_event(tree: str, event: dict[str, Any]) -> None:
    """Append one already-built event as one JSON line. Append-only, no
    read-modify-write of prior lines -- safe under concurrent git rebases the
    same way sent_scripts_events.jsonl is. Creates the parent directory and
    file on first use."""
    path = _log_path(tree)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def log_vo_requested(tree: str, *, batch_id: str, package_id: str, slot: str,
                      show: str, timestamp: str | None = None) -> dict[str, Any]:
    event = build_event("vo_requested", batch_id=batch_id, package_id=package_id,
                         slot=slot, show=show, timestamp=timestamp, vo_status="pending")
    append_event(tree, event)
    return event


def log_vo_received(tree: str, *, batch_id: str, package_id: str, slot: str,
                     show: str, vo_word_count: int, timestamp: str | None = None) -> dict[str, Any]:
    event = build_event("vo_received", batch_id=batch_id, package_id=package_id,
                         slot=slot, show=show, timestamp=timestamp, vo_word_count=vo_word_count)
    append_event(tree, event)
    return event


def log_vo_inserted(tree: str, *, batch_id: str, package_id: str, slot: str,
                     show: str, validator_exit_code: int, timestamp: str | None = None) -> dict[str, Any]:
    event = build_event("vo_inserted", batch_id=batch_id, package_id=package_id,
                         slot=slot, show=show, timestamp=timestamp,
                         validator_exit_code=validator_exit_code)
    append_event(tree, event)
    return event


def log_vo_rejected(tree: str, *, batch_id: str, package_id: str, slot: str, show: str,
                     validator_exit_code: int, failed_checks: list[str],
                     timestamp: str | None = None) -> dict[str, Any]:
    event = build_event("vo_rejected", batch_id=batch_id, package_id=package_id,
                         slot=slot, show=show, timestamp=timestamp,
                         validator_exit_code=validator_exit_code, failed_checks=list(failed_checks))
    append_event(tree, event)
    return event


def read_events(tree: str, *, batch_id: str | None = None, package_id: str | None = None) -> list[dict[str, Any]]:
    """Read back events, optionally filtered by batch_id and/or package_id.
    Used only for reconstructing the timeline / human inspection -- NEVER
    called from any gating path in the validators or append_send_batch.py."""
    path = _log_path(tree)
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if batch_id is not None and e.get("batch_id") != batch_id:
                continue
            if package_id is not None and e.get("package_id") != package_id:
                continue
            events.append(e)
    return events

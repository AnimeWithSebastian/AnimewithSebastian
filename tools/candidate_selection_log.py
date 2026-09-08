#!/usr/bin/env python3
"""Append-only observability log for candidate selection during the daily dual
package run (Fix 1, 2026-08-22).

Distinct from sent_scripts_log.json / sent_scripts_events.jsonl (which record
CONFIRMED SENDS) and from vo_handoff_log.jsonl (which records the Claude VO
round-trip timeline). Its only purpose is answering, after the fact, whether a
given format_type (e.g. THEORY_SPECULATION, SEASON_ROUNDUP) was genuinely
CONSIDERED and LOST on a given day, versus never having surfaced as a
candidate at all -- something sent_scripts_log.json alone cannot answer,
because it only ever records the two candidates that WON each day.

SCOPE OF GATING USE (revised 2026-08-22, Part 2 minimum-frequency-floor
design -- supersedes this module's original "pure observability, never a
gating input" claim, which is no longer accurate and must not be restated
elsewhere without this correction):

  This log IS now a real, sanctioned gating input, but to EXACTLY ONE
  consumer: validators/validate_dual_package.py's
  _validate_minimum_frequency_floor() function, which independently
  recomputes days_since_last_considered() against this log and fails the
  manifest closed if the manifest's self-reported minimum_frequency_floor
  field disagrees with that real recomputation. This is a deliberate,
  reviewed design decision (Part 2, approved 2026-08-22), not scope creep.

  It remains NEVER read by any OTHER check: not Law #166's
  blackout/recent-send/pending-batch checks, not any function in
  validate_dual_package.py other than _validate_minimum_frequency_floor,
  not validate_longform_flagship.py, and not append_send_batch.py. See
  tools/test_candidate_selection_log.py's
  test_never_imported_by_any_gating_module_except_minimum_frequency_floor
  for the test that mechanically enforces this narrower, still-true
  boundary, plus test_minimum_frequency_floor_is_the_only_reference_site
  which confirms the reference inside validate_dual_package.py appears
  ONLY inside that one function.

  Real consequence worth naming plainly: because this log now gates a real
  outcome (whether a format is forced into consideration), log_candidate()
  callers have a real incentive to want favorable values recorded that
  they did not have when this was pure historical observability. The
  append-only, schema-enforced-at-write-time discipline already built into
  build_event()/append_event() below stays important for a new reason --
  it was originally about audit-trail integrity; it is now also about
  resisting exactly that incentive.

WRITE TIMING -- READ THIS BEFORE CALLING log_candidate() (corrected design,
2026-08-22, per explicit user feedback on an earlier premature-write draft):

  Exactly ONE event is written per candidate considered on a given run, and
  it is written ONLY AFTER the full daily pipeline has finished running for
  that candidate -- i.e. after the monetization gate, format eligibility
  check, AND the diversity/blackout/final-selection pass have ALL completed
  for that candidate in this run's single model context. Call log_candidate()
  once per candidate near the end of STEP 3 (alongside/just before writing
  run_manifest.json), never mid-pipeline and never immediately after only one
  stage has run.

  Why: this cron run holds full knowledge of every candidate's final fate
  (selected, or rejected -- and if rejected, at which stage and why) by the
  time STEP 3 finishes. Writing earlier -- e.g. right after the monetization
  gate, before format eligibility or the diversity/blackout pass have even
  run -- would force `outcome` and `rejection_reason` to be filled in before
  they are actually known, making the log either wrong (a guessed outcome
  that a later stage overturns) or incomplete (fields left null that get
  silently orphaned once the real, later rejection happens). A single
  accurate write, made with full pipeline knowledge, is both sufficient and
  correct; there is no real reason requiring a second, TWO-write pattern here
  (contrast vo_handoff_log.py, where vo_received/vo_inserted/vo_rejected are
  genuinely three separate real-world events spread across a human round
  trip -- selection-pipeline stages, in contrast, all complete inside one run,
  one model context, before this log is ever touched).

Location: cron_tracking/daily_combined/candidate_selection_log.jsonl (one
JSON object per line, append-only, safe under concurrent git rebases the same
way sent_scripts_events.jsonl and vo_handoff_log.jsonl are).

One event type:

  candidate_scored -- one candidate considered during this run's selection
                      pipeline, with its final, pipeline-complete outcome.
                      Fields:
                        batch_id, run_ts, post_date, show, angle, format_type,
                        axis_scores (dict with sub_conversion,
                          brand_attractiveness, viral_discovery -- each a
                          HIGH/MED/LOW string),
                        cleared_monetization_gate (bool),
                        format_eligibility_checked (bool),
                        format_eligibility_result
                          ("eligible" | "ineligible" | "not_applicable"),
                        format_eligibility_reason (str, may be empty only
                          when format_eligibility_result == "not_applicable"),
                        outcome ("selected" | "rejected"),
                        rejection_reason (required non-empty string when
                          outcome == "rejected"; must be omitted/None when
                          outcome == "selected"),
                        slot_considered_for ("morning" | "evening" | "either"),
                        selected_package_id (uuid string, or None when
                          outcome == "rejected").
"""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any

LOG_RELATIVE_PATH = os.path.join("cron_tracking", "daily_combined", "candidate_selection_log.jsonl")

EVENT_TYPES = ("candidate_scored",)

_VALID_AXIS_SCORES = ("HIGH", "MED", "LOW")
_AXIS_KEYS = ("sub_conversion", "brand_attractiveness", "viral_discovery")
_VALID_ELIGIBILITY_RESULTS = ("eligible", "ineligible", "not_applicable")
_VALID_OUTCOMES = ("selected", "rejected")
_VALID_SLOTS = ("morning", "evening", "either")

# Fields required on every event (only one event type exists today, but this
# mirrors vo_handoff_log.py's _COMMON_REQUIRED / _TYPE_REQUIRED split so a
# second event type can be added later without restructuring).
_COMMON_REQUIRED = (
    "batch_id", "run_ts", "post_date", "show", "angle", "format_type",
    "axis_scores", "cleared_monetization_gate", "format_eligibility_checked",
    "format_eligibility_result", "outcome", "slot_considered_for",
)

_TYPE_REQUIRED: dict[str, tuple[str, ...]] = {
    "candidate_scored": (),
}


def _log_path(tree: str) -> str:
    return os.path.join(tree, LOG_RELATIVE_PATH)


def build_event(event_type: str, *, batch_id: str, run_ts: str, post_date: str,
                 show: str, angle: str, format_type: str,
                 axis_scores: dict[str, str], cleared_monetization_gate: bool,
                 format_eligibility_checked: bool, format_eligibility_result: str,
                 outcome: str, slot_considered_for: str,
                 format_eligibility_reason: str = "",
                 rejection_reason: str | None = None,
                 selected_package_id: str | None = None,
                 timestamp: str | None = None) -> dict[str, Any]:
    """Construct one schema-valid event dict. Raises ValueError on any
    malformed or incomplete event -- this keeps a bad event from ever
    reaching the log file. Enforces:
      - known event_type
      - all common required fields present
      - axis_scores has exactly the three required keys, each HIGH/MED/LOW
      - format_eligibility_result is one of the three valid enum values
      - format_eligibility_reason non-empty unless result == "not_applicable"
      - outcome is "selected" or "rejected"
      - rejection_reason is a required non-empty string when outcome ==
        "rejected", and must be omitted/None when outcome == "selected"
        (a selected candidate has no rejection reason by definition)
      - selected_package_id is required (non-empty) when outcome ==
        "selected", and must be None when outcome == "rejected"
      - slot_considered_for is one of morning/evening/either
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown candidate_selection event type: {event_type!r}; "
                          f"expected one of {EVENT_TYPES}")

    fields = {
        "batch_id": batch_id, "run_ts": run_ts, "post_date": post_date,
        "show": show, "angle": angle, "format_type": format_type,
        "axis_scores": axis_scores,
        "cleared_monetization_gate": cleared_monetization_gate,
        "format_eligibility_checked": format_eligibility_checked,
        "format_eligibility_result": format_eligibility_result,
        "format_eligibility_reason": format_eligibility_reason,
        "outcome": outcome,
        "rejection_reason": rejection_reason,
        "slot_considered_for": slot_considered_for,
        "selected_package_id": selected_package_id,
    }

    missing = [f for f in _COMMON_REQUIRED if fields.get(f) in (None, "")
               and f not in ("cleared_monetization_gate", "format_eligibility_checked")]
    # bool fields are allowed to be False -- only check they were actually passed
    for bool_field in ("cleared_monetization_gate", "format_eligibility_checked"):
        if not isinstance(fields.get(bool_field), bool):
            missing.append(bool_field)
    if missing:
        raise ValueError(f"{event_type} event missing/invalid required field(s): {sorted(set(missing))}")

    if not isinstance(axis_scores, dict) or set(axis_scores.keys()) != set(_AXIS_KEYS):
        raise ValueError(f"axis_scores must have exactly the keys {_AXIS_KEYS}; got {axis_scores!r}")
    bad_axis_values = {k: v for k, v in axis_scores.items() if v not in _VALID_AXIS_SCORES}
    if bad_axis_values:
        raise ValueError(f"axis_scores values must be one of {_VALID_AXIS_SCORES}; "
                          f"invalid entries: {bad_axis_values!r}")

    if format_eligibility_result not in _VALID_ELIGIBILITY_RESULTS:
        raise ValueError(f"format_eligibility_result must be one of {_VALID_ELIGIBILITY_RESULTS}; "
                          f"got {format_eligibility_result!r}")
    if format_eligibility_result != "not_applicable" and not format_eligibility_reason.strip():
        raise ValueError("format_eligibility_reason must be a non-empty string unless "
                          "format_eligibility_result == 'not_applicable'")

    if outcome not in _VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {_VALID_OUTCOMES}; got {outcome!r}")
    if outcome == "rejected":
        if not rejection_reason or not str(rejection_reason).strip():
            raise ValueError("rejection_reason is required and must be a non-empty string "
                              "when outcome == 'rejected'")
        if selected_package_id is not None:
            raise ValueError("selected_package_id must be None when outcome == 'rejected'")
    else:  # outcome == "selected"
        if rejection_reason is not None:
            raise ValueError("rejection_reason must be omitted/None when outcome == 'selected'")
        if not selected_package_id or not str(selected_package_id).strip():
            raise ValueError("selected_package_id is required and must be a non-empty string "
                              "when outcome == 'selected'")

    if slot_considered_for not in _VALID_SLOTS:
        raise ValueError(f"slot_considered_for must be one of {_VALID_SLOTS}; got {slot_considered_for!r}")

    event = {
        "event": event_type,
        "timestamp": timestamp or dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    event.update(fields)
    return event


def append_event(tree: str, event: dict[str, Any]) -> None:
    """Append one already-built event as one JSON line. Append-only, no
    read-modify-write of prior lines -- safe under concurrent git rebases the
    same way sent_scripts_events.jsonl and vo_handoff_log.jsonl are. Creates
    the parent directory and file on first use."""
    path = _log_path(tree)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def log_candidate(tree: str, *, batch_id: str, run_ts: str, post_date: str,
                   show: str, angle: str, format_type: str,
                   axis_scores: dict[str, str], cleared_monetization_gate: bool,
                   format_eligibility_checked: bool, format_eligibility_result: str,
                   outcome: str, slot_considered_for: str,
                   format_eligibility_reason: str = "",
                   rejection_reason: str | None = None,
                   selected_package_id: str | None = None,
                   timestamp: str | None = None) -> dict[str, Any]:
    """Convenience wrapper: build + append one candidate_scored event.

    Call this exactly ONCE per candidate considered on a run, and only after
    the full daily pipeline (monetization gate -> format eligibility ->
    diversity/blackout/final-selection) has completed for that candidate --
    see the write-timing note in the module docstring above."""
    event = build_event(
        "candidate_scored", batch_id=batch_id, run_ts=run_ts, post_date=post_date,
        show=show, angle=angle, format_type=format_type, axis_scores=axis_scores,
        cleared_monetization_gate=cleared_monetization_gate,
        format_eligibility_checked=format_eligibility_checked,
        format_eligibility_result=format_eligibility_result,
        format_eligibility_reason=format_eligibility_reason,
        outcome=outcome, rejection_reason=rejection_reason,
        slot_considered_for=slot_considered_for,
        selected_package_id=selected_package_id, timestamp=timestamp,
    )
    append_event(tree, event)
    return event


def read_events(tree: str, *, batch_id: str | None = None,
                 format_type: str | None = None) -> list[dict[str, Any]]:
    """Read back events, optionally filtered by batch_id and/or format_type.
    Used only for after-the-fact inspection (e.g. "did THEORY_SPECULATION
    candidates ever surface and lose, or never surface at all") -- NEVER
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
            if format_type is not None and e.get("format_type") != format_type:
                continue
            events.append(e)
    return events


def days_since_last_considered(tree: str, format_type: str, as_of_date: str,
                                *, exclude_batch_id: str | None = None) -> int | None:
    """Minimum-frequency floor (2026-08-22): real day-count since format_type
    was last CONSIDERED (i.e. got a candidate_scored event at all, regardless
    of outcome or eligibility result) -- not since it last WON. This is the
    one real, deliberate distinction the floor design rests on: a format that
    is faithfully evaluated every day and correctly loses on merit or
    eligibility must reset this clock (it WAS considered), while a format
    that is never even scored must not (it genuinely went dark). Using
    sent_scripts_log.json instead would erase that distinction, since a
    correctly-rejected format and a never-considered format look identical
    from a wins-only log -- this is why this function reads
    candidate_selection_log.jsonl exclusively, never sent_scripts_log.json.

    as_of_date is the anchor date (str, YYYY-MM-DD, normally the run's own
    post_date) the gap is measured back from -- passed explicitly rather than
    read from wall-clock time so this function is deterministic and testable
    against historical or synthetic data, not just "today."

    exclude_batch_id (2026-08-22, floor-overdue-at-eval-time fix): when set,
    events whose batch_id matches this value are excluded before computing
    the most-recent-event gap. This exists because log_candidate() writes
    happen in STEP 3, strictly BEFORE the STEP 6 validator runs (see
    cron_daily_runtime.txt) -- so by the time
    _validate_minimum_frequency_floor() calls this function, TODAY's own
    write already exists in the log. Without exclusion, any format actually
    evaluated this run always recomputes to gap=0 (today's own event is now
    the most recent), which the overdue check reads as "not overdue" --
    permanently erasing the ability to confirm "a format that WAS overdue
    going into today got force-evaluated today," the exact case the floor
    exists to guarantee. batch_id, not post_date, is the correct exclusion
    unit: this repo's real log legitimately has multiple batches sharing one
    post_date (e.g. a same-day re-run or backfill), so excluding by date
    could incorrectly also exclude a genuinely separate, real prior
    evaluation that happens to share today's date. batch_id uniquely
    identifies THIS run's own writes and nothing else's.

    Returns:
      - None if format_type has NEVER once appeared in the log (after any
        exclude_batch_id filtering) -- treated by callers as "infinitely
        overdue," which is the factually correct state for any format with
        zero real (non-excluded) candidate_scored history (e.g., as of this
        fix shipping, THEORY_SPECULATION / SEASON_ROUNDUP / WATCH_RANK all
        correctly return None against the real production log, since Fix 1
        only started writing events this session and none of the three has
        been scored since).
      - Otherwise, the integer day-count between the most recent non-excluded
        event's post_date for that format_type and as_of_date. Never negative
        in the normal case (most recent event should not postdate
        as_of_date), but this function does not itself validate ordering --
        it returns whatever the arithmetic produces, since a negative value
        is itself a useful, honest signal that the caller passed a stale
        as_of_date and should be visible rather than silently clamped.

    Malformed post_date values on individual events (missing, non-string, not
    valid YYYY-MM-DD) are skipped rather than raised -- this function is a
    read-side inspection helper, not the write-side schema gate build_event()
    already is, and an unparseable historical row should not make the whole
    query blow up. If a format_type has events but ALL of them have
    unparseable post_date values (or all are excluded by exclude_batch_id),
    this function returns None (same as never considered), since no real
    day-count can be computed from any of them.
    """
    anchor = dt.date.fromisoformat(as_of_date)
    events = read_events(tree, format_type=format_type)
    if exclude_batch_id is not None:
        events = [e for e in events if e.get("batch_id") != exclude_batch_id]
    parsed_dates: list[dt.date] = []
    for e in events:
        raw = e.get("post_date")
        if not isinstance(raw, str):
            continue
        try:
            parsed_dates.append(dt.date.fromisoformat(raw))
        except ValueError:
            continue
    if not parsed_dates:
        return None
    most_recent = max(parsed_dates)
    return (anchor - most_recent).days

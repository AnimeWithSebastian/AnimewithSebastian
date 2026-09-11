#!/usr/bin/env python3
"""Atomic, merge-safe dual-event logger for the combined daily dual-package run.

Called by cron_daily_runtime.txt ONLY AFTER both the MORNING and EVENING plain-text
emails have been confirmed sent. It:

  1. Appends TWO "sent" events to cron_tracking/sent_scripts_events.jsonl in ONE
     write (append-only JSONL — merge-safe under concurrent git rebases). Both rows
     share the manifest batch_id and carry distinct package_id values.
  2. Appends the two matching entries to the legacy sent_scripts_log.json array
     (read -> append -> atomic temp+rename) so existing consumers keep working.
  3. Writes the per-run state.json atomically (temp+rename) with accurate
     email_sent / log_appended / git_pushed flags and a shared batch_id.

IDEMPOTENT: the dedup key is (batch_id, package_id). Rerunning the same manifest
(e.g. a production retry after a git push) never duplicates a record in either log;
records already present are skipped while state flags such as git_pushed are still
updated. Partial-existing package IDs append only the missing record.

FAIL CLOSED: success (status="success") is written ONLY when both emails are sent
AND both log destinations have been appended. If --emails-sent is not asserted, the
helper records a failure state and appends NOTHING to the logs (never log a send
that did not happen). git_pushed is recorded separately and NEVER gates success of
the send+log step (git failure is non-blocking per repo convention) — but a git
failure is never recorded as a success.

MANIFEST RE-VALIDATION GATE (defense in depth): before appending anything, the helper
re-runs the deterministic preflight validator (validators/validate_dual_package.py) on
the manifest and FAILS CLOSED if the manifest does not pass. STEP 5 of the runtime is
supposed to validate before sending, but STEP 5 (validation) and STEP 7 (logging) were
previously decoupled — a manifest that never passed (or was overwritten after passing)
could still be logged as status="success" and appended to the sent log / ledger that
the weekly analytics cron reads. This gate binds logging to the same mechanical laws
so a non-conformant package can never be recorded as a successful send. If the
validator module cannot be imported, that is treated as a failure (cannot confirm
validity → do not record success).

Usage:
    python3 tools/append_send_batch.py <manifest.json> \
        --tree /home/user/workspace/repo \
        --emails-sent [--git-pushed] [--cron-id daily_combined]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any

CRON_ID_DEFAULT = "daily_combined"

# The deterministic validator lives in the sibling validators/ directory.
_VALIDATORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "validators")


def validate_manifest_failures(manifest: dict[str, Any],
                               tree: str | None = None) -> list[str]:
    """Re-run the deterministic preflight validator against the manifest.

    Returns the list of failed check names (empty list == manifest is clean). If the
    validator module cannot be imported, returns a single synthetic failure so the
    caller fails closed rather than logging a send it could not verify.

    SCHEMA CHANGE (2026-08-19, Claude-writes-VO workflow): Result.checks[1] is now a
    status STRING ("PASS"|"FAIL"|"SKIP"), not a bool. This function previously did
    `if not ok` on that position -- with a string, `not "FAIL"` and `not "PASS"` are
    BOTH False (non-empty strings are truthy), so that comparison would have silently
    stopped returning ANY failures at all, and the `if failures:` gate below would
    always pass. Fixed to compare the status string explicitly.

    TEST-ISOLATION FIX (2026-09-08, found during full repo audit): this previously
    called _v.validate_manifest(manifest) with no tree argument at all, so
    validate_dual_package's minimum_frequency_floor check silently fell back to its
    own _REPO_ROOT default and read the REAL, live floor-tracking log on disk --
    never the caller's own isolated --tree. Every test in test_append_send_batch.py
    using run_cli() (which does pass --tree to a temp directory) was therefore
    unknowingly validating against real, ever-growing production data instead of
    its own fixtures, causing failures that drift in and out as real time passes
    and that data grows, unrelated to anything the test itself set up. tree now
    threads all the way through to the real recomputation, matching the isolation
    main() already gives every other part of a test run. (This module still never
    imports the underlying floor-tracking log module directly -- the fix only
    passes tree through to validate_dual_package, the one sanctioned consumer.)
    """
    if _VALIDATORS_DIR not in sys.path:
        sys.path.insert(0, _VALIDATORS_DIR)
    try:
        import validate_dual_package as _v
    except Exception as e:  # noqa: BLE001 — cannot verify → fail closed
        return [f"validator import failed: {e}"]
    result = _v.validate_manifest(manifest, tree=tree)
    return [name for name, status, _ in result.checks if status == "FAIL"]


def validate_manifest_skips(manifest: dict[str, Any],
                            tree: str | None = None) -> list[str]:
    """Companion to validate_manifest_failures(): returns SKIPped check names.

    A manifest with ANY skip means vo_status == "pending" somewhere -- the package
    is still at the AWAITING_VO stage by definition and must NEVER reach a logged
    send here, even though it has zero real FAILs (Result.ok is True). This is the
    fully_passed distinction: append_batch() below must gate on zero failures AND
    zero skips, not just zero failures.

    See validate_manifest_failures()'s 2026-09-08 note -- tree threads through here
    for the identical test-isolation reason.
    """
    if _VALIDATORS_DIR not in sys.path:
        sys.path.insert(0, _VALIDATORS_DIR)
    try:
        import validate_dual_package as _v
    except Exception as e:  # noqa: BLE001 — cannot verify → fail closed
        return [f"validator import failed: {e}"]
    result = _v.validate_manifest(manifest, tree=tree)
    return [name for name, status, _ in result.checks if status == "SKIP"]


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _atomic_write(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _attribution_fields(pkg: dict[str, Any]) -> dict[str, Any]:
    """Laws #143-#145 attribution fields the WEEKLY analytics cron needs.

    The weekly cron (cron_analytics_runtime.txt STEP 4/5) is the sole enforcer of the
    topic-mix (>=9/14 timely), recurring-series (>=2/week), hook-family, funnel-status,
    and single-variant-integrity targets. It joins graded videos back to the per-package
    attribution recorded here (publication ledger carries no topic_class/series/hook
    fields, and the daily run_manifest.json is overwritten each day so it cannot supply
    a week of packages). If these fields are not persisted per send event, those weekly
    targets can never be computed and are silently skipped. The logger only runs after
    the deterministic validator passes, so every field below is guaranteed present."""
    return {
        "topic_class": pkg.get("topic_class"),
        "topic_signals": pkg.get("topic_signals", []) or [],
        "series": pkg.get("series"),
        "hook_family": pkg.get("hook_family"),
        "hook_line": pkg.get("hook_line"),
        "funnel_status": pkg.get("funnel_status"),
        # Item 3 addition (2026-07-25): full VO/loop/CTA archival. Prior to this change
        # only hook_line and vo_word_count were persisted -- the weekly analytics cron
        # and any future manual audit of a specific package's spoken content had no way
        # to recover the actual question/CTA/loop text or the full VO script from the
        # send-time logs, only from the daily run_manifest.json which is overwritten
        # every day. No new I/O required: pkg already carries all four fields when
        # _event_row/_legacy_row call this function (the deterministic validator has
        # already required their presence by the time append_batch runs).
        "question_line": pkg.get("question_line"),
        "cta_line": pkg.get("cta_line"),
        "loop_line": pkg.get("loop_line"),
        "vo": pkg.get("vo"),
    }


def _event_row(pkg: dict[str, Any], manifest: dict[str, Any], cron_id: str) -> dict[str, Any]:
    return {
        "event": "sent",
        "cron": cron_id,
        "batch_id": manifest.get("batch_id"),
        # corrects_batch_id (added 2026-08-13): a typed pointer back to the
        # original batch_id this send corrects. None for a normal (non-
        # correction) daily send -- this is purely additive metadata.
        "corrects_batch_id": manifest.get("corrects_batch_id"),
        "package_id": pkg.get("package_id"),
        "slot": pkg.get("slot"),
        "date_sent": manifest.get("run_ts") or _now_iso(),
        "post_date": manifest.get("post_date"),
        "show": pkg.get("show"),
        "angle": pkg.get("angle"),
        "format_type": pkg.get("format_type"),
        "format_reason": pkg.get("format_reason", ""),
        # correction_reason (added 2026-08-13): per-package, since a
        # correction batch may fix two packages for two different reasons.
        # None for a normal (non-correction) daily send.
        "correction_reason": pkg.get("correction_reason"),
        "title": pkg.get("youtube_title"),
        "tiktok_title": pkg.get("tiktok_title"),
        "traction_tier": pkg.get("traction_tier", ""),
        "gap_type": pkg.get("gap_type", ""),
        "fact_count": len(pkg.get("sources", []) or []),
        "vo_draft_included": bool(pkg.get("vo")),
        "vo_word_count": pkg.get("vo_word_count"),
        **_attribution_fields(pkg),
        "status": "sent",
    }


def _existing_keys_jsonl(events_path: str) -> set[tuple[Any, Any]]:
    """(batch_id, package_id) pairs already recorded in the JSONL ledger.

    F11 fix (production-audit finding, 2026-07-25): a line that fails to parse as
    JSON is excluded from the dedup set, which is a WARN-and-continue situation, not
    a fail-closed one -- blocking the whole append over one unrelated historical
    ledger line would be disproportionate. The exclusion is surfaced on stderr so it
    is never silently invisible.
    """
    keys: set[tuple[Any, Any]] = set()
    try:
        with open(events_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[WARN] {events_path}: a line could not be parsed as JSON "
                          "and was excluded from duplicate-detection", file=sys.stderr)
                    continue
                if isinstance(row, dict):
                    keys.add((row.get("batch_id"), row.get("package_id")))
    except OSError:
        pass
    return keys


class LegacyLogCorruptedError(Exception):
    """Raised when sent_scripts_log.json exists but cannot be safely treated as
    the historical record. Distinct from a genuinely missing file (first-ever
    run, or a fresh checkout), which is fine to treat as an empty list. This
    must never be silently downgraded to []  -- the caller cannot proceed to
    rewrite the file if it doesn't know whether [] means "nothing here yet" or
    "something here that we couldn't read.\""""


def _load_legacy(legacy_path: str) -> list[dict[str, Any]]:
    # A missing file (first-ever run, or a fresh checkout) is expected and fine to
    # treat as an empty list. A file that EXISTS but fails to parse is a different,
    # much more dangerous situation: silently treating a corrupted production log as
    # empty would make the next append effectively wipe the log's prior history. These
    # two cases are distinguished by CONTROL FLOW, not just warning text: a missing
    # file returns [], a corrupted file RAISES so the caller cannot proceed to
    # overwrite it with only the current run's rows.
    try:
        with open(legacy_path, encoding="utf-8") as fh:
            legacy = json.load(fh)
    except FileNotFoundError:
        return []
    except OSError as e:
        raise LegacyLogCorruptedError(
            f"could not read legacy log {legacy_path!r}: {e} — the file exists and "
            f"may need manual inspection; refusing to treat it as empty and overwrite it"
        ) from e
    except json.JSONDecodeError as e:
        raise LegacyLogCorruptedError(
            f"legacy log {legacy_path!r} exists but failed to parse as JSON ({e}) — "
            f"this likely means the file is CORRUPTED, not merely absent; refusing to "
            f"treat it as empty and overwrite it. Manually inspect and repair before retrying."
        ) from e
    if not isinstance(legacy, list):
        raise LegacyLogCorruptedError(
            f"legacy log {legacy_path!r} parsed but its top-level JSON is not a list "
            f"(got {type(legacy).__name__}) — refusing to treat it as empty and overwrite it."
        )
    return legacy


def _legacy_row(pkg: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "date_sent": manifest.get("run_ts") or _now_iso(),
        "post_date": manifest.get("post_date"),
        "slot": pkg.get("slot"),
        "show": pkg.get("show"),
        "angle": pkg.get("angle"),
        "format_type": pkg.get("format_type"),
        "format_reason": pkg.get("format_reason", ""),
        # correction_reason / corrects_batch_id (added 2026-08-13): see
        # _event_row() above for the full rationale. None on a normal send.
        "correction_reason": pkg.get("correction_reason"),
        "title": pkg.get("youtube_title"),
        "tiktok_title": pkg.get("tiktok_title"),
        "traction_tier": pkg.get("traction_tier", ""),
        "gap_type": pkg.get("gap_type", ""),
        "fact_count": len(pkg.get("sources", []) or []),
        "vo_draft_included": bool(pkg.get("vo")),
        "vo_word_count": pkg.get("vo_word_count"),
        "batch_id": manifest.get("batch_id"),
        "corrects_batch_id": manifest.get("corrects_batch_id"),
        "package_id": pkg.get("package_id"),
        **_attribution_fields(pkg),
        "status": "sent",
    }


def append_batch(manifest: dict[str, Any], tree: str, cron_id: str) -> dict[str, Any]:
    """Append both events to the JSONL ledger and the legacy array, idempotently.

    Dedup key is (batch_id, package_id). Rerunning the same manifest never
    duplicates a record in either log; only genuinely new package records are
    appended. When every record already exists this is a no-op on the logs (the
    caller still records accurate state flags such as git_pushed separately).
    """
    pkgs = manifest.get("packages", [])
    # Package count: normally exactly two, OR exactly one with an explicit,
    # non-empty M5 quality-over-quota justification -- mirrors the same exception
    # validate_dual_package.py already grants (see validate_manifest, "exactly two
    # packages exist, OR exactly one with a non-empty single_package_reason"). A
    # bare 1-package manifest with NO reason field still fails exactly as before --
    # this is intentionally NOT a general "1 or 2, no explanation needed" loosening,
    # since an unexplained missing package could mean a real pipeline failure rather
    # than a deliberate decision.
    single_reason = manifest.get("single_package_reason")
    is_justified_single = (
        len(pkgs) == 1
        and isinstance(single_reason, str)
        and bool(single_reason.strip())
    )
    if not (len(pkgs) == 2 or is_justified_single):
        raise ValueError(
            f"manifest must contain exactly 2 packages, or exactly 1 with a "
            f"non-empty single_package_reason, got {len(pkgs)} package(s) and "
            f"single_package_reason={single_reason!r}"
        )

    events_path = os.path.join(tree, "cron_tracking", "sent_scripts_events.jsonl")
    legacy_path = os.path.join(tree, "sent_scripts_log.json")
    batch_id = manifest.get("batch_id")

    # (1) JSONL ledger: append only rows whose (batch_id, package_id) is new,
    #     in ONE append write — atomic + merge-safe.
    existing_events = _existing_keys_jsonl(events_path)
    new_rows = [_event_row(p, manifest, cron_id) for p in pkgs
                if (batch_id, p.get("package_id")) not in existing_events]
    if new_rows:
        os.makedirs(os.path.dirname(events_path), exist_ok=True)
        blob = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new_rows)
        with open(events_path, "a", encoding="utf-8") as fh:
            fh.write(blob)
            fh.flush()
            os.fsync(fh.fileno())

    # (2) legacy array: append only new (batch_id, package_id) rows -> atomic rewrite.
    legacy = _load_legacy(legacy_path)
    existing_legacy = {(r.get("batch_id"), r.get("package_id"))
                       for r in legacy if isinstance(r, dict)}
    legacy_added = 0
    for p in pkgs:
        if (batch_id, p.get("package_id")) in existing_legacy:
            continue
        legacy.append(_legacy_row(p, manifest))
        existing_legacy.add((batch_id, p.get("package_id")))
        legacy_added += 1
    if legacy_added:
        _atomic_write(legacy_path, json.dumps(legacy, indent=2, ensure_ascii=False))

    return {"events_appended": len(new_rows),
            "events_skipped": len(pkgs) - len(new_rows),
            "legacy_added": legacy_added,
            "legacy_total": len(legacy),
            "package_ids": [p.get("package_id") for p in pkgs]}


_BLOCKING_STATUSES = ("AWAITING_APPROVAL", "AWAITING_VO")


def _confirmed_send_exists(batch_id: Any, tree: str, cron_id: str) -> bool:
    """True if a real 'sent' record for batch_id exists in either durable log.

    Checked in the JSONL ledger (via _existing_keys_jsonl, keyed on batch_id
    regardless of package_id) and in the top-level state.json's own batch_id
    field, matching the two locations Law #166's prose names explicitly.
    """
    events_path = os.path.join(tree, "cron_tracking", "sent_scripts_events.jsonl")
    if any(k[0] == batch_id for k in _existing_keys_jsonl(events_path)):
        return True
    top_state_path = os.path.join(tree, "cron_tracking", cron_id, "state.json")
    try:
        with open(top_state_path, encoding="utf-8") as fh:
            top_state = json.load(fh)
        if isinstance(top_state, dict) and top_state.get("batch_id") == batch_id \
                and top_state.get("status") == "success":
            return True
    except (OSError, json.JSONDecodeError):
        pass
    return False


def check_pending_batches(tree: str, cron_id: str) -> list[dict[str, Any]]:
    """Law #166 pending-batch check, ported to real code (was prose-only).

    A pending batch BLOCKS today's run only if BOTH are true:
      (a) its state.json's top-level "status" field is EXACTLY "AWAITING_APPROVAL"
          or exactly "AWAITING_VO" (direct dict-field read -- never a substring
          grep across the file, which is what produced F38's false positive), AND
      (b) no confirmed send exists for that batch_id in sent_scripts_events.jsonl
          or in the top-level state.json (see _confirmed_send_exists).

    Precedence order (checked in this order, first match wins):
      1. F37 correction-batch carve-out: if the pending record has a non-null
         corrects_batch_id AND (b) is false (i.e. a confirmed send already
         exists for it) while (a) still reads AWAITING_*, that is the F38
         stale-state condition, not a real backlog item -- excluded from the
         blocking list regardless of the raw status string.
      2. Otherwise, the two-part test above applies as written.

    Fails OPEN (non-blocking) on any pending directory whose state.json is
    missing, unreadable, or missing a "status" field -- this matches current
    de-facto behavior (nothing enforces this today) rather than introducing a
    new way for a corrupt/incomplete directory to halt every future run.

    Returns the list of blocking records (each a dict with batch_id, status,
    dir), so an empty list means clear to proceed.
    """
    pending_root = os.path.join(tree, "cron_tracking", cron_id, "pending")
    blocking: list[dict[str, Any]] = []
    try:
        entries = sorted(os.listdir(pending_root))
    except OSError:
        return blocking
    for entry in entries:
        state_path = os.path.join(pending_root, entry, "state.json")
        try:
            with open(state_path, encoding="utf-8") as fh:
                pending_state = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue  # fail open: unreadable/missing state.json never blocks
        if not isinstance(pending_state, dict):
            continue
        status = pending_state.get("status")
        batch_id = pending_state.get("batch_id", entry)
        if status not in _BLOCKING_STATUSES:
            continue  # (a) false -> never blocks, regardless of (b)
        already_sent = _confirmed_send_exists(batch_id, tree, cron_id)
        if pending_state.get("corrects_batch_id") is not None and already_sent:
            continue  # precedence 1: F37 carve-out overrides a stale AWAITING_* read
        if already_sent:
            continue  # (b) false -> F38 stale-state, never blocks
        blocking.append({"batch_id": batch_id, "status": status, "dir": entry})
    return blocking


def mirror_pending_state(manifest: dict[str, Any], tree: str, cron_id: str,
                         state: dict[str, Any]) -> str | None:
    """F38 fix (2026-08-15): flip the PER-BATCH pending/<batch_id>/state.json to a
    terminal status after a genuinely successful send.

    THE GAP THIS CLOSES: STEP 6 writes pending/<batch_id>/state.json with a
    non-terminal awaiting-approval status. STEP 7/8/9 then only ever wrote the
    TOP-LEVEL cron_tracking/<cron_id>/state.json -- nothing transitioned the
    per-batch copy. So a batch that sent hours or days ago still looked, to Law
    #166's pending-batch scan (which reads exactly that per-batch file), like an
    open unreviewed backlog item forever. That is the direct mechanical enabler of
    F37: the next unattended daily run would read it as still open and skip
    generating a fresh batch, with no distinct failure signal. This already
    happened for real to batch 32e0fcb9 (Link Click, post_date 2026-08-14), which
    sat non-terminal after its morning package had actually been sent.

    FAIL-SAFE BY DESIGN -- ONLY FLIPS ON SUCCESS. If the send/log did not fully
    succeed this writes NOTHING and leaves the pending state untouched, so a failed
    batch keeps blocking Law #166 exactly as it should. A terminal status is only
    ever recorded for a batch that really completed.

    STEP 6 FIELDS ARE PRESERVED (merge, not overwrite): single_package_reason,
    corrects_batch_id, held_packages and any hold record stay intact, because a
    batch can legitimately be terminal for one package while another is separately
    held (e.g. 32e0fcb9: Link Click sent, Slime held under Law #165 / F36).
    Reaching a terminal status here NEVER implies a held package was resolved.

    F73 fix (2026-09-08): also resolves the pending directory by the batch_id
    recorded INSIDE each directory's files when the directory name itself
    isn't the raw batch_id (see the fallback scan below) -- previously this
    silently no-op'd for any pending/ directory using a human-readable name.

    Returns the path written, or None when nothing was written. None is not a
    failure signal -- it means "not a success" or "no pending dir for this batch"
    (most batches never use the pending/ approval flow at all).
    """
    if state.get("status") != "success":
        return None
    batch_id = manifest.get("batch_id")
    if not batch_id:
        return None
    pending_root = os.path.join(tree, "cron_tracking", cron_id, "pending")
    pending_dir = os.path.join(pending_root, str(batch_id))
    if not os.path.isdir(pending_dir):
        # F73 fix (2026-09-08): the fast path above assumes the pending/
        # directory is literally named after the raw batch_id. Several real
        # batches this session (batchA_20260901, batchB_20260902,
        # fresh_20260907, replacement_20260902) used human-readable directory
        # names instead, so that assumption silently failed -- the function
        # returned None with no error, and those batches never got a per-batch
        # terminal state written at all. check_pending_batches() never had
        # this bug because it already matches by the batch_id recorded INSIDE
        # each directory's own file, never by the directory's name -- so this
        # fallback reuses that same content-based matching instead of
        # inventing a new convention.
        pending_dir = None
        try:
            entries = sorted(os.listdir(pending_root))
        except OSError:
            entries = []
        for entry in entries:
            candidate = os.path.join(pending_root, entry)
            if not os.path.isdir(candidate):
                continue
            found_id = None
            for fname in ("state.json", "run_manifest.json", "approval.json"):
                try:
                    with open(os.path.join(candidate, fname), encoding="utf-8") as fh:
                        payload = json.load(fh)
                except (OSError, json.JSONDecodeError):
                    continue
                if isinstance(payload, dict) and payload.get("batch_id"):
                    found_id = payload["batch_id"]
                    break
            if found_id == batch_id:
                pending_dir = candidate
                break
        if pending_dir is None:
            return None
    pending_path = os.path.join(pending_dir, "state.json")

    existing: dict[str, Any] = {}
    try:
        with open(pending_path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            existing = loaded
    except (OSError, json.JSONDecodeError):
        # A missing/corrupt per-batch file must not abort the send record -- the
        # top-level state.json is already written and authoritative. Still write a
        # terminal per-batch file so Law #166's scan gets a clean signal.
        existing = {}

    merged = dict(existing)
    merged.update({
        "status": "sent",          # terminal value proposed by F38 itself
        "emails_sent": state.get("emails_sent"),
        "log_appended": state.get("log_appended"),
        "git_pushed": state.get("git_pushed"),
        "error": state.get("error"),
        "batch_id": batch_id,
        "terminal_state_written_at": state.get("run_ts"),
        "terminal_state_written_by": "tools/append_send_batch.py (F38)",
    })
    _atomic_write(pending_path, json.dumps(merged, indent=2, ensure_ascii=False))
    return pending_path


def write_state(manifest: dict[str, Any], tree: str, cron_id: str, *,
                emails_sent: bool, log_appended: bool, git_pushed: bool,
                error: str | None) -> str:
    status = "success" if (emails_sent and log_appended and error is None) else "failed"
    pkgs = manifest.get("packages", [])
    state = {
        "cron_id": cron_id,
        "workflow": "combined_daily_dual_package",
        "batch_id": manifest.get("batch_id"),
        "run_ts": _now_iso(),
        "post_date": manifest.get("post_date"),
        "status": status,
        "emails_sent": emails_sent,
        "log_appended": log_appended,
        "git_pushed": git_pushed,
        "error": error,
        "packages": [
            {
                "package_id": p.get("package_id"),
                "slot": p.get("slot"),
                "show": p.get("show"),
                "format_type": p.get("format_type"),
                "vo_word_count": p.get("vo_word_count"),
            }
            for p in pkgs
        ],
    }
    state_path = os.path.join(tree, "cron_tracking", cron_id, "state.json")
    _atomic_write(state_path, json.dumps(state, indent=2, ensure_ascii=False))
    # F38 (2026-08-15): keep the per-batch pending copy in sync with this top-level
    # mirror. No-ops unless the send actually succeeded AND this batch used the
    # pending/ approval flow. Deliberately AFTER the top-level write: the top-level
    # state is authoritative, so it must land even if the per-batch mirror cannot.
    mirror_pending_state(manifest, tree, cron_id, state)
    return state_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--tree", default=os.getcwd(),
                    help="repo working tree root (default: cwd)")
    ap.add_argument("--cron-id", default=CRON_ID_DEFAULT)
    ap.add_argument("--emails-sent", action="store_true",
                    help="assert BOTH emails were confirmed sent (required to log)")
    ap.add_argument("--approval-file", default=None,
                    help="path to pending/<batch_id>/approval.json (Law #164/#165). "
                         "Required to log a send. Must exist, parse as JSON, and have "
                         "a non-empty fetch_review list where every entry has "
                         "fetched_content_supports_claim == true. NOTE (honest "
                         "limitation, same disclosure pattern as blackout_conflict/ "
                         "recent_send_conflict self-attestation): this check protects "
                         "the integrity of the LOG, not the send action itself -- by "
                         "the time this script runs, STEP 7 has already sent the "
                         "emails. This gate can refuse to record a send as successful "
                         "after the fact; it cannot retroactively unsend an email that "
                         "went out without a real approval.json.")
    ap.add_argument("--git-pushed", action="store_true")
    args = ap.parse_args(argv[1:])

    # FAIL CLOSED: a missing or malformed manifest must not crash with a bare
    # traceback and no diagnostic trail -- every other failure path in this file
    # writes a status="failed" state.json before returning 1; this one must too.
    try:
        with open(args.manifest, encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        path = write_state({}, args.tree, args.cron_id,
                           emails_sent=False, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"could not load manifest {args.manifest!r}: {e}")
        print(f"[BLOCKED] could not load manifest {args.manifest!r}: {e}; "
              f"wrote failure state to {path}", file=sys.stderr)
        return 1

    # FAIL CLOSED: never append a send that did not happen.
    if not args.emails_sent:
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=False, log_appended=False,
                           git_pushed=args.git_pushed,
                           error="emails not confirmed sent — nothing logged")
        print(f"[BLOCKED] --emails-sent not asserted; wrote failure state to {path}")
        return 1

    # FAIL CLOSED (Law #164/#165): never log a send without a recorded, real
    # fetch-based approval. See --approval-file help text above for the honest
    # limitation -- this protects the LOG's integrity, not the send call itself.
    if not args.approval_file:
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error="--approval-file not provided — cannot log a send "
                                 "without a recorded approval (Law #164)")
        print(f"[BLOCKED] --approval-file not provided; wrote failure state to {path}",
              file=sys.stderr)
        return 1

    try:
        with open(args.approval_file, encoding="utf-8") as fh:
            approval = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"could not load --approval-file {args.approval_file!r}: {e}")
        print(f"[BLOCKED] could not load approval file: {e}; wrote failure state to {path}",
              file=sys.stderr)
        return 1

    fetch_review = approval.get("fetch_review")
    if not isinstance(fetch_review, list) or not fetch_review:
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error="approval.json has no non-empty fetch_review list (Law #165) "
                                 "— an approval with no fetch record is not a completed review")
        print(f"[BLOCKED] approval.json missing fetch_review; wrote failure state to {path}",
              file=sys.stderr)
        return 1

    # SCHEMA PRE-CHECK (Law #173, added 2026-09-10 -- directly addresses F78): an
    # approval.json authored with a "verdict" string field (e.g. "confirmed")
    # instead of the required "fetched_content_supports_claim" boolean produced
    # the exact same generic "unsupported/malformed" error the genuine-content-
    # failure path below produces -- costing real diagnostic time distinguishing
    # a field-naming mistake from an actual verification failure. This scans for
    # entries missing the real field but carrying a plausible substitute name,
    # and fails with a distinct, schema-specific message BEFORE the generic
    # content-verification path, so the two failure classes are never conflated
    # again. An entry with NO substitute-looking field at all still falls through
    # to the existing generic check below, unchanged -- this only catches the
    # specific "used the wrong field name" shape F78 found.
    _VERDICT_SUBSTITUTE_KEYS = ("verdict", "supported", "confirmed", "status", "result")
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
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"approval.json schema mismatch (Law #173): "
                                 f"{len(schema_suspects)} fetch_review entr"
                                 f"{'y' if len(schema_suspects) == 1 else 'ies'} use a "
                                 f"different field name instead of the required boolean "
                                 f"'fetched_content_supports_claim' -- this looks like a "
                                 f"field-naming mistake, not a content-verification "
                                 f"failure (see F78). {detail}{more}")
        print(f"[BLOCKED] approval.json schema mismatch (Law #173, see F78); "
              f"wrote failure state to {path}", file=sys.stderr)
        return 1

    # CORE-AWARE GATE (2026-08-19, narrow fix for the false-positive block on
    # honestly-disclosed non-core claims): a fetch_review entry only needs
    # fetched_content_supports_claim == True when it is a CORE claim. An
    # entry explicitly marked non-core may legitimately have
    # fetched_content_supports_claim: False WITHOUT blocking the log, but
    # only if it carries a real, non-empty "note" explaining the gap --
    # non-core does not mean "skip disclosure", it means "not audience-
    # facing enough to be a hard blocker once honestly disclosed".
    #
    # core/non-core detection precedence (explicit, in order):
    #   1. A structured "core" key present on the entry (True or False) is
    #      authoritative. If present, the legacy text-prefix convention
    #      below is IGNORED for that entry -- the two signals never get a
    #      chance to silently disagree.
    #   2. Else, a claim string starting with a case-insensitive, start-
    #      anchored NON-CORE marker (in square brackets) is treated as
    #      core=False. This is the LEGACY path: every existing approval.json
    #      in this repo (7+ files, including real production batches)
    #      encodes non-core claims this way, since no approval.json has ever
    #      used a structured field.
    #   3. Else (no structured field, no text-prefix match): default to
    #      core=True -- the safe, strict default, identical to today's
    #      behavior for any entry with no explicit signal either way.
    #
    # GOING FORWARD: new approval.json files should be built using the
    # structured "core": true/false field, not the legacy bracketed text
    # marker. The text-prefix path exists only to keep historical/legacy
    # approvals working; it is not the intended long-term format.
    _NON_CORE_PREFIX_RE = re.compile(r"^\s*\[NON-CORE\b", re.IGNORECASE)

    def _is_core(entry: dict) -> bool:
        if "core" in entry and entry["core"] is not None:
            return entry["core"] is not False
        claim = entry.get("claim")
        if isinstance(claim, str) and _NON_CORE_PREFIX_RE.match(claim):
            return False
        return True

    def _has_real_note(entry: dict) -> bool:
        note = entry.get("note")
        return isinstance(note, str) and note.strip() != ""

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
        # note -- allowed through, does not block the log.

    if unsupported:
        # A malformed (non-dict) fetch_review entry is itself one of the things
        # this gate must fail closed on -- so the detail message must handle it
        # without calling .get() on a non-dict and crashing instead of blocking.
        detail = "; ".join(
            (str(e.get("claim", e)) if isinstance(e, dict) else repr(e))
            for e in unsupported[:5]
        )
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"approval.json contains {len(unsupported)} unsupported/malformed "
                                 f"core claim(s), cannot log as approved send (Law #165): {detail}")
        print(f"[BLOCKED] approval.json has unsupported claim(s); wrote failure state to {path}",
              file=sys.stderr)
        return 1

    # FAIL CLOSED: never log a send for a manifest that does not pass the validator.
    # Binds STEP 7 logging to the same mechanical gate as STEP 5 preflight.
    failures = validate_manifest_failures(manifest, tree=args.tree)
    if failures:
        detail = "; ".join(failures[:8]) + (f"; +{len(failures) - 8} more" if len(failures) > 8 else "")
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"manifest failed preflight validation ({len(failures)} check(s)): {detail}")
        print(f"[BLOCKED] manifest failed preflight validation "
              f"({len(failures)} check(s)); appended nothing; wrote failure state to {path}",
              file=sys.stderr)
        return 1

    # FAIL CLOSED (2026-08-19, Claude-writes-VO workflow): a manifest can have zero
    # FAILs but still be VO-pending (Result.ok True, Result.fully_passed False). That
    # is the AWAITING_VO draft/email stage, not a real send. Never log a send for a
    # manifest carrying any SKIP -- fully_passed, not ok, is the real send gate.
    skips = validate_manifest_skips(manifest, tree=args.tree)
    if skips:
        detail = "; ".join(skips[:8]) + (f"; +{len(skips) - 8} more" if len(skips) > 8 else "")
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"manifest is VO-pending, not fully validated "
                                 f"({len(skips)} check(s) skipped): {detail}")
        print(f"[BLOCKED] manifest has {len(skips)} skipped (VO-pending) check(s); "
              f"appended nothing; wrote failure state to {path}",
              file=sys.stderr)
        return 1

    try:
        summary = append_batch(manifest, args.tree, args.cron_id)
    except Exception as e:  # noqa: BLE001 — record failure state, never mark success
        write_state(manifest, args.tree, args.cron_id,
                    emails_sent=True, log_appended=False,
                    git_pushed=args.git_pushed, error=f"log append failed: {e}")
        print(f"[FAIL] log append failed: {e}", file=sys.stderr)
        return 1

    path = write_state(manifest, args.tree, args.cron_id,
                       emails_sent=True, log_appended=True,
                       git_pushed=args.git_pushed, error=None)
    print(f"[OK] appended {summary['events_appended']} events "
          f"(skipped {summary['events_skipped']} already-present; "
          f"legacy_added={summary['legacy_added']}); "
          f"package_ids={summary['package_ids']}; state -> {path}; "
          f"git_pushed={args.git_pushed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

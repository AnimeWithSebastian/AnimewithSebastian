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
import sys
from typing import Any

CRON_ID_DEFAULT = "daily_combined"

# The deterministic validator lives in the sibling validators/ directory.
_VALIDATORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "validators")


def _run_validator(manifest: dict[str, Any]):
    """Import the validator and run it. Returns (result, error_string).

    On import failure returns (None, msg) so every caller can fail closed rather than
    logging a send it was unable to verify.
    """
    if _VALIDATORS_DIR not in sys.path:
        sys.path.insert(0, _VALIDATORS_DIR)
    try:
        import validate_dual_package as _v
    except Exception as e:  # noqa: BLE001 — cannot verify → fail closed
        return None, f"validator import failed: {e}"
    return _v.validate_manifest(manifest), None


def validate_manifest_failures(manifest: dict[str, Any]) -> list[str]:
    """Re-run the deterministic preflight validator; return failed check names.

    Empty list == no FAILs. If the validator cannot be imported, returns a single
    synthetic failure so the caller fails closed.

    ============================ REAL BUG FIXED 2026-08-16 ============================
    This function previously ended with:

        return [name for name, ok, _ in result.checks if not ok]

    That was correct while checks[1] was a BOOL. It became SILENTLY, TOTALLY BROKEN the
    moment checks[1] became a status STRING, because every non-empty string is truthy
    in Python -- `not "FAIL"` and `not "PASS"` are BOTH False. The comprehension
    therefore matched NOTHING and this function returned an EMPTY LIST FOR EVERY
    MANIFEST, ALWAYS.

    The consequence was not cosmetic. main()'s send gate reads `if failures:` -- so a
    manifest failing any number of real preflight checks would have sailed through the
    gate and been written into the send log as a clean send, with no error state and no
    warning. A broken package could be logged as successfully sent.

    The fix is to compare the status explicitly. Anything else iterating these tuples
    must do the same; `if not ok` is never correct against a status string.
    ===================================================================================
    """
    result, err = _run_validator(manifest)
    if result is None:
        return [err]
    return [name for name, status, _ in result.checks if status == "FAIL"]


def validate_manifest_skips(manifest: dict[str, Any]) -> list[str]:
    """Return the names of checks the validator SKIPPED (could not evaluate).

    A skip means a VO-pending package: Perplexity has handed off validated facts and
    Claude has not written the VO yet, so the VO-dependent checks cannot be evaluated.
    Such a manifest is a legitimate draft, but it is NOT sendable and must never be
    written to the send log.

    Mirrors the explicit-status comparison in validate_manifest_failures above, for the
    same reason: `if not ok` would match nothing here too.

    On validator import failure this returns an empty list rather than a synthetic
    entry -- the import failure is already reported as a FAILURE by
    validate_manifest_failures, which main() checks first, so reporting it twice would
    double-count one problem.
    """
    result, err = _run_validator(manifest)
    if result is None:
        return []
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

    Returns the path written, or None when nothing was written. None is not a
    failure signal -- it means "not a success" or "no pending dir for this batch"
    (most batches never use the pending/ approval flow at all).
    """
    if state.get("status") != "success":
        return None
    batch_id = manifest.get("batch_id")
    if not batch_id:
        return None
    pending_dir = os.path.join(tree, "cron_tracking", cron_id, "pending", str(batch_id))
    if not os.path.isdir(pending_dir):
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

    unsupported = [e for e in fetch_review
                   if not isinstance(e, dict) or e.get("fetched_content_supports_claim") is not True]
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
    failures = validate_manifest_failures(manifest)
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

    # FAIL CLOSED ON SKIPS TOO (2026-08-16, VO handoff). `ok` (zero FAILs) is NOT the
    # send gate -- `fully_passed` (zero FAILs AND zero SKIPs) is. A manifest with
    # vo_status="pending" has real, unevaluated VO-dependent checks; it is a legitimate
    # draft but it has no finished VO, so logging it as a send would record an email
    # that could not have gone out. Blocked here as a distinct, named condition rather
    # than folded into the failure branch, so the state file says what actually happened.
    skips = validate_manifest_skips(manifest)
    if skips:
        detail = "; ".join(skips[:8]) + (f"; +{len(skips) - 8} more" if len(skips) > 8 else "")
        path = write_state(manifest, args.tree, args.cron_id,
                           emails_sent=args.emails_sent, log_appended=False,
                           git_pushed=args.git_pushed,
                           error=f"manifest has {len(skips)} unevaluated (SKIPPED) check(s) "
                                 f"-- VO not written yet, not sendable: {detail}")
        print(f"[BLOCKED] manifest has {len(skips)} SKIPPED check(s) (VO pending); "
              f"appended nothing; wrote failure state to {path}", file=sys.stderr)
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

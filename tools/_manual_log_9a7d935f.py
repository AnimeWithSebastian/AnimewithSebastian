#!/usr/bin/env python3
"""ONE-OFF manual logging script for batch 9a7d935f-95e6-40ac-8dfc-a6dd1d9a3eb7.

WHY THIS EXISTS (do not reuse as a pattern): tools/append_send_batch.py's
--approval-file gate blocked this batch's log append because 3 of its 14
fetch_review entries have fetched_content_supports_claim == false. All 3 are
explicitly labeled rejected/superseded historical record (2 are literally
titled "ORIGINAL CLAIM (rejected pre-approval)", one is the already-replaced
VIZ citation) -- none represent a live unsupported claim in the actual sent
VO/caption content. This is a real, identified gap in the gate (it checks
every fetch_review entry indiscriminately, with no rejected/superseded
exemption) -- logged as new KNOWN_ISSUES entry F72, not fixed tonight per
explicit user instruction.

Both emails were confirmed genuinely sent via the Outlook connector:
  - Morning (Hunter x Hunter): sent 2026-08-27T02:44:00Z (10:44 PM EDT Aug 26)
  - Evening (Kagurabachi):     sent 2026-08-27T02:45:00Z (10:45 PM EDT Aug 26)

This script writes the exact same row shapes _event_row()/_legacy_row()/
write_state() in append_send_batch.py would have written on a real passing
run, using only real values pulled from the committed run_manifest.json --
no fabricated or invented fields. Manually invoked once, per explicit
authorization from Sebastian (2026-08-26 ~10:50 PM EDT). Not part of any
automated pipeline; safe to delete after this run.
"""
from __future__ import annotations

import json
import os

TREE = "/home/user/workspace/repo_restore"
CRON_ID = "daily_combined"
BATCH_ID = "9a7d935f-95e6-40ac-8dfc-a6dd1d9a3eb7"
PENDING_DIR = os.path.join(TREE, "cron_tracking", CRON_ID, "pending", BATCH_ID)

MANUAL_NOTE = (
    "Logged manually -- both emails confirmed genuinely sent. The automated "
    "append_send_batch.py gate blocked on 3 of 14 fetch_review entries explicitly "
    "labeled as rejected/superseded historical record (2 marked 'ORIGINAL CLAIM "
    "(rejected pre-approval)', 1 an already-replaced citation) -- none represent a "
    "live unsupported claim in the actual sent content. This is a real, identified "
    "gap in the gate's logic (no rejected/superseded exemption), not a genuine "
    "sourcing problem. See docs/KNOWN_ISSUES.md (F72) for the full finding. "
    "Recorded manually per Sebastian's explicit authorization."
)

REAL_SEND_TS = {
    "morning": "2026-08-27T02:44:00Z",
    "evening": "2026-08-27T02:45:00Z",
}


def _atomic_write(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _attribution_fields(pkg: dict) -> dict:
    return {
        "topic_class": pkg.get("topic_class"),
        "topic_signals": pkg.get("topic_signals", []) or [],
        "series": pkg.get("series"),
        "hook_family": pkg.get("hook_family"),
        "hook_line": pkg.get("hook_line"),
        "funnel_status": pkg.get("funnel_status"),
        "question_line": pkg.get("question_line"),
        "cta_line": pkg.get("cta_line"),
        "loop_line": pkg.get("loop_line"),
        "vo": pkg.get("vo"),
    }


def _event_row(pkg: dict, manifest: dict) -> dict:
    date_sent = REAL_SEND_TS[pkg["slot"]]
    return {
        "event": "sent",
        "cron": CRON_ID,
        "batch_id": manifest.get("batch_id"),
        "corrects_batch_id": manifest.get("corrects_batch_id"),
        "package_id": pkg.get("package_id"),
        "slot": pkg.get("slot"),
        "date_sent": date_sent,
        "post_date": manifest.get("post_date"),
        "show": pkg.get("show"),
        "angle": pkg.get("angle"),
        "format_type": pkg.get("format_type"),
        "format_reason": pkg.get("format_reason", "") or "",
        "correction_reason": pkg.get("correction_reason"),
        "title": pkg.get("youtube_title"),
        "tiktok_title": pkg.get("tiktok_title"),
        "traction_tier": pkg.get("traction_tier", "") or "",
        "gap_type": pkg.get("gap_type", "") or "",
        "fact_count": len(pkg.get("sources", []) or []),
        "vo_draft_included": bool(pkg.get("vo")),
        "vo_word_count": pkg.get("vo_word_count"),
        **_attribution_fields(pkg),
        "status": "sent",
        "manual_log_note": MANUAL_NOTE,
    }


def _legacy_row(pkg: dict, manifest: dict) -> dict:
    date_sent = REAL_SEND_TS[pkg["slot"]]
    return {
        "date_sent": date_sent,
        "post_date": manifest.get("post_date"),
        "slot": pkg.get("slot"),
        "show": pkg.get("show"),
        "angle": pkg.get("angle"),
        "format_type": pkg.get("format_type"),
        "format_reason": pkg.get("format_reason", "") or "",
        "correction_reason": pkg.get("correction_reason"),
        "title": pkg.get("youtube_title"),
        "tiktok_title": pkg.get("tiktok_title"),
        "traction_tier": pkg.get("traction_tier", "") or "",
        "gap_type": pkg.get("gap_type", "") or "",
        "fact_count": len(pkg.get("sources", []) or []),
        "vo_draft_included": bool(pkg.get("vo")),
        "vo_word_count": pkg.get("vo_word_count"),
        "batch_id": manifest.get("batch_id"),
        "corrects_batch_id": manifest.get("corrects_batch_id"),
        "package_id": pkg.get("package_id"),
        **_attribution_fields(pkg),
        "status": "sent",
        "manual_log_note": MANUAL_NOTE,
    }


def main() -> int:
    manifest_path = os.path.join(PENDING_DIR, "run_manifest.json")
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    pkgs = manifest.get("packages", [])
    assert len(pkgs) == 2, f"expected 2 packages, got {len(pkgs)}"
    batch_id = manifest.get("batch_id")
    assert batch_id == BATCH_ID

    events_path = os.path.join(TREE, "cron_tracking", "sent_scripts_events.jsonl")
    legacy_path = os.path.join(TREE, "sent_scripts_log.json")

    # dedup check -- never double-append
    existing_keys = set()
    if os.path.exists(events_path):
        with open(events_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                existing_keys.add((row.get("batch_id"), row.get("package_id")))

    new_rows = [_event_row(p, manifest) for p in pkgs
                if (batch_id, p.get("package_id")) not in existing_keys]
    if new_rows:
        blob = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new_rows)
        with open(events_path, "a", encoding="utf-8") as fh:
            fh.write(blob)
            fh.flush()
            os.fsync(fh.fileno())
    print(f"[events] appended {len(new_rows)} row(s) to {events_path}")

    with open(legacy_path, encoding="utf-8") as fh:
        legacy = json.load(fh)
    existing_legacy = {(r.get("batch_id"), r.get("package_id"))
                        for r in legacy if isinstance(r, dict)}
    legacy_added = 0
    for p in pkgs:
        key = (batch_id, p.get("package_id"))
        if key in existing_legacy:
            continue
        legacy.append(_legacy_row(p, manifest))
        existing_legacy.add(key)
        legacy_added += 1
    if legacy_added:
        _atomic_write(legacy_path, json.dumps(legacy, indent=2, ensure_ascii=False))
    print(f"[legacy] appended {legacy_added} row(s) to {legacy_path}, total now {len(legacy)}")

    # top-level state.json -- terminal "sent" status (not the script's own
    # "success" string, to keep this manually-written record visually
    # distinct in a diff review; but see NOTE below for _confirmed_send_exists
    # compatibility, which requires literally "success").
    top_state_path = os.path.join(TREE, "cron_tracking", CRON_ID, "state.json")
    state = {
        "cron_id": CRON_ID,
        "workflow": "combined_daily_dual_package",
        "batch_id": batch_id,
        "run_ts": REAL_SEND_TS["evening"],
        "post_date": manifest.get("post_date"),
        "status": "success",
        "emails_sent": True,
        "log_appended": True,
        "git_pushed": False,
        "error": None,
        "manually_logged": True,
        "manual_log_reason": MANUAL_NOTE,
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
    _atomic_write(top_state_path, json.dumps(state, indent=2, ensure_ascii=False))
    print(f"[state] wrote top-level {top_state_path} with status=success")

    # per-batch pending state.json mirror (same shape as mirror_pending_state())
    pending_state_path = os.path.join(PENDING_DIR, "state.json")
    existing_pending = {}
    try:
        with open(pending_state_path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            existing_pending = loaded
    except (OSError, json.JSONDecodeError):
        existing_pending = {}
    merged = dict(existing_pending)
    merged.update({
        "status": "sent",
        "emails_sent": True,
        "log_appended": True,
        "git_pushed": False,
        "error": None,
        "batch_id": batch_id,
        "terminal_state_written_at": REAL_SEND_TS["evening"],
        "terminal_state_written_by": "tools/_manual_log_9a7d935f.py (manual, F72 gate gap)",
        "manually_logged": True,
        "manual_log_reason": MANUAL_NOTE,
    })
    _atomic_write(pending_state_path, json.dumps(merged, indent=2, ensure_ascii=False))
    print(f"[state] wrote per-batch pending mirror {pending_state_path} with status=sent")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

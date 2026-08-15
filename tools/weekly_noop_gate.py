#!/usr/bin/env python3
"""Deterministic early no-op gate for the weekly analytics cron (credit-safe mode).

Called by cron_analytics_runtime.txt AFTER STEP ZERO (GitHub restore) but BEFORE any
model-heavy work: before discovering/calling the YouTube connectors and before invoking
Sonnet synthesis or building/sending the email. It answers ONE cheap deterministic
question: has anything actually been PUBLISHED since the last successful weekly run?

  - "Published" is read ONLY from cron_tracking/publication_ledger.jsonl (event="published"
    rows with a real 11-char youtube_video_id). The sent log is NOT publication proof and
    is never consulted here.
  - The "cutoff" is the set of youtube_video_ids the last SUCCESSFUL full analytics run
    recorded in cron_tracking/2bb28991/state.json under `analytics_processed_video_ids`.

DECISION (exit code is the machine contract):
  EXIT_NOOP (0)      — zero NEW published video IDs since the cutoff. The gate writes a
                       small atomic no-op summary + state touch and the caller MUST skip
                       connectors, model synthesis, and email, then exit successfully.
  EXIT_RUN_FULL (10) — proceed with the full existing analytics workflow. Emitted when
                       there ARE new published IDs, OR when the decision cannot be made
                       confidently (state missing / corrupt / no cutoff recorded / any
                       exception). This FAILS OPEN to a full run so historical missing
                       state can never be mistaken for a legitimate no-op.

Only an explicit, confident zero-new-IDs result skips work. Everything else runs full.

Usage:
    python3 tools/weekly_noop_gate.py \
        --tree /home/user/workspace/repo [--now ISO8601]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any

CRON_ID = "2bb28991"
EXIT_NOOP = 0
EXIT_RUN_FULL = 10

# A real YouTube video id is 11 chars from the URL-safe base64 alphabet.
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


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


def published_video_ids(ledger_path: str) -> set[str]:
    """Distinct, VALID youtube_video_ids from event="published" ledger rows.

    Malformed JSON lines, non-published events, and missing/invalid video ids are
    skipped silently (they are not publication proof). Duplicates collapse to one id.
    A missing ledger file yields an empty set (nothing published yet)."""
    ids: set[str] = set()
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict) or row.get("event") != "published":
                    continue
                vid = row.get("youtube_video_id")
                if isinstance(vid, str) and _VIDEO_ID_RE.match(vid):
                    ids.add(vid)
    except OSError:
        pass
    return ids


def load_cutoff(state_path: str) -> tuple[set[str] | None, str]:
    """Return (processed_ids, reason).

    processed_ids is None when the cutoff cannot be established confidently — the caller
    MUST then run full (fail open). It is a (possibly empty) set only when the last
    successful run recorded a well-formed `analytics_processed_video_ids` list."""
    if not os.path.exists(state_path):
        return None, "no weekly state.json — full run"
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        return None, f"weekly state.json unreadable/corrupt ({e}) — full run"
    if not isinstance(state, dict):
        return None, "weekly state.json is not an object — full run"
    if "analytics_processed_video_ids" not in state:
        # historical state written before this field existed -> never a valid no-op
        return None, "no analytics_processed_video_ids cutoff recorded — full run"
    raw = state.get("analytics_processed_video_ids")
    if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
        return None, "analytics_processed_video_ids malformed — full run"
    return {x for x in raw if _VIDEO_ID_RE.match(x)}, "cutoff loaded"


def write_noop(state_path: str, summary_path: str, *, now: str,
               published_count: int, processed_count: int) -> None:
    """Small atomic no-op record: bump last_run, mark the run as a no-op, and preserve
    the existing cutoff (no new IDs means the processed set is unchanged)."""
    try:
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state, dict):
            state = {}
    except (OSError, json.JSONDecodeError):
        state = {}
    state["last_run"] = now
    state["last_run_mode"] = "noop"
    state["last_noop_ts"] = now
    state["run_count"] = int(state.get("run_count", 0)) + 1
    _atomic_write(state_path, json.dumps(state, indent=2, ensure_ascii=False))

    summary = {
        "cron_id": CRON_ID,
        "decision": "noop",
        "reason": "zero new published video IDs since last successful analytics run",
        "ts": now,
        "new_video_ids": 0,
        "published_ids_seen": published_count,
        "processed_ids_cutoff": processed_count,
        "connectors_called": False,
        "model_synthesis": False,
        "email_sent": False,
    }
    _atomic_write(summary_path, json.dumps(summary, indent=2, ensure_ascii=False))


def decide(tree: str, now: str) -> tuple[int, dict[str, Any]]:
    """Pure-ish decision + side effects (writes only on NOOP). Returns (exit_code, info)."""
    ledger_path = os.path.join(tree, "cron_tracking", "publication_ledger.jsonl")
    state_path = os.path.join(tree, "cron_tracking", CRON_ID, "state.json")
    summary_path = os.path.join(tree, "cron_tracking", CRON_ID, "last_noop_summary.json")

    published = published_video_ids(ledger_path)
    processed, reason = load_cutoff(state_path)

    if processed is None:
        # cannot establish a trustworthy cutoff -> full run (never a wrong no-op)
        return EXIT_RUN_FULL, {"decision": "run_full", "reason": reason,
                               "published_ids_seen": len(published),
                               "new_video_ids": sorted(published)}

    new_ids = published - processed
    if new_ids:
        return EXIT_RUN_FULL, {"decision": "run_full",
                               "reason": f"{len(new_ids)} new published video ID(s) since last run",
                               "published_ids_seen": len(published),
                               "processed_ids_cutoff": len(processed),
                               "new_video_ids": sorted(new_ids)}

    # confident no-op: nothing new published since the last successful run
    write_noop(state_path, summary_path, now=now,
               published_count=len(published), processed_count=len(processed))
    return EXIT_NOOP, {"decision": "noop",
                       "reason": "zero new published video IDs since last successful run",
                       "published_ids_seen": len(published),
                       "processed_ids_cutoff": len(processed),
                       "new_video_ids": []}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=os.getcwd(),
                    help="repo working tree root (default: cwd)")
    ap.add_argument("--now", default=None, help="override ISO timestamp (testing)")
    args = ap.parse_args(argv[1:])
    now = args.now or _now_iso()

    try:
        code, info = decide(args.tree, now)
    except Exception as e:  # noqa: BLE001 — never let an error cause a wrong no-op
        print(f"DECISION: RUN_FULL — gate error, failing open: {e}", file=sys.stderr)
        return EXIT_RUN_FULL

    if code == EXIT_NOOP:
        print(f"DECISION: NOOP — {info['reason']} "
              f"(published_seen={info['published_ids_seen']}, "
              f"cutoff={info['processed_ids_cutoff']}); "
              f"skip connectors/model/email")
    else:
        print(f"DECISION: RUN_FULL — {info['reason']} "
              f"(published_seen={info['published_ids_seen']}, "
              f"new={info.get('new_video_ids')})")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

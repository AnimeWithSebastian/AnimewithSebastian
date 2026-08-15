#!/usr/bin/env python3
"""Fail-closed publication-ledger writer (repairs the empty publication_ledger.jsonl gap).

WHY THIS EXISTS
cron_tracking/publication_ledger.schema.txt defines the ledger as the ONLY source of
truth for "a video is LIVE on YouTube," joined to the weekly analytics cron by real
youtube_video_id. Nothing in the repo ever wrote to it -- no automated upload step
exists (uploads are done manually by the channel owner after receiving the emailed
package), so the ledger has been empty since baseline. This tool is the missing,
deliberate write path. It NEVER infers, searches, or title-matches; it only records a
publication that has already been independently verified as real.

FAIL-CLOSED CONTRACT (every one of these blocks the write; there is no override flag)
  1. --youtube-video-id must be a syntactically real YouTube id (11 chars, URL-safe
     base64 alphabet). Garbage input is rejected before anything else runs.
  2. --package-id must reference a package that was ACTUALLY sent, i.e. it must exist
     in cron_tracking/sent_scripts_events.jsonl. You cannot publish a package that was
     never produced. Title is NEVER used to find or confirm this -- package_id is the
     only lookup key.
  3. --verified-metadata-file must be supplied: a JSON file holding a real YouTube Data
     API videos.list response (or the relevant subset: id, snippet.publishedAt,
     snippet.title, status.privacyStatus) for EXACTLY this youtube_video_id, fetched by
     the caller from the live API immediately before calling this tool. The tool checks:
       - metadata["id"] (or metadata["items"][0]["id"]) equals --youtube-video-id
       - status.privacyStatus (if present) is "public" -- a private/unlisted/draft
         video is not yet a real publication and is rejected
     This makes the "real" requirement mechanically enforced, not just a comment: the
     tool refuses to write a ledger row unless it can see the API's own confirmation
     that this exact video id exists and is public. It does not call the network itself
     (kept deterministic/testable) -- the caller (human operator or a future automation
     step) is responsible for producing that file from a genuine API call, never by
     hand-writing plausible-looking JSON.

     F9 addition (2026-07-25): when the real videos.list API call is genuinely
     unavailable (e.g. a broken connector, confirmed and logged separately), a SECOND,
     independent path accepts direct human confirmation via YouTube's own interface
     instead: metadata["human_attestation"] = {"verified": true, "verifier": ...,
     "verified_at": ..., "verification_method": ...}. This is a DIFFERENT check on a
     DIFFERENT field, checked by different code -- it is never a fallback that silently
     satisfies the status.privacyStatus check, the two are never blended into one field,
     and a partial/incomplete human_attestation block is rejected exactly like a missing
     status block. Critically, this path is usable ONLY when the API signal is genuinely
     absent or inconclusive (no status block, or a status block with no privacyStatus
     value) -- NEVER when status is present and explicitly disagrees (e.g. an actual
     "private"/"unlisted" value). A present, explicit non-public status is real evidence
     and is rejected outright even if a complete human_attestation is also supplied; the
     human path only fills in for a missing signal, never overrides a disagreeing one.
     Whichever path actually granted the confirmation is recorded on the resulting
     ledger row as verification_source ("api" | "human") so it is never ambiguous later
     which kind of confirmation backs a given row.
  4. No duplicate youtube_video_id may already have a "published" row in the ledger
     (one real video is recorded once).
  5. No package_id may already have a "published" row in the ledger (one package maps
     to at most one published video; if a correction is genuinely needed, that is a
     separate, explicit human decision outside this tool's scope -- it never silently
     overwrites).
  6. Never matches or infers by title, show name, date, or slot at any point.

On success, appends exactly one JSON line (event="published") to
cron_tracking/publication_ledger.jsonl, atomically-safe via a single buffered append +
fsync (append-only, matching the schema's git-merge-safety design). Never rewrites
existing lines.

Usage:
    python3 tools/record_publication.py \\
        --tree /home/user/workspace/repo \\
        --package-id 40fd3ec9-3e53-409e-9e48-06353ba9b239 \\
        --youtube-video-id Lgs9rCEirnU \\
        --verified-metadata-file /tmp/verified_Lgs9rCEirnU.json \\
        --objective REACH

Exit codes:
    0  -- published row appended
    20 -- rejected (see stderr for the specific fail-closed reason); nothing written
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from typing import Any

EXIT_OK = 0
EXIT_REJECTED = 20

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_VALID_OBJECTIVES = {"REACH", "ENGAGEMENT", "SUBSCRIBER_CONVERSION", "LONG_FORM_CONVERSION"}
_VALID_FORMATS = {"short", "long_form"}
_VALID_SLOTS = {"morning", "evening", None}


class RejectedError(Exception):
    """Raised for any fail-closed rejection. Message is the exact reason."""


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _append_line(path: str, line: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
        if not line.endswith("\n"):
            fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def validate_video_id(video_id: str) -> str:
    if not isinstance(video_id, str) or not _VIDEO_ID_RE.match(video_id):
        raise RejectedError(
            f"--youtube-video-id '{video_id}' is not a syntactically valid YouTube "
            "video id (must be exactly 11 chars, URL-safe base64 alphabet)"
        )
    return video_id


def load_sent_events(events_path: str) -> dict[str, dict[str, Any]]:
    """Map package_id -> most recent sent-event row, read from the real send log."""
    by_package: dict[str, dict[str, Any]] = {}
    try:
        with open(events_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict) or row.get("event") != "sent":
                    continue
                pkg_id = row.get("package_id")
                if isinstance(pkg_id, str) and pkg_id:
                    by_package[pkg_id] = row
    except OSError:
        pass
    return by_package


def load_ledger_rows(ledger_path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        pass
    return rows


def load_verified_metadata(metadata_path: str, expected_video_id: str) -> tuple[dict[str, Any], str]:
    """Load and validate a real YouTube Data API response for exactly this video id.

    Accepts either a raw videos.list response ({"items": [...]}) or a single flattened
    item ({"id": ..., "snippet": {...}, "status": {...}}). Rejects anything that does
    not carry a matching id and a public privacy status when that field is present.

    PUBLIC-STATUS CONFIRMATION HAS TWO INDEPENDENT, NON-BLENDED PATHS:
      (a) API path: item["status"]["privacyStatus"] == "public", from a real
          videos.list response.
      (b) Human-attestation path: a complete item["human_attestation"] block (see
          validate_human_attestation below), usable ONLY when the API signal is
          genuinely absent or inconclusive -- NEVER when status is present and
          explicitly disagrees. These two paths are never merged into one field or one
          check -- either is independently sufficient, but a present, disagreeing API
          status always wins and is rejected outright regardless of any human block.

    Returns (item, source) where source is "api" or "human" -- the caller records this
    on the ledger row so which kind of confirmation backs it is never ambiguous later.
    """
    try:
        with open(metadata_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as e:
        raise RejectedError(f"--verified-metadata-file could not be read: {e}") from e
    except json.JSONDecodeError as e:
        raise RejectedError(f"--verified-metadata-file is not valid JSON: {e}") from e

    if isinstance(data, dict) and "items" in data:
        items = data.get("items")
        if not isinstance(items, list) or len(items) != 1:
            raise RejectedError(
                "--verified-metadata-file videos.list response must contain exactly "
                f"one item for {expected_video_id}, got "
                f"{len(items) if isinstance(items, list) else 'non-list'}"
            )
        item = items[0]
    elif isinstance(data, dict):
        item = data
    else:
        raise RejectedError("--verified-metadata-file must be a JSON object")

    if not isinstance(item, dict) or item.get("id") != expected_video_id:
        raise RejectedError(
            f"--verified-metadata-file id does not match --youtube-video-id "
            f"{expected_video_id} (this tool never assumes a match -- the API "
            "response must confirm it explicitly)"
        )

    # F8 fix (production-audit finding, 2026-07-25): metadata with NO 'status' block
    # at all previously skipped this gate entirely and passed -- "cannot confirm
    # public" was silently treated the same as "confirmed public". This tool's whole
    # design is fail-closed (never assume; require explicit confirmation), so a
    # missing or incomplete status block must now be a rejection, not a bypass.
    #
    # F9 addition (2026-07-25): a SECOND, independent confirmation path was added
    # below for when the real videos.list API call is unavailable (e.g. a broken
    # connector) but a human has directly confirmed public status via YouTube's own
    # interface. This is a DIFFERENT check on a DIFFERENT field -- never a fallback
    # that silently satisfies the API check, and never blended into status.privacyStatus.
    #
    # Corrected during design review (2026-07-25, same day): the human path must be
    # usable ONLY when the API signal is genuinely INCONCLUSIVE (status absent, or a
    # dict with privacyStatus missing/null) -- never when status is PRESENT and
    # EXPLICITLY disagrees (e.g. privacyStatus == "private"/"unlisted"). A present,
    # explicit non-public status is real evidence, not an absence of evidence, and a
    # human attestation must never be allowed to silently override disagreeing
    # evidence -- only to fill in when there is none. Concrete failure mode this
    # prevents: a stale human_attestation left over from when a video really was
    # public, sitting alongside a fresh, working API call that now correctly reports
    # the video was taken down or set private -- the human block must NOT win there.
    status = item.get("status")
    api_confirmed = isinstance(status, dict) and status.get("privacyStatus") == "public"
    api_present_and_disagrees = (
        isinstance(status, dict)
        and status.get("privacyStatus") is not None
        and status.get("privacyStatus") != "public"
    )

    attestation_block = item.get("human_attestation")
    human_confirmed = False
    human_rejection_reason: str | None = None
    if attestation_block is not None and not api_present_and_disagrees:
        human_confirmed, human_rejection_reason = validate_human_attestation(attestation_block)

    if not api_confirmed and not human_confirmed:
        if api_present_and_disagrees:
            # Explicit disagreement: a real, present API status says non-public. This
            # is a conflict to surface and resolve, never something a human block can
            # silently override -- report it as a conflict even when a complete
            # human_attestation block was also supplied.
            conflict_note = (
                " (a human_attestation block was also present but is not permitted "
                "to override an explicit, present, disagreeing API status)"
                if attestation_block is not None
                else ""
            )
            raise RejectedError(
                f"video {expected_video_id} verified metadata explicitly shows "
                f"privacyStatus={status.get('privacyStatus')!r}, not 'public' -- "
                "this is a real, present API signal that disagrees, not an absence "
                f"of a signal, and is rejected outright{conflict_note}"
            )
        if attestation_block is not None and human_rejection_reason:
            # A human_attestation block was attempted but is incomplete -- surface
            # THAT reason, not the generic API message, so a partial attestation
            # fails loudly rather than silently falling through.
            raise RejectedError(
                f"video {expected_video_id} human_attestation block is invalid: "
                f"{human_rejection_reason} -- this tool never assumes public when it "
                "cannot verify; the block must be complete or omitted entirely"
            )
        raise RejectedError(
            f"video {expected_video_id} verified metadata shows privacyStatus is "
            f"not 'public' (status={status!r}) and no valid human_attestation "
            "block was supplied -- this tool never assumes public when it cannot "
            "verify; the metadata file must explicitly include either "
            "status.privacyStatus == 'public' (from a real API response) or a "
            "complete human_attestation block"
            )

    return item, ("api" if api_confirmed else "human")


_REQUIRED_HUMAN_ATTESTATION_FIELDS = (
    "verifier",
    "verified_at",
    "verification_method",
)


def validate_human_attestation(block: Any) -> tuple[bool, str | None]:
    """Validate a human_attestation block.

    Returns (True, None) only when the block is COMPLETE: verified is literally True,
    and all three sibling fields (verifier, verified_at, verification_method) are
    present as non-empty strings. Any partial block (e.g. verified: true with no
    verifier/timestamp) returns (False, <reason>) -- it must never silently satisfy
    the gate.
    """
    if not isinstance(block, dict):
        return False, "human_attestation must be an object, not a bare boolean or other type"
    if block.get("verified") is not True:
        return False, "human_attestation.verified must be exactly `true`"
    missing = [
        f for f in _REQUIRED_HUMAN_ATTESTATION_FIELDS
        if not isinstance(block.get(f), str) or not block.get(f).strip()
    ]
    if missing:
        return False, f"missing or empty required field(s): {', '.join(missing)}"
    return True, None


def build_row(
    *,
    package_row: dict[str, Any],
    video_id: str,
    verified_item: dict[str, Any],
    verification_source: str,
    now: str,
    objective: str,
    fmt: str,
    related_video_id: str | None,
    notes: str | None,
) -> dict[str, Any]:
    snippet = verified_item.get("snippet") if isinstance(verified_item.get("snippet"), dict) else {}
    publish_ts = snippet.get("publishedAt") or now
    real_title = snippet.get("title")

    slot = package_row.get("slot")
    if slot not in _VALID_SLOTS:
        slot = None

    is_short = fmt == "short"
    url = (
        f"https://www.youtube.com/shorts/{video_id}"
        if is_short
        else f"https://www.youtube.com/watch?v={video_id}"
    )

    return {
        "event": "published",
        "package_id": package_row.get("package_id"),
        "youtube_video_id": video_id,
        "youtube_url": url,
        "publish_ts": publish_ts,
        "format": fmt,
        "slot": slot,
        "show": package_row.get("show"),
        "angle": package_row.get("angle"),
        "objective": objective,
        "verification_source": verification_source,
        "runtime_sec": package_row.get("total_clip_time_sec") or package_row.get("runtime_sec"),
        "hook": package_row.get("hook_line"),
        "cta": package_row.get("cta_line") or "Leave your take.",
        "loop": package_row.get("loop_line"),
        # Law #85/#145 addendum (2026-07-27): related_video_id replaces the old
        # related_video_used boolean, which recorded intent, not outcome, and was
        # never true across any of 166 real sends. This records the actual selected
        # video ID (or null if none), so real usage rate is a real, checkable number.
        "related_video_id": related_video_id,
        "title": real_title if real_title is not None else package_row.get("title"),
        "notes": notes,
        "recorded_ts": now,
        "recorded_by": "tools/record_publication.py",
    }


def record_publication(
    tree: str,
    *,
    package_id: str,
    video_id: str,
    metadata_path: str,
    objective: str,
    fmt: str,
    related_video_id: str | None,
    notes: str | None,
    now: str | None = None,
) -> dict[str, Any]:
    """Full fail-closed pipeline. Raises RejectedError on any violation; writes nothing
    unless every check passes. Returns the appended row on success."""
    now = now or _now_iso()

    if objective not in _VALID_OBJECTIVES:
        raise RejectedError(
            f"--objective '{objective}' must be one of {sorted(_VALID_OBJECTIVES)}"
        )
    if fmt not in _VALID_FORMATS:
        raise RejectedError(f"--format '{fmt}' must be one of {sorted(_VALID_FORMATS)}")

    video_id = validate_video_id(video_id)

    if related_video_id is not None:
        related_video_id = related_video_id.strip() or None
    if related_video_id is not None and related_video_id == video_id:
        raise RejectedError(
            "related_video_id must not equal the video being published -- a video "
            "cannot be its own Related Video"
        )

    events_path = os.path.join(tree, "cron_tracking", "sent_scripts_events.jsonl")
    sent_by_package = load_sent_events(events_path)
    package_row = sent_by_package.get(package_id)
    if package_row is None:
        raise RejectedError(
            f"package_id '{package_id}' has no 'sent' event in "
            f"{events_path} -- refusing to publish a package that was never sent "
            "(package_id is the only lookup key; title is never used)"
        )

    verified_item, verification_source = load_verified_metadata(metadata_path, video_id)

    ledger_path = os.path.join(tree, "cron_tracking", "publication_ledger.jsonl")
    existing_rows = load_ledger_rows(ledger_path)
    for row in existing_rows:
        if row.get("event") != "published":
            continue
        if row.get("youtube_video_id") == video_id:
            raise RejectedError(
                f"youtube_video_id '{video_id}' already has a published row in the "
                "ledger -- refusing to write a duplicate"
            )
        if row.get("package_id") == package_id:
            raise RejectedError(
                f"package_id '{package_id}' already has a published row in the "
                f"ledger (video {row.get('youtube_video_id')}) -- refusing to "
                "silently overwrite; a correction requires an explicit separate "
                "human decision outside this tool"
            )

    new_row = build_row(
        package_row=package_row,
        video_id=video_id,
        verified_item=verified_item,
        verification_source=verification_source,
        now=now,
        objective=objective,
        fmt=fmt,
        related_video_id=related_video_id,
        notes=notes,
    )

    _append_line(ledger_path, json.dumps(new_row, ensure_ascii=False))
    return new_row


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tree", default=os.getcwd(), help="repo working tree root")
    ap.add_argument("--package-id", required=True)
    ap.add_argument("--youtube-video-id", required=True)
    ap.add_argument(
        "--verified-metadata-file",
        required=True,
        help="path to a JSON file holding a real YouTube Data API videos.list "
        "response (or single item) fetched live for this exact video id",
    )
    ap.add_argument(
        "--objective",
        default="REACH",
        choices=sorted(_VALID_OBJECTIVES),
    )
    ap.add_argument("--format", dest="fmt", default="short", choices=sorted(_VALID_FORMATS))
    ap.add_argument(
        "--related-video-id", default=None,
        help="YouTube video ID selected as this package's Related Video, if any "
        "(optional -- omit or leave unset when no qualifying prior video exists)",
    )
    ap.add_argument("--notes", default=None)
    ap.add_argument("--now", default=None, help="override ISO timestamp (testing)")
    args = ap.parse_args(argv[1:])

    try:
        row = record_publication(
            args.tree,
            package_id=args.package_id,
            video_id=args.youtube_video_id,
            metadata_path=args.verified_metadata_file,
            objective=args.objective,
            fmt=args.fmt,
            related_video_id=args.related_video_id,
            notes=args.notes,
            now=args.now,
        )
    except RejectedError as e:
        print(f"REJECTED: {e}", file=sys.stderr)
        return EXIT_REJECTED

    print(
        f"PUBLISHED recorded: package_id={row['package_id']} "
        f"youtube_video_id={row['youtube_video_id']} url={row['youtube_url']}"
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

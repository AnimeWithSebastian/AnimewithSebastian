#!/usr/bin/env python3
"""Convenience wrapper around record_publication.py (added July 24, 2026).

WHY THIS EXISTS
package_id is never shown in the actual production email (it's manifest-only, per
templates/package_template.txt's "NOT IN THE EMAIL" section) -- so requiring a
channel owner to hand-type a raw UUID after every real upload isn't usable in
practice. What the email DOES show is the show name and post date (subject line:
"TOMORROW | MORNING | [Show] | [Post Date] | [Title]"). This wrapper lets you look
the package_id up by --show/--post-date instead of copying a UUID, or list recent
sent-but-unpublished packages with --list.

WHAT THIS TOOL DOES NOT DO
This wrapper does not weaken, skip, or soften a single one of record_publication.py's
fail-closed checks (video-id format, sent-event existence, verified-metadata id/public-
status match, no-duplicate-video, no-duplicate-package). It calls record_publication()
UNMODIFIED, with the resolved package_id passed straight through, exactly as if you
had typed that package_id yourself on the record_publication.py command line. Every
rejection path, error message, and exit code is byte-identical to running
record_publication.py directly.

**THE --show/--post-date LOOKUP IS A CONVENIENCE FILTER ONLY -- IT IS NOT PART OF THE
REAL VALIDATION.** record_publication.py's own governing principle is "Never matches
or infers by title, show name, date, or slot at any point" for the actual publish
write, and that is unchanged here: the write path still keys ONLY on package_id and
youtube_video_id. The --show/--post-date match that THIS wrapper performs exists
solely to narrow down which package_id to hand to that unchanged write path -- it is
a case-insensitive SUBSTRING match on --show (not exact, not fuzzy-typo-tolerant)
combined with an exact match on --post-date, read from
cron_tracking/sent_scripts_events.jsonl (the same sent-event log record_publication.py
itself already reads for its "was this package actually sent" check).

This repo already has two different show-name strings that arguably refer to the same
show ("Bleach: Thousand-Year Blood War - The Calamity" vs "Bleach TYBW Part 4 -- The
Calamity") -- proof that title strings are not a reliable unique key. So substring
match is intentionally loose: it is designed to OVER-match and surface every plausible
candidate into an interactive picker, never to silently resolve to a single row on a
guess. Any time the lookup finds zero or more than one candidate, or ANY ambiguity is
possible, it prints the candidates (package_id, slot, post_date, batch_id, show) and
prompts for an explicit selection -- it never auto-picks among multiple matches. A
single unambiguous match still requires no confirmation prompt, but the resolved
package_id is always printed before it is used, so the choice is visible.

Usage:
    # Typical case -- resolves package_id automatically from show + post date shown
    # in the email, then delegates to record_publication.py's unmodified checks.
    python3 tools/mark_published.py \\
        --tree /home/user/workspace/repo \\
        --show "Black Lagoon / Crunchyroll Library Removals" \\
        --post-date 2026-07-25 \\
        --youtube-video-id dQw4w9WgXcQ \\
        --verified-metadata-file /tmp/verified_dQw4w9WgXcQ.json \\
        --objective REACH

    # Ambiguous match -- drops into an interactive picker instead of guessing.
    python3 tools/mark_published.py \\
        --tree /home/user/workspace/repo \\
        --show "Bleach" --post-date 2026-07-24 \\
        --youtube-video-id dQw4w9WgXcQ \\
        --verified-metadata-file /tmp/verified_dQw4w9WgXcQ.json

    # Discovery mode -- list every sent package with no matching published row yet.
    python3 tools/mark_published.py --tree /home/user/workspace/repo --list

Exit codes (identical meaning to record_publication.py):
    0  -- published row appended
    20 -- rejected by record_publication.py's fail-closed checks; nothing written
    2  -- this wrapper's own lookup could not resolve a package_id (no match, or
          user declined/failed to pick from an ambiguous list); record_publication.py
          was never invoked, nothing written
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

# Import the real, unmodified validation pipeline. This wrapper never reimplements or
# relaxes any of record_publication.py's fail-closed logic -- it only resolves
# --package-id for it.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record_publication as rp  # noqa: E402

EXIT_OK = 0
EXIT_REJECTED = 20
EXIT_LOOKUP_FAILED = 2


def _events_path(tree: str) -> str:
    return os.path.join(tree, "cron_tracking", "sent_scripts_events.jsonl")


def _ledger_path(tree: str) -> str:
    return os.path.join(tree, "cron_tracking", "publication_ledger.jsonl")


def load_sent_rows(events_path: str) -> list[dict[str, Any]]:
    """F12 fix (production-audit finding, 2026-07-25): corrected doc -- this
    previously claimed rows were "collapsed to the LAST occurrence", which
    contradicted its own next clause and did not match the actual code below.

    Every 'sent' row is returned AS-IS, with NO deduplication or collapsing by
    package_id (unlike record_publication.load_sent_events' package_id -> row
    semantics). Kept as a full list here so --list and the picker can show every
    distinct sent package_id, including reused show titles across batches."""
    rows: list[dict[str, Any]] = []
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
                if isinstance(row, dict) and row.get("event") == "sent":
                    rows.append(row)
    except OSError:
        pass
    return rows


def load_published_package_ids(ledger_path: str) -> set[str]:
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
                if isinstance(row, dict) and row.get("event") == "published":
                    pkg_id = row.get("package_id")
                    if isinstance(pkg_id, str):
                        ids.add(pkg_id)
    except OSError:
        pass
    return ids


def unpublished_sent_rows(tree: str) -> list[dict[str, Any]]:
    """All sent rows whose package_id has no 'published' ledger row yet."""
    sent = load_sent_rows(_events_path(tree))
    published_ids = load_published_package_ids(_ledger_path(tree))
    return [r for r in sent if r.get("package_id") not in published_ids]


def find_candidates(tree: str, show: str, post_date: str) -> list[dict[str, Any]]:
    """CONVENIENCE FILTER ONLY -- see module docstring. Case-insensitive substring
    match on --show, exact match on --post-date, restricted to sent packages that are
    not already published. Never used by the actual write path (package_id and
    youtube_video_id remain the only real keys, enforced inside record_publication.py
    unchanged)."""
    needle = show.strip().lower()
    candidates = []
    for row in unpublished_sent_rows(tree):
        row_show = str(row.get("show") or "")
        row_post_date = str(row.get("post_date") or "")
        if needle in row_show.lower() and row_post_date == post_date:
            candidates.append(row)
    return candidates


def _print_candidates(rows: list[dict[str, Any]], numbered: bool) -> None:
    for i, row in enumerate(rows, start=1):
        prefix = f"  [{i}] " if numbered else "  - "
        print(
            f"{prefix}package_id={row.get('package_id')} slot={row.get('slot')} "
            f"post_date={row.get('post_date')} batch={row.get('batch_id')} "
            f"show={row.get('show')!r}"
        )


def resolve_package_id(
    tree: str, show: str, post_date: str, *, interactive: bool = True
) -> str | None:
    """Resolve a package_id from --show/--post-date. Returns None (never guesses) if
    zero matches, or if more than one match and the picker is declined/unavailable/
    invalid. Always prints the resolved (or candidate) rows before returning -- the
    choice is never silent."""
    candidates = find_candidates(tree, show, post_date)

    if not candidates:
        print(
            f"No unpublished 'sent' package matches show={show!r} "
            f"post_date={post_date!r} in {_events_path(tree)}.",
            file=sys.stderr,
        )
        print(
            "This is only a lookup-convenience miss -- re-check the show text/date "
            "exactly as shown in the email, or run --list to see every unpublished "
            "sent package.",
            file=sys.stderr,
        )
        return None

    if len(candidates) == 1:
        row = candidates[0]
        print(f"Resolved package_id={row.get('package_id')!r} from show/post-date match:")
        _print_candidates(candidates, numbered=False)
        return row.get("package_id")

    print(
        f"Multiple unpublished sent packages match show={show!r} post_date={post_date!r}:",
    )
    _print_candidates(candidates, numbered=True)

    if not interactive or not sys.stdin.isatty():
        print(
            "Ambiguous match and no interactive terminal available -- refusing to "
            "guess. Re-run with a more specific --show, or select manually via --list.",
            file=sys.stderr,
        )
        return None

    try:
        choice = input(f"Select [1-{len(candidates)}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nNo selection made -- aborting.", file=sys.stderr)
        return None

    if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
        print(f"Invalid selection {choice!r} -- aborting.", file=sys.stderr)
        return None

    return candidates[int(choice) - 1].get("package_id")


def cmd_list(tree: str) -> int:
    rows = unpublished_sent_rows(tree)
    if not rows:
        print("No unpublished sent packages found.")
        return EXIT_OK
    print(f"{len(rows)} sent package(s) with no matching published row yet:")
    _print_candidates(rows, numbered=False)
    return EXIT_OK


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tree", default=os.getcwd(), help="repo working tree root")
    ap.add_argument(
        "--list",
        action="store_true",
        help="list every sent package with no matching published row yet, then exit",
    )
    ap.add_argument(
        "--show",
        default=None,
        help="show text as it appears in the email subject (convenience lookup only "
        "-- case-insensitive substring match, never used by the real write path)",
    )
    ap.add_argument(
        "--post-date",
        default=None,
        help="post date as it appears in the email subject, YYYY-MM-DD (convenience "
        "lookup only, exact match)",
    )
    ap.add_argument(
        "--package-id",
        default=None,
        help="skip the --show/--post-date lookup and pass this package_id straight "
        "through to record_publication.py (same as calling it directly)",
    )
    ap.add_argument("--youtube-video-id", default=None)
    ap.add_argument(
        "--verified-metadata-file",
        default=None,
        help="path to a JSON file holding a real YouTube Data API videos.list "
        "response (or single item) fetched live for this exact video id -- "
        "unchanged requirement, passed through to record_publication.py as-is",
    )
    ap.add_argument(
        "--objective",
        default="REACH",
        choices=sorted(rp._VALID_OBJECTIVES),
    )
    ap.add_argument("--format", dest="fmt", default="short", choices=sorted(rp._VALID_FORMATS))
    ap.add_argument(
        "--related-video-id", default=None,
        help="YouTube video ID selected as this package's Related Video, if any "
        "(optional)",
    )
    ap.add_argument("--notes", default=None)
    ap.add_argument("--now", default=None, help="override ISO timestamp (testing)")
    ap.add_argument(
        "--non-interactive",
        action="store_true",
        help="never prompt on an ambiguous match -- fail instead (for automation/tests)",
    )
    args = ap.parse_args(argv[1:])

    if args.list:
        return cmd_list(args.tree)

    if not args.youtube_video_id or not args.verified_metadata_file:
        print(
            "REJECTED: --youtube-video-id and --verified-metadata-file are required "
            "(unless --list is used)",
            file=sys.stderr,
        )
        return EXIT_LOOKUP_FAILED

    package_id = args.package_id
    if package_id is None:
        if not args.show or not args.post_date:
            print(
                "REJECTED: provide --package-id directly, OR both --show and "
                "--post-date for the convenience lookup",
                file=sys.stderr,
            )
            return EXIT_LOOKUP_FAILED
        package_id = resolve_package_id(
            args.tree, args.show, args.post_date, interactive=not args.non_interactive
        )
        if package_id is None:
            return EXIT_LOOKUP_FAILED

    # From here on, this is EXACTLY record_publication.py's own pipeline, unmodified.
    try:
        row = rp.record_publication(
            args.tree,
            package_id=package_id,
            video_id=args.youtube_video_id,
            metadata_path=args.verified_metadata_file,
            objective=args.objective,
            fmt=args.fmt,
            related_video_id=args.related_video_id,
            notes=args.notes,
            now=args.now,
        )
    except rp.RejectedError as e:
        print(f"REJECTED: {e}", file=sys.stderr)
        return EXIT_REJECTED

    print(
        f"PUBLISHED recorded: package_id={row['package_id']} "
        f"youtube_video_id={row['youtube_video_id']} url={row['youtube_url']}"
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

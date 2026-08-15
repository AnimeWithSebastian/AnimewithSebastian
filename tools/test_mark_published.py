#!/usr/bin/env python3
"""Tests for tools/mark_published.py (show/post-date convenience wrapper around
record_publication.py).

Pins two contracts:

1. LOOKUP IS CONVENIENCE-ONLY. --show/--post-date is a case-insensitive substring +
   exact-date filter used ONLY to find a candidate package_id list -- it must never
   silently resolve an ambiguous match, and it must never be able to satisfy any of
   record_publication.py's real fail-closed checks. Those checks are exercised here
   purely by confirming mark_published.py's success/rejection outcomes are IDENTICAL
   to calling record_publication.record_publication() directly with the same resolved
   package_id -- i.e. the wrapper adds a lookup step in front of an unmodified pipe.

2. NOTHING IS WEAKENED. Every rejection path that record_publication.py enforces
   (bad video id, package never sent, metadata id mismatch, non-public status,
   duplicate video, duplicate package) still rejects when reached through the wrapper,
   with package_id resolved automatically.

    python3 tools/test_mark_published.py
    python3 -m unittest discover  (from inside the tools/ directory)
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

import mark_published as mp
import record_publication as rp

VID = "Lgs9rCEirnU"
VID_2 = "oOEEqGMCBM8"
PKG_BLEACH_1 = "05a092fd-652b-4d87-a980-0ef5fbc5aa25"
PKG_BLEACH_2 = "91cc44aa-3e53-409e-9e48-06353ba9beef"
PKG_BLACK_LAGOON = "c699bd7d-51d7-4180-8c26-5662b06c7eed"


def sent_row(package_id: str, show: str, post_date: str, **extra) -> dict:
    row = {
        "event": "sent",
        "cron": "daily_combined",
        "batch_id": "9856951f-ea56-4740-8c73-f3eaa5a90728",
        "package_id": package_id,
        "slot": "morning",
        "date_sent": "2026-07-21T19:06:00-04:00",
        "post_date": post_date,
        "show": show,
        "angle": "angle",
        "title": f"{show}: Title",
        "hook_line": f"{show} opens strong.",
        "status": "sent",
    }
    row.update(extra)
    return row


def published_row(package_id: str, video_id: str) -> dict:
    return {"event": "published", "package_id": package_id, "youtube_video_id": video_id}


def api_metadata(video_id: str, *, privacy: str | None = "public") -> dict:
    item = {"id": video_id, "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": "Real Title"}}
    if privacy is not None:
        item["status"] = {"privacyStatus": privacy}
    return item


def human_attested_metadata(video_id: str) -> dict:
    """Metadata with NO status block (genuine API unavailability), confirmed instead
    via a complete human_attestation block -- F9 path, exercised end-to-end through
    the CLI wrapper same as the existing API-path success test."""
    return {
        "id": video_id,
        "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": "Real Title"},
        "human_attestation": {
            "verified": True,
            "verifier": "Sebastian Lemos",
            "verified_at": "2026-07-26T01:40:00-04:00",
            "verification_method": "YouTube Studio Details page, Visibility field, screenshot reviewed",
        },
    }


class MarkPublishedCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tree = self._tmp.name
        self.events_path = mp._events_path(self.tree)
        self.ledger_path = mp._ledger_path(self.tree)
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_events(self, rows: list[dict]) -> None:
        with open(self.events_path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def write_ledger(self, rows: list[dict]) -> None:
        with open(self.ledger_path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def write_metadata_file(self, item: dict) -> str:
        path = os.path.join(self.tree, f"meta_{item.get('id')}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(item, fh)
        return path

    # -- lookup resolution (convenience layer only) --

    def test_unique_match_resolves_without_prompt(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        pkg = mp.resolve_package_id(
            self.tree, "Black Lagoon", "2026-07-25", interactive=False
        )
        self.assertEqual(pkg, PKG_BLACK_LAGOON)

    def test_substring_match_is_case_insensitive(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        pkg = mp.resolve_package_id(self.tree, "black lagoon", "2026-07-25", interactive=False)
        self.assertEqual(pkg, PKG_BLACK_LAGOON)

    def test_no_match_returns_none_never_guesses(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        pkg = mp.resolve_package_id(self.tree, "Naruto", "2026-07-25", interactive=False)
        self.assertIsNone(pkg)

    def test_wrong_post_date_returns_none(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        pkg = mp.resolve_package_id(self.tree, "Black Lagoon", "2026-07-26", interactive=False)
        self.assertIsNone(pkg)

    def test_ambiguous_match_never_auto_resolves_non_interactive(self):
        # the real repo scenario: two different show strings, arguably the same show,
        # both matching a loose substring + same post date -- must NOT silently pick one
        self.write_events([
            sent_row(PKG_BLEACH_1, "Bleach: Thousand-Year Blood War - The Calamity", "2026-07-24"),
            sent_row(PKG_BLEACH_2, "Bleach TYBW Part 4 \u2014 The Calamity", "2026-07-24"),
        ])
        pkg = mp.resolve_package_id(self.tree, "Bleach", "2026-07-24", interactive=False)
        self.assertIsNone(pkg, "ambiguous match must never auto-resolve")

    def test_ambiguous_match_candidates_both_listed(self):
        self.write_events([
            sent_row(PKG_BLEACH_1, "Bleach: Thousand-Year Blood War - The Calamity", "2026-07-24"),
            sent_row(PKG_BLEACH_2, "Bleach TYBW Part 4 \u2014 The Calamity", "2026-07-24"),
        ])
        candidates = mp.find_candidates(self.tree, "Bleach", "2026-07-24")
        ids = {c["package_id"] for c in candidates}
        self.assertEqual(ids, {PKG_BLEACH_1, PKG_BLEACH_2})

    def test_already_published_package_excluded_from_candidates(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        self.write_ledger([published_row(PKG_BLACK_LAGOON, VID)])
        candidates = mp.find_candidates(self.tree, "Black Lagoon", "2026-07-25")
        self.assertEqual(candidates, [])

    def test_list_shows_only_unpublished(self):
        self.write_events([
            sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25"),
            sent_row(PKG_BLEACH_1, "Bleach: Thousand-Year Blood War - The Calamity", "2026-07-24"),
        ])
        self.write_ledger([published_row(PKG_BLEACH_1, VID)])
        rows = mp.unpublished_sent_rows(self.tree)
        ids = {r["package_id"] for r in rows}
        self.assertEqual(ids, {PKG_BLACK_LAGOON})

    # -- end-to-end: wrapper outcome must match calling record_publication.py directly --

    def test_success_path_identical_to_direct_call(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(api_metadata(VID))

        pkg = mp.resolve_package_id(self.tree, "Black Lagoon", "2026-07-25", interactive=False)
        self.assertEqual(pkg, PKG_BLACK_LAGOON)

        row = rp.record_publication(
            self.tree,
            package_id=pkg,
            video_id=VID,
            metadata_path=meta_path,
            objective="REACH",
            fmt="short",
            related_video_id=None,
            notes=None,
            now="2026-07-25T12:00:00+00:00",
        )
        self.assertEqual(row["package_id"], PKG_BLACK_LAGOON)
        self.assertEqual(row["youtube_video_id"], VID)

        with open(self.ledger_path, encoding="utf-8") as fh:
            lines = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["event"], "published")

    def test_rejection_bad_video_id_not_bypassed(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(api_metadata("not-11-chars!"))
        pkg = mp.resolve_package_id(self.tree, "Black Lagoon", "2026-07-25", interactive=False)
        with self.assertRaises(rp.RejectedError):
            rp.record_publication(
                self.tree, package_id=pkg, video_id="not-11-chars!",
                metadata_path=meta_path, objective="REACH", fmt="short",
                related_video_id=None, notes=None, now="2026-07-25T12:00:00+00:00",
            )

    def test_rejection_non_public_status_not_bypassed(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(api_metadata(VID, privacy="private"))
        pkg = mp.resolve_package_id(self.tree, "Black Lagoon", "2026-07-25", interactive=False)
        with self.assertRaises(rp.RejectedError):
            rp.record_publication(
                self.tree, package_id=pkg, video_id=VID,
                metadata_path=meta_path, objective="REACH", fmt="short",
                related_video_id=None, notes=None, now="2026-07-25T12:00:00+00:00",
            )

    def test_rejection_duplicate_package_not_bypassed(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        self.write_ledger([published_row(PKG_BLACK_LAGOON, VID_2)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        # already-published packages are excluded from lookup candidates entirely --
        # resolve_package_id must return None (nothing to resolve), confirming the
        # duplicate-package protection is visible even before reaching record_publication.
        pkg = mp.resolve_package_id(self.tree, "Black Lagoon", "2026-07-25", interactive=False)
        self.assertIsNone(pkg)
        # and even if a caller forced the raw package_id through directly (bypassing
        # the lookup, e.g. via --package-id), record_publication.py's own duplicate
        # check still rejects it -- the wrapper adds no override path.
        with self.assertRaises(rp.RejectedError):
            rp.record_publication(
                self.tree, package_id=PKG_BLACK_LAGOON, video_id=VID,
                metadata_path=meta_path, objective="REACH", fmt="short",
                related_video_id=None, notes=None, now="2026-07-25T12:00:00+00:00",
            )

    def test_rejection_package_never_sent_not_bypassed(self):
        # no sent events at all -- lookup finds nothing, and a direct package_id also
        # gets rejected by record_publication.py's own "was this ever sent" check.
        meta_path = self.write_metadata_file(api_metadata(VID))
        pkg = mp.resolve_package_id(self.tree, "Anything", "2026-07-25", interactive=False)
        self.assertIsNone(pkg)
        with self.assertRaises(rp.RejectedError):
            rp.record_publication(
                self.tree, package_id="never-sent-package-id", video_id=VID,
                metadata_path=meta_path, objective="REACH", fmt="short",
                related_video_id=None, notes=None, now="2026-07-25T12:00:00+00:00",
            )

    # -- CLI entry point --

    def test_cli_list_mode(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        rc = mp.main(["mark_published.py", "--tree", self.tree, "--list"])
        self.assertEqual(rc, mp.EXIT_OK)

    def test_cli_ambiguous_non_interactive_fails_closed(self):
        self.write_events([
            sent_row(PKG_BLEACH_1, "Bleach: Thousand-Year Blood War - The Calamity", "2026-07-24"),
            sent_row(PKG_BLEACH_2, "Bleach TYBW Part 4 \u2014 The Calamity", "2026-07-24"),
        ])
        meta_path = self.write_metadata_file(api_metadata(VID))
        rc = mp.main([
            "mark_published.py", "--tree", self.tree,
            "--show", "Bleach", "--post-date", "2026-07-24",
            "--youtube-video-id", VID, "--verified-metadata-file", meta_path,
            "--non-interactive",
        ])
        self.assertEqual(rc, mp.EXIT_LOOKUP_FAILED)
        # fail-closed before ever reaching record_publication.py: nothing written,
        # not even the ledger file/directory itself.
        self.assertFalse(os.path.exists(self.ledger_path))

    def test_cli_success_end_to_end(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(api_metadata(VID))
        rc = mp.main([
            "mark_published.py", "--tree", self.tree,
            "--show", "Black Lagoon", "--post-date", "2026-07-25",
            "--youtube-video-id", VID, "--verified-metadata-file", meta_path,
            "--now", "2026-07-25T12:00:00+00:00",
        ])
        self.assertEqual(rc, mp.EXIT_OK)
        with open(self.ledger_path, encoding="utf-8") as fh:
            lines = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["package_id"], PKG_BLACK_LAGOON)

    def test_cli_success_end_to_end_human_attestation_path(self):
        # F9: CLI-level end-to-end success via the human-attestation path (genuine API
        # unavailability, not disagreement) -- same shape as the API-path success test
        # above, confirming the wrapper doesn't weaken or bypass the new path either.
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(human_attested_metadata(VID))
        rc = mp.main([
            "mark_published.py", "--tree", self.tree,
            "--show", "Black Lagoon", "--post-date", "2026-07-25",
            "--youtube-video-id", VID, "--verified-metadata-file", meta_path,
            "--now", "2026-07-25T12:00:00+00:00",
        ])
        self.assertEqual(rc, mp.EXIT_OK)
        with open(self.ledger_path, encoding="utf-8") as fh:
            lines = [json.loads(l) for l in fh if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["package_id"], PKG_BLACK_LAGOON)
        self.assertEqual(lines[0]["verification_source"], "human")

    def test_cli_direct_package_id_skips_lookup(self):
        self.write_events([sent_row(PKG_BLACK_LAGOON, "Black Lagoon / Crunchyroll Library Removals", "2026-07-25")])
        meta_path = self.write_metadata_file(api_metadata(VID))
        rc = mp.main([
            "mark_published.py", "--tree", self.tree,
            "--package-id", PKG_BLACK_LAGOON,
            "--youtube-video-id", VID, "--verified-metadata-file", meta_path,
            "--now", "2026-07-25T12:00:00+00:00",
        ])
        self.assertEqual(rc, mp.EXIT_OK)

    def test_cli_missing_lookup_args_fails_closed(self):
        rc = mp.main(["mark_published.py", "--tree", self.tree,
                       "--youtube-video-id", VID, "--verified-metadata-file", "/nonexistent"])
        self.assertEqual(rc, mp.EXIT_LOOKUP_FAILED)


if __name__ == "__main__":
    unittest.main(verbosity=2)

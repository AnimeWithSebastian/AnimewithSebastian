#!/usr/bin/env python3
"""Tests for tools/record_publication.py (fail-closed publication-ledger writer).

Pins the contract: a "published" row is appended to the ledger ONLY when (1) the
video id is syntactically real, (2) the package_id has a genuine "sent" event on
record, (3) a real, matching, public-status API metadata file is supplied for that
exact video id, and (4) no conflicting row already exists for that video_id or
package_id. Every other input path must be REJECTED with nothing written -- this
suite exercises each rejection individually as well as the success path. No network
calls; the "verified metadata" is a caller-supplied JSON file standing in for a real
API response fetched before invocation. Runs against a throwaway tree only.

    python3 tools/test_record_publication.py
    python3 -m unittest discover  (from inside the tools/ directory)
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

import record_publication as rp

NOW = "2026-07-23T12:00:00+00:00"
VID = "Lgs9rCEirnU"  # real 11-char id used in this test suite
VID_2 = "oOEEqGMCBM8"
PKG = "40fd3ec9-3e53-409e-9e48-06353ba9b239"
PKG_2 = "f04d762f-d4cf-4b56-8b1b-ef5d8b35bc23"


def sent_event_row(package_id: str, **extra) -> dict:
    row = {
        "event": "sent",
        "cron": "daily_combined",
        "batch_id": "9856951f-ea56-4740-8c73-f3eaa5a90728",
        "package_id": package_id,
        "slot": "morning",
        "date_sent": "2026-07-21T19:06:00-04:00",
        "post_date": "2026-07-22",
        "show": "A Livid Lady's Guide to Getting Even",
        "angle": "political-takedown angle",
        "title": "A Livid Lady's Guide to Getting Even: The Political Takedown Behind the Revenge",
        "hook_line": "A Livid Lady's Guide to Getting Even isn't just revenge, it's a political takedown.",
        "status": "sent",
    }
    row.update(extra)
    return row


def api_metadata(video_id: str, *, privacy: str | None = "public", title: str = "Real Title") -> dict:
    item = {
        "id": video_id,
        "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": title},
    }
    if privacy is not None:
        item["status"] = {"privacyStatus": privacy}
    return item


def human_attestation_block(**overrides) -> dict:
    block = {
        "verified": True,
        "verifier": "Sebastian Lemos",
        "verified_at": "2026-07-26T01:40:00-04:00",
        "verification_method": "YouTube Studio Details page, Visibility field, screenshot reviewed",
    }
    block.update(overrides)
    return block


class RecordPublicationCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tree = self._tmp.name
        self.events_path = os.path.join(self.tree, "cron_tracking", "sent_scripts_events.jsonl")
        self.ledger_path = os.path.join(self.tree, "cron_tracking", "publication_ledger.jsonl")
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_events(self, rows: list[dict]) -> None:
        with open(self.events_path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def write_metadata_file(self, item: dict, *, as_list_response: bool = False) -> str:
        path = os.path.join(self.tree, f"meta_{item.get('id')}.json")
        payload = {"items": [item]} if as_list_response else item
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        return path

    def ledger_rows(self) -> list[dict]:
        if not os.path.exists(self.ledger_path):
            return []
        with open(self.ledger_path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def call(self, **kwargs):
        defaults = dict(
            tree=self.tree,
            package_id=PKG,
            video_id=VID,
            metadata_path=None,
            objective="REACH",
            fmt="short",
            related_video_id=None,
            notes=None,
            now=NOW,
        )
        defaults.update(kwargs)
        return rp.record_publication(defaults.pop("tree"), **defaults)


class TestSuccessPath(RecordPublicationCase):
    def test_valid_publication_is_recorded_exactly_once(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        row = self.call(metadata_path=meta_path)

        self.assertEqual(row["event"], "published")
        self.assertEqual(row["package_id"], PKG)
        self.assertEqual(row["youtube_video_id"], VID)
        self.assertEqual(row["youtube_url"], f"https://www.youtube.com/shorts/{VID}")
        self.assertEqual(row["publish_ts"], "2026-07-22T13:24:44Z")  # from real metadata, not `now`
        self.assertEqual(row["verification_source"], "api")
        rows = self.ledger_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["youtube_video_id"], VID)
        self.assertEqual(rows[0]["verification_source"], "api")

    def test_accepts_raw_videos_list_response_shape(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID), as_list_response=True)
        row = self.call(metadata_path=meta_path)
        self.assertEqual(row["youtube_video_id"], VID)

    def test_long_form_uses_watch_url_not_shorts(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        row = self.call(metadata_path=meta_path, fmt="long_form")
        self.assertEqual(row["youtube_url"], f"https://www.youtube.com/watch?v={VID}")

    def test_never_uses_title_as_a_lookup_key(self):
        # Package row has a completely different title than metadata; must still work,
        # proving package_id (not title) is the only join/lookup key.
        self.write_events([sent_event_row(PKG, title="Some Totally Different Title")])
        meta_path = self.write_metadata_file(api_metadata(VID, title="Yet Another Title"))
        row = self.call(metadata_path=meta_path)
        self.assertEqual(row["package_id"], PKG)


class TestRejections(RecordPublicationCase):
    def test_rejects_malformed_video_id_too_short(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata("short"))
        with self.assertRaisesRegex(rp.RejectedError, "not a syntactically valid"):
            self.call(video_id="short", metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_malformed_video_id_bad_chars(self):
        self.write_events([sent_event_row(PKG)])
        bad_id = "abc def!!!!"  # 11 chars but invalid charset/space
        meta_path = self.write_metadata_file(api_metadata(bad_id))
        with self.assertRaisesRegex(rp.RejectedError, "not a syntactically valid"):
            self.call(video_id=bad_id, metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_unknown_package_id(self):
        self.write_events([sent_event_row(PKG_2)])  # different package sent, not PKG
        meta_path = self.write_metadata_file(api_metadata(VID))
        with self.assertRaisesRegex(rp.RejectedError, "no 'sent' event"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_when_no_events_file_exists_at_all(self):
        # events_path never written -- must fail closed, not treat as "anything goes"
        meta_path = self.write_metadata_file(api_metadata(VID))
        with self.assertRaisesRegex(rp.RejectedError, "no 'sent' event"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_missing_metadata_file(self):
        self.write_events([sent_event_row(PKG)])
        with self.assertRaisesRegex(rp.RejectedError, "could not be read"):
            self.call(metadata_path=os.path.join(self.tree, "does_not_exist.json"))
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_invalid_json_metadata_file(self):
        self.write_events([sent_event_row(PKG)])
        path = os.path.join(self.tree, "bad.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{not valid json")
        with self.assertRaisesRegex(rp.RejectedError, "not valid JSON"):
            self.call(metadata_path=path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_metadata_id_mismatch(self):
        self.write_events([sent_event_row(PKG)])
        # metadata proves a DIFFERENT video id than the one being claimed
        meta_path = self.write_metadata_file(api_metadata(VID_2))
        with self.assertRaisesRegex(rp.RejectedError, "does not match"):
            self.call(video_id=VID, metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_non_public_privacy_status(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID, privacy="private"))
        with self.assertRaisesRegex(rp.RejectedError, "not 'public'"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_unlisted_privacy_status(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID, privacy="unlisted"))
        with self.assertRaisesRegex(rp.RejectedError, "not 'public'"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_missing_status_block_entirely(self):
        # F8 fix: metadata with NO 'status' block at all previously skipped the
        # privacy gate silently and PASSED. api_metadata(privacy=None) has always
        # supported building this case; no test exercised it until now.
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID, privacy=None))
        with self.assertRaisesRegex(rp.RejectedError, "not 'public'"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_videos_list_response_with_zero_items(self):
        self.write_events([sent_event_row(PKG)])
        path = os.path.join(self.tree, "empty.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"items": []}, fh)
        with self.assertRaisesRegex(rp.RejectedError, "exactly one item"):
            self.call(metadata_path=path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_videos_list_response_with_multiple_items(self):
        self.write_events([sent_event_row(PKG)])
        path = os.path.join(self.tree, "multi.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"items": [api_metadata(VID), api_metadata(VID_2)]}, fh)
        with self.assertRaisesRegex(rp.RejectedError, "exactly one item"):
            self.call(metadata_path=path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_duplicate_video_id(self):
        self.write_events([sent_event_row(PKG), sent_event_row(PKG_2)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        self.call(metadata_path=meta_path)  # first write succeeds
        # second package claiming the SAME real video id must be rejected
        with self.assertRaisesRegex(rp.RejectedError, "already has a published row"):
            self.call(package_id=PKG_2, metadata_path=meta_path)
        self.assertEqual(len(self.ledger_rows()), 1)

    def test_rejects_duplicate_package_id(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        self.call(metadata_path=meta_path)  # first write succeeds
        meta_path_2 = self.write_metadata_file(api_metadata(VID_2))
        # same package claiming a SECOND video id must be rejected (no silent overwrite)
        with self.assertRaisesRegex(rp.RejectedError, "already has a published row"):
            self.call(video_id=VID_2, metadata_path=meta_path_2)
        self.assertEqual(len(self.ledger_rows()), 1)

    def test_rejects_related_video_id_equal_to_own_video_id(self):
        # Law #85 addendum (2026-07-27): a video cannot be its own Related Video.
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        with self.assertRaisesRegex(rp.RejectedError, "cannot be its own Related Video"):
            self.call(metadata_path=meta_path, related_video_id=VID)
        self.assertEqual(self.ledger_rows(), [])

    def test_related_video_id_is_recorded_when_provided(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        row = self.call(metadata_path=meta_path, related_video_id=VID_2)
        self.assertEqual(row["related_video_id"], VID_2)
        self.assertEqual(self.ledger_rows()[0]["related_video_id"], VID_2)

    def test_related_video_id_defaults_to_null_when_absent(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        row = self.call(metadata_path=meta_path)  # related_video_id=None via self.call default
        self.assertIsNone(row["related_video_id"])

    def test_related_video_id_whitespace_only_normalizes_to_null(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        row = self.call(metadata_path=meta_path, related_video_id="   ")
        self.assertIsNone(row["related_video_id"])

    def test_rejects_invalid_objective(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        with self.assertRaisesRegex(rp.RejectedError, "--objective"):
            self.call(metadata_path=meta_path, objective="MADE_UP_GOAL")
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_invalid_format(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        with self.assertRaisesRegex(rp.RejectedError, "--format"):
            self.call(metadata_path=meta_path, fmt="medium_form")
        self.assertEqual(self.ledger_rows(), [])


class TestHumanAttestationPath(RecordPublicationCase):
    """F9: a SECOND, independent public-status confirmation path for when the real
    videos.list API call is unavailable. Must be usable ONLY when the API signal is
    genuinely absent/inconclusive -- NEVER when status is present and disagrees."""

    def _metadata_no_status(self, video_id: str, *, title: str = "Real Title", **attestation_overrides) -> dict:
        item = {
            "id": video_id,
            "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": title},
            "human_attestation": human_attestation_block(**attestation_overrides),
        }
        return item

    # -- success: genuine absence/inconclusiveness --

    def test_human_path_succeeds_when_status_block_entirely_absent(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        self.assertNotIn("status", item)
        meta_path = self.write_metadata_file(item)
        row = self.call(metadata_path=meta_path)
        self.assertEqual(row["youtube_video_id"], VID)
        self.assertEqual(row["verification_source"], "human")
        self.assertEqual(self.ledger_rows()[0]["verification_source"], "human")

    def test_human_path_succeeds_when_status_present_but_privacy_status_missing(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        item["status"] = {}  # dict present, but no privacyStatus key at all
        meta_path = self.write_metadata_file(item)
        row = self.call(metadata_path=meta_path)
        self.assertEqual(row["verification_source"], "human")

    def test_human_path_succeeds_when_privacy_status_is_explicitly_null(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        item["status"] = {"privacyStatus": None}
        meta_path = self.write_metadata_file(item)
        row = self.call(metadata_path=meta_path)
        self.assertEqual(row["verification_source"], "human")

    # -- rejection: explicit disagreement must NEVER be overridden by a human block --

    def test_rejects_human_attestation_when_api_status_present_and_disagrees_private(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        item["status"] = {"privacyStatus": "private"}
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "explicitly shows"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_human_attestation_when_api_status_present_and_disagrees_unlisted(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        item["status"] = {"privacyStatus": "unlisted"}
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "explicitly shows"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    # -- rejection: partial/malformed human_attestation blocks --

    def test_rejects_bare_boolean_human_attestation(self):
        self.write_events([sent_event_row(PKG)])
        item = {"id": VID, "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": "T"}}
        item["human_attestation"] = True  # wrong shape entirely, not an object
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "must be an object"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_human_attestation_true_with_no_siblings_at_all(self):
        # the user's explicit example: verified: true with nothing else
        self.write_events([sent_event_row(PKG)])
        item = {"id": VID, "snippet": {"publishedAt": "2026-07-22T13:24:44Z", "title": "T"}}
        item["human_attestation"] = {"verified": True}
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "missing or empty required field"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_human_attestation_with_only_one_of_three_siblings(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID)
        item["human_attestation"] = {"verified": True, "verifier": "Sebastian Lemos"}
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(
            rp.RejectedError, "verified_at.*verification_method|verification_method.*verified_at"
        ):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_human_attestation_with_empty_string_sibling(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID, verifier="")
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "verifier"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])

    def test_rejects_when_verified_field_is_not_literally_true(self):
        self.write_events([sent_event_row(PKG)])
        item = self._metadata_no_status(VID, verified="yes")
        meta_path = self.write_metadata_file(item)
        with self.assertRaisesRegex(rp.RejectedError, "must be exactly"):
            self.call(metadata_path=meta_path)
        self.assertEqual(self.ledger_rows(), [])


class TestCliEntryPoint(RecordPublicationCase):
    def test_main_returns_ok_exit_code_on_success(self):
        self.write_events([sent_event_row(PKG)])
        meta_path = self.write_metadata_file(api_metadata(VID))
        code = rp.main([
            "record_publication.py",
            "--tree", self.tree,
            "--package-id", PKG,
            "--youtube-video-id", VID,
            "--verified-metadata-file", meta_path,
            "--now", NOW,
        ])
        self.assertEqual(code, rp.EXIT_OK)
        self.assertEqual(len(self.ledger_rows()), 1)

    def test_main_returns_rejected_exit_code_on_failure(self):
        # no sent events at all -> must reject via CLI path too
        meta_path = self.write_metadata_file(api_metadata(VID))
        code = rp.main([
            "record_publication.py",
            "--tree", self.tree,
            "--package-id", PKG,
            "--youtube-video-id", VID,
            "--verified-metadata-file", meta_path,
            "--now", NOW,
        ])
        self.assertEqual(code, rp.EXIT_REJECTED)
        self.assertEqual(self.ledger_rows(), [])


if __name__ == "__main__":
    unittest.main()

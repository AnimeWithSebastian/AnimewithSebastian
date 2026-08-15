#!/usr/bin/env python3
"""Tests for the deterministic weekly analytics no-op gate (credit-safe mode).

Pins the fail-open contract: the gate returns NOOP (0) ONLY when it can confidently
prove zero new published video IDs since the last successful run's cutoff. New IDs,
missing/corrupt state, an absent cutoff field, and malformed input all return RUN_FULL
(10) so a full analytics run happens rather than a wrong no-op. Runs against a throwaway
tree — no repo state is touched. Stdlib unittest only.

    python3 tools/test_weekly_noop_gate.py
    python3 -m unittest discover  (from inside the tools/ directory)
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

import weekly_noop_gate as g

NOW = "2026-07-20T23:30:00Z"
VID_A = "abcdefghij1"   # 11-char valid ids
VID_B = "klmnopqrst2"
VID_C = "uvwxyz01234"


def published_row(vid: str, **extra) -> str:
    row = {"event": "published", "package_id": "pkg-" + vid,
           "youtube_video_id": vid, "publish_ts": NOW}
    row.update(extra)
    return json.dumps(row)


class GateCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tree = self._tmp.name
        self.ledger = os.path.join(self.tree, "cron_tracking", "publication_ledger.jsonl")
        self.state = os.path.join(self.tree, "cron_tracking", g.CRON_ID, "state.json")
        self.summary = os.path.join(self.tree, "cron_tracking", g.CRON_ID,
                                    "last_noop_summary.json")
        os.makedirs(os.path.dirname(self.ledger), exist_ok=True)
        os.makedirs(os.path.dirname(self.state), exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_ledger(self, lines):
        with open(self.ledger, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + ("\n" if lines else ""))

    def write_state(self, obj):
        if isinstance(obj, str):
            with open(self.state, "w", encoding="utf-8") as fh:
                fh.write(obj)
        else:
            with open(self.state, "w", encoding="utf-8") as fh:
                json.dump(obj, fh)

    def run_gate(self):
        return g.main(["weekly_noop_gate.py", "--tree", self.tree, "--now", NOW])

    def state_obj(self):
        with open(self.state, encoding="utf-8") as fh:
            return json.load(fh)

    def summary_obj(self):
        with open(self.summary, encoding="utf-8") as fh:
            return json.load(fh)


class TestNoOp(GateCase):
    def test_no_new_ids_returns_noop(self):
        self.write_ledger([published_row(VID_A), published_row(VID_B)])
        self.write_state({"run_count": 5, "analytics_processed_video_ids": [VID_A, VID_B]})
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)

    def test_noop_writes_summary_and_touches_state(self):
        self.write_ledger([published_row(VID_A)])
        self.write_state({"run_count": 5, "analytics_processed_video_ids": [VID_A]})
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)
        s = self.summary_obj()
        self.assertEqual(s["decision"], "noop")
        self.assertEqual(s["new_video_ids"], 0)
        self.assertFalse(s["connectors_called"] or s["model_synthesis"] or s["email_sent"])
        st = self.state_obj()
        self.assertEqual(st["last_run_mode"], "noop")
        self.assertEqual(st["run_count"], 6)  # bumped
        # cutoff preserved unchanged (no new IDs)
        self.assertEqual(st["analytics_processed_video_ids"], [VID_A])

    def test_empty_ledger_with_empty_cutoff_is_noop(self):
        self.write_ledger([])
        self.write_state({"analytics_processed_video_ids": []})
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)

    def test_duplicate_ledger_ids_do_not_count_as_new(self):
        # same id published twice (e.g. a metrics_update or a retry) is not "new work"
        self.write_ledger([published_row(VID_A), published_row(VID_A),
                           json.dumps({"event": "metrics_update",
                                       "youtube_video_id": VID_A, "window": "24h"})])
        self.write_state({"analytics_processed_video_ids": [VID_A]})
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)


class TestRunFull(GateCase):
    def test_new_id_returns_run_full(self):
        self.write_ledger([published_row(VID_A), published_row(VID_B)])
        self.write_state({"analytics_processed_video_ids": [VID_A]})
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)
        # a run_full must NOT write a no-op summary
        self.assertFalse(os.path.exists(self.summary))

    def test_missing_state_returns_run_full(self):
        self.write_ledger([published_row(VID_A)])
        # no state.json written
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)

    def test_corrupt_state_returns_run_full(self):
        self.write_ledger([published_row(VID_A)])
        self.write_state("{ this is not json ")
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)

    def test_state_without_cutoff_field_returns_run_full(self):
        # historical state (pre-credit-safe-mode) has no analytics_processed_video_ids
        self.write_ledger([published_row(VID_A)])
        self.write_state({"run_count": 5, "videos_graded": 53})
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)

    def test_malformed_cutoff_field_returns_run_full(self):
        self.write_ledger([published_row(VID_A)])
        self.write_state({"analytics_processed_video_ids": "not-a-list"})
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)

    def test_new_id_when_cutoff_empty_runs_full(self):
        self.write_ledger([published_row(VID_A)])
        self.write_state({"analytics_processed_video_ids": []})
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)


class TestVideoIdHygiene(GateCase):
    def test_invalid_and_missing_ids_are_ignored(self):
        # rows with a bad-length id, a null id, and a non-published event must not
        # be counted as published work
        self.write_ledger([
            published_row(VID_A),
            json.dumps({"event": "published", "youtube_video_id": "tooshort"}),
            json.dumps({"event": "published", "youtube_video_id": None}),
            json.dumps({"event": "published"}),
            json.dumps({"event": "sent", "youtube_video_id": VID_C}),
            "{ not json at all",
        ])
        self.write_state({"analytics_processed_video_ids": [VID_A]})
        # only VID_A is a valid published id, and it is already in the cutoff -> noop
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)

    def test_published_ids_seen_counts_only_valid_unique(self):
        self.write_ledger([published_row(VID_A), published_row(VID_A),
                           json.dumps({"event": "published", "youtube_video_id": "bad"})])
        ids = g.published_video_ids(self.ledger)
        self.assertEqual(ids, {VID_A})

    def test_missing_ledger_file_is_empty_published_set(self):
        # no ledger file at all
        self.write_state({"analytics_processed_video_ids": []})
        self.assertEqual(self.run_gate(), g.EXIT_NOOP)


class TestNoWriteOnRunFull(GateCase):
    def test_run_full_leaves_state_untouched(self):
        self.write_ledger([published_row(VID_A), published_row(VID_B)])
        original = {"run_count": 9, "analytics_processed_video_ids": [VID_A]}
        self.write_state(original)
        self.assertEqual(self.run_gate(), g.EXIT_RUN_FULL)
        # gate must not mutate state on a full-run decision (STEP 7 does that later)
        self.assertEqual(self.state_obj(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)

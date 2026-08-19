#!/usr/bin/env python3
"""Tests for the VO-handoff observability log (tools/vo_handoff_log.py).

Every test writes to a temp path, never the real
cron_tracking/daily_combined/vo_handoff_log.jsonl. Stdlib unittest only.

    python3 -m unittest discover  (from inside the tools/ directory)
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

import vo_handoff_log as L


class _TmpLog(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.mkdtemp()
        self.path = os.path.join(self._dir, "vo_handoff_log.jsonl")

    def events(self) -> list[dict]:
        return L.read_events(self.path)


class TestVoHandoffLogEvents(_TmpLog):
    def test_all_four_event_types_round_trip(self):
        L.log_vo_requested("b1", "p1", word_band="200-216", path=self.path)
        L.log_vo_received("b1", "p1", vo_word_count=210, path=self.path)
        L.log_vo_rejected("b1", "p1", validator_exit_code=1,
                          reason="word count out of band",
                          failed_checks=["[evening] VO within 200-216 words"],
                          path=self.path)
        L.log_vo_inserted("b1", "p1", validator_exit_code=0, path=self.path)
        self.assertEqual([e["event"] for e in self.events()],
                         ["vo_requested", "vo_received", "vo_rejected", "vo_inserted"])

    def test_every_record_carries_batch_package_and_timestamp(self):
        L.log_vo_requested("batch-x", "pkg-y", path=self.path)
        rec = self.events()[0]
        self.assertEqual(rec["batch_id"], "batch-x")
        self.assertEqual(rec["package_id"], "pkg-y")
        self.assertTrue(rec["ts"], "every event must carry a timestamp")

    def test_log_is_append_only_never_truncates(self):
        for i in range(3):
            L.log_vo_requested(f"b{i}", f"p{i}", path=self.path)
        self.assertEqual(len(self.events()), 3)
        # a later write must not clobber earlier lines
        L.log_vo_received("b0", "p0", path=self.path)
        self.assertEqual(len(self.events()), 4)

    def test_word_band_is_preserved_for_the_writer(self):
        # The band is the instruction handed to Claude; losing it would make the
        # request unreconstructable without re-deriving the edit length.
        L.log_vo_requested("b1", "p1", word_band="100-108", path=self.path)
        self.assertEqual(self.events()[0]["word_band"], "100-108")


class TestVoInsertedHardGuard(_TmpLog):
    """log_vo_inserted must REFUSE anything but a fully_passed (exit 0) validation."""

    def test_exit_zero_is_logged(self):
        L.log_vo_inserted("b1", "p1", validator_exit_code=0, path=self.path)
        self.assertEqual(len(self.events()), 1)

    def test_exit_three_partial_is_refused(self):
        # Exit 3 = PARTIAL: no failures, but VO-dependent checks are still SKIPPED.
        # Recording that as an insertion is the exact false-confidence this guards.
        with self.assertRaises(ValueError):
            L.log_vo_inserted("b1", "p1", validator_exit_code=3, path=self.path)
        self.assertEqual(self.events(), [], "nothing may be written on refusal")

    def test_exit_one_failure_is_refused(self):
        with self.assertRaises(ValueError):
            L.log_vo_inserted("b1", "p1", validator_exit_code=1, path=self.path)
        self.assertEqual(self.events(), [])


class TestVoHandoffLogValidation(_TmpLog):
    def test_unknown_event_type_rejected(self):
        with self.assertRaises(ValueError):
            L._base_record("vo_teleported", "b1", "p1")

    def test_blank_batch_or_package_id_rejected(self):
        with self.assertRaises(ValueError):
            L.log_vo_requested("", "p1", path=self.path)
        with self.assertRaises(ValueError):
            L.log_vo_requested("b1", "   ", path=self.path)


class TestFailedRevalidationScenario(_TmpLog):
    """Walk the real failed-revalidation path end to end.

    Scenario: handoff sent -> VO comes back -> re-validation FAILS -> VO rejected ->
    writer redoes it against the SAME batch_id/package_id -> second VO passes.

    The redo must NOT log a second vo_requested: one handoff was requested, and a
    duplicate would make the log read as two separate handoffs for one package.
    """

    def test_reject_then_redo_same_ids_single_request(self):
        BATCH, PKG = "d4a8f107-batch", "b7c41e0a-pkg"

        L.log_vo_requested(BATCH, PKG, word_band="200-216", path=self.path)
        L.log_vo_received(BATCH, PKG, vo_word_count=140, path=self.path)
        L.log_vo_rejected(BATCH, PKG, validator_exit_code=1,
                          reason="VO word count below the required band",
                          failed_checks=["[evening] VO within 200-216 words"],
                          path=self.path)

        # redo -- same ids, NO second vo_requested
        L.log_vo_received(BATCH, PKG, vo_word_count=208, path=self.path)
        L.log_vo_inserted(BATCH, PKG, validator_exit_code=0, path=self.path)

        evs = self.events()
        self.assertEqual([e["event"] for e in evs],
                         ["vo_requested", "vo_received", "vo_rejected",
                          "vo_received", "vo_inserted"])
        self.assertEqual(sum(1 for e in evs if e["event"] == "vo_requested"), 1,
                         "a redo must not log a second vo_requested")
        self.assertTrue(all(e["batch_id"] == BATCH and e["package_id"] == PKG for e in evs),
                        "a redo must reuse the same batch_id/package_id")
        # the rejection must carry the specific failed check, not just a boolean
        rej = next(e for e in evs if e["event"] == "vo_rejected")
        self.assertEqual(rej["failed_checks"], ["[evening] VO within 200-216 words"])


class TestObservabilityOnly(unittest.TestCase):
    """This log must never become an input to a gate."""

    def test_no_gate_reads_the_handoff_log(self):
        # Guards against the failure mode the module docstring names: a record that
        # quietly becomes a source of truth. If a gate ever starts importing this
        # module, this test should fail and force a deliberate decision.
        import io
        here = os.path.dirname(os.path.abspath(__file__))
        gate_files = [
            os.path.join(here, "append_send_batch.py"),
            os.path.join(here, "weekly_noop_gate.py"),
            os.path.join(os.path.dirname(here), "validators", "validate_dual_package.py"),
        ]
        for f in gate_files:
            if not os.path.exists(f):
                continue
            with io.open(f, encoding="utf-8") as fh:
                src = fh.read()
            self.assertNotIn("vo_handoff_log", src,
                             msg=f"{os.path.basename(f)} must not read the handoff log "
                                 f"-- it is observability only, never a gate input")


if __name__ == "__main__":
    unittest.main(verbosity=2)

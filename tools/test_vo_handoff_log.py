from __future__ import annotations

import os
import shutil
import tempfile
import unittest

import vo_handoff_log as vhl


class TestVoHandoffLogSchema(unittest.TestCase):
    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def test_unknown_event_type_rejected(self):
        with self.assertRaises(ValueError):
            vhl.build_event("vo_bogus", batch_id="b1", package_id="p1", slot="morning", show="X")

    def test_vo_requested_missing_field_rejected(self):
        # vo_status is auto-filled by log_vo_requested, but build_event directly
        # must still reject an incomplete manual construction.
        with self.assertRaises(ValueError):
            vhl.build_event("vo_requested", batch_id="b1", package_id="p1", slot="morning", show="X")

    def test_vo_inserted_requires_exit_code_zero(self):
        with self.assertRaises(ValueError):
            vhl.build_event("vo_inserted", batch_id="b1", package_id="p1", slot="morning",
                             show="X", validator_exit_code=1)
        with self.assertRaises(ValueError):
            vhl.build_event("vo_inserted", batch_id="b1", package_id="p1", slot="morning",
                             show="X", validator_exit_code=3)
        # zero is fine
        e = vhl.build_event("vo_inserted", batch_id="b1", package_id="p1", slot="morning",
                             show="X", validator_exit_code=0)
        self.assertEqual(e["validator_exit_code"], 0)

    def test_vo_rejected_requires_failed_checks(self):
        with self.assertRaises(ValueError):
            vhl.build_event("vo_rejected", batch_id="b1", package_id="p1", slot="morning",
                             show="X", validator_exit_code=1)

    def test_append_creates_file_and_parent_dir(self):
        path = vhl._log_path(self.tree)
        self.assertFalse(os.path.exists(path))
        vhl.log_vo_requested(self.tree, batch_id="b1", package_id="p1", slot="morning", show="X")
        self.assertTrue(os.path.exists(path))

    def test_events_are_one_json_object_per_line(self):
        vhl.log_vo_requested(self.tree, batch_id="b1", package_id="p1", slot="morning", show="X")
        vhl.log_vo_received(self.tree, batch_id="b1", package_id="p1", slot="morning", show="X",
                             vo_word_count=104)
        events = vhl.read_events(self.tree)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "vo_requested")
        self.assertEqual(events[1]["event"], "vo_received")
        self.assertEqual(events[1]["vo_word_count"], 104)

    def test_read_events_filters_by_batch_and_package(self):
        vhl.log_vo_requested(self.tree, batch_id="b1", package_id="p1", slot="morning", show="X")
        vhl.log_vo_requested(self.tree, batch_id="b1", package_id="p2", slot="evening", show="Y")
        vhl.log_vo_requested(self.tree, batch_id="b2", package_id="p3", slot="morning", show="Z")
        self.assertEqual(len(vhl.read_events(self.tree, batch_id="b1")), 2)
        self.assertEqual(len(vhl.read_events(self.tree, batch_id="b1", package_id="p2")), 1)
        self.assertEqual(len(vhl.read_events(self.tree, batch_id="b2")), 1)

    def test_explicit_failed_revalidation_case_full_timeline(self):
        """The exact case the user required to be shown explicitly: Sebastian
        pastes a VO, the full validator comes back with a real FAIL. Confirms:
        - vo_received IS logged (unconditional on receipt)
        - vo_inserted is NOT logged (only fully_passed logs it)
        - vo_rejected IS logged, carrying the failed check names
        - the redo reuses the SAME batch_id/package_id and does NOT log a
          second vo_requested -- the original one stands
        - the corrected VO that comes back next is just another vo_received
          for the same package_id, followed by vo_inserted once it passes
        """
        batch_id, package_id, slot, show = "9dc75e78", "pkg-morning-1", "morning", "Spy x Family"

        # 1. draft/email stage
        vhl.log_vo_requested(self.tree, batch_id=batch_id, package_id=package_id, slot=slot, show=show)

        # 2. Sebastian pastes VO #1 -- receipt is unconditional
        vhl.log_vo_received(self.tree, batch_id=batch_id, package_id=package_id, slot=slot,
                             show=show, vo_word_count=112)

        # 3. full validator re-run comes back with a REAL FAIL (exit code 1) --
        #    batch stays at AWAITING_VO, no vo_inserted, a vo_rejected instead
        vhl.log_vo_rejected(self.tree, batch_id=batch_id, package_id=package_id, slot=slot, show=show,
                             validator_exit_code=1, failed_checks=["VO within 100-108 words"])

        events_so_far = vhl.read_events(self.tree, batch_id=batch_id, package_id=package_id)
        self.assertEqual([e["event"] for e in events_so_far],
                          ["vo_requested", "vo_received", "vo_rejected"])
        self.assertNotIn("vo_inserted", [e["event"] for e in events_so_far])
        # exactly one vo_requested across the whole (still-open) round trip
        self.assertEqual(sum(1 for e in events_so_far if e["event"] == "vo_requested"), 1)

        # 4. redo round trip: Sebastian pastes a CORRECTED VO for the SAME
        #    batch_id/package_id. No new vo_requested is logged for this --
        #    only another vo_received.
        vhl.log_vo_received(self.tree, batch_id=batch_id, package_id=package_id, slot=slot,
                             show=show, vo_word_count=105)
        events_after_redo = vhl.read_events(self.tree, batch_id=batch_id, package_id=package_id)
        self.assertEqual(sum(1 for e in events_after_redo if e["event"] == "vo_requested"), 1,
                          "redo must not log a second vo_requested -- the original stands")
        self.assertEqual(sum(1 for e in events_after_redo if e["event"] == "vo_received"), 2)

        # 5. this time the full validator re-run is fully_passed (exit 0) --
        #    NOW vo_inserted is logged, and the batch can transition onward.
        vhl.log_vo_inserted(self.tree, batch_id=batch_id, package_id=package_id, slot=slot,
                             show=show, validator_exit_code=0)
        final_events = vhl.read_events(self.tree, batch_id=batch_id, package_id=package_id)
        self.assertEqual([e["event"] for e in final_events],
                          ["vo_requested", "vo_received", "vo_rejected", "vo_received", "vo_inserted"])
        # exactly one vo_inserted, matching the one fully_passed re-run
        self.assertEqual(sum(1 for e in final_events if e["event"] == "vo_inserted"), 1)

    def test_never_imported_by_any_gating_module(self):
        """Pure-observability guarantee: confirm neither the dual-package
        validator, the longform validator, nor append_send_batch.py imports
        this module -- it must never become a gating input."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gating_files = [
            os.path.join(repo_root, "validators", "validate_dual_package.py"),
            os.path.join(repo_root, "validators", "validate_longform_flagship.py"),
            os.path.join(repo_root, "tools", "append_send_batch.py"),
        ]
        for path in gating_files:
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertNotIn("vo_handoff_log", content,
                              msg=f"{path} must never import/reference vo_handoff_log (pure observability only)")


if __name__ == "__main__":
    unittest.main()

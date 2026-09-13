#!/usr/bin/env python3
"""Tests for tools/presend_approval_check.py (F87 fix) -- the STEP 6.5,
pre-STEP-7 CLI wrapper around approval_gate.check_fetch_review_gate().

Runs the real script as a subprocess (matching how it will actually be
invoked at STEP 6.5) rather than importing main() directly, so the test
also covers argv handling and exit codes exactly as an operator would see
them.

    python3 tools/test_presend_approval_check.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "presend_approval_check.py")


def run_check(approval_path: str | None) -> subprocess.CompletedProcess:
    argv = [sys.executable, _SCRIPT]
    if approval_path is not None:
        argv.append(approval_path)
    return subprocess.run(argv, capture_output=True, text=True)


def write_approval(tmpdir: str, fetch_review) -> str:
    path = os.path.join(tmpdir, "approval.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"approved_by": None, "approved_at": None,
                   "fetch_review": fetch_review}, fh)
    return path


class TestPresendApprovalCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_no_args_exits_2(self):
        proc = run_check(None)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)

    def test_missing_file_exits_2(self):
        proc = run_check(os.path.join(self.tmpdir, "does_not_exist.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("[ERROR]", proc.stderr)

    def test_malformed_json_exits_2(self):
        path = os.path.join(self.tmpdir, "bad.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{not valid json")
        proc = run_check(path)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("[ERROR]", proc.stderr)

    def test_passing_fetch_review_exits_0(self):
        path = write_approval(self.tmpdir, [
            {"claim": "supported core claim", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
        ])
        proc = run_check(path)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[PASS]", proc.stdout)

    def test_undisclosed_core_true_failure_exits_1_and_names_do_not_send(self):
        path = write_approval(self.tmpdir, [
            {"claim": "core claim that failed verification", "core": True,
             "url": "https://example.com/a", "fetched_content_supports_claim": False},
        ])
        proc = run_check(path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[BLOCKED]", proc.stderr)
        self.assertIn("DO NOT SEND", proc.stderr)

    def test_negative_control_marked_core_false_with_note_exits_0(self):
        # This is the exact tonight's-batch shape (d0385ca7): a genuine
        # negative control, correctly marked core:false with a real note,
        # must pass the pre-send check -- same as it now passes the
        # post-send gate after being corrected.
        path = write_approval(self.tmpdir, [
            {"claim": "does any source support the WRONG framing", "core": False,
             "url": "https://example.com/b", "fetched_content_supports_claim": False,
             "note": "negative control -- False is the correct, expected result, "
                     "not a failed verification"},
        ])
        proc = run_check(path)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[PASS]", proc.stdout)

    def test_negative_control_missing_core_marker_exits_1(self):
        # This is tonight's actual failure mode, reproduced: a genuine
        # negative control authored WITHOUT a core marker defaults to
        # core=True and blocks. The pre-send check catches this BEFORE a
        # send would happen, which is the entire point of F87's fix.
        path = write_approval(self.tmpdir, [
            {"claim": "does any source support the WRONG framing",
             "url": "https://example.com/c", "fetched_content_supports_claim": False,
             "note": "would have been a valid disclosure, but no core:false marker"},
        ])
        proc = run_check(path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("[BLOCKED]", proc.stderr)

    def test_schema_mismatch_exits_1_with_law_173_message(self):
        path = write_approval(self.tmpdir, [
            {"claim": "some claim", "url": "https://example.com/d", "verdict": "confirmed"},
        ])
        proc = run_check(path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("schema mismatch (Law #173)", proc.stderr)

    def test_non_object_json_exits_2(self):
        path = os.path.join(self.tmpdir, "list.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([1, 2, 3], fh)
        proc = run_check(path)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()

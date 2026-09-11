#!/usr/bin/env python3
"""Tests for tools/known_issues_status_audit.py.

Built against the real incident this tool exists for: F43 documented a
self-attestation gap whose fix shipped 2026-08-19, while its Status line still
read "OPEN -- findings record only, no fix written" 22 days later. Nothing
coupled "fix shipped" to "entry updated", so nothing caught it.

The tool deliberately REPORTS rather than gates (KNOWN_ISSUES.md's 66 entries
use freeform status prose; automated open/closed inference would false-positive
at a rate that trains people to ignore it). These tests pin that boundary too:
a hit is a review candidate, never a claim of staleness, and the tool never
blocks.
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import known_issues_status_audit as audit


class AuditCase(unittest.TestCase):
    def setUp(self):
        self.tree = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tree, "docs"), exist_ok=True)
        os.makedirs(os.path.join(self.tree, "tools"), exist_ok=True)
        os.makedirs(os.path.join(self.tree, "validators"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def write_issues(self, text):
        with open(os.path.join(self.tree, "docs", "KNOWN_ISSUES.md"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)

    def write_code(self, relpath, content="def placeholder():\n    pass\n"):
        full = os.path.join(self.tree, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)

    def run_audit(self, *flags):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = audit.main(["--tree", self.tree, *flags])
        return rc, buf.getvalue()


class TestStatusParsing(AuditCase):
    def test_open_entry_naming_existing_file_is_flagged(self):
        self.write_code("tools/thing.py")
        self.write_issues(
            "## F1: a real gap\n\n"
            "**Status:** OPEN — findings record only, no fix written.\n\n"
            "The fix would live in `tools/thing.py`.\n"
        )
        rc, out = self.run_audit()
        self.assertEqual(rc, 0)
        self.assertIn("F1", out)
        self.assertIn("tools/thing.py", out)

    def test_open_entry_naming_absent_file_is_not_flagged(self):
        self.write_issues(
            "## F2: a real gap\n\n"
            "**Status:** OPEN — no fix written.\n\n"
            "Would live in `tools/does_not_exist.py`.\n"
        )
        rc, out = self.run_audit()
        self.assertEqual(rc, 0)
        self.assertIn("No review candidates", out)

    def test_resolved_entry_is_never_flagged(self):
        self.write_code("tools/thing.py")
        self.write_issues(
            "## F3: fixed thing\n\n"
            "**Status:** RESOLVED in commit abc1234 (`tools/thing.py`).\n\n"
            "Done.\n"
        )
        rc, out = self.run_audit()
        self.assertIn("No review candidates", out)

    def test_mixed_status_with_resolution_marker_not_flagged(self):
        # Real shape from this repo: "OPEN (design question) / MECHANICAL RISK
        # CLOSED". A deliberate mixed state is not staleness.
        self.write_code("validators/validate_dual_package.py")
        self.write_issues(
            "## F4: partly handled\n\n"
            "**Status:** OPEN (design question) / MECHANICAL RISK CLOSED — the\n"
            "check in `validators/validate_dual_package.py` covers the risk.\n\n"
            "Body.\n"
        )
        rc, out = self.run_audit()
        self.assertIn("No review candidates", out)

    def test_logged_only_counts_as_unresolved(self):
        self.write_code("tools/thing.py")
        self.write_issues(
            "## F5: logged thing\n\n"
            "**Status:** Logged only. No code changes made.\n\n"
            "Relevant code is `tools/thing.py`.\n"
        )
        rc, out = self.run_audit()
        self.assertIn("F5", out)

    def test_function_reference_resolved_against_real_source(self):
        self.write_code("tools/helper.py",
                        "def check_recent_send_conflict():\n    pass\n")
        self.write_issues(
            "## F6: function gap\n\n"
            "**Status:** OPEN — no fix written.\n\n"
            "A real check would be `check_recent_send_conflict()`.\n"
        )
        rc, out = self.run_audit()
        self.assertIn("F6", out)
        self.assertIn("check_recent_send_conflict()", out)

    def test_function_reference_absent_is_not_flagged(self):
        self.write_code("tools/helper.py", "def something_else():\n    pass\n")
        self.write_issues(
            "## F7: function gap\n\n"
            "**Status:** OPEN — no fix written.\n\n"
            "Would need `never_written_function()`.\n"
        )
        rc, out = self.run_audit()
        self.assertIn("No review candidates", out)


class TestReportingBoundaries(AuditCase):
    def test_always_exits_zero_even_with_findings(self):
        self.write_code("tools/thing.py")
        self.write_issues(
            "## F8: gap\n\n**Status:** OPEN — no fix written.\n\n`tools/thing.py`\n"
        )
        rc, _ = self.run_audit()
        self.assertEqual(rc, 0, "audit is a report and must never block")

    def test_missing_known_issues_file_does_not_crash_or_block(self):
        rc, _ = self.run_audit()
        self.assertEqual(rc, 0)

    def test_output_states_a_hit_is_not_proof_of_staleness(self):
        # The tool must not overclaim -- an entry can legitimately cite
        # existing code while describing a real remaining gap in it.
        self.write_code("tools/thing.py")
        self.write_issues(
            "## F9: gap\n\n**Status:** OPEN — no fix written.\n\n`tools/thing.py`\n"
        )
        _, out = self.run_audit()
        self.assertIn("NOT proof", out)

    def test_verbose_lists_open_entries_without_code_refs(self):
        self.write_issues(
            "## F10: prose-only gap\n\n"
            "**Status:** OPEN — no fix written.\n\n"
            "This one names no code at all.\n"
        )
        _, out = self.run_audit("--verbose")
        self.assertIn("F10", out)
        self.assertIn("NO CHECKABLE CODE REFERENCE", out)

    def test_non_verbose_omits_uncheckable_entries(self):
        self.write_issues(
            "## F11: prose-only gap\n\n"
            "**Status:** OPEN — no fix written.\n\n"
            "Names no code.\n"
        )
        _, out = self.run_audit()
        self.assertNotIn("F11", out)


class TestRealIncidentShape(AuditCase):
    """Reproduces F43's actual shape -- the incident this tool exists for."""

    def test_f43_shape_is_flagged(self):
        self.write_code(
            "tools/conflict_check.py",
            "def check_recent_send_conflict(pkg, tree):\n    return {}\n")
        self.write_code("validators/validate_dual_package.py")
        self.write_issues(
            "## F43: `blackout_conflict` and `recent_send_conflict` are pure "
            "self-attestation with zero mechanical verification\n\n"
            "**Status:** OPEN — findings record only, no fix written. Same "
            "standing convention as every other backlog item here: no diff "
            "without explicit go-ahead and full diff review.\n\n"
            "A real check could live in `validators/validate_dual_package.py` "
            "and call `check_recent_send_conflict()`.\n"
        )
        rc, out = self.run_audit()
        self.assertEqual(rc, 0)
        self.assertIn("F43", out)
        self.assertIn("check_recent_send_conflict()", out)


if __name__ == "__main__":
    unittest.main()

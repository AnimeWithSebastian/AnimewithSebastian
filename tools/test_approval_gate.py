#!/usr/bin/env python3
"""Unit tests for tools/approval_gate.check_fetch_review_gate() (F87 fix).

These pin the EXTRACTED gate's behavior in isolation, independent of
append_send_batch.py's CLI/file/state plumbing. tools/test_append_send_batch.py
already exercises the same scenarios end-to-end through the CLI (62/62 passing
after the extraction, unchanged) -- this file exists so the shared function
itself has direct, fast, no-subprocess unit coverage that a future caller
(e.g. a different script than presend_approval_check.py) can rely on without
needing to shell out.

    python3 tools/test_approval_gate.py
"""

from __future__ import annotations

import unittest

from approval_gate import ApprovalGateResult, check_fetch_review_gate


class TestMissingOrEmptyFetchReview(unittest.TestCase):
    def test_none_blocks(self):
        r = check_fetch_review_gate(None)
        self.assertFalse(r.ok)
        self.assertIn("no non-empty fetch_review list", r.error)

    def test_empty_list_blocks(self):
        r = check_fetch_review_gate([])
        self.assertFalse(r.ok)
        self.assertIn("no non-empty fetch_review list", r.error)

    def test_non_list_blocks(self):
        r = check_fetch_review_gate({"claim": "not a list"})
        self.assertFalse(r.ok)
        self.assertIn("no non-empty fetch_review list", r.error)


class TestSchemaPreCheckLaw173(unittest.TestCase):
    def test_verdict_field_instead_of_real_field_blocks_with_schema_message(self):
        r = check_fetch_review_gate([
            {"claim": "some claim", "url": "https://example.com/a", "verdict": "confirmed"},
        ])
        self.assertFalse(r.ok)
        self.assertIn("schema mismatch (Law #173)", r.error)
        self.assertNotIn("unsupported/malformed", r.error)

    def test_correct_field_true_passes(self):
        r = check_fetch_review_gate([
            {"claim": "some claim", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
        ])
        self.assertTrue(r.ok)
        self.assertIsNone(r.error)

    def test_correct_field_false_skips_schema_check_hits_core_gate_instead(self):
        r = check_fetch_review_gate([
            {"claim": "some claim", "url": "https://example.com/a",
             "fetched_content_supports_claim": False},
        ])
        self.assertFalse(r.ok)
        self.assertNotIn("schema mismatch (Law #173)", r.error)
        self.assertIn("unsupported/malformed", r.error)

    def test_malformed_non_dict_entry_does_not_crash_schema_check(self):
        r = check_fetch_review_gate(["not a dict"])
        self.assertFalse(r.ok)
        self.assertIn("unsupported/malformed", r.error)


class TestCoreAwareGate(unittest.TestCase):
    """Mirrors tools/test_append_send_batch.py::TestCoreAwareApprovalGate,
    against the shared function directly instead of through the CLI."""

    def test_core_true_unsupported_entry_still_blocks(self):
        r = check_fetch_review_gate([
            {"claim": "core claim that failed verification", "core": True,
             "url": "https://example.com/a", "fetched_content_supports_claim": False,
             "note": "even with a note, a core claim that fails verification must block"},
        ])
        self.assertFalse(r.ok)
        self.assertIn("unsupported/malformed", r.error)

    def test_core_false_unsupported_entry_with_real_note_does_not_block(self):
        r = check_fetch_review_gate([
            {"claim": "non-core claim with an honestly disclosed gap", "core": False,
             "url": "https://example.com/b", "fetched_content_supports_claim": False,
             "note": "genuine negative control -- False is the correct/expected result"},
        ])
        self.assertTrue(r.ok)
        self.assertIsNone(r.error)

    def test_core_false_unsupported_entry_without_note_still_blocks(self):
        r = check_fetch_review_gate([
            {"claim": "non-core claim with no disclosure", "core": False,
             "url": "https://example.com/c", "fetched_content_supports_claim": False},
        ])
        self.assertFalse(r.ok)
        self.assertIn("unsupported/malformed", r.error)

    def test_core_false_unsupported_entry_with_empty_string_note_still_blocks(self):
        r = check_fetch_review_gate([
            {"claim": "non-core claim with a blank note", "core": False,
             "url": "https://example.com/c2", "fetched_content_supports_claim": False,
             "note": "   "},
        ])
        self.assertFalse(r.ok)

    def test_mixed_core_true_failure_and_core_false_disclosed_entry_blocks(self):
        r = check_fetch_review_gate([
            {"claim": "core claim that failed verification", "core": True,
             "url": "https://example.com/d1", "fetched_content_supports_claim": False,
             "note": "a note does not rescue a core claim"},
            {"claim": "non-core claim with an honest disclosure", "core": False,
             "url": "https://example.com/d2", "fetched_content_supports_claim": False,
             "note": "genuinely disclosed non-core gap, would pass on its own"},
        ])
        self.assertFalse(r.ok)

    def test_backward_compat_no_core_field_anywhere_still_strict(self):
        r = check_fetch_review_gate([
            {"claim": "claim A", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
            {"claim": "claim B", "url": "https://example.com/b",
             "fetched_content_supports_claim": False},
        ])
        self.assertFalse(r.ok)

    def test_legacy_non_core_text_prefix_with_real_note_does_not_block(self):
        r = check_fetch_review_gate([
            {"claim": "[NON-CORE] secondary detail not itself stated on this page",
             "url": "https://example.com/e", "fetched_content_supports_claim": False,
             "note": "independently confirmed elsewhere in this same approval"},
        ])
        self.assertTrue(r.ok)

    def test_structured_core_false_without_text_marker_does_not_block(self):
        r = check_fetch_review_gate([
            {"claim": "plain claim text, no bracket marker", "core": False,
             "url": "https://example.com/f", "fetched_content_supports_claim": False,
             "note": "structured field alone is sufficient, no text convention needed"},
        ])
        self.assertTrue(r.ok)

    def test_structured_core_true_overrides_conflicting_text_marker_and_blocks(self):
        r = check_fetch_review_gate([
            {"claim": "[NON-CORE] but structured field says otherwise", "core": True,
             "url": "https://example.com/g", "fetched_content_supports_claim": False,
             "note": "structured field is authoritative and wins over the text marker"},
        ])
        self.assertFalse(r.ok)


class TestApprovalGateResultEquality(unittest.TestCase):
    def test_equal_results_compare_equal(self):
        self.assertEqual(ApprovalGateResult(True, None), ApprovalGateResult(True, None))
        self.assertEqual(ApprovalGateResult(False, "x"), ApprovalGateResult(False, "x"))

    def test_different_results_compare_unequal(self):
        self.assertNotEqual(ApprovalGateResult(True, None), ApprovalGateResult(False, "x"))


if __name__ == "__main__":
    unittest.main()

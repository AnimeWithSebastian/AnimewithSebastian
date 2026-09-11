from __future__ import annotations

import os
import shutil
import tempfile
import unittest

import candidate_selection_log as csl


def _valid_kwargs(**overrides):
    """A minimal valid set of kwargs for a REJECTED candidate, since that is
    the most common real case (most candidates considered on a given day are
    rejected -- only two are ever selected). Tests that need a SELECTED
    candidate override outcome/rejection_reason/selected_package_id."""
    kwargs = dict(
        batch_id="b1", run_ts="2026-08-22T22:30:00+00:00", post_date="2026-08-23",
        show="One Piece", angle="Test angle", format_type="FACT_DROP",
        axis_scores={"sub_conversion": "HIGH", "brand_attractiveness": "MED", "viral_discovery": "LOW"},
        cleared_monetization_gate=True, format_eligibility_checked=True,
        format_eligibility_result="eligible", format_eligibility_reason="clears eligibility",
        outcome="rejected", rejection_reason="lost the diversity/blackout pass to another candidate",
        slot_considered_for="either", selected_package_id=None,
    )
    kwargs.update(overrides)
    return kwargs


class TestCandidateSelectionLogSchema(unittest.TestCase):
    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    # --- basic construction ---

    def test_valid_rejected_event_builds(self):
        e = csl.build_event("candidate_scored", **_valid_kwargs())
        self.assertEqual(e["event"], "candidate_scored")
        self.assertEqual(e["outcome"], "rejected")
        self.assertIn("timestamp", e)

    def test_valid_selected_event_builds(self):
        e = csl.build_event("candidate_scored", **_valid_kwargs(
            outcome="selected", rejection_reason=None,
            selected_package_id="pkg-morning-1"))
        self.assertEqual(e["outcome"], "selected")
        self.assertEqual(e["selected_package_id"], "pkg-morning-1")
        self.assertIsNone(e["rejection_reason"])

    def test_unknown_event_type_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_bogus", **_valid_kwargs())

    # --- required-field enforcement ---

    def test_missing_show_rejected(self):
        kwargs = _valid_kwargs()
        del kwargs["show"]
        with self.assertRaises(TypeError):
            # show has no default -- omitting it is a TypeError at the call
            # site, which is the strictest possible enforcement.
            csl.build_event("candidate_scored", **kwargs)

    def test_missing_batch_id_rejected(self):
        kwargs = _valid_kwargs()
        del kwargs["batch_id"]
        with self.assertRaises(TypeError):
            csl.build_event("candidate_scored", **kwargs)

    def test_empty_show_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(show=""))

    def test_empty_angle_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(angle=""))

    # --- axis_scores enforcement ---

    def test_axis_scores_missing_key_rejected(self):
        kwargs = _valid_kwargs()
        kwargs["axis_scores"] = {"sub_conversion": "HIGH", "brand_attractiveness": "MED"}
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **kwargs)

    def test_axis_scores_extra_key_rejected(self):
        kwargs = _valid_kwargs()
        kwargs["axis_scores"] = {
            "sub_conversion": "HIGH", "brand_attractiveness": "MED",
            "viral_discovery": "LOW", "extra_axis": "HIGH",
        }
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **kwargs)

    def test_axis_scores_invalid_value_rejected(self):
        kwargs = _valid_kwargs()
        kwargs["axis_scores"] = {
            "sub_conversion": "VERY_HIGH", "brand_attractiveness": "MED", "viral_discovery": "LOW",
        }
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **kwargs)

    # --- format_eligibility_result enforcement ---

    def test_invalid_eligibility_result_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(format_eligibility_result="maybe"))

    def test_eligibility_reason_required_unless_not_applicable(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                format_eligibility_result="ineligible", format_eligibility_reason=""))

    def test_eligibility_reason_may_be_empty_when_not_applicable(self):
        e = csl.build_event("candidate_scored", **_valid_kwargs(
            format_eligibility_result="not_applicable", format_eligibility_reason=""))
        self.assertEqual(e["format_eligibility_result"], "not_applicable")

    # --- outcome / rejection_reason / selected_package_id cross-field enforcement ---

    def test_invalid_outcome_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(outcome="pending"))

    def test_rejected_without_rejection_reason_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                outcome="rejected", rejection_reason=None))

    def test_rejected_with_empty_rejection_reason_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                outcome="rejected", rejection_reason="   "))

    def test_rejected_with_selected_package_id_rejected(self):
        # a rejected candidate must not carry a selected_package_id
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                outcome="rejected", selected_package_id="pkg-morning-1"))

    def test_selected_without_selected_package_id_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                outcome="selected", rejection_reason=None, selected_package_id=None))

    def test_selected_with_rejection_reason_rejected(self):
        # a selected candidate must not carry a rejection_reason
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(
                outcome="selected", rejection_reason="some reason",
                selected_package_id="pkg-morning-1"))

    # --- slot_considered_for enforcement ---

    def test_invalid_slot_rejected(self):
        with self.assertRaises(ValueError):
            csl.build_event("candidate_scored", **_valid_kwargs(slot_considered_for="afternoon"))

    def test_valid_slots_accepted(self):
        for slot in ("morning", "evening", "either"):
            e = csl.build_event("candidate_scored", **_valid_kwargs(slot_considered_for=slot))
            self.assertEqual(e["slot_considered_for"], slot)

    # --- append / read behavior ---

    def test_append_creates_file_and_parent_dir(self):
        path = csl._log_path(self.tree)
        self.assertFalse(os.path.exists(path))
        csl.log_candidate(self.tree, **_valid_kwargs())
        self.assertTrue(os.path.exists(path))

    def test_events_are_one_json_object_per_line(self):
        csl.log_candidate(self.tree, **_valid_kwargs(show="One Piece"))
        csl.log_candidate(self.tree, **_valid_kwargs(show="Naruto"))
        events = csl.read_events(self.tree)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["show"], "One Piece")
        self.assertEqual(events[1]["show"], "Naruto")

    def test_read_events_filters_by_batch_and_format_type(self):
        csl.log_candidate(self.tree, **_valid_kwargs(
            batch_id="b1", format_type="THEORY_SPECULATION", show="A"))
        csl.log_candidate(self.tree, **_valid_kwargs(
            batch_id="b1", format_type="FACT_DROP", show="B"))
        csl.log_candidate(self.tree, **_valid_kwargs(
            batch_id="b2", format_type="THEORY_SPECULATION", show="C"))
        self.assertEqual(len(csl.read_events(self.tree, batch_id="b1")), 2)
        self.assertEqual(len(csl.read_events(self.tree, batch_id="b1", format_type="THEORY_SPECULATION")), 1)
        self.assertEqual(len(csl.read_events(self.tree, format_type="THEORY_SPECULATION")), 2)
        self.assertEqual(len(csl.read_events(self.tree, batch_id="b2")), 1)

    def test_full_run_one_write_per_candidate_after_full_pipeline(self):
        """Simulates a real daily run's selection pipeline: several
        candidates considered, two selected (one per slot), the rest
        rejected at varying stages. Confirms each candidate gets EXACTLY
        ONE event, and that event carries its full, pipeline-complete
        outcome -- proving the corrected single-write-after-full-pipeline
        design (no intermediate/partial writes)."""
        batch_id, run_ts, post_date = "9dc75e78", "2026-08-22T22:30:00+00:00", "2026-08-23"

        # Candidate 1: fails the monetization gate outright -- format
        # eligibility is therefore never even checked for it.
        csl.log_candidate(
            self.tree, batch_id=batch_id, run_ts=run_ts, post_date=post_date,
            show="Show A", angle="Angle A", format_type="THEORY_SPECULATION",
            axis_scores={"sub_conversion": "LOW", "brand_attractiveness": "LOW", "viral_discovery": "MED"},
            cleared_monetization_gate=False, format_eligibility_checked=False,
            format_eligibility_result="not_applicable", format_eligibility_reason="",
            outcome="rejected", rejection_reason="failed monetization gate (<2-of-3 axes)",
            slot_considered_for="either", selected_package_id=None,
        )

        # Candidate 2: clears monetization, fails format eligibility.
        csl.log_candidate(
            self.tree, batch_id=batch_id, run_ts=run_ts, post_date=post_date,
            show="Show B", angle="Angle B", format_type="WATCH_RANK",
            axis_scores={"sub_conversion": "HIGH", "brand_attractiveness": "MED", "viral_discovery": "HIGH"},
            cleared_monetization_gate=True, format_eligibility_checked=True,
            format_eligibility_result="ineligible",
            format_eligibility_reason="fewer than 3 shows currently on Sebastian's watch list",
            outcome="rejected", rejection_reason="ineligible for WATCH_RANK this run",
            slot_considered_for="either", selected_package_id=None,
        )

        # Candidate 3: clears monetization + eligibility, but loses the
        # diversity/blackout/final-selection pass to another candidate.
        csl.log_candidate(
            self.tree, batch_id=batch_id, run_ts=run_ts, post_date=post_date,
            show="Show C", angle="Angle C", format_type="FACT_DROP",
            axis_scores={"sub_conversion": "HIGH", "brand_attractiveness": "HIGH", "viral_discovery": "MED"},
            cleared_monetization_gate=True, format_eligibility_checked=True,
            format_eligibility_result="eligible", format_eligibility_reason="clears eligibility",
            outcome="rejected", rejection_reason="lost final selection to Show D (same-show blackout)",
            slot_considered_for="morning", selected_package_id=None,
        )

        # Candidate 4: selected for morning.
        csl.log_candidate(
            self.tree, batch_id=batch_id, run_ts=run_ts, post_date=post_date,
            show="Show D", angle="Angle D", format_type="COMMENTARY",
            axis_scores={"sub_conversion": "HIGH", "brand_attractiveness": "HIGH", "viral_discovery": "HIGH"},
            cleared_monetization_gate=True, format_eligibility_checked=True,
            format_eligibility_result="eligible", format_eligibility_reason="clears eligibility",
            outcome="selected", rejection_reason=None,
            slot_considered_for="morning", selected_package_id="pkg-morning-1",
        )

        # Candidate 5: selected for evening.
        csl.log_candidate(
            self.tree, batch_id=batch_id, run_ts=run_ts, post_date=post_date,
            show="Show E", angle="Angle E", format_type="CHARACTER_DIVE",
            axis_scores={"sub_conversion": "MED", "brand_attractiveness": "HIGH", "viral_discovery": "HIGH"},
            cleared_monetization_gate=True, format_eligibility_checked=True,
            format_eligibility_result="eligible", format_eligibility_reason="clears eligibility",
            outcome="selected", rejection_reason=None,
            slot_considered_for="evening", selected_package_id="pkg-evening-1",
        )

        events = csl.read_events(self.tree, batch_id=batch_id)
        self.assertEqual(len(events), 5, "exactly one event per candidate -- no intermediate writes")
        outcomes = [e["outcome"] for e in events]
        self.assertEqual(outcomes.count("selected"), 2)
        self.assertEqual(outcomes.count("rejected"), 3)

        # Candidate 1's single event carries its FULL pipeline-complete
        # state in one write -- not-applicable eligibility because it never
        # got there, monetization gate false, rejected with reason.
        c1 = next(e for e in events if e["show"] == "Show A")
        self.assertFalse(c1["cleared_monetization_gate"])
        self.assertFalse(c1["format_eligibility_checked"])
        self.assertEqual(c1["format_eligibility_result"], "not_applicable")
        self.assertEqual(c1["outcome"], "rejected")
        self.assertTrue(c1["rejection_reason"])

        # THEORY_SPECULATION filter -- proving the log answers the original
        # open question: did THEORY_SPECULATION candidates surface and lose?
        theory_events = csl.read_events(self.tree, format_type="THEORY_SPECULATION")
        self.assertEqual(len(theory_events), 1)
        self.assertEqual(theory_events[0]["outcome"], "rejected")

    def test_never_imported_by_any_gating_module_except_minimum_frequency_floor(self):
        """Narrowed guarantee (revised 2026-08-22, Part 2 design): this log is
        now a real, sanctioned gating input, but to EXACTLY ONE consumer --
        validate_dual_package.py's _validate_minimum_frequency_floor(). It
        remains a hard invariant that NO OTHER gating module references it at
        all: not validate_longform_flagship.py, not append_send_batch.py (the
        Law #166 blackout/recent-send/pending-batch checks live there and in
        tools/conflict_check.py, neither of which may read this log). This is
        the still-true, narrower half of the original guarantee -- see
        test_minimum_frequency_floor_is_the_only_reference_site below for the
        other half (confirming validate_dual_package.py's own reference is
        itself scoped to exactly one function)."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excluded_gating_files = [
            os.path.join(repo_root, "validators", "validate_longform_flagship.py"),
            os.path.join(repo_root, "tools", "append_send_batch.py"),
            os.path.join(repo_root, "tools", "conflict_check.py"),
        ]
        for path in excluded_gating_files:
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertNotIn("candidate_selection_log", content,
                              msg=f"{path} must never import/reference candidate_selection_log -- "
                                  "only _validate_minimum_frequency_floor in validate_dual_package.py "
                                  "is a sanctioned gating consumer (2026-08-22)")

    def test_minimum_frequency_floor_is_the_only_reference_site(self):
        """Confirms the OTHER half of the narrowed guarantee: within
        validate_dual_package.py itself, every CODE use of the imported
        symbols days_since_last_considered / read_events is textually
        confined to the sanctioned import block and the body of
        _validate_minimum_frequency_floor(). No other function in that file
        (e.g. the Law #166-style checks, _validate_format_type_eligibility,
        etc.) may call these symbols -- the 'exactly one documented consumer'
        claim in candidate_selection_log.py's module docstring is verified
        here, not just asserted in prose.

        Deliberately checks only the imported CALLABLE symbols
        (days_since_last_considered, read_events), not the bare string
        "candidate_selection_log" -- that string legitimately appears in
        explanatory comments elsewhere in the file (e.g. the call-site comment
        in validate_manifest() naming what _validate_minimum_frequency_floor
        does), and flagging prose mentions would either produce false
        failures or pressure someone into deleting honest documentation just
        to keep this test green. The OTHER test above already checks the full
        module-name string against the excluded gating files -- this test's
        job is narrower: confirm the two actual callables stay confined to one
        function inside this one file."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(repo_root, "validators", "validate_dual_package.py")
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()

        # Find _validate_minimum_frequency_floor's real line span by locating
        # its def and the next top-level (zero-indent) def/class after it.
        start = next(i for i, l in enumerate(lines) if l.startswith("def _validate_minimum_frequency_floor("))
        end = next(
            (i for i in range(start + 1, len(lines))
             if lines[i] and not lines[i][0].isspace() and (lines[i].startswith("def ") or lines[i].startswith("class "))),
            len(lines),
        )

        # The sanctioned import is a try/from-import/except/fallback-assignment
        # block, not a single line -- find its real span: the preceding "try:"
        # line, the "from ... import" line, the following "except ...:" line
        # (itself unindented), and that except block's indented fallback-
        # assignment body (the standard degrade-to-None-on-import-failure
        # pattern used throughout this file, e.g. check_recent_send_conflict
        # right above it).
        import_line_idx = next(
            i for i, l in enumerate(lines) if "from candidate_selection_log import" in l
        )
        import_block_start = import_line_idx - 1  # the preceding "try:" line
        except_line_idx = import_line_idx + 1
        assert lines[except_line_idx].startswith("except"), (
            f"expected an 'except' line immediately after the from-import at "
            f"line {import_line_idx + 1}, got {lines[except_line_idx]!r} -- import block shape changed"
        )
        import_block_end = except_line_idx + 1
        while import_block_end < len(lines) and lines[import_block_end][0].isspace():
            import_block_end += 1
        # import_block_end now points just past the except block's last
        # indented fallback-assignment line.

        # The module-level SCHEMA docstring documents the manifest JSON shape
        # in prose/comments and legitimately names these functions when
        # explaining the minimum_frequency_floor field -- it is not executable
        # code and is not a third call site. Exclude its real line span.
        schema_start = next(i for i, l in enumerate(lines) if l.startswith("SCHEMA = "))
        schema_end = next(i for i in range(schema_start + 1, len(lines)) if lines[i].rstrip() == '"""')

        relevant_tokens = ("days_since_last_considered", "read_events")

        # SECOND SANCTIONED READ SITE (added 2026-09-11, F71 selection-log
        # completeness). The guarantee this test protects is "log reads are
        # confined to auditable, named places," not "there is literally one
        # line." When F71's completeness check was added it deliberately did
        # NOT widen this into an open list of consuming functions -- instead
        # validate_manifest() performs one read at the top-level boundary and
        # passes the resulting events into the check as a parameter, so the
        # check itself contains no log read at all. That read site is named
        # explicitly here rather than matched loosely, so a third one still
        # fails this test.
        sanctioned_read_start = next(
            (i for i, l in enumerate(lines)
             if "selection-log completeness (F71 fix" in l), None)
        sanctioned_read_end = None
        if sanctioned_read_start is not None:
            sanctioned_read_end = next(
                (i for i in range(sanctioned_read_start, len(lines))
                 if "_validate_selection_log_completeness(m, r, _selection_events)" in lines[i]),
                sanctioned_read_start)

        for i, line in enumerate(lines):
            if not any(tok in line for tok in relevant_tokens):
                continue
            in_function_body = start < i < end
            in_sanctioned_import_block = import_block_start <= i < import_block_end
            in_schema_docstring = schema_start <= i <= schema_end
            in_f71_read_site = (
                sanctioned_read_start is not None
                and sanctioned_read_end is not None
                and sanctioned_read_start <= i <= sanctioned_read_end)
            self.assertTrue(
                in_function_body or in_sanctioned_import_block or in_schema_docstring
                or in_f71_read_site,
                msg=f"{path}:{i + 1} calls days_since_last_considered/read_events "
                    f"outside the sanctioned import block, _validate_minimum_frequency_floor "
                    f"body, SCHEMA docstring, and the F71 completeness read site: {line.strip()!r}",
            )


if __name__ == "__main__":
    unittest.main()

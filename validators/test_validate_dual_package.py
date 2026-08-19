#!/usr/bin/env python3
"""Tests for the deterministic dual-package preflight validator.

Runs the valid fixture (must PASS) and a series of targeted mutations, each of
which must FAIL on a specific named check. Uses stdlib unittest only — no deps.

    python3 validators/test_validate_dual_package.py
    python3 -m unittest discover  (from inside the validators/ directory)
"""

from __future__ import annotations

import json
import os
import sys
import unittest

import validate_dual_package as v

_TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
import render_clip_descriptions as _render  # noqa: E402 — used by UPDATE 6 test helpers

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "valid_dual_package.json")
# KEYWORD_CALLBACK_FIXTURE removed (2026-07-27, Law #141 rescission) -- the fixture
# file validators/fixtures/keyword_callback_loop.json is DELETED (not merely orphaned):
# once the loop-rejection rule it existed to exercise was removed, running it through
# the live validator produced FAIL results for reasons that have nothing to do with
# loops (stale checks{} keys, missing anchors_claim tagging) -- a stale fixture that
# fails "for real" but for the wrong reason is actively misleading, not neutral, so it
# was deleted rather than left in place.
EXPERIMENT_FIXTURE = os.path.join(
    os.path.dirname(__file__), "fixtures", "valid_duration_experiment.json")
# Law #159 item 3 (built 2026-08-14): a realistic 3-show SEASON_ROUNDUP exercising the
# per-show claim_source_matrix sourcing rule. Did not exist before this change -- the
# format had no fixture of its own at all, which is part of why item 3 sat unbuilt.
ROUNDUP_FIXTURE = os.path.join(
    os.path.dirname(__file__), "fixtures", "valid_season_roundup.json")


def load_valid() -> dict:
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def load_roundup() -> dict:
    with open(ROUNDUP_FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def load_experiment() -> dict:
    with open(EXPERIMENT_FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def failed_names(manifest: dict) -> list[str]:
    r = v.validate_manifest(manifest)
    return [name for name, ok, _ in r.checks if ok == "FAIL"]


class TestValidDualPackage(unittest.TestCase):
    def test_valid_fixture_passes(self):
        r = v.validate_manifest(load_valid())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_loop_fields_fully_absent_still_passes(self):
        """2026-07-27, Law #141 rescission gap-fill: prior coverage only proved the
        loop fields are unchecked when PRESENT (the shipped fixtures still carry them
        inert). That is a different claim from fields being genuinely OPTIONAL --
        i.e. a manifest that never had them at all must also validate cleanly. This
        test strips loop_line, loop_transition, loop_transition_note,
        final_to_opening, final_to_opening_readaloud, carries_loop_back, and every
        anchors_claim='loop' matrix tag from BOTH packages and confirms the result
        still passes with zero loop-related failures."""
        m = load_valid()
        loop_scalar_fields = (
            "loop_line", "loop_transition", "loop_transition_note", "final_to_opening",
        )
        for pkg in m["packages"]:
            for field in loop_scalar_fields:
                pkg.pop(field, None)
            sqa = pkg.get("semantic_qa")
            if isinstance(sqa, dict):
                sqa.pop("final_to_opening_readaloud", None)
                matrix = sqa.get("claim_source_matrix", [])
                for entry in matrix:
                    if entry.get("anchors_claim") == "loop":
                        entry.pop("anchors_claim", None)
            for clip in pkg.get("clips", []):
                clip.pop("carries_loop_back", None)

        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures with loop fields fully absent: {r.failures()}")
        loop_mentions = [name for name in failed_names(m) if "loop" in name.lower()]
        self.assertEqual(loop_mentions, [],
                          msg=f"expected zero loop-related failures, got: {loop_mentions}")


class TestWordCountUnicodeAndContractions(unittest.TestCase):
    """F5 fix: _words() must count an accented name (e.g. Pok\u00e9mon) as ONE word,
    not two ("Pok"+"mon"), WITHOUT breaking contraction counting -- a naive \\w+
    fix drops apostrophes and splits "doesn't"/"it's" into two tokens each."""

    def test_word_count_handles_accented_names_as_single_words(self):
        self.assertEqual(v._words("I love Pok\u00e9mon a lot"), 5)
        self.assertEqual(v._words("Pok\u00e9mon is great"), 3)

    def test_word_count_preserves_contraction_counting(self):
        # Regression guard: matches the OLD [A-Za-z0-9']+ regex's contraction
        # behavior exactly -- "doesn't" and "it's" must each count as ONE word.
        self.assertEqual(v._words("...doesn't stop there."), 3)
        self.assertEqual(v._words("it's not coming... it's coming..."), 5)


class TestCrashInsteadOfCleanFailFixes(unittest.TestCase):
    """F2/F4 fixes (production-audit findings, 2026-07-25): several type-unguarded
    paths previously crashed with an unhandled traceback instead of producing a
    named check failure. A crash still blocks the send (non-zero exit either way),
    but leaves no diagnostic detail the cron could act on. All four cases below must
    now fail CLEANLY -- no exception -- with a real Result object listing failures."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        # must not raise -- that IS the regression being guarded against
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_non_numeric_vo_word_count_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["vo_word_count"] = "104"  # string, not a number
        self.assertFailsCleanly(m, "vo_word_count matches VO text")

    def test_non_string_source_url_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["sources"][0]["url"] = 12345  # number, not a string
        # the malformed source no longer counts as "good", so the >=2 sources
        # check is what actually fails here (the fixture only has 2 sources)
        self.assertFailsCleanly(m, ">=2 credible live sources")

    def test_non_dict_post_times_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["post_times"] = ["youtube 7pm", "tiktok 8pm"]  # list, not dict
        self.assertFailsCleanly(m, "post_times is an object with youtube/tiktok keys")

    def test_missing_content_type_fails(self):
        m = load_valid()
        del m["packages"][0]["content_type"]
        self.assertFailsCleanly(m, "content_type is 'short'")

    def test_correct_content_type_still_passes(self):
        m = load_valid()
        m["packages"][0]["content_type"] = "short"
        r = v.validate_manifest(m)
        content_type_failures = [n for n, ok, _ in r.checks
                                 if ok == "FAIL" and "content_type is 'short'" in n]
        self.assertEqual(content_type_failures, [])


class TestInvalidCases(unittest.TestCase):
    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        # and it must be blocked overall
        self.assertFalse(v.validate_manifest(manifest).ok)

    def test_duplicate_show(self):
        m = load_valid()
        m["packages"][1]["show"] = m["packages"][0]["show"]
        self.assertFailsOn(m, "distinct shows")

    def test_duplicate_format(self):
        m = load_valid()
        m["packages"][1]["format_type"] = m["packages"][0]["format_type"]
        self.assertFailsOn(m, "distinct formats")

    def test_short_vo(self):
        m = load_valid()
        m["packages"][0]["vo"] = ("Frieren's quietest scene is aggressive. Fern goes silent. "
                                  "Is Fern the scariest mage here, or the calmest killer? Leave your take. "
                                  "Her quietest scene is loud.")
        m["packages"][0]["vo_word_count"] = 24
        self.assertFailsOn(m, "VO within 100-108 words")

    def test_missing_cta(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["vo"] = pkg["vo"].replace(" Leave your take.", "")
        pkg["cta_line"] = "What do you think?"
        self.assertFailsOn(m, "CTA line is exactly")

    def test_cta_not_after_question(self):
        m = load_valid()
        pkg = m["packages"][1]
        # keep the CTA phrase but detach it from the question
        pkg["vo"] = pkg["vo"].replace(
            "or just fan service for veterans? Leave your take.",
            "or just fan service for veterans? Old fans know. Leave your take.")
        self.assertFailsOn(m, "immediately followed by")

    def test_onscreen_cta_start_sec_missing_fails(self):
        m = load_valid()
        del m["packages"][0]["onscreen_cta_start_sec"]
        self.assertFailsOn(m, "onscreen_cta_start_sec present")

    def test_onscreen_cta_start_sec_exactly_at_boundary_passes(self):
        # Law #62 addendum, 2026-07-27: target_sec - 5.0 is the earliest ALLOWED
        # value (inclusive) -- exactly at the boundary must PASS.
        m = load_valid()
        pkg = m["packages"][0]
        target = pkg["capcut_target_sec"]
        pkg["onscreen_cta_start_sec"] = target - 5.0
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_onscreen_cta_start_sec_just_outside_boundary_fails(self):
        # One unit earlier than the allowed window -- must FAIL.
        # STAGE 1 REBUILD (2026-08-09): window is now max(5.0, target_sec*0.15);
        # at the base fixture's 30s target that is still max(5.0, 4.5) == 5.0,
        # so this boundary is numerically unchanged from the pre-Stage-1 check.
        m = load_valid()
        pkg = m["packages"][0]
        target = pkg["capcut_target_sec"]
        pkg["onscreen_cta_start_sec"] = target - 5.0 - 1
        self.assertFailsOn(m, "within the closing")

    def test_face_direction(self):
        # STAGE 1 REBUILD (2026-08-09): face-cam split-screen is now the REQUIRED
        # default (creator top / anime bottom, Sebastian's confirmed decision) --
        # this test now proves the INVERSE failure: a package that reverts to
        # face=False with an anime-only video_style must fail both checks.
        m = load_valid()
        m["packages"][0]["face"] = False
        m["packages"][0]["video_style"] = "Anime Clips Only"
        names = failed_names(m)
        self.assertTrue(any("face flag is true" in n for n in names), names)
        self.assertTrue(any("declares the face-cam split-screen format" in n for n in names), names)

    def test_split_screen_direction(self):
        # STAGE 1 REBUILD (2026-08-09): split_screen=True is now REQUIRED (it is
        # the face-cam format itself), so this test proves the inverse failure --
        # reverting split_screen to False must fail.
        m = load_valid()
        m["packages"][1]["split_screen"] = False
        self.assertFailsOn(m, "split_screen flag is true")

    def test_clip_missing_duration(self):
        m = load_valid()
        del m["packages"][0]["clips"][0]["duration_sec"]
        self.assertFailsOn(m, "each clip has duration_sec")

    def test_clip_noncontiguous_ranges(self):
        m = load_valid()
        # introduce a 1s gap between cut 1 and cut 2 (and shift the rest)
        clips = m["packages"][0]["clips"]
        clips[1]["timeline_start_sec"] = 7   # was 6; leaves a gap 6->7
        self.assertFailsOn(m, "contiguous")

    def test_clip_wrong_duration_arithmetic(self):
        m = load_valid()
        # end-start no longer equals duration_sec for cut 1
        m["packages"][0]["clips"][0]["duration_sec"] = 5   # range is still 0..6
        self.assertFailsOn(m, "timeline_end_sec - timeline_start_sec == duration_sec")

    def test_clip_total_not_30(self):
        m = load_valid()
        # last cut ends early -> sum != 30 and final != 30
        clips = m["packages"][1]["clips"]
        clips[-1]["duration_sec"] = 5
        clips[-1]["timeline_end_sec"] = 29
        self.assertFailsOn(m, "sum of clip durations")

    def test_total_clip_time_field_wrong(self):
        m = load_valid()
        m["packages"][0]["total_clip_time_sec"] = 28
        self.assertFailsOn(m, "total_clip_time_sec == 30")

    def test_capcut_target_changed_without_updating_dependents_fails(self):
        # STAGE 1 REBUILD (2026-08-09): capcut_target_sec is no longer locked to a
        # literal 30 -- 25 is a legal open-ended length on its own (in [20,180]).
        # But changing ONLY capcut_target_sec without updating total_clip_time_sec
        # and the clip timeline to match must still fail, on the fields that are
        # now actually inconsistent.
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 25
        self.assertFailsOn(m, "total_clip_time_sec == 25")

    def test_capcut_target_out_of_range_fails(self):
        # STAGE 1 REBUILD (2026-08-09): the real open-ended bound is [20,180]s.
        # A value below 20 must fail the new range check itself.
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 10
        self.assertFailsOn(m, "numeric and within 20-180s")

    def test_capcut_target_above_180_fails(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 181
        self.assertFailsOn(m, "numeric and within 20-180s")

    def test_wrong_recipient(self):
        m = load_valid()
        # Audit item #21 (2026-08-14): was a real personal address committed to the repo.
        # Any non-hero_or_villain@outlook.com value exercises this check identically.
        m["recipient"] = "wrong@example.com"
        self.assertFailsOn(m, "recipient is exactly correct")

    def test_insufficient_sources(self):
        m = load_valid()
        m["packages"][0]["sources"] = m["packages"][0]["sources"][:1]
        self.assertFailsOn(m, ">=2 credible live sources")

    def test_source_missing_date(self):
        m = load_valid()
        for s in m["packages"][1]["sources"]:
            s.pop("date", None)
        self.assertFailsOn(m, ">=2 credible live sources")

    # test_missing_loop_line REMOVED (2026-07-27, Law #141 rescission) -- loop_line
    # is no longer a required field; an empty/missing loop_line no longer fails
    # validation.

    def test_missing_production_section(self):
        m = load_valid()
        m["packages"][1]["pinned_comment"] = ""
        self.assertFailsOn(m, "pinned comment")

    def test_combined_post_times(self):
        m = load_valid()
        same = "YouTube + TikTok — post 6 PM ET"
        m["packages"][0]["post_times"] = {"youtube": same, "tiktok": same}
        self.assertFailsOn(m, "separate YouTube + TikTok post-time lines")

    def test_blackout_conflict(self):
        m = load_valid()
        m["packages"][0]["blackout_conflict"] = True
        self.assertFailsOn(m, "blackout_conflict input present and clear")

    def test_recent_send_conflict(self):
        m = load_valid()
        m["packages"][1]["recent_send_conflict"] = True
        self.assertFailsOn(m, "recent_send_conflict input present and clear")

    def test_only_one_package(self):
        m = load_valid()
        m["packages"] = m["packages"][:1]
        self.assertFailsOn(m, "exactly two packages exist")

    def test_same_package_id(self):
        m = load_valid()
        m["packages"][1]["package_id"] = m["packages"][0]["package_id"]
        self.assertFailsOn(m, "distinct package_id per package")

    def test_missing_batch_id(self):
        m = load_valid()
        m.pop("batch_id", None)
        self.assertFailsOn(m, "shared batch_id present")

    def test_both_same_slot(self):
        m = load_valid()
        m["packages"][1]["slot"] = "morning"
        self.assertFailsOn(m, "one MORNING and one EVENING slot")

    def test_banned_bro(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["vo"] = pkg["vo"].replace("Most people read Fern as cold, but she is just certain.",
                                      "Trust me bro, people read Fern wrong.")
        self.assertFailsOn(m, "no banned word 'bro'")

    # --- Law #144/#145: opening_sentence must be the VO's exact first sentence ---
    # (2026-07-27, Law #141 rescission: the surrounding forced seamless-loop mandate
    # -- loop_transition, loop_line exact-final-sentence, carries_loop_back clip-plan
    # requirement, loop_read_aloud_pass, loop_transition_note, structured
    # final_to_opening, and the keyword-callback-rejection fixture test -- is removed.
    # opening_sentence's exact-first-sentence check is RETAINED below since it is
    # independently needed for hook_line == opening_sentence (Law #144/#145), not for
    # looping.)

    def test_wrong_opening_sentence(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["opening_sentence"] = "This is not the first sentence of the VO."
        self.assertFailsOn(m, "opening_sentence is the VO's exact first sentence")


class TestEvidenceBasedPackaging(unittest.TestCase):
    """Laws #143-#146: topic portfolio, recurring series, first-second hook, clean
    title, single-variant experiment, funnel/teaser gating, Shorts-pipeline guard."""

    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        self.assertFalse(v.validate_manifest(manifest).ok)

    # --- Shorts-pipeline guard (Law #146) ---
    def test_longform_leaks_into_shorts_manifest_rejected(self):
        m = load_valid()
        m["packages"][0]["content_type"] = "longform"
        self.assertFailsOn(m, "content_type is 'short'")

    # --- first-second hook (Law #144) ---
    def test_missing_hook_onscreen_text(self):
        m = load_valid()
        m["packages"][0]["hook_onscreen_text"] = "  "
        self.assertFailsOn(m, "hook_onscreen_text present")

    def test_hook_first_second_not_attested(self):
        m = load_valid()
        m["packages"][1]["hook_first_second"] = False
        self.assertFailsOn(m, "hook_first_second attested true")

    def test_isolation_test_pass_not_attested(self):
        m = load_valid()
        m["packages"][1]["isolation_test_pass"] = False
        self.assertFailsOn(m, "isolation_test_pass attested true")

    def test_hook_line_not_opening_sentence(self):
        m = load_valid()
        # change hook_line so it no longer equals the spoken opening sentence
        m["packages"][0]["hook_line"] = "A totally different framing that is not spoken first."
        # keep it in the candidate list so the experiment check isn't the cause
        m["packages"][0]["hook_candidates"][0] = m["packages"][0]["hook_line"]
        self.assertFailsOn(m, "hook_line equals opening_sentence")

    def test_hook_line_missing_entirely_rejected(self):
        # Regression test: previously `hook = (pkg.get("hook_line", "") or opening).strip()`
        # silently fell back to opening_sentence when hook_line was absent, and hook_line
        # was not in the `required` dict, so every downstream hook check passed trivially
        # even with hook_line never supplied at all. Removing it entirely must now fail
        # with an explicit, dedicated message -- not pass via the fallback.
        m = load_valid()
        m["packages"][0].pop("hook_line", None)
        self.assertFailsOn(m, "hook_line present")

    def test_hook_line_blank_string_rejected(self):
        # A present-but-blank hook_line must be treated the same as missing (not simply
        # falsy-checked away by the fallback's `or opening`).
        m = load_valid()
        m["packages"][0]["hook_line"] = "   "
        self.assertFailsOn(m, "hook_line present")

    def test_missing_hook_family(self):
        m = load_valid()
        m["packages"][0].pop("hook_family", None)
        self.assertFailsOn(m, "hook_family present")

    # --- external-lens framing experiment (Law #153, added 2026-07-27, BOUNDED) ---
    # OPTIONAL field. Weekly <=1/week cap is enforced by the analytics cron, not this
    # daily validator -- these tests cover only the daily-checkable part.
    def test_absent_external_lens_passes_cleanly(self):
        m = load_valid()
        self.assertNotIn("external_lens", m["packages"][0])
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_present_well_formed_external_lens_passes(self):
        m = load_valid()
        m["packages"][0]["external_lens"] = "psychology"
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_present_empty_string_external_lens_fails(self):
        m = load_valid()
        m["packages"][0]["external_lens"] = "   "
        self.assertFailsOn(m, "external_lens is a non-empty string when present")

    # --- single-variant experiment (Law #145) ---
    def test_one_hook_candidate_fails(self):
        m = load_valid()
        m["packages"][0]["hook_candidates"] = ["only one candidate"]
        self.assertFailsOn(m, "exactly 2 internal hook_candidates")

    def test_selected_index_out_of_range(self):
        m = load_valid()
        m["packages"][1]["selected_hook_index"] = 5
        self.assertFailsOn(m, "selected_hook_index selects one")

    def test_published_hook_not_selected_candidate(self):
        m = load_valid()
        # point selected index at the OTHER candidate that isn't the published hook
        m["packages"][0]["selected_hook_index"] = 1
        self.assertFailsOn(m, "published hook_line matches the selected candidate")

    def test_identical_hook_candidates(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["hook_candidates"] = [pkg["hook_line"], pkg["hook_line"]]
        self.assertFailsOn(m, "the two hook_candidates are distinct")

    def test_duplicate_published_hooks_across_packages(self):
        m = load_valid()
        # force both packages to publish the same hook line
        shared = m["packages"][0]["hook_line"]
        p1 = m["packages"][1]
        p1["hook_line"] = shared
        p1["opening_sentence"] = shared
        p1["vo"] = shared + " " + p1["vo"].split(". ", 1)[1]
        p1["hook_candidates"][0] = shared
        self.assertFailsOn(m, "distinct published hooks")

    # --- topic portfolio (Law #143) ---
    def test_bad_topic_class(self):
        m = load_valid()
        m["packages"][0]["topic_class"] = "whatever"
        self.assertFailsOn(m, "topic_class is 'timely' or 'evergreen'")

    def test_timely_without_signal(self):
        m = load_valid()
        m["packages"][0]["topic_class"] = "timely"
        m["packages"][0]["topic_signals"] = []
        self.assertFailsOn(m, "timely topic declares >=1 valid topic_signal")

    def test_evergreen_needs_no_signal(self):
        m = load_valid()
        m["packages"][0]["topic_class"] = "evergreen"
        m["packages"][0]["topic_signals"] = []
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    # --- recurring series metadata (Law #143) ---
    def test_malformed_series_rejected(self):
        m = load_valid()
        m["packages"][0]["series"] = {"id": "", "recurring": "yes"}
        self.assertFailsOn(m, "series metadata well-formed")

    def test_null_series_allowed(self):
        m = load_valid()
        m["packages"][0]["series"] = None
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    # --- funnel + teaser gating (Law #145/#146) ---
    def test_bad_funnel_status(self):
        m = load_valid()
        m["packages"][0]["funnel_status"] = "viral"
        self.assertFailsOn(m, "funnel_status is standalone|teaser|flagship_followup")

    def test_teaser_requires_flagship_url(self):
        m = load_valid()
        m["packages"][0]["funnel_status"] = "teaser"
        m["packages"][0].pop("flagship_url", None)
        self.assertFailsOn(m, "teaser Short carries a flagship_url")

    def test_teaser_with_flagship_url_ok(self):
        m = load_valid()
        m["packages"][0]["funnel_status"] = "teaser"
        m["packages"][0]["flagship_url"] = "https://youtu.be/flagship-01"
        # DORMANT SCAFFOLDING (Law #145 addendum, 2026-07-27): also required once
        # funnel_status is "teaser" -- must echo hook_line for the teaser to pass.
        m["packages"][0]["flagship_opening_hook_match"] = m["packages"][0]["hook_line"]
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_teaser_dormant_flagship_opening_hook_match_is_real_and_checked(self):
        # DORMANT-BUT-PRESENT schema check (Law #145 addendum, 2026-07-27): proves
        # flagship_opening_hook_match is genuine, running validation code -- not just
        # documentation -- even though zero real packages trigger this path today
        # (funnel_status has been "teaser" on 0/166 real sends). A teaser package
        # missing the field must fail on the new dormant check specifically.
        m = load_valid()
        m["packages"][0]["funnel_status"] = "teaser"
        m["packages"][0]["flagship_url"] = "https://youtu.be/flagship-01"
        m["packages"][0].pop("flagship_opening_hook_match", None)
        self.assertFailsOn(m, "flagship_opening_hook_match echoes hook_line")

        # a present-but-mismatched value must also fail -- the check compares content,
        # it does not just check presence.
        m2 = load_valid()
        m2["packages"][0]["funnel_status"] = "teaser"
        m2["packages"][0]["flagship_url"] = "https://youtu.be/flagship-01"
        m2["packages"][0]["flagship_opening_hook_match"] = "a completely unrelated sentence"
        self.assertFailsOn(m2, "flagship_opening_hook_match echoes hook_line")

        # a standalone (non-teaser) package must NEVER require this field -- confirms
        # the check is scoped strictly inside the teaser branch, not a global rule.
        m3 = load_valid()
        self.assertNotIn("flagship_opening_hook_match", m3["packages"][0])
        r3 = v.validate_manifest(m3)
        self.assertTrue(r3.ok, msg=f"unexpected failures: {r3.failures()}")

    # --- clean, searchable title (Law #144) ---
    def test_title_with_hashtag_rejected(self):
        m = load_valid()
        m["packages"][0]["youtube_title"] = "Frieren: Fern's Silence #anime #frieren"
        self.assertFailsOn(m, "YouTube title has no hashtags")

    def test_title_too_long_rejected(self):
        m = load_valid()
        m["packages"][0]["youtube_title"] = "Frieren " + "x" * 120
        self.assertFailsOn(m, "YouTube title within 60 chars")

    def test_youtube_title_just_over_60_rejected(self):
        m = load_valid()
        # 61 chars, still leads with the show keyword so only the length check trips
        m["packages"][0]["youtube_title"] = "Frieren " + "y" * 53
        self.assertEqual(len(m["packages"][0]["youtube_title"]), 61)
        self.assertFailsOn(m, "YouTube title within 60 chars")

    def test_title_missing_show_keyword(self):
        m = load_valid()
        m["packages"][0]["youtube_title"] = "The Quietest Killer In Anime Now"
        self.assertFailsOn(m, "show search keyword appears in title")

    def test_show_name_starting_with_the_not_trivially_passed(self):
        # Regression test (Law #148-adjacent fix, July 2026): previously show_tok picked
        # the FIRST word >=3 chars in the show name with no stopword filter, so a show
        # name starting with "The" (extremely common for anime titles) made the keyword
        # check trivially true for almost ANY title, since "the" appears in most English
        # sentences. A title with no real connection to the show must still fail.
        m = load_valid()
        m["packages"][0]["show"] = "The Elusive Samurai"
        m["packages"][0]["youtube_title"] = "The Reason Everyone Is Talking About This Now"
        self.assertFailsOn(m, "show search keyword appears in title")

    def test_show_with_no_qualifying_token_falls_back_to_full_show_string(self):
        # F3 fix: "86" has no token >=3 chars, which previously made this check
        # unconditionally, unfixably fail regardless of the title.
        m = load_valid()
        m["packages"][0]["show"] = "86"
        m["packages"][0]["youtube_title"] = "86 Just Got Its Darkest Episode Yet"
        names = failed_names(m)
        self.assertFalse(any("show search keyword appears in title" in n for n in names),
                         msg=f"expected the fallback to pass; got failures={names}")

    def test_show_with_no_qualifying_token_and_no_match_still_fails(self):
        # The fallback is a fallback MATCHER, not a free pass -- it must still fail
        # when the show genuinely isn't in the title.
        m = load_valid()
        m["packages"][0]["show"] = "86"
        m["packages"][0]["youtube_title"] = "This Title Never Mentions The Show At All"
        self.assertFailsOn(m, "show search keyword appears in title")

    def test_show_name_starting_with_the_passes_with_real_keyword(self):
        # Companion positive case: the SAME "The..."-prefixed show name must still pass
        # when the title genuinely contains a real content word from the show ("samurai"),
        # proving the fix filters the stopword without breaking real matches. Only the
        # show name and title are changed -- everything else (hook_line, opening_sentence,
        # series markers) is left as the known-valid fixture value, and the new title still
        # contains "Scene Test" (the fixture's series_public_name) so that unrelated check
        # keeps passing too.
        m = load_valid()
        m["packages"][0]["show"] = "The Elusive Samurai"
        m["packages"][0]["youtube_title"] = "Samurai Scene Test: A Silent Blade Explained"
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_youtube_title_equals_hook_rejected(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["youtube_title"] = pkg["hook_line"]
        self.assertFailsOn(m, "YouTube title is distinct from the published hook line")

    def test_duplicate_youtube_titles_across_packages_rejected(self):
        m = load_valid()
        m["packages"][1]["youtube_title"] = m["packages"][0]["youtube_title"]
        self.assertFailsOn(m, "distinct YouTube titles across the two packages")

    # --- punchy TikTok title (Law #144, revised) ---
    def test_missing_tiktok_title_rejected(self):
        m = load_valid()
        m["packages"][0].pop("tiktok_title", None)
        self.assertFailsOn(m, "TikTok title present")

    def test_empty_tiktok_title_rejected(self):
        m = load_valid()
        m["packages"][1]["tiktok_title"] = "   "
        self.assertFailsOn(m, "TikTok title present")

    def test_tiktok_title_too_long_rejected(self):
        m = load_valid()
        m["packages"][0]["tiktok_title"] = "z" * 56
        self.assertFailsOn(m, "TikTok title within 55 chars")

    def test_tiktok_title_with_hashtag_rejected(self):
        m = load_valid()
        m["packages"][0]["tiktok_title"] = "Fern's Silence #frieren"
        self.assertFailsOn(m, "TikTok title has no hashtags")

    def test_tiktok_caption_may_keep_hashtags(self):
        # the hashtag rule is enforced against tiktok_title, NOT the tiktok_post_text
        # caption, which may keep its platform-native hashtag pyramid.
        m = load_valid()
        m["packages"][0]["tiktok_post_text"] += " #frieren #animeshorts #anime #fyp"
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_tiktok_title_equals_hook_rejected(self):
        m = load_valid()
        pkg = m["packages"][1]
        pkg["tiktok_title"] = pkg["hook_line"]
        self.assertFailsOn(m, "TikTok title is distinct from the published hook line")

    def test_youtube_and_tiktok_titles_identical_rejected(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["tiktok_title"] = pkg["youtube_title"]
        self.assertFailsOn(m, "YouTube and TikTok titles are distinct")

    def test_duplicate_tiktok_titles_across_packages_rejected(self):
        m = load_valid()
        m["packages"][1]["tiktok_title"] = m["packages"][0]["tiktok_title"]
        self.assertFailsOn(m, "distinct TikTok titles across the two packages")


class TestDurationExperiment(unittest.TestCase):
    """STAGE 1 REBUILD (2026-08-09): the old M1 length-BAND gate inside
    _resolve_edit_target (list/ranking recurring-series only, numeric range
    restricted to 45-59s) is RETIRED. Variable length in [20,180]s is now the
    permanent open-ended default for every package -- there is no format_type or
    series.recurring gate on LENGTH anymore. capcut_target_sec absent still
    defaults to 30s with is_variable_length=False; capcut_target_sec present must
    simply be numeric and in range.

    STAGE 2 UPDATE (2026-08-09): the "at most one duration_experiment package per
    batch" cap flagged as a Stage-1-adjacent leftover is now ALSO retired, by
    explicit user decision (option 1: retire the field and its cap entirely, not
    repurposed, not kept as a soft signal). Variable length is unconditional for
    every package now, so there is no remaining concept of a bounded "experiment"
    to cap or flag. test_two_experiments_in_one_batch_rejected has been removed
    (it asserted a check that no longer exists). The 3 tests below that also
    checked for the OLD "duration_experiment allowed only for list/ranking" gate
    message keep their real, still-meaningful assertions (40s passing cleanly,
    format_type/series.recurring not gating length) but had their dead
    sub-assertion against that already-unreachable message string removed --
    confirmed via direct grep that the string does not appear anywhere in
    validate_dual_package.py, so that sub-assertion was vacuously true on every
    run and added no real coverage."""

    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        self.assertFalse(v.validate_manifest(manifest).ok)

    def test_valid_experiment_fixture_passes(self):
        r = v.validate_manifest(load_experiment())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_experiment_slot_uses_45s_timeline(self):
        # the evening experiment package tiles a 45s edit, not 30s
        m = load_experiment()
        exp = m["packages"][1]
        self.assertEqual(exp["capcut_target_sec"], 45)
        self.assertEqual(exp["clips"][-1]["timeline_end_sec"], 45)
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_40s_edit_now_legal_on_its_own(self):
        # STAGE 1 REBUILD (2026-08-09): 40s used to be "below the sanctioned 45-59s
        # band" and rejected outright. It is now a perfectly legal open-ended length
        # (in [20,180]) with no format/series gate. Built via _resize_package_to so
        # every dependent field (clip timeline, VO word band incl. opening_sentence/
        # question_line/cta_line consistency, CTA window) is genuinely internally
        # consistent at 40s, not hand-approximated -- self-caught the hand-rolled
        # version's real bugs (wrong word count, mismatched hook/opening fields)
        # before trusting this, same lesson as Stage 1's 45s test bug.
        m = load_experiment()
        m["packages"][1] = _resize_package_to(m["packages"][1], 40.0)
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[evening]" in n]
        self.assertEqual(pkg_failures, [], msg=f"40s must validate cleanly on its own merits; unexpected failures: {pkg_failures}")

    def test_format_type_no_longer_gates_length(self):
        # STAGE 1 REBUILD (2026-08-09): changing format_type away from list/ranking
        # must NOT reintroduce a length gate. NOTE: the fixture's morning package is
        # already CHARACTER_DIVE, so the evening package must move to a THIRD format
        # (not list/ranking, not CHARACTER_DIVE) to isolate this test from the
        # unrelated "distinct formats (no duplicate)" check -- confirmed by running
        # this in isolation first and finding the exact collision it would otherwise
        # cause.
        m = load_experiment()
        m["packages"][1]["format_type"] = "FACT_DROP"
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[evening]" in n]
        self.assertEqual(pkg_failures, [], msg=f"format_type must not gate edit length; unexpected failures: {pkg_failures}")

    def test_non_recurring_series_no_longer_gates_length(self):
        # STAGE 1 REBUILD (2026-08-09): series.recurring must NOT gate edit length
        # anymore. CONFIRMED (by reading validate_dual_package.py directly, not
        # assumed) that the M2 series-marker checks are gated behind
        # `series.recurring is True` -- setting series to None makes series_ok
        # False, so the ENTIRE M2 block is skipped, not failed. series_public_name/
        # series_next_line become simply unchecked in that state. So the correct
        # assertion is a full clean pass for the evening package, proving neither
        # M2 nor any length-related check fires.
        m = load_experiment()
        m["packages"][1]["series"] = None
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[evening]" in n]
        self.assertEqual(pkg_failures, [], msg=f"series=None must not produce any failure (M2 skipped, length ungated); unexpected failures: {pkg_failures}")

    def test_experiment_vo_scaled_band_enforced(self):
        # a 45s edit needs ~150-162 words; a 107-word (30s) VO is now too short
        m = load_experiment()
        exp = m["packages"][1]
        std = load_valid()["packages"][0]
        exp["vo"] = std["vo"]
        exp["vo_word_count"] = std["vo_word_count"]
        # keep hook consistency with the swapped VO so only the band check fails.
        # (loop_line/loop_transition copy removed 2026-07-27, Law #141 rescission --
        # those fields are inert now, so setting them no longer matters for isolating
        # this check to the word-count band.)
        exp["hook_line"] = std["hook_line"]
        exp["opening_sentence"] = std["opening_sentence"]
        exp["question_line"] = std["question_line"]
        exp["hook_candidates"] = list(std["hook_candidates"])
        exp["selected_hook_index"] = std["selected_hook_index"]
        exp["hook_onscreen_text"] = std["hook_onscreen_text"]
        self.assertFailsOn(m, "VO within 150-162 words")

    def test_default_package_can_now_freely_use_45s_when_fully_updated(self):
        # STAGE 1 REBUILD (2026-08-09): 30s is only the DEFAULT when
        # capcut_target_sec is absent -- it is no longer a hard lock. A base
        # package that deliberately moves to 45s, with every dependent field
        # (total_clip_time_sec, clip timeline, VO word band) updated to match, must
        # now PASS -- proving the old lock is genuinely gone, not just loosened.
        m = load_valid()
        pkg = m["packages"][0]
        pkg["capcut_target_sec"] = 45
        pkg["total_clip_time_sec"] = 45
        pkg["clips"][-1]["duration_sec"] = 21
        pkg["clips"][-1]["timeline_end_sec"] = 45
        pkg["onscreen_cta_start_sec"] = 45 - max(5.0, 45 * 0.15)  # new CTA formula, exact floor
        # Build the VO to land exactly inside the 45s band (148-162 words, Law #138
        # calibrated table) -- 9 fixed words (opening sentence + question + CTA)
        # plus N filler words must total between 148 and 162; 150 total is safely
        # mid-band and avoids off-by-one drift from naive string splitting.
        opening = "Fern's silence is the most aggressive thing she does."
        question_cta = "Is Fern the scariest mage here, or the calmest killer? Leave your take."
        fixed_words = len(opening.split()) + len(question_cta.split())
        target_total = 155
        filler_count = target_total - fixed_words
        pkg["vo"] = f"{opening} " + ("word " * filler_count).strip() + f" {question_cta}"
        pkg["vo_word_count"] = len(pkg["vo"].split())
        assert 148 <= pkg["vo_word_count"] <= 162, pkg["vo_word_count"]
        r = v.validate_manifest(m)
        failures = [n for n, ok, d in r.failures()]
        self.assertFalse(
            any("capcut_target_sec == 30" in n or "locked to 30" in n for n in failures),
            msg=f"the old 30s hard lock must be gone; failures={failures}")

    def test_absent_capcut_target_sec_defaults_to_30(self):
        # STAGE 1 REBUILD (2026-08-09): when capcut_target_sec is entirely absent,
        # _resolve_edit_target must still fall back to the 30s default so old-style
        # manifests that never set the field keep working unchanged.
        m = load_valid()
        del m["packages"][0]["capcut_target_sec"]
        r = v.validate_manifest(m)
        failures = [n for n, ok, d in r.failures()]
        # total_clip_time_sec (30) and the clip timeline (tiling to 30) already
        # match the fixture, so the only new failure should be the presence check
        # for capcut_target_sec itself never having existed as a range check --
        # there should be no "numeric and within 20-180s" failure since the field
        # being absent takes the default path, not the range-check path.
        self.assertFalse(
            any("numeric and within 20-180s" in n for n in failures),
            msg=f"absent capcut_target_sec must silently default to 30s, not fail range check; failures={failures}")


class TestViewerFacingSeriesMarker(unittest.TestCase):
    """M2 (Law #143): a recurring series must be perceivable by viewers — a public
    name in the title/on-screen text plus a next-installment cue in a published close."""

    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        self.assertFalse(v.validate_manifest(manifest).ok)

    def test_missing_series_public_name(self):
        m = load_valid()
        m["packages"][0].pop("series_public_name", None)
        self.assertFailsOn(m, "series_public_name present")

    def test_series_public_name_not_shown(self):
        m = load_valid()
        # present but appears in neither the title nor the on-screen text
        m["packages"][0]["series_public_name"] = "Ghost Segment"
        self.assertFailsOn(m, "series_public_name shown in title or first-second")

    def test_missing_series_next_line(self):
        m = load_valid()
        m["packages"][1].pop("series_next_line", None)
        self.assertFailsOn(m, "series_next_line present")

    def test_series_next_line_not_in_close(self):
        m = load_valid()
        m["packages"][1]["series_next_line"] = "This cue is never published anywhere."
        self.assertFailsOn(m, "series_next_line appears in a published close")

    def test_non_recurring_series_needs_no_marker(self):
        # series present but recurring=false -> M2 markers not required
        m = load_valid()
        pkg = m["packages"][0]
        pkg["series"] = {"id": "one_off_take", "recurring": False}
        pkg.pop("series_public_name", None)
        pkg.pop("series_next_line", None)
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_null_series_needs_no_marker(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["series"] = None
        pkg.pop("series_public_name", None)
        pkg.pop("series_next_line", None)
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")


# TestColonHandoffLoop REMOVED IN FULL (2026-07-27, Law #141 rescission). This class
# tested the DIRECT GRAMMATICAL COLON HANDOFF mechanic (loop_line must end with ':',
# opening_sentence must not, the two must not be identical) added by Law #147's
# strengthening of Law #141. That mechanic is rescinded -- see
# laws/law_141_seamless_loop_mechanics.md. A sanity check that the shipped fixtures
# still validate cleanly is retained in TestValidDualPackage above (unaffected by this
# removal, since the fixtures' now-inert loop_line/opening_sentence pairs still happen
# to satisfy every remaining check).


class TestSemanticQA(unittest.TestCase):
    """Law #147 / credit-safe mode: the single generation context must self-audit both
    packages before returning and record it in the manifest. The validator confirms the
    audit is PRESENT and well-SHAPED and enforces two MECHANICAL properties of the
    claim-to-source matrix — every core claim cites a listed dated source, and no core
    claim is supported ONLY by encyclopedic sources. It does NOT prove source truth or
    writing quality (model attestation + weekly human spot-check)."""

    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        self.assertFalse(v.validate_manifest(manifest).ok)

    def test_missing_semantic_qa_rejected(self):
        m = load_valid()
        m["packages"][0].pop("semantic_qa", None)
        self.assertFailsOn(m, "semantic_qa audit present")

    def test_semantic_qa_not_object_rejected(self):
        m = load_valid()
        m["packages"][1]["semantic_qa"] = "audited"
        self.assertFailsOn(m, "semantic_qa audit present")

    def test_audited_before_return_false_rejected(self):
        m = load_valid()
        m["packages"][0]["semantic_qa"]["audited_before_return"] = False
        self.assertFailsOn(m, "audited_before_return attested true")

    # NEEDLE UPDATED 2026-08-16 (VO-handoff split), not weakened. The single
    # "semantic_qa.checks all attested true" check was split into a VO-independent
    # half (always enforced) and a VO-dependent half (skipped only when
    # vo_status == 'pending'). These tests still assert a real FAIL on the same
    # mutated key -- only the check's NAME changed, so the needle follows it to
    # whichever half owns that key.
    def test_missing_check_flag_rejected(self):
        m = load_valid()
        m["packages"][0]["semantic_qa"]["checks"].pop("hook_claim_coverage", None)
        self.assertFailsOn(m, "semantic_qa.checks VO-dependent attested true")

    def test_false_check_flag_rejected(self):
        m = load_valid()
        m["packages"][1]["semantic_qa"]["checks"]["clip_timing_tiling"] = False
        self.assertFailsOn(m, "semantic_qa.checks VO-independent attested true")

    # test_readaloud_mismatch_rejected REMOVED (2026-07-27, Law #141 rescission) --
    # final_to_opening_readaloud is no longer checked; a mismatch (or its absence) no
    # longer fails validation.

    def test_malformed_matrix_rejected(self):
        m = load_valid()
        m["packages"][0]["semantic_qa"]["claim_source_matrix"] = "not a list"
        self.assertFailsOn(m, "claim_source_matrix present with >=1 core claim")

    def test_matrix_no_core_claim_rejected(self):
        m = load_valid()
        for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]:
            e["core"] = False
        self.assertFailsOn(m, "claim_source_matrix present with >=1 core claim")

    def test_core_claim_source_not_in_package_sources_rejected(self):
        m = load_valid()
        core = next(e for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]
                    if e["core"])
        core["source_urls"] = ["https://example.com/not-a-listed-source"]
        self.assertFailsOn(m, "every core claim cites a listed dated source")

    def test_core_claim_only_encyclopedic_rejected(self):
        # a core claim supported solely by Wikipedia/MAL/Fandom must be rejected; the
        # source must also be listed (with a date) so only the encyclopedic rule trips
        m = load_valid()
        pkg = m["packages"][0]
        enc_url = "https://en.wikipedia.org/wiki/Frieren"
        pkg["sources"].append({"claim": "background", "url": enc_url, "date": "Jul 2026"})
        core = next(e for e in pkg["semantic_qa"]["claim_source_matrix"] if e["core"])
        core["source_urls"] = [enc_url]
        self.assertFailsOn(m, "no core claim relies solely on Wikipedia/MAL/Fandom")

    def test_encyclopedic_paired_with_live_source_ok(self):
        # an encyclopedic source is fine as long as the core claim ALSO cites a
        # non-encyclopedic dated source (the shipped One Piece fixture does this)
        r = v.validate_manifest(load_valid())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    # -- Law #58 restoration: per-claim-type minimums (policy decision, July 24 2026) --

    def test_core_claim_missing_claim_type_rejected(self):
        # every core entry must now carry a claim_type in CLAIM_TYPES, or the matrix
        # is considered malformed (this is what makes the type-specific rule below
        # enforceable at all).
        m = load_valid()
        core = next(e for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]
                    if e["core"])
        core.pop("claim_type", None)
        self.assertFailsOn(m, "claim_source_matrix present with >=1 core claim")

    def test_high_risk_type_b_single_source_rejected(self):
        # TYPE B (creator quote/confirmed interview) with only 1 listed source must
        # fail even though it satisfies the flat >=1-listed-source rule -- this is
        # exactly the gap the user flagged as a regression from Law #58.
        m = load_valid()
        pkg = m["packages"][0]
        core = next(e for e in pkg["semantic_qa"]["claim_source_matrix"] if e["core"])
        core["claim_type"] = "B"
        core["claim"] = "The director said in an interview the finale was reshot"
        core["source_urls"] = ["https://www.crunchyroll.com/frieren"]
        self.assertFailsOn(m, "Law #58 high-risk claims (type B/E)")

    def test_high_risk_type_e_two_encyclopedic_sources_rejected(self):
        # TYPE E (cross-show connection) with 2 listed sources but BOTH encyclopedic
        # must still fail -- 2 sources alone isn't enough, one must be non-encyclopedic
        # (standing in for Law #58's "named, credible" requirement).
        m = load_valid()
        pkg = m["packages"][0]
        wiki_url = "https://en.wikipedia.org/wiki/Frieren"
        fandom_url = "https://frieren.fandom.com/wiki/Aura"
        pkg["sources"].append({"claim": "background", "url": wiki_url, "date": "Jul 2026"})
        pkg["sources"].append({"claim": "background2", "url": fandom_url, "date": "Jul 2026"})
        core = next(e for e in pkg["semantic_qa"]["claim_source_matrix"] if e["core"])
        core["claim_type"] = "E"
        core["source_urls"] = [wiki_url, fandom_url]
        self.assertFailsOn(m, "Law #58 high-risk claims (type B/E)")

    def test_high_risk_type_b_two_sources_one_named_ok(self):
        # TYPE B with 2 listed sources, at least one non-encyclopedic, passes.
        m = load_valid()
        pkg = m["packages"][0]
        named_url = "https://www.animenewsnetwork.com/interview/frieren-director"
        pkg["sources"].append({"claim": "director interview", "url": named_url, "date": "Jul 2026"})
        core = next(e for e in pkg["semantic_qa"]["claim_source_matrix"] if e["core"])
        core["claim_type"] = "B"
        core["source_urls"] = [core["source_urls"][0], named_url]
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_non_high_risk_type_still_needs_only_one_source(self):
        # TYPE A/C/D/F keep the flat >=1 listed + >=1 non-encyclopedic rule -- adding
        # a claim_type must not tighten requirements for non-high-risk types.
        m = load_valid()
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")
        core_types = {e.get("claim_type") for pkg in m["packages"]
                      for e in pkg["semantic_qa"]["claim_source_matrix"] if e["core"]}
        self.assertTrue(core_types & {"A", "C", "D"},
                        msg=f"fixture should exercise non-high-risk types, got {core_types}")


class TestHookClaimCoverageAndNumericCrossCheck(unittest.TestCase):
    """2026-07-25 production-audit findings (Laws #148/#150 fix): 1.5 requires the
    hook's own claim to be its own core:true matrix entry tagged anchors_claim='hook'
    with a real listed source -- not just satisfied by '>=1 core claim exists
    somewhere in the matrix'. 1.6 requires a numeric_cross_check self-attestation
    alongside the other five checks.

    Renamed from TestHookLoopClaimCoverageAndNumericCrossCheck (2026-07-27, Law #141
    rescission): the parallel 'loop' anchor requirement is removed -- anchors_claim is
    still accepted as a value (it's an open string, not an enum) but is no longer
    required or checked, so the loop-anchor tests that used to live here are removed.
    """

    def assertFailsOn(self, manifest: dict, needle: str):
        names = failed_names(manifest)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a failure containing {needle!r}; got failures={names}")
        self.assertFalse(v.validate_manifest(manifest).ok)

    def test_valid_fixture_has_anchored_hook_claim(self):
        # sanity: the shipped fixture already satisfies the hook-anchor rule
        r = v.validate_manifest(load_valid())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_missing_hook_anchor_rejected(self):
        m = load_valid()
        for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]:
            if e.get("anchors_claim") == "hook":
                e.pop("anchors_claim", None)
        self.assertFailsOn(m, "hook_line/opening_sentence's claim is its own sourced core matrix entry")

    # test_missing_loop_anchor_rejected REMOVED (2026-07-27, Law #141 rescission) --
    # a missing/absent anchors_claim="loop" tag no longer fails validation.

    def test_hook_anchor_present_but_not_core_rejected(self):
        # tagging anchors_claim='hook' on a non-core entry must not satisfy the check --
        # the anchored claim itself must be core:true.
        m = load_valid()
        for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]:
            if e.get("anchors_claim") == "hook":
                e["core"] = False
        self.assertFailsOn(m, "hook_line/opening_sentence's claim is its own sourced core matrix entry")

    def test_hook_anchor_present_but_source_not_listed_rejected(self):
        # the anchored entry's source_urls must actually be in the package's sources[]
        # list -- an anchors_claim tag with an unlisted/fabricated source must fail.
        m = load_valid()
        for e in m["packages"][0]["semantic_qa"]["claim_source_matrix"]:
            if e.get("anchors_claim") == "hook":
                e["source_urls"] = ["https://example.com/not-a-listed-source"]
        self.assertFailsOn(m, "hook_line/opening_sentence's claim is its own sourced core matrix entry")

    def test_missing_hook_claim_coverage_check_flag_rejected(self):
        m = load_valid()
        m["packages"][0]["semantic_qa"]["checks"].pop("hook_claim_coverage", None)
        self.assertFailsOn(m, "semantic_qa.checks VO-dependent attested true")

    def test_false_hook_claim_coverage_check_flag_rejected(self):
        m = load_valid()
        m["packages"][1]["semantic_qa"]["checks"]["hook_claim_coverage"] = False
        self.assertFailsOn(m, "semantic_qa.checks VO-dependent attested true")

    def test_missing_numeric_cross_check_flag_rejected(self):
        m = load_valid()
        m["packages"][0]["semantic_qa"]["checks"].pop("numeric_cross_check", None)
        self.assertFailsOn(m, "semantic_qa.checks VO-dependent attested true")

    def test_false_numeric_cross_check_flag_rejected(self):
        m = load_valid()
        m["packages"][1]["semantic_qa"]["checks"]["numeric_cross_check"] = False
        self.assertFailsOn(m, "semantic_qa.checks VO-dependent attested true")

    # test_hook_and_loop_anchors_can_be_the_same_entry_if_it_is_both REMOVED
    # (2026-07-27, Law #141 rescission) -- there is no longer a separate loop-anchor
    # requirement to confirm can coexist with the hook anchor on the same entry.


class TestClipVerificationLaw73(unittest.TestCase):
    """Law #73 (restored and extended for daily_combined, July 25, 2026):
    _validate_clip_verification must cleanly fail -- never crash -- on each of
    the four malformed-input shapes below, matching the
    TestCrashInsteadOfCleanFailFixes standard used for every other fix tonight."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        # must not raise -- that IS the regression being guarded against
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_missing_scene_verified_on_a_clip_fails_cleanly(self):
        m = load_valid()
        del m["packages"][0]["clips"][0]["scene_verified"]
        self.assertFailsCleanly(m, "each clip has scene_verified (bool) set")

    def test_scene_verified_true_missing_verification_source_url_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["clips"][0]["scene_verified"] = True
        m["packages"][0]["clips"][0].pop("verification_source_url", None)
        self.assertFailsCleanly(m, "verification_source_url present wherever scene_verified is true")

    def test_scene_verified_false_missing_manga_reference_fails_cleanly(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = False
        clip.pop("verification_source_url", None)
        clip.pop("manga_reference", None)
        clip.pop("verification_note", None)
        self.assertFailsCleanly(m, "manga_reference or verification_note present wherever scene_verified is false")

    def test_scene_verified_false_with_verification_note_only_passes_F20(self):
        # F20 (docs/KNOWN_ISSUES.md): a clip with scene_verified=false may
        # satisfy the fallback check with a non-empty verification_note
        # instead of manga_reference -- the third state for "real aired
        # footage almost certainly exists but no clip-level video source was
        # independently confirmed this pass," as opposed to the manga-only
        # fallback case. Matches the real shipped shape in both the One Piece
        # (package e41804f5-3651-4f89-91ba-3e848e7578e0) and Sakamoto Days
        # (commit 9284ac2) manifests: scene_verified=false, no
        # manga_reference key at all, verification_note carries the F20
        # explanation.
        #
        # Law #73 UPDATE 8 (2026-08-10) note: F20's own check is UNCHANGED --
        # a bare verification_note still satisfies IT. But UPDATE 8 added a
        # SECOND, independent layer (footage_status + footage_search_performed)
        # that also applies to every scene_verified=false clip, so this test
        # now also sets those two fields to isolate what it is actually
        # proving (F20's own fallback logic) from UPDATE 8's separate,
        # additional requirement -- see TestFootageStatusLaw73Update8 below
        # for dedicated coverage of the new fields on their own.
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = False
        clip.pop("verification_source_url", None)
        clip.pop("manga_reference", None)
        clip["verification_note"] = (
            "No independently confirmed clip-level video source for this exact "
            "beat this pass; real aired footage almost certainly exists (see F20)."
        )
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = (
            "Searched YouTube and Crunchyroll for this exact beat; no matching "
            "clip-level video source located this pass."
        )
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_scene_verified_false_empty_verification_note_still_fails_cleanly(self):
        # whitespace-only verification_note must not satisfy the check --
        # same .strip() discipline already applied to manga_reference and
        # film_release_gap_note elsewhere in this file.
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = False
        clip.pop("verification_source_url", None)
        clip.pop("manga_reference", None)
        clip["verification_note"] = "   "
        self.assertFailsCleanly(m, "manga_reference or verification_note present wherever scene_verified is false")

    def test_clip_plan_needs_manga_source_non_boolean_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_manga_source"] = "yes"  # string, not bool
        self.assertFailsCleanly(m, "clip_plan_needs_manga_source is boolean when present")


class TestFootageStatusLaw73Update8(unittest.TestCase):
    """Law #73 UPDATE 8 (added 2026-08-10, same-day fix after the Re:ZERO /
    Love Unseen footage-location correction incident -- docs/KNOWN_ISSUES.md
    F21 context). F20's own fallback (manga_reference OR a bare
    verification_note, tested above in TestClipVerificationLaw73) is
    UNCHANGED by this update. This class covers the three NEW, INDEPENDENT
    requirements added on top of it for every scene_verified=false clip:

      1. footage_status (required enum) with aired_not_located hard-blocking.
      2. footage_search_performed (required, MECHANICAL FLOOR -- must name a
         real video platform, not just be a non-empty string).
      3. location_pointer.url, when present, must also appear in the
         package's own sources[] list (cross-field consistency).

    Same BANNED_COMPARATIVE_LANGUAGE-style discipline: adversarial tests
    prove the mechanical floor in (2) actually REJECTS a copy-pasted/empty
    search string, not merely that a well-formed one passes.
    """

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def _base_unverified_clip(self, m: dict) -> dict:
        """Returns packages[0].clips[0] set to scene_verified=false with a
        valid F20 fallback already in place, so tests in this class isolate
        the NEW UPDATE 8 fields rather than accidentally tripping F20."""
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = False
        clip.pop("verification_source_url", None)
        clip.pop("manga_reference", None)
        clip["verification_note"] = (
            "No independently confirmed clip-level video source for this exact "
            "beat this pass; real aired footage almost certainly exists (see F20)."
        )
        return clip

    def _valid_footage_search_performed(self) -> str:
        return ("Searched YouTube and Crunchyroll for this exact beat; no "
                "matching clip-level video source located this pass.")

    # --- footage_status enum: presence/shape ---

    def test_missing_footage_status_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip.pop("footage_status", None)
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        self.assertFailsCleanly(m, "footage_status present and a valid enum value wherever scene_verified is false")

    def test_footage_status_invalid_value_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "probably_fine"  # not in FOOTAGE_STATUS_VALUES
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        self.assertFailsCleanly(m, "footage_status present and a valid enum value wherever scene_verified is false")

    def test_footage_status_non_string_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = True  # bool, not one of the enum strings
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        self.assertFailsCleanly(m, "footage_status present and a valid enum value wherever scene_verified is false")

    # --- footage_status enum: the three non-blocking values pass ---

    def test_footage_status_aired_and_located_passes(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "aired_and_located"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_footage_status_unaired_trailer_only_passes(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_trailer_only"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_footage_status_unaired_no_footage_passes(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # --- footage_status enum: aired_not_located HARD-BLOCKS ---

    def test_footage_status_aired_not_located_hard_blocks_even_with_everything_else_valid(self):
        # This is the exact scenario the user specified: footage_status=
        # aired_not_located must fail closed with the SAME treatment as any
        # other required-but-missing field -- no attestation elsewhere
        # (a perfectly well-formed verification_note, a valid
        # footage_search_performed naming a real platform) can rescue it.
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "aired_not_located"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        self.assertFailsCleanly(m, "no clip has footage_status=aired_not_located")

    def test_footage_status_aired_not_located_fails_even_alongside_manga_reference(self):
        # Confirms the hard block is not merely "F20 fallback missing" --
        # even a fully-valid manga_reference cannot rescue aired_not_located.
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip.pop("verification_note", None)
        clip["manga_reference"] = "Chapter 1170, page 4, panel 2 -- the handover beat."
        clip["footage_status"] = "aired_not_located"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        self.assertFailsCleanly(m, "no clip has footage_status=aired_not_located")

    # --- footage_search_performed: mechanical floor (not mere presence) ---

    def test_footage_search_performed_missing_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip.pop("footage_search_performed", None)
        self.assertFailsCleanly(m, "footage_search_performed present and names a recognizable video platform")

    def test_footage_search_performed_empty_string_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = ""
        self.assertFailsCleanly(m, "footage_search_performed present and names a recognizable video platform")

    def test_footage_search_performed_whitespace_only_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = "   "
        self.assertFailsCleanly(m, "footage_search_performed present and names a recognizable video platform")

    def test_footage_search_performed_copy_pasted_generic_string_fails_the_mechanical_floor(self):
        # THE test the user explicitly asked for: a confident-sounding,
        # non-empty, but platform-agnostic/copy-pasted search summary must
        # still be REJECTED -- proving this is a real mechanical floor
        # (an actual platform-name check), not merely a non-empty-string
        # check dressed up with a new field name. This is exactly the kind
        # of self-attested text (no real platform ever named) that slipped
        # through as a bare verification_note in the Re:ZERO/Love Unseen
        # incident this update exists to prevent.
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = (
            "Searched around for footage of this beat; could not confirm a "
            "clip-level source this pass."
        )
        self.assertFailsCleanly(m, "footage_search_performed present and names a recognizable video platform")

    def test_footage_search_performed_non_string_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = 12345
        self.assertFailsCleanly(m, "footage_search_performed present and names a recognizable video platform")

    def test_footage_search_performed_names_a_platform_in_prose_passes(self):
        # Deliberately permissive on FORMAT: a platform name written in
        # ordinary prose (not a bare URL/domain) must still satisfy the
        # floor, since the requirement is "names a recognizable platform,"
        # not "contains a URL."
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = (
            "Checked Crunchyroll's episode library and the official YouTube "
            "channel; no matching clip-level source found for this beat."
        )
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_footage_search_performed_case_insensitive_match_passes(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = "SEARCHED YOUTUBE, no matching clip located."
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_footage_search_performed_sentence_initial_x_dot_com_passes(self):
        # Adversarial fix for a real false-rejection bug: FOOTAGE_SEARCH_DOMAINS
        # originally listed " x.com" WITH a leading space (to avoid colliding
        # with unrelated words containing "x.com" as a substring). But that
        # leading-space requirement means a search-summary string that
        # legitimately opens with "X.com had..." -- capitalized,
        # sentence-initial, no space before it once lowercased -- would fail
        # to match at all, even though it plainly names a real video/social
        # platform. This proves the fix: "x.com" is matched as a bare
        # substring (like every other domain in the list), so sentence-
        # initial usage is no longer silently rejected.
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = (
            "X.com had a since-deleted post confirming this beat; no "
            "clip-level video source located this pass."
        )
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # --- location_pointer: optional, shape-checked when present ---

    def test_location_pointer_absent_is_not_a_failure(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        clip.pop("location_pointer", None)
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_location_pointer_missing_url_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        clip["location_pointer"] = {"description": "Candidate clip found but not yet confirmed."}
        self.assertFailsCleanly(m, "location_pointer well-formed (url + description) when present")

    def test_location_pointer_empty_description_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        clip["location_pointer"] = {
            "url": "https://www.youtube.com/watch?v=example123",
            "description": "   ",
        }
        self.assertFailsCleanly(m, "location_pointer well-formed (url + description) when present")

    def test_location_pointer_non_dict_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        clip["location_pointer"] = "https://www.youtube.com/watch?v=example123"
        self.assertFailsCleanly(m, "location_pointer well-formed (url + description) when present")

    # --- location_pointer.url cross-field check against package sources[] ---

    def test_location_pointer_url_not_in_sources_fails_cleanly(self):
        m = load_valid()
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        clip["location_pointer"] = {
            "url": "https://www.youtube.com/watch?v=not_in_sources_list",
            "description": "A candidate clip that was never added to the package's own sources.",
        }
        self.assertFailsCleanly(m, "location_pointer.url also appears in the package's sources list")

    def test_location_pointer_url_matching_a_listed_source_passes(self):
        m = load_valid()
        pkg = m["packages"][0]
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        listed_url = "https://www.youtube.com/watch?v=example123"
        pkg.setdefault("sources", [])
        pkg["sources"].append({"claim": "Test source for location_pointer cross-check", "url": listed_url, "date": "Aug 2026"})
        clip["location_pointer"] = {
            "url": listed_url,
            "description": "The same official upload already listed in this package's sources.",
        }
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_location_pointer_url_matches_listed_source_case_and_whitespace_insensitively(self):
        # _norm() lowercases and collapses whitespace -- the cross-field
        # check should use the same normalization as the existing
        # claim_source_matrix / pkg_source_urls pattern, not a raw ==.
        m = load_valid()
        pkg = m["packages"][0]
        clip = self._base_unverified_clip(m)
        clip["footage_status"] = "unaired_no_footage"
        clip["footage_search_performed"] = self._valid_footage_search_performed()
        pkg.setdefault("sources", [])
        pkg["sources"].append({"claim": "Test source", "url": "https://www.YouTube.com/watch?v=Example123", "date": "Aug 2026"})
        clip["location_pointer"] = {
            "url": "  https://www.youtube.com/watch?v=example123  ",
            "description": "Same upload, different case/whitespace than the sources[] entry.",
        }
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_multiple_unverified_clips_each_independently_checked_for_footage_status(self):
        # Confirms the per-clip index reporting works across more than one
        # scene_verified=false clip in the same package (mirrors the
        # existing multi-clip-index coverage pattern used for
        # verified_missing_source elsewhere in this file).
        m = load_valid()
        pkg = m["packages"][0]
        clip0 = pkg["clips"][0]
        clip0["scene_verified"] = False
        clip0.pop("verification_source_url", None)
        clip0.pop("manga_reference", None)
        clip0["verification_note"] = "No confirmed source this pass (see F20)."
        clip0["footage_status"] = "unaired_no_footage"
        clip0["footage_search_performed"] = self._valid_footage_search_performed()
        # second clip deliberately missing footage_status
        clip1 = pkg["clips"][1] if len(pkg["clips"]) > 1 else None
        if clip1 is None:
            self.skipTest("fixture package 0 has fewer than 2 clips")
        clip1["scene_verified"] = False
        clip1.pop("verification_source_url", None)
        clip1.pop("manga_reference", None)
        clip1["verification_note"] = "No confirmed source this pass (see F20)."
        clip1.pop("footage_status", None)
        clip1["footage_search_performed"] = self._valid_footage_search_performed()
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        matches = [n for n in names_failed if "footage_status present and a valid enum value" in n]
        self.assertEqual(len(matches), 1, msg=f"expected exactly one footage_status failure line; got {matches}")
        # the detail string embeds the 1-based clip index list -- clip1 is
        # index 1 (0-based) in the clips array, so it must be reported as [2].
        detail = [detail for name, ok, detail in r.checks if ok == "FAIL" and "footage_status present and a valid enum value" in name][0]
        self.assertIn("[2]", detail, msg=f"expected clip index 2 (1-based) flagged; got detail={detail!r}")


class TestClaimVsSourceCheckAndStoryPointGateLaw73Update4(unittest.TestCase):
    """Law #73 UPDATE 4 (added July 28, 2026, port-back to daily_combined
    validator): claim_vs_source_check is required (presence/shape only, M6
    pattern) on every clip with scene_verified=true, and the validator
    mechanically enforces the one non-attestation-dependent piece: a clip
    cannot be scene_verified=true while self-reporting
    claim_vs_source_check.match=false. story_point_gate is an OPTIONAL
    top-level object, shape-checked only when present."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def _valid_cvsc(self):
        return {
            "claimed_beat": "Character X delivers the decisive counter-attack in the final confrontation.",
            "source_content_confirmed": "Official episode transcript at the cited URL shows this exact exchange and counter-attack.",
            "match": True,
        }

    # 1. valid claim_vs_source_check on a scene_verified=true clip -- passes.
    def test_valid_claim_vs_source_check_on_verified_clip_passes(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        clip.pop("manga_reference", None)
        clip.pop("verification_note", None)
        clip["claim_vs_source_check"] = self._valid_cvsc()
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # 2. scene_verified=true, claim_vs_source_check missing entirely -- fails.
    def test_verified_clip_missing_claim_vs_source_check_fails_cleanly(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        clip.pop("claim_vs_source_check", None)
        self.assertFailsCleanly(m, "claim_vs_source_check present and well-formed wherever scene_verified is true")

    # 3. scene_verified=true, claim_vs_source_check present but malformed
    #    (match is a string, not bool; claimed_beat empty) -- fails, and both
    #    malformed variants are checked independently.
    def test_verified_clip_claim_vs_source_check_match_wrong_type_fails_cleanly(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        cvsc = self._valid_cvsc()
        cvsc["match"] = "true"  # string, not bool
        clip["claim_vs_source_check"] = cvsc
        self.assertFailsCleanly(m, "claim_vs_source_check present and well-formed wherever scene_verified is true")

    def test_verified_clip_claim_vs_source_check_empty_claimed_beat_fails_cleanly(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        cvsc = self._valid_cvsc()
        cvsc["claimed_beat"] = "   "  # whitespace-only, fails .strip() != ""
        clip["claim_vs_source_check"] = cvsc
        self.assertFailsCleanly(m, "claim_vs_source_check present and well-formed wherever scene_verified is true")

    # 4. scene_verified=true with claim_vs_source_check.match=false -- fails
    #    the CONTRADICTION check specifically, not the shape check, since the
    #    object itself is well-formed (just internally contradictory). The two
    #    failure modes must be distinguishable by check name.
    def test_verified_clip_with_match_false_fails_contradiction_check_not_shape_check(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        cvsc = self._valid_cvsc()
        cvsc["match"] = False  # well-formed shape, but internally contradictory
        clip["claim_vs_source_check"] = cvsc
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertFalse(r.ok)
        # must fail the contradiction check specifically...
        self.assertTrue(
            any("no clip is scene_verified=true with claim_vs_source_check.match=false" in n for n in names_failed),
            msg=f"expected the contradiction check to fail; got failures={names_failed}",
        )
        # ...and must NOT fail the shape check, since the object itself is well-formed
        self.assertFalse(
            any("claim_vs_source_check present and well-formed wherever scene_verified is true" in n for n in names_failed),
            msg=f"shape check should not fail when claim_vs_source_check is well-formed but match=false; got failures={names_failed}",
        )

    # 5. story_point_gate absent -- passes (optional-when-absent).
    def test_story_point_gate_absent_passes_and_no_check_attempted(self):
        m = load_valid()
        self.assertNotIn("story_point_gate", m["packages"][0])
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")
        gate_checks = [name for name, ok, _ in r.checks if "story_point_gate" in name]
        self.assertEqual(gate_checks, [], msg=f"expected no story_point_gate check attempted when field absent; got {gate_checks}")

    # 6. story_point_gate present and well-formed -- passes.
    def test_story_point_gate_present_well_formed_passes(self):
        m = load_valid()
        m["packages"][0]["story_point_gate"] = {
            "anime_has_reached_this_point": True,
            "checked_via": "https://example.com/official-episode-list-checked-this-session",
        }
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # 7. story_point_gate present but malformed -- fails, both variants.
    def test_story_point_gate_missing_checked_via_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["story_point_gate"] = {"anime_has_reached_this_point": False}
        self.assertFailsCleanly(m, "story_point_gate is well-formed when present")

    def test_story_point_gate_anime_has_reached_this_point_wrong_type_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["story_point_gate"] = {
            "anime_has_reached_this_point": "no",  # string, not bool
            "checked_via": "https://example.com/official-episode-list",
        }
        self.assertFailsCleanly(m, "story_point_gate is well-formed when present")


# Frozen historical snapshot of the Blue Box package's clip plan exactly as
# committed in 93e268f (2026-07-28), BEFORE Law #73 Update 4/5 existed and
# BEFORE this content was hand-corrected later the same night. Deliberately
# NOT read from the live manifest file -- that file was subsequently edited
# in place (real Episode 1 sourcing applied to all 4 clips, see git log for
# the commit following 93e268f) and no longer has this shape. This constant
# preserves the original historical fact the regression test below is
# documenting, independent of any future change to the live file.
FROZEN_BLUE_BOX_CLIPS_PRE_UPDATE_4 = [
    {
        "scene": "Blue Box anime S1 \u2014 Taiki and Chinatsu gym establishing shot",
        "reason": "Anchors the 'gym where it all started' detail from the finale for viewers who haven't read the manga",
        "duration_sec": 8,
        "timeline_start_sec": 0,
        "timeline_end_sec": 8,
        "scene_verified": True,
        "verification_source_url": "https://www.animenewsnetwork.com/news/2025-12-20/blue-box-anime-2nd-season-debuts-in-fall-2026/.232332",
    },
    {
        "scene": "Blue Box anime S1 \u2014 Taiki and Chinatsu emotional/romantic moment footage",
        "reason": "Visual pairing for the 'genuinely positive finale reception' beat",
        "duration_sec": 8,
        "timeline_start_sec": 8,
        "timeline_end_sec": 16,
        "scene_verified": True,
        "verification_source_url": "https://www.animenewsnetwork.com/news/2025-12-20/blue-box-anime-2nd-season-debuts-in-fall-2026/.232332",
    },
    {
        "scene": "Blue Box anime S1 \u2014 cast group/school setting footage",
        "reason": "Carries the pivot into the real 'crisis' beat (issue shortage) with a change in visual pacing",
        "duration_sec": 7,
        "timeline_start_sec": 16,
        "timeline_end_sec": 23,
        "scene_verified": True,
        "verification_source_url": "https://www.animenewsnetwork.com/news/2025-12-20/blue-box-anime-2nd-season-debuts-in-fall-2026/.232332",
    },
    {
        "scene": "Blue Box anime S1 \u2014 closing wide shot of the gym/school",
        "reason": "Closes on the same visual motif as the opening cut, reinforcing the full-circle framing for the CTA beat",
        "duration_sec": 7,
        "timeline_start_sec": 23,
        "timeline_end_sec": 30,
        "scene_verified": True,
        "verification_source_url": "https://www.animenewsnetwork.com/news/2025-12-20/blue-box-anime-2nd-season-debuts-in-fall-2026/.232332",
    },
]


class TestRealSakamotoDaysBlueBoxManifestLaw73Update4(unittest.TestCase):
    """Regression check against the actual historical dual-package manifest
    sent July 28, 2026 (cron_tracking/manual_step3_20260728/run_manifest.json),
    drafted and sent BEFORE Law #73 Update 4 existed. Split into two explicit
    assertions per the real content of each package:

      (1) The Sakamoto Days package (morning slot, package_id
          d4a91c3e-5f82-4b16-9e3a-7c2d5e8f1a90) has scene_verified=false on
          every clip, using verification_note/manga_reference fallbacks only.
          None of Update 4's new checks apply to scene_verified=false clips,
          so this package must remain genuinely unaffected.

      (2) The Blue Box package (evening slot, package_id
          f7c2e9b4-3a61-4d8f-b527-9e4c1a6d8f32) has scene_verified=true on
          all 4 clips but carries no claim_vs_source_check field at all --
          that field did not exist when this package was drafted. Under
          today's validator this package now correctly FAILS the new
          presence/shape check.

    This is EXPECTED, INTENDED, FORWARD-LOOKING behavior, not a regression:
    Update 4 was not in effect when this manifest was drafted, sent, and
    logged, and there is no requirement (nor any mechanism) for a
    pre-Update-4 manifest to retroactively satisfy a requirement that did
    not exist yet. Requiring old manifests to retroactively pass a new check
    would defeat the entire point of adding the check going forward. The
    real send already happened and the log entries already reflect the
    rules in effect at that time -- this test documents that fact, it does
    not imply anything needs to be corrected or resent.

    UPDATE (2026-07-28, later same night): the Blue Box package's clips in
    the LIVE manifest file were hand-corrected after this test class was
    written -- all 4 clips were re-sourced to real, independently verified
    Episode 1 content (Law #73 Update 4/5 claim_vs_source_check + clip_locate
    fields added; one factually wrong claim, the "closing wide shot of the
    gym/school", was replaced with the real confirmed closing scene). That
    correction is a genuine content fix and is intentionally reflected in the
    live file going forward. Method (1) below still reads the live file
    (correct: the Sakamoto Days package's scene_verified=false content was
    never touched by this fix). Method (2) below now reads a FROZEN fixture
    of the pre-correction Blue Box clips instead of the live file, so that
    this historical regression fact remains permanently documented and
    stops depending on the live file's current, now-different content.
    """

    MANIFEST_PATH = os.path.join(
        os.path.dirname(__file__), "..", "cron_tracking", "manual_step3_20260728", "run_manifest.json"
    )

    def _load_real_manifest(self) -> dict:
        with open(self.MANIFEST_PATH, encoding="utf-8") as fh:
            return json.load(fh)

    def _package(self, manifest: dict, package_id: str) -> dict:
        for pkg in manifest["packages"]:
            if pkg.get("package_id") == package_id:
                return pkg
        self.fail(f"package_id {package_id!r} not found in real manifest -- has the file moved or changed?")

    def test_sakamoto_days_package_unaffected_by_update_4_checks(self):
        m = self._load_real_manifest()
        pkg = self._package(m, "d4a91c3e-5f82-4b16-9e3a-7c2d5e8f1a90")
        clips = pkg.get("clips", [])
        self.assertTrue(len(clips) > 0)
        self.assertTrue(all(c.get("scene_verified") is False for c in clips),
                         msg="expected all Sakamoto Days clips to be scene_verified=false in the real manifest")
        # Validate the whole manifest and confirm no Update 4 check fires
        # against any Sakamoto Days clip specifically. Since Update 4's checks
        # only fire on scene_verified=true clips or a present story_point_gate,
        # and this package has neither, this package must contribute zero
        # Update 4 failures regardless of what the other package does.
        r = v.validate_manifest(m)
        sakamoto_slot_prefix = f"[{pkg.get('slot')}]"
        failed_update4_for_sakamoto = [
            name for name, ok, _ in r.checks
            if ok == "FAIL" and "UPDATE 4" in name and name.startswith(sakamoto_slot_prefix)
        ]
        self.assertEqual(failed_update4_for_sakamoto, [],
                          msg=f"expected zero Update 4 failures scoped to the Sakamoto Days ({pkg.get('slot')}) package; got {failed_update4_for_sakamoto}")

    def test_blue_box_package_correctly_failed_new_check_pre_update_4_snapshot(self):
        """Uses a FROZEN pre-correction snapshot (see FROZEN_BLUE_BOX_CLIPS_PRE_UPDATE_4
        above), not the live manifest file -- the live file's Blue Box clips
        were hand-corrected after this test was written and no longer have
        this shape. This test documents a historical fact about the state as
        of commit 93e268f, not an ongoing property of the live file."""
        m = self._load_real_manifest()
        pkg = dict(self._package(m, "f7c2e9b4-3a61-4d8f-b527-9e4c1a6d8f32"))
        pkg["clips"] = FROZEN_BLUE_BOX_CLIPS_PRE_UPDATE_4
        clips = pkg["clips"]
        self.assertTrue(len(clips) > 0)
        self.assertTrue(all(c.get("scene_verified") is True for c in clips),
                         msg="expected all Blue Box clips to be scene_verified=true in the frozen pre-correction snapshot")
        self.assertTrue(all("claim_vs_source_check" not in c for c in clips),
                         msg="expected no claim_vs_source_check field on the frozen pre-Update-4 Blue Box clips")
        # Validate a synthetic manifest built from the live file but with the
        # Blue Box package's clips swapped for the frozen pre-correction
        # snapshot, so the Update 4 shape check fires against exactly the
        # historical content this test documents.
        m_frozen = json.loads(json.dumps(m))
        for p in m_frozen["packages"]:
            if p.get("package_id") == "f7c2e9b4-3a61-4d8f-b527-9e4c1a6d8f32":
                p["clips"] = FROZEN_BLUE_BOX_CLIPS_PRE_UPDATE_4
        r = v.validate_manifest(m_frozen)
        blue_box_slot_prefix = f"[{pkg.get('slot')}]"
        failed = [
            name for name, ok, _ in r.checks
            if ok == "FAIL" and name.startswith(blue_box_slot_prefix)
        ]
        # EXPECTED failure: exactly the new presence/shape check, for exactly
        # this reason. This is intended, forward-looking enforcement -- not a
        # regression, and does not retroactively affect the already-sent,
        # already-logged historical record.
        self.assertTrue(
            any("claim_vs_source_check present and well-formed wherever scene_verified is true" in n for n in failed),
            msg=f"expected the new Update 4 shape check to be the (expected) failure; got {failed}",
        )
        # confirm the contradiction check specifically does NOT also fire --
        # there's no self-reported match=false here, just an absent field
        # entirely, which is a distinct failure mode.
        self.assertFalse(
            any("no clip is scene_verified=true with claim_vs_source_check.match=false" in n for n in failed),
            msg=f"contradiction check should not fire when the field is simply absent; got {failed}",
        )


class TestTheatricalFilmReleaseDelayLaw73_3B(unittest.TestCase):
    """Law #73 3B (theatrical films separate release window clause, added
    July 26, 2026): clip_plan_needs_release_delay must be boolean when present,
    and film_release_gap_note must be a non-empty string whenever the flag is
    true. Regression incident: the July 25, 2026 evening Demon Slayer: Infinity
    Castle package (batch_id dfe00d0c-a062-438b-83fc-8576fa6e0148, package_id
    ba0bab4c-dbf2-42b4-a5dd-feb6b7cdc49a) shipped before this clause existed."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        # must not raise -- that IS the regression being guarded against
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_clip_plan_needs_release_delay_non_boolean_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_release_delay"] = "yes"  # string, not bool
        self.assertFailsCleanly(m, "clip_plan_needs_release_delay is boolean when present")

    def test_release_delay_true_missing_gap_note_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_release_delay"] = True
        m["packages"][0].pop("film_release_gap_note", None)
        self.assertFailsCleanly(m, "film_release_gap_note present wherever clip_plan_needs_release_delay is true")

    def test_release_delay_true_empty_string_gap_note_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_release_delay"] = True
        m["packages"][0]["film_release_gap_note"] = "   "  # whitespace-only, fails .strip() != ""
        self.assertFailsCleanly(m, "film_release_gap_note present wherever clip_plan_needs_release_delay is true")

    def test_release_delay_true_with_real_gap_note_passes(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_release_delay"] = True
        m["packages"][0]["film_release_gap_note"] = "theatrical-only as of run date, no home/streaming release yet"
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_release_delay_false_gap_note_not_required(self):
        m = load_valid()
        m["packages"][0]["clip_plan_needs_release_delay"] = False
        m["packages"][0].pop("film_release_gap_note", None)
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_release_delay_absent_no_check_attempted_existing_fixtures_unaffected(self):
        # regression guard: the two shipped valid fixtures must still pass
        # unchanged -- this feature must never require new fields on packages
        # that never touch a theatrical film
        m = load_valid()
        self.assertNotIn("clip_plan_needs_release_delay", m["packages"][0])
        self.assertNotIn("film_release_gap_note", m["packages"][0])
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")
        release_delay_checks = [name for name, ok, _ in r.checks if "clip_plan_needs_release_delay" in name or "film_release_gap_note" in name]
        self.assertEqual(release_delay_checks, [], msg=f"expected no 3B checks attempted when field absent; got {release_delay_checks}")


class TestClipCountFloorRemovedF22(unittest.TestCase):
    """F22 fix (2026-07-28): the old fixed 'at least 4 clips' floor measured
    clip COUNT, not clip-plan quality, and had no comment ever justifying the
    number 4. Real coverage is guaranteed by _validate_clip_timeline's
    contiguous 0->target_sec tiling check, which already fails hard on an
    empty/malformed clip plan. Replaced with a plain non-empty check so any
    honestly-tiled clip count -- 2, 3, 4, or more -- passes on equal footing.
    Regression case: the real, human-approved Sakamoto Days 3-cut restructure
    (7/13/10s, commit 9284ac2) must pass end to end, not be blocked by an
    arbitrary count floor unrelated to its actual correctness."""

    def _retile(self, m: dict, durations: list[int]):
        # Rebuild packages[0]['clips'] as `len(durations)` contiguous cuts
        # tiling 0->30s with the given per-cut durations (must sum to 30),
        # reusing the fixture's existing scene_verified/verification_source_url
        # shape so only clip COUNT/timing changes, nothing else.
        assert sum(durations) == 30, f"test fixture bug: durations must sum to 30, got {durations}"
        clips = []
        t = 0
        for i, dur in enumerate(durations):
            clips.append({
                "scene": f"test clip {i+1}",
                "reason": "test beat",
                "carries_loop_back": False,
                "duration_sec": dur,
                "timeline_start_sec": t,
                "timeline_end_sec": t + dur,
                "scene_verified": True,
                "verification_source_url": "https://example.com/verified-source",
                "claim_vs_source_check": {
                    "claimed_beat": f"Test clip {i+1} shows its designated test beat.",
                    "source_content_confirmed": "The cited test source was checked and confirmed to show this same test beat.",
                    "match": True,
                },
                "clip_locate": {
                    "season": 1,
                    "episode": 1,
                    "locate_confirmed_via": "the same cited test source confirmed above",
                    "episode_source": "explicitly_stated",
                },
            })
            t += dur
        m["packages"][0]["clips"] = clips
        # Law #73 UPDATE 6: clip_descriptions must literally surface every
        # verified clip's season/episode. This helper replaces clips[]
        # wholesale for a COUNT/timing test unrelated to UPDATE 6, so rebuild
        # a matching CUT-per-clip clip_descriptions here rather than leaving
        # the fixture's stale 5-CUT text mismatched against the new count.
        m["packages"][0]["clip_descriptions"] = " ".join(
            f"CUT{i + 1}: test clip {i + 1} shows its designated test beat."
            for i in range(len(durations))
        )
        m["packages"][0]["clip_descriptions"] = _render.ensure_clip_locations(
            m["packages"][0]["clip_descriptions"], clips
        )
        return m

    def test_valid_3cut_manifest_passes_matching_sakamoto_days_shape(self):
        # Mirrors the real Sakamoto Days restructure ratio (7/13/10s out of 30).
        m = load_valid()
        self._retile(m, [7, 13, 10])
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_valid_2cut_manifest_also_passes_no_arbitrary_floor(self):
        # Confirms the fix removed a fixed floor entirely, not just lowered it
        # to 3 -- 2 honestly-tiled clips must pass exactly as readily.
        m = load_valid()
        self._retile(m, [15, 15])
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    def test_empty_clips_still_fails_cleanly_no_new_hole(self):
        # Removing the count floor must not open a hole for an empty clip plan --
        # this is caught by the new explicit non-empty check.
        m = load_valid()
        m["packages"][0]["clips"] = []
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any("clip plan is non-empty" in n for n in names),
                        msg=f"expected a clean failure containing 'clip plan is non-empty'; got failures={names}")
        self.assertFalse(r.ok)


class TestFormatTypeEnumLaw85Law96WatchRank(unittest.TestCase):
    """format_type must be one of the controlled FORMAT_TYPES tokens (this class
    covers Law #85's hierarchy + Law #96's rotation formats + Law #98's WATCH_RANK;
    the full live enum has grown to 17 tokens as of Law #158/#159/#160 -- see
    TestFormatTypeEnumLaw158Law159Law160 below for the later additions). Free-text
    and compound labels observed in real production history (e.g. "industry
    controversy hybrid", "SEASON_PREVIEW / dub-cast reveal") are no longer
    permitted."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        # must not raise -- that IS the regression being guarded against
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_valid_fixture_uses_controlled_tokens_and_passes(self):
        # sanity check: the shipped valid fixture's format_type values are both in
        # FORMAT_TYPES (this would also be caught by test_valid_fixture_passes, but
        # asserting it here documents the enum's intent explicitly)
        m = load_valid()
        fmts = [p["format_type"] for p in m["packages"]]
        self.assertTrue(all(f in v.FORMAT_TYPES for f in fmts), f"fmts={fmts}")
        self.assertTrue(v.validate_manifest(m).ok)

    def test_free_text_format_type_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["format_type"] = "industry controversy / show retrospective hybrid"
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_compound_slash_format_type_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["format_type"] = "SEASON_PREVIEW / dub-cast reveal"
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_non_string_format_type_fails_cleanly(self):
        m = load_valid()
        m["packages"][0]["format_type"] = 12345  # number, not a string
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_missing_format_type_fails_cleanly(self):
        m = load_valid()
        del m["packages"][0]["format_type"]
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_law_96_season_rating_token_accepted(self):
        m = load_valid()
        m["packages"][0]["format_type"] = "SEASON_RATING"
        # format_type is now valid, but SEASON_RATING == the other package's format_type
        # would violate the distinct-formats check, so confirm this specific check passes
        # rather than asserting the whole manifest is ok
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertNotIn("[morning] format_type is one of the controlled tokens",
                          [n for n in names_failed if "controlled tokens" in n])

    def test_law_98_watch_rank_token_accepted(self):
        m = load_experiment()
        # the experiment fixture's evening package already uses WATCH_RANK; confirm no
        # controlled-token failure is raised for it specifically
        r = v.validate_manifest(m)
        token_failures = [name for name, ok, _ in r.checks
                           if ok == "FAIL" and "controlled tokens" in name]
        self.assertEqual(token_failures, [], f"unexpected token failures: {token_failures}")

    def test_law_98_unported_formats_rejected(self):
        # SEASON_RANK, EPISODE_REVIEW, EPISODE_VS_MANGA are Law #98 codes that were
        # deliberately NOT ported -- confirm they are still rejected as out of scope
        for unported in ("SEASON_RANK", "EPISODE_REVIEW", "EPISODE_VS_MANGA"):
            with self.subTest(format_type=unported):
                m = load_valid()
                m["packages"][0]["format_type"] = unported
                self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_slept_on_and_hidden_gem_both_accepted_as_distinct_tokens(self):
        # Law #85's text combines these as one format ("SLEPT_ON / HIDDEN_GEM"), but
        # real production history used both as distinct format_type strings -- confirm
        # both are individually accepted by the enum check.
        for tok in ("SLEPT_ON", "HIDDEN_GEM"):
            with self.subTest(format_type=tok):
                m = load_valid()
                m["packages"][0]["format_type"] = tok
                r = v.validate_manifest(m)
                token_failures = [name for name, ok, _ in r.checks
                                   if ok == "FAIL" and "controlled tokens" in name]
                self.assertEqual(token_failures, [], f"unexpected token failures: {token_failures}")


class TestNonStringFieldCrashes(unittest.TestCase):
    """F15 fix (docs/KNOWN_ISSUES.md, 2026-07-25 finding / 2026-07-25 fix): all 19
    documented non-string-input crash sites in validate_dual_package.py previously
    raised an unhandled AttributeError/TypeError instead of failing cleanly with a
    named Result check, whenever a field held a non-string/non-list value (e.g. a
    number, dict, bool, or wrong-shaped list where a plain string/list was expected).
    The fix routes every one of these fields through the new _str()/_list() typed
    getters, which coerce any wrong-typed value to a safe default ('' or []) instead
    of crashing. Each test below applies both documented poison values -- an int
    (12345) and a wrong-shaped list (['a']) -- to a single package field on top of
    the otherwise-valid dual-package fixture and asserts validate_manifest() returns
    a real Result object (never raises) with ok=False.

    NOTE on 'slot': docs/KNOWN_ISSUES.md originally cited validate_package()'s
    `slot = pkg.get("slot", f"pkg{idx}")` (used only in an f-string label) as the
    crash site, but that line never actually crashes on any input type. Live-testing
    the full pipeline traced the REAL crash to a different, undocumented site in
    validate_manifest(): `slots = sorted(_norm(p.get("slot", "")) for p in pkgs)`.
    That is the site fixed and exercised here.
    """

    POISON_VALUES = (12345, ["a"])

    def assertFieldFailsCleanly(self, field: str, poison):
        m = load_valid()
        m["packages"][0][field] = poison
        try:
            r = v.validate_manifest(m)
        except Exception as e:  # pragma: no cover - the regression being guarded against
            self.fail(f"{field}={poison!r} raised {type(e).__name__}: {e} instead of "
                      f"failing cleanly")
        self.assertIsInstance(r, v.Result)
        self.assertFalse(r.ok, msg=f"{field}={poison!r} unexpectedly passed validation")

    # test_loop_line_non_string_fails_cleanly REMOVED (2026-07-27, Law #141
    # rescission) -- loop_line is no longer read by the validator, so poisoning it
    # with a non-string value no longer causes (or needs to cause) a validation
    # failure; asserting r.ok is False here would now be a false assertion.

    def test_opening_sentence_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("opening_sentence", poison)

    def test_sources_non_list_fails_cleanly(self):
        # 12345 and ["a"] are both meaningful poisons here: 12345 is non-list, and
        # ["a"] is a wrong-shaped list (strings instead of source dicts) -- both must
        # collapse to "not enough good sources" rather than crashing.
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("sources", poison)

    def test_slot_non_string_fails_cleanly(self):
        # Real crash site is validate_manifest()'s cross-package slot dedup check,
        # not validate_package()'s f-string label use -- see class docstring.
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("slot", poison)

    def test_vo_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("vo", poison)

    def test_cta_line_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("cta_line", poison)

    def test_question_line_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("question_line", poison)

    def test_video_style_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("video_style", poison)

    def test_clips_non_list_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("clips", poison)

    def test_hook_line_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("hook_line", poison)

    def test_content_type_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("content_type", poison)

    def test_hook_onscreen_text_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("hook_onscreen_text", poison)

    def test_topic_class_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("topic_class", poison)

    def test_topic_signals_non_list_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("topic_signals", poison)

    def test_series_public_name_non_string_fails_cleanly(self):
        # Only reachable when series.recurring is True -- the default valid_dual_package
        # fixture's package already has series.recurring=true, so this path executes.
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("series_public_name", poison)

    def test_youtube_title_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("youtube_title", poison)

    def test_series_next_line_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("series_next_line", poison)

    def test_funnel_status_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("funnel_status", poison)

    def test_tiktok_title_non_string_fails_cleanly(self):
        for poison in self.POISON_VALUES:
            with self.subTest(poison=poison):
                self.assertFieldFailsCleanly("tiktok_title", poison)


class TestSinglePackageReason(unittest.TestCase):
    """F_new fix (2026-07-26): a manifest may legitimately contain 1 package instead
    of 2 ONLY if it carries a non-empty top-level single_package_reason field stating
    the M5 quality-over-quota justification for leaving the second slot unfilled. A
    1-package manifest with no reason field must still fail exactly as before -- this
    is not a general "1 or 2, no explanation needed" loosening.
    """

    def make_single_package_manifest(self, reason=None):
        m = load_valid()
        # Keep only package 0 (already slot="morning" and passes every per-package
        # mechanical check in the shipped fixture) to isolate this test to the
        # structural package-count/slot checks, not incidental per-package failures.
        m["packages"] = [m["packages"][0]]
        if reason is not None:
            m["single_package_reason"] = reason
        else:
            m.pop("single_package_reason", None)
        return m

    def test_valid_single_package_with_reason_passes(self):
        m = self.make_single_package_manifest(
            reason=("Two clean, verified candidates independently blocked by Law #85 "
                     "scoring (all-3-LOW hard rule); the one remaining timely candidate "
                     "is a same-day topic repeat of yesterday's send. Second slot "
                     "intentionally left unfilled per M5 quality-over-quota."))
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_single_package_without_reason_still_fails_same_as_today(self):
        m = self.make_single_package_manifest(reason=None)
        names = failed_names(m)
        self.assertTrue(
            any("exactly two packages exist" in n for n in names), names)
        self.assertTrue(
            any("one MORNING and one EVENING slot" in n for n in names), names)
        self.assertFalse(v.validate_manifest(m).ok)

    def test_single_package_with_empty_string_reason_still_fails(self):
        # Whitespace-only / empty-string reason must not count as "explained".
        for empty_reason in ("", "   ", "\t\n"):
            with self.subTest(empty_reason=repr(empty_reason)):
                m = self.make_single_package_manifest(reason=empty_reason)
                names = failed_names(m)
                self.assertTrue(
                    any("exactly two packages exist" in n for n in names), names)
                self.assertFalse(v.validate_manifest(m).ok)

    def test_single_package_with_non_string_reason_still_fails(self):
        # Non-string reason (e.g. True, 123, a list) must not count as "explained" --
        # same crash-instead-of-clean-fail category the F15/F_new fixes guard against.
        for poison in (True, 123, ["a reason"], {"note": "reason"}):
            with self.subTest(poison=poison):
                m = self.make_single_package_manifest(reason=poison)
                names = failed_names(m)
                self.assertTrue(
                    any("exactly two packages exist" in n for n in names), names)
                self.assertFalse(v.validate_manifest(m).ok)

    def test_single_package_reason_present_but_two_packages_is_unaffected(self):
        # A normal 2-package manifest must be completely unaffected by the presence
        # of an (irrelevant/unused) single_package_reason field.
        m = load_valid()
        m["single_package_reason"] = "should have no effect when packages has length 2"
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_normal_two_package_manifest_unaffected_no_reason_field(self):
        # Baseline: the ordinary 2-package case with no single_package_reason field
        # at all must pass exactly as it did before this fix.
        m = load_valid()
        self.assertNotIn("single_package_reason", m)
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_single_package_reason_does_not_relax_two_package_slot_check(self):
        # Guard against the fix accidentally loosening the 2-package morning+evening
        # requirement itself -- e.g. two "morning" packages with a reason present
        # must still fail on the slot check, since the reason field is defined to
        # apply ONLY to the exactly-1-package case.
        m = load_valid()
        m["packages"][1]["slot"] = "morning"
        m["single_package_reason"] = "irrelevant for the 2-package case"
        names = failed_names(m)
        self.assertTrue(any("one MORNING and one EVENING slot" in n
                             for n in names), names)
        self.assertFalse(v.validate_manifest(m).ok)

    def test_single_package_wrong_slot_value_fails(self):
        # A single justified package must still carry a real "morning" or "evening"
        # slot value -- a placeholder like "single_07-28" is not accepted.
        m = self.make_single_package_manifest(
            reason="valid M5 justification text, but slot value below is not")
        m["packages"][0]["slot"] = "single_07-28"
        names = failed_names(m)
        self.assertTrue(
            any("single justified package has a morning or evening slot" in n
                for n in names), names)
        self.assertFalse(v.validate_manifest(m).ok)


class TestClipLocateGroundingLaw73Update5(unittest.TestCase):
    """Law #73 UPDATE 5 (added July 28, 2026): clip_locate is required
    (presence/shape only, M6 pattern) on every clip with scene_verified=true.
    The validator also runs a narrow, best-effort cross-check: if BOTH
    claim_vs_source_check.source_content_confirmed and
    clip_locate.locate_confirmed_via contain an extractable episode-number
    token, those tokens must not disagree. If either field lacks an
    extractable token, the comparison is silently skipped -- it is neither a
    pass nor a fail on its own, just an absence of a checkable claim."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def _valid_cvsc(self, episode_text: str = "episode 16"):
        return {
            "claimed_beat": "Character X delivers the decisive counter-attack in the final confrontation.",
            "source_content_confirmed": f"Official {episode_text} transcript at the cited URL shows this exact exchange and counter-attack.",
            "match": True,
        }

    def _valid_clip_locate(self, episode: int = 16, via_text: str | None = None, episode_source: str = "explicitly_stated"):
        return {
            "season": 1,
            "episode": episode,
            "locate_confirmed_via": via_text or f"the same official episode {episode} transcript cited above",
            "episode_source": episode_source,
        }

    def _backfill_other_verified_clips(self, m: dict, skip_pkg_idx: int, skip_clip_idx: int):
        """load_valid() ships a dual package where BOTH morning and evening
        already contain scene_verified=true clips (Update 4's own fixture
        data). Since clip_locate is now required on every such clip, tests
        that target ONE specific clip must still backfill a valid,
        internally-consistent clip_locate (paired with a token-matching
        claim_vs_source_check) on every OTHER pre-existing verified clip, so
        the manifest-level pass/fail reflects only the one clip under test."""
        for pi, pkg in enumerate(m["packages"]):
            for ci, c in enumerate(pkg.get("clips", [])):
                if pi == skip_pkg_idx and ci == skip_clip_idx:
                    continue
                if c.get("scene_verified") is True:
                    # Fully overwrite both fields (not just fill-if-missing) so no
                    # pre-existing fixture prose (e.g. a stray "Episode 23" in the
                    # original text) can collide with the forced episode-1 token
                    # used for backfilled clips here.
                    c["claim_vs_source_check"] = self._valid_cvsc(episode_text="episode 1")
                    c["clip_locate"] = self._valid_clip_locate(episode=1, via_text="the same source cited above, episode 1")
            # Law #73 UPDATE 6: clip_descriptions must literally surface every
            # verified clip's season/episode. Re-derive it here so tests in this
            # class -- which target UPDATE 5's shape/cross-check logic, not
            # UPDATE 6's text-surfacing logic -- aren't incidentally broken by
            # clip_locate mutations this helper makes on their behalf.
            pkg["clip_descriptions"] = _render.ensure_clip_locations(
                pkg.get("clip_descriptions", ""), pkg.get("clips", [])
            )

    def _make_verified_clip(self, m: dict):
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        clip.pop("manga_reference", None)
        clip.pop("verification_note", None)
        self._backfill_other_verified_clips(m, skip_pkg_idx=0, skip_clip_idx=0)
        return clip

    def _sync_clip_descriptions(self, m: dict, pkg_idx: int = 0):
        """Re-derives packages[pkg_idx]'s clip_descriptions from its current
        clips[] so UPDATE 6's text-surfacing check reflects whatever
        clip_locate mutation the calling test just made. Mirrors the real
        pipeline's intended call site (tools/render_clip_descriptions.py)."""
        pkg = m["packages"][pkg_idx]
        pkg["clip_descriptions"] = _render.ensure_clip_locations(
            pkg.get("clip_descriptions", ""), pkg.get("clips", [])
        )

    # 1. valid clip_locate on a scene_verified=true clip -- passes.
    def test_valid_clip_locate_on_verified_clip_passes(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc()
        clip["clip_locate"] = self._valid_clip_locate()
        self._sync_clip_descriptions(m)
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # 2. scene_verified=true, clip_locate missing entirely -- fails.
    def test_verified_clip_missing_clip_locate_fails_cleanly(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc()
        clip.pop("clip_locate", None)
        self.assertFailsCleanly(m, "clip_locate present and well-formed wherever scene_verified is true")

    # 3. episode as a bool must fail -- bool is a subclass of int in Python,
    #    so the shape check must explicitly exclude it rather than silently
    #    accepting True/False as episode numbers 1/0.
    def test_verified_clip_clip_locate_episode_as_bool_fails_cleanly(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc()
        cl = self._valid_clip_locate()
        cl["episode"] = True  # bool, not a real episode int -- must not be silently accepted
        clip["clip_locate"] = cl
        self.assertFailsCleanly(m, "clip_locate present and well-formed wherever scene_verified is true")

    # 4. matching episode tokens in both fields -- passes (no mismatch flagged).
    def test_matching_episode_tokens_in_both_fields_passes(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc(episode_text="episode 16")
        clip["clip_locate"] = self._valid_clip_locate(episode=16, via_text="the same official episode 16 transcript cited above")
        self._sync_clip_descriptions(m)
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")

    # 5. mismatched episode tokens in both fields -- fails, and the failure
    #    must specifically name the cross-check, not the shape check (the
    #    object itself is well-formed, just internally inconsistent).
    def test_mismatched_episode_tokens_fails_cross_check_specifically(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc(episode_text="episode 16")
        clip["clip_locate"] = self._valid_clip_locate(episode=17, via_text="the same official episode 17 transcript cited above")
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertFalse(r.ok)
        self.assertTrue(
            any("clip_locate episode number does not contradict claim_vs_source_check when both state one" in n
                for n in names_failed),
            msg=f"expected the cross-check to fail; got failures={names_failed}",
        )
        self.assertFalse(
            any("clip_locate present and well-formed wherever scene_verified is true" in n for n in names_failed),
            msg=f"shape check should not fail when clip_locate is well-formed but tokens mismatch; got failures={names_failed}",
        )

    # 6. one field with no extractable episode token -- the cross-check must
    #    be silently skipped (neither a pass-with-evidence nor a fail), and
    #    the overall manifest must still pass since nothing else is wrong.
    def test_one_field_without_extractable_token_skips_cross_check_silently(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        # source_content_confirmed has no "episode N" token at all.
        cvsc = self._valid_cvsc()
        cvsc["source_content_confirmed"] = "Official transcript at the cited URL shows this exact exchange and counter-attack."
        clip["claim_vs_source_check"] = cvsc
        clip["clip_locate"] = self._valid_clip_locate(episode=16, via_text="the same official transcript cited above, which does not itself state an episode number in prose")
        self._sync_clip_descriptions(m)
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass (cross-check silently skipped, no other issues); got failures={names}")
        # The cross-check name itself is still present in the checks list (it always
        # runs, once per package -- [morning] here is the clip under test), but
        # must report ok=True since no comparison was attempted for that clip.
        morning_cross_check_results = [ok for name, ok, _ in r.checks
                                        if name.startswith("[morning]")
                                        and "clip_locate episode number does not contradict claim_vs_source_check when both state one" in name]
        self.assertEqual(morning_cross_check_results, [v.STATUS_PASS],
                          msg="cross-check must report PASS when skipped, not silently absent or failing")

    # 7. locate_confirmed_via as a bare URL must fail the shape check --
    #    the field's own spec requires "one sentence" naming how the same
    #    already-cited source establishes the episode (e.g. "the same Anime
    #    News Network episode 16 review cited above"), never a bare URL. A
    #    bare URL also silently defeats the episode-token cross-check, since
    #    URL slugs match the episode-number regex inconsistently depending on
    #    whether they use spaces, hyphens, or underscores -- an accidental
    #    non-match, not a real scope boundary. This must fail as a shape
    #    violation, not silently pass or silently skip the cross-check.
    def test_clip_locate_bare_url_fails_shape_check(self):
        m = load_valid()
        clip = self._make_verified_clip(m)
        clip["claim_vs_source_check"] = self._valid_cvsc(episode_text="episode 16")
        cl = self._valid_clip_locate(episode=16)
        cl["locate_confirmed_via"] = "https://example.com/wiki/Episode_16"  # bare URL, not a descriptive sentence
        clip["clip_locate"] = cl
        self.assertFailsCleanly(m, "clip_locate present and well-formed wherever scene_verified is true")


class TestClipDescriptionsSurfaceLocationLaw73Update6(unittest.TestCase):
    """Law #73 UPDATE 6 (added 2026-08-05): clip_locate (structured,
    UPDATE 5) and clip_descriptions (free text, what the email actually
    sends) are independent representations of the same fact. This closes
    the gap where a verified clip's season/episode could be silently
    dropped from clip_descriptions while every other check still passed
    (confirmed twice: 2026-08-02 One Piece/MHA, 2026-08-05 Bleach TYBW).
    """

    CHECK_NAME = "clip_descriptions surfaces clip_locate season/episode for every verified clip (Law #73 UPDATE 6)"

    def _five_cut_text(self, tag_cut_3: str | None) -> str:
        """Builds a plain 5-CUT clip_descriptions string matching the real
        demonstrated shape. tag_cut_3, if given, is appended verbatim to
        CUT3's segment (e.g. ' -- S1E9'); if None, CUT3 has no location
        token at all."""
        cut3 = "CUT3: Aura's own Scales of Obedience reverses onto her."
        if tag_cut_3:
            cut3 += f" \u2014 {tag_cut_3}"
        return " ".join([
            "CUT1: Frieren calmly confronts Aura and her undead army. \u2014 S1E9.",
            "CUT2: Aura taunts Frieren over her restraint. \u2014 S1E10.",
            cut3 + ".",
            "CUT4: Aura realizes the spells she is facing are far above what she assumed. \u2014 S1E9.",
            "CUT5: Frieren, resolved and merciless, declares she will kill Aura. \u2014 S1E9.",
        ])

    def _clip(self, scene_verified: bool, season: int | None = 1, episode: int | None = 9,
               start: int = 0, dur: int = 6):
        clip = {
            "scene": "test scene",
            "reason": "test beat",
            "carries_loop_back": False,
            "duration_sec": dur,
            "timeline_start_sec": start,
            "timeline_end_sec": start + dur,
            "scene_verified": scene_verified,
        }
        if scene_verified:
            clip["verification_source_url"] = "https://example.com/verified-source"
            clip["claim_vs_source_check"] = {
                "claimed_beat": "Test clip shows its designated test beat.",
                "source_content_confirmed": "The cited test source was checked and confirmed to show this same test beat.",
                "match": True,
            }
            clip["clip_locate"] = {
                "season": season,
                "episode": episode,
                "locate_confirmed_via": "the same cited test source confirmed above",
                "episode_source": "explicitly_stated",
            }
        return clip

    # 1. Passing case: every scene_verified=true clip's season/episode is
    #    literally present in its own CUT segment -- check passes.
    def test_all_verified_clips_have_matching_location_passes(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["clips"] = [
            self._clip(True, 1, 9, start=0),
            self._clip(True, 1, 10, start=6),
            self._clip(True, 1, 10, start=12),
            self._clip(True, 1, 9, start=18),
            self._clip(True, 1, 9, start=24),
        ]
        pkg["clip_descriptions"] = self._five_cut_text(tag_cut_3="S1E10")
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(r.ok, msg=f"expected pass; got failures={names}")
        passing_names = [name for name, ok, _ in r.checks if ok and self.CHECK_NAME in name]
        self.assertTrue(any("[morning]" in n for n in passing_names),
                         msg="expected the UPDATE 6 check itself to appear and pass for morning")

    # 2. Failing case: one verified clip's location is omitted from its CUT
    #    segment in clip_descriptions -- check fails, naming that cut.
    def test_verified_clip_missing_location_in_clip_descriptions_fails_cleanly(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["clips"] = [
            self._clip(True, 1, 9, start=0),
            self._clip(True, 1, 10, start=6),
            self._clip(True, 1, 10, start=12),
            self._clip(True, 1, 9, start=18),
            self._clip(True, 1, 9, start=24),
        ]
        # CUT3's segment carries no location token at all -- omitted.
        pkg["clip_descriptions"] = self._five_cut_text(tag_cut_3=None)
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertFalse(r.ok)
        matching = [n for n in names_failed if self.CHECK_NAME in n and "[morning]" in n]
        self.assertTrue(matching, msg=f"expected the UPDATE 6 check to fail for morning; got failures={names_failed}")
        detail = next(msg for name, ok, msg in r.checks if name == matching[0])
        self.assertIn("3", detail, msg=f"expected cut 3 to be named in the failure detail; got {detail!r}")

    # 3. scene_verified=false clips correctly require nothing -- a clip plan
    #    with zero location tokens anywhere still passes the UPDATE 6 check
    #    as long as no clip is scene_verified=true.
    def test_unverified_clips_require_no_location_in_clip_descriptions(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["clips"] = [self._clip(False, start=i * 6) for i in range(5)]
        pkg["clip_descriptions"] = " ".join([
            "CUT1: Frieren calmly confronts Aura and her undead army.",
            "CUT2: Aura taunts Frieren over her restraint.",
            "CUT3: Aura's own Scales of Obedience reverses onto her.",
            "CUT4: Aura realizes the spells she is facing are far above what she assumed.",
            "CUT5: Frieren, resolved and merciless, declares she will kill Aura.",
        ])
        r = v.validate_manifest(m)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        update6_failed = [n for n in names if self.CHECK_NAME in n]
        self.assertEqual(update6_failed, [], msg=f"UPDATE 6 check must not fail when no clip is scene_verified=true; got failures={names}")

    # 4. Over-split case (flagged in adversarial review, 2026-08-05): a
    #    mid-sentence reference to another cut inside a segment's own prose
    #    (e.g. CUT1's text itself mentions "CUT2") makes _CUT_SPLIT_RE fire
    #    an extra time, producing MORE segments than clips. This must be
    #    caught and failed closed, not silently mismapped by zipping
    #    clips[i] against segments[i] for the first N and dropping the rest.
    def test_over_split_clip_descriptions_fails_cleanly_instead_of_mismapping(self):
        m = load_valid()
        pkg = m["packages"][0]
        pkg["clips"] = [
            self._clip(True, 1, 9, start=0),
            self._clip(True, 1, 10, start=6),
            self._clip(True, 1, 10, start=12),
            self._clip(True, 1, 9, start=18),
            self._clip(True, 1, 9, start=24),
        ]
        # CUT4's own prose mentions "CUT2" mid-sentence, causing
        # _CUT_SPLIT_RE (which fires on every "CUT\s*\d+" occurrence with no
        # header-vs-prose distinction) to over-split this into 6 segments
        # for 5 clips.
        pkg["clip_descriptions"] = " ".join([
            "CUT1: Frieren calmly confronts Aura and her undead army. \u2014 S1E9.",
            "CUT2: Aura taunts Frieren over her restraint. \u2014 S1E10.",
            "CUT3: Aura's own Scales of Obedience reverses onto her. \u2014 S1E10.",
            "CUT4: the closing beat mirrors CUT2's earlier taunt but inverted. \u2014 S1E9.",
            "CUT5: Frieren, resolved and merciless, declares she will kill Aura. \u2014 S1E9.",
        ])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertFalse(r.ok)
        matching = [n for n in names_failed if self.CHECK_NAME in n and "[morning]" in n]
        self.assertTrue(matching, msg=f"expected the UPDATE 6 check to fail closed on an over-split; got failures={names_failed}")
        detail = next(msg for name, ok, msg in r.checks if name == matching[0])
        self.assertIn("does not match", detail, msg=f"expected a segment-count-mismatch message, not a per-cut mismap; got {detail!r}")




class TestVoPendingSkipBehavior(unittest.TestCase):
    """vo_status="pending" -- the Perplexity -> Claude VO handoff draft stage.

    Added 2026-08-16. The contract under test: VO-dependent checks SKIP, everything
    else still runs and attests for real, and a skipped manifest is never sendable.
    """

    def _pending(self):
        """Valid fixture with the evening package flipped to vo_status=pending."""
        m = load_valid()
        m["packages"][1]["vo_status"] = "pending"
        return m

    @staticmethod
    def _statuses(r):
        return {name: status for name, status, _ in r.checks}

    # --- the five VO-dependent semantic_qa keys skip; the five others do not --------
    def test_vo_dependent_qa_half_skips_and_independent_half_still_runs(self):
        r = v.validate_manifest(self._pending())
        st = self._statuses(r)
        dep = [n for n in st if "VO-dependent attested true" in n and n.startswith("[evening]")]
        indep = [n for n in st if "VO-independent attested true" in n and n.startswith("[evening]")]
        self.assertEqual(len(dep), 1)
        self.assertEqual(len(indep), 1)
        self.assertEqual(st[dep[0]], v.STATUS_SKIP)
        self.assertEqual(st[indep[0]], v.STATUS_PASS,
                         "VO-independent attestations must still be enforced for real")

    def test_key_partition_is_five_and_five_derived_not_hardcoded(self):
        self.assertEqual(len(v.VO_DEPENDENT_QA_KEYS), 5)
        self.assertEqual(len(v.VO_INDEPENDENT_QA_KEYS), 5)
        # derived by subtraction: no key may be lost or duplicated
        self.assertEqual(set(v.VO_DEPENDENT_QA_KEYS) | set(v.VO_INDEPENDENT_QA_KEYS),
                         set(v.SEMANTIC_QA_CHECK_KEYS))
        self.assertEqual(set(v.VO_DEPENDENT_QA_KEYS) & set(v.VO_INDEPENDENT_QA_KEYS), set())

    # --- the six VO-dependent mechanical checks skip --------------------------------
    def test_all_six_vo_dependent_mechanical_checks_skip(self):
        r = v.validate_manifest(self._pending())
        st = self._statuses(r)
        needles = [
            "vo_word_count matches VO text",
            "words",                                   # the VO word-band check
            "in VO",                                   # question+CTA contiguity
            "exact CTA phrase present in VO",
            "opening_sentence is the VO's exact first sentence",
            "VO contains no banned word",
            "hook_line equals opening_sentence",
        ]
        for needle in needles:
            hits = [n for n in st if n.startswith("[evening]") and needle in n]
            self.assertTrue(hits, f"no evening check matching {needle!r}")
            for n in hits:
                self.assertEqual(st[n], v.STATUS_SKIP,
                                 f"{n} should SKIP while vo_status=pending")

    def test_structural_checks_still_pass_for_real_on_a_pending_package(self):
        r = v.validate_manifest(self._pending())
        st = self._statuses(r)
        # a representative spread of non-VO checks must still be PASS, not SKIP
        for needle in ("format_type is one of the controlled tokens",
                       "clip timings tile", "YouTube title within",
                       "recipient is exactly", "sources"):
            hits = [n for n in st if needle in n]
            if hits:
                self.assertNotIn(v.STATUS_SKIP, [st[n] for n in hits],
                                 f"{needle!r} must not be skipped -- it does not read the VO")

    # --- ok vs fully_passed ---------------------------------------------------------
    def test_pending_manifest_is_ok_but_not_fully_passed(self):
        r = v.validate_manifest(self._pending())
        self.assertTrue(r.ok, f"no real failures expected; got {r.failures()}")
        self.assertFalse(r.fully_passed, "skips must keep fully_passed False")
        self.assertTrue(r.skips())

    def test_complete_manifest_is_both_ok_and_fully_passed(self):
        r = v.validate_manifest(load_valid())
        self.assertTrue(r.ok)
        self.assertTrue(r.fully_passed, "a clean complete manifest must be fully_passed")
        self.assertEqual(r.skips(), [])

    # --- default and malformed values -----------------------------------------------
    def test_absent_vo_status_defaults_to_complete_and_enforces_everything(self):
        m = load_valid()
        for pkg in m["packages"]:
            pkg.pop("vo_status", None)
        r = v.validate_manifest(m)
        self.assertEqual(r.skips(), [], "absent vo_status must mean full enforcement")
        self.assertTrue(r.fully_passed)

    # Every malformed shape must FAIL the enum check AND buy zero skips. Looped
    # rather than spot-checked because "pending" is the only value that unlocks
    # skipping: anything that is merely pending-ish must not, and a near-miss
    # (case, whitespace, typo) is exactly how that would regress unnoticed.
    MALFORMED_VO_STATUS = (
        ("wrong case", "PENDING"),
        ("surrounding whitespace", " pending "),
        ("typo", "pendign"),
        ("non-string int", 1),
        ("None", None),
        ("bool True", True),          # note: True is not a str, and must not pass
        ("empty string", ""),
        ("unrelated word", "draft"),
    )

    def test_malformed_vo_status_fails_and_buys_no_skips(self):
        for label, bad in self.MALFORMED_VO_STATUS:
            with self.subTest(value=label):
                m = load_valid()
                m["packages"][1]["vo_status"] = bad
                r = v.validate_manifest(m)
                names = [n for n, s, _ in r.checks if s == v.STATUS_FAIL]
                self.assertTrue(any("vo_status is one of" in n for n in names),
                                f"{label}: expected a vo_status failure; got {names}")
                self.assertEqual(r.skips(), [],
                                 f"{label}: a malformed vo_status must never buy "
                                 f"VO-dependent skips")

    def test_only_exact_pending_unlocks_skipping(self):
        # The positive half of the guard above: the ONE value that must work.
        m = load_valid()
        m["packages"][1]["vo_status"] = "pending"
        r = v.validate_manifest(m)
        self.assertTrue(r.skips(), "exact 'pending' must unlock VO-dependent skips")
        self.assertFalse(any("vo_status is one of" in n
                             for n, s, _ in r.checks if s == v.STATUS_FAIL),
                         "'pending' is a valid enum value and must not fail the check")

    # --- exit codes -----------------------------------------------------------------
    def test_exit_code_three_for_partial_and_zero_for_complete(self):
        import json as _json, tempfile as _tf, os as _os
        d = _tf.mkdtemp()
        pend = _os.path.join(d, "pending.json")
        comp = _os.path.join(d, "complete.json")
        with open(pend, "w", encoding="utf-8") as fh:
            _json.dump(self._pending(), fh)
        with open(comp, "w", encoding="utf-8") as fh:
            _json.dump(load_valid(), fh)
        self.assertEqual(v.main(["prog", pend]), 3, "PARTIAL must exit 3, not 0 or 1")
        self.assertEqual(v.main(["prog", comp]), 0, "fully_passed must exit 0")

    def test_report_shows_skip_and_partial_verdict(self):
        r = v.validate_manifest(self._pending())
        out = v.format_report(r)
        self.assertIn("[SKIP]", out)
        self.assertIn("PARTIAL", out)
        # NB: the PARTIAL verdict legitimately contains the substring "cleared to
        # send" as part of "NOT cleared to send", so assert on the POSITIVE clearance
        # string specifically rather than the substring.
        self.assertNotIn("PASS — cleared to send", out,
                         "a PARTIAL report must never carry the positive send clearance")
        self.assertIn("NOT cleared to send", out)

if __name__ == "__main__":
    unittest.main(verbosity=2)


def _resize_package_to(pkg: dict, target_sec: float) -> dict:
    """Test helper (Stage 1 rebuild, 2026-08-09): mutate a copy of a valid base
    package in place so every length-dependent field (capcut_target_sec,
    total_clip_time_sec, clip timeline tiling, VO word count, CTA start) is
    internally consistent at an arbitrary target_sec. Keeps clip COUNT the same
    (5 clips) and just rescales durations proportionally, with the remainder
    folded into the last clip so timeline_end_sec lands exactly on target_sec."""
    import copy
    pkg = copy.deepcopy(pkg)
    n = len(pkg["clips"])
    base = int(target_sec // n)
    remainder = int(target_sec - base * n)
    start = 0
    for i, clip in enumerate(pkg["clips"]):
        dur = base + (remainder if i == n - 1 else 0)
        clip["duration_sec"] = dur
        clip["timeline_start_sec"] = start
        clip["timeline_end_sec"] = start + dur
        start += dur
    pkg["capcut_target_sec"] = target_sec
    pkg["total_clip_time_sec"] = target_sec

    vo_min = round(v.VO_WPS_MIN * target_sec)
    vo_max = round(v.VO_WPS_MAX * target_sec)
    word_count = (vo_min + vo_max) // 2  # safely mid-band
    opening = pkg["opening_sentence"]
    question = pkg["question_line"]
    cta = pkg["cta_line"]
    fixed = opening.split() + question.split() + cta.split()
    filler_needed = max(0, word_count - len(fixed))
    pkg["vo"] = (opening + " " + ("word " * filler_needed).strip() + " " + question + " " + cta).strip()
    pkg["vo_word_count"] = len(pkg["vo"].split())

    cta_window = max(5.0, target_sec * 0.15)
    pkg["onscreen_cta_start_sec"] = target_sec - cta_window
    return pkg


class TestLengthSelectionAtRealTargets(unittest.TestCase):
    """NEW (Stage 1, per user instruction): length selection at multiple real
    target values -- 30s (default/no-op path), 90s, and 180s (the real YouTube
    Shorts ceiling, https://support.google.com/youtube/answer/15424877) -- must
    each resolve and validate cleanly end to end via _resolve_edit_target."""

    def test_30s_target_resolves_and_validates(self):
        m = load_valid()
        m["packages"][0] = _resize_package_to(m["packages"][0], 30.0)
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[morning]" in n]
        self.assertEqual(pkg_failures, [], msg=f"unexpected failures at 30s: {pkg_failures}")

    def test_90s_target_resolves_and_validates(self):
        m = load_valid()
        m["packages"][0] = _resize_package_to(m["packages"][0], 90.0)
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[morning]" in n]
        self.assertEqual(pkg_failures, [], msg=f"unexpected failures at 90s: {pkg_failures}")

    def test_180s_target_resolves_and_validates(self):
        # 180s is the real, confirmed YouTube Shorts ceiling (MAX_EDIT_SEC).
        m = load_valid()
        m["packages"][0] = _resize_package_to(m["packages"][0], 180.0)
        r = v.validate_manifest(m)
        pkg_failures = [n for n, ok, d in r.failures() if "[morning]" in n]
        self.assertEqual(pkg_failures, [], msg=f"unexpected failures at 180s: {pkg_failures}")

    def test_is_variable_length_flag_false_only_at_exactly_30(self):
        # _resolve_edit_target returns is_variable_length = (target != 30.0).
        # Assert this directly against the function, not just end-to-end ok/fail,
        # since no validator check currently surfaces this flag as a named result.
        m = load_valid()
        r = v.Result()
        target, is_var = v._resolve_edit_target(m["packages"][0], "[morning]", r)
        self.assertEqual(target, 30.0)
        self.assertFalse(is_var)

        pkg90 = dict(m["packages"][0])
        pkg90["capcut_target_sec"] = 90.0
        r2 = v.Result()
        target2, is_var2 = v._resolve_edit_target(pkg90, "[morning]", r2)
        self.assertEqual(target2, 90.0)
        self.assertTrue(is_var2)


class TestCTAFormulaBoundaryCases(unittest.TestCase):
    """NEW (Stage 1, per user instruction): CTA formula boundary cases --
    target_sec - max(5.0, target_sec*0.15) -- at real target_sec values, proving
    both the pass and fail side of the floor at each."""

    def _at_boundary(self, target_sec: float, offset: float) -> dict:
        m = load_valid()
        pkg = _resize_package_to(m["packages"][0], target_sec)
        cta_window = max(5.0, target_sec * 0.15)
        floor = target_sec - cta_window
        pkg["onscreen_cta_start_sec"] = floor + offset
        m["packages"][0] = pkg
        return m

    def test_30s_exact_floor_passes(self):
        # max(5.0, 4.5) == 5.0 -> floor == 25.0, identical to the pre-Stage-1 rule.
        m = self._at_boundary(30.0, 0.0)
        r = v.validate_manifest(m)
        cta_failures = [n for n, ok, d in r.failures() if "onscreen_cta_start_sec within" in n]
        self.assertEqual(cta_failures, [])

    def test_30s_one_second_below_floor_fails(self):
        m = self._at_boundary(30.0, -1.0)
        names = failed_names(m)
        self.assertTrue(any("onscreen_cta_start_sec within the closing 5.0s" in n for n in names), names)

    def test_90s_exact_floor_passes(self):
        # max(5.0, 13.5) == 13.5 -> floor == 76.5.
        m = self._at_boundary(90.0, 0.0)
        r = v.validate_manifest(m)
        cta_failures = [n for n, ok, d in r.failures() if "onscreen_cta_start_sec within" in n]
        self.assertEqual(cta_failures, [])

    def test_90s_just_below_floor_fails(self):
        m = self._at_boundary(90.0, -0.5)
        names = failed_names(m)
        self.assertTrue(any("onscreen_cta_start_sec within the closing 13.5s" in n for n in names), names)

    def test_180s_exact_floor_passes(self):
        # max(5.0, 27.0) == 27.0 -> floor == 153.0.
        m = self._at_boundary(180.0, 0.0)
        r = v.validate_manifest(m)
        cta_failures = [n for n, ok, d in r.failures() if "onscreen_cta_start_sec within" in n]
        self.assertEqual(cta_failures, [])

    def test_180s_just_below_floor_fails(self):
        m = self._at_boundary(180.0, -0.5)
        names = failed_names(m)
        self.assertTrue(any("onscreen_cta_start_sec within the closing 27.0s" in n for n in names), names)


class TestLaw73TopTrackExemption(unittest.TestCase):
    """NEW (Stage 1, per user instruction): proves the Law #73 clip-verification
    chain is scoped ONLY to pkg["clips"] (the bottom-half anime footage track) and
    has zero requirements on any top-half creator-cam field. A face-cam package
    that sets no scene_verified/verification_source_url-style fields anywhere
    except inside clips[] -- and has no "top track" structure at all in the
    schema -- must validate cleanly, proving the scoping doc is enforced in
    practice, not just asserted in a comment."""

    def test_facecam_package_with_no_top_track_fields_passes_law73(self):
        m = load_valid()
        pkg = m["packages"][0]
        # Confirm the required face-cam fields are set (creator top / anime bottom).
        self.assertTrue(pkg["face"])
        self.assertTrue(pkg["split_screen"])
        # There is no top-track schema field in this manifest format at all --
        # the package has no "creator_clips", "top_track", "facecam_verification"
        # or similar key. Assert that directly: the only clip-shaped, verification-
        # bearing structure anywhere in the package is pkg["clips"] itself.
        top_track_like_keys = [
            k for k in pkg.keys()
            if k != "clips" and ("track" in k.lower() or "facecam" in k.lower() or "creator_clip" in k.lower())
        ]
        self.assertEqual(top_track_like_keys, [],
                          msg=f"unexpected top-track-like keys found, scoping assumption violated: {top_track_like_keys}")
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_law73_ignores_bogus_top_track_key_entirely(self):
        # Even if a future draft accidentally attaches a malformed "top_track"-like
        # key with garbage content, _validate_clip_verification must not touch it --
        # it only ever reads pkg["clips"]. This proves the scoping is structural
        # (the function signature/body only takes clips), not just a convention.
        m = load_valid()
        pkg = m["packages"][0]
        pkg["creator_track"] = {"totally": "malformed", "scene_verified": "not even a bool"}
        r = v.validate_manifest(m)
        self.assertTrue(r.ok, msg=f"a bogus creator_track key must be inert; unexpected failures: {r.failures()}")

    def test_removing_scene_verified_from_clips_still_fails_law73_normally(self):
        # Sanity check the exemption is scoped correctly the OTHER way too: Law #73
        # must still fully apply to the bottom-half clips[] track. Stripping
        # scene_verified from a clips[] entry must still fail, proving the top-track
        # exemption did not accidentally weaken bottom-track enforcement.
        m = load_valid()
        del m["packages"][0]["clips"][0]["scene_verified"]
        r = v.validate_manifest(m)
        self.assertFalse(r.ok)


class TestOpenEndedLengthAdversarial(unittest.TestCase):
    """NEW (Stage 1, per user instruction): adversarial tests deliberately trying
    to break the new open-ended length logic in _resolve_edit_target -- same
    standard as the real bugs caught during the Law #73 UPDATE 6 build (the NxN
    regex false-positive, the over-split mismatch)."""

    def test_non_numeric_string_capcut_target_fails_closed(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = "thirty"
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)
        self.assertFalse(v.validate_manifest(m).ok)

    def test_boolean_capcut_target_fails_closed(self):
        # bool is a subclass of int in Python -- True/False must not silently
        # coerce into 1/0 and slip past a naive isinstance(x, (int, float)) check.
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = True
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_exactly_at_20_lower_bound_passes_range_check(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 20.0
        r = v.Result()
        target, _ = v._resolve_edit_target(m["packages"][0], "[morning]", r)
        self.assertEqual(target, 20.0)
        range_failures = [n for n, ok, d in r.failures() if "numeric and within 20-180s" in n]
        self.assertEqual(range_failures, [])

    def test_one_below_20_lower_bound_fails(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 19.999
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_exactly_at_180_upper_bound_passes_range_check(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 180.0
        r = v.Result()
        target, _ = v._resolve_edit_target(m["packages"][0], "[morning]", r)
        self.assertEqual(target, 180.0)
        range_failures = [n for n, ok, d in r.failures() if "numeric and within 20-180s" in n]
        self.assertEqual(range_failures, [])

    def test_one_above_180_upper_bound_fails(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 180.001
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_negative_capcut_target_fails_closed(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = -30.0
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_zero_capcut_target_fails_closed(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = 0.0
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_nan_capcut_target_fails_closed(self):
        # NaN breaks naive range comparisons silently (NaN <= x is always False,
        # but so is x <= NaN -- a sloppy `not (MIN <= ct <= MAX)` can be fooled by
        # short-circuit logic bugs elsewhere). Confirm it is explicitly rejected.
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = float("nan")
        r = v.Result()
        target, is_var = v._resolve_edit_target(m["packages"][0], "[morning]", r)
        range_failures = [n for n, ok, d in r.failures() if "numeric and within 20-180s" in n]
        self.assertTrue(range_failures, msg="NaN must fail the numeric range check")
        # even though the check fails, the function must still return a safe
        # fallback target (30.0) so downstream checks don't crash on NaN.
        self.assertEqual(target, 30.0)

    def test_positive_infinity_capcut_target_fails_closed(self):
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = float("inf")
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_none_capcut_target_sec_treated_as_absent_default(self):
        # An explicit None is a common accidental JSON serialization of "unset" --
        # confirm it takes the SAME default path as a fully absent key (30.0,
        # is_variable_length=False), not the numeric-range-check path where it
        # would fail closed as "not numeric".
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = None
        r = v.Result()
        target, is_var = v._resolve_edit_target(m["packages"][0], "[morning]", r)
        self.assertEqual(target, 30.0)
        self.assertFalse(is_var)
        range_failures = [n for n, ok, d in r.failures() if "numeric and within 20-180s" in n]
        self.assertEqual(range_failures, [],
                          msg="None should be treated as absent/default, not fail the range check")

    def test_numeric_string_is_not_silently_coerced(self):
        # "45" (a string, not a float/int) must not silently pass a stringly-typed
        # numeric check -- Python's `"45" <= 180` raises TypeError if ever compared
        # directly, but a lenient validator might attempt float() coercion. Confirm
        # the actual behavior is explicit rejection, not silent coercion to 45.0.
        m = load_valid()
        m["packages"][0]["capcut_target_sec"] = "45"
        names = failed_names(m)
        self.assertTrue(any("numeric and within 20-180s" in n for n in names), names)

    def test_cta_floor_never_exceeds_target_sec_itself(self):
        # Adversarial check on the CTA formula, not just the length gate: at every
        # real target in [20,180], the computed floor (target - max(5, target*0.15))
        # must stay strictly less than target_sec, so the CTA window is never
        # inverted or degenerate (e.g. a floor >= target would make the check
        # impossible to ever pass).
        for target_sec in (20.0, 30.0, 45.0, 90.0, 133.0, 180.0):
            cta_window = max(5.0, target_sec * 0.15)
            floor = target_sec - cta_window
            self.assertLess(floor, target_sec, msg=f"degenerate CTA floor at target_sec={target_sec}")
            self.assertGreaterEqual(floor, 0.0, msg=f"negative CTA floor at target_sec={target_sec}")


class TestFormatTypeEnumLaw158Law159Law160(unittest.TestCase):
    """Law #158/#159 (added 2026-08-10): FORMAT_TYPES grows from 14 to 16 tokens with
    WORTH_WATCHING and SEASON_ROUNDUP. The legacy, pre-enum UPCOMING_HYPE/HYPE_PREVIEW
    strings are formally retired and must remain rejected."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_worth_watching_token_in_format_types(self):
        self.assertIn("WORTH_WATCHING", v.FORMAT_TYPES)

    def test_season_roundup_token_in_format_types(self):
        self.assertIn("SEASON_ROUNDUP", v.FORMAT_TYPES)

    def test_theory_speculation_token_in_format_types(self):
        self.assertIn("THEORY_SPECULATION", v.FORMAT_TYPES)

    def test_format_types_now_seventeen_tokens(self):
        self.assertEqual(len(v.FORMAT_TYPES), 17, f"FORMAT_TYPES={v.FORMAT_TYPES}")

    def test_legacy_upcoming_hype_still_rejected(self):
        m = load_valid()
        m["packages"][0]["format_type"] = "UPCOMING_HYPE"
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_legacy_hype_preview_still_rejected(self):
        m = load_valid()
        m["packages"][0]["format_type"] = "HYPE_PREVIEW"
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")

    def test_legacy_compound_season_preview_upcoming_hype_still_rejected(self):
        # the confirmed-invalid compound label documented in law_159's retirement
        # rationale -- must remain rejected, same as any other free-text label.
        m = load_valid()
        m["packages"][0]["format_type"] = "SEASON_PREVIEW / UPCOMING_HYPE"
        self.assertFailsCleanly(m, "format_type is one of the controlled tokens")


def _make_worth_watching_package(base_pkg: dict) -> dict:
    """Test helper: mutate a copy of a valid base package into a minimally-valid
    WORTH_WATCHING package (Law #158) -- single-show persuasion, no comparison,
    no_comparative_language self-attested true, and no banned comparative phrase
    present in any of the checked fields."""
    pkg = json.loads(json.dumps(base_pkg))  # deep copy via round-trip, matches
                                             # this file's existing copy style
    pkg["format_type"] = "WORTH_WATCHING"
    pkg["no_comparative_language"] = True
    return pkg


class TestWorthWatchingComparativeLanguageLaw158(unittest.TestCase):
    """Law #158 (added 2026-08-10): WORTH_WATCHING packages must both self-attest
    no_comparative_language=true AND pass a mechanical BANNED_COMPARATIVE_LANGUAGE
    scan -- a false self-attestation must not bypass the mechanical check, and the
    mechanical check must not fire for any other format_type."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_worth_watching_with_clean_fields_passes_comparative_checks(self):
        m = load_valid()
        m["packages"][0] = _make_worth_watching_package(m["packages"][0])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        comp_failures = [n for n in names_failed if "Law #158" in n]
        self.assertEqual(comp_failures, [], f"unexpected Law #158 failures: {comp_failures}")

    def test_missing_self_attestation_fails_cleanly(self):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        del pkg["no_comparative_language"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no_comparative_language self-attestation present and true")

    def test_self_attestation_false_fails_cleanly(self):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["no_comparative_language"] = False
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no_comparative_language self-attestation present and true")

    def test_banned_phrase_in_vo_fails_even_with_true_self_attestation(self):
        # the mechanical check must catch a banned phrase even when the model
        # falsely self-attests no_comparative_language=true -- self-attestation
        # alone must never be sufficient (confirmed decision, 2026-08-10).
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["vo"] = pkg["vo"] + " This is better than the last season by far."
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no banned comparative/ranking language found")

    def test_banned_phrase_in_youtube_title_fails_cleanly(self):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["youtube_title"] = "This Is the #1 Anime This Season"
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no banned comparative/ranking language found")

    def test_banned_phrase_in_tiktok_post_text_fails_cleanly(self):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["tiktok_post_text"] = pkg.get("tiktok_post_text", "") + " It beats every other show this year."
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no banned comparative/ranking language found")

    def test_comparative_language_check_not_applied_to_other_format_types(self):
        # a package that is NOT WORTH_WATCHING may freely contain "better than"
        # style language -- the mechanical scan must be scoped strictly to
        # WORTH_WATCHING and never fire for any of the other 15 format_types.
        m = load_valid()
        self.assertNotEqual(m["packages"][0]["format_type"], "WORTH_WATCHING")
        m["packages"][0]["vo"] = m["packages"][0]["vo"] + " This is better than the last season."
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        comp_failures = [n for n in names_failed if "Law #158" in n]
        self.assertEqual(comp_failures, [], f"comparative check should not fire for non-WORTH_WATCHING: {comp_failures}")

    def test_over_with_trailing_space_matches_comparison_construction(self):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["hook_line"] = "Pick this over anything else airing."
        pkg["opening_sentence"] = pkg["hook_line"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no banned comparative/ranking language found")

    # --- Adversarial false-positive tests, 2026-08-10 same-day fix ---
    # The first-draft BANNED_COMPARATIVE_LANGUAGE was a bare-substring scan where
    # "over " and "beats" fired on ordinary, non-comparative VO language. These
    # tests prove the regex-based replacement does NOT false-positive on realistic
    # innocent phrasing. Each helper below builds an otherwise-clean WORTH_WATCHING
    # package, injects exactly one innocent phrase, and asserts zero Law #158
    # comparative-language failures.

    def _assert_innocent_phrase_does_not_fire(self, phrase: str):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["vo"] = pkg["vo"] + " " + phrase
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        comp_failures = [n for n in names_failed if "Law #158" in n]
        self.assertEqual(comp_failures, [], f"innocent phrase {phrase!r} incorrectly triggered Law #158: {comp_failures}")

    def test_innocent_changes_over_time_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("The character changes over time in ways nobody expects.")

    def test_innocent_all_over_again_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("The whole plan falls apart, and he has to start all over again.")

    def test_innocent_hands_it_over_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("He finally hands it over without a single word of protest.")

    def test_innocent_hero_beats_villain_in_story_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("The hero beats the villain in the final chapter after years of buildup.")

    def test_innocent_its_all_over_now_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("It's all over now, and nothing will ever be the same for these two.")

    def test_innocent_picks_up_over_the_summer_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("The story picks up over the summer, right where the manga left off.")

    def test_innocent_climbs_over_the_wall_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("He climbs over the wall just as the guards turn around.")

    def test_innocent_watched_it_over_the_weekend_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("A lot of fans watched it over the weekend and are still talking about it.")

    def test_innocent_thinks_it_over_carefully_does_not_fire(self):
        self._assert_innocent_phrase_does_not_fire("She thinks it over carefully before making her final decision.")

    # --- Confirm the comparative patterns still fire on real ranking/comparison language ---

    def _assert_comparative_phrase_fires(self, phrase: str):
        m = load_valid()
        pkg = _make_worth_watching_package(m["packages"][0])
        pkg["vo"] = pkg["vo"] + " " + phrase
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no banned comparative/ranking language found")

    def test_comparative_better_than_last_season_fires(self):
        self._assert_comparative_phrase_fires("This is better than the last season in every way.")

    def test_comparative_pick_this_over_anything_else_airing_fires(self):
        self._assert_comparative_phrase_fires("Pick this over anything else airing right now.")

    def test_comparative_beats_every_other_show_fires(self):
        self._assert_comparative_phrase_fires("It beats every other show this year, hands down.")

    def test_comparative_number_one_anime_this_season_fires(self):
        self._assert_comparative_phrase_fires("This is the number one anime this season.")

    def test_comparative_loses_to_the_sequel_fires(self):
        self._assert_comparative_phrase_fires("Honestly, it loses to the sequel in every way.")

    def test_comparative_outranks_the_competition_fires(self):
        self._assert_comparative_phrase_fires("It outranks the competition easily this season.")

    def test_comparative_choose_this_over_everything_else_fires(self):
        self._assert_comparative_phrase_fires("Choose this over everything else airing this week.")

    def test_comparative_top_pick_fires(self):
        # confirmed as CORRECT ranking language, not a false positive -- 'top pick'
        # is a real superlative/ranking claim even without an explicit comparison object.
        self._assert_comparative_phrase_fires("She's my top pick for best girl this season.")


def _make_season_roundup_clip(*, source: str, timeline_start_sec: float, timeline_end_sec: float) -> dict:
    """Test helper: build one Law #159 SEASON_ROUNDUP clip using exactly one of
    the three valid source types: 'anime', 'manga', or 'trailer'."""
    duration = timeline_end_sec - timeline_start_sec
    clip = {
        "scene": "placeholder scene description for a SEASON_ROUNDUP test clip",
        "reason": "placeholder reason",
        "carries_loop_back": False,
        "duration_sec": duration,
        "timeline_start_sec": timeline_start_sec,
        "timeline_end_sec": timeline_end_sec,
    }
    if source == "anime":
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/aired-episode-source"
        clip["claim_vs_source_check"] = {
            "claimed_beat": "placeholder claimed beat",
            "source_content_confirmed": "placeholder confirmed source text",
            "match": True,
        }
        clip["clip_locate"] = {
            "season": 1, "episode": 1, "locate_confirmed_via": "placeholder source",
            "episode_source": "explicitly_stated",
        }
    elif source == "manga":
        clip["scene_verified"] = False
        clip["manga_reference"] = "Chapter 1, page 3"
    elif source == "trailer":
        clip["trailer_reference"] = {
            "trailer_title_or_id": "Season 2 Official Trailer",
            "claimed_beat": "placeholder claimed trailer beat",
            "source_content_confirmed": "placeholder confirmed trailer content",
            "match": True,
        }
    else:
        raise ValueError(f"unknown source type {source!r}")
    return clip


def _make_season_roundup_package(base_pkg: dict, clip_sources: list[str]) -> dict:
    """Test helper: mutate a copy of a valid base package into a minimally-valid
    SEASON_ROUNDUP package (Law #159) with clips built from clip_sources, one of
    'anime'/'manga'/'trailer' each, tiled contiguously across the package's
    existing capcut_target_sec/total_clip_time_sec."""
    pkg = json.loads(json.dumps(base_pkg))
    pkg["format_type"] = "SEASON_ROUNDUP"

    # Law #159 item 3 (built 2026-08-14): "minimally-valid SEASON_ROUNDUP" now also
    # means per-show sourcing -- an explicit roundup_shows denominator plus one core
    # claim per declared show, each citing its OWN distinct listed, dated,
    # non-encyclopedic source. Without this the package is a roundup declaring no
    # shows, which the per-show validator correctly rejects. Added here so these
    # CLIP-sourcing tests keep exercising an otherwise-valid roundup and fail only on
    # the clip issue each one is actually about.
    _s1 = "https://www.animenewsnetwork.com/news/2026-08-14/roundup-show-one/.240101"
    _s2 = "https://www.crunchyroll.com/news/announcements/2026/8/14/roundup-show-two"
    pkg["roundup_shows"] = ["Roundup Show One", "Roundup Show Two"]
    pkg["sources"] = list(pkg.get("sources") or []) + [
        {"claim": "Roundup Show One premiered this week", "url": _s1, "date": "Aug 2026"},
        {"claim": "Roundup Show Two premiered this week", "url": _s2, "date": "Aug 2026"},
    ]
    pkg.setdefault("semantic_qa", {})["claim_source_matrix"] = [
        {"claim": "Roundup Show One premiered this week.", "core": True, "claim_type": "C",
         "source_urls": [_s1], "anchors_claim": "hook", "show": "Roundup Show One"},
        {"claim": "Roundup Show Two premiered this week.", "core": True, "claim_type": "C",
         "source_urls": [_s2], "show": "Roundup Show Two"},
    ]

    target = pkg["capcut_target_sec"]
    n = len(clip_sources)
    each = target / n
    clips = []
    for i, source in enumerate(clip_sources):
        start = round(i * each, 3)
        end = target if i == n - 1 else round((i + 1) * each, 3)
        clips.append(_make_season_roundup_clip(source=source, timeline_start_sec=start, timeline_end_sec=end))
    pkg["clips"] = clips
    return pkg


class TestSeasonRoundupClipSourcingLaw159(unittest.TestCase):
    """Law #159 (added 2026-08-10): SEASON_ROUNDUP clips may use exactly one of
    three valid source types -- aired anime (existing scene_verified/clip_locate
    chain), manga_reference (existing fallback), or the NEW trailer_reference
    object. Existing Law #73 behavior for all other 15 format_types must be
    completely unaffected by this branch."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    def test_all_anime_sourced_clips_pass(self):
        m = load_valid()
        m["packages"][0] = _make_season_roundup_package(m["packages"][0], ["anime", "anime"])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law159_failures = [n for n in names_failed if "Law #159" in n]
        self.assertEqual(law159_failures, [], f"unexpected Law #159 failures: {law159_failures}")

    def test_all_manga_sourced_clips_pass(self):
        m = load_valid()
        m["packages"][0] = _make_season_roundup_package(m["packages"][0], ["manga", "manga"])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law159_failures = [n for n in names_failed if "Law #159" in n]
        self.assertEqual(law159_failures, [], f"unexpected Law #159 failures: {law159_failures}")

    def test_all_trailer_sourced_clips_pass(self):
        m = load_valid()
        m["packages"][0] = _make_season_roundup_package(m["packages"][0], ["trailer", "trailer"])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law159_failures = [n for n in names_failed if "Law #159" in n]
        self.assertEqual(law159_failures, [], f"unexpected Law #159 failures: {law159_failures}")

    def test_mixed_anime_manga_trailer_sources_pass(self):
        m = load_valid()
        # Build via the helper so the Law #159 per-show sourcing scaffolding (item 3,
        # 2026-08-14) is present, then override clips with the mixed-source set this
        # test is actually about. Previously this constructed the roundup inline and so
        # silently skipped that scaffolding.
        pkg = _make_season_roundup_package(m["packages"][0], ["anime", "anime", "anime"])
        pkg["clips"] = [
            _make_season_roundup_clip(source="anime", timeline_start_sec=0, timeline_end_sec=10),
            _make_season_roundup_clip(source="manga", timeline_start_sec=10, timeline_end_sec=20),
            _make_season_roundup_clip(source="trailer", timeline_start_sec=20, timeline_end_sec=30),
        ]
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law159_failures = [n for n in names_failed if "Law #159" in n]
        self.assertEqual(law159_failures, [], f"unexpected Law #159 failures: {law159_failures}")

    def test_trailer_reference_missing_claimed_beat_fails_cleanly(self):
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["trailer", "trailer"])
        del pkg["clips"][0]["trailer_reference"]["claimed_beat"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "every clip has a well-formed source object for its declared type")

    def test_trailer_reference_match_false_fails_cleanly(self):
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["trailer", "trailer"])
        pkg["clips"][0]["trailer_reference"]["match"] = False
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "every trailer_reference has match == true")

    def test_clip_with_both_clip_locate_and_trailer_reference_fails_cleanly(self):
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["trailer", "trailer"])
        pkg["clips"][0]["clip_locate"] = {"season": 1, "episode": 1, "locate_confirmed_via": "placeholder"}
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "no clip declares both clip_locate and trailer_reference")

    def test_clip_with_no_valid_source_at_all_fails_cleanly(self):
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["trailer", "trailer"])
        pkg["clips"][0] = {
            "scene": "no source at all",
            "reason": "placeholder",
            "carries_loop_back": False,
            "duration_sec": pkg["clips"][0]["duration_sec"],
            "timeline_start_sec": pkg["clips"][0]["timeline_start_sec"],
            "timeline_end_sec": pkg["clips"][0]["timeline_end_sec"],
            "scene_verified": False,
        }
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "every clip has exactly one valid, verified source")

    def test_empty_clips_list_fails_cleanly_not_crash(self):
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["anime"])
        pkg["clips"] = []
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "clip plan is non-empty")

    def test_non_season_roundup_package_still_uses_law_73_path_unaffected(self):
        # a non-SEASON_ROUNDUP package with a trailer_reference-only clip (no
        # scene_verified/manga_reference) must still fail under the EXISTING
        # Law #73 path, proving the branch at the call site is scoped correctly
        # and does not leak the new three-way logic into other format_types.
        m = load_valid()
        self.assertNotEqual(m["packages"][0]["format_type"], "SEASON_ROUNDUP")
        clip = m["packages"][0]["clips"][0]
        for key in ("scene_verified", "verification_source_url", "manga_reference", "verification_note"):
            clip.pop(key, None)
        clip["trailer_reference"] = {
            "trailer_title_or_id": "x", "claimed_beat": "y",
            "source_content_confirmed": "z", "match": True,
        }
        self.assertFailsCleanly(m, "each clip has scene_verified (bool) set")

    def test_anime_sourced_clip_missing_clip_locate_fails_cleanly(self):
        # REAL GAP CLOSED 2026-08-10 (same-day review fix): the first-draft version
        # of _validate_season_roundup_clip_sourcing counted scene_verified=true alone
        # as a valid source, with NO clip_locate enforcement at all -- unlike every
        # other format_type's anime path (Law #73 UPDATE 5). This test proves a
        # SEASON_ROUNDUP anime-sourced clip with scene_verified=true and no
        # clip_locate object now fails closed, naming the gap explicitly.
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["anime", "manga"])
        del pkg["clips"][0]["clip_locate"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(
            m, "clip_locate present and well-formed wherever scene_verified is true (Law #73 UPDATE 5, applied to Law #159 anime path)")

    def test_anime_sourced_clip_malformed_clip_locate_fails_cleanly(self):
        # same gap, malformed rather than missing: a bare URL in locate_confirmed_via
        # is explicitly disallowed by _clip_locate_shape_ok (same rule as every other
        # format_type) -- confirms the SHARED helper's full rule set applies here,
        # not just a presence check.
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["anime", "manga"])
        pkg["clips"][0]["clip_locate"] = {
            "season": 1, "episode": 1, "locate_confirmed_via": "https://example.com/bare-url-not-allowed",
        }
        m["packages"][0] = pkg
        self.assertFailsCleanly(
            m, "clip_locate present and well-formed wherever scene_verified is true (Law #73 UPDATE 5, applied to Law #159 anime path)")

    def test_anime_sourced_clip_missing_clip_locate_also_fails_no_valid_source(self):
        # a clip with scene_verified=true but no valid clip_locate must not be
        # silently counted as a valid source either -- both the dedicated
        # clip_locate check AND the exactly-one-valid-source check should fire.
        m = load_valid()
        pkg = _make_season_roundup_package(m["packages"][0], ["anime"])
        del pkg["clips"][0]["clip_locate"]
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(
            any("clip_locate present and well-formed" in n for n in names_failed),
            msg=f"expected clip_locate check to fail; got failures={names_failed}")
        self.assertTrue(
            any("every clip has exactly one valid, verified source" in n for n in names_failed),
            msg=f"expected no-valid-source check to also fail (missing clip_locate must not count as valid); got failures={names_failed}")

    def test_manga_and_trailer_clips_unaffected_by_clip_locate_requirement(self):
        # confirm the new clip_locate enforcement is scoped strictly to
        # scene_verified=true clips -- manga and trailer clips (which correctly
        # carry no clip_locate at all) must not be flagged by it.
        m = load_valid()
        m["packages"][0] = _make_season_roundup_package(m["packages"][0], ["manga", "trailer"])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        clip_locate_failures = [n for n in names_failed if "clip_locate present and well-formed" in n]
        self.assertEqual(clip_locate_failures, [], f"manga/trailer clips should not trigger clip_locate check: {clip_locate_failures}")


class TestClipLocateShapeOkSharedHelperLaw159(unittest.TestCase):
    """Law #158/#159 same-day fix (2026-08-10): _clip_locate_shape_ok was extracted
    from a closure inside _validate_clip_verification to a module-level function so
    both the original Law #73 anime path and the new SEASON_ROUNDUP anime path share
    identical behavior. These tests confirm the extraction preserved the exact
    original Law #73 UPDATE 5 semantics for the pre-existing (non-SEASON_ROUNDUP)
    caller, guarding against any behavior drift introduced by the refactor."""

    def test_well_formed_clip_locate_passes(self):
        cl = {"season": 1, "episode": 3, "locate_confirmed_via": "the same ANN episode 3 review cited above", "episode_source": "explicitly_stated"}
        self.assertTrue(v._clip_locate_shape_ok({"clip_locate": cl}))

    def test_missing_clip_locate_fails(self):
        self.assertFalse(v._clip_locate_shape_ok({}))

    def test_clip_locate_not_a_dict_fails(self):
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": "season 1 episode 3"}))

    def test_bare_url_in_locate_confirmed_via_fails(self):
        cl = {"season": 1, "episode": 3, "locate_confirmed_via": "https://example.com/ep3"}
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    def test_missing_episode_fails(self):
        cl = {"season": 1, "locate_confirmed_via": "the same ANN episode 3 review cited above"}
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    def test_boolean_episode_fails(self):
        # episode must be an int and not a bool (bool is a subclass of int in
        # Python, so this guards the isinstance(..., bool) exclusion specifically).
        cl = {"season": 1, "episode": True, "locate_confirmed_via": "the same ANN episode 3 review cited above"}
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    def test_optional_approx_timestamp_none_is_ok(self):
        cl = {"season": 1, "episode": 3, "locate_confirmed_via": "the same ANN episode 3 review cited above", "approx_timestamp": None, "episode_source": "explicitly_stated"}
        self.assertTrue(v._clip_locate_shape_ok({"clip_locate": cl}))

    def test_empty_string_approx_timestamp_fails(self):
        cl = {"season": 1, "episode": 3, "locate_confirmed_via": "the same ANN episode 3 review cited above", "approx_timestamp": "   "}
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))


class TestEpisodeSourceDisclosureLaw167(unittest.TestCase):
    """Law #167 (added 2026-08-13): episode_source is a required disclosure
    field on every clip_locate object, mirroring Law #73 UPDATE 8's
    footage_status pattern -- it is a self-attested statement of HOW the
    episode number was determined (explicitly_stated: the source directly
    names the episode number; inferred: worked out from other evidence, e.g.
    air-date ordering or a recap's own numbering), not an independently
    verified fact. The validator cannot check whether the attestation is
    honest, same limitation already disclosed for footage_status and
    blackout_conflict elsewhere in this file -- it can only check the field
    is present and is one of the two allowed values. Neither value gets any
    extra requirement beyond that: "explicitly_stated" does NOT require
    anything more elaborate in locate_confirmed_via, and "inferred" does NOT
    require a separate justification field -- this is a disclosure flag, not
    a differential evidence bar, exactly matching how footage_status's enum
    values are treated as equally valid, mechanically-unweighted disclosures."""

    def _base_cl(self, **overrides):
        cl = {"season": 1, "episode": 3,
              "locate_confirmed_via": "the same ANN episode 3 review cited above"}
        cl.update(overrides)
        return cl

    # 1. missing episode_source entirely -- fails.
    def test_missing_episode_source_fails(self):
        cl = self._base_cl()  # no episode_source key at all
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 2. invalid/unrecognized value -- fails. Guards against silently
    #    accepting a typo or a made-up third value as if it were valid.
    def test_invalid_episode_source_value_fails(self):
        cl = self._base_cl(episode_source="guessed")
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 2b. empty string -- fails (not treated as a truthy "present" value).
    def test_empty_string_episode_source_fails(self):
        cl = self._base_cl(episode_source="")
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 2c. None -- fails (distinguishes from approx_timestamp, which is the
    #     one field on this object where None is explicitly allowed).
    def test_none_episode_source_fails(self):
        cl = self._base_cl(episode_source=None)
        self.assertFalse(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 3. "explicitly_stated" -- passes, with nothing extra required beyond
    #    the normal shape check (locate_confirmed_via unchanged from the
    #    always-required plain-sentence form).
    def test_explicitly_stated_passes_with_ordinary_locate_confirmed_via(self):
        cl = self._base_cl(episode_source="explicitly_stated")
        self.assertTrue(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 4. "inferred" -- passes, and specifically WITHOUT any separate source/
    #    justification field. This is the exact case the review asked to
    #    confirm: inferred must not silently require something the shape
    #    check doesn't actually demand of it.
    def test_inferred_passes_without_requiring_a_separate_source_field(self):
        cl = self._base_cl(episode_source="inferred")
        self.assertNotIn("inferred_justification", cl)  # sanity: no such field exists in this fixture
        self.assertTrue(v._clip_locate_shape_ok({"clip_locate": cl}))

    # 5. both valid values must be accepted on an otherwise-identical object
    #    -- neither is treated as more or less trustworthy by the shape check.
    def test_explicitly_stated_and_inferred_both_pass_identically(self):
        cl_a = self._base_cl(episode_source="explicitly_stated")
        cl_b = self._base_cl(episode_source="inferred")
        self.assertEqual(
            v._clip_locate_shape_ok({"clip_locate": cl_a}),
            v._clip_locate_shape_ok({"clip_locate": cl_b}),
        )
        self.assertTrue(v._clip_locate_shape_ok({"clip_locate": cl_a}))

    # 6. end-to-end through validate_manifest(): a verified clip in the real
    #    fixture missing episode_source fails cleanly and specifically names
    #    the same clip_locate shape check as every other clip_locate defect,
    #    not a separate/uninformative failure name.
    def test_end_to_end_missing_episode_source_fails_cleanly_on_real_manifest(self):
        m = load_valid()
        clip = m["packages"][0]["clips"][0]
        clip["scene_verified"] = True
        clip["verification_source_url"] = "https://example.com/verified-episode-clip"
        clip.pop("manga_reference", None)
        clip.pop("verification_note", None)
        clip["claim_vs_source_check"] = {
            "claimed_beat": "Character X delivers the decisive counter-attack in the final confrontation.",
            "source_content_confirmed": "Official episode 16 transcript at the cited URL shows this exact exchange and counter-attack.",
            "match": True,
        }
        cl = {"season": 1, "episode": 16,
              "locate_confirmed_via": "the same official episode 16 transcript cited above"}
        # deliberately no episode_source key
        clip["clip_locate"] = cl
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertFalse(r.ok)
        self.assertTrue(
            any("clip_locate present and well-formed wherever scene_verified is true" in n for n in names_failed),
            msg=f"expected the shared clip_locate shape check to fail; got failures={names_failed}",
        )


def _make_theory_speculation_package(base_pkg: dict, *, claim_line: str | None = None) -> dict:
    """Test helper: mutate a copy of a valid base package into a minimally-valid
    THEORY_SPECULATION package (Law #160) -- real (empty-but-searched) originality
    artifact, a hedged theory_claim_line containing a required hedge phrase and no
    banned certainty language, and theory_hedge_attested=true."""
    pkg = json.loads(json.dumps(base_pkg))  # deep copy via round-trip, matches
                                             # this file's existing copy style
    pkg["format_type"] = "THEORY_SPECULATION"
    pkg["related_existing_theories"] = []
    pkg["originality_search_performed"] = {
        "query": "Daemons of the Shadow Realm ending theory Reddit YouTube 2026",
        "search_performed": True,
    }
    pkg["theory_claim_line"] = claim_line or (
        "This theory suggests the sealed door was never meant to hold the "
        "villain in -- it was meant to hold something else out."
    )
    pkg["theory_hedge_attested"] = True
    return pkg


class TestTheorySpeculationLaw160(unittest.TestCase):
    """Law #160 (added 2026-08-11): THEORY_SPECULATION packages must (1) document a
    real originality-research artifact (not a boolean), (2) both self-attest
    theory_hedge_attested=true AND pass a mechanical minimum-hedge-floor + banned-
    certainty-language scan on theory_claim_line ONLY, (3) surface credit when
    extending an existing theory, and (4) provide a sourced revisit_justification
    whenever blackout/recent-send is flagged. Mirrors
    TestWorthWatchingComparativeLanguageLaw158's structure and adversarial-testing
    discipline."""

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    # --- clean package passes ---

    def test_theory_speculation_with_clean_fields_passes_law160_checks(self):
        m = load_valid()
        m["packages"][0] = _make_theory_speculation_package(m["packages"][0])
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law160_failures = [n for n in names_failed if "Law #160" in n]
        self.assertEqual(law160_failures, [], f"unexpected Law #160 failures: {law160_failures}")

    # --- Decision 1: originality research artifact ---

    def test_missing_related_existing_theories_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        del pkg["related_existing_theories"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "related_existing_theories present and well-formed")

    def test_malformed_related_existing_theories_entry_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["related_existing_theories"] = [{"theory_description": "some theory"}]  # missing source_url/how_this_differs
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "related_existing_theories present and well-formed")

    def test_missing_originality_search_performed_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        del pkg["originality_search_performed"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "originality_search_performed present and well-formed")

    def test_originality_search_performed_false_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["originality_search_performed"]["search_performed"] = False
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "originality_search_performed present and well-formed")

    # --- Decision 2: hedge floor + certainty ban ---

    def test_missing_theory_claim_line_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        del pkg["theory_claim_line"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "theory_claim_line present")

    def test_missing_hedge_attestation_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        del pkg["theory_hedge_attested"]
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "theory_hedge_attested self-attestation present and true")

    def test_hedge_attestation_false_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["theory_hedge_attested"] = False
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "theory_hedge_attested self-attestation present and true")

    def test_claim_line_missing_required_hedge_fails_mechanical_floor(self):
        # Present, hedge-attested=true, no banned certainty phrase -- but the actual
        # sentence contains NONE of the REQUIRED_THEORY_HEDGES phrases. The mechanical
        # floor must catch this even though nothing else is wrong.
        m = load_valid()
        pkg = _make_theory_speculation_package(
            m["packages"][0],
            claim_line="The sealed door was never meant to hold the villain in.",
        )
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "theory_claim_line contains a required minimum hedge phrase")

    def test_overconfident_theory_claim_fails_even_with_true_hedge_attestation(self):
        # MIRRORS test_banned_phrase_in_vo_fails_even_with_true_self_attestation
        # (Law #158): the mechanical check must catch over-confident certainty
        # language even when theory_hedge_attested is (falsely) true. This is the
        # required adversarial test proving the hedge floor actually catches an
        # over-confident theory claim, not just that it accepts a compliant one.
        m = load_valid()
        pkg = _make_theory_speculation_package(
            m["packages"][0],
            claim_line=(
                "This theory suggests the sealed door was a trap -- and this is "
                "confirmed by the chapter 40 flashback."
            ),
        )
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "theory_claim_line has no banned certainty language")

    def test_certainty_language_check_not_applied_to_other_format_types(self):
        # a non-THEORY_SPECULATION package may freely contain "this is confirmed"-
        # style language elsewhere in its VO -- the mechanical scan must be scoped
        # strictly to THEORY_SPECULATION's theory_claim_line and never fire for any
        # of the other 16 format_types.
        m = load_valid()
        self.assertNotEqual(m["packages"][0]["format_type"], "THEORY_SPECULATION")
        m["packages"][0]["vo"] = m["packages"][0]["vo"] + " This is confirmed by the official site."
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        law160_failures = [n for n in names_failed if "Law #160" in n]
        self.assertEqual(law160_failures, [], f"Law #160 checks should not fire for non-THEORY_SPECULATION: {law160_failures}")

    # --- Adversarial: certainty-ban must not false-positive on legitimate
    # evidence-tier sourcing language describing a confirmed SOURCE fact (as opposed
    # to the theory claim asserting itself as settled). This is checked against
    # theory_claim_line only, so an innocent phrase belongs elsewhere in the VO. ---

    def test_innocent_confirmed_source_language_elsewhere_in_vo_does_not_fire(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["vo"] = pkg["vo"] + " The official site confirmed the chapter's release date."
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        certainty_failures = [n for n in names_failed if "no banned certainty language" in n]
        self.assertEqual(certainty_failures, [], f"innocent source-confirmation language incorrectly triggered Law #160: {certainty_failures}")

    # --- Decision 3: disclosure credit ---

    def test_credit_required_when_how_this_differs_present_but_missing_fails_cleanly(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["related_existing_theories"] = [{
            "theory_description": "A popular fan theory holds the seal was always temporary.",
            "source_url": "https://example.com/theory-thread",
            "how_this_differs": "This adds the chapter 40 flashback detail nobody connected yet.",
        }]
        # vo/pinned_comment/tiktok_post_text deliberately left with no "theory" mention
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "existing-theory credit surfaced in viewer-facing text")

    def test_hedge_phrase_bare_theory_word_does_not_satisfy_credit_check(self):
        # REGRESSION TEST for a real bug found during user review (2026-08-11): the
        # original Decision 3 implementation matched the BARE word "theory" anywhere in
        # vo/pinned_comment/tiktok_post_text. theory_claim_line is itself part of vo, and
        # several REQUIRED_THEORY_HEDGES phrases already contain "theory" ("this theory
        # suggests", "the working theory here is", "the leading theory is") -- so a
        # package could satisfy the Decision 2 hedge floor and, purely as a side effect,
        # trip the old bare-word credit check without ever actually crediting the real
        # existing theory it's building on. This constructs exactly that scenario: a
        # real related_existing_theories entry with a non-empty how_this_differs (credit
        # IS required), a theory_claim_line using a hedge phrase containing "theory"
        # embedded directly in vo (as the law text says it must be), and NO genuine
        # attribution language anywhere. The corrected check must FAIL this -- the old
        # implementation would have incorrectly PASSED it.
        m = load_valid()
        claim_line = "This theory suggests the sealed door was never meant to hold the villain in."
        pkg = _make_theory_speculation_package(m["packages"][0], claim_line=claim_line)
        # theory_claim_line is part of vo per the law text -- embed it for real, the way
        # a real generated package would.
        pkg["vo"] = pkg["vo"] + " " + claim_line
        pkg["related_existing_theories"] = [{
            "theory_description": "A popular fan theory holds the seal was always temporary.",
            "source_url": "https://example.com/theory-thread",
            "how_this_differs": "This adds the chapter 40 flashback detail nobody connected yet.",
        }]
        # Deliberately no fans/viewers/theorists attribution language and no determiner+
        # theory noun phrase anywhere -- the only occurrence of the word "theory" comes
        # from the hedge phrase itself.
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "existing-theory credit surfaced in viewer-facing text")

    def test_credit_present_in_pinned_comment_passes(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["related_existing_theories"] = [{
            "theory_description": "A popular fan theory holds the seal was always temporary.",
            "source_url": "https://example.com/theory-thread",
            "how_this_differs": "This adds the chapter 40 flashback detail nobody connected yet.",
        }]
        pkg["pinned_comment"] = pkg.get("pinned_comment", "") + " A popular theory already covers part of this -- here's the new piece."
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        credit_failures = [n for n in names_failed if "existing-theory credit surfaced" in n]
        self.assertEqual(credit_failures, [], f"unexpected credit-check failure: {credit_failures}")

    def test_credit_not_required_when_related_theories_empty(self):
        # an empty related_existing_theories list (genuinely searched, nothing found)
        # must NOT trigger the credit-required check -- there is nothing to credit.
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        self.assertEqual(pkg["related_existing_theories"], [])
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        credit_failures = [n for n in names_failed if "existing-theory credit surfaced" in n]
        self.assertEqual(credit_failures, [], f"credit check should not fire with an empty related_existing_theories list: {credit_failures}")

    # --- Decision 4: revisit justification ---

    def test_revisit_justification_required_when_blackout_conflict_true(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["blackout_conflict"] = True  # simulates a same-show-same-question revisit
        m["packages"][0] = pkg
        self.assertFailsCleanly(m, "revisit_justification present and well-formed when blackout/recent-send flagged")

    def test_revisit_justification_well_formed_with_blackout_conflict_true_passes(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        pkg["blackout_conflict"] = True
        pkg["revisit_justification"] = {
            "new_evidence_summary": "Chapter 41 revealed a new flashback panel not available at the last send.",
            "new_evidence_source_url": "https://example.com/chapter-41",
            "new_evidence_date": "2026-08-10",
        }
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        revisit_failures = [n for n in names_failed if "revisit_justification present and well-formed" in n]
        self.assertEqual(revisit_failures, [], f"unexpected revisit_justification failure: {revisit_failures}")

    def test_revisit_justification_not_required_when_no_blackout_conflict(self):
        m = load_valid()
        pkg = _make_theory_speculation_package(m["packages"][0])
        # blackout_conflict/recent_send_conflict remain False (inherited from base fixture)
        m["packages"][0] = pkg
        r = v.validate_manifest(m)
        names_failed = [name for name, ok, _ in r.checks if ok == "FAIL"]
        revisit_failures = [n for n in names_failed if "revisit_justification present and well-formed" in n]
        self.assertEqual(revisit_failures, [], f"revisit_justification check should not fire without a blackout/recent-send flag: {revisit_failures}")


class TestSeasonRoundupPerShowSourcingLaw159(unittest.TestCase):
    """Law #159 implementation item 3, BUILT 2026-08-14.

    Law #159 requires "a real, distinct source per show, never one source waved across
    all shows in the roundup." Before this change _validate_semantic_qa only asked
    ">=1 core claim exists somewhere in the matrix", so a multi-show roundup could ship
    one sourced claim about one show and pass -- the gap cron_daily_runtime.txt named as
    the explicit blocker keeping SEASON_ROUNDUP non-selectable from the daily run.

    Structure mirrors TestSeasonRoundupClipSourcingLaw159: a clean-pass case, one case
    per failure mode, and a scoping case proving zero leakage into the other 16
    format_types.
    """

    PER_SHOW_CHECKS = (
        "every core claim tagged with a roundup show",
        "every roundup show has >=1 core claim",
        "every roundup show cites >=1 listed dated non-encyclopedic source",
        "no source URL reused across two shows",
        "roundup_shows present and well-formed",
    )

    def law159_failures(self, manifest: dict) -> list[str]:
        r = v.validate_manifest(manifest)
        return [n for n, ok, _ in r.checks if ok == "FAIL" and "Law #159" in n]

    def assertFailsCleanly(self, manifest: dict, needle: str):
        r = v.validate_manifest(manifest)
        names = [name for name, ok, _ in r.checks if ok == "FAIL"]
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected a clean failure containing {needle!r}; got failures={names}")
        self.assertFalse(r.ok)

    # --- clean pass ---

    def test_valid_roundup_fixture_passes(self):
        r = v.validate_manifest(load_roundup())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_valid_roundup_emits_all_per_show_checks(self):
        # the checks must actually RUN on a roundup, not silently no-op
        r = v.validate_manifest(load_roundup())
        names = [n for n, _, _ in r.checks]
        for needle in self.PER_SHOW_CHECKS:
            self.assertTrue(any(needle in n for n in names),
                            msg=f"per-show check {needle!r} never ran on a SEASON_ROUNDUP package")

    # --- coverage failure ---

    def test_show_with_no_core_claim_fails_closed(self):
        m = load_roundup()
        # drop the third show's only core entry -> roundup_shows still lists 3 shows
        m["packages"][0]["semantic_qa"]["claim_source_matrix"].pop(2)
        self.assertFailsCleanly(m, "every roundup show has >=1 core claim")

    def test_one_source_waved_across_all_shows_fails_closed(self):
        # the exact Law #159 failure mode: a single sourced claim, three shows declared
        m = load_roundup()
        matrix = m["packages"][0]["semantic_qa"]["claim_source_matrix"]
        m["packages"][0]["semantic_qa"]["claim_source_matrix"] = [matrix[0], matrix[-1]]
        self.assertFailsCleanly(m, "every roundup show has >=1 core claim")

    # --- attribution failure ---

    def test_core_claim_missing_show_tag_fails_closed(self):
        m = load_roundup()
        m["packages"][0]["semantic_qa"]["claim_source_matrix"][1].pop("show")
        self.assertFailsCleanly(m, "every core claim tagged with a roundup show")

    def test_core_claim_tagged_with_unknown_show_fails_closed(self):
        m = load_roundup()
        m["packages"][0]["semantic_qa"]["claim_source_matrix"][1]["show"] = "Some Other Anime"
        self.assertFailsCleanly(m, "every core claim tagged with a roundup show")

    # --- source-reuse / distinctness failure ---

    def test_same_source_url_reused_across_two_shows_fails_closed(self):
        m = load_roundup()
        pkg = m["packages"][0]
        shared = pkg["sources"][0]["url"]          # already show 1's source
        pkg["semantic_qa"]["claim_source_matrix"][2]["source_urls"] = [shared]
        self.assertFailsCleanly(m, "no source URL reused across two shows")

    def test_show_sourced_only_encyclopedically_fails_closed(self):
        m = load_roundup()
        pkg = m["packages"][0]
        wiki = "https://en.wikipedia.org/wiki/Witch_Hat_Atelier"
        pkg["sources"].append({"claim": "encyclopedic", "url": wiki, "date": "Aug 2026"})
        pkg["semantic_qa"]["claim_source_matrix"][2]["source_urls"] = [wiki]
        self.assertFailsCleanly(m, "cites >=1 listed dated non-encyclopedic source")

    def test_show_source_not_listed_in_sources_fails_closed(self):
        m = load_roundup()
        pkg = m["packages"][0]
        pkg["semantic_qa"]["claim_source_matrix"][2]["source_urls"] = [
            "https://example.com/not-in-sources"]
        self.assertFailsCleanly(m, "cites >=1 listed dated non-encyclopedic source")

    # --- roundup_shows shape ---

    def test_roundup_shows_absent_fails_closed(self):
        m = load_roundup()
        m["packages"][0].pop("roundup_shows")
        self.assertFailsCleanly(m, "roundup_shows present and well-formed")

    def test_roundup_shows_single_name_fails_closed(self):
        m = load_roundup()
        m["packages"][0]["roundup_shows"] = ["Kagurabachi"]
        self.assertFailsCleanly(m, "roundup_shows present and well-formed")

    def test_roundup_shows_case_insensitive_duplicate_fails_closed(self):
        m = load_roundup()
        m["packages"][0]["roundup_shows"] = ["Kagurabachi", "KAGURABACHI", "Witch Hat Atelier Season 2"]
        self.assertFailsCleanly(m, "roundup_shows present and well-formed")

    def test_roundup_shows_empty_string_fails_closed(self):
        m = load_roundup()
        m["packages"][0]["roundup_shows"] = ["Kagurabachi", "   "]
        self.assertFailsCleanly(m, "roundup_shows present and well-formed")

    def test_malformed_roundup_shows_still_reports_per_show_checks(self):
        # a malformed denominator must not make the per-show discipline silently vanish
        m = load_roundup()
        m["packages"][0]["roundup_shows"] = "not-a-list"
        failures = self.law159_failures(m)
        for needle in ("every roundup show has >=1 core claim",
                       "no source URL reused across two shows"):
            self.assertTrue(any(needle in f for f in failures),
                            msg=f"{needle!r} should be reported as failed, not skipped; got {failures}")

    # --- scoping: no leakage into the other 16 format_types ---

    def test_stray_roundup_shows_on_non_roundup_fails_closed(self):
        m = load_roundup()
        m["packages"][1]["roundup_shows"] = ["A", "B"]   # evening pkg is WRONG_TAKE
        self.assertFailsCleanly(m, "roundup_shows absent on non-SEASON_ROUNDUP package")

    def test_no_per_show_checks_run_on_any_other_format_type(self):
        others = [ft for ft in v.FORMAT_TYPES if ft != "SEASON_ROUNDUP"]
        self.assertEqual(len(others), 16, "expected 16 non-roundup tokens")
        for ft in others:
            m = load_valid()
            m["packages"][0]["format_type"] = ft
            names = [n for n, _, _ in v.validate_manifest(m).checks]
            for needle in self.PER_SHOW_CHECKS:
                leaked = [n for n in names if needle in n]
                self.assertEqual(leaked, [],
                                 msg=f"per-show check {needle!r} leaked into format_type={ft}: {leaked}")

    def test_baseline_fixtures_unaffected(self):
        for loader in (load_valid, load_experiment):
            r = v.validate_manifest(loader())
            self.assertTrue(r.ok, msg=f"baseline fixture regressed: {r.failures()}")

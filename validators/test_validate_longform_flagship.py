#!/usr/bin/env python3
"""Tests for the long-form flagship validator (Law #146).

The valid fixture must PASS; targeted mutations must FAIL on a specific check. The
key separation guarantees: face-cam is allowed, Shorts loop/timing fields are
rejected, and the video cannot be classifiable as a Short. Stdlib unittest only.

LENGTH EXPECTATIONS WERE INVERTED 2026-08-15, not deleted. This file previously
asserted that 200s FAILED ("too short") and 3000s FAILED ("too long") against a fixed
480-720s band. Law #146 retired that band on 2026-07-26: a 16:9 video is long-form at
any length and no upper bound was reinstated. Both manifests are therefore CORRECT
under the current law, and the two tests now assert they pass. The tests were kept and
their expectations reversed rather than removed, so the change is visible in the diff
instead of looking like dropped coverage.

    python3 validators/test_validate_longform_flagship.py
    python3 -m unittest discover  (from inside the validators/ directory)
"""

from __future__ import annotations

import json
import os
import unittest

import validate_longform_flagship as v

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "valid_longform_flagship.json")


def load_valid() -> dict:
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def failed_names(m: dict) -> list[str]:
    return [name for name, ok, _ in v.validate_flagship(m).checks if not ok]


class TestValidFlagship(unittest.TestCase):
    def test_valid_fixture_passes(self):
        r = v.validate_flagship(load_valid())
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_face_cam_allowed(self):
        # face-cam TRUE must not be a failure for long-form (unlike Shorts)
        m = load_valid()
        m["face"] = True
        self.assertTrue(v.validate_flagship(m).ok)


class TestInvalidFlagship(unittest.TestCase):
    def assertFailsOn(self, m: dict, needle: str):
        names = failed_names(m)
        self.assertTrue(any(needle in n for n in names),
                        msg=f"expected failure containing {needle!r}; got {names}")
        self.assertFalse(v.validate_flagship(m).ok)

    def test_wrong_content_type(self):
        m = load_valid(); m["content_type"] = "short"
        self.assertFailsOn(m, "content_type is 'longform'")

    # --- EXPECTATION INVERTED 2026-08-15 (see module docstring). These two previously
    # asserted failure against the retired 480-720s band. Under Law #146's two-tier
    # rule both are valid 16:9 flagships, so they now assert PASS. Kept, not deleted.
    def test_duration_200s_now_passes_16x9(self):
        m = load_valid(); m["duration_sec"] = 200; m["aspect_ratio"] = "16:9"
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_duration_3000s_now_passes_no_ceiling(self):
        m = load_valid(); m["duration_sec"] = 3000; m["aspect_ratio"] = "16:9"
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_shorts_only_field_rejected(self):
        m = load_valid(); m["loop_line"] = "some final sentence"
        self.assertFailsOn(m, "no Shorts-only loop/timing fields")

    def test_capcut_field_rejected(self):
        m = load_valid(); m["capcut_target_sec"] = 30
        self.assertFailsOn(m, "no Shorts-only loop/timing fields")

    def test_too_few_chapters(self):
        m = load_valid(); m["chapters"] = m["chapters"][:2]
        self.assertFailsOn(m, "at least 3 chapters")

    def test_first_chapter_not_zero(self):
        m = load_valid(); m["chapters"][0]["start_sec"] = 10
        self.assertFailsOn(m, "first chapter starts at 0:00")

    def test_chapters_not_increasing(self):
        m = load_valid(); m["chapters"][2]["start_sec"] = m["chapters"][1]["start_sec"]
        self.assertFailsOn(m, "chapter start times strictly increase")

    def test_keyword_not_in_first_line(self):
        m = load_valid()
        m["description"] = "This opening line mentions nothing relevant.\nSecond line has frieren."
        self.assertFailsOn(m, "first description line contains a primary keyword")

    def test_keyword_substring_inside_unrelated_word_rejected(self):
        # Regression test: the keyword check used to be plain substring containment
        # (`k in first_line`), so a short keyword like "one" would falsely match inside
        # an unrelated word like "someone". Word-boundary matching must reject this.
        m = load_valid()
        m["primary_keywords"] = ["one"]
        m["description"] = "Someone recorded this entire arc from memory.\nSecond line has one."
        self.assertFailsOn(m, "first description line contains a primary keyword")

    def test_keyword_whole_word_match_passes(self):
        # Companion positive case: the same short keyword must still pass when it
        # genuinely appears as its own word in the first line.
        m = load_valid()
        m["primary_keywords"] = ["one"]
        m["description"] = "This one detail changes the entire arc.\nMore context follows here."
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_too_many_keywords(self):
        m = load_valid(); m["primary_keywords"] = ["a", "b", "c"]
        self.assertFailsOn(m, "1-2 primary_keywords declared")

    def test_missing_playlist_link(self):
        m = load_valid(); m["playlist_link"] = ""
        self.assertFailsOn(m, "playlist_link present")

    def test_missing_pinned_next_link(self):
        m = load_valid(); m.pop("pinned_next_link", None)
        self.assertFailsOn(m, "pinned_next_link present")

    def test_missing_comment_prompt(self):
        m = load_valid(); m["comment_prompt"] = "no question here"
        self.assertFailsOn(m, "explicit comment_prompt question present")

    def test_teasers_without_flagship_url(self):
        m = load_valid(); m.pop("flagship_url", None)
        self.assertFailsOn(m, "teasers planned only after flagship_url exists")

    def test_teaser_count_out_of_band(self):
        m = load_valid(); m["teaser_shorts_planned"] = 9
        self.assertFailsOn(m, "teaser count within")

    def test_teaser_count_above_m5_cap(self):
        # M5: 5 teasers used to be allowed; the cap is now <=3
        m = load_valid(); m["teaser_shorts_planned"] = 5
        self.assertFailsOn(m, "teaser count within")

    def test_teaser_count_at_m5_cap_ok(self):
        m = load_valid(); m["teaser_shorts_planned"] = 3
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_zero_teasers_needs_no_flagship_url(self):
        m = load_valid(); m["teaser_shorts_planned"] = 0; m.pop("flagship_url", None)
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_bad_model_rejected(self):
        m = load_valid(); m["model"] = "gpt-4"
        self.assertFailsOn(m, "model is Sonnet 5.0 or Fable 5")

    def test_wrong_recipient(self):
        # Audit item #21 (2026-08-14): was a real personal address committed to the repo.
        # Any non-hero_or_villain@outlook.com value exercises this check identically.
        m = load_valid(); m["recipient"] = "wrong@example.com"
        self.assertFailsOn(m, "recipient is exactly correct")

    def test_non_dict_chapter_entry_fails_cleanly(self):
        m = load_valid()
        m["chapters"] = m["chapters"][:2] + ["not a dict"]
        r = v.validate_flagship(m)
        self.assertFalse(r.ok)
        names = [n for n, ok, _ in r.checks if not ok]
        self.assertTrue(any("at least 3 chapters" in n for n in names),
                        msg=f"expected a clean failure; got failures={names}")


class TestLengthRuleLaw146(unittest.TestCase):
    """Law #146 two-tier length rule: floor by FORMAT, target advisory, no ceiling.

    Added 2026-08-15 alongside the removal of the hard 480-720s band.
    """

    # --- FLOOR: 16:9 is long-form at any length -------------------------------
    def test_16x9_short_duration_clears_floor(self):
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 200
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_16x9_very_long_duration_has_no_ceiling(self):
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 3000
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_16x9_at_target_passes(self):
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 600
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    # --- FLOOR: vertical/square ARE Shorts at or below 3:00 -------------------
    def test_vertical_below_short_ceiling_fails_floor(self):
        m = load_valid(); m["aspect_ratio"] = "9:16"; m["duration_sec"] = 120
        names = failed_names(m)
        self.assertTrue(any("Short-classification floor" in n for n in names),
                        msg=f"expected floor failure; got {names}")
        self.assertFalse(v.validate_flagship(m).ok)

    def test_square_below_short_ceiling_fails_floor(self):
        m = load_valid(); m["aspect_ratio"] = "1:1"; m["duration_sec"] = 90
        names = failed_names(m)
        self.assertTrue(any("Short-classification floor" in n for n in names),
                        msg=f"expected floor failure; got {names}")

    def test_vertical_above_short_ceiling_clears_floor(self):
        m = load_valid(); m["aspect_ratio"] = "9:16"; m["duration_sec"] = 300
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"unexpected failures: {r.failures()}")

    def test_vertical_exactly_at_short_ceiling_fails(self):
        # 180s is still a Short ("up to 3:00"); the floor requires exceeding it.
        m = load_valid(); m["aspect_ratio"] = "9:16"; m["duration_sec"] = 180
        self.assertFalse(v.validate_flagship(m).ok)

    # --- FAIL-CLOSED on missing/invalid inputs --------------------------------
    def test_missing_aspect_ratio_fails_closed(self):
        m = load_valid(); m.pop("aspect_ratio", None)
        names = failed_names(m)
        self.assertTrue(any("aspect_ratio present" in n for n in names),
                        msg=f"expected aspect_ratio failure; got {names}")
        # the floor must ALSO fail rather than silently skip
        self.assertTrue(any("Short-classification floor" in n for n in names),
                        msg=f"floor must fail closed when unevaluatable; got {names}")

    def test_invalid_aspect_ratio_fails_closed(self):
        m = load_valid(); m["aspect_ratio"] = "4:3"
        names = failed_names(m)
        self.assertTrue(any("aspect_ratio present" in n for n in names),
                        msg=f"expected aspect_ratio failure; got {names}")

    def test_non_numeric_duration_fails_closed(self):
        m = load_valid(); m["duration_sec"] = "600"
        names = failed_names(m)
        self.assertTrue(any("positive number" in n for n in names),
                        msg=f"expected duration failure; got {names}")
        self.assertTrue(any("Short-classification floor" in n for n in names),
                        msg=f"floor must fail closed when unevaluatable; got {names}")

    # --- TARGET is advisory, never a gate -------------------------------------
    def test_below_target_emits_advisory_but_still_passes(self):
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 300
        r = v.validate_flagship(m)
        self.assertTrue(r.ok, msg=f"advisory must not block; failures={r.failures()}")
        self.assertTrue(r.advisories, "expected an advisory below the 8:00 target")
        self.assertIn("mid-roll", r.advisories[0])

    def test_at_or_above_target_emits_no_advisory(self):
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 600
        r = v.validate_flagship(m)
        self.assertEqual(r.advisories, [])

    def test_advisory_never_counted_as_a_check(self):
        # An advisory must not appear in checks[] -- it would print as [PASS]/[FAIL]
        # for something that was never gated.
        m = load_valid(); m["aspect_ratio"] = "16:9"; m["duration_sec"] = 300
        r = v.validate_flagship(m)
        self.assertTrue(all("mid-roll" not in name for name, _, _ in r.checks))

    def test_failing_manifest_emits_no_advisories(self):
        # 120s would normally trigger the below-target advisory, but this manifest is
        # BLOCKED on the Short-classification floor. A blocked package must show its
        # failure cleanly, without an ad-revenue note attached to a video that can't ship.
        m = load_valid(); m["aspect_ratio"] = "9:16"; m["duration_sec"] = 120
        r = v.validate_flagship(m)
        self.assertFalse(r.ok, "fixture setup wrong: this manifest should be blocked")
        self.assertEqual(r.advisories, [],
                         msg=f"blocked manifest must emit no advisories; got {r.advisories}")
        self.assertNotIn("ADVISORY", v.format_report(r))

    def test_retired_band_constants_are_gone(self):
        # Guards against anything reintroducing a hard band later.
        self.assertFalse(hasattr(v, "LONGFORM_MIN_SEC"))
        self.assertFalse(hasattr(v, "LONGFORM_MAX_SEC"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

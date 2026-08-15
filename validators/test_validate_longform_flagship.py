#!/usr/bin/env python3
"""Tests for the long-form flagship validator (Law #146).

The valid fixture must PASS; targeted mutations must FAIL on a specific check. The
key separation guarantees: face-cam is allowed, Shorts loop/timing fields are
rejected, and the 8-12 min band is enforced. Stdlib unittest only.

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

    def test_duration_too_short(self):
        m = load_valid(); m["duration_sec"] = 200
        self.assertFailsOn(m, "min band")

    def test_duration_too_long(self):
        m = load_valid(); m["duration_sec"] = 3000
        self.assertFailsOn(m, "min band")

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

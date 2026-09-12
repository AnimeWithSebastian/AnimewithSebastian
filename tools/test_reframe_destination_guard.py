from __future__ import annotations

import os
import unittest

import reframe_destination_guard as rdg

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_PATH = os.path.join(REPO_ROOT, "cron_daily_runtime.txt")


class TestUnconditionalPairings(unittest.TestCase):
    """Every destination transcribed with condition=None must return PASS,
    never PASS_WITH_CONDITION."""

    def test_episode_moment_to_character_dive_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("EPISODE_MOMENT", "CHARACTER_DIVE")
        self.assertEqual(result.outcome, "PASS")

    def test_the_moment_to_commentary_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("THE_MOMENT", "COMMENTARY")
        self.assertEqual(result.outcome, "PASS")

    def test_villain_defense_to_wrong_take_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("VILLAIN_DEFENSE", "WRONG_TAKE")
        self.assertEqual(result.outcome, "PASS")

    def test_origin_story_to_wrong_take_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("ORIGIN_STORY", "WRONG_TAKE")
        self.assertEqual(result.outcome, "PASS")

    def test_season_rating_to_watch_rank_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("SEASON_RATING", "WATCH_RANK")
        self.assertEqual(result.outcome, "PASS")

    def test_season_roundup_to_worth_watching_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("SEASON_ROUNDUP", "WORTH_WATCHING")
        self.assertEqual(result.outcome, "PASS")

    def test_theory_speculation_to_commentary_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("THEORY_SPECULATION", "COMMENTARY")
        self.assertEqual(result.outcome, "PASS")

    def test_theory_speculation_to_character_dive_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("THEORY_SPECULATION", "CHARACTER_DIVE")
        self.assertEqual(result.outcome, "PASS")

    def test_watch_rank_to_worth_watching_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("WATCH_RANK", "WORTH_WATCHING")
        self.assertEqual(result.outcome, "PASS")

    def test_character_dive_to_origin_story_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("CHARACTER_DIVE", "ORIGIN_STORY")
        self.assertEqual(result.outcome, "PASS")


class TestConditionalPairings(unittest.TestCase):
    """The two real judgment-call cases: PASS_WITH_CONDITION, never a
    hard FAIL, with the condition text surfaced in detail."""

    def test_watch_rank_to_season_roundup_passes_with_condition(self):
        result = rdg.guard_reframe_pairing("WATCH_RANK", "SEASON_ROUNDUP")
        self.assertEqual(result.outcome, "PASS_WITH_CONDITION")
        self.assertIn("per-candidate check at draft time", result.detail)
        self.assertIn("Law #165", result.detail)

    def test_character_dive_to_villain_defense_passes_with_condition(self):
        result = rdg.guard_reframe_pairing("CHARACTER_DIVE", "VILLAIN_DEFENSE")
        self.assertEqual(result.outcome, "PASS_WITH_CONDITION")
        self.assertIn("genuinely disliked", result.detail)
        self.assertIn("Law #165", result.detail)


class TestWorthWatchingHardFail(unittest.TestCase):
    """WORTH_WATCHING's empty destination list is the one genuine
    categorical FAIL -- there is no destination at all, conditional or
    otherwise, so this must never be PASS_WITH_CONDITION."""

    def test_worth_watching_any_destination_fails(self):
        result = rdg.guard_reframe_pairing("WORTH_WATCHING", "SLEPT_ON")
        self.assertEqual(result.outcome, "FAIL")
        self.assertIn("NO valid reframe destination", result.detail)

    def test_worth_watching_hidden_gem_fails(self):
        result = rdg.guard_reframe_pairing("WORTH_WATCHING", "HIDDEN_GEM")
        self.assertEqual(result.outcome, "FAIL")


class TestNotInAllowedSet(unittest.TestCase):
    """A pairing not transcribed under an existing key is a real FAIL,
    distinct from WORTH_WATCHING's empty-list FAIL -- message must name
    the allowed set instead."""

    def test_episode_moment_to_unrelated_format_fails(self):
        result = rdg.guard_reframe_pairing("EPISODE_MOMENT", "WATCH_RANK")
        self.assertEqual(result.outcome, "FAIL")
        self.assertIn("not in the allowed reframe set", result.detail)
        self.assertIn("CHARACTER_DIVE", result.detail)


class TestUntranscribedSourceRaises(unittest.TestCase):
    """A format_type not present as a REFRAME_MAP key at all is a gap in
    the hand transcription, not a real 'no destination exists' finding --
    must raise loudly, never silently equated with WORTH_WATCHING."""

    def test_untranscribed_key_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            rdg.guard_reframe_pairing("NOT_A_REAL_FORMAT_TOKEN", "COMMENTARY")
        self.assertIn("gap in the hand transcription", str(ctx.exception))


class TestV71LogPrefix(unittest.TestCase):
    """V-71: reframe rejection_reason must carry the required
    machine-distinguishable prefix. Plain string check -- only PASS/FAIL,
    never PASS_WITH_CONDITION."""

    def test_cooldown_reframe_prefix_passes(self):
        result = rdg.check_reframe_log_prefix(
            "cooldown_reframe: EPISODE_MOMENT on cooldown, reframed to CHARACTER_DIVE"
        )
        self.assertEqual(result.outcome, "PASS")

    def test_blackout_reframe_prefix_passes(self):
        result = rdg.check_reframe_log_prefix(
            "blackout_reframe: SEASON_RATING hard-blacked-out for this show, reframed to WATCH_RANK"
        )
        self.assertEqual(result.outcome, "PASS")

    def test_missing_prefix_fails(self):
        result = rdg.check_reframe_log_prefix(
            "EPISODE_MOMENT was on cooldown so we picked CHARACTER_DIVE instead"
        )
        self.assertEqual(result.outcome, "FAIL")
        self.assertIn("does not start with", result.detail)

    def test_wrong_prefix_fails(self):
        result = rdg.check_reframe_log_prefix(
            "reframe due to cooldown: EPISODE_MOMENT unavailable"
        )
        self.assertEqual(result.outcome, "FAIL")

    def test_none_rejection_reason_fails(self):
        result = rdg.check_reframe_log_prefix(None)
        self.assertEqual(result.outcome, "FAIL")
        self.assertIn("missing entirely", result.detail)

    def test_prefix_check_never_returns_pass_with_condition(self):
        for reason in (
            None,
            "cooldown_reframe: x",
            "blackout_reframe: x",
            "no prefix here",
        ):
            result = rdg.check_reframe_log_prefix(reason)
            self.assertIn(result.outcome, ("PASS", "FAIL"))


class TestResultEqualityAndValidation(unittest.TestCase):
    def test_invalid_outcome_raises(self):
        with self.assertRaises(ValueError):
            rdg.ReframeGuardResult("MAYBE", "detail")

    def test_equal_results_compare_equal(self):
        a = rdg.ReframeGuardResult("PASS", "same detail")
        b = rdg.ReframeGuardResult("PASS", "same detail")
        self.assertEqual(a, b)

    def test_different_outcome_not_equal(self):
        a = rdg.ReframeGuardResult("PASS", "same detail")
        b = rdg.ReframeGuardResult("FAIL", "same detail")
        self.assertNotEqual(a, b)


class TestMapStaysInSyncWithProse(unittest.TestCase):
    """REFRAME_MAP is a hand transcription of cron_daily_runtime.txt's
    REFRAME MAPPING prose, done once by a human. This test cannot verify
    the transcription is semantically correct (that requires a human
    re-reading both sides), but it CAN catch the cheapest, most likely
    drift: a source format_type being renamed or removed from the prose
    while this dict still references the old name. Every key in
    REFRAME_MAP must appear in cron_daily_runtime.txt attached to a
    "-> reframe" arrow, or this test fails loudly."""

    @classmethod
    def setUpClass(cls):
        with open(RUNTIME_PATH, encoding="utf-8") as fh:
            cls.runtime_text = fh.read()

    def test_every_map_key_appears_as_a_reframe_source_in_the_prose(self):
        missing = []
        for source_format in rdg.REFRAME_MAP:
            # The prose pattern is "<TOKEN>[ / <TOKEN2>] on cooldown ->
            # reframe as". Check for the token immediately followed
            # (allowing the alternate-token slash form) by "on cooldown".
            needle_a = f"{source_format} on cooldown"
            needle_b = f"{source_format} on cooldown ->"
            needle_slash_prefix = f"{source_format} /"
            needle_slash_suffix = f"/ {source_format}"
            if not any(
                needle in self.runtime_text
                for needle in (needle_a, needle_b, needle_slash_prefix, needle_slash_suffix)
            ):
                missing.append(source_format)
        self.assertEqual(
            missing,
            [],
            f"REFRAME_MAP key(s) {missing} no longer appear as a reframe "
            f"source in cron_daily_runtime.txt's REFRAME MAPPING prose -- "
            f"the prose may have renamed or removed this pairing. Re-read "
            f"the REFRAME MAPPING section (search 'REFRAME MAPPING —') and "
            f"update tools/reframe_destination_guard.py's REFRAME_MAP to "
            f"match before trusting this module again.",
        )

    def test_worth_watching_dropped_language_still_present(self):
        # Confirms the specific "checked and rejected" language this
        # module's WORTH_WATCHING FAIL messaging depends on has not been
        # silently softened or removed from the prose.
        self.assertIn("DROPPED, CHECKED AND REJECTED", self.runtime_text)
        self.assertIn("No reframe destination exists for WORTH_WATCHING", self.runtime_text)


if __name__ == "__main__":
    unittest.main()

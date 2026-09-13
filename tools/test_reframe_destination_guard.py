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

    def test_fact_drop_to_commentary_passes_unconditionally(self):
        result = rdg.guard_reframe_pairing("FACT_DROP", "COMMENTARY")
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

    def test_fact_drop_to_wrong_take_passes_with_condition(self):
        # FIX 1 (2026-09-12, F86 closure): FACT_DROP's lore-explainer half
        # may reframe to WRONG_TAKE, but only when the fact corrects a real
        # community myth -- not every FACT_DROP fact has one, same
        # conditional shape as CHARACTER_DIVE -> VILLAIN_DEFENSE above.
        result = rdg.guard_reframe_pairing("FACT_DROP", "WRONG_TAKE")
        self.assertEqual(result.outcome, "PASS_WITH_CONDITION")
        self.assertIn("real, existing community myth", result.detail)
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

    def test_fact_drop_appears_as_a_reframe_source_in_the_prose(self):
        # Direct regression pin for FIX 1: FACT_DROP was previously ABSENT
        # from REFRAME_MAP entirely (F86) -- this confirms the added prose
        # bullet uses the exact "FACT_DROP on cooldown ->" pattern the sync
        # test above already checks generically for every key.
        self.assertIn("FACT_DROP on cooldown ->", self.runtime_text)

    def test_worth_watching_dropped_language_still_present(self):
        # Confirms the specific "checked and rejected" language this
        # module's WORTH_WATCHING FAIL messaging depends on has not been
        # silently softened or removed from the prose.
        self.assertIn("DROPPED, CHECKED AND REJECTED", self.runtime_text)
        self.assertIn("No reframe destination exists for WORTH_WATCHING", self.runtime_text)


class TestReframeCitationAnchorsResolve(unittest.TestCase):
    """F89 (2026-09-12): every citation into cron_daily_runtime.txt in
    reframe_destination_guard.py used to be a line number, and had already
    drifted -- the file gets edited and nothing checked whether the cited
    ranges still resolved to the described content. rdg.REFRAME_CITATION_
    ANCHORS now holds a short, verbatim quoted fragment per citation
    instead. This test cannot verify an anchor is still SEMANTICALLY
    correct (that requires a human re-reading both sides, same limitation
    as TestMapStaysInSyncWithProse above), but it CAN catch the cheapest,
    most likely drift: the cited passage being renamed, reworded, or
    removed while the guard module still quotes the old text. Every
    anchor string must appear verbatim in cron_daily_runtime.txt, or this
    test fails loudly naming exactly which anchor broke."""

    @classmethod
    def setUpClass(cls):
        with open(RUNTIME_PATH, encoding="utf-8") as fh:
            cls.runtime_text = fh.read()

    def test_every_anchor_resolves_in_the_runtime_file(self):
        missing = [
            anchor_id
            for anchor_id, anchor_text in rdg.REFRAME_CITATION_ANCHORS.items()
            if anchor_text not in self.runtime_text
        ]
        self.assertEqual(
            missing,
            [],
            f"REFRAME_CITATION_ANCHORS id(s) {missing} no longer appear "
            f"verbatim in cron_daily_runtime.txt -- the cited passage was "
            f"likely reworded, moved, or removed. Re-read the REFRAME "
            f"MAPPING section (search 'REFRAME MAPPING \u2014') and update "
            f"both the anchor string in reframe_destination_guard.py's "
            f"REFRAME_CITATION_ANCHORS and whatever claim that citation "
            f"was supporting before trusting this module again.",
        )

    def test_anchor_dict_has_no_duplicate_ids_or_empty_strings(self):
        # Cheap sanity check on the anchor dict itself -- an accidentally
        # duplicated key silently overwrites the earlier entry (Python dict
        # literals don't error on this), and an empty string trivially
        # "matches" everywhere, defeating the whole point of an anchor.
        for anchor_id, anchor_text in rdg.REFRAME_CITATION_ANCHORS.items():
            self.assertTrue(
                anchor_text.strip(),
                f"anchor {anchor_id!r} is empty or whitespace-only",
            )

    def test_every_anchor_is_unique_in_the_runtime_file(self):
        # F89 (2026-09-12): presence alone (test above) is not enough. An
        # anchor that is only INCIDENTALLY unique today -- a short fragment
        # that happens not to occur twice, rather than a clause distinctive
        # enough that it structurally couldn't -- can start silently
        # matching a second, unrelated passage after some unrelated edit,
        # at which point the citation is no longer reliably pointing at the
        # passage it was meant to. Assert count == 1, not merely >= 1, and
        # name every anchor that fails so a human knows exactly what
        # drifted into ambiguity instead of having to re-diff the whole file.
        non_unique = {
            anchor_id: self.runtime_text.count(anchor_text)
            for anchor_id, anchor_text in rdg.REFRAME_CITATION_ANCHORS.items()
            if self.runtime_text.count(anchor_text) != 1
        }
        self.assertEqual(
            non_unique,
            {},
            f"REFRAME_CITATION_ANCHORS entries with an occurrence count "
            f"other than 1 in cron_daily_runtime.txt: {non_unique} "
            f"(anchor_id -> occurrence count). A count of 0 means the "
            f"anchor is missing (see the resolves-in-the-runtime-file test "
            f"above); a count >= 2 means the anchor text now matches more "
            f"than one passage and can no longer reliably identify which "
            f"one this citation means -- reword the anchor to a clause "
            f"distinctive enough that it can't collide, not just one that "
            f"happens not to today.",
        )


if __name__ == "__main__":
    unittest.main()

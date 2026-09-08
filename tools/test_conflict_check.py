#!/usr/bin/env python3
"""Adversarial tests for tools/conflict_check.py (item #3+#8, recurring-
failure-patterns audit, 2026-08-18).

Uses stdlib unittest only, against an in-memory history list (no filesystem
writes needed except for the one test that exercises _load_send_history's
real-file path).

    python3 tools/test_conflict_check.py
"""

from __future__ import annotations

import difflib
import json
import os
import tempfile
import unittest

import conflict_check as c


def pkg(**kw):
    base = {"show": "One Piece", "format_type": "THE_MOMENT",
            "angle": "generic angle", "post_date": "2026-08-20"}
    base.update(kw)
    return base


def sent(**kw):
    base = {"batch_id": "hist-batch", "show": "One Piece",
            "format_type": "THE_MOMENT", "angle": "generic angle",
            "date_sent": "2026-08-15T00:00:00Z"}
    base.update(kw)
    return base


class TestDifferentShow(unittest.TestCase):
    def test_different_show_entirely_no_flag(self):
        history = [sent(show="Bleach", angle="Ichigo unlocks a new form")]
        result = c.check_recent_send_conflict(
            pkg(show="One Piece", angle="Luffy unlocks a new form"),
            tree="unused", history=history)
        self.assertFalse(result["blocked"])


class TestRealF43Gabon(unittest.TestCase):
    """Reconstructed verbatim from docs/KNOWN_ISSUES.md F43 (both the
    original 6818490a near-miss and its second occurrence in f54413d8)."""

    def test_real_gaban_near_miss_blocks_despite_false_attestation(self):
        history = [sent(
            batch_id="6818490a", show="One Piece", format_type="THE_MOMENT",
            angle="Chapter 1190: Scopper Gaban lands the first confirmed "
                  "injury on Imu in the entire series, then loses his arm for it",
            date_sent="2026-08-08T00:00:00Z",
        )]
        candidate = pkg(
            show="One Piece", format_type="THE_MOMENT",
            angle="Gaban sacrifices his arm to save Luffy from Imu in "
                  "Ch.1190 -- fate left unconfirmed",
            post_date="2026-08-14",  # six days later, matching the real incident
            recent_send_conflict=False,  # the real false attestation
        )
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"],
                         "must block the real Gaban near-miss even though the "
                         "package itself attests recent_send_conflict=False")
        self.assertEqual(result["matched_batch_id"], "6818490a")

    def test_real_gaban_repeat_still_blocks_outside_date_window_via_angle_signal(self):
        # THE_MOMENT has no format-specific window -> generic 7-day fallback.
        # KNOWN_ISSUES.md's own "one honest caveat" says a date window alone
        # would NOT catch this on day 8+ -- confirm the angle-similarity
        # signal (precedence 3) still catches it independent of date.
        history = [sent(
            batch_id="6818490a", show="One Piece", format_type="THE_MOMENT",
            angle="Chapter 1190: Scopper Gaban lands the first confirmed "
                  "injury on Imu in the entire series, then loses his arm for it",
            date_sent="2026-08-08T00:00:00Z",
        )]
        candidate = pkg(
            show="One Piece", format_type="THE_MOMENT",
            angle="Scopper Gaban lands the first confirmed injury on Imu, "
                  "then loses his arm for it",  # near-identical angle text
            post_date="2026-08-20",  # 12 days later -- outside the 7-day generic window
        )
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"],
                         "angle-similarity signal must fire even outside the date window")
        self.assertEqual(result["signal"], "angle_similarity")


class TestDateWindowBoundaries(unittest.TestCase):
    def test_outside_format_window_does_not_block(self):
        # SEASON_RATING = 7 days; 8 days later with a genuinely different angle.
        history = [sent(show="Frieren", format_type="SEASON_RATING",
                        angle="Frieren's pacing this season is a mistake",
                        date_sent="2026-08-01T00:00:00Z")]
        candidate = pkg(show="Frieren", format_type="SEASON_RATING",
                        angle="Frieren's new arc finally earns its slow pace",
                        post_date="2026-08-09")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_exactly_at_window_boundary_blocks(self):
        # 7-day window: post_date - date_sent == 6 days is inside [0,7).
        history = [sent(show="Frieren", format_type="SEASON_RATING",
                        date_sent="2026-08-01T00:00:00Z")]
        candidate = pkg(show="Frieren", format_type="SEASON_RATING",
                        angle="different but same-show", post_date="2026-08-07")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "date_window_blackout")

    def test_one_day_past_window_does_not_date_block(self):
        history = [sent(show="Frieren", format_type="SEASON_RATING",
                        angle="totally unrelated wording about pacing",
                        date_sent="2026-08-01T00:00:00Z")]
        candidate = pkg(show="Frieren", format_type="SEASON_RATING",
                        angle="a completely different opinion about animation quality",
                        post_date="2026-08-08")  # exactly 7 days later -> outside [0,7)
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_manga_vs_anime_14_day_window(self):
        history = [sent(show="Vinland Saga", format_type="MANGA_VS_ANIME",
                        date_sent="2026-08-01T00:00:00Z")]
        inside = pkg(show="Vinland Saga", format_type="MANGA_VS_ANIME",
                    angle="different scene", post_date="2026-08-13")  # 12 days
        outside = pkg(show="Vinland Saga", format_type="MANGA_VS_ANIME",
                     angle="different scene entirely, no overlap in wording",
                     post_date="2026-08-16")  # 15 days
        self.assertTrue(c.check_recent_send_conflict(inside, tree="unused", history=history)["blocked"])
        self.assertFalse(c.check_recent_send_conflict(outside, tree="unused", history=history)["blocked"])

    def test_episode_moment_has_no_date_blackout(self):
        # EPISODE_MOMENT = 0 -> date-window branch never fires, even same-day.
        history = [sent(show="Bleach", format_type="EPISODE_MOMENT",
                        angle="totally different beat, no wording overlap",
                        date_sent="2026-08-19T00:00:00Z")]
        candidate = pkg(show="Bleach", format_type="EPISODE_MOMENT",
                       angle="a completely unrelated moment from the same episode airing",
                       post_date="2026-08-19")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_undocumented_format_never_date_blocks_only_angle_can(self):
        # WRONG_TAKE has no documented window anywhere -> NO date-window
        # signal at all (corrected design). Same show, 5 days apart, but
        # angle text is genuinely different -> must NOT block.
        history = [sent(show="Solo Leveling", format_type="WRONG_TAKE",
                        angle="Sung Jinwoo's guild politics take is overrated",
                        date_sent="2026-08-01T00:00:00Z")]
        different_angle = pkg(show="Solo Leveling", format_type="WRONG_TAKE",
                              angle="The anime's pacing in episode 9 was a mistake",
                              post_date="2026-08-06")  # 5 days later
        result = c.check_recent_send_conflict(different_angle, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "undocumented formats must never block on date proximity alone")

    def test_undocumented_format_within_loose_window_high_similarity_blocks(self):
        # THE_MOMENT (undocumented), 85 days apart -- inside the 90-day loose
        # search window -- with genuinely high angle similarity -> blocks.
        history = [sent(show="Kagurabachi", format_type="THE_MOMENT",
                        angle="Chihiro's blade shatters mid-fight, forcing him "
                              "to improvise a new technique on the spot",
                        date_sent="2026-05-26T00:00:00Z")]
        candidate = pkg(show="Kagurabachi", format_type="THE_MOMENT",
                       angle="Chihiro's blade shatters mid fight, forcing him "
                             "to improvise a new technique on the spot",
                       post_date="2026-08-19")  # 85 days later
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "angle_similarity")

    def test_undocumented_format_within_loose_window_low_similarity_does_not_block(self):
        # Same setup, but genuinely different content -- must NOT block just
        # because a same-show candidate exists somewhere in the search window.
        history = [sent(show="Kagurabachi", format_type="THE_MOMENT",
                        angle="Chihiro's blade shatters mid-fight, forcing him "
                              "to improvise a new technique on the spot",
                        date_sent="2026-05-26T00:00:00Z")]
        candidate = pkg(show="Kagurabachi", format_type="THE_MOMENT",
                       angle="Kunishige refuses to break focus on the forge "
                             "even with a blade at his throat",
                       post_date="2026-08-19")  # 85 days later
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "existing in the search window must not itself block "
                          "-- only real similarity should")

    def test_undocumented_format_outside_loose_window_never_considered(self):
        # 95 days apart (outside the 90-day search window), even with
        # identical angle text -> not even considered, must not block.
        history = [sent(show="Kagurabachi", format_type="THE_MOMENT",
                        angle="Chihiro's blade shatters mid-fight",
                        date_sent="2026-05-16T00:00:00Z")]
        candidate = pkg(show="Kagurabachi", format_type="THE_MOMENT",
                       angle="Chihiro's blade shatters mid-fight",
                       post_date="2026-08-19")  # 95 days later
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "rows outside the loose search window must not be considered at all")


class TestAngleSimilaritySignal(unittest.TestCase):
    def test_low_similarity_same_show_does_not_block(self):
        history = [sent(show="Jujutsu Kaisen", format_type="THE_MOMENT",
                        angle="Gojo's domain expansion changes the fight forever",
                        date_sent="2026-06-01T00:00:00Z")]  # far outside any window
        candidate = pkg(show="Jujutsu Kaisen", format_type="THE_MOMENT",
                       angle="Yuji's resolve after losing a friend defines the arc",
                       post_date="2026-08-20")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_high_similarity_outside_window_still_blocks(self):
        history = [sent(show="Jujutsu Kaisen", format_type="THE_MOMENT",
                        angle="Gojo's domain expansion changes the fight forever",
                        date_sent="2026-06-01T00:00:00Z")]
        candidate = pkg(show="Jujutsu Kaisen", format_type="THE_MOMENT",
                       angle="Gojo's domain expansion changes this fight forever",
                       post_date="2026-08-20")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "angle_similarity")


class TestTheorySpeculationSameQuestion(unittest.TestCase):
    def test_same_question_no_justification_blocks(self):
        history = [sent(show="One Piece", format_type="THEORY_SPECULATION",
                        angle="unrelated angle text",
                        question_line="Is Imu actually a Void Century god?",
                        date_sent="2026-05-01T00:00:00Z")]  # far outside any date window
        candidate = pkg(show="One Piece", format_type="THEORY_SPECULATION",
                       angle="different phrasing entirely",
                       question_line="Is Imu actually a Void Century god?",
                       post_date="2026-08-20")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "theory_same_question")

    def test_same_question_with_well_formed_justification_does_not_block(self):
        history = [sent(show="One Piece", format_type="THEORY_SPECULATION",
                        question_line="Is Imu actually a Void Century god?",
                        date_sent="2026-05-01T00:00:00Z")]
        candidate = pkg(show="One Piece", format_type="THEORY_SPECULATION",
                       angle="different phrasing", post_date="2026-08-20",
                       question_line="Is Imu actually a Void Century god?",
                       revisit_justification={
                           "new_evidence_summary": "Chapter 1190 confirms Imu's age range",
                           "new_evidence_source_url": "https://example.com/ch1190",
                           "new_evidence_date": "2026-08-15",
                       })
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_same_question_with_malformed_justification_still_blocks(self):
        history = [sent(show="One Piece", format_type="THEORY_SPECULATION",
                        question_line="Is Imu actually a Void Century god?",
                        date_sent="2026-05-01T00:00:00Z")]
        # missing new_evidence_source_url -> not well-formed
        candidate = pkg(show="One Piece", format_type="THEORY_SPECULATION",
                       angle="different phrasing", post_date="2026-08-20",
                       question_line="Is Imu actually a Void Century god?",
                       revisit_justification={
                           "new_evidence_summary": "some summary",
                           "new_evidence_date": "2026-08-15",
                       })
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])

    def test_different_question_same_show_does_not_theory_block(self):
        history = [sent(show="One Piece", format_type="THEORY_SPECULATION",
                        angle="totally unrelated wording, no overlap at all here",
                        question_line="Is Imu actually a Void Century god?",
                        date_sent="2026-05-01T00:00:00Z")]
        candidate = pkg(show="One Piece", format_type="THEORY_SPECULATION",
                       angle="a completely separate theory about Zunesha's past",
                       post_date="2026-08-20",
                       question_line="Is Zunesha secretly a Void Century survivor?")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])


class TestEdgeCasesAndRobustness(unittest.TestCase):
    def test_empty_history_first_ever_run_no_false_positive(self):
        result = c.check_recent_send_conflict(pkg(), tree="unused", history=[])
        self.assertFalse(result["blocked"])

    def test_missing_show_field_does_not_crash(self):
        result = c.check_recent_send_conflict({"angle": "x"}, tree="unused", history=[sent()])
        self.assertFalse(result["blocked"])

    def test_missing_angle_field_does_not_crash(self):
        history = [sent(show="One Piece", date_sent="2026-01-01T00:00:00Z")]
        result = c.check_recent_send_conflict(
            {"show": "One Piece", "format_type": "THE_MOMENT", "post_date": "2026-08-20"},
            tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_missing_post_date_skips_date_window_but_angle_signal_still_runs(self):
        history = [sent(show="One Piece", format_type="THE_MOMENT",
                        angle="Gaban loses his arm protecting Luffy from Imu",
                        date_sent="2026-01-01T00:00:00Z")]
        candidate = {"show": "One Piece", "format_type": "THE_MOMENT",
                    "angle": "Gaban loses his arm protecting Luffy from Imu"}
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "angle_similarity")

    def test_malformed_history_row_is_skipped_not_crashed_on(self):
        history = [{"show": None, "angle": 12345}, sent(show="Naruto",
                   angle="totally different", date_sent="2026-01-01T00:00:00Z")]
        result = c.check_recent_send_conflict(
            pkg(show="Naruto", angle="a completely unrelated fresh angle here"),
            tree="unused", history=history)
        self.assertFalse(result["blocked"])

    def test_case_insensitive_show_match(self):
        # Isolates case-insensitivity specifically: show names differ only
        # in case, angles are near-identical (so angle-similarity, not a
        # date floor, is what should fire -- THE_MOMENT has no documented
        # window post-correction).
        history = [sent(show="one piece", format_type="THE_MOMENT",
                        angle="Gaban loses his arm fighting Imu in chapter 1190",
                        date_sent="2026-08-15T00:00:00Z")]
        candidate = pkg(show="ONE PIECE", format_type="THE_MOMENT",
                       angle="Gaban loses his arm fighting Imu in chapter 1190",
                       post_date="2026-08-16")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"],
                         "case-different show names must still be matched as the same show")


class TestSharedEntitySignal(unittest.TestCase):
    """Six required adversarial tests for the THIRD DESIGN CORRECTION
    (shared-entity signal added alongside angle-similarity after the
    corrected fallback design was shown to miss the real F43 Gaban case)."""

    def test_1_real_gaban_case_entity_signal_catches_what_similarity_missed(self):
        # The two REAL angle strings from F43 score only 0.26 on
        # difflib.SequenceMatcher (confirmed below) -- well under the 0.6
        # threshold -- so angle-similarity alone would NOT catch this. The
        # shared-entity signal (same character "Imu"/"Gaban" + same chapter
        # number 1190) must catch it independently.
        original = ("Chapter 1190: Scopper Gaban lands the first confirmed "
                     "injury on Imu in the entire series, then loses his arm for it")
        near_dup = ("Gaban sacrifices his arm to save Luffy from Imu in "
                     "Ch.1190 -- fate left unconfirmed")
        ratio = difflib.SequenceMatcher(None, original.lower(), near_dup.lower()).ratio()
        self.assertLess(ratio, c.ANGLE_SIMILARITY_THRESHOLD,
                         "sanity check: confirms these two real strings really "
                         "do score below threshold, so this test is meaningful")

        history = [sent(batch_id="6818490a-f6fd-4647-95a7-f6a723d3b166",
                        show="One Piece", format_type="THE_MOMENT",
                        angle=original, date_sent="2026-08-08T00:00:00Z")]
        candidate = pkg(show="One Piece", format_type="THE_MOMENT",
                       angle=near_dup, post_date="2026-08-14")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "shared_entity")

    def test_2_different_episodes_same_show_does_not_fire_entity_signal(self):
        # Real prior near-miss risk this design must avoid re-introducing:
        # same show, different episodes/chapters within days -- Mushoku
        # Tensei COMMENTARY (marriage backlash) vs CHARACTER_DIVE (Sara
        # apology), 5 real days apart, no shared chapter/episode number.
        history = [sent(show="Mushoku Tensei: Jobless Reincarnation Season 3",
                        format_type="COMMENTARY",
                        angle="The 'PDF anime' review-bombing backlash after "
                              "Rudeus marries Roxy -- deserved reckoning or not",
                        date_sent="2026-07-31T00:00:00Z")]
        candidate = pkg(show="Mushoku Tensei: Jobless Reincarnation Season 3",
                       format_type="CHARACTER_DIVE",
                       angle="Rudeus finally apologizes to Sara and admits he "
                             "confused heartbreak for love -- while Eris earns "
                             "the Sword King title",
                       post_date="2026-08-05")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "shared show alone (no shared entity+number) must not fire")

    def test_3_shared_character_different_chapter_does_not_fire(self):
        # Same character mentioned, but genuinely different chapter numbers
        # -- must NOT fire on character overlap alone without the number match.
        history = [sent(show="One Piece", format_type="THE_MOMENT",
                        angle="Chapter 1150: Gaban first appears guarding the throne",
                        date_sent="2026-06-01T00:00:00Z")]
        candidate = pkg(show="One Piece", format_type="THE_MOMENT",
                       angle="Chapter 1190: Gaban loses his arm fighting Imu",
                       post_date="2026-08-19")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "shared character with a DIFFERENT chapter number must not fire")

    def test_4_number_format_variants_still_normalize_and_match(self):
        variants = ["Chapter 1190", "Ch.1190", "Ch 1190", "chapter 1190", "Ch. 1190"]
        for variant_a in variants:
            for variant_b in variants:
                angle_a = f"{variant_a}: Gaban loses his arm fighting Imu"
                angle_b = f"{variant_b} -- Gaban's arm is lost fighting Imu"
                with self.subTest(a=variant_a, b=variant_b):
                    self.assertTrue(c._shared_entity_signal(angle_a, angle_b),
                                     f"{variant_a!r} vs {variant_b!r} should normalize to the same number")

    def test_5_no_number_in_either_angle_falls_back_to_similarity_no_crash(self):
        # General character-focused angle with no specific numbered
        # reference in either string -- entity signal correctly does not
        # fire (no number to match), falls back to angle-similarity alone,
        # does not crash.
        history = [sent(show="One Piece", format_type="THE_MOMENT",
                        angle="Gaban's loyalty to the Celestial Dragons is "
                              "finally tested in a way nobody expected",
                        date_sent="2026-06-01T00:00:00Z")]
        candidate = pkg(show="One Piece", format_type="THE_MOMENT",
                       angle="Zoro's swordsmanship reaches a new level after "
                             "training with the strongest blade in Wano",
                       post_date="2026-08-19")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"])
        self.assertIsNone(result["signal"])

    def test_6_real_data_full_history_true_positive_and_no_new_false_positives(self):
        # Real data check: load the ACTUAL sent_scripts_events.jsonl and
        # confirm (a) the real Gaban near-miss is caught when replayed as a
        # candidate against real history, and (b) no unrelated real
        # historical row is falsely flagged as an entity-signal match against
        # a genuinely different show or an unrelated same-show entry.
        import os
        tree = os.path.join(os.path.dirname(__file__), "..")
        history = c._load_send_history(tree)
        self.assertGreater(len(history), 0, "real history file must be loadable")

        gaban_original = next(r for r in history if r.get("batch_id") ==
                              "6818490a-f6fd-4647-95a7-f6a723d3b166" and r.get("show") == "One Piece")
        candidate = pkg(show="One Piece", format_type="THE_MOMENT",
                       angle="Gaban sacrifices his arm to save Luffy from Imu "
                             "in Ch.1190 -- fate left unconfirmed",
                       post_date="2026-08-14")
        result = c.check_recent_send_conflict(candidate, tree=tree,
                                               history=[gaban_original])
        self.assertTrue(result["blocked"])
        self.assertEqual(result["signal"], "shared_entity")

        # No-new-false-positive check: every OTHER real historical row,
        # excluding rows that share both show AND (entity+number) with a
        # DIFFERENT real batch, should not fire the entity signal against
        # an unrelated fresh candidate for a different show entirely.
        fresh = pkg(show="Frieren: Beyond Journey's End", format_type="SEASON_RATING",
                   angle="Frieren season 2 finally slows down and it works",
                   post_date="2026-08-25")
        full_result = c.check_recent_send_conflict(fresh, tree=tree, history=history)
        self.assertFalse(full_result["blocked"],
                          "an unrelated show/angle must not be flagged against the full real ledger")


class TestBatchExclusion(unittest.TestCase):
    """Adversarial tests #8 and #9 requested after the real-data backtest:
    same-batch packages and real corrects_batch_id corrections must never
    false-positive against the batch/target they belong to, but a
    correction must still be checked normally against unrelated history.
    """

    def test_8_same_batch_same_show_does_not_flag_each_other(self):
        # Edge case: two packages in the CURRENT candidate's own batch,
        # same show. Shouldn't occur in practice (send-ledger comparison
        # runs against already-sent history, not sibling drafts), but the
        # exclusion must hold defensively if this function is ever reused
        # to compare drafts within the same batch before sending.
        history = [sent(batch_id="same-batch-id", show="One Piece",
                        format_type="THE_MOMENT",
                        angle="Sibling package in the same batch, same show",
                        date_sent="2026-08-19T00:00:00Z")]
        candidate = pkg(batch_id="same-batch-id", show="One Piece",
                       format_type="THE_MOMENT",
                       angle="Sibling package in the same batch, same show",
                       post_date="2026-08-19")
        result = c.check_recent_send_conflict(candidate, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "a package must never be flagged against its own batch_id")

    def test_9_real_correction_does_not_flag_against_its_own_target_batch(self):
        # Reconstructed verbatim from the real b03ef8b6 -> 32e0fcb9 Link Click
        # correction pair (cron_tracking/sent_scripts_events.jsonl): the
        # correction re-sends the same show/near-identical angle one day
        # later with corrects_batch_id set. Must NOT flag against that
        # specific target batch.
        history = [sent(
            batch_id="b03ef8b6-d254-442a-aaf9-673a6578a0c5", show="Link Click",
            format_type="SEASON_PREVIEW",
            angle="Season 3 Part One premieres August 14 on Crunchyroll as a "
                  "doubled-length 24-episode story, two months earlier than "
                  "announced, picking up the Bahati fire case and Xia Fei's "
                  "disappearance",
            date_sent="2026-08-13T22:40:00+00:00",
        )]
        correction = pkg(
            batch_id="32e0fcb9-440c-4b2e-8bd4-0c900390b3c1",
            corrects_batch_id="b03ef8b6-d254-442a-aaf9-673a6578a0c5",
            show="Link Click", format_type="SEASON_PREVIEW",
            angle="Season 3 Part One premieres August 14 on Crunchyroll as a "
                  "doubled-length 24-episode story, two months earlier than "
                  "announced, picking up the Bahati fire case and Xia Fei's "
                  "disappearance",  # near-identical angle -- this IS the correction
            post_date="2026-08-14",
        )
        result = c.check_recent_send_conflict(correction, tree="unused", history=history)
        self.assertFalse(result["blocked"],
                          "a correction must not be flagged against the exact "
                          "batch it is correcting")

    def test_9_real_correction_still_flags_against_unrelated_recent_send(self):
        # Same correction, but now there IS a genuinely unrelated recent
        # same-show send in history (not the one being corrected) with a
        # highly similar angle -- the correction must still be caught
        # normally against everything OTHER than its own correction target.
        history = [
            sent(batch_id="b03ef8b6-d254-442a-aaf9-673a6578a0c5", show="Link Click",
                format_type="SEASON_PREVIEW",
                angle="Season 3 Part One premieres August 14 on Crunchyroll as a "
                      "doubled-length 24-episode story, two months earlier than "
                      "announced, picking up the Bahati fire case and Xia Fei's "
                      "disappearance",
                date_sent="2026-08-13T22:40:00+00:00"),
            sent(batch_id="unrelated-other-batch", show="Link Click",
                format_type="SEASON_PREVIEW",
                angle="Season 3 Part One premieres August 14 on Crunchyroll as a "
                      "doubled length 24 episode story, two months earlier than "
                      "announced, picking up the Bahati fire case and Xia Fei "
                      "disappearance",  # near-duplicate of a DIFFERENT batch
                date_sent="2026-08-13T23:00:00+00:00"),
        ]
        correction = pkg(
            batch_id="32e0fcb9-440c-4b2e-8bd4-0c900390b3c1",
            corrects_batch_id="b03ef8b6-d254-442a-aaf9-673a6578a0c5",
            show="Link Click", format_type="SEASON_PREVIEW",
            angle="Season 3 Part One premieres August 14 on Crunchyroll as a "
                  "doubled-length 24-episode story, two months earlier than "
                  "announced, picking up the Bahati fire case and Xia Fei's "
                  "disappearance",
            post_date="2026-08-14",
        )
        result = c.check_recent_send_conflict(correction, tree="unused", history=history)
        self.assertTrue(result["blocked"],
                         "a correction must still be checked normally against "
                         "history OTHER than its own correction target")
        self.assertEqual(result["matched_batch_id"], "unrelated-other-batch")


class TestRealFileLoading(unittest.TestCase):
    """Exercises _load_send_history against a real temp file, including a
    malformed line, matching append_send_batch.py's WARN-and-continue
    convention for the same file."""

    def test_load_real_jsonl_file_with_one_bad_line(self):
        with tempfile.TemporaryDirectory() as tree:
            events_dir = os.path.join(tree, "cron_tracking")
            os.makedirs(events_dir)
            path = os.path.join(events_dir, "sent_scripts_events.jsonl")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(sent(show="Naruto")) + "\n")
                fh.write("{ not valid json\n")
                fh.write(json.dumps(sent(show="Bleach")) + "\n")
            rows = c._load_send_history(tree)
            self.assertEqual(len(rows), 2)
            self.assertEqual({r["show"] for r in rows}, {"Naruto", "Bleach"})

    def test_missing_file_returns_empty_no_crash(self):
        with tempfile.TemporaryDirectory() as tree:
            self.assertEqual(c._load_send_history(tree), [])


class TestRealProductionDataSnapshot(unittest.TestCase):
    """The two real rows currently in sent_scripts_events.jsonl (batch
    8ca83216, Mushoku Tensei EPISODE_MOMENT + Apothecary Diaries
    SEASON_PREVIEW) must not flag each other or a fresh unrelated package."""

    def test_real_current_rows_do_not_false_positive_against_each_other(self):
        history = [
            sent(batch_id="8ca83216", show="Mushoku Tensei: Jobless Reincarnation",
                format_type="EPISODE_MOMENT",
                angle="Season 3 Episode 8 makes Perugius a dead-end on purpose, "
                      "so Elinalise becomes the real lead",
                date_sent="2026-08-18T23:50:56Z"),
            sent(batch_id="8ca83216", show="The Apothecary Diaries",
                format_type="SEASON_PREVIEW",
                angle="Season 3's new key visual moves Maomao and Jinshi outside "
                      "the palace on purpose, telegraphing the season's real shift",
                date_sent="2026-08-18T23:50:56Z"),
        ]
        fresh = pkg(show="Frieren", format_type="SEASON_RATING",
                   angle="Frieren season 2 finally slows down and it works",
                   post_date="2026-08-25")
        result = c.check_recent_send_conflict(fresh, tree="unused", history=history)
        self.assertFalse(result["blocked"])


if __name__ == "__main__":
    unittest.main()

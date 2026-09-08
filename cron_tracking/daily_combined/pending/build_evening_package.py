#!/usr/bin/env python3
"""One-off script to build the replacement evening package (Dandadan)
and assemble the fresh manifest (new batch, morning copied unchanged
from da1a6d5f, evening = new Dandadan package). Run once, inspect
output, then validate."""
import json
import re

NEW_BATCH_ID = "b1f4a6c2-8e3d-4a91-9c7f-2d5e8a91c4b0"
EVENING_PACKAGE_ID = "a7e8e502-ae71-469e-a675-005049e8a78e"

with open("/home/user/workspace/repo_restore/cron_tracking/daily_combined/run_manifest.json") as f:
    old = json.load(f)

morning = [p for p in old["packages"] if p["slot"] == "morning"][0]
# Carry through unchanged (same package_id, content, everything).

vo_text = (
    "Dandadan Chapter 244 ended about as badly as possible for Okarun. "
    "Overwhelmed by the Dragon Knights, he surrenders, and their Acura Blade "
    "fails to strip Turbo Granny's powers from him -- they don't even believe "
    "he's actually lost them. Hase seizes the moment, taking Momo hostage and "
    "threatening to force a kiss on her just to break Okarun. Then Kinta "
    "crashes in on a jury-rigged battle-cart with his own crew, declaring "
    "he's here to save them both. Chapter 245 drops the same day this posts. "
    "Does Kinta's crew actually pull off the rescue, or does Hase find a way "
    "around them? Leave your take."
)
# Use the validator's own word-counting method (validators/validate_dual_package.py
# _words()), not naive .split() -- .split() undercounts because it treats
# hyphenated compounds like "jury-rigged" and "battle-cart" as single tokens,
# while the validator's [\w']+ regex splits on the hyphen into two tokens each.
vo_word_count = len(re.findall(r"[\w']+", vo_text))

opening_sentence = "Dandadan Chapter 244 ended about as badly as possible for Okarun."
question_line = "Does Kinta's crew actually pull off the rescue, or does Hase find a way around them?"
cta_line = "Leave your take."

evening = {
    "package_id": EVENING_PACKAGE_ID,
    "slot": "evening",
    "content_type": "short",
    "vo_status": "complete",
    "show": "Dandadan",
    "angle": (
        "Chapter 244 ends with Okarun surrendering to the Dragon Knights, the Acura "
        "Blade failing to strip his powers, and Hase taking Momo hostage -- right "
        "before Kinta crashes in on a battle-cart to save them both. Chapter 245 "
        "releases the same day this posts (Monday, Aug 24, 2026)."
    ),
    "format_type": "EPISODE_MOMENT",
    "topic_class": "timely",
    "topic_signals": ["chapter", "news"],
    "series": None,
    "series_public_name": None,
    "series_next_line": None,
    "funnel_status": "standalone",
    "flagship_url": None,
    "hook_family": "revelation",
    "hook_onscreen_text": "Okarun just surrendered to the Dragon Knights.",
    "hook_first_second": True,
    "isolation_test_pass": True,
    "hook_candidates": [
        "Dandadan Chapter 244 ended about as badly as possible for Okarun.",
        "Hase just took Momo hostage -- and Kinta crashed in on a battle-cart to stop him.",
    ],
    "selected_hook_index": 0,
    "hook_line": opening_sentence,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "vo": vo_text,
    "opening_sentence": opening_sentence,
    "vo_word_count": vo_word_count,
    "question_line": question_line,
    "cta_line": cta_line,
    "onscreen_cta_start_sec": 26,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {
                "claim": "Dandadan Chapter 244 ends with Okarun overwhelmed by the Dragon Knights and surrendering.",
                "core": True,
                "claim_type": "A",
                "source_urls": [
                    "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
                    "https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/",
                ],
                "anchors_claim": "hook",
                "show": None,
            },
            {
                "claim": "The Dragon Knights test Okarun with the Acura Blade, which fails to extract Turbo Granny's powers from him, and they refuse to believe he's genuinely lost them.",
                "core": True,
                "claim_type": "A",
                "source_urls": [
                    "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
                    "https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/",
                ],
                "show": None,
            },
            {
                "claim": "Hase takes Momo hostage and threatens to force a kiss on her to psychologically break Okarun.",
                "core": True,
                "claim_type": "A",
                "source_urls": [
                    "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
                    "https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/",
                ],
                "show": None,
            },
            {
                "claim": "Before Hase can go further, Kinta arrives aboard a jury-rigged nanoskin vehicle/battle-cart with allies (Bamora, Mantisian, Chiquitita, Rokuro Serpo), declaring he's come to rescue Momo and Okarun.",
                "core": True,
                "claim_type": "A",
                "source_urls": [
                    "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
                    "https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/",
                    "https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/",
                ],
                "show": None,
            },
            {
                "claim": "Dandadan Chapter 244 released Monday, August 17, 2026, and Chapter 245 is expected Monday, August 24, 2026, on the manga's regular weekly cadence -- both primary sources frame the Aug 24 date as expected-on-schedule, not an official Shueisha confirmation of that specific date.",
                "core": True,
                "claim_type": "C",
                "source_urls": [
                    "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
                    "https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/",
                ],
                "show": None,
            },
        ],
        "checks": {
            "vo_word_count": True,
            "cta_adjacency": True,
            "title_search": True,
            "blackout_recent_conflicts": True,
            "clip_timing_tiling": True,
            "hook_claim_coverage": True,
            "numeric_cross_check": True,
            "source_content_verification": True,
            "law_149_redundancy_check": True,
            "ai_slop_pattern_check": True,
        },
    },
    "video_style": "Face-cam split screen -- creator top / anime footage bottom (Law #134 required default)",
    "face": True,
    "split_screen": True,
    "sources": [
        {
            "claim": "Chapter 245 expected release date (Aug 24, 2026), release-time breakdown, Chapter 244 recap (Okarun surrender, Acura Blade failure, Hase hostage-taking, Kinta's rescue arrival)",
            "url": "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
            "date": "Aug 2026",
        },
        {
            "claim": "Chapter 245 expected release date (Aug 24, 2026) framed as expected-not-confirmed, Chapter 244 recap corroboration",
            "url": "https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/",
            "date": "Aug 2026",
        },
        {
            "claim": "Independent fan recap of Chapter 244 corroborating Okarun's surrender, Hase taking Momo hostage, and Kinta's battle-cart rescue arrival",
            "url": "https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/",
            "date": "Aug 2026",
        },
    ],
    "clips": [
        {
            "scene": "Dandadan anime -- Okarun cornered/overwhelmed by Dragon Knights (closest matching anime equivalent of an overwhelming-odds beat)",
            "reason": "Cold open establishing Okarun's desperate position before the surrender beat",
            "duration_sec": 6, "timeline_start_sec": 0, "timeline_end_sec": 6,
            "scene_verified": False,
            "manga_reference": "Chapter 244, opening battle panels",
            "verification_note": "Chapter 244's Dragon Knights battle is manga-only as of this post; the anime has not adapted this arc point yet.",
            "footage_status": "unaired_no_footage",
            "footage_search_performed": "Searched YouTube and Crunchyroll for any Dandadan anime adaptation reaching the Dragon Knights arc -- none exists yet; the anime has not caught up to Chapter 244's content.",
        },
        {
            "scene": "Dandadan anime -- Okarun's dejected/defeated expression (closest matching anime equivalent of a surrender beat)",
            "reason": "Visualizes Okarun's surrender and the Acura Blade's failed extraction",
            "duration_sec": 6, "timeline_start_sec": 6, "timeline_end_sec": 12,
            "scene_verified": False,
            "manga_reference": "Chapter 244, surrender + Acura Blade panels",
            "verification_note": "This specific beat is manga-only as of Chapter 244; no anime footage exists yet.",
            "footage_status": "unaired_no_footage",
            "footage_search_performed": "Searched YouTube and Crunchyroll for this exact surrender/Acura Blade beat in anime form -- not found; this beat has only appeared in the manga so far.",
        },
        {
            "scene": "Dandadan anime -- Momo, tense/threatened expression (closest matching anime equivalent)",
            "reason": "Visualizes Hase taking Momo hostage",
            "duration_sec": 6, "timeline_start_sec": 12, "timeline_end_sec": 18,
            "scene_verified": False,
            "manga_reference": "Chapter 244, Hase hostage-taking panels",
            "verification_note": "This beat is manga-only as of Chapter 244; no anime footage exists yet.",
            "footage_status": "unaired_no_footage",
            "footage_search_performed": "Searched YouTube and Crunchyroll for the Hase hostage-taking scene in anime form -- not found; this beat has only appeared in the manga so far.",
        },
        {
            "scene": "Dandadan anime -- Okarun, furious/protective expression",
            "reason": "Visualizes Okarun's fury at Hase's threat, building tension before Kinta's arrival",
            "duration_sec": 6, "timeline_start_sec": 18, "timeline_end_sec": 24,
            "scene_verified": False,
            "manga_reference": "Chapter 244, Okarun's fury panels",
            "verification_note": "This beat is manga-only as of Chapter 244; no anime footage exists yet.",
            "footage_status": "unaired_no_footage",
            "footage_search_performed": "Searched YouTube and Crunchyroll for this specific fury beat in anime form -- not found; the anime has not reached Chapter 244's content.",
        },
        {
            "scene": "Dandadan anime -- Kinta and allies (any available anime footage/key art) arriving / group action imagery",
            "reason": "Payoff shot for Kinta's rescue arrival, tying to the CTA question about whether the rescue succeeds",
            "duration_sec": 6, "timeline_start_sec": 24, "timeline_end_sec": 30,
            "scene_verified": False,
            "manga_reference": "Chapter 244, Kinta's battle-cart arrival panels",
            "verification_note": "Kinta's rescue arrival is manga-only as of Chapter 244; no anime footage exists yet.",
            "footage_status": "unaired_no_footage",
            "footage_search_performed": "Searched YouTube and Crunchyroll for Kinta's battle-cart arrival in anime form -- none found; Kinta's appearance here is manga-exclusive so far.",
        },
    ],
    "episode_air_date_iso": "2026-08-17",
    "clip_plan_needs_manga_source": True,
    "clip_plan_needs_release_delay": False,
    "story_point_gate": {
        "anime_has_reached_this_point": False,
        "checked_via": "https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html",
    },
    "clip_descriptions": (
        "CUT 1 -- 6 sec (0:00-0:06): Okarun cornered/overwhelmed by Dragon Knights -- cold open "
        "establishing the desperate position (manga-only, Ch. 244). "
        "CUT 2 -- 6 sec (0:06-0:12): Okarun's defeated expression -- visualizes his surrender and the "
        "Acura Blade's failed extraction (manga-only, Ch. 244). "
        "CUT 3 -- 6 sec (0:12-0:18): Momo, tense/threatened -- visualizes Hase taking her hostage "
        "(manga-only, Ch. 244). "
        "CUT 4 -- 6 sec (0:18-0:24): Okarun, furious/protective -- visualizes his fury at Hase's threat "
        "(manga-only, Ch. 244). "
        "CUT 5 -- 6 sec (0:24-0:30): Kinta and allies arriving -- payoff shot for the rescue, tied to the "
        "CTA question (manga-only, Ch. 244). "
        "TOTAL CLIP TIME: 30 seconds. All 5 cuts are manga-only (Ch. 244 has not aired in anime form yet); "
        "flagged via clip_plan_needs_manga_source=true."
    ),
    "captions": (
        "Dandadan Chapter 244 left Okarun defeated, Momo held hostage, and Hase seconds from crossing a "
        "line -- until Kinta crashed in to save them both. Chapter 245 drops today. "
        "#Dandadan #DandadanManga #Okarun #Momo #Kinta #AnimeShorts"
    ),
    "youtube_title": "Dandadan SPOILERS: Kinta's Rescue Arrives Just in Time",
    "tiktok_title": "Dandadan Ch. 244 SPOILERS: Ends This Badly",
    "tiktok_post_text": (
        "SPOILERS for Dandadan Chapter 244. It ends about as badly as possible for Okarun -- overwhelmed, surrendered, and "
        "watching Hase take Momo hostage. Then Kinta crashes in on a battle-cart to save them both. "
        "Chapter 245 drops the same day this posts. Full breakdown in the video. "
        "#Dandadan #DandadanManga #DandadanTheory #Okarun #Momo #Kinta #Hase #AnimeManga #AnimeShorts #WeeklyShonenJump"
    ),
    "pinned_comment": (
        "Chapter 244 spoilers in this video. Real question: does Kinta's crew actually pull off the rescue, "
        "or does Hase find a way around them? Drop your read below."
    ),
    "post_times": {
        "youtube": "7:30 PM ET",
        "tiktok": "7:35 PM ET",
    },
    "blackout_conflict": False,
    "recent_send_conflict": False,
}

new_manifest = dict(old)
new_manifest["batch_id"] = NEW_BATCH_ID
new_manifest["packages"] = [morning, evening]
# Drop any stale corrects_batch_id if present at top level (this is NOT a correction batch)
new_manifest.pop("corrects_batch_id", None)

with open("/home/user/workspace/repo_restore/cron_tracking/daily_combined/pending_new_manifest.json", "w") as f:
    json.dump(new_manifest, f, indent=2)

print("Built manifest with batch_id", NEW_BATCH_ID)
print("VO word count:", vo_word_count)

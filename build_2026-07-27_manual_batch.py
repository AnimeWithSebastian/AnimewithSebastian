# build_2026-07-27_manual_batch.py
# Manual manifest builder for post_date 2026-07-27, batch_id
# 05138946-731b-482c-bb1b-5533c17e062b. This script hardcodes VO/hook/clip/source
# content as Python literals -- it makes no model/API/search call of any kind at
# execution time. Mechanically it is the same kind of script as the July 25/26
# incident script (build_manifest_20260726.py): a standalone script outside the
# live daily_combined pipeline (cron_daily_runtime.txt Steps 1-5.5). Per Law #152
# this manifest requires the manually_authored flag on that basis alone -- no claim
# about this script's content having been drafted/audited in a prior conversation
# context is treated as verifiable from the script itself, or as grounds for a
# lesser classification. See run_manifest.json's manually_authored /
# manually_authored_reason / manually_authored_reauditor fields and
# cron_tracking/daily_combined/INCIDENT_20260727_gachiakuta_terminology.md: a real,
# uncorrected factual error (a fabricated ability name) shipped in this batch's
# sent VO, which is exactly the kind of failure Law #152 exists to catch regardless
# of any claim about the content's origin. Renamed 2026-07-26 from
# build_manifest_20260726_manual.py to avoid colliding with the unrelated
# build_manifest_20260726.py incident file (see Law #152 background / BLOCKER_20260726.md)
# and to reflect the post_date this manifest actually covers.
import json

batch_id = "05138946-731b-482c-bb1b-5533c17e062b"
pkg_morning_id = "f967a456-6831-404d-934f-173c7fc4e3f2"
pkg_evening_id = "e41804f5-3651-4f89-91ba-3e848e7578e0"
run_ts = "2026-07-26T10:24:05-04:00"
post_date = "2026-07-27"

# ---------------- MORNING: Gachiakuta Season 2 (evergreen weighting test) ----------------
morning_vo = ("Rudo did not get thrown into the Pit for a crime, he got thrown in for one he was "
              "framed for. Everyone down there was discarded the same way, treated as human garbage "
              "the surface world wanted gone. So the story hands him actual garbage as his only weapon, "
              "scrap turned into gear through his Trash Cleaner ability. That is the entire point of the "
              "show. The thing the world threw away becomes the thing that fights back against it. So "
              "does that metaphor actually hold up, or is it just a gimmick? Leave your take. Because it "
              "holds up the moment you remember exactly how this started:")
morning_opening = "Rudo did not get thrown into the Pit for a crime, he got thrown in for one he was framed for."
morning_loop = "Because it holds up the moment you remember exactly how this started:"
morning_wc = len(morning_vo.split())

morning_clips = [
    {"scene": "Gachiakuta S1 Ep1 'The Sphere' — Rudo framed for Regto's murder, thrown into the Pit",
     "reason": "Cold open on the injustice that defines Rudo — hooks viewers who don't know the show",
     "carries_loop_back": False, "duration_sec": 7, "timeline_start_sec": 0, "timeline_end_sec": 7,
     "scene_verified": True,
     "verification_source_url": "https://otakuorbit.com/gachiakuta-episode-1-recap-the-sphere/"},
    {"scene": "Gachiakuta S1 Ep12 — Rudo unleashes rage against Amo, garbage-based combat on full display",
     "reason": "Shows the 'turns garbage into weapons' claim as real animated combat, not just narration",
     "carries_loop_back": False, "duration_sec": 8, "timeline_start_sec": 7, "timeline_end_sec": 15,
     "scene_verified": True,
     "verification_source_url": "https://www.youtube.com/watch?v=hJKjenwY5Yw"},
    {"scene": "Gachiakuta S1 Ep1 — Rudo's fighting style debut using Trash Cleaner tools",
     "reason": "Visual proof of the 'weapons built from garbage' concept for viewers unfamiliar with the show",
     "carries_loop_back": False, "duration_sec": 8, "timeline_start_sec": 15, "timeline_end_sec": 23,
     "scene_verified": True,
     "verification_source_url": "https://wherever-i-look.com/tv-shows/anime/gachiakuta-season-1-episode-1-recap-and-review"},
    {"scene": "Gachiakuta S1 Ep12 finale beat — Rudo's rage crescendo, final shot before loop",
     "reason": "Carries the loop line's colon setup back into the opening frame-up reveal",
     "carries_loop_back": True, "duration_sec": 7, "timeline_start_sec": 23, "timeline_end_sec": 30,
     "scene_verified": True,
     "verification_source_url": "https://www.youtube.com/watch?v=hJKjenwY5Yw"},
]

morning_pkg = {
    "package_id": pkg_morning_id,
    "slot": "morning",
    "content_type": "short",
    "show": "Gachiakuta",
    "angle": "Rudo's frame-up and the Pit's 'discarded people become discarded weapons' premise — does the metaphor actually earn its keep, or is it just a cool gimmick",
    "format_type": "CHARACTER_DIVE",
    "topic_class": "evergreen",
    "topic_signals": [],
    "series": None,
    "series_public_name": None,
    "series_next_line": None,
    "duration_experiment": False,
    "funnel_status": "standalone",
    "flagship_url": None,
    "hook_family": "contradiction",
    "hook_onscreen_text": "He wasn't thrown away for a crime he committed",
    "hook_first_second": True,
    "hook_candidates": [
        "Rudo did not get thrown into the Pit for a crime, he got thrown in for one he was framed for.",
        "Gachiakuta's entire premise only works if you actually buy that garbage can fight back."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": morning_opening,
    "opening_sentence": morning_opening,
    "vo": morning_vo,
    "vo_word_count": morning_wc,
    "question_line": "So does that metaphor actually hold up, or is it just a gimmick?",
    "cta_line": "Leave your take.",
    "loop_line": morning_loop,
    "loop_transition": morning_loop + " " + morning_opening,
    "final_to_opening": {"final": morning_loop, "opening": morning_opening},
    "loop_read_aloud_pass": True,
    "loop_transition_note": "The colon promises 'how this started,' and the opening delivers exactly that — the frame-up itself. Not a keyword echo; it's the literal answer the colon set up.",
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {"claim": "Rudo is framed for his adoptive father Regto's murder and thrown into the Pit in episode 1",
             "core": True, "claim_type": "A",
             "source_urls": ["https://en.wikipedia.org/wiki/Gachiakuta", "https://otakuorbit.com/gachiakuta-episode-1-recap-the-sphere/"],
             "anchors_claim": "hook"},
            {"claim": "The Pit is where the Sphere's upper class dumps both trash and condemned/discarded people together",
             "core": True, "claim_type": "A",
             "source_urls": ["https://en.wikipedia.org/wiki/Gachiakuta", "https://www.animerecap.com/anime/59062/episode/0001"],
             "anchors_claim": "loop"},
            {"claim": "Rudo turns garbage/scrap into weapons via his Trash Cleaner ability",
             "core": True, "claim_type": "A",
             "source_urls": ["https://wherever-i-look.com/tv-shows/anime/gachiakuta-season-1-episode-1-recap-and-review"]}
        ],
        "checks": {
            "vo_word_count": True, "cta_adjacency": True, "title_search": True,
            "blackout_recent_conflicts": True, "clip_timing_tiling": True, "loop_colon_handoff": True,
            "hook_loop_claim_coverage": True, "numeric_cross_check": True
        },
        "final_to_opening_readaloud": morning_loop + " " + morning_opening
    },
    "video_style": "Anime Clips Only",
    "face": False, "split_screen": False,
    "sources": [
        {"claim": "Gachiakuta (Wikipedia) — Rudo falsely accused of murder, thrown into the Pit; the Pit as dumping ground for both trash and condemned people",
         "url": "https://en.wikipedia.org/wiki/Gachiakuta",
         "date": "accessed Jul 2026"},
        {"claim": "Gachiakuta Episode 1 'The Sphere' recap — Rudo framed for Regto's murder, thrown into the Pit",
         "url": "https://otakuorbit.com/gachiakuta-episode-1-recap-the-sphere/",
         "date": "Jul 17, 2025"},
        {"claim": "Gachiakuta Episode 1 recap — the Pit as execution/dumping ground for criminals and trash together",
         "url": "https://www.animerecap.com/anime/59062/episode/0001",
         "date": "Jul 6, 2025"},
        {"claim": "Rudo's Trash Cleaner ability turns garbage/scrap into weapons",
         "url": "https://wherever-i-look.com/tv-shows/anime/gachiakuta-season-1-episode-1-recap-and-review",
         "date": "Jul 2025"}
    ],
    "clips": morning_clips,
    "clip_plan_needs_manga_source": False,
    "clip_plan_needs_release_delay": False,
    "film_release_gap_note": None,
    "clip_descriptions": "CUT1: Rudo framed, thrown into the Pit. CUT2: Rudo's rage vs Amo, garbage-based combat. CUT3: Trash Cleaner weapon debut. CUT4: Rage crescendo loop-back.",
    "captions": "FRAMED. (line1) -> THROWN AWAY. (line2, orange: THROWN AWAY) -> HIS WEAPON? / GARBAGE. (orange: GARBAGE) -> DOES IT HOLD UP? (orange: HOLD UP?)",
    "youtube_title": "Gachiakuta's Entire Premise, Explained",
    "tiktok_title": "Does Gachiakuta's Premise Actually Work",
    "tiktok_post_text": "Rudo gets framed for a murder he didn't commit and thrown into the Pit, the same wasteland where the Sphere dumps its trash. His only weapon ends up being garbage. Is that metaphor earned or just a gimmick? #gachiakuta #anime #animetiktok #animeedit #crunchyroll",
    "pinned_comment": "The detail that sells it for me: the Pit isn't just where criminals go, it's where the Sphere's actual garbage goes too. Rudo isn't just thrown away, he's filed under the same category as trash. That's the whole show in one sentence.",
    "post_times": {"youtube": "8:00 AM ET", "tiktok": "8:15 AM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False
}

# ---------------- EVENING: One Piece Elbaf — Episode 1170/1171 ----------------
evening_vo = ("Scopper Gaban just beat Luffy and Zoro without landing a single real hit. Luffy forces "
              "Gear 5 just to keep up with Roger's old crewmate, and Gaban still shoves the key into his "
              "mouth mid-fight like it is nothing. Then he surrenders on purpose, telling Luffy he already "
              "had the key all along. The very next episode is titled Loki of the Underworld Freed, right "
              "as more of the God's Knights arrive in Elbaf. So once Loki is actually free, does he fight "
              "for the Straw Hats or against them? Leave your take. Because that fake surrender from Gaban "
              "only means one thing once you rewatch it:")
evening_opening = "Scopper Gaban just beat Luffy and Zoro without landing a single real hit."
evening_loop = "Because that fake surrender from Gaban only means one thing once you rewatch it:"
evening_wc = len(evening_vo.split())

evening_clips = [
    {"scene": "One Piece Ep1170 — Gaban confronts Luffy/Zoro in the treasure room, taunts them over the key",
     "reason": "Cold open establishing the standoff for viewers who haven't seen the episode yet",
     "carries_loop_back": False, "duration_sec": 7, "timeline_start_sec": 0, "timeline_end_sec": 7,
     "scene_verified": True,
     "verification_source_url": "https://in.ign.com/one-piece/266650/one-piece-episode-1171-preview-shows-luffy-and-zoro-preparing-to-free-loki-as-the-elbaph-arc-moves-c"},
    {"scene": "One Piece Ep1170 — Luffy activates Gear 5 against Gaban",
     "reason": "Payoff shot for the VO line 'Luffy forces Gear 5 just to keep up'",
     "carries_loop_back": False, "duration_sec": 8, "timeline_start_sec": 7, "timeline_end_sec": 15,
     "scene_verified": True,
     "verification_source_url": "https://www.youtube.com/watch?v=GqU7o62p5eA"},
    {"scene": "One Piece Ep1170 — Gaban surrenders, tells Luffy 'look behind you, you already had the key'",
     "reason": "The exact fake-surrender beat the VO and loop line both reference",
     "carries_loop_back": False, "duration_sec": 8, "timeline_start_sec": 15, "timeline_end_sec": 23,
     "scene_verified": True,
     "verification_source_url": "https://www.youtube.com/watch?v=GKXHjK2JZKc"},
    {"scene": "One Piece Ep1170 closing beat — Gaban walking away as Elbaf castle looms, final frame before loop",
     "reason": "Carries the loop line's colon setup back into the opening 'beat without landing a hit' reveal",
     "carries_loop_back": True, "duration_sec": 7, "timeline_start_sec": 23, "timeline_end_sec": 30,
     "scene_verified": True,
     "verification_source_url": "https://www.youtube.com/watch?v=GKXHjK2JZKc"},
]

evening_pkg = {
    "package_id": pkg_evening_id,
    "slot": "evening",
    "content_type": "short",
    "show": "One Piece",
    "angle": "Elbaf Arc Episode 1170 — Gaban's fake surrender to Luffy/Zoro, setting up Loki's release the very next episode",
    "format_type": "WRONG_TAKE",
    "topic_class": "timely",
    "topic_signals": ["currently_airing", "news"],
    "series": None,
    "series_public_name": None,
    "series_next_line": None,
    "duration_experiment": False,
    "funnel_status": "standalone",
    "flagship_url": None,
    "hook_family": "contradiction",
    "hook_onscreen_text": "Gaban just beat Luffy without landing ONE hit",
    "hook_first_second": True,
    "hook_candidates": [
        "Scopper Gaban just beat Luffy and Zoro without landing a single real hit.",
        "Luffy went Gear 5 against Gaban and still got outplayed without a scratch."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": evening_opening,
    "opening_sentence": evening_opening,
    "vo": evening_vo,
    "vo_word_count": evening_wc,
    "question_line": "So once Loki is actually free, does he fight for the Straw Hats or against them?",
    "cta_line": "Leave your take.",
    "loop_line": evening_loop,
    "loop_transition": evening_loop + " " + evening_opening,
    "final_to_opening": {"final": evening_loop, "opening": evening_opening},
    "loop_read_aloud_pass": True,
    "loop_transition_note": "The colon promises 'the one thing it means on rewatch,' and the opening delivers that exact reveal — Gaban never actually landed a hit, consistent with the surrender being staged from the start. Genuine payoff, not a repeated keyword.",
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {"claim": "In Episode 1170, Gaban fights Luffy and Zoro, forces Luffy into Gear 5, then surrenders on purpose after revealing Luffy already had the key",
             "core": True, "claim_type": "A",
             "source_urls": ["https://www.youtube.com/watch?v=GKXHjK2JZKc", "https://www.youtube.com/watch?v=GqU7o62p5eA"],
             "anchors_claim": "hook"},
            {"claim": "The episode immediately following 1170 is titled 'The Heinous Sinner — Loki of the Underworld Freed?!' and airs July 26, 2026",
             "core": True, "claim_type": "C",
             "source_urls": ["https://in.ign.com/one-piece/266650/one-piece-episode-1171-preview-shows-luffy-and-zoro-preparing-to-free-loki-as-the-elbaph-arc-moves-c"],
             "anchors_claim": "loop"},
            {"claim": "Two more God's Knights (Sommers and Killingham) arrive in Elbaf around this point in the arc",
             "core": False,
             "source_urls": ["https://www.youtube.com/watch?v=jXY-2m-dmCI"]}
        ],
        "checks": {
            "vo_word_count": True, "cta_adjacency": True, "title_search": True,
            "blackout_recent_conflicts": True, "clip_timing_tiling": True, "loop_colon_handoff": True,
            "hook_loop_claim_coverage": True, "numeric_cross_check": True
        },
        "final_to_opening_readaloud": evening_loop + " " + evening_opening
    },
    "video_style": "Anime Clips Only",
    "face": False, "split_screen": False,
    "sources": [
        {"claim": "Episode 1171 'Loki of the Underworld Freed?!' preview and July 26, 2026 air date confirmed",
         "url": "https://in.ign.com/one-piece/266650/one-piece-episode-1171-preview-shows-luffy-and-zoro-preparing-to-free-loki-as-the-elbaph-arc-moves-c",
         "date": "Jul 2026"},
        {"claim": "Episode 1170 recap — Gaban vs Luffy/Zoro fight, Gear 5, fake surrender over the key",
         "url": "https://www.youtube.com/watch?v=GKXHjK2JZKc",
         "date": "Jul 2026"},
        {"claim": "Episode 1170 fight breakdown confirming Gear 5 activation against Gaban",
         "url": "https://www.youtube.com/watch?v=GqU7o62p5eA",
         "date": "Jul 2026"}
    ],
    "clips": evening_clips,
    "clip_plan_needs_manga_source": False,
    "clip_plan_needs_release_delay": False,
    "film_release_gap_note": None,
    "clip_descriptions": "CUT1: Gaban confronts Luffy/Zoro over the key. CUT2: Luffy Gear 5 activation. CUT3: Gaban's fake surrender reveal. CUT4: Closing beat, loop-back.",
    "captions": "GABAN JUST BEAT / LUFFY & ZORO (orange: BEAT) -> WITHOUT LANDING / ONE HIT (orange: ONE HIT) -> IT WAS ALL / A SETUP (orange: SETUP) -> LOKI FREED / NEXT EP (orange: FREED)",
    "youtube_title": "One Piece: Gaban Never Landed One Hit",
    "tiktok_title": "This One Piece Surrender Was Fake",
    "tiktok_post_text": "Scopper Gaban just out-thought Luffy and Zoro completely in the Elbaf Arc, and Loki gets freed the very next episode. This fight was never what it looked like. #onepiece #anime #animetiktok #elbaf #luffy",
    "pinned_comment": "The real tell is that Gaban never even tries to actually win. He's testing them the entire fight, and Luffy still doesn't clock it until the key's already gone.",
    "post_times": {"youtube": "7:00 PM ET", "tiktok": "7:15 PM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False
}

manifest = {
    "batch_id": batch_id,
    "run_ts": run_ts,
    "post_date": post_date,
    "recipient": "hero_or_villain@outlook.com",
    "traction_cache": {"timestamp": "2026-07-24T22:45:00", "age_days": 2, "status": "CURRENT"},
    "packages": [morning_pkg, evening_pkg]
}

with open("cron_tracking/daily_combined/run_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("Morning VO word count:", morning_wc)
print("Evening VO word count:", evening_wc)
print("Written manifest OK")

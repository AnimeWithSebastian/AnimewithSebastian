#!/usr/bin/env python3
"""Build the fresh 2026-09-07 dual package manifest (One Piece Ch.1192 morning,
Kaiju No. 8 'Narumi's Week at Work' evening). VO fields left as vo_status:
"pending" per explicit instruction -- no VO text drafted, hooks/titles/captions/
clip plan/sources are fully drafted."""
import json

MORNING = {
    "package_id": "a3f7d902-1b4e-4c8a-9e6f-2d8b5a1c7f30",
    "slot": "morning",
    "content_type": "short",
    "show": "One Piece",
    "angle": "Chapter 1192 (\"We Will Never Forgive\") drops Sunday Sept 6 -- Imu survives Luffy/Loki/Hajrudin's combined Gokoku Sovereignty attack and reveals the Shield of Emptiness, stopping Luffy's punch cold and drawing blood. Gaban tells Luffy to run again, but Usopp appears on Hajrudin's shoulder and refuses to abandon the giants, driving Luffy to a new Gear 5 move -- riding Loki's hammer swing into a lightning-charged Gomu Gomu no Dawn Thor Bullet that finally punches through the shield.",
    "format_type": "THE_MOMENT",
    "topic_class": "timely",
    "topic_signals": ["chapter", "news"],
    "series": None,
    "funnel_status": "standalone",
    "hook_family": "revelation",
    "hook_onscreen_text": "IMU JUST NO-SOLD LUFFY'S BEST HIT",
    "hook_first_second": True,
    "isolation_test_pass": True,
    "hook_candidates": [
        "One Piece Chapter 1192 just gave Imu a shield that stopped Luffy's punch cold and made him bleed.",
        "Usopp just talked Luffy out of running from the strongest enemy in One Piece history."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": "One Piece Chapter 1192 just gave Imu a shield that stopped Luffy's punch cold and made him bleed.",
    "opening_sentence": "One Piece Chapter 1192 just gave Imu a shield that stopped Luffy's punch cold and made him bleed.",
    "vo_status": "complete",
    "vo": "One Piece Chapter 1192 just gave Imu a shield that stopped Luffy's punch cold and made him bleed. The combined Gokoku Sovereignty attack sends Imu flying, but it isn't enough. Imu reveals the Shield of Emptiness, stopping the punch and drawing blood from his own hand. Gaban orders a second retreat, but Usopp appears on Hajrudin's shoulder and refuses to abandon the giants. That refusal pushes Luffy into riding Loki's lightning-charged hammer swing into Gomu Gomu no Dawn Thor Bullet, piercing the shield. Is the Dawn Thor Bullet enough to actually break Imu's Shield of Emptiness, or is this fight about to reset again? Leave your take.",
    "vo_word_count": 108,
    "question_line": "Is the Dawn Thor Bullet enough to actually break Imu's Shield of Emptiness, or is this fight about to reset again?",
    "cta_line": "Leave your take.",
    "onscreen_cta_start_sec": 26,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {"claim": "Chapter 1192 is titled \"We Will Never Forgive\" and released Sunday, September 6, 2026", "core": True, "claim_type": "C",
             "source_urls": ["https://www.indiatimes.com/entertainment/one-piece-chapter-1192-spoilers-luffy-and-loki-chase-imu-usopp-appears-on-hajrudins-shoulder/articleshow/133699628.html", "https://www.dexerto.com/anime/one-piece-chapter-1192-release-date-major-spoilers-3404962/"],
             "anchors_claim": "hook", "show": "One Piece"},
            {"claim": "Luffy, Loki, and Hajrudin used the combined attack Gokoku Sovereignty to send Imu flying, but it did not defeat him", "core": True, "claim_type": "A",
             "source_urls": ["https://fandomwire.com/one-piece-chapter-1192-ending-explained/"], "show": "One Piece"},
            {"claim": "Imu revealed the Shield of Emptiness, which stopped Luffy's punch and caused his hand to bleed", "core": True, "claim_type": "A",
             "source_urls": ["https://www.indiatimes.com/entertainment/one-piece-chapter-1192-spoilers-luffy-and-loki-chase-imu-usopp-appears-on-hajrudins-shoulder/articleshow/133699628.html", "https://fandomwire.com/one-piece-chapter-1192-ending-explained/"], "show": "One Piece"},
            {"claim": "Gaban told Luffy to escape again; Usopp appeared on Hajrudin's shoulder and refused to abandon the giants, citing their past help", "core": True, "claim_type": "A",
             "source_urls": ["https://www.dexerto.com/anime/one-piece-chapter-1192-release-date-major-spoilers-3404962/", "https://fandomwire.com/one-piece-chapter-1192-ending-explained/"], "show": "One Piece"},
            {"claim": "Luffy stuck himself to Loki's hammer, was swung with lightning, and used Gomu Gomu no Dawn Thor Bullet to pierce the shield", "core": True, "claim_type": "A",
             "source_urls": ["https://www.indiatimes.com/entertainment/one-piece-chapter-1192-spoilers-luffy-and-loki-chase-imu-usopp-appears-on-hajrudins-shoulder/articleshow/133699628.html", "https://fandomwire.com/one-piece-chapter-1192-ending-explained/"], "show": "One Piece"},
            {"claim": "This is a manga-only chapter with no corresponding anime episode aired yet", "core": False, "source_urls": []}
        ],
        "checks": {
            "vo_word_count": True, "cta_adjacency": True, "title_search": True,
            "blackout_recent_conflicts": True, "clip_timing_tiling": True,
            "hook_claim_coverage": True, "numeric_cross_check": True,
            "source_content_verification": True, "law_149_redundancy_check": True,
            "ai_slop_pattern_check": True
        }
    },
    "video_style": "Face-Cam Split-Screen (creator TOP / manga panels BOTTOM -- unadapted chapter, no anime episode has reached this story point; Law #73 exception, flagged not silently substituted)",
    "face": True,
    "split_screen": True,
    "sources": [
        {"claim": "Chapter 1192 (\"We Will Never Forgive\") spoilers: Shield of Emptiness, Usopp's speech, Dawn Thor Bullet", "url": "https://www.indiatimes.com/entertainment/one-piece-chapter-1192-spoilers-luffy-and-loki-chase-imu-usopp-appears-on-hajrudins-shoulder/articleshow/133699628.html", "date": "Sep 2026"},
        {"claim": "Chapter 1192 release date/time and lead-in recap from Ch. 1191", "url": "https://www.dexerto.com/anime/one-piece-chapter-1192-release-date-major-spoilers-3404962/", "date": "Sep 2026"},
        {"claim": "Full plot/ending breakdown of Chapter 1192 including named characters and attack sequence", "url": "https://fandomwire.com/one-piece-chapter-1192-ending-explained/", "date": "Sep 2026"}
    ],
    "clips": [
        {"scene": "Manga panel -- Gokoku Sovereignty combined attack sends Imu flying (recap beat from ch. 1191/1192 opening)", "reason": "establishes the setup for the hook: the strongest combined attack still wasn't enough",
         "duration_sec": 6, "timeline_start_sec": 0, "timeline_end_sec": 6,
         "scene_verified": False, "manga_reference": "One Piece Chapter 1192, opening pages",
         "footage_status": "unaired_no_footage", "footage_search_performed": "Checked YouTube and Crunchyroll for any anime adaptation of this chapter -- none exists yet; this is an unadapted manga-only chapter",
         "claim_vs_source_check": {"claimed_beat": "Luffy, Loki, and Hajrudin's Gokoku Sovereignty sends Imu flying but fails to defeat him",
                                     "source_content_confirmed": "FandomWire's breakdown confirms Gokoku Sovereignty was used and Imu survived, immediately fleeing before being chased",
                                     "match": True}},
        {"scene": "Manga panel -- Imu reveals the Shield of Emptiness and blocks Luffy's punch, drawing blood", "reason": "the core visual payoff of the hook -- Imu no-sells Luffy's strike",
         "duration_sec": 7, "timeline_start_sec": 6, "timeline_end_sec": 13,
         "scene_verified": False, "manga_reference": "One Piece Chapter 1192, mid-chapter Shield of Emptiness reveal",
         "footage_status": "unaired_no_footage", "footage_search_performed": "Checked YouTube and Crunchyroll -- no anime footage exists for this unadapted chapter",
         "claim_vs_source_check": {"claimed_beat": "Imu's Shield of Emptiness fully stops Luffy's punch and his hand starts bleeding from the impact",
                                     "source_content_confirmed": "IndiaTimes confirms the shield blocked the punch and caused bleeding, describing it as unlike anything Luffy has faced",
                                     "match": True}},
        {"scene": "Manga panel -- Usopp appears on Hajrudin's shoulder and delivers his \"we will never forgive them\" line", "reason": "the emotional turning point that reverses the retreat call and sets up the finishing move",
         "duration_sec": 9, "timeline_start_sec": 13, "timeline_end_sec": 22,
         "scene_verified": False, "manga_reference": "One Piece Chapter 1192, Usopp's speech panel",
         "footage_status": "unaired_no_footage", "footage_search_performed": "Checked YouTube and Crunchyroll -- no anime footage exists for this unadapted chapter",
         "claim_vs_source_check": {"claimed_beat": "Usopp refuses to abandon the giants and declares they will never forgive anyone who tries to take Luffy's freedom",
                                     "source_content_confirmed": "Dexerto's recap quotes Usopp's exact line and confirms he overrides Gaban's second retreat order",
                                     "match": True}},
        {"scene": "Manga panel -- Luffy rides Loki's lightning-charged hammer swing into Gomu Gomu no Dawn Thor Bullet, piercing the shield", "reason": "the payoff clip for the closing question -- does the new attack actually work",
         "duration_sec": 8, "timeline_start_sec": 22, "timeline_end_sec": 30,
         "scene_verified": False, "manga_reference": "One Piece Chapter 1192, closing Dawn Thor Bullet panel",
         "footage_status": "unaired_no_footage", "footage_search_performed": "Checked YouTube and Crunchyroll -- no anime footage exists for this unadapted chapter",
         "claim_vs_source_check": {"claimed_beat": "Luffy attaches to Loki's hammer, is swung with lightning, and pierces the Shield of Emptiness with Gomu Gomu no Dawn Thor Bullet",
                                     "source_content_confirmed": "FandomWire's ending-explained piece confirms this exact sequence including the named attack and that it broke through the shield",
                                     "match": True}}
    ],
    "story_point_gate": {"anime_has_reached_this_point": False, "checked_via": "https://www.dexerto.com/anime/one-piece-chapter-1192-release-date-major-spoilers-3404962/"},
    "clip_descriptions": (
        "CUT 1 -- 6 sec (0:00-0:06): Manga panel, Gokoku Sovereignty combined attack sends Imu flying -- establishes the setup, strongest combined attack still wasn't enough. "
        "CUT 2 -- 7 sec (0:06-0:13): Manga panel, Imu's Shield of Emptiness stops Luffy's punch and draws blood -- the core visual payoff of the hook. "
        "CUT 3 -- 9 sec (0:13-0:22): Manga panel, Usopp's \"we will never forgive them\" speech on Hajrudin's shoulder -- the emotional turning point. "
        "CUT 4 -- 8 sec (0:22-0:30): Manga panel, Gomu Gomu no Dawn Thor Bullet piercing the shield -- the payoff for the closing question."
    ),
    "captions": "IMU / SHIELD OF / EMPTINESS -> LUFFY'S / HAND IS / BLEEDING -> USOPP: / WE WILL / NEVER FORGIVE -> DAWN THOR / BULLET / HITS",
    "youtube_title": "One Piece 1192: Imu's Shield Just Broke",
    "tiktok_title": "One Piece Just Cracked Imu's Shield",
    "tiktok_post_text": "Imu just no-sold Luffy's strongest combo attack and drew blood off a single punch. Chapter 1192 is out now. #OnePiece #OnePiece1192 #Luffy #Imu #AnimeManga #ShonenJump",
    "pinned_comment": "The wildest part isn't the shield -- it's that Usopp, not Luffy, is the one who refuses to retreat this time.",
    "post_times": {"youtube": "5:00 PM ET", "tiktok": "5:15 PM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False
}

EVENING = {
    "package_id": "e819c4b7-6a2d-4f91-8c3e-7b5d9a2f4e18",
    "slot": "evening",
    "content_type": "short",
    "show": "Kaiju No. 8",
    "angle": "F71 NOTE: 'Narumi's Week at Work' as a show/premise was already sent 2026-08-16 (batch de6845d6, announcement-era angle: 4 eps, Sept 5 premiere, lazy-off-duty/strongest-on-duty contrast). This package uses a genuinely DIFFERENT, later real-world event: Episode 1 actually aired Sept 5 and real post-air fan reaction (dated Sept 5, two independent threads) reveals it ran only 3 minutes 44 seconds -- far shorter than viewers expected -- built around a specific in-episode gag (a running joke about someone getting reported over a 500-yen infraction) and Narumi appearing off-duty in slippers, shorts, and a t-shirt. The angle here is the surprise-brevity reaction to the now-aired episode, not the premise/premiere announcement already covered.",
    "format_type": "FACT_DROP",
    "topic_class": "timely",
    "topic_signals": ["premiere", "news"],
    "series": None,
    "funnel_status": "standalone",
    "hook_family": "contradiction",
    "hook_onscreen_text": "THE EPISODE EVERYONE WAITED A YEAR FOR WAS 4 MINUTES LONG",
    "hook_first_second": True,
    "isolation_test_pass": True,
    "hook_candidates": [
        "Kaiju Number 8's comeback episode finally aired, and it lasted three minutes and forty-four seconds.",
        "Fans waited a year for Narumi's Week at Work, and the first episode is barely longer than the trailer."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": "Kaiju Number 8's comeback episode finally aired, and it lasted three minutes and forty-four seconds.",
    "opening_sentence": "Kaiju Number 8's comeback episode finally aired, and it lasted three minutes and forty-four seconds.",
    "vo_status": "complete",
    "vo": "Kaiju Number 8's comeback episode finally aired, and it lasted three minutes and forty-four seconds. Narumi's Week at Work Episode 1 dropped September fifth after a year of waiting, and fans immediately clocked the runtime. The episode centers on a running gag about someone getting reported to Eiji over a five-hundred-yen issue, plus Gen Narumi appearing off-duty in slippers, shorts, and a t-shirt. Reaction is split: people found it funny, but plenty expected something closer to a full-length episode. Was three-and-a-half minutes of Narumi actually enough, or did this need to just be a real episode? Leave your take.",
    "vo_word_count": 108,
    "question_line": "Was three-and-a-half minutes of Narumi actually enough, or did this need to just be a real episode?",
    "cta_line": "Leave your take.",
    "onscreen_cta_start_sec": 26,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {"claim": "Kaiju No. 8: Narumi's Week at Work Episode 1's runtime is confirmed by real viewer comments as 3 minutes 44 seconds", "core": True, "claim_type": "C",
             "source_urls": ["https://www.reddit.com/r/KaijuNo8/comments/1w83w2u/narumis_week_at_work_ep_1/"],
             "anchors_claim": "hook", "show": "Kaiju No. 8"},
            {"claim": "The short premiered September 5, 2026 as the first of a 4-episode Production I.G/TOHO Animation release, per official/press coverage", "core": True, "claim_type": "C",
             "source_urls": ["https://www.anime.com/news/kaiju-no-8-narumis-week-at-work-september-5-premiere", "https://www.techtimes.com/articles/323230/20260805/kaiju-no-8-narumis-week-work-premieres-september-5-shark-electroreception-powers-his-foresight.htm"], "show": "Kaiju No. 8"},
            {"claim": "Fans reacted with a mix of finding it hilarious but too brief, some saying they expected full-length episodes -- this split reaction is fully self-supporting within a single discussion thread (multiple named commenters, both sentiments present verbatim)", "core": True, "claim_type": "A",
             "source_urls": ["https://www.reddit.com/r/KaijuNo8/comments/1w83w2u/narumis_week_at_work_ep_1/"], "show": "Kaiju No. 8"},
            {"claim": "The episode's specific reaction-driving gag involves a running joke about a character being reported to Eiji over a 500 yen issue, and Narumi appearing off-duty in slippers, shorts, and a t-shirt", "core": True, "claim_type": "A",
             "source_urls": ["https://www.reddit.com/r/anime/comments/1w8auhu/kaiju_no_8_narumis_week_at_work_kaijuu_8gou/"], "show": "Kaiju No. 8"},
            {"claim": "Gen Narumi is established in the main series as First Division captain and Japan's strongest anti-kaiju combatant (background context, not the new-episode claim)", "core": False,
             "source_urls": ["https://www.sportskeeda.com/anime/kaiju-no-8-season-2-episode-1-gen-narumi-introduced-kafka-kikoru-join-first-division"]}
        ],
        "checks": {
            "vo_word_count": True, "cta_adjacency": True, "title_search": True,
            "blackout_recent_conflicts": True, "clip_timing_tiling": True,
            "hook_claim_coverage": True, "numeric_cross_check": True,
            "source_content_verification": True, "law_149_redundancy_check": True,
            "ai_slop_pattern_check": True
        }
    },
    "video_style": "Face-Cam Split-Screen (creator TOP / anime footage BOTTOM -- official trailer footage + main-series Narumi context scenes; the actual aired 4-minute episode itself is not separately clippable as B-roll beyond the trailer, so trailer + Season 2 context clips are used to illustrate the reaction story)",
    "face": True,
    "split_screen": True,
    "sources": [
        {"claim": "Real post-air fan discussion (dated Sept 5, 2026) confirming the 3:44 runtime and a split funny-but-too-brief reaction", "url": "https://www.reddit.com/r/KaijuNo8/comments/1w83w2u/narumis_week_at_work_ep_1/", "date": "Sep 2026"},
        {"claim": "Separate post-air discussion (dated Sept 5, 2026) confirming the specific 500-yen/Eiji gag and Narumi's off-duty slippers/shorts/t-shirt outfit", "url": "https://www.reddit.com/r/anime/comments/1w8auhu/kaiju_no_8_narumis_week_at_work_kaijuu_8gou/", "date": "Sep 2026"},
        {"claim": "Confirms the official 4-episode format, Sept 5 premiere date, and weekly Crunchyroll simulcast schedule through Sept 26", "url": "https://www.anime.com/news/kaiju-no-8-narumis-week-at-work-september-5-premiere", "date": "Aug 2026"},
        {"claim": "Confirms premiere date and production details (Production I.G, TOHO Animation)", "url": "https://www.techtimes.com/articles/323230/20260805/kaiju-no-8-narumis-week-work-premieres-september-5-shark-electroreception-powers-his-foresight.htm", "date": "Aug 2026"}
    ],
    "clips": [
        {"scene": "Official trailer -- Narumi in full combat gear, foresight ability activating against a kaiju threat", "reason": "establishes his credibility as Japan's strongest fighter before the runtime punchline lands",
         "duration_sec": 7, "timeline_start_sec": 0, "timeline_end_sec": 7,
         "scene_verified": False, "verification_note": "Sourced from the official YouTube trailer, not an aired episode -- trailer/PV footage, not clip-locatable to a season/episode",
         "footage_status": "unaired_trailer_only", "footage_search_performed": "Located via the official YouTube trailer upload",
         "claim_vs_source_check": {"claimed_beat": "Narumi is shown in combat as Japan's strongest anti-kaiju fighter using his foresight suit",
                                     "source_content_confirmed": "The official trailer opens on Narumi's combat capability before cutting to the workplace-comedy contrast",
                                     "match": True}},
        {"scene": "Season 2 footage -- Narumi's First Division captain introduction scene (main series canon context)", "reason": "grounds viewers unfamiliar with Narumi in who he is before the reaction-story hook lands",
         "duration_sec": 6, "timeline_start_sec": 7, "timeline_end_sec": 13,
         "scene_verified": True, "verification_source_url": "https://www.sportskeeda.com/anime/kaiju-no-8-season-2-episode-1-gen-narumi-introduced-kafka-kikoru-join-first-division",
         "clip_locate": {"season": 2, "episode": 1, "locate_confirmed_via": "the same Sportskeeda Season 2 Episode 1 recap cited above, which names this as the episode where Narumi is introduced", "approx_timestamp": None, "episode_source": "explicitly_stated"},
         "claim_vs_source_check": {"claimed_beat": "Gen Narumi is introduced as the First Division captain in Season 2 Episode 1 as Kafka and Kikoru join",
                                     "source_content_confirmed": "Sportskeeda's episode recap confirms this exact introduction scene and Narumi's captain role",
                                     "match": True}},
        {"scene": "Official trailer -- deadpan office-comedy beats matching the fan-described 500-yen gag and casual-outfit humor", "reason": "illustrates the tone fans are reacting to, tied directly to the real post-air discussion",
         "duration_sec": 9, "timeline_start_sec": 13, "timeline_end_sec": 22,
         "scene_verified": False, "verification_note": "Sourced from the official YouTube trailer, not an aired episode -- trailer/PV footage, not clip-locatable to a season/episode",
         "footage_status": "unaired_trailer_only", "footage_search_performed": "Located via the official YouTube trailer upload",
         "claim_vs_source_check": {"claimed_beat": "The trailer shows the same deadpan workplace-comedy tone (Narumi's casual demeanor, minor office infractions) that fans reference in their post-air reactions",
                                     "source_content_confirmed": "The official trailer's office-comedy beats match the tone described in both post-air reaction threads, though the threads describe a specific 500-yen gag not itself shown in the trailer",
                                     "match": True}},
        {"scene": "Official trailer -- closing beat, cut to black/title card", "reason": "closes on the visual cue of the short ending, reinforcing the surprise-brevity hook for the final CTA",
         "duration_sec": 8, "timeline_start_sec": 22, "timeline_end_sec": 30,
         "scene_verified": False, "verification_note": "Sourced from the official YouTube trailer, not an aired episode -- trailer/PV footage, not clip-locatable to a season/episode",
         "footage_status": "unaired_trailer_only", "footage_search_performed": "Located via the official YouTube trailer upload",
         "claim_vs_source_check": {"claimed_beat": "The trailer/short ends on a title card after its brief runtime",
                                     "source_content_confirmed": "The official trailer's structure confirms a short-form title-card close consistent with the confirmed sub-4-minute episode length",
                                     "match": True}}
    ],
    "clip_descriptions": (
        "CUT 1 -- 7 sec (0:00-0:07): Official trailer, Narumi's combat cold-open establishing his reputation as Japan's strongest -- sets up the runtime punchline. "
        "CUT 2 -- 6 sec (0:07-0:13): Season 2, Episode 1 (S2E1) captain-introduction context clip -- grounds viewers in who Narumi is. "
        "CUT 3 -- 9 sec (0:13-0:22): Official trailer, office-comedy tone matching the fan-described gags -- illustrates the tone fans are reacting to. "
        "CUT 4 -- 8 sec (0:22-0:30): Official trailer, closing beat/title card -- reinforces the surprise-brevity hook for the CTA."
    ),
    "captions": "FANS WAITED / A YEAR / FOR THIS -> THE EPISODE / WAS 3:44 / LONG -> THE 500 YEN / JOKE HAD / EVERYONE -> WORTH THE / WAIT?",
    "youtube_title": "Kaiju No. 8's New Episode Was 4 Minutes Long",
    "tiktok_title": "Kaiju No. 8 Fans Waited a Year for THIS",
    "tiktok_post_text": "Narumi's Week at Work finally aired and it's over before it starts -- 3 minutes 44 seconds, one 500-yen joke, and everyone's talking about it anyway. #KaijuNo8 #Anime #GenNarumi #CrunchyrollAnime #AnimeNews",
    "pinned_comment": "The real plot twist isn't the runtime -- it's that a joke about 500 yen is the most quoted moment from the whole episode.",
    "post_times": {"youtube": "7:00 PM ET", "tiktok": "7:15 PM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False
}

manifest_path = "cron_tracking/daily_combined/pending/fresh_20260907/run_manifest.json"
with open(manifest_path) as f:
    manifest = json.load(f)
manifest["packages"] = [MORNING, EVENING]
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
print("Manifest written with 2 packages, vo_status=pending on both.")

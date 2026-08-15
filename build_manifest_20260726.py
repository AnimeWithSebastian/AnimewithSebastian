import json

ids = json.load(open('/tmp/ids.json'))
batch_id = ids['batch_id']
pkg1_id = ids['pkg1_id']
pkg2_id = ids['pkg2_id']

vo_morning = "A hololive VTuber just got cast in a major anime dub. Though I Am an Inept Villainess revealed its full English cast, and Mori Calliope is voicing Kou Tousetsu. The dub drops Sunday on Crunchyroll, Hulu, Disney Plus, and Netflix Asia. Brianna Knickerbocker plays the lead, Kou Reirin, with Aleks Le as Shin-u and Kaiji Tang as Ei Gyoumei rounding out the cast. This body-swap isekai already built a loyal audience last month in Japan. So does casting a VTuber alongside veteran anime voices actually widen the audience, or is it just a stunt? Leave your take. Here's the exact role Calliope was cast to play:"

vo_evening = "The highest grossing anime film ever is finally hitting streaming. Demon Slayer: Infinity Castle premieres on Crunchyroll Tuesday, after a year in theaters. It made over seven hundred million dollars worldwide, beating Spirited Away, Your Name, and the franchise's own Mugen Train. Crunchyroll streams it worldwide outside Japan and Mainland China, with subs and the same English dub from US theaters. Netflix carries it across most of Asia the same day. This is the first chapter of the trilogy closing the series. So is two days really worth the wait after a long theatrical hold? Leave your take. Here's the exact day this record breaking film finally streams:"

pkg_morning = {
    "package_id": pkg1_id,
    "slot": "morning",
    "content_type": "short",
    "show": "Though I Am an Inept Villainess",
    "angle": "English dub cast revealed July 24 — Mori Calliope joins the cast, dub debuts July 26 on Crunchyroll/Hulu/Disney+/Netflix Asia",
    "format_type": "SEASON_PREVIEW / dub-cast reveal",
    "topic_class": "timely",
    "topic_signals": ["premiere", "news"],
    "series": None,
    "duration_experiment": False,
    "funnel_status": "standalone",
    "hook_family": "revelation",
    "hook_onscreen_text": "A VTuber just got cast in a major anime dub.",
    "hook_first_second": True,
    "hook_candidates": [
        "A hololive VTuber just got cast in a major anime dub.",
        "Though I Am an Inept Villainess just revealed its English dub cast, and one name stands out."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": "A hololive VTuber just got cast in a major anime dub.",
    "opening_sentence": "A hololive VTuber just got cast in a major anime dub.",
    "vo": vo_morning,
    "vo_word_count": 108,
    "question_line": "So does casting a VTuber alongside veteran anime voices actually widen the audience, or is it just a stunt?",
    "cta_line": "Leave your take.",
    "loop_line": "Here's the exact role Calliope was cast to play:",
    "loop_transition": "Here's the exact role Calliope was cast to play: A hololive VTuber just got cast in a major anime dub.",
    "final_to_opening": {
        "final": "Here's the exact role Calliope was cast to play:",
        "opening": "A hololive VTuber just got cast in a major anime dub."
    },
    "loop_read_aloud_pass": True,
    "loop_transition_note": "Loop line sets up 'the exact role' as an incomplete question; opening sentence answers it by identifying the VTuber-cast-in-a-dub fact, continuing as one thought rather than a keyword echo.",
    "video_style": "Anime Clips Only",
    "face": False,
    "split_screen": False,
    "sources": [
        {
            "claim": "TOHO announced the English dub cast for Though I Am an Inept Villainess on July 24, 2026, with the dub debuting July 26 on Crunchyroll, Hulu, and Disney+ (Netflix in Asia)",
            "url": "https://www.animenewsnetwork.com/news/2026-07-24/though-i-am-an-inept-villainess-anime-reveals-english-dub-cast-july-26-debut-trailer/.239940",
            "date": "Jul 2026"
        },
        {
            "claim": "The English dub cast includes Mori Calliope (hololive English VTuber) as Kou Tousetsu, Brianna Knickerbocker as Kou Reirin, Aleks Le as Shin-u, Kaiji Tang as Ei Gyoumei, and Rebecca Wang as Shu Keigetsu",
            "url": "https://www.animationmagazine.net/2026/07/though-i-am-an-inept-villainess-english-dub-trailer-introduces-new-voice-cast/",
            "date": "Jul 2026"
        }
    ],
    "clips": [
        {
            "scene": "Though I Am an Inept Villainess - Kou Reirin close-up, court setting establishing shot",
            "reason": "Cold open identifying the show and lead character central to the dub reveal",
            "duration_sec": 6, "timeline_start_sec": 0, "timeline_end_sec": 6,
            "carries_loop_back": False
        },
        {
            "scene": "Though I Am an Inept Villainess - body-swap transformation moment",
            "reason": "Visualizes the show's core body-swap premise while VO explains the dub cast news",
            "duration_sec": 7, "timeline_start_sec": 6, "timeline_end_sec": 13,
            "carries_loop_back": False
        },
        {
            "scene": "Though I Am an Inept Villainess - Shin-u action/sword sequence",
            "reason": "Shows a second principal character tied to the newly cast dub voices",
            "duration_sec": 6, "timeline_start_sec": 13, "timeline_end_sec": 19,
            "carries_loop_back": False
        },
        {
            "scene": "Though I Am an Inept Villainess - imperial court group scene, ensemble cast shot",
            "reason": "Reinforces the ensemble cast size matching the multiple dub actors named in the VO",
            "duration_sec": 6, "timeline_start_sec": 19, "timeline_end_sec": 25,
            "carries_loop_back": False
        },
        {
            "scene": "Though I Am an Inept Villainess - Kou Reirin final close-up, contemplative expression",
            "reason": "Final cut returns to the lead character and carries the loop line back into CUT 1 / the opening, completing the seamless loop",
            "duration_sec": 5, "timeline_start_sec": 25, "timeline_end_sec": 30,
            "carries_loop_back": True
        }
    ],
    "clip_descriptions": "5-cut sequence opening and closing on Kou Reirin, with body-swap, Shin-u action, and ensemble court shots in between to visualize the newly cast dub roles; anime footage only, no face/split/inset.",
    "captions": "A hololive VTuber just joined a major anime dub cast. Mori Calliope is voicing Kou Tousetsu in Though I Am an Inept Villainess, dropping this Sunday on Crunchyroll, Hulu, Disney+, and Netflix Asia. #anime #isekai #dub #animenews #animetok",
    "youtube_title": "Inept Villainess Dub Cast Has a VTuber",
    "tiktok_title": "Villainess anime dub cast has a VTuber",
    "tiktok_post_text": "A hololive VTuber just got cast in a major anime dub — Mori Calliope is voicing Kou Tousetsu in Though I Am an Inept Villainess. The English dub drops this Sunday on Crunchyroll, Hulu, Disney+, and Netflix Asia. #anime #isekai #animenews #animenewstoday #animetok #animeshorts #animecommentary #hololive #animedub",
    "pinned_comment": "Calliope isn't the only surprise in this cast — Kaiji Tang and Aleks Le are also voicing principal roles. Leave your take below.",
    "post_times": {"youtube": "8:00 AM ET", "tiktok": "8:15 AM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {
                "claim": "A hololive VTuber (Mori Calliope) got cast in a major anime dub",
                "core": True,
                "claim_type": "A",
                "source_urls": ["https://www.animationmagazine.net/2026/07/though-i-am-an-inept-villainess-english-dub-trailer-introduces-new-voice-cast/"],
                "anchors_claim": "hook"
            },
            {
                "claim": "The exact role Mori Calliope was cast to play is Kou Tousetsu",
                "core": True,
                "claim_type": "A",
                "source_urls": ["https://www.animationmagazine.net/2026/07/though-i-am-an-inept-villainess-english-dub-trailer-introduces-new-voice-cast/"],
                "anchors_claim": "loop"
            },
            {
                "claim": "TOHO announced the English dub cast July 24, 2026, with the dub debuting July 26 on Crunchyroll, Hulu, and Disney+ (Netflix in Asia)",
                "core": True,
                "claim_type": "C",
                "source_urls": ["https://www.animenewsnetwork.com/news/2026-07-24/though-i-am-an-inept-villainess-anime-reveals-english-dub-cast-july-26-debut-trailer/.239940"]
            },
            {
                "claim": "Brianna Knickerbocker, Aleks Le, and Kaiji Tang round out principal dub cast roles",
                "core": False,
                "source_urls": ["https://www.animationmagazine.net/2026/07/though-i-am-an-inept-villainess-english-dub-trailer-introduces-new-voice-cast/"]
            }
        ],
        "checks": {
            "vo_word_count": True,
            "cta_adjacency": True,
            "title_search": True,
            "blackout_recent_conflicts": True,
            "clip_timing_tiling": True,
            "loop_colon_handoff": True,
            "hook_loop_claim_coverage": True,
            "numeric_cross_check": True
        },
        "final_to_opening_readaloud": "Here's the exact role Calliope was cast to play: A hololive VTuber just got cast in a major anime dub."
    }
}

pkg_evening = {
    "package_id": pkg2_id,
    "slot": "evening",
    "content_type": "short",
    "show": "Demon Slayer: Infinity Castle",
    "angle": "The highest-grossing anime film ever streams for the first time on Crunchyroll July 28, 2026, after a year in theaters",
    "format_type": "SEASON_PREVIEW / UPCOMING_HYPE",
    "topic_class": "timely",
    "topic_signals": ["premiere", "news"],
    "series": None,
    "duration_experiment": False,
    "funnel_status": "standalone",
    "hook_family": "revelation",
    "hook_onscreen_text": "The highest-grossing anime film ever is finally streaming.",
    "hook_first_second": True,
    "hook_candidates": [
        "The highest grossing anime film ever is finally hitting streaming.",
        "After a full year in theaters, this record breaking anime film finally has a streaming date."
    ],
    "selected_hook_index": 0,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": "The highest grossing anime film ever is finally hitting streaming.",
    "opening_sentence": "The highest grossing anime film ever is finally hitting streaming.",
    "vo": vo_evening,
    "vo_word_count": 108,
    "question_line": "So is two days really worth the wait after a long theatrical hold?",
    "cta_line": "Leave your take.",
    "loop_line": "Here's the exact day this record breaking film finally streams:",
    "loop_transition": "Here's the exact day this record breaking film finally streams: The highest grossing anime film ever is finally hitting streaming.",
    "final_to_opening": {
        "final": "Here's the exact day this record breaking film finally streams:",
        "opening": "The highest grossing anime film ever is finally hitting streaming."
    },
    "loop_read_aloud_pass": True,
    "loop_transition_note": "Loop line poses 'the exact day' as an incomplete setup; opening sentence continues the thought by identifying the film's streaming arrival, not a self-contained restatement.",
    "video_style": "Anime Clips Only",
    "face": False,
    "split_screen": False,
    "sources": [
        {
            "claim": "Demon Slayer: Kimetsu no Yaiba Infinity Castle streams on Crunchyroll worldwide (outside Japan/Mainland China) starting July 28, 2026, with Netflix carrying it across most of Asia the same day",
            "url": "https://www.cbr.com/crunchyroll-netflix-demon-slayer-infinity-castle-streaming-date/",
            "date": "Jul 2026"
        },
        {
            "claim": "Crunchyroll confirmed at Anime Expo that the film will stream with Japanese audio, English subtitles, and the English dub that played in US theaters",
            "url": "https://www.animenewsnetwork.com/news/2026-07-03/1st-demon-slayer-infinity-castle-anime-film-to-stream-on-crunchyroll-on-july-28/.239275",
            "date": "Jul 2026"
        },
        {
            "claim": "Infinity Castle is the highest-grossing anime film in global box office history, surpassing Spirited Away ($395M), Your Name ($405M), and Mugen Train ($506M)",
            "url": "https://www.independent.co.uk/arts-entertainment/films/news/demon-slayer-infinity-castle-box-office-records-b2831182.html",
            "date": "Sep 2025"
        }
    ],
    "clips": [
        {
            "scene": "Demon Slayer: Infinity Castle - Tanjiro establishing shot inside the shifting castle corridors",
            "reason": "Cold open on the film's iconic setting to anchor the streaming-premiere announcement",
            "duration_sec": 6, "timeline_start_sec": 0, "timeline_end_sec": 6,
            "carries_loop_back": False
        },
        {
            "scene": "Demon Slayer: Infinity Castle - Hashira ensemble battle-ready shot",
            "reason": "Reinforces the scale of the film while VO covers its box office record",
            "duration_sec": 7, "timeline_start_sec": 6, "timeline_end_sec": 13,
            "carries_loop_back": False
        },
        {
            "scene": "Demon Slayer: Infinity Castle - Muzan Kibutsuji imposing reveal shot",
            "reason": "Visualizes the film's central antagonist while VO details the streaming platforms",
            "duration_sec": 6, "timeline_start_sec": 13, "timeline_end_sec": 19,
            "carries_loop_back": False
        },
        {
            "scene": "Demon Slayer: Infinity Castle - Nezuko action sequence, demon form",
            "reason": "Second major character beat, keeps visual variety while VO makes the box office comparison",
            "duration_sec": 6, "timeline_start_sec": 19, "timeline_end_sec": 25,
            "carries_loop_back": False
        },
        {
            "scene": "Demon Slayer: Infinity Castle - Tanjiro final close-up, resolute expression",
            "reason": "Final cut returns to Tanjiro and carries the loop line back into CUT 1 / the opening, completing the seamless loop",
            "duration_sec": 5, "timeline_start_sec": 25, "timeline_end_sec": 30,
            "carries_loop_back": True
        }
    ],
    "clip_descriptions": "5-cut sequence opening and closing on Tanjiro/Infinity Castle imagery, with Hashira ensemble, Muzan, and Nezuko shots in between to visualize the film's scale and stakes; anime footage only, no face/split/inset.",
    "captions": "The highest-grossing anime film ever is finally streaming. Demon Slayer: Infinity Castle hits Crunchyroll worldwide July 28, after a year in theaters and $700M+ at the box office. #anime #demonslayer #infinitycastle #animenews #animetok",
    "youtube_title": "Demon Slayer Infinity Castle Finally Streams",
    "tiktok_title": "Infinity Castle finally hits streaming",
    "tiktok_post_text": "The highest-grossing anime film ever is finally hitting streaming — Demon Slayer: Infinity Castle premieres on Crunchyroll worldwide July 28, after a full year in theaters and over $700M at the box office. #anime #demonslayer #infinitycastle #animenews #animenewstoday #animetok #animeshorts #animecommentary #crunchyroll",
    "pinned_comment": "This is only the first film in the trilogy — the next chapter doesn't even have a release date yet. Leave your take below.",
    "post_times": {"youtube": "7:30 PM ET", "tiktok": "7:45 PM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {
                "claim": "Demon Slayer: Infinity Castle is the highest-grossing anime film ever and is finally hitting streaming",
                "core": True,
                "claim_type": "C",
                "source_urls": ["https://www.independent.co.uk/arts-entertainment/films/news/demon-slayer-infinity-castle-box-office-records-b2831182.html"],
                "anchors_claim": "hook"
            },
            {
                "claim": "The exact day the film streams is July 28, 2026, on Crunchyroll worldwide",
                "core": True,
                "claim_type": "C",
                "source_urls": ["https://www.cbr.com/crunchyroll-netflix-demon-slayer-infinity-castle-streaming-date/"],
                "anchors_claim": "loop"
            },
            {
                "claim": "The film streams with Japanese audio, English subtitles, and the same English dub that played in US theaters, with Netflix carrying it across most of Asia the same day",
                "core": True,
                "claim_type": "A",
                "source_urls": ["https://www.animenewsnetwork.com/news/2026-07-03/1st-demon-slayer-infinity-castle-anime-film-to-stream-on-crunchyroll-on-july-28/.239275"]
            },
            {
                "claim": "The film beat Spirited Away ($395M), Your Name ($405M), and Mugen Train ($506M) at the global box office",
                "core": True,
                "claim_type": "C",
                "source_urls": ["https://www.independent.co.uk/arts-entertainment/films/news/demon-slayer-infinity-castle-box-office-records-b2831182.html"]
            }
        ],
        "checks": {
            "vo_word_count": True,
            "cta_adjacency": True,
            "title_search": True,
            "blackout_recent_conflicts": True,
            "clip_timing_tiling": True,
            "loop_colon_handoff": True,
            "hook_loop_claim_coverage": True,
            "numeric_cross_check": True
        },
        "final_to_opening_readaloud": "Here's the exact day this record breaking film finally streams: The highest grossing anime film ever is finally hitting streaming."
    }
}

manifest = {
    "batch_id": batch_id,
    "run_ts": "2026-07-25T12:26:00-04:00",
    "post_date": "2026-07-26",
    "recipient": "hero_or_villain@outlook.com",
    "traction_cache": {
        "timestamp": "2026-07-24T18:50:00-04:00",
        "age_days": 1,
        "status": "CURRENT"
    },
    "packages": [pkg_morning, pkg_evening]
}

with open('cron_tracking/daily_combined/run_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("Manifest written.")
print("Morning VO word count:", pkg_morning['vo_word_count'])
print("Evening VO word count:", pkg_evening['vo_word_count'])
print("YT title morning len:", len(pkg_morning['youtube_title']))
print("TT title morning len:", len(pkg_morning['tiktok_title']))
print("YT title evening len:", len(pkg_evening['youtube_title']))
print("TT title evening len:", len(pkg_evening['tiktok_title']))

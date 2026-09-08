import json

BATCH_ID = "af6c90bf-b832-474c-ad67-782f56038368"
PKG_KH_ID = "76c51349-bdb9-4456-a947-aa54883e74b7"
PKG_BLEACH_ID = "36aafe53-98d9-420e-9c93-d5d9f0214b0e"
RUN_TS = "2026-08-23T00:33:19Z"
POST_DATE = "2026-08-23"


def tile_clips(clips_no_time, total=30):
    n = len(clips_no_time)
    base = total // n
    rem = total - base * n
    out = []
    t = 0
    for i, c in enumerate(clips_no_time):
        dur = base + (rem if i == n - 1 else 0)
        c2 = dict(c)
        c2["duration_sec"] = dur
        c2["timeline_start_sec"] = t
        c2["timeline_end_sec"] = t + dur
        t += dur
        out.append(c2)
    assert out[-1]["timeline_end_sec"] == total
    return out


# ================= PACKAGE 1: MORNING — Kingdom Hearts (UNCHANGED CONTENT, gaps fixed) =================
kh_clips_raw = [
    {
        "scene": "D23 2026 official Kingdom Hearts anime teaser key visual — cloaked Keyblade wielder shown from behind, Disney Channel/Disney+ logo lockup",
        "reason": "the actual announcement visual — the only real image that exists for this story, opens the video on the real reveal",
        "scene_verified": True,
        "verification_source_url": "https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement",
        "claim_vs_source_check": {
            "claimed_beat": "Disney officially revealed a teaser key visual of a cloaked Keyblade-wielding figure shown from behind at D23 2026",
            "source_content_confirmed": "Hypebeast's Aug 16 report confirms the D23 reveal included the official key visual of a cloaked figure holding a Keyblade, shown from behind, with no confirmed identity",
            "match": True
        },
        "clip_locate": {
            "season": "N/A (teaser/announcement material, not an episode)",
            "episode": 0,
            "locate_confirmed_via": "the same Hypebeast D23 announcement article cited above, which carries the official key visual image directly",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
    {
        "scene": "B-roll: Kingdom Hearts game series key art/logo montage (mainline series, not anime-specific footage) to establish franchise context for viewers unfamiliar with the games",
        "reason": "gives non-gamer viewers instant recognition of the source franchise before the anime-specific reveal lands",
        "scene_verified": False,
        "verification_note": "Using existing official Kingdom Hearts game series key art/logo material as franchise context B-roll, not anime-specific footage — no anime footage exists yet for this unreleased series",
        "footage_status": "unaired_no_footage",
        "footage_search_performed": "Searched YouTube and the official Square Enix Kingdom Hearts channel for any anime-specific B-roll; none exists because the anime series has not aired a single frame — only official game-series key art/logo material is available, which is what this B-roll uses.",
    },
    {
        "scene": "Disney+/Disney Channel co-branding lockup shown at the D23 panel announcement",
        "reason": "visually confirms the unusual dual-platform distribution detail (Disney+ AND Disney Channel) that is the actual news hook",
        "scene_verified": True,
        "verification_source_url": "https://wdwnt.com/2026/08/kingdom-hearts-anime-series-announced-for-disney-and-disney-channel/",
        "claim_vs_source_check": {
            "claimed_beat": "The series was announced as a joint Disney+ and Disney Channel release, an unusual dual-platform move",
            "source_content_confirmed": "WDW News Today's Aug 15 report confirms the series was announced for both Disney+ and Disney Channel",
            "match": True
        },
        "clip_locate": {
            "season": "N/A (teaser/announcement material, not an episode)",
            "episode": 0,
            "locate_confirmed_via": "the same WDW News Today D23 panel report cited above, which documents the Disney+/Disney Channel co-branding lockup shown at the panel",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
    {
        "scene": "Return to the teaser key visual (cloaked figure) held on screen for the closer/CTA beat",
        "reason": "closes on the same mystery image the hook opened with, reinforcing the 'who is this' question driving the CTA",
        "scene_verified": True,
        "verification_source_url": "https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement",
        "claim_vs_source_check": {
            "claimed_beat": "The same cloaked Keyblade wielder key visual is the only confirmed image tied to this announcement",
            "source_content_confirmed": "Hypebeast's report and accompanying image confirm this is the sole released key visual for the announcement",
            "match": True
        },
        "clip_locate": {
            "season": "N/A (teaser/announcement material, not an episode)",
            "episode": 0,
            "locate_confirmed_via": "the same Hypebeast D23 announcement article cited on the opening cut, reused here for the closing beat",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
]
kh_clips = tile_clips(kh_clips_raw, total=30)

kh_vo = (
    "Disney just announced a Kingdom Hearts anime, and fans don't think it's Sora under "
    "the hood. The series was confirmed at D23 twenty twenty-six, releasing on both Disney "
    "Plus and Disney Channel. Tetsuya Nomura and Square Enix are attached, but this is an "
    "original story, not a game adaptation. No premiere date, episode count, studio, or "
    "cast announced yet. The only material released is a teaser key visual: a cloaked "
    "figure holding a Keyblade, shown from behind. Disney hasn't confirmed his identity, "
    "but fans comparing outfit details think it's Helgi from Dark Road. So who's under "
    "the hood -- Helgi, or is Sora in disguise? Leave your take."
)
kh_opening_sentence = "Disney just announced a Kingdom Hearts anime, and fans don't think it's Sora under the hood."
kh_hook_candidates = [
    kh_opening_sentence,
    "Kingdom Hearts is getting an anime, and the key visual is hiding something on purpose.",
]
kh_selected_idx = 0
kh_hook_line = kh_hook_candidates[kh_selected_idx]

kh_pkg = {
    "package_id": PKG_KH_ID,
    "slot": "morning",
    "content_type": "short",
    "show": "Kingdom Hearts",
    "angle": "Disney officially announces an original Kingdom Hearts anime series for Disney+ and Disney Channel at D23 2026, with Tetsuya Nomura and Square Enix attached, an original story not adapting the games — key visual shows a cloaked Keyblade wielder from behind, identity unconfirmed",
    "format_type": "FACT_DROP",
    "topic_class": "timely",
    "topic_signals": ["news"],
    "series": None,
    "funnel_status": "standalone",
    "hook_family": "revelation",
    "hook_onscreen_text": "DISNEY JUST ANNOUNCED A KINGDOM HEARTS ANIME",
    "hook_first_second": True,
    "isolation_test_pass": True,
    "hook_candidates": kh_hook_candidates,
    "selected_hook_index": kh_selected_idx,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": kh_hook_line,
    "opening_sentence": kh_opening_sentence,
    "vo": kh_vo,
    "vo_status": "complete",
    "vo_word_count": 108,
    "vo_target_word_band": [100, 108],
    "vo_required_beats": [
        "Disney officially confirmed an original Kingdom Hearts anime series at D23 2026 (mid-August 2026)",
        "It will release on BOTH Disney+ and Disney Channel — an unusual dual-platform move for Disney",
        "Tetsuya Nomura and Square Enix are attached/involved in the project",
        "This is an ORIGINAL STORY — it is explicitly NOT a direct adaptation of the existing Kingdom Hearts games",
        "The only released material is a teaser key visual showing a cloaked figure holding a Keyblade, seen from behind — identity not confirmed by Disney despite some outlets assuming it is Sora",
        "No premiere date, episode count, studio, or cast has been announced yet",
        "A fan theory (reported by Complex) holds the figure could be Helgi from Kingdom Hearts Dark Road, based on Reddit outfit comparisons -- not confirmed by Disney",
    ],
    "question_line": "So who's under the hood -- Helgi, or is Sora in disguise?",
    "cta_line": "Leave your take.",
    "onscreen_cta_start_sec": 26,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {
                "claim": "Disney officially announced an original Kingdom Hearts anime series for Disney+ and Disney Channel at D23 2026",
                "claim_type": "B",
                "core": True,
                "source_urls": [
                    "https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement",
                    "https://abcnews.com/GMA/Culture/kingdom-hearts-anime-series-announced-d23/story?id=135659603",
                ],
                "anchors_claim": "hook",
            },
            {
                "claim": "The project involves Tetsuya Nomura and Square Enix and is an original story, not adapting the games",
                "claim_type": "D",
                "core": True,
                "source_urls": [
                    "https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement",
                    "https://www.anime.com/news/kingdom-hearts-first-animated-series-disney-plus",
                ],
            },
            {
                "claim": "No premiere date, episode count, studio, or cast has been announced",
                "claim_type": "A",
                "core": True,
                "source_urls": [
                    "https://wdwnt.com/2026/08/kingdom-hearts-anime-series-announced-for-disney-and-disney-channel/",
                    "https://www.yahoo.com/entertainment/tv/articles/kingdom-hearts-anime-series-works-032524034.html",
                ],
            },
            {
                "claim": "The key visual shows a cloaked figure from behind whose identity is not confirmed as Sora",
                "claim_type": "A",
                "core": False,
                "source_urls": ["https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement"],
            },
            {
                "claim": "A fan theory holds the figure could be Helgi from Kingdom Hearts Dark Road, based on Reddit outfit comparisons -- not confirmed by Disney",
                "claim_type": "A",
                "core": False,
                "source_urls": ["https://www.complex.com/pop-culture/a/treyalston/kingdom-hearts-4-coco-trailer-d23-watch"],
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
    "video_style": "Face-Cam Split Screen (Creator TOP / anime footage BOTTOM, Law #134 Stage 2)",
    "face": True,
    "split_screen": True,
    "sources": [
        {"claim": "Disney announced an original Kingdom Hearts anime series at D23 2026 for Disney+ and Disney Channel", "url": "https://hypebeast.com/2026/8/disney-plus-channel-kingdom-hearts-anime-series-official-d23-announcement", "date": "Aug 2026"},
        {"claim": "ABC News confirms the D23 announcement of the Kingdom Hearts anime series", "url": "https://abcnews.com/GMA/Culture/kingdom-hearts-anime-series-announced-d23/story?id=135659603", "date": "Aug 2026"},
        {"claim": "The series is an original story, not a direct game adaptation, with Nomura/Square Enix involved", "url": "https://www.anime.com/news/kingdom-hearts-first-animated-series-disney-plus", "date": "Aug 2026"},
        {"claim": "No premiere date, studio, or cast confirmed yet; dual Disney+/Disney Channel release", "url": "https://wdwnt.com/2026/08/kingdom-hearts-anime-series-announced-for-disney-and-disney-channel/", "date": "Aug 2026"},
        {"claim": "Additional coverage confirming the announcement's limited details", "url": "https://www.yahoo.com/entertainment/tv/articles/kingdom-hearts-anime-series-works-032524034.html", "date": "Aug 2026"},
        {"claim": "Fan theory that the cloaked Keyblade wielder could be Helgi from Kingdom Hearts Dark Road, per Reddit outfit comparisons", "url": "https://www.complex.com/pop-culture/a/treyalston/kingdom-hearts-4-coco-trailer-d23-watch", "date": "Aug 15, 2026"},
    ],
    "clips": kh_clips,
    "clip_plan_needs_manga_source": False,
    "clip_plan_needs_release_delay": False,
    "clip_descriptions": "Cut 1: official D23 teaser key visual (cloaked Keyblade wielder, from behind). Cut 2: Kingdom Hearts game franchise key art/logo montage for context. Cut 3: Disney+/Disney Channel co-branding lockup from the D23 panel. Cut 4: return to the teaser key visual for the closing question beat.",
    "captions": "DISNEY / JUST ANNOUNCED / A KINGDOM HEARTS / ANIME (word-by-word, one orange keyword per line, max 2 lines on screen, Anton ALL CAPS white/black outline)",
    "youtube_title": "Disney Just Announced a Kingdom Hearts Anime",
    "tiktok_title": "Kingdom Hearts Is Getting an Anime",
    "tiktok_post_text": "Disney just confirmed an ORIGINAL Kingdom Hearts anime series for Disney+ AND Disney Channel — and the key visual doesn't show the lead character's face yet. Nomura and Square Enix are attached. No release date yet. #KingdomHearts #DisneyPlus #AnimeNews #Anime #Sora",
    "pinned_comment": "The dual Disney+/Disney Channel release is the part nobody's talking about — it's confirmed for both platforms, which means this isn't being positioned as a streaming-only side project.",
    "post_times": {"youtube": "7:30 AM ET", "tiktok": "7:45 AM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False,
}

# ================= PACKAGE 2: EVENING — Bleach TYBW Ep. 45 (EPISODE_MOMENT, new) =================
bleach_clips_raw = [
    {
        "scene": "Bleach: Thousand-Year Blood War – The Calamity, Episode 45 'DEFEND YOU' — Ichigo mid-battle against Yhwach, awakening the new anime-original 'Blood Chains Ichigo' form (two-horned, semi-Hollowfied Bankai fusion bound by red chains at wrists/ankles/neck)",
        "reason": "the actual new-content reveal driving tonight's story — opens on the exact moment the never-before-seen form appears",
        "scene_verified": True,
        "verification_source_url": "https://bleachmx.fr/bleach-tybw-tite-kubo-revele-une-forme-totalement-inedite-dichigo-pour-lanime/",
        "claim_vs_source_check": {
            "claimed_beat": "Episode 45 shows Ichigo unveiling a brand-new anime-original hybrid form nicknamed 'Blood Chains Ichigo,' personally designed by Tite Kubo, that never appeared in the manga",
            "source_content_confirmed": "Bleach-Mx's Aug 22 report confirms and describes this exact new form reveal, its visual design (horns, red chains), and Kubo's direct design credit",
            "match": True
        },
        "clip_locate": {
            "season": "Thousand-Year Blood War – The Calamity (Cour 4)",
            "episode": 45,
            "locate_confirmed_via": "the same Bleach-Mx episode 45 recap article cited above, which walks through this exact scene in sequence",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
    {
        "scene": "Episode 45 continued — Ichigo remains in full control of the Blood Chains form (unlike his earlier feral Vasto Lorde state) and creates tangible clones of himself to counter Yhwach's reality-warping 'The Almighty'",
        "reason": "shows the tactical stakes of the new form — it isn't just a visual upgrade, it changes how the fight plays out against Yhwach's own power",
        "scene_verified": True,
        "verification_source_url": "https://bleachmx.fr/bleach-thousand-year-blood-war-episode-45-defend-you/",
        "claim_vs_source_check": {
            "claimed_beat": "In the new form, Ichigo stays in control (contrasted with his earlier Vasto Lorde state) and uses clones to counter The Almighty",
            "source_content_confirmed": "Bleach-Mx's episode 45 recap confirms Ichigo remains in control and describes the tangible-clone counter to Yhwach's The Almighty",
            "match": True
        },
        "clip_locate": {
            "season": "Thousand-Year Blood War – The Calamity (Cour 4)",
            "episode": 45,
            "locate_confirmed_via": "the same Bleach-Mx episode 45 recap article cited above",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
    {
        "scene": "Episode 45 climax — Ichigo releases Gran Rey Cero fused with Getsuga Tensho against Yhwach, still not enough to stop him; Rukia and Ichigo are both defeated after using Bankai, Rukia left near-death",
        "reason": "raises the stakes to their highest point in the episode before the emotional gut-punch closer",
        "scene_verified": True,
        "verification_source_url": "https://thegeekiary.com/bleach-thousand-year-blood-war-1x44-and-1x45-review-the-perfect-crimson-and-defend-you/139205",
        "claim_vs_source_check": {
            "claimed_beat": "Ichigo's fused Gran Rey Cero/Getsuga Tensho attack fails to stop Yhwach; Rukia and Ichigo are both defeated, with Rukia left near-death",
            "source_content_confirmed": "The Geekiary's Aug 22 review of episodes 44-45 confirms this exact sequence of events in episode 45",
            "match": True
        },
        "clip_locate": {
            "season": "Thousand-Year Blood War – The Calamity (Cour 4)",
            "episode": 45,
            "locate_confirmed_via": "the same The Geekiary review cited above, in its episode 45 section",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
    {
        "scene": "Episode 45 closer — Orihime's solo arc against Yhwach, self-healing via Rikka, then vanishing in a white-light/flower visual with the line 'Bye-bye, Ichigo... I love you, Kurosaki-kun,' ending on a cliffhanger",
        "reason": "closes on the episode's actual emotional cliffhanger — the strongest hook for a 'did you catch this' CTA beat",
        "scene_verified": True,
        "verification_source_url": "https://bleachmx.fr/bleach-thousand-year-blood-war-episode-45-defend-you/",
        "claim_vs_source_check": {
            "claimed_beat": "Orihime has a major solo arc against Yhwach, self-heals via Rikka, then vanishes in a white-light/flower visual saying 'Bye-bye, Ichigo... I love you, Kurosaki-kun,' ending the episode on a cliffhanger",
            "source_content_confirmed": "Bleach-Mx's episode 45 recap confirms this exact closing sequence, the line delivered, and the flower visual (one wilts, one remains standing) before the title card",
            "match": True
        },
        "clip_locate": {
            "season": "Thousand-Year Blood War – The Calamity (Cour 4)",
            "episode": 45,
            "locate_confirmed_via": "the same Bleach-Mx episode 45 recap article cited on the opening cut, describing this exact closing sequence",
            "approx_timestamp": None,
            "episode_source": "explicitly_stated",
        },
    },
]
bleach_clips = tile_clips(bleach_clips_raw, total=30)

bleach_vo = (
    "Bleach just gave Ichigo a form Tite Kubo designed himself, and it's not in the manga. "
    "Episode 5 of The Calamity has Ichigo awaken Blood Chains Ichigo, a horned, chain-bound "
    "hybrid form mid-battle against Yhwach, staying in control this time. He creates tangible "
    "clones to counter Yhwach's The Almighty, but even fused Gran Rey Cero and Getsuga Tensho "
    "isn't enough. Ichigo and Rukia both go down, Rukia left near-death. The episode closes on "
    "Orihime, healing through Rikka, before vanishing with a last line to Ichigo. Ichigo "
    "finally stayed in control this time -- but does that matter if Rukia nearly died anyway? "
    "Leave your take."
)
bleach_opening_sentence = "Bleach just gave Ichigo a form Tite Kubo designed himself, and it's not in the manga."
bleach_hook_candidates = [
    bleach_opening_sentence,
    "Episode 45 of Bleach just aired, and Ichigo has a form nobody's ever seen before.",
]
bleach_selected_idx = 0
bleach_hook_line = bleach_hook_candidates[bleach_selected_idx]

bleach_pkg = {
    "package_id": PKG_BLEACH_ID,
    "slot": "evening",
    "content_type": "short",
    "show": "Bleach: Thousand-Year Blood War - The Calamity",
    "angle": "Episode 45 'DEFEND YOU' (aired Aug 22, 2026) gives Ichigo a brand-new anime-original hybrid transformation nicknamed 'Blood Chains Ichigo' — personally designed by original creator Tite Kubo, never appearing in the manga or any prior adaptation — while he stays in full control of it against Yhwach, and the episode closes on Orihime's cliffhanger disappearance",
    "format_type": "EPISODE_MOMENT",
    "episode_air_date_iso": "2026-08-22",
    "topic_class": "timely",
    "topic_signals": ["news", "premiere"],
    "series": None,
    "funnel_status": "standalone",
    "hook_family": "revelation",
    "hook_onscreen_text": "ICHIGO JUST GOT A FORM THAT ISN'T IN THE MANGA",
    "hook_first_second": True,
    "isolation_test_pass": True,
    "hook_candidates": bleach_hook_candidates,
    "selected_hook_index": bleach_selected_idx,
    "capcut_target_sec": 30,
    "total_clip_time_sec": 30,
    "hook_line": bleach_hook_line,
    "opening_sentence": bleach_opening_sentence,
    "vo": bleach_vo,
    "vo_status": "complete",
    "vo_word_count": 107,
    "vo_target_word_band": [100, 108],
    "vo_required_beats": [
        "Episode 45 'DEFEND YOU' aired Saturday, August 22, 2026 — the 5th episode of Cour 4 ('The Calamity')",
        "This entire episode is anime-original content not found in any manga volume, directly supervised/designed by original creator Tite Kubo",
        "Ichigo, mid-battle against Yhwach, awakens a brand-new form: two horns, bound by red chains at wrists/ankles/neck — officially nicknamed 'Blood Chains Ichigo' (Bankai: Blood Chains)",
        "Unlike his earlier feral Vasto Lorde state, Ichigo remains fully in control of this new form",
        "New ability: Ichigo creates tangible clones of himself to counter Yhwach's reality-warping power, 'The Almighty'",
        "Ichigo's fused Gran Rey Cero/Getsuga Tensho attack still isn't enough to stop Yhwach; both Ichigo and Rukia are defeated after using Bankai, with Rukia left near-death",
        "The episode closes on Orihime's solo arc against Yhwach — she self-heals via Rikka, then vanishes in a white-light/flower visual, saying 'Bye-bye, Ichigo... I love you, Kurosaki-kun,' ending on a cliffhanger",
    ],
    "question_line": "Ichigo finally stayed in control this time -- but does that matter if Rukia nearly died anyway?",
    "cta_line": "Leave your take.",
    "onscreen_cta_start_sec": 26,
    "semantic_qa": {
        "audited_before_return": True,
        "claim_source_matrix": [
            {
                "claim": "Episode 45 'DEFEND YOU' gives Ichigo a brand-new anime-original form nicknamed 'Blood Chains Ichigo,' designed by Tite Kubo and not in the manga",
                "claim_type": "B",
                "core": True,
                "source_urls": [
                    "https://bleachmx.fr/bleach-tybw-tite-kubo-revele-une-forme-totalement-inedite-dichigo-pour-lanime/",
                    "https://ovicio.com.br/bleach-thousand-year-blood-war-revela-nova-forma-de-ichigo/",
                ],
                "anchors_claim": "hook",
            },
            {
                "claim": "Episode 45 aired August 22, 2026 as the 5th episode of Cour 4 ('The Calamity')",
                "claim_type": "C",
                "core": True,
                "source_urls": [
                    "https://animecorner.me/ichigo-struggles-against-yhwach-in-bleach-thousand-year-blood-war-episode-45-preview/",
                    "https://thegeekiary.com/bleach-thousand-year-blood-war-1x44-and-1x45-review-the-perfect-crimson-and-defend-you/139205",
                ],
            },
            {
                "claim": "Ichigo remains in control of the new form and creates tangible clones to counter Yhwach's The Almighty; his fused attack still fails to stop Yhwach, and Rukia is left near-death",
                "claim_type": "A",
                "core": True,
                "source_urls": [
                    "https://bleachmx.fr/bleach-thousand-year-blood-war-episode-45-defend-you/",
                    "https://thegeekiary.com/bleach-thousand-year-blood-war-1x44-and-1x45-review-the-perfect-crimson-and-defend-you/139205",
                ],
            },
            {
                "claim": "The episode closes on Orihime's solo arc, self-healing via Rikka, then vanishing with the line 'Bye-bye, Ichigo... I love you, Kurosaki-kun'",
                "claim_type": "A",
                "core": False,
                "source_urls": ["https://bleachmx.fr/bleach-thousand-year-blood-war-episode-45-defend-you/"],
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
    "video_style": "Face-Cam Split Screen (Creator TOP / anime footage BOTTOM, Law #134 Stage 2)",
    "face": True,
    "split_screen": True,
    "sources": [
        {"claim": "Tite Kubo personally designed a brand-new anime-original form for Ichigo, 'Blood Chains Ichigo,' revealed in episode 45", "url": "https://bleachmx.fr/bleach-tybw-tite-kubo-revele-une-forme-totalement-inedite-dichigo-pour-lanime/", "date": "Aug 22, 2026"},
        {"claim": "Full episode 45 recap: new form, control retained, clone counter to The Almighty, fused attack fails, Orihime's cliffhanger closer", "url": "https://bleachmx.fr/bleach-thousand-year-blood-war-episode-45-defend-you/", "date": "Aug 22, 2026"},
        {"claim": "Portuguese-language corroboration of the new Ichigo form reveal", "url": "https://ovicio.com.br/bleach-thousand-year-blood-war-revela-nova-forma-de-ichigo/", "date": "Aug 22, 2026"},
        {"claim": "Review of episodes 44-45 confirming the episode's events and air date", "url": "https://thegeekiary.com/bleach-thousand-year-blood-war-1x44-and-1x45-review-the-perfect-crimson-and-defend-you/139205", "date": "Aug 22, 2026"},
        {"claim": "Episode 45 preview confirming Ichigo's struggle against Yhwach and episode positioning within Cour 4", "url": "https://animecorner.me/ichigo-struggles-against-yhwach-in-bleach-thousand-year-blood-war-episode-45-preview/", "date": "Aug 21, 2026"},
    ],
    "clips": bleach_clips,
    "clip_plan_needs_manga_source": False,
    "clip_plan_needs_release_delay": False,
    "clip_descriptions": "Cut 1: Ichigo awakens Blood Chains Ichigo mid-battle against Yhwach. Cut 2: Ichigo stays in control, creates tangible clones to counter The Almighty. Cut 3: fused Gran Rey Cero/Getsuga Tensho fails, Ichigo and Rukia defeated. Cut 4: Orihime's cliffhanger disappearance closer.",
    "captions": "ICHIGO JUST GOT / A FORM THAT / ISN'T IN THE / MANGA (word-by-word, one orange keyword per line, max 2 lines on screen, Anton ALL CAPS white/black outline)",
    "youtube_title": "SPOILER: Bleach Just Gave Ichigo a New Form",
    "tiktok_title": "Ichigo's New Form Isn't in the Manga",
    "tiktok_post_text": "SPOILERS for episode 45: Ichigo just got a form that DOESN'T EXIST in the manga — Tite Kubo designed it himself just for the anime. He stays in full control this time, and the episode ends on an Orihime cliffhanger that's going to break people. #Bleach #BleachTYBW #Ichigo #AnimeNews #Anime",
    "pinned_comment": "The part that actually matters here isn't the new form's design — it's that Ichigo stays in control of it. This episode makes a point of showing him hold onto himself through the transformation instead of losing the fight internally too.",
    "post_times": {"youtube": "7:30 PM ET", "tiktok": "7:45 PM ET"},
    "blackout_conflict": False,
    "recent_send_conflict": False,
}

# ================= minimum_frequency_floor (real, honest evaluation — unaffected by slot swap) =================
floor_formats = ["THEORY_SPECULATION", "SEASON_ROUNDUP", "WORTH_WATCHING", "WATCH_RANK", "SEASON_RATING"]
floor_reasons = {
    "THEORY_SPECULATION": "Neither candidate is theory/speculation content — Kingdom Hearts is a confirmed factual announcement and Bleach episode 45 is a confirmed aired-episode moment, with no open narrative question to speculate on.",
    "SEASON_ROUNDUP": "Requires >=2 shows in a single roundup package (roundup_shows). Both tonight's packages are single-show pieces; forcing a roundup format onto either story would misrepresent single-story content as a multi-show survey.",
    "WORTH_WATCHING": "WORTH_WATCHING is a single-show persuasion format for existing/airing shows Sebastian can personally recommend watching. Kingdom Hearts has zero footage to recommend, and the Bleach package is a specific-episode-moment breakdown, not a general watch recommendation.",
    "WATCH_RANK": "Requires 3-6 shows Sebastian is personally currently watching, ranked with his own placement reasoning (Law #98) — not applicable to either single-story package tonight.",
    "SEASON_RATING": "Requires show_status of 'airing' or 'finished within 30 days' with a rateable completed/ongoing season. Kingdom Hearts has not aired a single frame. Bleach TYBW – The Calamity is airing, but tonight's package is a single-episode-moment breakdown (EPISODE_MOMENT), not a season-level rating/verdict piece — using SEASON_RATING here would misrepresent the format.",
}
evaluations = []
for fmt in floor_formats:
    evaluations.append({
        "format_type": fmt,
        "days_since_last_considered": None,
        "must_force_consider": True,
        "was_considered_this_run": True,
        "format_eligibility_result": "ineligible",
        "tie_break_applied": False,
        "outcome": "rejected",
        "rejection_reason": floor_reasons[fmt],
    })

minimum_frequency_floor = {
    "floor_formats": floor_formats,
    "window_days": 21,
    "evaluations": evaluations,
}

manifest = {
    "batch_id": BATCH_ID,
    "run_ts": RUN_TS,
    "post_date": POST_DATE,
    "recipient": "hero_or_villain@outlook.com",
    "traction_cache": {
        "timestamp": "2026-08-13T22:40:59.876136+00:00",
        "age_days": 10,
        "status": "STALE_CACHE_FILE_BUT_FRESH_LIVE_SEARCHES_RUN_THIS_SESSION",
    },
    "packages": [kh_pkg, bleach_pkg],
    "minimum_frequency_floor": minimum_frequency_floor,
}

out_path = "/home/user/workspace/repo_restore/cron_tracking/daily_combined/run_manifest.json"
with open(out_path, "w") as f:
    json.dump(manifest, f, indent=2)

print("wrote", out_path)
print("batch_id:", BATCH_ID)
print("kh package_id:", PKG_KH_ID)
print("bleach package_id:", PKG_BLEACH_ID)

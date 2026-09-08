# VO Fact Package — Batch da1a6d5f (Aug 24, 2026)

Manual trigger of the daily_combined dual package for tomorrow's post_date (2026-08-24). Both packages are drafted through the pre-VO gate: clip plans, sources, hooks, titles, and captions are complete. **VO text is intentionally NOT written** — `vo_status: "pending"` on both, per the standing Claude-writes-VO workflow. This file gives you everything needed to write both scripts.

**Validator result:** `python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json` → **RESULT: PARTIAL — 16 check(s) skipped pending VO; DO NOT SEND, DO NOT APPROVE — EXIT CODE: 3** (as expected). Zero real FAILs. All 16 skips are exclusively the VO-dependent checks (`vo_word_count`, `VO within 100-108 words`, `question immediately followed by CTA in VO`, `exact CTA phrase present in VO`, `opening_sentence is the VO's exact first sentence`, `VO contains no banned word 'bro'`, `hook_line equals opening_sentence`, and the 5 `semantic_qa.checks` VO-dependent keys, etc.) — no non-VO mechanical check failed.

**Conflict check (double-method, re-confirmed live tonight against the real send log):**
- **One Piece** — grep + full-record substring scan of `sent_scripts_log.json` / `sent_scripts_events.jsonl`: most recent send Aug 9, 2026 ("Ch. 1190: Imu Finally Bleeds"). This package covers Chapter 1191 — a distinct, later beat, 15 days out. Clean.
- **Skeleton Knight in Another World S2** — most recent send July 15, 2026 (same-day-dub angle). This package covers the Episode 7 name-reveal — a completely different angle, 40 days out. Clean.

**post_date explicitly confirmed present:** `"post_date": "2026-08-24"` on the manifest (verified directly in the built JSON, not assumed) — closing the F58 gap where a missing post_date silently disables date-blackout signals.

**Two real mechanical gaps found and fixed this run** (surfacing per your standing rule, not silently patched):
1. **Stale video-style pattern.** The build script's Skeleton Knight package still used the old `"Anime Clips Only (anime footage only; no face/split/inset)"` pattern with `face=False, split_screen=False`. Law #134 (2026-08-09, STAGE 1 REBUILD) inverted this months ago — face-cam split-screen (creator top / anime footage bottom) is now the required default for all Shorts. Fixed on both packages to `face=True, split_screen=True` with the correct `video_style` string.
2. **Missing newer schema fields.** Both packages were missing fields added by laws after the script was last touched: `claim_type` (Law #58) on every core `claim_source_matrix` entry, `clip_locate` (Law #73 UPDATE 5) on every `scene_verified=true` clip, and `footage_status`/`footage_search_performed` (Law #73 UPDATE 8) on every `scene_verified=false` clip. Also had to reformat both packages' `clip_descriptions` into the "CUT N — X sec (start–end): scene — why" format with a literal "S{season}E{episode}" token per verified cut (Law #73 UPDATE 6), and remove a stray "Cuts 1-4" reference in the evening package's closing sentence that the CUT-segment splitter was mis-parsing as a 6th segment (over-split false trip, not a real content issue).

---

## Package 1 (Morning) — One Piece, Chapter 1191

**Format type:** THE_MOMENT
**Topic class:** timely (currently airing / same-week chapter release)
**YouTube title:** One Piece Ch. 1191: Imu Just Changed Shape
**TikTok title:** One Piece Just Made Imu Transform
**Target VO word band:** 100–108 words, ~104 target (standard law; no duration_experiment on this package)

### Hook candidates
1. **[SELECTED]** "One Piece Chapter 1191 just did something Imu has never done in over 1,100 chapters: transform mid-fight."
2. "Gaban told Luffy to run from Imu. Luffy didn't. And Chapter 1191 just showed you why he was right not to."

### Question line
"Is Loki showing up enough to actually turn this fight, or is Imu still three steps ahead?"
(followed immediately by the exact CTA phrase: "Leave your take.")

### Sourced beats (chronological, for VO drafting)
1. Chapter 1191, titled "There's Still Loki," released Sunday, Aug 23, 2026, in Weekly Shonen Jump Issue #39 — same-day via Manga Plus/Viz. ([Game Rant](https://gamerant.com/one-piece-manga-break-august-30/), [Dexerto](https://www.dexerto.com/anime/one-piece-chapter-1191-release-date-major-spoilers-3399495/))
2. Imu undergoes a visible transformation mid-fight: grows larger, sprouts four horns, gains black arms, a pointed goatee, a chest pendant of three horned skulls; the eye-covered rings that were spiked bracelets now encircle the waist/legs. ([Gulf News](https://gulfnews.com/entertainment/one-piece-chapter-1191-spoilers-imus-demonic-transformation-luffys-wild-recovery-can-the-trio-take-him-down-1.500644205), [Dexerto](https://www.dexerto.com/anime/one-piece-chapter-1191-release-date-major-spoilers-3399495/))
3. Imu taunts Gaban directly, referencing his God Valley past and mocking that he "only" lost an arm this time. Gaban, still one-armed from the prior chapter, tells Luffy to evacuate Elbaf. Luffy refuses. ([Yahoo Entertainment](https://www.yahoo.com/entertainment/tv/articles/one-piece-chapter-1191-spoilers-071245309.html), [Gulf News](https://gulfnews.com/entertainment/one-piece-chapter-1191-spoilers-imus-demonic-transformation-luffys-wild-recovery-can-the-trio-take-him-down-1.500644205))
4. Hajrudin punches Imu away to protect Luffy and Gaban, takes a hit from Imu's dark aura, and refuses to flee: "Even if I die, Loki is there." Loki then arrives — fulfilling the chapter's title. ([AOL](https://www.aol.com/articles/one-piece-chapter-1191-raw-090000000.html), [Dexerto](https://www.dexerto.com/anime/one-piece-chapter-1191-release-date-major-spoilers-3399495/))
5. Luffy recovers strength by eating stored food, then combines with Loki and Hajrudin into a joint attack ("Gokoku Sovereignty" / "Sovereignty of the Three Generals") against Imu. Chapter ends there. Confirmed break next week — no Chapter 1192 until Sept 6, 2026 (WSJ Issue #41). ([Game Rant](https://gamerant.com/one-piece-manga-break-august-30/), [Yahoo Entertainment](https://www.yahoo.com/entertainment/tv/articles/one-piece-chapter-1191-spoilers-071245309.html))

Non-core context (available if useful, not required in VO): this directly follows the previous chapter (Aug 8, 2026, already covered by the channel), where Gaban lost his arm to Imu.

### All dated sources
- [Game Rant — "One Piece Manga Break August 30"](https://gamerant.com/one-piece-manga-break-august-30/)
- [Gulf News — "One Piece Chapter 1191 spoilers: Imu's demonic transformation..."](https://gulfnews.com/entertainment/one-piece-chapter-1191-spoilers-imus-demonic-transformation-luffys-wild-recovery-can-the-trio-take-him-down-1.500644205)
- [Dexerto — "One Piece Chapter 1191 release date, major spoilers"](https://www.dexerto.com/anime/one-piece-chapter-1191-release-date-major-spoilers-3399495/)
- [Yahoo Entertainment — "One Piece Chapter 1191 spoilers"](https://www.yahoo.com/entertainment/tv/articles/one-piece-chapter-1191-spoilers-071245309.html)
- [AOL — "One Piece Chapter 1191 raw"](https://www.aol.com/articles/one-piece-chapter-1191-raw-090000000.html)

### Clip plan (30s edit, face-cam split-screen: creator top / anime footage bottom)
All 5 clips are manga-only (Chapter 1191 has not aired in anime form yet).

- **CUT 1 — 6 sec (0:00–0:06):** Imu's throne room / Elbaf battlefield establishing shot — cold open to set Imu and the Elbaf stakes (manga-only, Ch. 1191).
- **CUT 2 — 6 sec (0:06–0:12):** Imu mid-battle, aura/energy effects intensifying — visualizes the transformation beat, horns and black arms (manga-only, Ch. 1191).
- **CUT 3 — 6 sec (0:12–0:18):** Gaban, injured one-armed stance — visualizes his line telling Luffy to evacuate Elbaf (manga-only, Ch. 1191).
- **CUT 4 — 6 sec (0:18–0:24):** Luffy, determined refusal expression — visualizes his refusal to evacuate and recovery beat (manga-only, Ch. 1191).
- **CUT 5 — 6 sec (0:24–0:30):** Loki arriving / combo-attack imagery — payoff shot for the chapter title and the three-way combo setup (manga-only, Ch. 1191).
- **TOTAL CLIP TIME: 30 seconds.**

### Captions / TikTok / pinned comment
**Captions:** "One Piece Chapter 1191 is out and Imu just transformed mid-fight. Gaban — still down an arm from last chapter — tells Luffy to run. He doesn't. Then the chapter's title promise finally lands: Loki shows up. #OnePiece #OnePieceManga #Elbaf #Luffy #Imu #AnimeShorts"

---

## Package 2 (Evening) — Skeleton Knight in Another World Season 2

**Format type:** CHARACTER_DIVE
**Topic class:** timely (Episode 8, tied to this angle, releases same-day Aug 24)
**YouTube title:** Skeleton Knight S2: Chiyome's Real Name Is Mia
**TikTok title:** Chiyome's Real Name Just Got Revealed
**Target VO word band:** 100–108 words, ~104 target (standard law; no duration_experiment on this package)

### Hook candidates
1. **[SELECTED]** "Chiyome from Skeleton Knight in Another World isn't her real name — Episode 7 just confirmed it's a title, and her actual name is Mia."
2. "Skeleton Knight Season 2 just quietly answered a question fans have had since Chiyome showed up: that's not her name."

### Question line
"Now that Episode 8 is titled around her tragic past, how dark do you think Mia's backstory actually gets?"
(followed immediately by the exact CTA phrase: "Leave your take.")

### Sourced beats (chronological, for VO drafting)
1. Skeleton Knight in Another World Season 2, Episode 7 ("The Spirit of Chivalry Blooms at the Shinobi Village"), aired Aug 17, 2026, revealed that Chiyome's real name is Mia — "Chiyome" is a title bestowed on the most skilled of the Jinshin Clan's Six Great Ninja. ([SoapCentral](https://www.soapcentral.com/anime/skeleton-knight-another-world-season-2-episode-7-arc-finds-place-ninja-village), [MyAnimeList forum](https://myanimelist.net/forum/?topicid=2271352))
2. The reveal happens during a village festival episode; Arc and Goemon have a tug-of-war contest that ends in a draw (light beat, non-core context). ([MyAnimeList forum](https://myanimelist.net/forum/?topicid=2271352), [Reddit r/Animedubs](https://www.reddit.com/r/Animedubs/comments/1vqsezf/skeleton_knight_in_another_world_season_2_episode/))
3. Episode 7 also reveals that Danka's attacker is one of the Six Ninja — a missing member named Sasuke — whose blank expression raises questions about his motive for working with a corrupt nobleman/the pontiff. ([Reddit r/Animedubs](https://www.reddit.com/r/Animedubs/comments/1vqsezf/skeleton_knight_in_another_world_season_2_episode/), [MyAnimeList forum](https://myanimelist.net/forum/?topicid=2271352))
4. Episode 8, titled "The Sea Hears the Tale of the Tragic Kunoichi's Past," releases the same day as this post, Aug 24, 2026 — confirmed via two independent episode-listing sources. ([watch.rdd.media](https://watch.rdd.media/shows/skeleton-knight-in-another-world/season/2/episode/9/), [TVmaze](https://www.tvmaze.com/seasons/201785/skeleton-knight-in-another-world-season-2/episodes))
5. Season 2 is produced by Aura Studio, premiered July 4, 2026, and airs Saturdays — confirmed via Wikipedia, MyAnimeList, and Radio Times' full episode schedule (resolves an earlier Monday/Saturday listing discrepancy in favor of Saturday). ([Wikipedia](https://en.wikipedia.org/wiki/Skeleton_Knight_in_Another_World), [Radio Times](https://www.radiotimes.com/tv/fantasy/anime/skeleton-knight-in-another-world-season-2-release-schedule-when-are-new-episodes-on-crunchyroll/))

Non-core context (available if useful, not required in VO): per the franchise's own light-novel canon (character-background only, not a dated news claim) — Chiyome/Mia is an orphan of the beastfolk Jinshin Clan, chosen as one of the Six Ninja named after historical Japanese ninja (Mochizuki Chiyome). ([Wikipedia](https://en.wikipedia.org/wiki/Skeleton_Knight_in_Another_World))

### All dated sources
- [SoapCentral — "Skeleton Knight in Another World Season 2 Episode 7: Arc finds his place in the ninja village"](https://www.soapcentral.com/anime/skeleton-knight-another-world-season-2-episode-7-arc-finds-place-ninja-village)
- [MyAnimeList forum — Episode 7 discussion thread](https://myanimelist.net/forum/?topicid=2271352)
- [Reddit r/Animedubs — Episode 7 discussion thread](https://www.reddit.com/r/Animedubs/comments/1vqsezf/skeleton_knight_in_another_world_season_2_episode/)
- [watch.rdd.media — episode listing](https://watch.rdd.media/shows/skeleton-knight-in-another-world/season/2/episode/9/)
- [TVmaze — season episode list](https://www.tvmaze.com/seasons/201785/skeleton-knight-in-another-world-season-2/episodes)
- [Wikipedia — Skeleton Knight in Another World](https://en.wikipedia.org/wiki/Skeleton_Knight_in_Another_World)
- [Radio Times — release schedule](https://www.radiotimes.com/tv/fantasy/anime/skeleton-knight-in-another-world-season-2-release-schedule-when-are-new-episodes-on-crunchyroll/)

### Clip plan (30s edit, face-cam split-screen: creator top / anime footage bottom)
Clips 1–4 are real Episode 7 footage/recaps (Season 2, Episode 7 — confirmed explicitly via the sources above). Clip 5 is a title-matching bridge shot only (Episode 8 airs same-day with no synopsis published yet at research time).

- **CUT 1 — 6 sec (0:00–0:06):** Ninja village festival establishing shot — cold open setting the festival scene (S2E7).
- **CUT 2 — 6 sec (0:06–0:12):** Chiyome/Ariane festival scene, name-reveal dialogue beat — visualizes the Six Ninja naming and Chiyome's title reveal (S2E7).
- **CUT 3 — 6 sec (0:12–0:18):** Arc vs. Goemon tug-of-war contest — light pacing beat for mid-video variety (S2E7).
- **CUT 4 — 6 sec (0:18–0:24):** Sasuke reveal beat (Danka's attacker) — sets up the subplot Episode 8's title continues (S2E7).
- **CUT 5 — 6 sec (0:24–0:30):** Ocean/coastal establishing shot — bridges into the Episode 8 teaser (title-matching visual bridge only; Episode 8 airs same-day with no synopsis yet at research time).
- **TOTAL CLIP TIME: 30 seconds.**

### Captions / TikTok / pinned comment
**Captions:** "Skeleton Knight in Another World Season 2 just confirmed Chiyome isn't her real name — it's Mia. And Episode 8, out today, is literally titled around her tragic past. #SkeletonKnight #SkeletonKnightInAnotherWorld #Isekai #AnimeShorts #Chiyome"

**TikTok post text:** "Skeleton Knight in Another World Season 2 Episode 7 just confirmed Chiyome isn't her real name — it's a title, and her actual name is Mia. Episode 8, out today, is titled 'The Sea Hears the Tale of the Tragic Kunoichi's Past.' Full breakdown in the video. #SkeletonKnight #SkeletonKnightInAnotherWorld #Isekai #Chiyome #AnimeManga #AnimeShorts #Crunchyroll"

---

## Status / next step
Stopped exactly at the pre-VO gate as instructed: validator PARTIAL (exit 3), no email drafted, no send, no traction-cache rewrite, no git commit. This is pure research/draft output for your review. Once you paste VO text for both packages, the standard re-validation flow applies (`AWAITING_VO` → full re-run → `AWAITING_APPROVAL` only on a fully-passed run).

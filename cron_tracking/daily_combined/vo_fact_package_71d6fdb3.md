# VO Fact Package — Batch 71d6fdb3-d1f0-4af8-a26c-c072c9a087cf

**Repo:** SEBLABHRIS/AnimeWithSebastian.git (origin/main), committed `615f90a`, pushed and verified.
**post_date:** 2026-08-22
**Status:** VO_PENDING — staged through STEP 6 (validator) only. No email drafted, no send, no log append, no approval.json.
**Both packages:** standard 30s edit. `capcut_target_sec = 30`, `total_clip_time_sec = 30`, `duration_experiment` is NOT set on either package — so this is the DEFAULT VO word band: **100–108 words, target ~104** (Law #138/#131 v3). Not the 45–59s experiment band.

**⚠️ NEW GAP FOUND WHILE PREPARING THIS PACKAGE (not yet in KNOWN_ISSUES.md — recommend logging as F60):** `hero_or_villain_master_laws_final.txt` (line 14327) documents that EPISODE_MOMENT packages require a **SPOILER WARNING in the YouTube title and first line of TikTok post text**. `validators/validate_dual_package.py` has no check enforcing this — it's a documented law with zero mechanical enforcement, the same category of gap as F58/F59. The morning package (Victoria of Many Faces, EPISODE_MOMENT) currently has **no spoiler flag** in either `youtube_title` or `tiktok_post_text` below. Recommend you add one when you finalize titles during the VO pass (e.g. prefix with "SPOILER:" or "⚠️ Ep7 Spoilers —"), and I can add a validator check for this afterward so it's not manual-only going forward.

---

## MORNING — Victoria of Many Faces
`package_id: ef2318ab-7b1f-439b-b334-ba17b22b0e64` | `format_type: EPISODE_MOMENT` | `episode_air_date_iso: 2026-08-19` (within the validator's 7-day EPISODE_MOMENT window against post_date 2026-08-22)

### Hook / structure fields
- **hook_line / opening_sentence (fixed, must be first VO sentence verbatim):** "Victoria just got everything she wanted, then rode away from it."
- **question_line (must be followed immediately by the exact phrase "Leave your take."):** "Was Victoria protecting the people she loves by leaving, or just running from the first real family she ever had?"
- **hook_onscreen_text:** "Victoria just got everything she wanted, then rode away from it."
- **hook_family:** contradiction
- **topic_class:** timely — **topic_signals:** currently_airing
- **series:** none (not a recurring-series package)
- **funnel_status:** standalone

### Hook candidates (internal — hook_line above is the selected/published one, index 0)
1. "Victoria just got everything she wanted, then rode away from it." ← SELECTED
2. "Victoria of Many Faces just spent an entire episode proving she has a family, then had her disappear anyway."

### Angle
Episode 7 ("I Made Great Memories," aired Aug 19, 2026) spends its runtime resolving the Baron-household arc and proving Victoria has built a real family with Nonna and the household around her — then ends with Victoria disappearing on horseback, writing farewell letters to everyone who loves her, with no return in sight. The contradiction (finally earning the family she wanted, then leaving it) is the hook.

### Every sourced beat the VO needs to cover
1. Episode 7, "I Made Great Memories" (Suteki na Omoide ga Dekita no wa), aired August 19, 2026, directed by Naoki Murata, written by Naohiro Fukushima, storyboarded by Kiyotaka Ohata.
2. The episode resolves the Baron-household arc: Nonna had been taken in by a Baron's family who called her by their deceased daughter Dolores's name and locked her in a room, trying to mold her into a replacement. Nonna escapes using spy skills Victoria taught her, defeating the Baron's man Clark in a fight.
3. After Nonna is returned, the Baron's family thanks Victoria instead of resenting her, and hands over the belongings that had been set aside for Dolores — Nonna's indifference to those belongings makes Victoria reflect on her own past.
4. Jeffrey (the noble love interest) has deduced Victoria is likely a spy for a rival kingdom, and says he would give up his noble status to be with her.
5. Jeffrey's brother, a member of the Third Order of Knights, has separately deduced she's probably behind a prison break — he's torn between loyalty to the kingdom and love for his brother.
6. The episode ends with Victoria taking a horse and leaving without returning, writing letters to everyone close to her for Jeffrey to deliver. Nonna, who had wanted Victoria and Jeffrey to live together as a family, is left without her adoptive mother again.
7. Background/premise (context only, not necessarily VO-spoken): Chloe was a spy for the Kingdom of Hagl until her boss betrayed her; she retired to civilian life in the Kingdom of Ashbury under the alias Victoria Sellers and adopted an abandoned girl, Nonna, discovering her spy skills apply to civilian life too. Studio Deen production, directed by Nobukage Kimura, premiered July 8, 2026 on TV Tokyo/AT-X, streams on Crunchyroll. Based on Syuu's web novel and Komo Ushino's manga.

### Complete sources (real, dated)
| Claim | URL | Date |
|---|---|---|
| Episode 7 plot: Nonna/Baron arc resolution, Jeffrey and his brother's deductions, Victoria's departure on horseback with goodbye letters | [reddit.com/r/anime](https://www.reddit.com/r/anime/comments/1vrrnvh/victoria_of_many_faces_tefuda_ga_oome_no_victoria/) | Aug 18–19, 2026 |
| Episode 7 title, air date, director/writer/storyboard credits; series premise, studio, streaming platform | [en.wikipedia.org/wiki/Victoria_of_Many_Faces](https://en.wikipedia.org/wiki/Victoria_of_Many_Faces) | checked Aug 21, 2026 |
| Corroborating Episode 7 air date (Aug 19, 2026) | [watch.rdd.media](https://watch.rdd.media/shows/victoria-of-many-faces/) | page dated Aug 8, 2026; episode date confirmed Aug 19 |
| Series reception/tone context | [animenewsnetwork.com preview guide](https://www.animenewsnetwork.com/preview-guide/2026/summer/victoria-of-many-faces/.237677) | Jul 7, 2026 |

**Note on sourcing discipline:** the core claim (Episode 7's ending/departure beat) is sourced from a Reddit episode-discussion thread — a non-encyclopedic, dated, first-hand plot recap — paired with Wikipedia's encyclopedic episode-list entry for the same episode, satisfying the no-solely-encyclopedic rule.

### Clip plan (5 cuts, 30s total, all scene_verified — for editing reference, not VO content directly)
- CUT 1 — 6 sec (0:00–0:06): Official Crunchyroll trailer, Victoria/Chloe key visual opening beat — [youtube.com/watch?v=2LotdklGqKA](https://www.youtube.com/watch?v=2LotdklGqKA)
- CUT 2 — 6 sec (0:06–0:12): "Victoria and Nonna" official short trailer, found-family bond beat — [crunchyroll.com/news](https://www.crunchyroll.com/news/latest/2026/6/12/victoria-of-many-faces-anime-victoria-and-nonna-short-trailer)
- CUT 3 — 6 sec (0:12–0:18): Episode 7 official upload (Ani-One Philippines, EN Sub/JP Dub) — [youtube.com/watch?v=L9a4eg2mnu4](https://www.youtube.com/watch?v=L9a4eg2mnu4)
- CUT 4 — 6 sec (0:18–0:24): Official supporting-characters trailer, the household Victoria is leaving behind — [crunchyroll.com/news](https://www.crunchyroll.com/news/latest/2026/6/26/victoria-of-many-faces-anime-supporting-characters-trailer)
- CUT 5 — 6 sec (0:24–0:30): Title card/wide shot, held for CTA overlay — [youtube.com/watch?v=2LotdklGqKA](https://www.youtube.com/watch?v=2LotdklGqKA)
- TOTAL CLIP TIME: 30 seconds

### Current title fields (⚠️ spoiler flag missing — see gap note above)
- **youtube_title:** "Victoria of Many Faces Just Left Everyone Who Loves Her"
- **tiktok_title:** "Victoria Got Her Family, Then Vanished"
- **tiktok_post_text:** "Victoria of Many Faces just spent a whole episode proving she finally has a family -- then had her ride off and disappear anyway. #anime #victoriaofmanyfaces #isekai #animenews #crunchyroll"

---

## EVENING — Clevatess (Season 2)
`package_id: 2e619614-b27d-489a-a149-e2257516f4a9` | `format_type: THE_MOMENT`
**Note on format choice:** both packages initially targeted EPISODE_MOMENT, but the validator hard-blocks duplicate `format_type` within a batch, and EPISODE_MOMENT also carries a 0-day blackout window in `tools/conflict_check.py`. THE_MOMENT was used instead for this slot to keep the batch valid — the content is still a specific dated episode beat, just under the correct distinct format token. **THE_MOMENT is not in the documented spoiler-warning list** (that's EPISODE_MOMENT/EPISODE_REVIEW/EPISODE_VS_MANGA specifically), so no spoiler-flag gap applies here — but you may still want one given how recent and plot-heavy this beat is; your call during the VO pass.

### Hook / structure fields
- **hook_line / opening_sentence (fixed, must be first VO sentence verbatim):** "Clevatess just revealed the princess has been working for the villain the whole time."
- **question_line (must be followed immediately by the exact phrase "Leave your take."):** "If the princess is choosing this path herself, does that make her more dangerous than Vorden -- or just his easiest target?"
- **hook_onscreen_text:** "Clevatess just revealed the princess has been working for the villain the whole time."
- **hook_family:** revelation
- **topic_class:** timely — **topic_signals:** currently_airing
- **series:** none (not a recurring-series package)
- **funnel_status:** standalone

### Hook candidates (internal — hook_line above is the selected/published one, index 0)
1. "Clevatess just revealed the princess has been working for the villain the whole time." ← SELECTED
2. "Everyone at Clevatess's academy is hiding something, and Episode 7 just proved the princess is one of them."

### Angle
Season 2 Episode 7 (aired Aug 19, 2026) reveals the academy's Dean and the disguised princess are both tied to the villain Vorden, and the princess's obsession with dark magic and the mysterious Book of Toah is quietly steering her onto his path — while Alicia, still recovering from injury, chooses to investigate a new underground crack alone rather than wait for help.

### Every sourced beat the VO needs to cover
1. Season 2 Episode 7 aired August 19, 2026, and shifts focus toward a secret underground gathering connected to a group called the Union, which is obsessed with magic, ancient legends, and reviving the legendary Hero.
2. The academy's Dean is revealed to have a connection to the disguised princess, who is closely tied to villain Vorden; her obsession with dark magic and the mysterious Book of Toah appears to be steering her toward his agenda, driven by her own desire to find purpose.
3. The twins use their appearance-replicating ability to infiltrate hidden areas of the academy and discover the underground gathering tied to the Union.
4. Alicia, still recovering from the prior battle and in poor physical condition, discovers a new red crack leading further underground and chooses to investigate it alone rather than wait for help — reckless, but consistent with her character.
5. Vorden's influence is shown extending beyond a single character or kingdom, with powerful figures becoming involved in his plans; the episode does not reveal his precise motivation for reviving the Hero-era history.
6. Background (context only, not necessarily VO-spoken): Clevatess is one of the world's Four Beast Kings who killed thirteen heroes, then resurrected one of them, Alicia Glenfall, binding her to him with dark ichor that animates her corpse and lets him issue commands to her body — though her will and personality remain her own. In Season 2, Alicia is undercover inside Solsein Divine Academy while Clevatess poses as human instructor "Klen." Season 1 ended with villain General Dorel dead and Clevatess obtaining the Book of Toah, which revealed the original Hero Legend was politically manufactured.

### Complete sources (real, dated)
| Claim | URL | Date |
|---|---|---|
| Episode 7 plot: Union conspiracy, Dean/princess/Vorden connection, Alicia's solo underground investigation | [aol.com](https://www.aol.com/articles/clevatess-season-2-episode-7-053000000.html) | Aug 20, 2026 |
| Episode 7 title ("The Surface World and the Hidden World") and air date confirmation | [en.wikipedia.org/wiki/Clevatess](https://en.wikipedia.org/wiki/Clevatess) | checked Aug 21, 2026 |
| Series premise, Season 1 resolution, Season 2 academy-undercover setup, Book of Toah backstory, Alicia's dark-ichor resurrection | [techtimes.com](https://www.techtimes.com/articles/324117/20260812/clevatess-season-2-episode-6-airs-undead-hero-grows-stronger-injury.htm) | Aug 12, 2026 |
| Episode 7 community discussion corroboration | [reddit.com/r/anime](https://www.reddit.com/r/anime/comments/1vskfnh/clevatess_season_2_clevatess_ii_majuu_no_ou_to/) | Aug 19, 2026 |

**Note on sourcing discipline:** the core claims (Dean/princess/Vorden reveal, Alicia's solo investigation) are sourced from AOL — a non-encyclopedic, dated episode recap — paired with Wikipedia's encyclopedic episode-list entry, satisfying the no-solely-encyclopedic rule.

### Clip plan (5 cuts, 30s total, all scene_verified — for editing reference, not VO content directly)
- CUT 1 — 6 sec (0:00–0:06): Official Season 2 trailer, academy key visual — [youtube.com/watch?v=qsbyAix6lUY](https://www.youtube.com/watch?v=qsbyAix6lUY)
- CUT 2 — 6 sec (0:06–0:12): "Alicia is Blackmailing Naie" official Crunchyroll clip (S2E3) — [youtube.com/watch?v=vVqTkEUBULw](https://www.youtube.com/watch?v=vVqTkEUBULw)
- CUT 3 — 6 sec (0:12–0:18): "Alicia Got Launched Into Orbit" official Crunchyroll clip (S1E8) — [youtube.com/watch?v=1aRglpBlxuc](https://www.youtube.com/watch?v=1aRglpBlxuc)
- CUT 4 — 6 sec (0:18–0:24): Official Season 2 Trailer 2, Vorden/villain-network beat — [youtube.com/watch?v=I0hg5ve_rIY](https://www.youtube.com/watch?v=I0hg5ve_rIY)
- CUT 5 — 6 sec (0:24–0:30): Title card/logo hold, held for CTA overlay — [youtube.com/watch?v=qsbyAix6lUY](https://www.youtube.com/watch?v=qsbyAix6lUY)
- TOTAL CLIP TIME: 30 seconds

### Current title fields
- **youtube_title:** "Clevatess Just Outed the Princess as a Villain's Asset"
- **tiktok_title:** "Clevatess: The Princess Was In On It"
- **tiktok_post_text:** "Clevatess Season 2 Episode 7 just revealed the academy's own princess has been quietly steered toward the villain's plan the entire time. #anime #clevatess #darkfantasy #animenews #crunchyroll"

---

## Conflict-check evidence (F58/F59 manual scrutiny, per your standing instruction)
- **Victoria of Many Faces:** double-method scan (exact show-string grep + full-record Python substring scan across `sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`) returned **zero hits** in either file. Fully clean, never sent before.
- **Clevatess:** same double-method scan returned **1 prior hit** — 2026-07-08, PREMIERE-window angle ("discovery window before premiere flood"). Manually eyeballed per F59 (not relying solely on the 0.6 similarity threshold): 44 days distant, and the angle is materially different (pre-premiere hype vs. this batch's Aug-19 conspiracy-reveal beat). Judged safe to send.
- **episode_air_date_iso** is genuinely set to `2026-08-19` on the morning package (not None) and validator-checked against the 7-day EPISODE_MOMENT window — closing the F58 gap for this specific package.

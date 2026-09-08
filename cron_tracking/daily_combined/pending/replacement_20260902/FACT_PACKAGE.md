# Fact Package — Replacement Batch (2026-09-02)

**Batch ID:** `2539246a-faec-4de1-91d8-766fbecc3a3f`
**Status:** Drafted, validator PASSED at STEP 6 preflight (exit code 3 = PARTIAL/OK-with-VO-skips, zero FAILs, 186 checks passed). **Not sent, not committed, not pushed** — staged exactly through STEP 6 per your instruction.
**Manifest location:** `cron_tracking/daily_combined/pending/replacement_20260902/run_manifest.json`

This is a **fresh pending draft, not a correction** — no `corrects_batch_id` anywhere. It replaces two of tonight's four already-sent packages on a pure content-preference basis (too manga-heavy), per F71.

## What's being replaced

| Slot | Was | New |
|---|---|---|
| Morning, post_date 2026-09-02 | Kagurabachi Ch. 130 (manga panels, `THE_MOMENT`, package `2fc49176-32b7-4166-8224-a99e5bb57dc3`) | **Re:ZERO Season 4 Episode 15** (real aired footage, `EPISODE_MOMENT`) |
| Evening, post_date 2026-09-01 | Chainsaw Man Reze Arc (`FACT_DROP`, unaired trailer only, package `337a6d2a-d5a1-4e08-b504-c19d28b2d7af`) | **Grand Blue Dreaming Season 3 Episode 9** (real aired footage, `THE_MOMENT`) |

**Untouched, no changes:** Blue Lock Ch. 359 (Batch A morning 9/1, `86e33c6a-...`) and Solo Leveling: Ragnarok (Batch B evening 9/2, `a37c63b8-...`). Original send records for all 4 original packages (Batch A `815f25ca`, Batch B `bd5bda60`) are untouched.

## Conflict check (double-method, both clean)

**Re:ZERO** — only 3 prior sends ever, none touching Episode 15 or `EPISODE_MOMENT` format:
- FACT_DROP, 2026-06-12
- SEASON_PREVIEW, 2026-08-12
- SEASON_PREVIEW, 2026-08-11 (package `d08b72b8-d1ca-4e73-9f63-8c68e36a1df2`)

**Grand Blue Dreaming** — only 3 prior sends ever, none touching Episode 9 or this specific `THE_MOMENT` episode content:
- SEASON_PREVIEW, 2026-07-06
- MANGA_VS_ANIME, 2026-07-14
- THE_MOMENT, 2026-08-18 (package `79bbef25-6967-422f-b430-31c9b9c05da5`) — this was **Episode 6**, a different episode than the one used here (Episode 9)

Verified via grep against `sent_scripts_log.json` + `sent_scripts_events.jsonl` (Method 1) and an independent Python JSON substring scan of the full log (Method 2). Both methods agree exactly — zero discrepancies.

---

## Package 1 — Re:ZERO Season 4, Episode 15 (Morning, post_date 2026-09-02)

**Format:** `EPISODE_MOMENT` | **Episode air date:** 2026-09-02 (same day — 0 days old, well inside the 7-day window)
**Angle:** Episode 15 ("A Devoted Star") reveals Reid Astrea's soul has taken over Roy Alphard's body ("Roid"). Subaru Returns by Death straight into interrogating Shaula about the Pleiades Watchtower's hidden trial rules before facing five stacked obstacles blocking the tower's top.

### Sources
1. Episode 15 (overall episode 81), titled "A Devoted Star" (一途な星), aired September 2, 2026 on TOKYO MX and other Japanese channels, part of the Recapture Arc (Cour 2) — [Mantan-Web](https://en.mantan-web.jp/e_article/20260831dog00m200054000a.html)
2. Official synopsis: Reid roams freely through the Watchtower because his soul has taken over Roy Alphard's body (remaining Sin Archbishop of Gluttony); Subaru, having Returned by Death, questions Shaula about the tower's hidden trial rules to overcome five obstacles — a demonic-beast stampede, two Sin Archbishops, a giant scorpion, and a rising black shadow — [Animate Times](https://www.animatetimes.com/news/details.php?id=1788248569)
3. Independent same-day episode write-up corroborating the Reid/Roy Alphard reveal and the Subaru/Shaula balcony confrontation — [X/Twitter reaction post](https://x.com/rezero_ice/status/2092717105476976921)

### Hook candidates (published: #1)
1. **"SPOILERS: Re:ZERO just revealed who's actually inside that body."** ← selected
2. "SPOILER WARNING: Episode 15 just confirmed Roy Alphard isn't the one you're fighting."

### Titles
- **YouTube:** SPOILER: Re:ZERO S4E15 Body Reveal
- **TikTok title:** Re:ZERO just revealed who's inside that body
- **TikTok caption:** "SPOILER for Re:ZERO Season 4 Episode 15. This episode just confirmed whose soul is actually running that body -- and Subaru still has four more threats standing between him and the truth. #ReZero #ReZeroSeason4 #AnimeManga #AnimeTok #Isekai"

### Question / CTA
"Is Subaru walking into a trial he can actually win, or another loop he doesn't see coming? Leave your take."

### Pinned comment
"Episode 15 ('A Devoted Star') aired September 2 on Crunchyroll same-day. Episode 16 is next week."

### Clip plan (30s, tiling 0→30, all real aired footage, face-cam split-screen)
- **CUT 1 — 10 sec (0:00–0:10):** Reid roaming the Watchtower, revealed to be inside Roy Alphard's body — delivers the hook.
- **CUT 2 — 12 sec (0:10–0:22):** Subaru's Return by Death and the five stacked tower obstacles — raises the stakes.
- **CUT 3 — 8 sec (0:22–0:30):** Subaru presses Shaula for the trial's hidden rules — lands the question/CTA.
- **TOTAL CLIP TIME: 30 seconds.**

### Post times
YouTube Shorts — 9:00 AM ET | TikTok — 9:15 AM ET

**VO status: pending — not written, per your instruction.**

---

## Package 2 — Grand Blue Dreaming Season 3, Episode 9 (Evening, post_date 2026-09-01)

**Format:** `THE_MOMENT`
**Angle:** Episode 9 ("Ordeals") stacks three separate personal crises — Mitarai's panicked marriage proposal, Yamamoto's Spirytus stunt gone wrong, and Nojima's bidet disaster — into the show's most chaotic single-episode pileup, while Iori quietly starts worrying about who takes over Peek a Boo once the seniors graduate.

**Important note from research:** naive searches for "Grand Blue episode 9" return Season 1 Episode 9 (2018) content by default — had to run a corrected, more specific search including "season 3" and "2026" to isolate the real current episode. Flagging this for future research passes on this show.

### Sources
1. Episode 9, officially titled "Ordeals" (受難), aired August 31, 2026 in Japan's late-night slot on TOKYO MX and BS11, with MBS airing September 1, 2026; streaming internationally on Crunchyroll — [IndiaTimes recap](https://www.indiatimes.com/trending/grand-blue-dreaming-season-3-episode-9-recap-yamamotos-unbelievable-spirytus-stunt-steals-the-show-as-mitarai-and-nojima-face-disasters/articleshow/133667310.html)
2. Official pre-air synopsis: seeing his seniors start job hunting, Iori begins considering Peek a Boo's leadership changeover; Nojima wants to become a YouTuber, Yamamoto is in love with a VTuber, and Mitarai nearly has his jaw shattered by girlfriend Rie before panicking into a marriage proposal — [Animate Times](https://www.animatetimes.com/news/details.php?id=1787627889)
3. Post-air recap confirms Yamamoto's Spirytus-bottle stunt backfires (bottle gets stuck, he ends up drunk from the setup itself) and Nojima separately triggers a bidet malfunction — [IndiaTimes recap](https://www.indiatimes.com/trending/grand-blue-dreaming-season-3-episode-9-recap-yamamotos-unbelievable-spirytus-stunt-steals-the-show-as-mitarai-and-nojima-face-disasters/articleshow/133667310.html)

### Hook candidates (published: #1)
1. **"SPOILERS: Grand Blue's newest episode ends in a proposal nobody wanted."** ← selected
2. "SPOILER WARNING: One bottle of Spirytus just wrecked Grand Blue's whole episode."

### Titles
- **YouTube:** SPOILER: Grand Blue S3E9 Proposal
- **TikTok title:** Grand Blue's newest episode ends in a proposal
- **TikTok caption:** "SPOILER for Grand Blue Dreaming Season 3 Episode 9. This episode stacks three disasters in one go -- and Mitarai's ends in a marriage proposal nobody saw coming. #GrandBlue #GrandBlueDreaming #AnimeComedy #AnimeTok #AnimeManga"

### Question / CTA
"Whose disaster was actually the worst: Mitarai's proposal, Yamamoto's Spirytus stunt, or Nojima's bidet? Leave your take."

### Pinned comment
"Episode 9 ('Ordeals') aired August 31/September 1 and is streaming now on Crunchyroll. Episode 10 is next week."

### Clip plan (30s, tiling 0→30, all real aired footage, face-cam split-screen)
- **CUT 1 — 6 sec (0:00–0:06):** Iori noticing his seniors job-hunting, starting to worry about Peek a Boo's future — sets up the quieter throughline.
- **CUT 2 — 12 sec (0:06–0:18):** Mitarai's panicked marriage proposal to Rie — delivers the hook.
- **CUT 3 — 12 sec (0:18–0:30):** Yamamoto's Spirytus stunt and Nojima's bidet disaster collide — lands the question/CTA.
- **TOTAL CLIP TIME: 30 seconds.**

### Post times
YouTube Shorts — 6:00 PM ET | TikTok — 6:15 PM ET

**VO status: pending — not written, per your instruction.**

---

## Validator result

```
RESULT: PARTIAL — 16 check(s) skipped pending VO; DO NOT SEND, DO NOT APPROVE
```

Zero FAILs across 186 mechanical checks. All 16 skips are exactly the VO-dependent checks (word count, CTA adjacency in VO text, hook-claim coverage in VO, numeric cross-check, AI-slop pattern check) that cannot be evaluated before VO text exists — this is the same PARTIAL/exit-3 state used by prior VO-pending batches (e.g. `8ca83216`). No commit, no push, no send — staged exactly through STEP 6 as instructed.

## Next step

Once you write the VO for each package (100–108 words, ending on the question line + exact CTA "Leave your take."), I can drop it into the manifest, re-run the validator for the full audit (VO word count, CTA adjacency, hook-claim coverage, etc.), and stage it for your final send approval.

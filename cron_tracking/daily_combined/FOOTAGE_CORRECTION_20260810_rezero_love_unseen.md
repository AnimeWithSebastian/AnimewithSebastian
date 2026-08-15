# Footage-location correction sends — 2026-08-10 tonight

**Batch:** `79531612-04d5-4caa-94da-d05490ff994d` (original daily_combined run, post_date 2026-08-11)
**Packages corrected:** morning `d08b72b8-d1ca-4e73-9f63-8c68e36a1df2` (Re:ZERO Season 4 Part 2, SEASON_PREVIEW), evening `6b7ad021-c808-4f52-80c7-a6b697182fba` (Love Unseen Beneath the Clear Night Sky, WORTH_WATCHING)

## What this is

Two correction emails, sent as separate messages (not resends of the original package emails), addressing footage-location gaps discovered during post-send investigation of both packages' `scene_verified:false` / F20-fallback clips:

- **Re:ZERO correction** — original `verification_note` was correct-but-incomplete. Episode 12 has not aired (premieres 2026-08-12), so the original `scene_verified:false` calls stand. But the note omitted that real official trailer/PV footage (released 2026-08-05, containing genuine new animation — Sin Archbishops, Subaru, Pleiades Watchtower) exists and is usable as B-roll, clearly labeled as pre-release trailer material.
- **Love Unseen correction** — original `verification_note` was factually wrong, not merely incomplete. Research had stopped at a single text-only page and never checked for the aired episode itself, even though Episode 6 aired the same day (2026-08-10) the package was drafted. A full official Episode 6 upload (Ani-One India, licensed via Medialink Entertainment, 24:01 runtime) was live and findable at send time.

Both corrections are additive pointers to real, verified footage sources — they do not alter any other field in the original manifest/packages.

## Send confirmation

Two `send_email` tool calls were made (one per correction), both to `hero_or_villain@outlook.com` only:

| Correction | Subject | send_email call result |
|---|---|---|
| Re:ZERO | `CORRECTION \| MORNING \| Re:ZERO Returns With a Watchtower Mission \| August 11, 2026 \| Trailer B-Roll Pointer Added` | `status: SENT` |
| Love Unseen | `CORRECTION \| EVENING \| Love Unseen Starts With a White Cane \| August 11, 2026 \| Verification Note Was Wrong, Real Footage Located` | `status: SENT` |

## Mailbox verification (real counts, direct `search_email`)

A follow-up `search_email` call against both exact subject strings returned **4 distinct email objects** — 2 per correction, each pair sharing a thread_id, full `email_id` strings confirmed distinct, timestamps 3 seconds apart:

| Correction | Copy 1 | Copy 2 | Gap |
|---|---|---|---|
| Love Unseen | `...AAABC7jDwAAAA` @ 23:49:28 UTC | `...AAABC7i0DAAAA` @ 23:49:25 UTC | ~3 sec |
| Re:ZERO | `...AAABC7jDvAAAA` @ 23:49:10 UTC | `...AAABC7i0CAAAA` @ 23:49:07 UTC | ~3 sec |

**This is the pre-existing, already-documented F21 connector defect** (`docs/KNOWN_ISSUES.md`, "Outlook connector `send_email` intermittently dispatches one call as two"), not a new issue and not an agent-side double-send — exactly one `send_email` tool call was made per correction (confirmed via this turn's tool-call history). Same signature as all 15+ prior confirmed F21 occurrences: same subject, same body, same thread, 2 distinct `email_id`s, 2-7 seconds apart. This occurrence has been appended as a new row to the existing F21 table in `docs/KNOWN_ISSUES.md`.

## Logging decision — why `append_send_batch.py` was NOT re-run

These are **corrections to already-sent, already-logged packages** (`package_id`s `d08b72b8-...` and `6b7ad021-...` were already logged as `sent` when the original packages went out earlier tonight, batch `79531612-...`). Per the established precedent for every prior correction-resend in this project (e.g. `CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md`, `VO_CRAFT_CORRECTION_20260802_run9_onepiece_fragment_fix.md`, `JARGON_CORRECTION_20260804_bleach_cour_fix.md`), `tools/append_send_batch.py` is not re-run against an already-logged `package_id` — this dated tracking record is the designated log entry for the correction-send event instead, consistent with the `(batch_id, package_id)` dedup key already used by the durable logs.

No changes were made to `sent_scripts_log.json`, `cron_tracking/sent_scripts_events.jsonl`, or `state.json` for this correction — those already correctly reflect the original sends.

## Sources cited in the correction emails

- Re:ZERO S4P2 official trailer: https://www.youtube.com/watch?v=8ergiZBRpQI
- Re:ZERO S4P2 additional trailer upload: https://www.youtube.com/watch?v=q4V_RizFL_A
- Re:ZERO trailer content confirmation: https://mystiqora.com/rezero-season-4-part-2-trailer-episode-12-preview-revealed-and-the-recapture-arc-release-date-revealed/
- Re:ZERO S4P2 premiere date (Aug 12, 2026): https://www.radiotimes.com/tv/fantasy/anime/rezero-starting-life-in-another-world-season-4-part-2-release-schedule/, https://en.wikipedia.org/wiki/Re:Zero_season_4
- Love Unseen Episode 6 full official upload: https://www.youtube.com/watch?v=XRdBP2T1Ieg
- Love Unseen Episode 6 air date confirmation: https://en.wikipedia.org/wiki/Love_Unseen_Beneath_the_Clear_Night_Sky
- Love Unseen Crunchyroll availability: https://www.justwatch.com/us/tv-show/love-unseen-beneath-the-clear-night-sky-2026

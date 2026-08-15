# Correction-to-correction send — Re:ZERO trailer sourcing — 2026-08-10 tonight

**Batch:** `79531612-04d5-4caa-94da-d05490ff994d` (original daily_combined run, post_date 2026-08-11)
**Package corrected:** morning `d08b72b8-d1ca-4e73-9f63-8c68e36a1df2` (Re:ZERO Season 4 Part 2, SEASON_PREVIEW)
**Corrects:** the earlier tonight `FOOTAGE_CORRECTION_20260810_rezero_love_unseen.md` Re:ZERO correction email itself, not the original package email.

## What this is

A second-order correction: the first Re:ZERO footage correction (sent earlier tonight, subject `CORRECTION | MORNING | Re:ZERO Returns With a Watchtower Mission | August 11, 2026 | Trailer B-Roll Pointer Added`) itself cited two unverified sources as trailer footage:

1. `https://www.youtube.com/watch?v=8ergiZBRpQI` — titled "Re:Zero Season 4 Part 2 Official Commercial" but uploaded by "Lord D. Daemond," an unverified account with no tie to the show's official channel, Crunchyroll, or any confirmed rights-holder. "Official" was uploader-supplied title text, not a verified indicator.
2. `https://www.youtube.com/watch?v=q4V_RizFL_A` — not a trailer upload at all. It is a reaction/commentary video ("RE:ZERO SEASON 4 COUR 2 TRAILER IS ABSOLUTELY INSANE! | Reconquest Arc Trailer REACTION") from channel "Myrmonden," reacting to the real trailer rather than hosting it.

Both were accepted on title-text plausibility rather than by checking the uploading channel — the exact gap Law #73 UPDATE 8 (ported into the runtime tonight, in the same session, prior to this correction) was written to close.

**Replacement verified source:** `https://www.youtube.com/watch?v=2RqqQuy7pgo` — the real official Re:ZERO Season 4 Part 2 "Recapture Arc" PV, verified by the uploading channel's own name/branding (「Re:ゼロから始める異世界生活」チャンネル【公式】, the 【公式】 "official" marker being part of the channel identity itself, not title text). Uploaded 2026-08-05, runtime 1:13, contains real animated footage and music. Description confirms broadcast start August 12, 2026 across 21 Japanese stations plus ABEMA/dアニメストア, WHITE FOX animation credits, and links to the show's official site (re-zero-anime.jp) and official X account (x.com/Rezero_official).

Re:ZERO Season 4 Part 2 has not aired yet (premieres 2026-08-12), so this remains pre-air trailer/PV material, not aired-episode footage — that part of the original assessment was correct and unchanged. No other field in the Re:ZERO package changes; this is a sourcing correction only.

## Send confirmation

One `send_email` tool call was made, to `hero_or_villain@outlook.com` only:

| Correction | Subject | send_email call result |
|---|---|---|
| Re:ZERO (trailer source) | `CORRECTION TO CORRECTION \| Re:ZERO Trailer Source Was Wrong \| August 11, 2026 \| Replaced With Verified Official PV` | `status: SENT` |

## Mailbox verification (real counts, direct `search_email`)

A follow-up `search_email` call against the exact subject string returned **2 distinct email objects** sharing one `thread_id`, distinct `email_id` strings, timestamps ~3 seconds apart:

| Copy | email_id suffix | Timestamp (UTC) |
|---|---|---|
| 1 | `...AAABC7jDxAAAA` | 2026-08-11T01:12:39Z |
| 2 | `...AAABC7i0EAAAA` | 2026-08-11T01:12:36Z |

**This is the pre-existing, already-documented F21 connector defect** (`docs/KNOWN_ISSUES.md`, "Outlook connector `send_email` intermittently dispatches one call as two"), not a new issue and not an agent-side double-send — exactly one `send_email` tool call was made (confirmed via this turn's tool-call history). Same signature as all prior confirmed F21 occurrences tonight and earlier in the project: same subject, same body, same thread, 2 distinct `email_id`s, seconds apart. This occurrence should be appended as a new row to the existing F21 table in `docs/KNOWN_ISSUES.md`.

## Logging decision — why `append_send_batch.py` was NOT re-run

This is a **correction to an already-sent, already-logged package** (`package_id` `d08b72b8-...` was already logged as `sent` when the original package went out earlier tonight, batch `79531612-...`, and the first-order footage correction was itself logged via its own tracking doc rather than a re-run of the batch logger). Per the established precedent for every prior correction-resend in this project (e.g. `CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md`, `VO_CRAFT_CORRECTION_20260802_run9_onepiece_fragment_fix.md`, `JARGON_CORRECTION_20260804_bleach_cour_fix.md`, `FOOTAGE_CORRECTION_20260810_rezero_love_unseen.md`), `tools/append_send_batch.py` is not re-run against an already-logged `package_id` — this dated tracking record is the designated log entry for this correction-send event instead, consistent with the `(batch_id, package_id)` dedup key already used by the durable logs.

No changes were made to `sent_scripts_log.json`, `cron_tracking/sent_scripts_events.jsonl`, or `state.json` for this correction — those already correctly reflect the original sends.

## Sources cited in this correction email

- Rejected source 1 (unverified uploader): https://www.youtube.com/watch?v=8ergiZBRpQI
- Rejected source 2 (reaction video, not a trailer): https://www.youtube.com/watch?v=q4V_RizFL_A
- Verified replacement — official Re:ZERO S4P2 "Recapture Arc" PV: https://www.youtube.com/watch?v=2RqqQuy7pgo

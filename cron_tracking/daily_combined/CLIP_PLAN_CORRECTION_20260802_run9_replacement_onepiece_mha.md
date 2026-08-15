# Clip plan correction record — One Piece morning, My Hero Academia evening (replacement batch) — 2026-08-02

## Status

This is the tracking record for the "CLIP PLAN CORRECTION" send of both
replacement-batch packages (`batch_id c8401ef5-1d1e-48ce-a3f4-39443498caea`,
originally sent 2026-08-02T14:10:54Z-14:11:23Z UTC), adding a per-cut
SEASON/EPISODE LOCATION line that was confirmed missing from the original
send despite the underlying data already existing in the validated run
manifest's `clip_locate` field (generated during Law #73 clip verification).
This is the original, first-and-only correction for these package_ids — no
prior correction round touched these two packages.

## Packages corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f | Added `SEASON/EPISODE LOCATION: One Piece, Egghead/Elbaf arc, Episode 1171` to all 5 cuts, each with its own source citation (DoubleSama, FandomWire x3, Anime News Network). No VO, hook, title, captions, or other content changed. |
| My Hero Academia | evening | c8401ef5-1d1e-48ce-a3f4-39443498caea | d7c2a4b1-9e8f-4a3c-b1d2-3e4f5a6b7c8d | Added `SEASON/EPISODE LOCATION` to all 4 cuts: Cuts 1-2 -> "Season 4 (Shie Hassaikai/Overhaul arc) — specific episode number not confirmed by source, arc-only" (ComicBook.com, MHA Fandom "Rewind"); Cuts 3-4 -> "I Am a Hero Too (2026 special) — standalone, not part of the 8-season TV run" (Anime News Network Anime Expo review). Honest arc-only gap for Cuts 1-2 preserved as-is, no episode number invented. No VO, hook, title, captions, or other content changed. |

## Why no fresh research/verification was needed

The season/episode location data for every cut already existed in
`cron_tracking/daily_combined/run_manifest_20260802_v2_replacement.json`'s
`clip_locate` field for both packages, generated during the original Law #73
clip-verification pass before the initial send. The defect was that this
already-verified data was never surfaced into the email body — a formatting
omission, not a missing-verification gap. No new sources were fetched and no
claims were re-verified for this correction.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`CORRECTED_SCRIPT_SEND_20260802_run9_onepiece_mha.md` and earlier
precedents): `tools/append_send_batch.py`'s dedup key is
`(batch_id, package_id)` only. Both `b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`
and `d7c2a4b1-9e8f-4a3c-b1d2-3e4f5a6b7c8d` already carry `"status": "sent"`
rows in `sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`,
logged at the original 2026-08-02T14:10:54Z-14:11:23Z send time (committed in
`b87b5f5`/`2524d79`). Re-running the logger against these same
`(batch_id, package_id)` pairs would be a silent no-op
(`events_appended: 0`) and would NOT reflect this correction. Per explicit
user instruction this round, `sent_scripts_log.json` and
`sent_scripts_events.jsonl` are left untouched — this markdown file is the
record instead.

## Sends and mailbox verification

Both emails sent to `hero_or_villain@outlook.com` only, subject prefix
`CLIP PLAN CORRECTION | ...` (no captions changed this round, so not
`CLIP PLAN + CAPTIONS CORRECTION`). Verified via direct `search_email`
full-string `email_id` comparison immediately after sending.

| Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|
| CLIP PLAN CORRECTION \| MORNING \| One Piece \| originally sent 2026-08-02 \| One Piece Freed the One Giant Everyone Warned Against | 2026-08-02T14:25:47Z, 2026-08-02T14:25:49Z | 2 (genuine duplicate) |
| CLIP PLAN CORRECTION \| EVENING \| My Hero Academia \| originally sent 2026-08-02 \| My Hero Academia: Her Quirk Could Erase People | 2026-08-02T14:26:14Z, 2026-08-02T14:26:19Z | 2 (genuine duplicate) |

**One Piece (morning): 2 real mailbox copies — genuine F21 duplicate-dispatch
recurrence.** Two distinct full `email_id`s confirmed via direct string
comparison (`...U3DkAAAA` at 14:25:47Z and `...U3TPAAAA` at 14:25:49Z), same
`thread_id`, ~2 seconds apart. Only one `send_email` tool call was made for
this package.

**My Hero Academia (evening): 2 real mailbox copies — genuine F21
duplicate-dispatch recurrence.** Two distinct full `email_id`s confirmed via
direct string comparison (`...U3DlAAAA` at 14:26:14Z and `...U3TQAAAA` at
14:26:19Z), same `thread_id`, ~5 seconds apart. Only one `send_email` tool
call was made for this package.

Both occurrences are consistent with F21's established finding that this is
a connector/transport-side defect, not an agent-side double-send. Both have
been appended to the F21 history table in `docs/KNOWN_ISSUES.md`.

**No emails were sent to any address other than `hero_or_villain@outlook.com`.**
The original 2026-08-02T14:10:54Z-14:11:23Z copies (pre-correction content,
without season/episode location lines) were NOT re-triggered or removed —
they remain present as the honest historical record of the original send,
per explicit standing user instruction not to touch existing send records.

## Filed

Date: 2026-08-02T14:26:19Z (UTC) — set to the latest of the confirmed send
timestamps above.

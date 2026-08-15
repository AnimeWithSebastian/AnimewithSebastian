# Clip plan correction record — Bleach TYBW morning (season/episode surfacing) — 2026-08-05

## Status

This is the tracking record for the "CLIP PLAN CORRECTION" send of the Bleach:
Thousand-Year Blood War – The Calamity morning package only
(`batch_id 8f3c1e2a-9d4b-4a7f-b6c3-2e1f0a9d8c7b`,
`package_id b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7`). This is the second
correction round for this package_id (the first was the 2026-08-04 jargon
fix, `JARGON_CORRECTION_20260804_bleach_cour_fix.md`).

## What triggered this round

The user noticed neither the Bleach morning nor Solo Leveling evening sent
emails included per-cut season/episode/chapter location data, and asked for
a direct manifest check on `clip_locate` (Law #73 Update 5) for both
packages before any drafting, to determine whether this was a legitimate
absence or a rendering gap in each case.

Direct read of `cron_tracking/daily_combined/run_manifest.json` found:

- **Bleach** (`b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7`): all 5 cuts carry
  `scene_verified: true` with a complete `clip_locate` object each
  (`{"season": 4, "episode": 41, "locate_confirmed_via": "..."}`). None of
  this reached the sent email — `clip_descriptions` (the field actually
  composed into the email body) contained no season/episode label anywhere.
  **Rendering gap, not a legitimate absence.**
- **Solo Leveling** (`c2b3d4e5-f6a7-4890-b1c2-d3e4f5a6b7c8`): all 5 cuts are
  `scene_verified: false` with only a `verification_note` field — correctly,
  no `clip_locate` object exists, since the schema only generates one for
  verified clips. **Nothing was omitted; there is no location data to
  surface for this package.**

A repo-wide precedent search found this exact bug type already occurred once
before: `docs/KNOWN_ISSUES.md` documents a 2026-08-02 "CLIP PLAN CORRECTION"
resend for One Piece and My Hero Academia
(`CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md`), confirming
this is a **recurring** rendering gap, not a first occurrence, on the Bleach
package tonight.

## Root cause

No deterministic email-composer script exists anywhere in the repository
(confirmed via a repo-wide grep for compose/render/build-body style
functions — none found). `clip_descriptions` is authored as free text
directly in-context during each cron run, with no programmatic link back to
`clip_locate`. The validator (`validators/validate_dual_package.py`, lines
356–521) already checks `clip_locate` shape/presence correctly whenever
`scene_verified: true`, but has no check tying that structured data to the
actual rendered text sent in the email (lines 846–853 only check that
`clip_descriptions` is a non-empty string). This is the second time the gap
has let a verified clip's location data go unsent.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Bleach: Thousand-Year Blood War – The Calamity | morning | 8f3c1e2a-9d4b-4a7f-b6c3-2e1f0a9d8c7b | b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7 | Each of the 5 clip-plan cuts now explicitly states "SEASON 4, EPISODE 41", pulled directly from that cut's existing `clip_locate` field (`season: 4, episode: 41` on all 5 cuts). Pure surfacing fix — no new research, no other content change. VO, hook, titles, captions, TikTok text, pinned comment, post times, and sources are all unchanged from the prior (jargon-corrected) send. |

## Validator

Manifest already passed `validators/validate_dual_package.py` in its current
state before this correction (this round only changes the free-text
`clip_descriptions` field to include data the manifest already validated as
present and correctly shaped under `clip_locate` — no schema-level manifest
change was required).

## Send

Sent via the Outlook connector (`source_id: outlook`) as a plain-text
correction email to `hero_or_villain@outlook.com` only, subject:
`CORRECTION | MORNING | Bleach | 2026-08-05 | Bleach Just Benched Ichigo for Yoruichi`.
Confirmed `status: SENT`.

## F21 connector defect observed (see docs/KNOWN_ISSUES.md)

Mailbox verification via direct `search_email` with an exact-subject-string
filter found 2 distinct email objects for this send (citation_id 1 at
2026-08-05T00:51:40Z, citation_id 2 at 2026-08-05T00:51:36Z), same thread,
~4 sec apart. Only one `send_email` tool call was made this turn for this
package — this is another occurrence of the already-documented F21 Outlook
connector duplicate-dispatch defect (cosmetic mailbox duplication, not an
agent-side double-send). Logged as a new row in the F21 history table in
`docs/KNOWN_ISSUES.md`.

## Logging note

This package_id was already logged as `sent` in `sent_scripts_log.json` /
`cron_tracking/sent_scripts_events.jsonl` from the original send and the
2026-08-04 jargon-correction round. Per the same established convention as
every prior correction round on an already-logged package_id,
`tools/append_send_batch.py` was **not** re-run for this correction — this
dated tracking record serves as the append log for this round instead.

## Separately: permanent pipeline fix

This occurrence is the trigger for a proposed permanent fix (deterministic
`clip_descriptions` derivation from `clip_locate` + a new fail-closed
validator check) tracked and built separately from this correction send —
see the pipeline-fix commit and its own documentation for details. This
tracking doc covers only the Bleach correction send itself.

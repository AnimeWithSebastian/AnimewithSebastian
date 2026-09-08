# Clip plan correction record — One Piece morning, Dandadan evening — 2026-08-24

## Status

This is the tracking record for the "CLIP PLAN CORRECTION" send of both
packages in `batch_id b1f4a6c2-8e3d-4a91-9c7f-2d5e8a91c4b0` (originally sent
2026-08-24T01:17:16Z morning / 2026-08-24T01:19:08Z evening). This is a
production-script correction, not a public-facing retraction — the video for
each package has not been cut yet, so this delivers the corrected clip plan
Sebastian will actually use to edit. No prior correction round touched these
two packages.

## The bug

Both packages' fact-verification layer had already honestly flagged, per
clip, that the content is manga-only (`footage_status: "unaired_no_footage"`,
plus a `verification_note` stating no anime footage exists) and had already
set the package-level `clip_plan_needs_manga_source: true` flag. But the
actual instructed content — the `scene` field on every clip and the rendered
`clip_descriptions` text, i.e. what Sebastian is told to physically cut into
the video — still described an anime-footage substitution ("most recent
matching anime footage," "closest matching anime equivalent," "any available
anime footage/key art") instead of the real manga panel. The honesty
disclosure existed; the instructed footage choice did not follow it. This
same incorrect language went out live in both original sent emails
(`email_morning.txt`, `email_evening.txt`).

## Packages corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | b1f4a6c2-8e3d-4a91-9c7f-2d5e8a91c4b0 | e1a2b3c4-0001-4a11-9001-000000000001 | All 5 `clips[].scene` fields rewritten from anime-footage-substitution language to explicit Chapter 1191 manga panel references (opening panel, transformation panels, Gaban panel, Luffy/Hajrudin panel, Loki arrival splash panel). `clip_descriptions` rewritten to match. `scene_verified` remains `false` and `footage_status` remains `unaired_no_footage` on every cut — those fields were already honest; only the footage-source language changed. No VO, hook, title, captions, sources, or other content changed. |
| Dandadan | evening | b1f4a6c2-8e3d-4a91-9c7f-2d5e8a91c4b0 | a7e8e502-ae71-469e-a675-005049e8a78e | Same correction pattern applied to all 5 `clips[].scene` fields for Chapter 244 (Dragon Knights opening panel, surrender/Acura Blade panel, Hase/Momo hostage panel, Okarun fury panel, Kinta battle-cart arrival panel). `clip_descriptions` rewritten to match. `scene_verified`/`footage_status` unchanged (already honest). No VO, hook, title, captions, sources, or other content changed. |

## Why `scene_verified` / `footage_status` were NOT changed to a new "manga confirmed" state

An earlier draft of this correction attempted to mark these clips
`scene_verified: true` with a new, invented `footage_status` value
(`manga_panel_confirmed`) to signal the manga-panel fix. The preflight
validator correctly rejected this: `scene_verified: true` triggers Law #73's
requirement for `verification_source_url`, `claim_vs_source_check`, and
`clip_locate` — fields that describe *locating an aired anime clip*, which
does not apply here and would have had to be fabricated to pass. Rather than
force a fake pass, this was reverted. Manga-only content correctly stays
`scene_verified: false` / `footage_status: unaired_no_footage` (both true
statements — no anime footage exists) with the fix entirely inside the
`scene` / `manga_reference` / `clip_descriptions` text, which Law #73 already
recognizes as the honest disclosure path for unaired content. See the new
standing rule in `docs/PROJECT_HANDOFF.md` for the durable version of this
distinction.

## Why no fresh research/verification was needed

The manga chapter numbers, panel beats, and `manga_reference` values were
already correct and already present in the original manifest — the only
defect was the `scene` field's footage-source language. No new claims were
made and no new sources were fetched for this correction; the existing
`sources` list on both packages is unchanged.

## Files updated

- `cron_tracking/daily_combined/pending_new_manifest.json` (the real, current
  manifest for this batch)
- `cron_tracking/daily_combined/pending/b1f4a6c2-8e3d-4a91-9c7f-2d5e8a91c4b0/run_manifest.json`
  (kept byte-identical to the above)
- `docs/PROJECT_HANDOFF.md` — new standing rule #6 added to the STANDING
  COMMUNICATION AND PROCESS RULES section

Note: `cron_tracking/daily_combined/run_manifest.json` (the literal
top-level file) was intentionally NOT touched — it belongs to a different,
earlier batch (`da1a6d5f-...`, Skeleton Knight morning + a different
Dandadan chapter evening pairing), not this batch. Editing it would have
corrupted that batch's real manifest.

## Sends

Both emails sent to `hero_or_villain@outlook.com` only. See send
confirmation details logged via `tools/append_send_batch.py` for this
correction event.

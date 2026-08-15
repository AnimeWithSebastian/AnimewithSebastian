# VO craft correction record — One Piece morning (fragment-stacking fix) — 2026-08-02

## Status

This is the tracking record for the "VO CRAFT CORRECTION" send of the One
Piece morning package only (`batch_id c8401ef5-1d1e-48ce-a3f4-39443498caea`,
`package_id b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`), rewriting the VO to merge
sequential physical-action beats that had been stacked as short, staccato
fragments, per newly-added Law #149 point 6. This is the second correction
round for this package_id — the first was the CLIP PLAN CORRECTION (season/
episode location data, sent 2026-08-02T14:25:47Z-14:25:49Z, see
`CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md`). The My
Hero Academia evening package in the same batch was NOT touched this round.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f | VO rewritten (Option B of three rebuilt drafts, user-selected) to merge four consecutive non-CTA fragments ("He just stands up." / "Chains already gone." / "Weapon in hand." plus the surrounding staccato run) into flowing compound sentences, keeping every underlying fact unchanged. Closer question changed from re-asking whether Luffy's trust was justified to a forward-looking question about what Loki does next. Word count unchanged at 108 (within the 100-108 band). Hook, CTA, clip plan, season/episode location data, titles, captions, TikTok text, pinned comment, sources, and post times all unchanged from the prior correction round. |

## New law added this round: Law #149 point 6

Added to `hero_or_villain_master_laws_final.txt`, inserted between existing
point 5 and the "END Law #149" footer. This is a new point within the
existing Law #149 (VO craft), not a standalone law — it is a specific,
evidence-backed instance of point 5's existing "read as speech, not prose"
principle. Full text as approved by the user, unchanged from draft:

- Sequential physical-action beats must be merged into flowing compound/
  complex sentences rather than stacked as isolated short fragments.
- A fragment budget of at most 1 non-CTA sentence fragment per VO.
- Reject example: OP_178 (package_id `b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`,
  the original, pre-correction One Piece VO) — four consecutive non-CTA
  fragments describing a single continuous action sequence.
- Accept example: Berserk_171 (package_id
  `f2b8d9e3-5a4c-4b0f-9d2e-6f7a8b9c0d1e`) — the same category of action beat
  written as one compound sentence.

Diff shown to and approved by the user before staging.

## Why fresh research/verification was not needed

No new factual claims were introduced. The correction is a prose-craft
rewrite of already-verified facts (Hajrudin's objection, Sanji and Zoro's
reactions, Luffy freeing Loki, the silence after) — all sourced to the same
four URLs already cited in the prior correction round and unchanged here.
No new sources were fetched and no claims were re-verified for this
correction.

## Honest validator-limitation note

Ran `python3 validators/validate_dual_package.py` against the corrected
manifest (`run_manifest_20260802_v2_replacement.json`): all 156 existing
mechanical checks PASS for both packages (word count, CTA adjacency, hook/
opening_sentence consistency, clip timing tiling, sourcing, Law #73 clip
verification). The validator has **no mechanical check for fragment count or
sequential-action-beat merging** — Law #149 point 6 is brand new as of
tonight and could not be validator-enforced for this correction, only
self-audited, consistent with every other self-attested check in this
system. Self-audit result: the final VO has exactly 1 non-CTA fragment
("Luffy freed him anyway.") — within the new 1-fragment budget — versus 4
non-CTA fragments in the original.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md` and earlier
precedents): `tools/append_send_batch.py`'s dedup key is
`(batch_id, package_id)` only. `b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f` already
carries a `"status": "sent"` row in `sent_scripts_log.json` and
`cron_tracking/sent_scripts_events.jsonl`, logged at the original
2026-08-02T14:10:54Z send time. Re-running the logger against this same
`(batch_id, package_id)` pair would be a silent no-op
(`events_appended: 0`) and would not reflect this correction. Per the same
established pattern, `sent_scripts_log.json` and `sent_scripts_events.jsonl`
are left untouched — this markdown file is the record instead.

## Send and mailbox verification

Email sent to `hero_or_villain@outlook.com` only, subject `VO CRAFT
CORRECTION | One Piece | corrects fragment-stacking per new Law #149 point
6`. Verified via direct `search_email` full-string `email_id` comparison
immediately after sending.

| Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|
| VO CRAFT CORRECTION \| One Piece \| corrects fragment-stacking per new Law #149 point 6 | 2026-08-02T23:18:13Z, 2026-08-02T23:18:17Z | 2 (genuine duplicate) |

**One Piece (morning): 2 real mailbox copies — genuine F21 duplicate-dispatch
recurrence.** Two distinct full `email_id`s confirmed via direct string
comparison (`...U3DoAAAA` at 23:18:13Z and `...U3TTAAAA` at 23:18:17Z), same
`thread_id`, ~4 seconds apart. Only one `send_email` tool call was made for
this package (confirmed via this turn's tool-call history).

This occurrence is consistent with F21's established finding that this is a
connector/transport-side defect, not an agent-side double-send. It has been
appended to the F21 history table in `docs/KNOWN_ISSUES.md`.

**No emails were sent to any address other than `hero_or_villain@outlook.com`.**
The prior 2026-08-02T14:25:47Z-14:25:49Z clip-plan-correction copies (still
missing the fragment fix) were NOT re-triggered or removed — they remain
present as the honest historical record of that correction round, per
explicit standing user instruction not to touch existing send records. The
My Hero Academia evening package and its mailbox copies were not touched
this round.

## Filed

Date: 2026-08-02T23:18:17Z (UTC) — set to the latest of the confirmed send
timestamps above.

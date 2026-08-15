# Jargon correction record — Bleach TYBW morning (removed "cour") — 2026-08-04

## Status

This is the tracking record for the "JARGON CORRECTION" send of the Bleach:
Thousand-Year Blood War – The Calamity morning package only
(`batch_id 8f3c1e2a-9d4b-4a7f-b6c3-2e1f0a9d8c7b`,
`package_id b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7`). This is the first
correction round for this package_id.

The Solo Leveling evening package in the same batch was NOT touched by this
round — it had not yet been sent and remains held pending a separate,
in-progress clip-verification review (unrelated to this jargon fix).

## What triggered this round

The user pointed out that "cour" — insider anime-production jargon for a
roughly 3-month broadcast block — appeared throughout the already-sent
morning package and would not be understood by a casual viewer, violating
Law #133 (GENERAL AUDIENCE LANGUAGE STANDARD). A repo-wide check confirmed
"cour" was not on Law #133's existing banned-term list (NEET, power scaling,
nakama, waifu, canon, filler, gaslighting) — this is the gap that let it
through the original send's self-audit.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Bleach: Thousand-Year Blood War – The Calamity | morning | 8f3c1e2a-9d4b-4a7f-b6c3-2e1f0a9d8c7b | b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7 | Every instance of "cour" replaced with plain language: "final stretch" (angle, hook_onscreen_text, hook_candidates x2, hook_line, opening_sentence, VO opening sentence, tiktok_post_text, tiktok_title, clip_descriptions, two internal semantic_qa/clip audit fields) or "all season" (VO's "first time all cour" -> "first time all season", and the matching claim_source_matrix entry). VO word count changed from 108 to 108 (round-tripped through 107 mid-edit before "Calamity" — see below — was restored, landing back at 108, still within the 100-108 band). Question/CTA closer unchanged ("...Ichigo? Leave your take."). Clip plan, per-cut timings, captions, YouTube title, pinned comment (reworded from "this whole cour" to "this whole final stretch"), sources, and post times otherwise unchanged from the original send. |

## Self-caught error during this correction: "Calamity" drop

While trimming the VO to fit the word-count band after swapping in "final
stretch" (2 words) for "final cour" (2 words), an unrelated word — "Calamity"
in "the strongest **Calamity** opener yet" — was cut without any actual
justification. This was an unintentional editing slip, not a deliberate
content decision; there was no register or jargon problem with "Calamity"
(it is the story-arc's proper name, not insider-production jargon). The user
caught that the correction email's "no other content changed" claim was not
accurate as first drafted and asked for it to be resolved before sending.
"Calamity" was restored. Final word count: 108 (top of the 100-108 band).

## Validator

Re-ran `python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json`
after all edits (both the jargon fix and the Calamity restoration): **PASS**,
160/160 checks, exit code 0.

## Send

Sent via the Outlook connector (`source_id: outlook`) as a plain-text
correction email to `hero_or_villain@outlook.com` only, subject:
`CORRECTION | MORNING | Bleach: Thousand-Year Blood War – The Calamity | 2026-08-05 | "final stretch" replaces "final cour"`.
Confirmed `status: SENT`.

## F21 connector defect observed (see docs/KNOWN_ISSUES.md)

Mailbox verification via direct `search_email` found 2 distinct full
`email_id` values for this send (`...AAA-1-sQAAAA` at 2026-08-04T23:04:59Z,
`...AAA-18okAAAA` at 2026-08-04T23:05:02Z), same thread, ~3 sec apart. Only
one `send_email` tool call was made this turn for this package — this is
another occurrence of the already-documented F21 Outlook connector
duplicate-dispatch defect (cosmetic mailbox duplication, not an agent-side
double-send). Logged as a new row in the F21 history table in
`docs/KNOWN_ISSUES.md`.

## Logging note

This package_id was already logged as `sent` in `sent_scripts_log.json` /
`cron_tracking/sent_scripts_events.jsonl` from the original send earlier
today. Per the same established convention as every prior correction round
on an already-logged package_id (see the One Piece VO craft/structural
correction records from 2026-08-02), `tools/append_send_batch.py` was **not**
re-run for this correction — this dated tracking record serves as the append
log for this round instead. The manifest file itself
(`cron_tracking/daily_combined/run_manifest.json`) was edited in place to
reflect the corrected morning package text, since it is the source of truth
for what was actually sent.

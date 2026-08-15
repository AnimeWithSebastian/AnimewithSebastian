# Rewrite Send Record — Round 2 (2026-07-27, late evening)

## Status: THIS IS THE SECOND CORRECTION PASS for these 4 packages, not the first

This file records a SECOND real send of rewritten versions of the same 4 packages
already covered once before in `REWRITE_SEND_20260727_batch.md` (round 1, sent
2026-07-27T01:48–01:51 UTC). Do not read this file in isolation — read it alongside
round 1's file to understand the full history of a given package.

**Known issue in the round-1 file, not yet corrected there:** `REWRITE_SEND_20260727_batch.md`
claims 2 mailbox copies landed per email (8 total) due to a "known Outlook connector
duplicate-send behavior." A direct `search_email` mailbox check performed during this
round-2 session (2026-07-27 ~22:00 ET) found only 1 real copy of each of the 4 round-1
emails, not 2. That means round 1's "2 copies / duplicate-dispatch bug" claim is
overstated and needs its own separate correction commit to `REWRITE_SEND_20260727_batch.md`
and `INCIDENT_20260728_dr_stone_unsourced_claim.md` (both currently claim 2 copies).
This round-2 file does NOT repeat that error — see the real per-email counts logged
below, checked directly via `search_email` for round 2's own sends.

## What changed in this round, per package

- **Gachiakuta** (morning, batch_id `05138946-731b-482c-bb1b-5533c17e062b`,
  package_id `f967a456-6831-404d-934f-173c7fc4e3f2`): confirmed content-consistent
  with the round-1 sent version already in the mailbox; re-sent as-is per this
  session's authorization to ship all 4 together as one reviewed batch.
- **One Piece** (evening, same batch_id, package_id `e41804f5-3651-4f89-91ba-3e848e7578e0`):
  confirmed content-consistent with the round-1 sent version; re-sent as-is.
- **Slime S4** (morning, batch_id `794d00b8-96b5-44d5-b310-f70dff48245f`,
  package_id `a6cd0642-5205-4e4a-a66e-5dd58bd14b44`): confirmed content-consistent
  with the round-1 sent version; re-sent as-is.
- **Dr. Stone: Science Future** (evening, same batch_id, package_id
  `711db69c-6ef7-4546-9744-9725e1171793`): this is the package with substantive
  changes this round. This session's working file (`dr_stone.json`) had drifted onto
  a stale branch — built around fixing an "unsourced MAL score claim" that round 1
  had ALREADY superseded with a different, already-correct fix (Reddit/FandomWire/
  ComicBook two-sided sourcing on the "Fans are split" claim). Round 2 discovery
  process:
  1. Fetched the real, complete round-1 sent email body directly via `search_email`
     (not the truncated search snippet) as the true baseline.
  2. Confirmed via direct code read that no MAL/ANN claim exists anywhere in the
     real round-1 sent version — the session's premise for touching Dr Stone this
     round was itself based on stale content, not a real live gap.
  3. Rebuilt the package from that real round-1 baseline, changing ONLY genuinely
     new requirements introduced after round 1 shipped: added the now-required
     `onscreen_cta_start_sec: 26` field (Law #62 addendum), renamed
     `hook_loop_claim_coverage` to `hook_claim_coverage` and added the three newer
     semantic_qa checks (`source_content_verification`, `law_149_redundancy_check`,
     `ai_slop_pattern_check`) — manually re-audited against the round-1 VO text and
     all passed clean. The MAL/ANN claim was NOT reintroduced in any form; the
     round-1 Reddit/FandomWire/ComicBook sourcing is preserved unchanged.
  4. `related_video_id` was deliberately NOT added — confirmed via
     `laws/law_85_monetization_first.md` this is an optional, publish-time-only
     field used by `tools/record_publication.py`, not a pre-send manifest field,
     with 0% real usage across all 166 sent packages to date and no
     candidate-selection logic to populate it meaningfully here.
  - Full rebuilt package: `/home/user/workspace/rewrite_manifests/dr_stone_v2_rebuilt.json`
  - Validated standalone: `python3 validators/validate_dual_package.py` → PASS, exit 0
  - Validated as part of its real batch pairing (`batch_slime_drstone_v2.json`
    alongside Slime S4) → PASS, exit 0

## Why `append_send_batch.py` was not run for this round either

Same reason as round 1, confirmed again by direct code read this round:
`tools/append_send_batch.py`'s `_event_row()` hardcodes `"event": "sent"` (line 125)
and its dedup key is `(batch_id, package_id)` only (`_existing_keys_jsonl()`,
line ~148). The `main()` argparse defines only `manifest`, `--tree`, `--cron-id`,
`--emails-sent`, `--git-pushed` — no `--event-type` flag and no note-passing
parameter exist anywhere in the file. Running it against these same 4
`(batch_id, package_id)` pairs (already recorded from round 1, and in Dr Stone's
case, from the original 2026-07-26 send before that) would be a correct-but-silent
no-op: `events_appended: 0`. No code change to add a distinct "rewritten"/"corrected"
event type was authorized this round. This is the SAME unresolved backlog item as
round 1 — not a new instance of it. See round 1's file for the original backlog-item
text; it has not yet been ported to `docs/KNOWN_ISSUES.md` as a numbered F-item.

## Real send confirmations (round 2)

(Filled in immediately after send, with real search_email results — see below in
the same session. No copy counts are asserted here until independently confirmed by
a direct mailbox query for round 2's own message-ids/timestamps, given the round-1
file's overstated count.)

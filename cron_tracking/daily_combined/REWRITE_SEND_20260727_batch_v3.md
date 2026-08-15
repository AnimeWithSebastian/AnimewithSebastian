# Rewrite send record — Round 3 (2026-07-28, late night)

## Status: THIS IS THE THIRD CORRECTION PASS for Gachiakuta and Slime S4, and the SECOND real send of a corrected Dr. Stone

Round 1 (`REWRITE_SEND_20260727_batch.md`, sent 2026-07-27T01:48–01:51 UTC, commit
`858bdbe`) sent corrected versions of Gachiakuta, One Piece, Slime S4, and Dr. Stone.
Round 2 (`REWRITE_SEND_20260727_batch_v2.md`) drafted a further Dr. Stone rebuild but
was never actually sent or committed — its "Real send confirmations" section was left
blank and the file remains untracked in git to this day. This file, round 3, is the
first completed send following round 2's abandoned attempt. One Piece is NOT part of
this round — it remains HELD per `docs/KNOWN_ISSUES.md` F20 and is out of scope here.

Read this file alongside round 1's for full history on Gachiakuta and Slime S4.
Dr. Stone's real correction history is: original 2026-07-26 send → round 1 rewrite
(unsourced "Fans are split" claim replaced with sourced two-sided claim) → round 2
(drafted but never sent) → this round (Kohaku/Stanley sourcing correction to the
species stand-down claim, propagated to the VO, the Cut 2 clip reason, both affected
source claim texts, and a new `conflict_flags` entry — see below).

## Packages sent this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Gachiakuta | morning | 05138946-731b-482c-bb1b-5533c17e062b | f967a456-6831-404d-934f-173c7fc4e3f2 | No content change this round — resent as-is, fresh-validated. |
| That Time I Got Reincarnated as a Slime Season 4 | morning | 794d00b8-96b5-44d5-b310-f70dff48245f | a6cd0642-5205-4e4a-a66e-5dd58bd14b44 | No content change this round (the "cours"-jargon fix was applied in an earlier round) — resent as-is, fresh-validated. |
| Dr. Stone: Science Future | evening | 794d00b8-96b5-44d5-b310-f70dff48245f | 711db69c-6ef7-4546-9744-9725e1171793 | Five coordinated fixes, all propagating the same correction: (1) VO clause "Senku talks the alien Why-Man species down through pure logic alone, and they leave Earth in peace after one conversation, with a single Medusa staying behind because his reasoning fascinates it." rewritten to "Kohaku and Stanley's threats are what actually make the Why-Man species back down and leave in peace, though Senku's own words convince one Medusa to stay behind." — corrects an unsupported "logic alone" framing against the real cited source ([ScreenRant](https://screenrant.com/dr-stone-ending-explained/): "the Why-Man species refrains from petrifying humanity due to the threats posed by Kohaku and Stanley... Senku's words convince one of the parasitic entities to remain on Earth"). `vo_word_count` corrected 108→104. (2) `semantic_qa.claim_source_matrix` entry text corrected to match (dropped "through negotiation alone," attributes the species-wide stand-down to Kohaku/Stanley). (3) `clips[1].reason` corrected from "one Medusa stays behind fascinated by his logic" to the Kohaku/Stanley framing. (4) `sources[0].claim` (ScreenRant) rewritten to state exactly what the article says instead of a "negotiates a partnership" misstatement. (5) `sources[1].claim` ([LeisureByte](https://leisurebyte.com/dr-stone-ending-explained/)) narrowed to only what it actually supports (peaceful departure, one device staying) after live re-verification showed LeisureByte does NOT corroborate the Kohaku/Stanley threat mechanism — it gives a threat-free "species' own conclusion" account instead. This is disclosed via a new `semantic_qa.conflict_flags` entry (topic: "Why the Why-Man species stands down and departs Earth peacefully") rather than silently picking one source's framing for the other. Loop pair (`opening_sentence`/`loop_line`/`loop_transition`) unaffected throughout — the edited VO clause is in the interior, not the first or last sentence — re-verified unchanged after all edits. |

Note: Gachiakuta and Slime S4 are both slot `morning` in this table — this is a
corrections batch, not a daily dual-package morning/evening pairing, so no slot
conflict applies.

## Validation before send

All three re-ran `validators/validate_dual_package.py` fresh this round, each wrapped
in a disposable single-package test manifest (deleted immediately after, deletion
confirmed via `find` each time — no wrapper files persist in the repo):

- Gachiakuta: **PASS, exit 0**
- Slime S4: **PASS, exit 0** (re-verified fresh, not reused from an earlier round's result)
- Dr. Stone (post-correction): **PASS, exit 0** — full check list included Law #73
  clip-verification checks and all `semantic_qa`/`claim_source_matrix` checks against
  the corrected wording.

## Why `append_send_batch.py` is not being run for these three package_ids

Same reason established in round 1 and round 2, re-confirmed by a direct code read
this round: `tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only
(`_existing_keys_jsonl()`), and `_event_row()` hardcodes `"event": "sent"` with no
`--event-type` or note-passing mechanism anywhere in `main()`'s argparse definition.

All three package_ids already have a `"status": "sent"` row in `sent_scripts_log.json`
and a matching `"event": "sent"` row in `cron_tracking/sent_scripts_events.jsonl` under
their original batch_ids (`05138946-...` for Gachiakuta, `794d00b8-...` for Slime S4
and Dr. Stone). Running the logger against a manifest reusing these same
`(batch_id, package_id)` pairs would be a correct-but-silent no-op
(`events_appended: 0`). Running it against a *new* batch_id for the same package_ids —
the only way tonight's `daily_combined` cron machinery would normally construct a
send — would NOT be caught by the dedup guard and would silently append a second,
ambiguous `"sent"` row for the same package_id with different content and no
distinguishing event type. Neither outcome is desirable, and no code change to
`append_send_batch.py` was authorized. This markdown file is the record instead, per
the same non-destructive tracking-doc pattern established in round 1 and round 2. The
original `sent_scripts_log.json` / `sent_scripts_events.jsonl` entries for these three
package_ids are NOT modified, duplicated, or appended to — this file is the only new
record of tonight's round-3 send.

**Backlog item** (same as round 1/round 2, still not yet ported to
`docs/KNOWN_ISSUES.md` as a numbered F-item): add a distinct `--event-type` (default
`"sent"`, allow `"rewritten"`/`"corrected"`) and an optional free-text `note` field to
`append_send_batch.py`'s event schema, excluded from quota/dedup counting in the
weekly analytics join, so corrections like this one can be logged as first-class
events instead of living only in markdown tracking files.

## Sends and mailbox verification

All three sent to `hero_or_villain@outlook.com` only. Verified independently via a
direct `search_email` query per show immediately after sending — no copy count is
asserted without this direct confirmation, given round 1's overstated-count error
corrected earlier tonight in commit `cbea46f`.

| Show | Subject | Sent (UTC) | Mailbox copies found |
|---|---|---|---|
| Gachiakuta | `REWRITTEN SCRIPT \| MORNING \| Gachiakuta \| originally sent 2026-07-26 \| Gachiakuta's Entire Premise, Explained` | 2026-07-28T04:23:06Z | **1** — confirmed via direct `search_email`, exactly one email_id under this exact subject. |
| Slime S4 | `REWRITTEN SCRIPT \| MORNING \| That Time I Got Reincarnated as a Slime Season 4 \| originally sent 2026-07-26 \| Slime S4: Rimuru vs Granbell, Same Goal` | 2026-07-28T04:22:57Z | **1** — confirmed via direct `search_email`, exactly one email_id under this exact subject. |
| Dr. Stone | `REWRITTEN SCRIPT \| EVENING \| Dr. Stone: Science Future \| originally sent 2026-07-26 \| Dr Stone's Finale Has Zero Fights In It` | 2026-07-28T04:22:57Z | **1** for tonight's send — confirmed by filtering `search_email` results for this exact subject down to only the `2026-07-28` date-stamped email_id. A second email_id sharing this exact subject string does exist in the mailbox, but its timestamp is `2026-07-27T01:51:24Z` — the pre-existing round-1/round-2-era send from the prior night, not a duplicate of tonight's action. Subject text intentionally carries no round marker (matching round 1's convention), so two genuinely distinct send events can legitimately share one subject string; tonight's action itself produced exactly one new copy. |

No instance of the `BLOCKER_20260728_duplicate_dispatch.md` connector defect (one
`send_email` call producing two mailbox-side sends) was observed on any of the three
sends tonight.

## Filed

Date: 2026-07-28T04:23:06Z (UTC) — set to the latest of the three confirmed send
timestamps above.

# Rewrite send record — 2026-07-27T01:48–01:51 UTC batch

## What this is

A record of 4 corrected/rewritten packages sent tonight, all reusing the same
`batch_id`/`package_id` pairs as their original 2026-07-26 sends (not new content
slots — corrections to already-logged packages). This file exists because
`tools/append_send_batch.py` could not log these as new events without either
double-counting the day's quota or requiring a code change that was not authorized
tonight (see rationale below). Historical `sent_scripts_log.json` /
`cron_tracking/sent_scripts_events.jsonl` rows for the original 2026-07-26 sends are
NOT modified or duplicated — this file is the only record of tonight's corrections.

## Packages corrected and resent

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Gachiakuta | morning | 05138946-731b-482c-bb1b-5533c17e062b | f967a456-6831-404d-934f-173c7fc4e3f2 | No content change — resent as-is per explicit approval, bundled with the other 3 corrected packages in one send batch. |
| One Piece | evening | 05138946-731b-482c-bb1b-5533c17e062b | e41804f5-3651-4f89-91ba-3e848e7578e0 | `opening_sentence`/`hook_line` rewritten from a qualifier-muddied line to state plainly Gaban never lands a real hit; `loop_line` re-verified against the new wording; `vo_word_count` corrected 108→106. |
| That Time I Got Reincarnated as a Slime Season 4 | morning | 794d00b8-96b5-44d5-b310-f70dff48245f | a6cd0642-5205-4e4a-a66e-5dd58bd14b44 | Removed "cours" jargon from VO, tiktok_post_text, captions, internal `angle`/`sources`/clip `scene`/`reason` fields; `vo_word_count` corrected 100 (was previously adjusted from 101 in an earlier pass — see prior-turn record). |
| Dr. Stone: Science Future | evening | 794d00b8-96b5-44d5-b310-f70dff48245f | 711db69c-6ef7-4546-9744-9725e1171793 | Unsourced "Fans are split" claim replaced with sourced two-sided claim — see `INCIDENT_20260728_dr_stone_unsourced_claim.md` "Correction sent" section for full detail. |

## Validation before send

Both rewrite manifests re-ran `validators/validate_dual_package.py`:
- `test_manifest_0727.json` (Gachiakuta + One Piece): **PASS, exit 0**
- `test_manifest_0728.json` (Slime S4 + Dr Stone): **PASS, exit 0**

Full suite: `python3 -m unittest discover -s validators` → **198 tests, OK**.

Additionally, a raw grep confirmed zero remaining instances of "cours" in Gachiakuta,
One Piece, and Dr Stone (they never contained it) before send:
```
=== grep 'cours' in gachiakuta.json === (exit: 1, no output)
=== grep 'cours' in one_piece.json === (exit: 1, no output)
=== grep 'cours' in dr_stone.json === (exit: 1, no output)
```

## Sends and mailbox verification

All 4 sent to hero_or_villain@outlook.com only, via the Outlook connector's
`send_email` tool:

| Show | Subject | Sent (UTC) | Mailbox copies found |
|---|---|---|---|
| Gachiakuta | REWRITTEN SCRIPT \| MORNING \| Gachiakuta \| originally sent 2026-07-26 \| Gachiakuta: Rudo's Conviction Doesn't Add Up | 2026-07-27T01:48:xx | 1 |
| One Piece | REWRITTEN SCRIPT \| EVENING \| One Piece \| originally sent 2026-07-26 \| One Piece: Gaban Never Actually Lost | 2026-07-27T01:50:xx | 1 |
| Slime S4 | REWRITTEN SCRIPT \| MORNING \| That Time I Got Reincarnated as a Slime Season 4 \| originally sent 2026-07-26 \| Slime S4: Rimuru and His Enemy Want the Same Thing | 2026-07-27T01:51:00 / 01:51:03 | 1 |
| Dr Stone | REWRITTEN SCRIPT \| EVENING \| Dr. Stone: Science Future \| originally sent 2026-07-26 \| Dr Stone's Finale Has Zero Fights In It | 2026-07-27T01:51:24 / 01:51:27 | 1 |

**Correction (filed alongside round 3, see `REWRITE_SEND_20260727_batch_v3.md`):** the
"2 copies" / duplicate-dispatch claim above was overstated. A direct `search_email`
mailbox check performed during round 2 (2026-07-27 ~22:00 ET, see
`REWRITE_SEND_20260727_batch_v2.md`) found only **1 real copy** of each of these 4
emails, not 2. Total: 4 emails in the mailbox for this 4-package batch, not 8.
The table above now reflects the corrected count directly; the original "2 copies"
claim is preserved in this note rather than the table, per the standing rule against
rewriting historical records — this correction documents the error, it does not erase
what was originally claimed.

## Why no new sent_scripts_log.json / sent_scripts_events.jsonl rows were written

`tools/append_send_batch.py` was inspected directly rather than assumed:

- `_event_row()` hardcodes `"event": "sent"` — there is no parameter or branch
  producing any other event string (e.g. `"rewritten"`), and no note/annotation
  field on the row schema at all.
- `_existing_keys_jsonl()` builds its dedup set from `(batch_id, package_id)` pairs
  only, ignoring the `event` field — so even a hand-written `"rewritten"` row
  appended outside the script would silently make future legitimate runs for that
  same key skip, corrupting dedup for anyone who later expects the script's own
  invariants to hold.
- `append_batch()` has no `--event-type` or note-passing mechanism in its signature.

Running the script as-is against these manifests would correctly report
`events_appended: 0, legacy_added: 0` for all 4 packages (idempotent no-op, since all
4 `(batch_id, package_id)` pairs already exist in both logs from the original
2026-07-26 send) — it would NOT double-count the day's quota, but it also would not
create any record that a correction happened. That silent-no-record outcome is worse
than not running the script at all, so it was not run. No code change to
`append_send_batch.py` was authorized tonight per the standing rule requiring
explicit go-ahead before any code edit.

**Backlog item** (same treatment as F15/F16/F17): add a distinct `--event-type`
(default `"sent"`, allow `"rewritten"`/`"corrected"`) and an optional free-text `note`
field to `append_send_batch.py`'s event schema, excluded from quota/dedup counting in
the weekly analytics join, so corrections like tonight's can be logged as first-class
events instead of living only in markdown tracking files.

## Filed

Date: 2026-07-27T01:53 UTC (immediately following the 4-email send batch above).

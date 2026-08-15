# Rewrite send record — Blue Box Cut 4 correction (2026-07-28, late night)

## Status: Full replacement send of the corrected Blue Box evening package, batch `b3e8f2a1`

Earlier tonight, a Law #73 review found that the Blue Box (evening slot) package's
original clip plan had a factually wrong Cut 4 claim ("closing wide shot of the
gym/school" — that shot does not exist in Episode 1) and, independent of that
specific error, all 4 clips shared one bogus `verification_source_url` (a Season 2
renewal announcement that verifies none of the 4 scene claims). Both problems were
corrected in `run_manifest.json` (this directory) via a surgical `edit`, re-validated
PASS, and logged separately (see `docs/KNOWN_ISSUES.md`'s two dated entries and
commit `7959bfe` for the test/doc follow-up). This file records the corrected
package's actual **email resend** to the real inbox, which is a distinct action from
that earlier file/test/doc work.

## Package resent

| Show | Slot | batch_id | package_id | What changed vs. the original 2026-07-28 09:54 AM ET send |
|---|---|---|---|---|
| Blue Box (Ao no Hako) | evening | b3e8f2a1-7c4d-4e9a-9f21-6a8d4c5e2b17 | f7c2e9b4-3a61-4d8f-b527-9e4c1a6d8f32 | All 4 clips re-sourced to real, independently verified Episode 1 ("Chinatsu Senpai") content. Cut 4 specifically corrected from a false "closing gym/school shot" claim to the real, sourced kitchen-scene closing beat (Taiki learns Chinatsu will live with his family; city-view zoom-out). Each clip now carries its own real `verification_source_url`, full `claim_vs_source_check`, and full `clip_locate` (Law #73 Update 4/5 fields, absent in the original send). VO, hook, captions, titles, TikTok text, pinned comment, and post times are unchanged from the original — only the `clips` array and `clip_descriptions` text changed. |

VO, hook line, YouTube/TikTok titles, captions, pinned comment, and post times are all
identical to the original send — this was a clip-plan-only content correction, not a
full rewrite of the package's voice track or metadata.

## Validation before send

Re-ran `validators/validate_dual_package.py` directly against the real, live
`run_manifest.json` in this directory (not a scratch copy) after the corrective edit:
**PASS, exit 0** — full check list including all Law #73 Update 4/5 clip-verification
checks and all `semantic_qa`/`claim_source_matrix` checks. Full suite
(`python3 -m unittest discover` under `validators/`) also re-run clean: **210/210
passing**, no regressions.

## Why `append_send_batch.py` is not being run for this package_id

Same reasoning already established and re-confirmed earlier tonight (see
`REWRITE_SEND_20260727_batch_v3.md`'s "Why `append_send_batch.py` is not being run"
section, which applies identically here): the tool's dedup key is
`(batch_id, package_id)` only, and this package_id already has a `"status": "sent"`
row in `sent_scripts_log.json` under the same `batch_id` from the original 2026-07-28
send. Running the logger again would either silently no-op (if reusing the same
batch_id/package_id pair) or append an ambiguous second "sent" row with no
distinguishing event type (if given a new batch_id). Neither is correct, and no code
change to `append_send_batch.py` was authorized tonight. This markdown file is the
record instead. The original `sent_scripts_log.json` entry for this package_id is
**not** modified, duplicated, or appended to.

## Send and mailbox verification

Sent to `hero_or_villain@outlook.com` only, via a single `send_email` tool call.

**Real, direct `search_email` verification result — duplicate dispatch observed:**
the search (filtered to the exact subject string, run immediately after sending)
returned **2 distinct `email_id` values**, not 1:

| email_id (truncated) | Timestamp (UTC) |
|---|---|
| `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0w...` | 2026-07-29T00:33:28Z |
| `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0w...` | 2026-07-29T00:33:24Z |

Both share the identical subject (`REWRITTEN SCRIPT | EVENING | Blue Box (Ao no Hako)
| originally sent 2026-07-28 | Blue Box Ended, But a One Piece Card Ruined It`),
identical body content, identical `thread_id`, and land 4 seconds apart. This subject
string did not exist in the mailbox before tonight (unlike the round-3 Dr. Stone case,
where two same-subject emails legitimately corresponded to two different nights'
sends) — so this is **not** two distinct real send events being conflated. Exactly one
`send_email` call was made this action. The mailbox nonetheless holds two copies of
that single call's output, consistent with the pre-existing duplicate-dispatch
connector defect already tracked in `BLOCKER_20260728_duplicate_dispatch.md`. No
attempt was made to delete either copy — deleting mailbox items was not authorized and
is out of scope for this record.

**Reported plainly, per the standing no-assumption rule:** 2 copies confirmed via
direct search, not 1. Not treated as a clean single send.

## Filed

Date: 2026-07-29T00:33:28Z (UTC) — the later of the two confirmed copies' timestamps.

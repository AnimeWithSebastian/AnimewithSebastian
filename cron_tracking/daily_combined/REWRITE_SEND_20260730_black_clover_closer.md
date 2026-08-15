# Rewrite send record — Black Clover morning closer correction (2026-07-30)

## Status

This round corrects the Black Clover morning package from tonight's `daily_combined`
batch (`batch_id 439755dc-4f9f-479b-9668-8b01079091bf`, originally sent
2026-07-30T22:45:48Z as part of the scheduled cron run), after a three-round
user-guided defect fix on the closer/question line:

- **Round 1**: original closer "Does Black Clover deserve a real ending?" flagged as
  not a genuine two-sided prompt (same defect pattern as an earlier Hunter x Hunter
  fix). Two grounded options were proposed from the VO's own specific facts; the user
  selected the wait/gap framing: "Episode 170 aired in 2021. Is a Season 2 five years
  later still worth the wait, or did the moment already pass?"
- **Round 2**: a Law #149 redundancy was caught — "episode 170 aired in 2021" restated
  a fact already stated one sentence earlier in the VO body. The user corrected this
  to: "Five years later, is it still worth the wait, or did the moment already pass?"
- **Round 3**: the validator's real tokenizer (`re.findall(r"[\w']+", text)`, which
  splits hyphenated words like "fifteen-page" into two tokens) put the Round 2 VO at
  109 words, not the manually-counted 108. The user approved dropping "still" to land
  at exactly 108 per the validator's actual count. **Final closer**: "Five years later,
  is it worth the wait, or did the moment already pass?"

The correction was applied as a surgical field replacement to the live
`cron_tracking/daily_combined/run_manifest.json` (`packages[0].vo`,
`packages[0].vo_word_count`, `packages[0].question_line`), re-validated fresh against
the actual file with `validators/validate_dual_package.py`, and confirmed **PASS,
exit code 0** (both packages) before sending.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Black Clover | morning | 439755dc-4f9f-479b-9668-8b01079091bf | c13e2098-69b3-49ce-a3f2-6d900be9fc44 | Closer/question_line replaced across 3 rounds: "Does Black Clover deserve a real ending?" → "Episode 170 aired in 2021. Is a Season 2 five years later still worth the wait, or did the moment already pass?" → "Five years later, is it still worth the wait, or did the moment already pass?" → final: "Five years later, is it worth the wait, or did the moment already pass?" (redundant "episode 170 aired in 2021" restatement removed per Law #149; "still" dropped to correct word count to exactly 108 per the validator's real `[\w']+` tokenizer). VO body otherwise unchanged. |

The Akane-banashi evening package (`package_id e3cbe254-d7fd-4707-adf4-6126eefdc458`,
same `batch_id`) is untouched this round.

## Validation before send

`validators/validate_dual_package.py` run fresh against the actual live
`cron_tracking/daily_combined/run_manifest.json` after the correction:

**RESULT: PASS — exit code 0, all checks green** (both packages).

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`REWRITE_SEND_20260727_batch_v3.md`, `REWRITE_SEND_20260730_hxh_berserk.md`),
re-confirmed by direct code read again tonight: `tools/append_send_batch.py`'s dedup
key is `(batch_id, package_id)` only, with no `--event-type` or note-passing
mechanism.

`c13e2098-69b3-49ce-a3f2-6d900be9fc44` already carries a `"status": "sent"` row in
`sent_scripts_log.json` and `sent_scripts_events.jsonl` under `batch_id
439755dc-4f9f-479b-9668-8b01079091bf` from `2026-07-30T22:39:00+00:00`, with the
original (pre-correction) closer text. Re-running the logger against this same
`(batch_id, package_id)` pair would be a silent no-op (`events_appended: 0`) and would
NOT update the logged closer/VO text — it would incorrectly appear as if nothing had
changed. Constructing a new batch_id or package_id for the same correction would
bypass the dedup guard and append a second, ambiguous `"sent"` row with no
distinguishing event type. Neither is desirable. This markdown file is the record
instead. The original `sent_scripts_log.json` / `sent_scripts_events.jsonl` entries
for this package_id are NOT modified, duplicated, or appended to — they remain the
honest historical record of what was originally logged at send time.

**Backlog item** (same standing item noted in every prior correction round): add a
distinct `--event-type` (default `"sent"`, allow `"rewritten"`/`"corrected"`) and an
optional free-text `note` field to `append_send_batch.py`'s event schema, excluded
from quota/dedup counting in the weekly analytics join.

## Sends and mailbox verification

Sent to `hero_or_villain@outlook.com` only, same subject line as the original
(`TOMORROW | MORNING | Black Clover | 2026-07-31 | Black Clover Ended. The Anime
Never Showed It`) — this round did not use a `REWRITTEN SCRIPT | ...` prefix as prior
rounds did. Verified via a direct `search_email` query on the exact subject string
immediately after sending.

| Sent (per Outlook, UTC) | Content | Mailbox copies found |
|---|---|---|
| 2026-07-30T22:45:48Z | Original — old closer ("Does Black Clover deserve a real ending?") | 1 (pre-existing, untouched) |
| 2026-07-31T00:09:54Z | Corrected — final closer ("Five years later, is it worth the wait, or did the moment already pass?") | 1 |
| 2026-07-31T00:09:58Z | Corrected — identical to above (duplicate) | 1 |

**Total mailbox copies of this exact subject line: 3** — confirmed via direct
`search_email`, three distinct `email_id`s, all dated 2026-07-30/31, verified
byte-for-byte distinct (different `email_id`s, same `thread_id`).

**F21 duplicate-dispatch defect observed on this send.** One `send_email` tool call
was made for the corrected package; it produced two mailbox-side copies with distinct
`email_id`s, 4 seconds apart (`00:09:54Z` and `00:09:58Z`), both from
`hero_or_villain@outlook.com` to `hero_or_villain@outlook.com`, both carrying the
exact corrected content approved by the user. This matches the known connector-side
duplicate-dispatch pattern referenced in `docs/KNOWN_ISSUES.md` (F21) and observed in
the prior same-night round (`REWRITE_SEND_20260730_hxh_berserk.md`) — not a new
defect, and not evidence of a second distinct send action on this side. No emails
were sent to any address other than `hero_or_villain@outlook.com`. The original
2026-07-30T22:45:48Z copy (old closer) was NOT re-triggered or removed — it remains
present as the honest historical record of the original cron send, per explicit user
instruction not to touch the mailbox.

## Filed

Date: 2026-07-31T00:09:58Z (UTC) — set to the latest of the confirmed send
timestamps above.

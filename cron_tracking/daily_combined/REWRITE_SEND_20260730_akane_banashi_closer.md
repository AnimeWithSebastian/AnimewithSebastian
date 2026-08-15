# Rewrite send record — Akane-banashi evening closer correction (2026-07-30)

## Status

This round corrects the Akane-banashi evening package from tonight's `daily_combined`
batch (`batch_id 439755dc-4f9f-479b-9668-8b01079091bf`, originally sent
2026-07-30T22:39:00+00:00 as part of the scheduled cron run, with a mailbox-observed
duplicate dispatch at that same original send — see Mailbox verification below), after
a single-round user-guided defect fix on the closer/question line.

**This defect is a different category from tonight's other three corrections
(Hunter x Hunter, Berserk, Black Clover), which all shared the "not a genuine
two-sided answer" pattern.** The Akane-banashi original closer — "Why isn't this in
the same conversation as the biggest shonen right now?" — has a distinct defect:
it references an undefined comparison ("the biggest shonen right now") that is never
named or established anywhere in the 108-word VO. This is a vagueness / undefined-
referent violation, not a one-sided-answer violation, and is recorded here explicitly
as a separate defect category for the log.

- **Round 1**: user proposed a replacement grounded only in facts already present in
  the VO (free-to-watch, already-renewed for Season 2): "Is rakugo too niche to break
  out, or is this a marketing problem?" — a genuine two-sided question with zero
  undefined references. Real regex word count
  (`len(re.findall(r"[\w']+", text))`) against the fixed VO base confirmed this
  closer brings the full VO to exactly 108 words, with no redundancy against earlier
  VO content and no unstated judgment terms. The user locked in this exact wording,
  no further rounds needed.

The correction was applied as a surgical field replacement to the live
`cron_tracking/daily_combined/run_manifest.json` (`packages[1].vo`,
`packages[1].question_line`; `packages[1].vo_word_count` unchanged at 108, since the
old and new closers happened to both total 108 words), re-validated fresh against the
actual file with `validators/validate_dual_package.py`, and confirmed **PASS, exit
code 0** (both packages) before sending. The live file was re-fetched immediately
before editing to confirm it matched the byte-for-byte content the correction was
drafted against (per the standing re-verification standard).

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Akane-banashi | evening | 439755dc-4f9f-479b-9668-8b01079091bf | e3cbe254-d7fd-4707-adf4-6126eefdc458 | Closer/question_line replaced: "Why isn't this in the same conversation as the biggest shonen right now?" (undefined-referent defect — "the biggest shonen right now" never established in the VO) → final: "Is rakugo too niche to break out, or is this a marketing problem?" (genuine two-sided question, grounded only in facts already stated in the VO: free-to-watch, already-renewed). VO body otherwise unchanged; `vo_word_count` unchanged at 108 (both closers total 108 words under the validator's real tokenizer). |

The Black Clover morning package (`package_id c13e2098-69b3-49ce-a3f2-6d900be9fc44`,
same `batch_id`) was corrected and closed out earlier tonight — see
`REWRITE_SEND_20260730_black_clover_closer.md` — and is untouched this round.

## Validation before send

`validators/validate_dual_package.py` run fresh against the actual live
`cron_tracking/daily_combined/run_manifest.json` after the correction:

**RESULT: PASS — exit code 0, all checks green** (both packages), including
`question_line is a question`, `question immediately followed by 'Leave your take.'
in VO`, Law #149 redundancy check, and all Law #73 clip-verification checks.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds tonight (see
`REWRITE_SEND_20260730_black_clover_closer.md` and earlier files referenced there):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only, with no
`--event-type` or note-passing mechanism.

`e3cbe254-d7fd-4707-adf4-6126eefdc458` already carries a `"status": "sent"` row in
`sent_scripts_log.json` and `sent_scripts_events.jsonl` under `batch_id
439755dc-4f9f-479b-9668-8b01079091bf` from `2026-07-30T22:39:00+00:00`, with the
original (pre-correction) closer text — confirmed by direct read/grep of both files
immediately before drafting this document, not assumed. Re-running the logger against
this same `(batch_id, package_id)` pair would be a silent no-op (`events_appended: 0`)
and would NOT update the logged closer/VO text — it would incorrectly appear as if
nothing had changed. This markdown file is the record instead. The original
`sent_scripts_log.json` / `sent_scripts_events.jsonl` entries for this package_id are
NOT modified, duplicated, or appended to — they remain the honest historical record of
what was originally logged at send time.

**Backlog item** (same standing item noted in every prior correction round tonight):
add a distinct `--event-type` (default `"sent"`, allow `"rewritten"`/`"corrected"`)
and an optional free-text `note` field to `append_send_batch.py`'s event schema,
excluded from quota/dedup counting in the weekly analytics join.

## Sends and mailbox verification

Sent to `hero_or_villain@outlook.com` only, same subject line as the original
(`TOMORROW | EVENING | Akane-banashi | 2026-07-31 | Nobody's Talking About
Akane-banashi (They Should Be)`). Verified via a direct `search_email` query on the
exact subject string both before (baseline) and after sending.

| Sent (per Outlook, UTC) | Content | Mailbox copies found |
|---|---|---|
| 2026-07-30T22:46:30Z | Original — old closer ("Why isn't this in the same conversation as the biggest shonen right now?") | 1 (pre-existing, untouched) |
| 2026-07-30T22:46:36Z | Original — identical to above (duplicate, 6 seconds apart) | 1 (pre-existing, untouched) |
| 2026-07-31T01:16:01Z | Corrected — final closer ("Is rakugo too niche to break out, or is this a marketing problem?") | 1 |

**Total mailbox copies of this exact subject line: 3** — confirmed via direct
`search_email`, three distinct `email_id`s, all sharing the same `thread_id`, verified
byte-for-byte distinct by body content (2 old-closer copies, 1 new-closer copy).

**F21 duplicate-dispatch defect observed on the ORIGINAL cron send, not on tonight's
corrected resend.** Unlike Black Clover (whose original cron send produced exactly 1
mailbox copy and whose correction round is what triggered an F21 duplicate), the
Akane-banashi original cron send itself already produced two mailbox-side copies with
distinct `email_id`s, 6 seconds apart (`22:46:30Z` and `22:46:36Z`), both carrying the
old (pre-correction) closer text. This is a separate, earlier instance of the same
known connector-side duplicate-dispatch pattern referenced in `docs/KNOWN_ISSUES.md`
(F21) — not caused by, and not related to, tonight's correction workflow. Tonight's
corrected resend (`01:16:01Z`) produced exactly **one** mailbox copy — no F21 duplicate
occurred on this specific send action. No emails were sent to any address other than
`hero_or_villain@outlook.com`. Neither original 2026-07-30T22:46:30Z/22:46:36Z copy
(old closer) was re-triggered or removed — both remain present as the honest
historical record of the original cron send, per explicit user instruction not to
touch the mailbox.

## Filed

Date: 2026-07-31T01:16:01Z (UTC) — set to the confirmed corrected-send timestamp
above.

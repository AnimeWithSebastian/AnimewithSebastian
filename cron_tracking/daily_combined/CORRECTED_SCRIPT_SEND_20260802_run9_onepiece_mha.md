# Corrected script resend record — Run #9 (One Piece morning, My Hero
Academia evening) — 2026-08-02

## Status

This is the tracking record for the "CORRECTED SCRIPT" resend of both run #9
packages (`batch_id c8401ef5-1d1e-48ce-a3f4-39443498caea`, originally sent
2026-08-01T23:46:16Z-23:46:39Z UTC as part of the scheduled `daily_combined`
cron run), following a user-directed independent post-send verification pass
that found real, confirmed defects in both packages. Full defect findings are
documented in `docs/KNOWN_ISSUES.md` under **F27** (self-audit reliability
failure) and the **F21** history table (duplicate-dispatch recurrence).

## Packages corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | 4af7ca6d-1545-4eae-8252-dc459afc39f6 | Closer replaced: "Elbaf isn't done rewriting what this crew can survive." (Law #149 point 9 poetic-restatement violation) -> "One title card did what 1,171 episodes never tried." (108 validator-counted words, dropped "of power-ups" from the initially-locked wording to fit the validator's real `[\w']+` tokenizer). VO body otherwise unchanged. |
| My Hero Academia | evening | c8401ef5-1d1e-48ce-a3f4-39443498caea | 8f3552ac-bca7-4a1e-a6ed-8eb4afaa2756 | Three corrections: (1) dropped the unsupported "adapts the final material Horikoshi wrote for the series" superlative and the ComicBook.com "confirmed" sentence that directly contradicted ComicBook.com's actual page content; replaced with disclosed-conflict sourcing language (GameRant/ScreenRant confirm a real Horikoshi one-shot adaptation; ComicBook.com calls the special original). (2) Closer replaced: "Eri got an ending nobody scripted for her." (Law #149 point 9 violation, also self-contradictory against the VO's own Horikoshi-scripted claim) -> "Other heroes got final battles. Eri got a final note instead." (107 validator-counted words, changed "Every other hero got a final battle" -> "Other heroes got final battles" to fit the validator's real tokenizer). (3) Sources list corrected: independently re-verified the "six-page" one-shot detail against GameRant's actual article text (confirmed verbatim: "This one-shot spanned only six pages") and disclosed a genuine, unresolved year conflict between GameRant ("2025") and ScreenRant ("December 2024") rather than silently picking one. |

## Validation before resend

`validators/validate_dual_package.py` run fresh against the corrected
`cron_tracking/daily_combined/run_manifest.json`:

**RESULT: PASS — exit code 0, zero FAIL lines, both packages.**

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`REWRITE_SEND_20260730_black_clover_closer.md` and earlier precedents):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only.
Both `4af7ca6d-1545-4eae-8252-dc459afc39f6` and
`8f3552ac-bca7-4a1e-a6ed-8eb4afaa2756` already carry `"status": "sent"` rows
in `sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`
under this same `batch_id`, logged at the original 2026-08-01 send time with
the original (pre-correction) content. Re-running the logger against these
same `(batch_id, package_id)` pairs would be a silent no-op
(`events_appended: 0`) and would NOT reflect the correction. Per explicit
user instruction this round, `sent_scripts_log.json` and
`sent_scripts_events.jsonl` are left untouched — this markdown file is the
record instead.

## Sends and mailbox verification

Both emails sent to `hero_or_villain@outlook.com` only, subject prefix
`CORRECTED SCRIPT | ...` per explicit user request this round. Verified via
direct `search_email` full-string `email_id` comparison immediately after
sending.

| Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|
| CORRECTED SCRIPT \| MORNING \| One Piece \| 2026-08-02 \| One Piece Just Titled an Episode 'Fear' | 2026-08-02T02:17:45Z | 1 |
| CORRECTED SCRIPT \| EVENING \| My Hero Academia \| 2026-08-02 \| My Hero Academia Isn't Actually Over | 2026-08-02T02:17:44Z, 2026-08-02T02:17:51Z | 2 (genuine duplicate) |

**Morning (One Piece): 1 real mailbox copy, no duplicate this round.**
`email_id` ending `...U3DdAAAA`. Only one `send_email` tool call was made.

**Evening (My Hero Academia): 2 real mailbox copies — genuine F21
duplicate-dispatch recurrence.** Two distinct full `email_id`s confirmed via
direct string comparison (`...U3DcAAAA` at 02:17:44Z and `...U3TGAAAA` at
02:17:51Z), same `thread_id` (`...GiduyhsW`), ~7 seconds apart. Only one
`send_email` tool call was made for this package — consistent with F21's
established finding that this is a connector/transport-side defect, not an
agent-side double-send. This occurrence has been appended to the F21 history
table in `docs/KNOWN_ISSUES.md` alongside the 2026-08-01 (run #9 original
send) occurrence documented in the same table.

**No emails were sent to any address other than `hero_or_villain@outlook.com`.**
The original 2026-08-01T23:46:16Z-23:46:39Z copies (pre-correction content,
4 total mailbox copies per F21/F27) were NOT re-triggered or removed — they
remain present as the honest historical record of the original cron send,
per explicit standing user instruction not to touch existing send records.

## Filed

Date: 2026-08-02T02:17:51Z (UTC) — set to the latest of the confirmed send
timestamps above.

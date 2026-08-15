# Rewrite send record — Hunter x Hunter / Berserk fact-verification round (2026-07-30)

## Status

This round resends the daily_combined batch originally sent 2026-07-29 for Hunter x
Hunter (morning) and Berserk (evening), after two coordinated fixes earlier tonight:
(1) a closer/CTA-adjacency correction carried over from an earlier fix pass, and (2)
this round's headline fix — two fact-verification errors caught by independent
source/transcript re-checks:

- **Hunter x Hunter**: original VO asserted a specific "inking past chapter 421,
  layouts past chapter 430" stage split. Re-verification found the two sources cited
  for that claim ([animefanatika.co.za](https://animefanatika.co.za/bento-news-july-2026-the-ultimate-anime-news-roundup/)
  and [respawn.outlookindia.com](https://respawn.outlookindia.com/pop-culture/pop-culture-news/hunter-x-hunter-volume-39-set-for-july-release-after-22-month-gap))
  contradict each other on which chapter number maps to which production stage. A
  third source ([gametrader.sg](https://gametrader.sg)) does support the exact 421/430
  split but is not currently cited in the manifest, and per the user's explicit
  conservative-approach decision it was deliberately NOT swapped in this round. The VO
  was corrected to the claim both currently-cited sources actually support without
  contradiction: "well past chapter 420, with a real inking backlog of over 20
  chapters" — no specific chapter-to-production-stage pairing is asserted.
- **Berserk**: original VO asserted a "World Tree tether" mechanic keeping Griffith
  physically bound to Falconia. Independent verification of the actual transcripts
  (not just titles/descriptions, per Law #155) of both cited YouTube videos
  ([Hajime no Raju](https://www.youtube.com/watch?v=7qaZwslFmK8) and
  [Anime Balls Deep](https://www.youtube.com/watch?v=CXRurHplECc)) found zero mention
  of a World Tree or any physical-distance/tether mechanic. Both videos DO support a
  related but more general thematic claim instead: the God Hand mocking Falconia as a
  hollow illusion/"dollhouse" Griffith built for himself. The VO was corrected to state
  only this well-supported thematic claim.

Both corrections were applied as surgical field replacements to the live
`cron_tracking/daily_combined/run_manifest.json` (commits `7495fb6` and `3f93e80`,
both pushed to `origin/main` earlier tonight), re-validated fresh against the actual
file with `validators/validate_dual_package.py`, and confirmed **PASS, exit code 0**
before any send in this round.

## Packages sent this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Hunter x Hunter | morning | ac60c0a6-a81b-4033-ba5f-a431fa98b10d | d1a7c8e2-4f3b-4a9e-8c1d-5e6f7a8b9c0d | VO corrected from a specific 421/430 chapter-stage split to the conservative, fully-source-supported "well past chapter 420, real inking backlog of over 20 chapters" claim (108→101 words). Propagated to `claim_source_matrix`, the affected `sources` entry, and `tiktok_post_text` (removed "already written past 430"). |
| Berserk | evening | ac60c0a6-a81b-4033-ba5f-a431fa98b10d | f2b8d9e3-5a4c-4b0f-9d2e-6f7a8b9c0d1e | VO corrected from an unsupported "World Tree tether" mechanic to the transcript-verified "Falconia as a hollow illusion Griffith built for himself" framing. Propagated to `claim_source_matrix`, the affected `sources` entry, and `clip_descriptions` (removed "World Tree tether" reference). |

Both packages share `batch_id ac60c0a6-a81b-4033-ba5f-a431fa98b10d` and `post_date
2026-07-30` — this is the original daily_combined batch being corrected in place, not
a new batch.

## Validation before send

`validators/validate_dual_package.py` run fresh against the actual live
`cron_tracking/daily_combined/run_manifest.json` after both correction commits:

**RESULT: PASS — exit code 0, all checks green** (both packages, including Law #73
clip-verification checks and all `semantic_qa`/`claim_source_matrix` checks against
the corrected wording).

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`REWRITE_SEND_20260727_batch_v3.md`), re-confirmed by direct code read again tonight:
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only, with no
`--event-type` or note-passing mechanism.

Both `d1a7c8e2-...` and `f2b8d9e3-...` already carry a `"status": "sent"` row in
`sent_scripts_log.json` under the original batch_id `ac60c0a6-...` from
2026-07-29T18:56:00-04:00. Re-running the logger against this same `(batch_id,
package_id)` pair would be a silent no-op (`events_appended: 0`). Constructing a new
batch_id for the same two package_ids would bypass the dedup guard and append a second,
ambiguous `"sent"` row with no distinguishing event type. Neither is desirable. This
markdown file is the record instead. The original `sent_scripts_log.json` /
`sent_scripts_events.jsonl` entries for these two package_ids are NOT modified,
duplicated, or appended to.

**Backlog item** (same standing item noted in every prior correction round): add a
distinct `--event-type` (default `"sent"`, allow `"rewritten"`/`"corrected"`) and an
optional free-text `note` field to `append_send_batch.py`'s event schema, excluded
from quota/dedup counting in the weekly analytics join.

## Sends and mailbox verification

Both sent to `hero_or_villain@outlook.com` only. Verified via a direct `search_email`
query immediately after sending, filtered to the exact subject strings and today's
date.

| Show | Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|---|
| Hunter x Hunter | `REWRITTEN SCRIPT \| MORNING \| Hunter x Hunter \| originally sent 2026-07-29 \| Hunter x Hunter Manga Is 90 Chapters Ahead` | 2026-07-30T15:08:45Z and 2026-07-30T15:08:40Z | **2** — confirmed via direct `search_email`, two distinct `email_id`s under this exact subject, both dated 2026-07-30. |
| Berserk | `REWRITTEN SCRIPT \| EVENING \| Berserk \| originally sent 2026-07-29 \| Berserk Just Proved Griffith's Throne Is a Cage` | 2026-07-30T15:08:46Z and 2026-07-30T15:08:42Z | **2** — confirmed via direct `search_email`, two distinct `email_id`s under this exact subject, both dated 2026-07-30. |

**F21 duplicate-dispatch defect observed on BOTH sends tonight.** One `send_email`
tool call was made for each show; each produced two mailbox-side copies with distinct
`email_id`s, ~2-5 seconds apart, both from `hero_or_villain@outlook.com` to
`hero_or_villain@outlook.com`, both carrying the exact corrected content approved by
the user. This matches the known connector-side duplicate-dispatch pattern referenced
in `docs/KNOWN_ISSUES.md` (F21) and observed in a prior round's blocker note
(`BLOCKER_20260728_duplicate_dispatch.md`) — not a new defect, and not evidence of a
second distinct send action on this side. No emails were sent to any address other
than `hero_or_villain@outlook.com`. No pre-existing 2026-07-29-dated copies of these
two exact subjects were re-triggered — both older `TOMORROW | ...` originals from
2026-07-29T22:43-22:44 UTC remain present and untouched, confirming tonight's four
`REWRITTEN SCRIPT`-subject copies (two per show) are new, not re-surfaced duplicates
of the original send.

## Filed

Date: 2026-07-30T15:08:46Z (UTC) — set to the latest of the confirmed send timestamps
above.

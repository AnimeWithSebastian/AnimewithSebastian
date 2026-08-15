# Archived — That Time I Got Reincarnated as a Slime Correction (Evening, 2026-08-14 target) Held for Law #165 Fetch-and-Confirm Failure

## Status: HELD, NOT DELETED, NOT SENT, NOT FURTHER REVISED TONIGHT

This is a **correction package** for the Slime evening slot that was already
sent once on the original send date as part of `batch_id`
`b03ef8b6-d254-442a-aaf9-673a6578a0c5` (`package_id`
`8cf962b9-786a-42ab-9888-8de397136784`). A correction batch,
`batch_id` `32e0fcb9-440c-4b2e-8bd4-0c900390b3c1` (`corrects_batch_id` →
`b03ef8b6-d254-442a-aaf9-673a6578a0c5`), was drafted tonight alongside a
Link Click correction to fix a wrong Cut 6 clip timestamp
(`18:00-24:49` → `1:48-2:38`, confirmed against
`https://www.youtube.com/watch?v=_4xtVj881w4`). That timestamp fix is correct
and is **not** the reason for this hold.

| Show | package_id | Slot | Correction batch_id | Corrects (original) batch_id |
|---|---|---|---|---|
| That Time I Got Reincarnated as a Slime | 8cf962b9-786a-42ab-9888-8de397136784 | evening | 32e0fcb9-440c-4b2e-8bd4-0c900390b3c1 | b03ef8b6-d254-442a-aaf9-673a6578a0c5 |

## Why this is held (root cause, not a wording defect)

During the mandatory Law #165 fetch-and-confirm review (every core claim's
cited URL must be actually fetched and confirmed to state the claim — not
re-read from the manifest's own self-report), a **separate, previously
unnoticed** problem was found in this same package: the core, hook-anchored
claim "Slime Season 4 Episode 18 aired August 7, 2026" is contradicted by
both of its own cited sources once genuinely fetched tonight.

- `https://www.comicbasics.com/that-time-i-got-reincarnated-as-a-slime-season-4-episode-18-release-date-and-time/`
  (published 2026-08-06): states Episode 18 was scheduled to premiere
  **August 14, 2026**, "a week after Episode 17, which aired on August 7,
  2026." This directly places August 7 on Episode 17, not Episode 18.
- `https://www.aol.com/articles/time-got-reincarnated-slime-season-153000000.html`
  (published 2026-08-08): describes "this week's installment" (the most
  recent one as of Aug 8) as the one where "Diablo confronts Raine after she
  insults Rimuru... he started to overwhelm his opponents" — the exact fight
  beat the VO's hook attributes to Episode 18 — and frames Episode 18's own
  content as still speculative/upcoming.

Both sources, read plainly, place the Diablo-vs-Rain(e) fight the entire VO
is built around in Episode 17, aired August 7 — not Episode 18 as the
package's hook claims. Per Law #165: "If it does not [support the claim]...
Do not approve. Either find a real supporting source and correct the
citation, or cut/soften the claim, before this package may be approved."
This is exactly that class of failure, so the package cannot be approved as
drafted.

## Open hypothesis, not yet checked (first thing to investigate on resume)

Sebastian flagged, and this note preserves, one specific possibility that
would make the actual fix much smaller than a full rebuild: this could be a
numbering-convention mismatch rather than a genuine wrong-episode error. The
package's own VO parenthetically references an absolute episode count
("Episode 18 (Episode 90)") alongside the season-relative count, and
Slime Season 4 is confirmed (per `comicbasics.com`) to run five full cours
across multiple years — a structure where absolute-vs-season-relative
numbering conventions could plausibly diverge by one under some official
listings. This has not been checked in this session. If it resolves cleanly,
the correction may only need a season/absolute-numbering clarification
rather than re-sourcing the entire fight-content claim against Episode 17.

## What this note does NOT do

- Does not delete, modify, or resend this package or generate any email for
  it tonight. No correction email for this package_id has been sent.
- Does not affect or reopen the original 2026-08-07 send of this package
  (`batch_id` `b03ef8b6-d254-442a-aaf9-673a6578a0c5`) — that entry in
  `sent_scripts_log.json` / `sent_scripts_events.jsonl` is untouched by this
  hold and is a separate, already-closed question from tonight's correction
  attempt.
- Does not touch the already-correct Cut 6 clip-timestamp fix
  (`1:48-2:38`) — that fix stands and should be carried forward unchanged
  whenever this package is revisited, rather than re-derived from scratch.
- Does not affect or gate Link Click's correction, which is independently
  verified and proceeds tonight alone as a single-package manifest under
  `batch_id` `32e0fcb9-440c-4b2e-8bd4-0c900390b3c1`
  (`single_package_reason` documents this exact hold as the reason Slime is
  absent from that batch).
- Does not mark the show "That Time I Got Reincarnated as a Slime" or this
  package_id as blocked from future coverage. Revisiting this correction is
  a fresh investigation, not a same-night patch under time pressure, per
  Sebastian's explicit instruction.

## Related known-issues entry

See `docs/KNOWN_ISSUES.md` F36 for the full process-level writeup of this
finding, including the exact fetched quotes from both contradicting sources.

Filed: 2026-08-14 (session time, Thursday 2026-08-13 10:15 PM EDT)

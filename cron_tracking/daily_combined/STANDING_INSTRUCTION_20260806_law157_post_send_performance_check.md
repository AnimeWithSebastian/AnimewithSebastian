# Standing Instruction — Law #157: Post-Send Real-Data Performance Verification

**Date received:** 2026-08-06, ~6:51 PM ET
**Source:** direct Sebastian instruction, verbatim reproduced below
**Status:** CODIFIED into `hero_or_villain_master_laws_final.txt` (Law #157) and
ported into `cron_daily_runtime.txt` (new STEP 9) the same day. Not yet
executed against real data — the triggering batch has not been published or
aged 24h yet (see "Trigger status" below).

## Instruction as given (verbatim)

> Standing instruction for all future daily_combined batches, starting
> with tonight's Kagurabachi + Gachiakuta send: report back on real
> performance data once it's available (respecting the known 24-48hr
> reporting delay), not just send-confirmation status.
>
> Specifically, once real data exists for these two videos:
>
> 1. Pull real impressions and views via the API (same method already
> used successfully tonight — youtube_analytics_api-get-video-metrics
> against the real video IDs once they're published).
>
> 2. Compare against the real baseline already established tonight:
> JJK (452/53), Tanya (654-738/34-35), Chainsaw Man (28-33/0-1), Solo
> Leveling (8/0). Report plainly which pattern these two land closer
> to — the "real test audience, moderate conversion" pattern, or the
> "near-zero impressions, no real test at all" pattern.
>
> 3. If either lands in the near-zero pattern: this is a real, useful data
> point for the still-open question of whether this is a platform-side
> issue (the pattern already found in tonight's research, and reported
> via the submitted YouTube feedback) or something else — report it as
> exactly that, don't speculate beyond what the data shows.
>
> 4. If either lands in the moderate-conversion pattern with weak view-
> through despite real impressions: run the Isolation Test on that
> specific hook again, now that it's real audience behavior confirming
> or contradicting the pre-send judgment — same as how JJK/Tanya's
> real data already validated the hook-check process once tonight.
>
> This isn't a one-time check — apply this same real-data comparison to
> every future batch going forward, so any pattern (good or bad) gets
> caught with real evidence, not assumed either way.

## What was done tonight to codify this

1. Added **Law #157 — Post-Send Real-Data Performance Verification** to
   `hero_or_villain_master_laws_final.txt`, immediately after Law #144.1
   (The Isolation Test), following the established law-file format (WHY THIS
   LAW EXISTS / WHAT THIS LAW REQUIRES / ENFORCEMENT-SCOPE NOTES / PORT-BACK
   REQUIRED note).
2. Ported Law #157 directly into `cron_daily_runtime.txt`:
   - Added a reference entry in the ENFORCED LAW SET list (STEP 0 section).
   - Added a full new **STEP 9 — POST-SEND REAL-DATA PERFORMANCE CHECK**
     section at the end of the runtime, with the exact procedure: resolve
     real video_id, pull real impressions/views, gate on the 24h reporting
     delay, classify against the two named real patterns, branch to either
     the platform-side-issue reporting path or the Isolation Test re-run
     path, log the result in `docs/PERFORMANCE_DATA.md`, and push.
   - Unlike some prior laws that were left as "PORT-BACK REQUIRED" for a
     future pass, this one was ported into the runtime in the SAME pass it
     was written, since it needs to actually fire on a future unattended
     scheduled run rather than depend on a human re-reading the law file.
3. This tracking doc, recording the instruction verbatim and what was done
   about it — same pattern as every other standing-rule/correction doc this
   session.

## Trigger status for the two named videos (checked tonight, not yet ready)

- **Kagurabachi** (`package_id fc92f1fc-de9d-4829-9f5c-7bf144f99fa3`,
  batch_id `8c737fff-f523-4b00-896a-4e2fc8a40152`, post_date 2026-08-07)
- **Gachiakuta** (`package_id 88dff475-d267-46d1-946f-f65bdaf5c785`,
  same batch_id, post_date 2026-08-07)

Checked `cron_tracking/publication_ledger.jsonl` tonight: **neither package_id
has a `published` event yet** — expected, since post_date is tomorrow
(2026-08-07) and this ledger only records actual YouTube publish events, not
sends. Law #157's own timing rule (24h+ past PUBLISH, not past send) means
this check cannot run yet regardless of how much time has passed since the
correction email or the original send — it is gated on real publication plus
24h, which has not started yet.

**Next action:** on a future daily_combined run (or a dedicated check once
Sebastian confirms these are live on YouTube), confirm publication via the
ledger, confirm 24h+ has elapsed since that publish timestamp, then execute
STEP 9 exactly as written and log the result in `docs/PERFORMANCE_DATA.md`.

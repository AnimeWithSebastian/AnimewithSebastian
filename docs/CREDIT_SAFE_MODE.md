# Credit-Safe Mode — Waste-Prevention Policy

**Status:** ACTIVE (July 21, 2026). Governed by Law #147. User-approved and enabled now.

This document is the operational policy for Part 3 of credit-safe mode. It is a
**waste-prevention** policy, not a quality-reduction policy. Nothing here reduces
posting frequency, the Claude Sonnet 5.0 creative routing (Law #137), live-research
depth, candidate-specific source verification, human semantic review, or fail-closed
validation. It exists to stop spending credits on work that does not improve a
published video.

**No new scheduled task is added and no existing cadence is increased.** The daily
combined cron (`daily_combined`) stays daily at 23:30 UTC; the weekly analytics cron
(`2bb28991`) stays Sundays at 23:30 UTC.

## Policy rules

1. **Non-email dry runs — only when justified.** Run a full non-email dry run of a cron
   ONLY after a code/runtime change to that cron's logic, or immediately after a
   validation failure that needs reproduction. Do not dry-run unchanged pipelines "to be
   safe" — the fail-closed validator (`validators/validate_dual_package.py`) already
   gates every real send.

2. **Full audits — monthly or incident-driven.** The exhaustive audit (full VO
   21/22-check pass, conversion audit, content-ID/channel-identity matrices, model
   compliance sweep) runs on a monthly cadence or when triggered by a specific incident
   or metric regression. It is NOT part of every daily run; the daily run keeps its
   one-pass semantic QA (Law #147 Part 1), and the full audit findings live in the
   manifest, not the email.

3. **Traction cache — 3-day freshness (Law #129).** Refresh `cron_traction_cache.json`
   only if it is missing or older than 3 days. A daily run inside that window reuses the
   cache instead of re-running discovery.

4. **One shared search sweep per daily run.** The daily combined run performs exactly
   ONE 8-search current-market sweep and uses it (plus the cache) for BOTH the morning
   and evening packages, including candidate-specific fact verification. No per-package
   or per-check extra sweeps.

5. **Claude Fable 5 — restricted routing (Law #137).** Fable 5 is reserved for
   long-form flagship scripts (Law #146), major strategy work, and the monthly audit.
   Routine daily Shorts generation is Claude Sonnet 5.0. Never route routine daily work
   to Fable.

6. **Mechanical work uses scripts, not model contexts.** Rendering, logging, state
   updates, and validation are done by deterministic Python tools
   (`validators/validate_dual_package.py`, `tools/append_send_batch.py`,
   `tools/weekly_noop_gate.py`) — not by spinning up additional model contexts. Reserve
   model contexts for genuine creative generation and analysis.

## Weekly early no-op gate (Part 2 recap)

Before the weekly analytics cron discovers or calls any YouTube connector or runs
model-heavy synthesis, it runs `tools/weekly_noop_gate.py`:

```
python3 tools/weekly_noop_gate.py --tree "$(pwd)"
```

- **Exit 0 (NOOP):** zero new published `youtube_video_id`s in
  `cron_tracking/publication_ledger.jsonl` since the last successful run's cutoff. The
  cron writes a small atomic no-op state + `last_noop_summary.json` and exits
  successfully — no connectors, no model synthesis, no email.
- **Exit 10 (RUN_FULL):** new published IDs exist, OR state is missing/corrupt/lacks the
  cutoff field, OR any error occurred. The full analytics workflow runs unchanged.

The gate fails **open**: it only takes the cheap no-op path when it can confidently
prove there is nothing new to analyze. Sent-package history is not treated as
publication proof — only ledger `youtube_video_id` entries count.

## What credit-safe mode must never do

- Never skip or weaken the fail-closed pre-send validator.
- Never reduce the number of daily packages or change posting times.
- Never downgrade creative generation off Sonnet 5.0 to save credits.
- Never let a deterministic script claim it has proven a claim TRUE or a loop
  semantically seamless — those remain model self-attestation plus weekly human review.
- Never take a weekly no-op when it cannot prove zero new published IDs.

## References
- Law #147 (`laws/law_147_credit_safe_mode.md`), Law #141 (colon handoff), Law #139
  (slim email), Law #129 (traction cache), Law #137 (model routing), Law #146 (longform).
- `cron_daily_runtime.txt` STEP 4.5; `cron_analytics_runtime.txt` STEP 0.5.

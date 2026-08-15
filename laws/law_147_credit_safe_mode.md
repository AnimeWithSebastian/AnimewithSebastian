# Law #147 — Credit-Safe Mode (added July 21, 2026)

**Status:** ACTIVE. User-approved and enabled now. Codifies a set of
**quality-preserving** credit-efficiency measures. This law MUST NOT be read as a
license to cut quality. It explicitly does **not** reduce posting frequency, the
Claude Sonnet 5.0 creative routing (Law #137), live-research depth, candidate-specific
source verification, human semantic review, or fail-closed validation. It removes
wasted model contexts and redundant connector calls only.

## Why this changed
Credit spend was going to redundant work, not to quality: multi-pass regeneration
loops, no-op weekly analytics runs that still discovered/called YouTube connectors and
ran model synthesis with nothing new to analyze, non-email dry runs on unchanged code,
and full audits more often than the evidence justified. None of these improved a single
published video. Credit-safe mode reclaims that spend without touching the creative bar.

## Part 1 — One-pass semantic QA before return/send (daily Shorts)
The SINGLE Claude Sonnet 5.0 generation context that drafts the two daily packages MUST
self-audit BOTH packages **before returning** — no second model launch, no extra
research sweep. Each package records a `semantic_qa` object in the run manifest (NOT in
the slim email — Law #139):

- `claim_source_matrix`: every core factual/narrative claim with `core: true|false` and
  `source_urls`. Every core claim MUST cite ≥1 credible **dated** source that is also in
  the package `sources`. **No core claim may rely SOLELY on encyclopedic sources**
  (wikipedia.org / myanimelist.net / fandom.com / wikia.com) — pair an encyclopedic
  source with a non-encyclopedic dated one, else fix or cut the claim.
- `checks`: `vo_word_count`, `cta_adjacency`, `title_search`,
  `blackout_recent_conflicts`, `clip_timing_tiling`, `hook_claim_coverage`,
  `numeric_cross_check`, `source_content_verification`, `law_149_redundancy_check`,
  `ai_slop_pattern_check` — all `true` (ten keys total; `loop_colon_handoff` REMOVED and
  `hook_loop_claim_coverage` RENAMED to `hook_claim_coverage` as of 2026-07-27 — see
  "Loop-strengthening rescinded" below).
- `audited_before_return: true`.

If any check is honestly false, the model FIXES the draft in the same context and
re-audits. It must NEVER attest a check true just to clear it.

### Loop-strengthening rescinded (2026-07-27)
This law originally strengthened Law #141's seamless-loop mandate into a **direct
grammatical colon handoff**: `loop_line` had to end with `":"`, `opening_sentence` had
to complete it without itself ending in `":"`, the two could not be identical, and the
model recorded the read-aloud pair as `final_to_opening_readaloud`. Law #141 itself is
now rescinded (no confirmed platform benefit, documented register-violation cost — see
`laws/law_141_seamless_loop_mechanics.md`), so this strengthening is moot along with
it. The `final_to_opening_readaloud` field and the `loop_colon_handoff` check key are
removed from the `semantic_qa` contract; Part 1's core one-pass self-audit structure
(the ten checks above, `audited_before_return`, and the claim-source matrix) is
otherwise unchanged and remains in force.

### Validator honesty (hard boundary)
`validators/validate_dual_package.py` checks the **presence and shape** of `semantic_qa`
only. It does **NOT and CANNOT** prove that a claim is TRUE. That remains a model
self-attestation (M6) plus a **weekly human spot-check**. Deterministic tooling must
never claim otherwise, in code, comments, prose, or output. (The mechanical
colon-handoff properties this section previously described no longer exist — removed
alongside the Law #141 rescission.)

## Part 2 — Weekly analytics early no-op gate
The weekly analytics cron (`2bb28991`, Sundays 23:30 UTC) runs a cheap deterministic
preflight, `tools/weekly_noop_gate.py`, **before** discovering/calling YouTube
connectors or invoking any model-heavy synthesis. It compares the distinct
`youtube_video_id`s of `event=="published"` rows in
`cron_tracking/publication_ledger.jsonl` against the last successful run's cutoff,
`analytics_processed_video_ids` in `cron_tracking/2bb28991/state.json`.

- **Zero new published IDs** → write a small atomic no-op state + `last_noop_summary.json`
  and exit successfully. NO connector calls, NO model synthesis, NO email.
- **≥1 new published ID** → RUN FULL. The complete analytics workflow is preserved
  (JOINED / PUBLISHED-NO-ANALYTICS / ANALYTICS-NO-LEDGER / SENT-NOT-PUBLISHED).

**Fail open, never fail into a wrong no-op.** Missing state, corrupt JSON, an absent
`analytics_processed_video_ids` field, a malformed cutoff, or any exception all return
RUN_FULL (exit 10). Sent-package history is NOT publication proof — only the ledger's
`youtube_video_id` entries are. A no-op is taken ONLY when the gate can confidently
prove zero new published IDs.

## Part 3 — Waste-prevention policy (documented, no schedule change)
See `docs/CREDIT_SAFE_MODE.md`. In brief: non-email dry runs only after code/runtime
changes or a validation failure; full audits monthly or incident-driven; traction cache
refreshed only if missing or >3 days old (Law #129); ONE shared 8-search sweep per daily
run; Claude Fable 5 restricted to flagship scripts / major strategy / monthly audits
(Law #137); mechanical rendering, logging, and validation use deterministic scripts, not
extra model contexts. **No new scheduled task is added and no cadence is increased.**

## Compatibility
- Schedules unchanged: `daily_combined` daily 23:30 UTC; `2bb28991` Sundays 23:30 UTC.
- Output contracts unchanged: slim dual-package email (Law #139), manifest schema,
  `tools/append_send_batch.py`, weekly analytics state — all preserved. `semantic_qa` is
  an additive manifest field; `analytics_processed_video_ids` + `last_run_mode` are
  additive state fields (historical state without them safely triggers a full run).

## Enforcement / tests
- `validators/validate_dual_package.py` (+ `validators/test_validate_dual_package.py`):
  semantic_qa shape/domain checks, fail-closed. (Colon-handoff mechanics REMOVED
  2026-07-27 alongside the Law #141 rescission — no longer enforced here.)
- `tools/weekly_noop_gate.py` (+ `tools/test_weekly_noop_gate.py`): no-op vs run-full
  decision, fail-open on missing/corrupt/absent-cutoff state, video-id hygiene, no state
  mutation on run-full.

## Files touched by this law
- `laws/law_147_credit_safe_mode.md` (this file); `laws/law_141_seamless_loop_mechanics.md`
  (originally: colon-handoff strengthening — that strengthening is itself rescinded as
  of 2026-07-27, see that file's full rewrite); `docs/CREDIT_SAFE_MODE.md`.
- `validators/validate_dual_package.py`, its fixtures, and tests.
- `tools/weekly_noop_gate.py`, `tools/test_weekly_noop_gate.py`.
- `cron_daily_runtime.txt`, `scheduler/daily_dual_package_task.txt`,
  `templates/package_template.txt`, `cron_analytics_runtime.txt`.

## Rollback
Remove the STEP 4.5 semantic-QA audit + STEP 0.5 no-op gate references from the runtimes,
drop the `semantic_qa` validator block, and delete
`tools/weekly_noop_gate.py`. No historical records are affected. Schedules never changed,
so rollback needs no scheduler action.

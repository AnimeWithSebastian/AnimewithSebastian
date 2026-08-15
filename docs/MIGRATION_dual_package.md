# Migration — Combined Daily Dual-Package Workflow (Law #139)

**Date:** July 15, 2026 · **Status:** user-approved · **Goal:** lower daily credit
use for Hero or Villain with **no change to creative quality**.

## Before → After

| | Before | After |
|---|---|---|
| Scheduled daily tasks | 2 (morning `d43ab889` + evening `57a3c92e`), ~1h apart | 1 (`daily_combined`) |
| Model launches / day | 2 | 1 (Claude Sonnet 5.0, one context) |
| Broad research sweeps / day | 2 full 8-search stacks | 1 shared sweep |
| Traction cache refresh | per-run tendency | ≤ once / 3 days (Law #129) |
| Runtime loaded / day | 2 large runtimes (+ rework/splits) | 1 concise runtime + template + validator |
| Emails | 2 long audit-heavy | 2 slim actionable (audit moved to run log) |
| Preflight | model re-reads/revises | deterministic validator, fail-closed |
| Logging | per-run | 1 atomic dual-event append (shared `batch_id`) |
| Weekly analytics `2bb28991` | Sundays | **unchanged** |

Per-idea fact verification (≥2 dated live sources each), all creative laws, and the
weekly analytics cadence are unchanged. The audit checks are **moved** to the run
manifest / internal run log and enforced by the validator — not removed.

## Update — Per-cut clip timings now REQUIRED (Law #140, July 16, 2026)
The prior no-per-cut-timings preference is **superseded**. Every Shorts package must
now carry per-cut timings: each cut has `duration_sec`, `timeline_start_sec`, and
`timeline_end_sec`; the cuts tile the fixed 30-second edit contiguously (first starts
at 0, each cut's end equals the next cut's start, the final cut ends at 30, and the
durations sum to 30); each package sets `capcut_target_sec` = 30 and
`total_clip_time_sec` = 30. The email renders each cut as `CUT N — X sec
(0:00–0:06): scene — why` and ends the clip plan with `TOTAL CLIP TIME: 30 seconds`.
The validator fails closed on missing timing, wrong end−start arithmetic,
non-contiguous ranges (gap/overlap), a first cut not at 0 or last cut not at 30, a
duration sum ≠ 30, or `capcut_target_sec`/`total_clip_time_sec` ≠ 30. See
`laws/law_140_per_cut_clip_timings.md`.

## Update — Explicit seamless loop now REQUIRED (Law #141, July 16, 2026)
The prior weak "shared-anchor-word" loop acceptance is **superseded**. A loop-back is
no longer accepted just because the final line shares a keyword with the opening.
Every Shorts package must now carry: `opening_sentence` (the VO's exact first
sentence), `loop_line` (the VO's exact final sentence), `loop_transition` =
`loop_line + " " + opening_sentence` (or structured `final_to_opening`),
`loop_read_aloud_pass` = true, and a nonempty `loop_transition_note`. In the clip
plan, EXACTLY the final cut sets `carries_loop_back` = true (all others false) and its
`reason` states it carries the loop into CUT 1 / the opening. The email renders a
visible `LOOP-BACK: <final> -> <opening>` line plus the note. The validator fails
closed on a wrong first/last sentence, a loop_transition that does not equal
loop_line + " " + opening_sentence, a missing/false read-aloud attestation, an empty
note, zero or multiple loop-carrying cuts, a loop carrier that is not the final cut,
or a final cut whose reason omits the loop language. Because deterministic checks
cannot judge semantics, the runtime instructs Claude Sonnet 5.0 to read the
final→opening pair aloud and reject keyword callbacks, topic echoes, or complete
endings that do not naturally feed the opening. See
`laws/law_141_seamless_loop_mechanics.md`.

> **RESCINDED — July 27, 2026.** The mandate described above (loop_line,
> loop_transition, loop_read_aloud_pass, loop_transition_note, the "exactly the final
> cut has carries_loop_back=true" clip-plan requirement, and the "colon handoff"
> strengthening from Law #147) is superseded. This section is preserved verbatim as
> the historical record of what was required between July 16 and July 27, 2026 — it
> is no longer in effect. Current state: `opening_sentence` remains required
> (independent of looping, for the Law #144/#145 hook_line equality check); the VO may
> end on any clean, complete, natural closing thought; a loop-style ending is allowed
> if it arises naturally but is neither required nor specially scored. See the
> rewritten `laws/law_141_seamless_loop_mechanics.md` for the full rescission
> rationale, and Law #147's targeted edit / Law #151's superseded notice for the
> corresponding downstream updates.

## Update — Evidence-based selection, packaging, measurement & long-form separation (Laws #143-#146, July 17, 2026)
Grounded in two evidence files (`channel_analytics_audit_findings.md` — private
analytics; `anime_channel_research_audit_2026-07-16.md` — official/benchmark
research). All additions are **credit-neutral**: they consume the ONE existing shared
sweep + cache and the manifest the run already produces — **no** extra searches or
model launches. Highest-confidence, low-regret invariants only; weekly aggregates are
enforced by the analytics cron, not a single daily run.

- **Law #143 — Topic portfolio & recurring series.** Each package sets `topic_class`
  ∈ {timely, evergreen} (timely ⇒ ≥1 `topic_signals` from currently_airing / premiere
  / chapter / news / seasonal_ranking) and optional `series` `{id, recurring}`. Weekly
  targets (≥9/14 timely, ≥2 recurring-series/week) live in `cron_analytics_runtime.txt`
  — **not a per-run ban**; evergreen is preserved for durable ideas/experiments.
- **Law #144 — Shorts packaging & first-second hook.** Per package: `hook_onscreen_text`
  (on-screen break shown in second 1), `hook_first_second`=true, `hook_line` ==
  `opening_sentence`, `hook_family`; YouTube title **no hashtags, ≤100 chars, show
  keyword within the first 40 chars**. No unverifiable performance claims are asserted.
- **Law #145 — Measurement, attribution & single-variant experiment.** Per package:
  `funnel_status` ∈ {standalone, teaser, flagship_followup} (teaser ⇒ `flagship_url`);
  exactly **2** internal `hook_candidates` + `selected_hook_index`, published
  `hook_line` == the selected candidate; the two daily packages must have **distinct
  published hooks** (publish ONE variant — never duplicate Shorts). Attribution fields
  (topic_class, series, hook_family, format_type, funnel_status) flow to the weekly
  cron for grounded, non-causal breakdowns.
- **Law #146 — Long-form flagship separation.** 8-12-min flagship is a **distinct
  product** with its OWN validator (`validators/validate_longform_flagship.py`): 480-720s
  duration, face-cam PERMITTED, ≥3 chapters, keyword-rich first description line,
  playlist + pinned-next links, comment prompt, **0 or 1-3** teaser Shorts only after a
  `flagship_url` exists (cap lowered from 5 — M5). Shorts-only fields (`capcut_target_sec`, `total_clip_time_sec`,
  `loop_line`, `loop_transition`, `loop_read_aloud_pass`) are **rejected** on a flagship;
  the Shorts validator rejects any package whose `content_type` != "short". *(Note,
  2026-07-27: this cross-reference predates the Law #141 rescission above — those
  Shorts-only fields are now optional/inert on Shorts packages too, not just rejected
  on flagships. The flagship rejection rule itself is unchanged and out of scope for
  the Law #141 rescission; Law #146 was not otherwise touched.)*

## Update — Post-deployment strategic corrections M1-M6 (July 17, 2026)
Grounded in the Fable red-team report (`fable-post-deployment-strategy-audit.md`). These
refine — not replace — Laws #140/#143-#146; the weekly-attribution persistence fix
(commit 6b47ae4) is preserved. All still credit-neutral (no new searches/model launches).

- **M1 — Sanctioned 45-59s duration experiment (Law #140 extension).** A package may set
  `duration_experiment`=true for a **45-59s** edit **only** for list/ranking formats that
  are a recurring series. Gated to **≤1 experiment per batch/week**; the 30s default is
  untouched (`_vo_band(30)` still yields 100-108). VO band + clip tiling scale to the
  edit length. Enforced by `_resolve_edit_target` + the per-batch cap in
  `validate_dual_package.py`.
- **M2 — Viewer-facing recurring-series marker (Law #143 rule 5).** When `series.recurring`
  is true a package must carry `series_public_name` (shown in `youtube_title` or
  `hook_onscreen_text`) and `series_next_line` (shown in `captions`/`pinned_comment`/
  `tiktok_post_text`) — deterministic string-presence checks, fail-closed. Non-recurring /
  null series need no marker.
- **M3 — Sequential hook-family evaluation (Law #145 rule 5).** The unmeasurable same-video
  A/B KPI is retired; the weekly cron accumulates **~8 matured Shorts (≥7d) per
  `hook_family`** and compares distributions. Two internal candidates are still drafted;
  exactly one is published.
- **M4 — Statistical hygiene in the weekly cron.** Breakout/median on **day-7 fixed-age
  views**; stayed-to-watch as **rolling percentile bands** (prefer engaged-view-aligned);
  comments/subscribers per 1k over a **≥4-week rolling window**; historical rows missing
  attribution are **`attribution-unavailable`, excluded from denominators — not zero**.
- **M5 — Quality-over-quota + teaser cap.** Quotas (≥9/14 timely, ≥2 series, cadence,
  teasers) are FLAGS, never a mandate to ship a weak package. Flagship teasers capped at
  **≤3/week** until funnel evidence justifies more (`validate_longform_flagship.py`
  TEASER_MAX=3). Cadence is continuity logic, not a growth guarantee.
- **M6 — Attestations, not verified facts.** `hook_first_second`
  and model-labeled `topic_class` are self-reports: validators enforce presence/schema
  only; the weekly cron spot-checks a 2-3 package sample by hand and never reports them as
  machine-verified. (`loop_read_aloud_pass` was an attestation here too until the Law
  #141 rescission, 2026-07-27, removed it from the checked set — see the rescission
  note above.)
- **Evidence corrections (law rationale).** 8-12 min is a **user sustainability/format
  choice on n=2**, not an observed sweet spot (revisit 720s after 4-6 flagships); the
  no-title-hashtag rule rests on **this channel's cohort data**, distinct from YouTube's
  official *tags* guidance; **cadence is continuity, not a growth guarantee**;
  recurring-series → regular viewers is a **HYPOTHESIS with a week-8 success gate**.

**Not automated (deliberate, with reason):** the research notes a localization/foreign-
language opportunity (~50% of animation fans watch in other languages). This is a real
growth lever but **not** a low-regret deterministic invariant — it needs translation
QA, per-language packaging, and human review, so it is documented as a recommendation
rather than enforced by a validator. Flag for future manual evaluation.

## New / changed files
- `cron_daily_runtime.txt` — authoritative combined runtime (cron `daily_combined`).
- `templates/package_template.txt` — compact per-slot email/package shape.
- `validators/validate_dual_package.py` — deterministic fail-closed preflight validator.
- `validators/test_validate_dual_package.py`, `validators/fixtures/valid_dual_package.json` — tests + fixture.
- `tools/append_send_batch.py` — atomic dual-event logger (shared `batch_id`, distinct `package_id`).
- `laws/law_139_combined_daily_dual_package.md` — governance.
- `laws/law_140_per_cut_clip_timings.md` — per-cut clip timings requirement (supersedes the no-timings rule).
- `laws/law_141_seamless_loop_mechanics.md` — explicit seamless-loop mechanics (supersedes the shared-anchor loop check). **RESCINDED 2026-07-27** — file rewritten in place to record the rescission; see the note above.
- `validators/fixtures/keyword_callback_loop.json` — negative fixture: old keyword-callback loop, was rejected under Law #141. **DELETED 2026-07-27** — once the rejection rule it existed to exercise was removed, a live validator run showed the fixture failing for unrelated, stale reasons (missing `anchors_claim` tagging, stale `checks{}` keys) rather than the loop mechanic it was built to test; a fixture that fails "for real" but for the wrong reason is actively misleading, not a neutral leftover, so it was deleted rather than left orphaned.
- `scheduler/daily_dual_package_task.txt` — scheduled-task prompt text.
- `cron_tracking/daily_combined/` — run manifest + state for the new workflow.
- `cron_morning_runtime.txt`, `cron_evening_runtime.txt` — **preserved intact**; a
  SUPERSEDED-for-future-daily-generation banner was added at the top only.
- `cron_analytics_runtime.txt` — added a batch-awareness note (one batch, two
  packages); **behavior/cadence unchanged**, join still on `youtube_video_id` only.
  Also added the Laws #143-#145 weekly targets/flags (topic mix ≥9/14, recurring
  series ≥2/week, stayed-to-watch <40% re-hook / ≥60% strong, breakout rate >2×
  rolling median, per-1k rates, attribution breakdowns) — grounded, non-causal.
- `laws/law_143_topic_portfolio_and_recurring_series.md`,
  `laws/law_144_shorts_packaging_and_first_second_hook.md`,
  `laws/law_145_measurement_and_single_variant_experiment.md`,
  `laws/law_146_longform_flagship_separation.md` — new governance (evidence-based).
- `validators/validate_longform_flagship.py` + `validators/fixtures/valid_longform_flagship.json`
  + `validators/test_validate_longform_flagship.py` — separate long-form flagship
  validator, fixture, and tests (Law #146).
- `validators/validate_dual_package.py` — extended with the Laws #143-#145 Shorts
  invariants (first-second hook, single-variant experiment, topic/series/funnel,
  clean searchable title, content_type guard); fixtures migrated to the new fields.

Nothing was deleted: all historical runtimes, logs (`sent_scripts_log.json`,
`sent_scripts_events.jsonl`), the publication ledger, blackout/traction/state files
remain in place.

## Cut-over steps (parent agent / scheduler)
1. Apply the scheduled-task prompt in `scheduler/daily_dual_package_task.txt` as a
   single daily task (cron `daily_combined`, 23:30 UTC).
2. Disable/delete the two legacy daily tasks (`d43ab889`, `57a3c92e`).
3. Leave the weekly analytics task (`2bb28991`, Sundays) untouched.

## Verifying a run
- Manifest schema: `python3 validators/validate_dual_package.py --schema`
- Preflight (must exit 0 before sending): `python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json`
- Tests: `cd validators && python3 -m unittest test_validate_dual_package -v`
- Logging: `python3 tools/append_send_batch.py <manifest> --tree <tree> --emails-sent [--git-pushed]`
  (omit `--emails-sent` and it records a failure state and logs nothing — fail-closed).
  The logger also re-runs `validate_dual_package.py` on the manifest and fails closed
  (appends nothing, `status="failed"`) if it does not pass, so a non-conformant
  manifest can never be recorded as a successful send even if STEP 5 was skipped.

## Rollback
The change is fully reversible; no data was destroyed.
1. Re-enable the two legacy daily tasks pointing at `cron_morning_runtime.txt`
   (`d43ab889`) and `cron_evening_runtime.txt` (`57a3c92e`) — both are intact below
   their SUPERSEDED banner (which can stay or be removed; it does not affect logic).
2. Disable the `daily_combined` task.
3. No log/ledger migration is needed — the legacy runs append to the same
   `sent_scripts_log.json` / `sent_scripts_events.jsonl` and read the same
   blackout/traction files. The `batch_id` field added by the combined run is
   additive and ignored by the legacy runs and by the analytics join.
4. Optionally delete `cron_tracking/daily_combined/` if abandoning the workflow;
   leaving it is harmless.

The new-vs-old paths share the same logs and creative laws, so you can also run the
combined task and the legacy tasks are simply not scheduled — switching back is only
a scheduler change.

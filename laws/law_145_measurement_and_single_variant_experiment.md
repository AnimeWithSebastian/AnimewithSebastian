# Law #145 — Measurement, Attribution & Single-Variant Experiment Protocol (added July 17, 2026)

**Status:** ACTIVE. User-approved. Governs how runs are made measurable and how hook
experiments are conducted. Credit-neutral: attribution fields are derived from data
the run already produces; the experiment is drafted inside the one existing model
context. No extra searches or model launches.

## Evidence base (both must agree)
- **Channel analytics:** breakout hits are rare (5.3% of Shorts > 2× the ~1,452 median);
  "stayed to watch" bands (<40% weak, 60%+ strong) and comments/subs per 1k views are
  the actionable levers; only 3 of 57 Shorts broke out — so attribution matters.
- **Official/benchmark research:** recommends testing first-second hooks, then keeping
  what works ("don't change what's working"); warns against over-changing performers
  and against reading too much into small samples.

## Rules
1. **Attribution fields (per package, machine fields).** Every package records
   `topic_class`, `series`, `hook_family`, `format_type`, and `funnel_status`
   (∈ {`standalone`, `teaser`, `flagship_followup`}). These flow into the send log so
   the weekly cron can attribute results by timely-vs-evergreen, recurring series, hook
   family, format, and funnel stage.
2. **Single-variant experiment (publish exactly ONE).** Draft **two** hook candidates
   internally per package (`hook_candidates` = exactly 2, distinct); pick one
   (`selected_hook_index` ∈ {0,1}); the published `hook_line` MUST equal the selected
   candidate. **Never publish duplicate Shorts of the same insight** — the two daily
   packages must have distinct published hooks and distinct shows. The losing candidate
   is kept for the record, not posted. Enforced deterministically, fail-closed.
3. **Teaser gating.** A `teaser` Short must carry a `flagship_url` — teasers are only
   produced **after** a flagship exists (mirrors Law #146).

   **Addendum, added 2026-07-27 (DORMANT scaffolding).** A `teaser` package must also
   carry `flagship_opening_hook_match`, a value echoing the teaser's own `hook_line`,
   enforced by the Shorts validator's teaser branch. **This rule has never fired and
   cannot fire on any real package today**: as of 2026-07-27, `funnel_status` has been
   `"teaser"` on 0 of 166 real sent packages, `flagship_url` has been populated on 0 of
   166, and no flagship has ever been produced on this channel (Law #146's own text).
   The check exists in running validator code now so the schema is ready the day a real
   teaser/flagship pair exists, but it carries no evidence of being correct in practice
   yet — it is schema readiness, not a proven requirement. Shorts-side only;
   `validate_longform_flagship.py` has no matching field today.
4. **Weekly analytics targets/flags (grounded, non-causal).** The weekly cron reports
   and flags, without claiming statistical significance on small samples:
   - **Stayed-to-watch** reported as a **rolling percentile band** (not fixed 40/60
     absolutes — raw retention is replay-inflated since 2025-03-31 and drifts); prefer
     the **engaged-view-aligned** metric where the API exposes it. The 40%/60% cutoffs
     are legacy heuristics, retained only as a coarse fallback when percentile bands
     lack enough matured Shorts.
   - Average % viewed, replays, and **comments/subscribers per 1k views computed over a
     ≥4-week rolling window** (per-1k on a single week is too noisy to act on — M4).
   - Regular vs casual viewers (returning-viewer gap).
   - **Breakout = > 2× the rolling median of day-7 fixed-age views** (compare like-aged
     videos, not raw lifetime views, to avoid right-censoring bias on new uploads — M4);
     report breakout rate.
   - Topic-mix vs Law #143 target (≥9/14 timely) and recurring-series count (≥2/week).

5. **Sequential hook-family evaluation (M3 — replaces same-video A/B).** There is **no
   measurable same-video A/B** on Shorts: two candidates on one upload cannot be
   attributed, and publishing two Shorts fragments the algorithm's signal. Instead, the
   weekly cron evaluates **hook families sequentially** — accumulate **~8 matured Shorts
   (≥7 days old) per `hook_family`**, then compare the distribution of the matured metric
   across families. Rules 1-2 still hold (draft two internal candidates, publish exactly
   one); the "experiment" is the *cross-Short, cross-family* comparison over time, not a
   within-video test. Do not declare a winning family on fewer than ~8 matured Shorts.

## Evidence grade / correction
- **The retired same-video A/B "KPI" was unmeasurable.** Earlier framing implied a
  first-second-hook A/B could be read off a single Short; it cannot. Rule 5 replaces it
  with sequential per-family accumulation (~8 matured Shorts) — the only attributable
  form on a one-upload-per-slot channel.
- **`hook_family` and `topic_class` are model attestations, not verified facts (M6).**
  Deterministic validators check that the field is present and well-formed; they do
  **not** verify the hook truly belongs to the declared family or that a `timely` topic
  is genuinely timely. The weekly cron must spot-check a 2-3 package sample by hand and
  never report these as machine-verified.
- **Historical rows missing attribution are `attribution-unavailable`, not zero (M4).**
  Packages predating the attribution-persistence fix (commit 6b47ae4) have no
  `topic_class`/`hook_family`/etc.; exclude them from denominators rather than counting
  them as a category, or the mix/family rates are silently biased.

## What this law does NOT do
- It does not run A/B by publishing two Shorts (that would fragment the algorithm's
  signal and duplicate content) — the experiment is a single-variant internal
  selection compared sequentially across matured Shorts. It does not assert causal
  significance on small samples.

## Cross-references
- Packaging/hook families: Law #144. Topic/series targets: Law #143.
- Long-form funnel/teasers: Law #146. Combined workflow + logging: Law #139.

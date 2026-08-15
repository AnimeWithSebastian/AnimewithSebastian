# Law #143 — Evidence-Based Topic Portfolio & Recurring-Series Architecture (added July 17, 2026)

**Status:** ACTIVE. User-approved. Governs which ideas the daily dual-package run
selects. Credit-neutral: it constrains selection using the ONE existing shared
research sweep + the ≤3-day traction cache (Law #129). It adds **no** extra searches
or model launches.

## Evidence base (both must agree)
- **Channel analytics** (`channel_analytics_audit_findings.md`): timely/current-market
  ideas outperformed evergreen; there are **0 "regular viewers"** (a returning-audience
  gap); recurring structures — seasonal ranking and episode/scene tests — were among
  the strongest performers.
- **Official/benchmark research** (`anime_channel_research_audit_2026-07-16.md`):
  YouTube ranks search on title/description/content match, so release-timed topics ride
  existing demand; every commentary benchmark's topic engine is release-driven (weekly
  chapters, seasonal premieres, industry news).

## Rules
1. **Topic classification (per package, machine field).** Every Shorts package sets
   `topic_class` ∈ {`timely`, `evergreen`}. A `timely` package must declare ≥1
   `topic_signals` value from {`currently_airing`, `premiere`, `chapter`, `news`,
   `seasonal_ranking`}. Enforced by the deterministic validator, fail-closed.
2. **Weekly portfolio target (NOT a ban).** Across the 14 daily Short slots in a week,
   **≥9 must be `timely`**; up to 5 may be `evergreen`/experiments. This is a *weekly
   aggregate*, so it is enforced/flagged by the **weekly analytics cron**
   (`cron_analytics_runtime.txt`), not by a single daily run. Evergreen is deliberately
   preserved for durable/rewatchable ideas and experiments.
3. **Recurring-series metadata (per package).** Packages may carry a `series` object
   `{"id": <machine-id>, "recurring": true|false}` (or null/omitted for one-offs).
   `id` is a **generic machine field** (e.g. `seasonal_power_ranking`,
   `episode_scene_test`) — not brittle public branding. Enforced well-formed when
   present.
4. **Weekly recurring-series target.** **≥2 packages per week** must belong to a
   recurring `series` using a proven structure (seasonal ranking + episode/scene test
   are the evidence-backed defaults). This addresses the returning-viewer gap without
   forcing the same show; blackout/diversity laws (#125-#128, same-day-same-show ban)
   are unchanged and still win. Enforced/flagged by the weekly analytics cron.
5. **Viewer-facing series marker (M2 — REQUIRED when `series.recurring` is true).** The
   `series.id` in rule 3 is a machine field a viewer cannot perceive; a returning viewer
   cannot form around a series they cannot see. So a recurring-series package must also
   carry `series_public_name` (a short viewer-facing name that appears in the
   `youtube_title` **or** `hook_onscreen_text`) and `series_next_line` (a next-installment
   cue that appears in `captions`, `pinned_comment`, **or** `tiktok_post_text`). Both are
   deterministic string-presence checks, enforced fail-closed by the Shorts validator.
   Non-recurring and one-off (`series` null) packages need no marker.

## Evidence grade / correction
- **Recurring series → regular viewers is a HYPOTHESIS, not a finding.** No series
  existed before this law, so nothing in the data shows series *cause* regulars — rules
  4-5 are a test, not a proven lever. **Success gate:** sustained nonzero 28-day regular
  viewers by **week 8** of recurring-series publishing. If it is still ~0 at week 8,
  redesign the recurrence *mechanism* (rule 5 makes the test fair) rather than raising
  the series quota. Tracked by the weekly analytics cron.
- **2026-07-27 correction (real data, does not change rule 4).** This channel's own
  60-video permutation-tested data shows recurring-format Shorts at 0.317 subs/1,000
  views vs. 0.440 for standalone — standalone is directionally ahead, gap is
  statistically null (p=0.32). This does NOT indicate series content underperforms;
  it indicates the mechanism rule 4 exists to test has not been meaningfully run yet.
  Playlist traffic — the actual returning-viewer mechanism — is ~0 in practice (12
  total views across the whole research window, 0.012% of all views). The week-8
  success gate above must now ALSO check playlist-traffic-share explicitly, not only
  28-day regular viewers, since a subs-conversion number alone cannot distinguish "the
  mechanism worked" from "something else moved the number while playlists stayed
  unused." Rule 4's quota is unchanged by this correction — pending evidence does not
  yet justify removing a test before its own mechanism has been exercised.
- **Timely ≥9/14 is directional but triangulated** (channel winners + benchmarks +
  YouTube search-match ranking). It is a flagged guardrail, not a per-run ban; do not
  tighten beyond 9/14 on current evidence — some "evergreen-looking" content compounds
  for weeks, and the 5-slot evergreen budget preserves that option.

## What this law does NOT do
- It does not ban evergreen content, does not force a specific show, and does not add
  any research spend. Selection consumes the existing shared sweep + cache only.
- It does not invent performance/market claims; targets are portfolio guardrails, not
  causal guarantees.

## Cross-references
- Selection & diversity: Law #125-#128; same-day-same-show ban (Law #139 §4).
- Traction cache cadence: Law #129. Combined daily workflow: Law #139.
- Packaging/hook: Law #144. Measurement/attribution: Law #145.

# Law #140 — Per-Cut Clip Timings Required (added July 16, 2026)

**Status:** ACTIVE. User-approved. **Supersedes the prior "no per-cut timings"
preference** for the combined daily dual-package workflow (and its expression in
Law #77 / Law #139 §6). Every Shorts package now REQUIRES per-cut clip lengths and
a total clip duration.

## What changed
The earlier rule banned per-cut durations/timings on the clip plan (user
preference). The user has explicitly reversed that. From now on every CapCut clip
plan must show, for each cut, an exact length and its cumulative position on the
fixed 30-second edit, plus a stated total.

## Requirement

> **INTERNAL CONTRADICTION RESOLVED 2026-08-14 (full law audit).** The Requirement and
> Enforcement sections below were written against the old fixed 30-second edit and still
> say `capcut_target_sec` = 30 / `total_clip_time_sec` = 30 / "the final cut ends at 30"
> / "TOTAL CLIP TIME: 30 seconds" as hard, exact values. **The Stage 2 change of
> 2026-08-09 (see "Duration experiment (M1) — RETIRED" below) made edit length
> open-ended across 20–180s for every package**, and the running code agrees:
> `validate_dual_package.py` defines `MIN_EDIT_SEC = 20.0` / `MAX_EDIT_SEC = 180.0` and
> resolves the target via `_resolve_edit_target`, with no hard 30 anywhere. Law #62's
> own CTA addendum also already states the open-ended `[20,180]` range.
>
> **Read every literal `30` in the two sections below as `capcut_target_sec` (the
> resolved edit length for that package).** The tiling rule itself is unchanged: cuts
> tile `0 → capcut_target_sec` contiguously with no gaps or overlaps, durations sum to
> the resolved target, and `total_clip_time_sec` equals it. The literal text is left in
> place rather than rewritten because per authority order the validator governs, and
> silently editing the number would erase the record of the drift.

For **every** clip (cut) in **every** package:
- `duration_sec` — the cut's length in seconds (positive number).
- `timeline_start_sec` and `timeline_end_sec` — the cut's cumulative range on the
  edit (`timeline_end_sec - timeline_start_sec` must equal `duration_sec`).
- Displayed in the email as a clear cumulative range, e.g. `CUT 1 — 6 sec
  (0:00–0:06): scene — why`.

For **every** package:
- `capcut_target_sec` = 30 (the fixed edit length; exactly 30).
- `total_clip_time_sec` = 30.
- The cuts must **tile the edit contiguously with no gaps or overlaps**: the first
  cut starts at 0, each cut's end equals the next cut's start, the final cut ends at
  30, and `sum(duration_sec)` equals `capcut_target_sec` and equals exactly 30.
- The email must print `TOTAL CLIP TIME: 30 seconds`.

The fixed 30-second edit (Law #138 — VO fills the fixed edit) is unchanged; this law
adds the explicit per-cut timeline on top of it. All other creative laws
(100–108-word VO, exact CTA placement, loop line, face-cam split-screen layout
per Law #134 Stage 2, separate production sections, ≥2 dated sources, etc.)
remain fully enforced.

## Duration experiment (M1) — RETIRED (Stage 2, 2026-08-09)
The `duration_experiment` field and its 45-59s/list-ranking/recurring-series/≤1-per-batch
gate described here are fully retired, not repurposed or kept as a soft signal. Edit
length is now genuinely open-ended across **20-180 seconds** for every package — any
format, recurring or not, may use any length in that range with no special flag, no
format/series gate, and no per-batch cap. `capcut_target_sec`/`total_clip_time_sec` simply
take the resolved edit length directly; the cuts tile `0→capcut_target_sec` contiguously
as before, and the VO band scales linearly with the edit at the same calibrated rate
(3.3-3.6 w/s; `_vo_band(30)` still yields exactly 100-108, unchanged). There is no longer
a distinction between a "default" length and an "experimental" one. Enforced by
`validate_dual_package.py` (`_resolve_edit_target`, with `MIN_EDIT_SEC=20.0` /
`MAX_EDIT_SEC=180.0`; the M1 per-batch experiment cap no longer exists).
Cross-ref: Law #143 (recurring series — unaffected, still governs its own M2 viewer-facing
markers independently of edit length), Law #145 (measurement), Law #138 (ceiling updated
to 180 sec in the same Stage 2 pass).

## Enforcement
`validators/validate_dual_package.py` fails closed if any cut is missing timing,
if `end - start != duration_sec`, if the ranges are non-contiguous (gap/overlap),
if the first cut does not start at 0 or the last does not end at 30, if the
durations do not sum to 30, or if `capcut_target_sec`/`total_clip_time_sec` is not
exactly 30. Covered by `validators/test_validate_dual_package.py` (missing duration,
non-contiguous ranges, wrong duration arithmetic, total not 30, wrong
total_clip_time_sec, capcut_target not 30).

## Files touched by this law
- `laws/law_140_per_cut_clip_timings.md` (this file).
- `validators/validate_dual_package.py`, `validators/fixtures/valid_dual_package.json`,
  `validators/test_validate_dual_package.py`.
- `cron_daily_runtime.txt`, `templates/package_template.txt`,
  `scheduler/daily_dual_package_task.txt`, `docs/MIGRATION_dual_package.md`,
  `laws/law_139_combined_daily_dual_package.md` (per-cut-timing language superseded).

## Rollback
Revert to the no-timings rule by restoring the prior validator clip check, removing
the `duration_sec`/`timeline_*`/`total_clip_time_sec` requirements, and re-adding the
"no per-cut timings" language. No historical records are affected by this law.

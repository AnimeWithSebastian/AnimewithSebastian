# Underperformance deprioritization rule — enforcement tracking

Tracks whether the underperformance-deprioritization rule stated in Law #61 and
Law #65 has any real enforcement, separate from whether it is correctly documented.

## Finding 1 — the rule is real and stated identically in two places

- `laws/law_61_analytics_feedback_loop.md` ("Format Priority Updates"): "If a
  format consistently underperforms → it drops in priority for 2 weeks before
  being re-evaluated."
- `laws/law_65_content_adaptation_loop.md` ("What gets adjusted based on
  analytics"): "Format types that consistently underperform → deprioritized for
  2 weeks."

This is not an invented or misremembered rule — it is written down, in force, and
consistent across both source files.

## Finding 2 — zero code enforcement exists anywhere

Confirmed via direct search: no match for this logic (or the "2 weeks" /
"deprioritiz*" concept generally) in:
- `validators/*.py` (any validator file)
- `tools/*.py` (any tool script)
- `cron_daily_runtime.txt` (the daily selection runtime)
- `cron_analytics_runtime.txt` (the weekly analytics runtime), beyond the report
  step described in Finding 4 below

## Finding 3 — the state file this rule depends on does not exist

Both law files describe the mechanism as reading/writing
`analytics_performance_log.json`. That file does not exist anywhere in the repo
(confirmed via direct filesystem search). There is nothing for a "2 weeks"
deprioritization window to be tracked against, even manually.

## Finding 4 — the weekly cron only reports; it does not act

`cron_analytics_runtime.txt`'s STEP 5 ("FLAG WHAT TO CHANGE") lists underperforming
format/show combos under a heading explicitly marked "RETIRE (do not delete — just
flag for the report)." This step produces a report line, not a state change. The
daily selection runtime (`cron_daily_runtime.txt`) never reads any deprioritization
state and has no logic that would lower a format's odds of selection based on
recent underperformance.

## Net effect

The rule is real and intentional — it is not vague aspiration, it is written as a
concrete mechanism (2-week deprioritization window) in two law files. But nothing
in the repo currently enforces it, tracks the 2-week window, or even records
whether a format was ever actually deprioritized under this rule. This is
identical in shape to the ACTIVE EVERGREEN WEIGHTING audit-trail gap documented in
docs/EVERGREEN_WEIGHTING_TRACKING.md: a real mechanism with no way to confirm or
deny it has ever fired. The difference here is one step further — evergreen
weighting at least has runtime instruction text describing how to check/apply it;
this rule has no instruction anywhere for how the daily or weekly runtime should
actually read or write the missing state file, only a stated policy outcome.

**Not proposed as a fix in this entry** — per standing rule, no code change without
explicit go-ahead and diff review. A future fix would need to: (a) decide whether
`analytics_performance_log.json` should be created and by which cron, (b) add
runtime instruction text (daily and/or weekly) describing when to read/write it,
and (c) add a corresponding audit field to run_manifest.json so this tracking file
can be updated with confirmed/denied outcomes instead of the static gap-only entry
this currently is.

## Log

| Date | Finding | Result |
|---|---|---|
| 2026-07-26 | Initial audit (Law #85 monetization review) | Rule confirmed real, zero enforcement, zero state file, zero runtime instruction — gap documented, no fix applied |

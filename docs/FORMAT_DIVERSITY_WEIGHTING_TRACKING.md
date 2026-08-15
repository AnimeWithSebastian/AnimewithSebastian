# ACTIVE FORMAT-DIVERSITY WEIGHTING — real-world exercise tracking

Tracks whether the ACTIVE FORMAT-DIVERSITY WEIGHTING step (cron_daily_runtime.txt,
added as an addition to Step 3 alongside ACTIVE EVERGREEN WEIGHTING) has ever
actually been exercised in a real daily send, separate from whether a package
simply happens to carry a non-overused format_type for unrelated reasons.

## Finding 1 — mechanism has zero audit trail from day one

Same gap as documented in docs/EVERGREEN_WEIGHTING_TRACKING.md: nothing in
run_manifest.json, the manual build scripts, or any other tracked artifact
records:
- the trailing-14 format_type counts this step is supposed to compute from
  sent_scripts_log.json before each run, or
- whether the downweighting path was actually invoked for either of the day's
  two slot selections, versus the slot being filled by an unrelated selection
  path, or
- whether a format was ever actually overused (>=5/14) at the time of any given
  run, which would be needed to even test whether downweighting should have
  applied.

**Practical consequence:** identical to the evergreen-weighting gap — there is
currently no way to confirm or deny, for any past or future run, whether this
mechanism has ever fired. This tracking doc is created at the same time as the
mechanism itself specifically to avoid the blind-spot pattern already found
twice tonight (evergreen weighting, underperformance-deprioritization) where a
real mechanism runs unaudited for weeks before anyone notices there's no way to
check it.

## Update 2026-08-11 — audit field SHAPE now defined in the schema (still not populated by any run)

Design proposal approved 2026-08-11 (same day the FACT_DROP trailing-14 count
first crossed this mechanism's own 5-of-14 threshold — see run_manifest.json
batch_id cfbfaaaf-def7-4775-b643-d27667ea9000). The field shape below is now
documented in validators/validate_dual_package.py's SCHEMA string (PACKAGE
block, key `format_diversity_weighting`):

```
"format_diversity_weighting": {
  "trailing_format_counts": {"FORMAT_TYPE_TOKEN": 0},
  "threshold": 5,
  "overused_format": "FORMAT_TYPE_TOKEN or null",
  "downweighting_applied": false,
  "eligible_candidates": ["FORMAT_TYPE_TOKEN", "..."],
  "selected_format": "FORMAT_TYPE_TOKEN",
  "changed_outcome": false
}
```

`changed_outcome` is the field that actually answers the open question this
doc exists to track — not just "was the rule consulted" (`downweighting_
applied`) but "did the rule ever cause a DIFFERENT candidate to win than would
have won on Law #85 hierarchy rank alone." A mechanism can be consulted every
run and still be provably inert on outcomes if `changed_outcome` never turns
true — this is the exact ambiguity Finding 1 above describes, now given a
concrete field to resolve it.

**Still true, unchanged by this update:** this is schema documentation only.
No check in validate_dual_package.py requires this key's presence, shape, or
internal consistency, and cron_daily_runtime.txt's STEP 3 is NOT YET instructed
to compute or write these values. Until that separate, deferred runtime-wiring
round happens, every past AND future run will continue producing manifests
with this key absent, and Finding 1's practical consequence ("no way to confirm
or deny... whether this mechanism has ever fired") remains fully in force. This
update only removes the "what would the field even look like" uncertainty from
a future fix — it does not populate any real data point.

## Log

| Date | post_date | batch_id | Result |
|---|---|---|---|
| 2026-07-26 | — | — | Mechanism created 2026-07-26; no send yet to evaluate. Baseline entry only. |
| 2026-08-11 | 2026-08-12 | cfbfaaaf-def7-4775-b643-d27667ea9000 | NOT CONFIRMED — FACT_DROP real trailing-14 count reached 5/14 (the exact threshold) on this batch per independent audit, but run_manifest.json for this batch carries no format_diversity_weighting key (predates this schema addition), so whether downweighting was consulted or changed the outcome for this specific send is unknown and unrecoverable after the fact. Audit field SHAPE defined this same day for future runs; still not wired into STEP 3 execution. |

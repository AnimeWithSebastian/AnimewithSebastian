# ACTIVE EVERGREEN WEIGHTING — real-world exercise tracking

Tracks whether the ACTIVE EVERGREEN WEIGHTING step (cron_daily_runtime.txt, added
as an addition to Law #143's TOPIC PORTFOLIO) has ever actually been exercised in a
real daily send, separate from whether a package simply happens to carry
topic_class: evergreen for unrelated reasons.

## Finding 1 — 2026-07-27 batch (Gachiakuta) is NOT a confirmed data point

batch_id 05138946-731b-482c-bb1b-5533c17e062b, post_date 2026-07-27, MORNING slot,
show: Gachiakuta, is the first genuinely evergreen send (topic_class: evergreen)
since the evergreen-weighting step was added to the runtime. However:

- The weighting step names two eligible format families for the upweighted
  candidate: ORIGIN_STORY, or SLEPT_ON/HIDDEN_GEM ("these are Law #85's own stated
  evergreen/brand-authority formats").
- The Gachiakuta package's format_type is CHARACTER_DIVE — not one of the two
  eligible formats.

**This cannot be credited as a confirmed exercise of the new weighting mechanism.**
It may simply reflect the pre-existing TOPIC PORTFOLIO evergreen allowance ("a run
may legitimately be evergreen for a durable idea/experiment"), which predates
tonight's weighting addition and applies independent of it. There is no positive
evidence either way — this entry exists to prevent the send from being
mischaracterized as validation of the fix in any future summary or report.

## Finding 2 — the weighting mechanism has zero audit trail

Independent of Finding 1: nothing in run_manifest.json, the manual build scripts, or
any other tracked artifact records:
- the trailing-14-entries evergreen count the weighting step is supposed to compute
  from sent_scripts_log.json before each run, or
- whether the upweighting path was actually invoked for either of the day's two
  slot selections, versus the slot being filled by an unrelated selection path.

**Practical consequence:** there is currently no way to confirm or deny, for any
past or future run, whether this mechanism has ever fired — independent of whether
any given package happens to superficially qualify (right topic_class, right
format_type). The fix may be working invisibly, or may never be exercised in
practice, and nothing in the repo can currently distinguish those two states.

## Update 2026-08-11 — audit field SHAPE now defined in the schema (still not populated by any run)

Design proposal approved 2026-08-11, in the same review round that defined the
sibling format_diversity_weighting field (see
docs/FORMAT_DIVERSITY_WEIGHTING_TRACKING.md). The field shape below is now
documented in validators/validate_dual_package.py's SCHEMA string (PACKAGE
block, key `evergreen_weighting`):

```
"evergreen_weighting": {
  "trailing_evergreen_count": 0,
  "threshold": 5,
  "upweighting_eligible": false,
  "eligible_candidate_format": "ORIGIN_STORY | SLEPT_ON | HIDDEN_GEM | null",
  "upweighting_applied": false,
  "selected_topic_class": "timely | evergreen",
  "changed_outcome": false
}
```

`changed_outcome` is designed to resolve exactly the ambiguity Finding 1 above
describes: it is true ONLY if upweighting caused an evergreen candidate to win
a slot that would otherwise have gone timely. Had this field existed on the
2026-07-27 Gachiakuta batch, `eligible_candidate_format` would show whether an
ORIGIN_STORY/SLEPT_ON/HIDDEN_GEM candidate was even in play that day —
resolving Finding 1's open question directly instead of requiring the manual
post-hoc inference this doc had to fall back on.

**Still true, unchanged by this update:** this is schema documentation only.
No check in validate_dual_package.py requires this key's presence, shape, or
internal consistency, and cron_daily_runtime.txt's STEP 3 is NOT YET instructed
to compute or write these values. Until that separate, deferred runtime-wiring
round happens, every past AND future run will continue producing manifests
with this key absent, and Finding 2's practical consequence ("no way to confirm
or deny... whether this mechanism has ever fired") remains fully in force. This
update only removes the "what would the field even look like" uncertainty from
a future fix — it does not populate any real data point, including for
tonight's own Frieren/Shonen Jump batch (cfbfaaaf-def7-4775-b643-d27667ea9000),
which also predates this schema addition and carries no evergreen_weighting
key.

## Log

| Date | post_date | batch_id | Result |
|---|---|---|---|
| 2026-07-26 | 2026-07-27 | 05138946-731b-482c-bb1b-5533c17e062b | NOT CONFIRMED (Finding 1) — format_type mismatch, no audit trail (Finding 2) |
| 2026-08-11 | 2026-08-12 | cfbfaaaf-def7-4775-b643-d27667ea9000 | NOT CONFIRMED — no evergreen_weighting key present (predates this schema addition); unknown and unrecoverable after the fact whether upweighting was consulted for this batch. Audit field SHAPE defined this same day for future runs; still not wired into STEP 3 execution. |

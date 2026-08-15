================================================================================
LAW #77 — CLIP DURATION REQUIREMENT
VERSION: 1.0 — June 25, 2026
APPLIES TO: All crons (57a3c92e, d43ab889) + manual runs
CREATED: After clip instruction blocks were being sent without per-cut durations or total video runtime, leaving the creator without a clear edit order.
PURPOSE: Every clip instruction block must state total video runtime AND per-cut duration in seconds. No guessing. No missing durations.
================================================================================

## CORE RULE

Every STEP 11 clip instruction block MUST include:

1. TOTAL VIDEO RUNTIME — stated at the very top of the clip block, before any cuts
2. Duration per cut — every single cut must list its duration in seconds

## FORMAT REQUIREMENT

At the top of every STEP 11 block:

  TOTAL VIDEO RUNTIME: ~XX sec

For every cut:

  CUT X — [Scene description] | Duration: X sec

## DURATION FORMULA (from VO word count)

  60–70 words  →  ~25–28 sec total runtime
  71–80 words  →  ~29–33 sec total runtime
  81–90 words  →  ~34–37 sec total runtime

CUT 1 brand stamp = always 3 sec.
Most cuts = 3–6 sec each.
No single cut may exceed 8 sec.

## VIOLATION

A clip block that:
  - Does not state total video runtime at top → LAW #77 VIOLATION
  - Has any cut without a "| Duration: X sec" label → LAW #77 VIOLATION

## WHAT TRIGGERED THIS LAW

June 25, 2026 — Clip instruction blocks sent without per-cut durations. Creator flagged
that they need to know how long each cut should be in the edit — not just what clip to use.
Without durations the edit order is incomplete and useless for CapCut production.

SELF-HEAL SOURCE: /home/user/workspace/laws/law_77_clip_duration.md
================================================================================
END OF CLIP DURATION LAW — LAW #77
================================================================================

================================================================================
LAW #77 — CLIP DURATION REQUIREMENT
VERSION: 1.0 — June 25, 2026
APPLIES TO: All crons + manual runs. [Cron IDs corrected 2026-08-14 during a full
            law audit: this line named the retired morning/evening crons
            `57a3c92e` and `d43ab889`, which Law #139 replaced on 2026-07-15 with
            the single `daily_combined` run. The law itself still applies in full —
            only the cron identifiers were stale.]
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
  ^^^ SUPERSEDED by Law #82 (June 28, 2026) — banner added 2026-08-14 during a full law
  audit. Law #82 permanently BANS brand stamps, logo animations and intro sequences:
  "CUT 1 in every clip plan = first content clip, no exceptions," and "Runtime total
  video runtime calculation does NOT include any intro time (none exists)." This line
  is the direct opposite and had stood unmarked for ~7 weeks. DO NOT budget 3 seconds
  for a brand stamp. CUT 1 is the first real content clip with VO already running.
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

SELF-HEAL SOURCE: laws/law_77_clip_duration.md
  [Path corrected 2026-08-15 during a law audit. This read
  "/home/user/workspace/laws/law_77_clip_duration.md" — the old sandbox
  layout, which does not resolve in this repo-based checkout. Per Session Fixes
  FIX 25 the GitHub repo is the authoritative source, so the path is now
  repo-relative. The self-heal instruction itself is UNCHANGED — only the path
  was stale.]
================================================================================
END OF CLIP DURATION LAW — LAW #77
================================================================================

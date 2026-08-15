================================================================================
AIRING STATUS ENFORCEMENT LAW — LAW #53
VERSION: 1.0 — June 7, 2026
APPLIES TO: All crons + manual runs. [Cron IDs corrected 2026-08-14 during a full
            law audit: this line named the retired morning/evening crons
            `57a3c92e` and `d43ab889`, which Law #139 replaced on 2026-07-15 with
            the single `daily_combined` run. The law itself still applies in full —
            only the cron identifiers were stale.]
CREATED: After Steel Ball Run VO referenced manga-only content (Love Train,
         Lucy Steel, D4C) that has not aired in animated form.
PURPOSE: Zero VO lines can reference content that does not exist yet in anime.
         Manga content, unaired arcs, and future episodes are HARD BLOCKED.
================================================================================

## THE RULE

Before any research or VO is written for any show, confirm:
1. How many episodes have actually aired
2. Whether the show is split-cour or stage-based (each stage treated separately)
3. The exact episode ceiling — VO cannot reference anything beyond it

This check runs BEFORE show selection is finalized. If the angle requires
content that hasn't aired — the angle is blocked, not just the line.

## HARD STOP CONDITIONS

Any of these = DO NOT SEND:
- VO references a scene from an episode that has not aired
- VO references manga-only content framed as "in the show"
- VO references a future arc, future transformation, or unaired plot point
- VO uses language like "what happens next" as if it has already aired when it hasn't

## SPLIT-COUR / STAGE ENFORCEMENT

Split-cour shows and stage-based releases (like Steel Ball Run) are treated
as currently airing with a hard episode ceiling per stage.

STEEL BALL RUN — CURRENT STATUS:
Only Stage 1 (Episode 1) has aired on Netflix.
Stage 2 begins Fall 2026.
BLOCKED CONTENT (manga-only, not yet animated):
  - D4C (Dirty Deeds Done Dirt Cheap)
  - Love Train
  - Tusk Act 1–4
  - President Valentine's final arc
  - Lucy Steel mechanic
  - Golden Spin (full version)
  - Johnny's resolution

## HOW TO VERIFY

Run this search before any VO is written for a show with potential airing gaps:
"[show name] episodes aired [current year] site:myanimelist.net OR site:anilist.co"

For split-cour:
"[show name] part 2 release date [year]"
"[show name] how many episodes season [N]"

Source must be a confirmed MAL, AniList, or official page — not fan speculation.

## WHAT SHOWS UP IN THE EMAIL

Add one line to the Research Note block:
AIRING STATUS CHECK: [Show] — [N] episodes aired as of [date] — VO respects episode ceiling ✓
or
AIRING STATUS CHECK: [Show] — FLAGGED — angle requires unaired content — show swapped to [new show]

## AUTO-FAIL CHECK

Before every send:
[ ] Is selected show currently airing or recently finished?
[ ] If split-cour: which stage? What is the episode ceiling?
[ ] Does any VO line reference content beyond the ceiling?
[ ] If Steel Ball Run: none of the blocked content listed above appears anywhere

SELF-HEAL SOURCE: /home/user/workspace/laws/law_53_airing_status.md
================================================================================
END OF AIRING STATUS ENFORCEMENT LAW — LAW #53
================================================================================

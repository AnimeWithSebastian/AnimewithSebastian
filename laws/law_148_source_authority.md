# Law #148 — Source Authority, Attribution Accuracy, and Conflict Handling (added July 24, 2026)

**Status:** ACTIVE — HARD LAW
**Added:** July 24, 2026
**Applies to:** Every `core: true` claim in every package's `semantic_qa.claim_source_matrix` (daily_combined and long-form alike).

For every claim marked `core: true` in the claim_source_matrix:

1. SOURCE STRENGTH OVER MINIMUM SUFFICIENCY. Before finalizing a citation, check whether a primary
   or trade-press source covers the same fact, versus a fan aggregator, roundup blog, or forum post.
   Prefer the stronger source even if a weaker one already technically satisfies the "one dated,
   non-encyclopedic source" rule (Law #147). If unsure which source is stronger, verify before
   deciding — do not default to whichever source was found first.

1a. SOURCE QUALITY TIERS (added July 28, 2026 — formalizes the informal preference already stated
    in point 1 above). When comparing sources for the same claim, apply these four tiers, from
    strongest to weakest:

    TIER 1 — OFFICIAL/PRIMARY: Platform statements, studio/publisher announcements, official
    trailers, official social accounts of the studio/platform/creator, direct creator interviews
    conducted by a credentialed outlet.

    TIER 2 — ESTABLISHED ENTERTAINMENT/JOURNALISM: Named outlets with editorial standards and real
    bylines (e.g. ScreenRant, Anime News Network, Crunchyroll News, trade press). Must have an
    identifiable author and publication, not an unattributed aggregator page.

    TIER 3 — RECAP/ANALYSIS CONTENT: A specific, checkable claim from a video or article that must
    be verified by actually fetching/watching it directly — never assumed from a title, thumbnail,
    or search snippet alone (this ties directly into STEP 4.5 point 1.7's source content
    verification requirement).

    TIER 4 — FAN FORUMS/REDDIT/COMMUNITY DISCUSSION: Useful only as corroboration that a claim is
    plausible or as a signal that a genuine debate/controversy exists among viewers. NEVER
    sufficient alone to support a factual claim — must be paired with a Tier 1-3 source for the
    underlying fact itself.

    RULE: When a higher tier and lower tier source are both available for the same claim, prefer
    and cite the higher tier source. A lower-tier source already in use should be replaced with a
    higher-tier one if one is found during the same research pass, even if the lower-tier source
    technically satisfies the minimum sourcing requirement (Law #147). This does not retroactively
    require re-opening claims already sourced and shipped — it applies at the time of active
    sourcing/citation decisions, consistent with point 1's existing "before finalizing a citation"
    scope.

    Tiering does NOT override Law #154 (conflict-of-interest exclusion) — a Tier 1 source that is
    also a conflict-of-interest source under Law #154 is still excluded entirely, regardless of
    its tier.

2. EXACT ATTRIBUTION. Attribute claims exactly as the source states them. Do not blend or
   redistribute credit across a different or additional party than the source names (e.g., do not
   credit a platform-wide policy to a single spokesperson the source never names, and do not credit
   an individual creator's statement to "the studio" or "the platform" as a whole). Re-check the
   claim against the actual source sentence at citation time — not against general familiarity with
   the topic or a recalled paraphrase from earlier in the research sweep.

3. NO SILENT CONFLICT RESOLUTION. When sources disagree on a number, date, count, or name that is
   central to the hook, do not silently pick one and move on. Either (a) flag the uncertainty in the
   pinned comment, or (b) pick the better-sourced version per Law #148.1 and note why in the
   claim_source_matrix. Never present a contested fact as settled when the sources themselves are
   split.

NOTE ON LAW #148 vs. THE ONE-SWEEP RULE: the daily_combined "one shared research sweep" limit
(cron_daily_runtime.txt Step 3) applies to IDEA DISCOVERY only. Claim-verification searches under
Law #148 — checking source authority, checking for conflicting numbers on an already-selected
idea — are a separate, always-allowed step and do NOT count against the one-sweep limit.

---
END Law #148 — SOURCE AUTHORITY, ATTRIBUTION ACCURACY, AND CONFLICT HANDLING | Anime With Sebastian | July 24, 2026

# Law #84 — Deep Research Mandate (Video Recommendations)
**Added:** June 28, 2026
**Status:** ACTIVE — with a scoped supersession inside the automated `daily_combined`
cron only (policy decision, July 24, 2026; documented in the Law #147 style).
**Triggered by:** User called out that video recommendations were NOT based on actual trending data, views, engagement, or subscriber behavior. Agent admitted shortcut. Law created to prevent recurrence permanently.

---

## SUPERSESSION NOTE — scope limited to `daily_combined` (added July 24, 2026)

Inside the automated `daily_combined` cron ONLY (`cron_daily_runtime.txt`), Law #84's
original **8-searches-PER-IDEA** minimum is superseded by Law #147/#148's credit-safe
mode: `daily_combined` runs **ONE shared 8-search sweep per day covering BOTH ideas**,
rather than a full separate 8-search stack for each. This is a **credit-reduction**
change to how the research budget is spent, not a reduction in verification depth —
Law #78's existing per-idea candidate-specific verification (≥2 credible live sources
dated per idea) is **UNCHANGED and still required for EACH idea** on top of the shared
sweep.

This supersession is **scoped to `daily_combined`'s automated context only**. Law #84's
original 8-search-per-idea minimum remains **FULLY ACTIVE, with no supersession**, for
any manual or ad-hoc "give me video ideas" / "what should I make today" / replacement-
idea request made OUTSIDE the automated daily cron — exactly as the "Applies To"
section below already specifies. Nothing about Law #84 is weakened outside
`daily_combined`.

---

## The Law

**Every video recommendation presented to the user — for any slot, any format, any show — MUST be grounded in a full 8-search research stack run in that session. Memory, pattern-matching, training data, and assumed trends are BANNED as a basis for any recommendation.**

Video ideas are not creative suggestions. They are research conclusions. Every idea must be earned by the data.

---

## The 8-Search Stack (ALL REQUIRED — no shortcuts)

**SEARCH 1 — Trending anime tonight**
What is actually moving in the anime community right now? Pull from Reddit (r/anime, r/AnimeSuggest), AniTrendz, Anime Corner, YouTube trending, Twitter/X anime trending — dated within 48 hours. Cannot be skipped.

**SEARCH 2 — Show-specific traction on target shows**
For each candidate show: what is the active search volume, thread activity, and YouTube engagement looking like RIGHT NOW? Pull live sources. Not assumed.

**SEARCH 3 — Fandom gaps**
What is the fandom talking about that has NOT been made into a short yet? Where is the discourse ahead of the content? This is the opportunity window.

**SEARCH 4 — Consensus check / saturation**
What angles are ALREADY covered? What has been posted by multiple creators this week? Any angle that is saturated = BLOCKED. Must be verified before recommending.

**SEARCH 5 — Format research on target shows**
What formats are performing on this show right now? FACT_DROP, CHARACTER_DIVE, WRONG_TAKE, COMMENTARY — which is actually getting views and engagement on this specific show at this specific moment?

**SEARCH 6 — Platform engagement signals**
What engagement behavior is active on this content? Comments, shares, saves, reply threads? High comment activity = more recommend-worthy. Verified per show, not assumed.

**SEARCH 7 — Niche-wide format traction**
Across the anime Shorts niche tonight: what formats are overperforming? What duration? What hook style? This determines format recommendation independent of show-specific data.

**SEARCH 8 — Competitor check on specific angles**
Before any angle is presented: has a competitor posted this angle this week? Check YouTube Shorts search, TikTok search, and known competitor channels. CLEAR or BLOCKED with evidence.

---

## What Every Recommendation Must Include

Each video idea presented to the user must contain ALL of the following:

1. **Show** — name and current airing/release status (verified, dated source)
2. **Why now** — live traction signal with source URL and publication date
3. **Format** — which of the 19 formats and why this format fits this show at this moment (from SEARCH 5 or SEARCH 7)
4. **Angle** — the specific angle, NOT the generic one. Must pass the GAP test (not already covered by competitors)
5. **Competitor status** — CLEAR or BLOCKED with evidence from SEARCH 8
6. **Engagement signal** — views, comments, shares, or fandom activity metric that justifies this show being selected over others tonight
7. **Conversion relevance** — does this show/angle have subscriber conversion potential based on channel analytics? (benchmark: 4PX-qQRsqjY = 0.153%)

If any of the 7 elements cannot be sourced from live research run in-session → **idea is BLOCKED. It does not get presented.**

---

## The Failure Pattern

**WRONG:**
Agent picks HxH because it's "popular." Agent picks Mushoku Tensei S3 because "it's premiering soon." Neither was verified against live engagement data, competitor activity, or format traction. Ideas presented as finished recommendations.

**RIGHT:**
Agent runs all 8 searches. HxH Ch411 chapter drop confirmed with 567-day hiatus context verified. Specific revelation (Woble does not qualify for succession war) confirmed as the non-saturated angle. Competitor check shows "HxH is back" coverage exists but Woble revelation gap is CLEAR. FACT_DROP format confirmed as performing on HxH-adjacent content. All 7 elements present. Idea presented.

---

## Hard Rules

- **Minimum search count per session: 8** — never fewer for a full recommendation set
- **No idea may be presented before SEARCH 4 (saturation check) is complete**
- **No idea may be presented before SEARCH 8 (competitor check) is complete**
- **If only 1–2 searches were run, the session is incomplete — run remaining searches before presenting options**
- **Agent must state which searches were run when presenting final recommendations**
- **If user asks "are these based on deep research?" — agent must name every search run, what it found, and which source confirmed it**

---

## Relationship to Other Laws

- **Law #52:** Never source factual claims from memory. Law #84 extends this upstream — the *selection* of video ideas must also be sourced from live data, not memory.
- **Law #75:** Research Before Recommendations (3-search minimum). Law #84 supersedes and expands Law #75 — the minimum is now 8 searches for any full recommendation package. Law #75 remains active for emergency/quick checks only.
- **Law #73:** Every clip reference must be verified via live source. Law #84 governs the layer before clips — the idea selection phase.
- **Law #78:** Every source must include publication date. 90+ days = flag. 180+ days = second source required. Applies to all 8 searches.
- **Law #139 / #147 / #148:** Inside `daily_combined` only, these credit-safe-mode laws
  supersede this law's 8-per-idea minimum with one shared 8-search sweep per day; see
  SUPERSESSION NOTE above. Outside `daily_combined`, this law governs unchanged.

---

## Applies To

- All video recommendations in any context (manual, cron, follow-up)
- Morning and evening slot show picks
- "Give me ideas" or "give me options" requests
- Any proactive suggestion about what to post
- Replacement video requests after a void or blackout
- "What should I make today" — same standard, full 8 searches

---

## Origin

User statement — June 28, 2026:
*"All my videos should be based on deep research on what's popular what's gonna get engagement views subscribers comments that needs to be a law"*

Prior incident: Agent delivered 2 replacement ideas (HxH Ch411, Mushoku Tensei S3) without running the full research stack. User caught it. Agent ran full 8 searches retroactively. Law #84 prevents this from happening again — research runs FIRST, ideas come AFTER.

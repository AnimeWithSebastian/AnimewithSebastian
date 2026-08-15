# Law #154 — Conflict-of-Interest Source Exclusion (added July 28, 2026)

**Status:** ACTIVE — HARD LAW
**Added:** July 28, 2026
**Applies to:** Every source considered for every claim in every package (daily_combined and long-form alike).

## Why this law exists

During live research passes in the July 27–28, 2026 session, sites selling engagement/views (e.g. ytviews.in) and AI content-tool vendor marketing blogs (e.g. ghostshorts.com, reelforgeai.io) were excluded from sourcing consideration on sight. This was the correct call, but it was never written down — it existed only as an in-the-moment judgment, repeatable only if the same person happened to notice the same pattern again. This law codifies that judgment as a checkable rule.

## 1. Definition

A CONFLICT-OF-INTEREST SOURCE is any source that directly profits from the claim being true — as opposed to an independent source with no commercial stake in whether the claim is accurate. A source is conflict-of-interest if it meets ANY of the following:

  (a) It sells the product or service the claim is describing or promoting.
  (b) It sells engagement, views, followers, subscribers, or similar inflatable social metrics — regardless of what specific claim it's being cited for.
  (c) It is the vendor's own marketing content (blog, landing page, press release, sponsored placement) for a tool, platform, or service that the claim is about.

This is distinct from a source simply being biased, opinionated, or enthusiastic. Independent journalism, fan commentary, and community discussion are NOT conflict-of-interest sources even when they express a strong opinion — they are excluded only if they have a direct financial stake in the specific claim being true.

## 2. The rule: exclusion, not a staleness-style backup requirement

A conflict-of-interest source may NEVER be used to support a claim — not as a sole source, and not even when paired with a second, independent source. This is not a "needs corroboration" rule like Law #78's staleness handling; pairing does not cure a conflict-of-interest source. If the only sources available for a claim are conflict-of-interest sources, the claim must be CUT or REWRITTEN to rely entirely on independent sourcing. There is no partial-credit or backup-source path that allows a conflict-of-interest source to remain in the claim_source_matrix at all, even as a secondary or supporting citation.

## 3. Example categories (for checkability, not exhaustive)

- **Engagement-selling sites:** Any site whose business is selling views, watch time, subscribers, likes, or comments (e.g. ytviews.in and similar services). Excluded even from claims about platform mechanics or algorithm behavior, since their incentive is to make the metric they sell look attainable/impactful.
- **AI/content-tool vendor marketing:** A tool or platform's own blog, landing page, or press content marketing its own product (e.g. ghostshorts.com, reelforgeai.io) cited to support a claim about that same tool's capabilities, market position, or creator outcomes. Independent reviews or journalism ABOUT the tool are not excluded — only the vendor's own promotional content about itself.
- **Self-interested corporate statements on own controversies:** A company's own press release, blog post, or statement characterizing its own controversial practice (e.g. a streaming platform's official post defending a paywall change, or a studio's statement responding to backlash over its own decision) used as the SOLE characterization of whether the practice is/was controversial or how it was received. The company's statement of its own position/facts may still be quoted AS their stated position — but it cannot stand in as the source that the practice was controversial, well-received, or justified; that requires independent reporting or audience reaction coverage.

## 4. What this does not cover

This law does not exclude a source merely for being commercial, for-profit, or affiliated with an industry (e.g. a mainstream trade outlet running ads is not conflict-of-interest). The test is a DIRECT financial stake in the specific claim being true — not general commercial existence.

## 5. Enforcement

Self-attested during STEP 4.5 (semantic QA self-audit) as part of the existing SOURCE AUTHORITY / ATTRIBUTION / CONFLICT CHECK point (STEP 4.5.7, Law #148), extended to also screen for conflict-of-interest sources per this law.

No validator blocklist exists for this law by deliberate design decision (July 28, 2026): the category (engagement-sellers, vendor marketing) is too open-ended and fast-changing for a maintained domain list to stay meaningfully current, and a stale blocklist would create false confidence worse than an honestly-labeled self-attested judgment call. This mirrors the same self-attestation-only precedent already used for `hook_first_second`, `topic_class`, and other checks the validator cannot mechanically verify (Law #147's "Validator honesty" section).

## Cross-references

- Law #78 — source date/staleness rules (a different problem: age, not conflict of interest; pairing cures staleness but never cures conflict of interest).
- Law #148 — source authority, attribution accuracy, and conflict handling (comparative source-strength ranking; this law is a binary exclusion that applies before any strength comparison).
- Law #147 — the "one dated, non-encyclopedic source" minimum sufficiency rule (also does not cure a conflict-of-interest exclusion; a conflict-of-interest source cannot serve as the "non-encyclopedic" pairing source either).

SELF-HEAL SOURCE: laws/law_154_conflict_of_interest_exclusion.md
  [Path corrected 2026-08-15 during a law audit. This read
  "/home/user/workspace/laws/law_154_conflict_of_interest_exclusion.md" — the old sandbox
  layout, which does not resolve in this repo-based checkout. Per Session Fixes
  FIX 25 the GitHub repo is the authoritative source, so the path is now
  repo-relative. The self-heal instruction itself is UNCHANGED — only the path
  was stale.]
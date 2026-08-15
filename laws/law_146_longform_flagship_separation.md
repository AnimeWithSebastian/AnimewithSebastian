# Law #146 — Long-Form Flagship Separation (added July 17, 2026)

**Status:** ACTIVE. User-approved. Codifies the 8-12 minute long-form flagship as a
**distinct product** from the 30-second Shorts. Extends (does not replace) Law #66/#136
long-form governance. Fable governance is unchanged (Law #137).

## Evidence base (both must agree)
- **Channel analytics:** **no long-form baseline exists yet** — subs are 91% from the
  Shorts feed; the returning-viewer/subscriber gap needs a long-form home.
- **Official/benchmark research:** absolute watch time matters most for long content
  (relative watch time for Shorts); chapters + keyword-first descriptions + playlist
  links drive discovery/retention; the Shorts→flagship funnel is proven by distributors
  (preview/highlight → full content).

## Evidence grade / correction
- **The 8-12 min band is a user sustainability / format choice, NOT an observed
  sweet spot.** The only "benchmark cluster at ~8-13 min" reference rests on **n=2**
  external channels and **zero** long-form data on THIS channel (no flagship has shipped
  yet). Treat 480-720s as a producible, funnel-appropriate window Sebastian can sustain,
  not as an evidence-backed optimum. **Revisit the upper bound (720s) after 4-6 flagships**
  have matured day-7 retention data; do not defend the band as data-driven until then.
- **The Shorts→flagship funnel is a mechanism hypothesis, not a channel-proven lever.**
  It works for distributors generically; it has produced 0 subscribers here so far. The
  M5 teaser cap (rule 3) keeps the test cheap until funnel evidence exists.

## Unresolved risk — algorithm mixing dilution (logged July 26, 2026)
- **Unverified but plausible, no reliable data exists to confirm or rule it out
  for this niche.** Adding a long-form flagship product to a Shorts-primary
  channel could plausibly help OR hurt how YouTube's algorithm treats the
  channel's existing Shorts performance — the effect is highly niche-dependent
  per available research, and anime commentary/entertainment content is not a
  category any located source measured directly.
- One peer-reviewed source (arXiv:2402.18208v2, Rajendran/Creusy/Garnes, April
  2024, n=250 channels) found a real, statistically significant long-form VIEW
  decline tied to Shorts adoption for large, long-form-heavy channels (mean
  −743,589 views/channel, p=0.011) — but found no significant likes/comments
  harm, and the effect size dependency on subscriber tier and content category
  means it may not transfer to a small, Shorts-heavy anime-commentary channel
  adding occasional long-form, which is the opposite profile from the study's
  "long-form-heavy" cohort where the effect concentrated.
- A secondary source (ytgrowth.io, July 2026) reports a niche-dependent mixing
  effect table showing Entertainment-category channels at scale seeing the
  worst outcome of any category (−90%) — but that source's own underlying
  "18,000-channel dataset" could not be independently traced or verified, so
  this figure is flagged as unconfirmed, not relied upon.
- No source located anywhere in this system's research addresses anime
  commentary specifically, or a channel of this size specifically. This risk
  stays open and unresolved until real on-channel data exists after flagships
  have actually shipped — it is not something either Law #66, #136, or #146
  currently accounts for, weighs, or mitigates in their existing rules.

## Rules
1. **Shorts laws do NOT apply to long-form.** The 30-second fixed edit, per-cut timings
   tiling 0→30s (Law #140), and the explicit seamless loop (Law #141) are Shorts-only.
   A flagship manifest must NOT carry Shorts-only fields (`capcut_target_sec`,
   `total_clip_time_sec`, `loop_line`, `loop_transition`, `loop_read_aloud_pass`).
2. **Distinct flagship requirements (deterministic, fail-closed —
   `validators/validate_longform_flagship.py`):**
   - `content_type` = `longform`; **two-tier length rule, replacing the single
     8-12 min band (July 26, 2026 correction) — supersedes Law #66's original
     5-8 min and Law #136's original 6-12 min "earned target" figures (both
     predate this law):**
     - **FLOOR (hard requirement, monetization-eligible at all):** must not be
       classified as a YouTube Short. Per YouTube's own current rule, a
       square/vertical video is a Short only up to 3:00; a 16:9 video is
       long-form at any length. This channel's flagships are already 16:9, so
       the floor is satisfied by format, not by hitting a specific runtime
       number. There is no separate per-video minimum duration for basic ad
       eligibility beyond this — only channel-level YPP requirements
       (subscribers/watch hours) apply.
     - **TARGET (recommended, not mandatory):** reach 8:00 (480s) — the
       confirmed, current threshold where mid-roll ads become available
       (multiple ad placements per video, not just pre/post-roll) — when the
       material genuinely supports it, per Law #136's "earned target, not a
       mandate" philosophy. This is a revenue-optimization recommendation, not
       a hard gate.
     - **NEVER pad a video to reach the 8-minute target if the material
       doesn't support that length.** A shorter video that is monetization-
       eligible (i.e., correctly classified as long-form) is better than a
       padded one that hits 8 minutes with filler — consistent with Law #149's
       "no redundant sentences" principle, applied here at the video-length
       level rather than the sentence level.
     - **No flagship has ever been produced on this channel yet** (per the
       Evidence base section above), so an unusually long first attempt
       carries more unproven production risk than a shorter one and is worth
       extra scrutiny before committing to it — not a blocked length, just a
       named consideration.
     - The old fixed 480-720s (8-12 min) band is retired as a mandatory range;
       8 minutes remains referenced only as the ad-revenue-optimization
       target above, not as a floor or a ceiling. No upper bound is
       reinstated by this correction.
   - **Face-cam is PERMITTED and recommended** (the Shorts anime-only/no-face rule does
     NOT apply). `face` may be true.
   - **≥3 chapters**, first at 0:00, strictly increasing start times.
   - **Keyword-rich first description line**: 1-2 `primary_keywords`, ≥1 present in the
     first line (feature them in the title too).
   - **`playlist_link`** and a **`pinned_next_link`** (next video / playlist) for
     follow-on retention.
   - An explicit **`comment_prompt`** question.
3. **Teaser Shorts only after a flagship URL exists — capped at ≤3/week (M5).** Plan
   **0, or 1-3** teaser Shorts for a flagship, and only once `flagship_url` is set. The
   cap was lowered from 5 to **3** because the funnel has produced **0** subscribers so
   far; do not raise it until day-7 flagship retention + teaser→flagship click evidence
   justifies expansion. Quotas never force a weak teaser (quality-over-quota, M5).
   (Shorts-side mirror: a `teaser` Short must carry a `flagship_url` — Law #145.)
4. **Model routing.** Per Law #137, **Claude Fable 5 is permitted for flagship
   scripts** (and major strategy/audits); routine daily Shorts remain Sonnet 5.0. The
   flagship validator accepts Sonnet 5.0 or Fable 5.

## Credit efficiency
- Long-form is produced on its own trigger (Law #66 long-form trigger from the weekly
  analytics cron), not by adding steps to the daily Shorts run. The daily combined
  context, single shared sweep, and cache are unchanged.

## Cross-references
- Long-form trigger/status: Law #66/#136 + `cron_analytics_runtime.txt`.
- Model routing: Law #137. Shorts loop/timing (excluded here): Law #140/#141.
- Funnel/teaser attribution: Law #145.
- Source verification: Law #58 (Pre-Send Verification). #58 is written for
  Shorts but its six claim types, consistency check, and dangling-claim rule
  apply in principle to any factual claim in a flagship VO — Law #136 Section 6
  already says as much. A flagship manifest's FACT VERIFICATION BLOCK must meet
  the same bar: no claim sourced from memory, every claim dated and cited.
- Clip verification: Law #73. #73's own header states it applies to "ALL video
  formats — Shorts and Long-Form" and its pre-send gate already names "Law #58
  (Shorts) and Law #72 (Long-Form)" — a flagship's clips[] must pass the same
  VERIFIED/FLAGGED test, not a Shorts-only reading of that law.
- VO writing craft: Law #149. #149's own scope line currently reads "Applies
  to: Every VO drafted for daily_combined Shorts packages" — it does not
  natively cover long-form. This cross-reference extends its five craft rules
  (no redundant sentences, specificity over gesture, hedge strength matching
  source confidence, promised-content delivery, read-as-speech) to flagship VO
  by analogy, the same way Law #136 already adapts Law #58 for long-form. This
  does not change Law #149's own applies-to line — that stays Shorts-scoped as
  written; a flagship package should be held to the same craft standard, not
  treated as literally governed by an unedited Shorts-only law.

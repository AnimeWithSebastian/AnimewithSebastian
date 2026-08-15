# Format research tracking — candidate FORMAT_TYPES additions

Tracks research findings on content formats that may or may not warrant addition
to FORMAT_TYPES, separate from any decision to actually add them.

## Finding 1 — 2026-07-26 anime-commentary Shorts/TikTok format research pass

Research question: what content formats/structures are genuinely popular or
high-performing specifically for anime-commentary Shorts/TikTok (not generic
Shorts advice), and does anything in current use represent a real gap in the
existing 14-token FORMAT_TYPES list (WRONG_TAKE, CHARACTER_DIVE, THE_MOMENT,
FACT_DROP, COMMENTARY, VILLAIN_DEFENSE, ORIGIN_STORY, SLEPT_ON, HIDDEN_GEM,
SEASON_RATING, SEASON_PREVIEW, MANGA_VS_ANIME, EPISODE_MOMENT, WATCH_RANK).

**Two structurally-distinct candidate formats were identified:**

1. **Versus-debate / power-scaling** — a two-sided character/entity comparison
   with a verdict (e.g. "who would win," feats-based power scaling). Structurally
   distinct from COMMENTARY (single-subject opinion/analysis) and from
   VILLAIN_DEFENSE (single-subject reframe) — the core content unit is a
   comparison between two things, not an opinion about one thing.
2. **Theory / prediction** — a creator's own forward-looking, unconfirmed claim
   about where a story is headed, supported by foreshadowing evidence.
   Structurally distinct from FACT_DROP (confirmed, dated fact) and from
   WRONG_TAKE (reacting to someone else's already-stated opinion) — a prediction
   is an unconfirmed claim originating from the creator, not a confirmed fact or
   a reaction to an existing take.

Both passed the "is this actually a new format, or just an existing token filmed
differently" scrutiny test applied to avoid repeating the
SEASON_POWER_RANKING_LIST/WATCH_RANK duplication mistake from earlier the same
night. Two other candidates considered in the same pass did NOT pass this test
and were ruled out as new formats: reaction/duet/stitch to fan or creator content
(ruled out as COMMENTARY or WRONG_TAKE with a different visual/editing
treatment) and tier-list livestreams (ruled out as a different medium — live,
long-form — not applicable to a Shorts-format token at all).

## Finding 2 — neither candidate has sufficient real engagement evidence

For both candidates, all supporting evidence for their performance specifically
in the anime-commentary Shorts/TikTok short-form context is marketing-blog
sourced only (FluxNote, FlowShorts, Packapop-style AI-content-tool SEO listicles
recommending these as video ideas). No quantified engagement data (view counts,
comment rates, like ratios, or any niche-specific benchmark) was found for either
format. Real creator examples exist for both topics, but those examples are
long-form or livestream content (e.g. power-scaling explainer videos, theory
livestream discussions), not confirmed high-performing 30-second Shorts in this
exact structure — so they do not confirm the short-form version's performance
either.

## Net effect

Two candidates are real and structurally distinct — not duplicates of existing
tokens — but neither clears the bar for addition to FORMAT_TYPES on current
evidence. The only support found is marketing-blog listicles with no quantified
data behind them, which is explicitly insufficient per the standing rule against
manufacturing a clean finding from thin evidence. No proposal to add either to
FORMAT_TYPES, the validator, or any law was made or is being made in this entry.

**Revisit conditions:**
- Better/dated/non-marketing-blog evidence surfaces for either format's real
  performance in anime-commentary Shorts specifically, or
- This channel's own real ledger data (`publication_ledger.jsonl` joined to
  YouTube Analytics) becomes substantial enough to test whether either format
  performs well in practice if a package of that type is ever actually sent —
  at which point this would be real first-party evidence, not secondhand
  marketing claims.

**Not proposed as a fix in this entry** — per standing rule, no code, validator,
or law change without explicit go-ahead and diff review. This entry is a logged
research finding only.

## Log

| Date | Candidates identified | Result |
|---|---|---|
| 2026-07-26 | Versus-debate/power-scaling, theory/prediction | Both structurally distinct (not duplicates), NEITHER added — marketing-blog-only evidence, no quantified data, insufficient to justify a FORMAT_TYPES change |

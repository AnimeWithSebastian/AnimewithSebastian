# Law #153 — External-Lens Framing Experiment (added 2026-07-27, BOUNDED EXPERIMENT)

**Status:** ACTIVE, EXPERIMENTAL. Capped at 1 package/week. Not a strategy change —
a tracked test of a pattern proven only in long-form, being tested for the first time
on this channel's actual format (Shorts).

## Evidence base
- **Super Eyepatch Wolf** (@SuperEyepatchWolf, retrieved 2026-07-27): long-form videos
  framing anime through a non-anime discipline dramatically outperform his own
  straight-recommendation videos on the same channel, same audience — Punpun analyzed
  through a depression/mental-health lens: 6.37M views; Junji Ito analyzed through a
  horror-craft lens: 5.40M views; Akira analyzed through a film-history lens: 4.60M
  views. His "Why You Should Watch [X]" recommendation-framed videos land at
  2.36M-2.64M views. Non-anime framing outperforms recommendation framing by roughly
  2.4x, controlling for channel and audience.
- **Cinema Therapy** (@CinemaTherapy): *A Silent Voice*, analyzed through clinical
  psychology (bullying/suicide themes), is the channel's #2 video of all time at
  4.31M views — outperforming *Spirited Away* (1.37M) and *The Boy and the Heron*
  (368K) despite both having far greater mainstream source-material recognition.
  Framing outperformed brand recognition.
- **Critical gap, disclosed up front:** zero verified examples of this pattern exist
  under 60 seconds anywhere in public record as of 2026-07-27. Both examples above are
  long-form. This law authorizes a Shorts-format test of a pattern proven only in
  long-form — it is not evidence the pattern transfers to a 30-60 second format.

## Rules
1. **Cap: ≤1 package/week** may set `external_lens` (a non-null value). This is a hard
   ceiling enforced by the weekly analytics cron, not a target — 0/week is a fully
   compliant outcome. This is opt-in, not quota-driven like Law #143 rule 4.
2. **`external_lens` field (per package, optional, machine field).** When set, must be
   a non-empty string naming the non-anime discipline used to frame the content (e.g.
   `"psychology"`, `"film_craft"`, `"philosophy"`, `"history"`). Free text, not a
   closed enum — the exact vocabulary of framing lenses is itself unproven for this
   channel, and forcing a premature closed list would hide real variation the weekly
   cron needs to see. Enforced well-formed (non-empty string) when present, fail-closed.
3. **Distinguishability requirement (self-attestation, M6-style).** A package setting
   `external_lens` must NOT also use a "should you watch this" / recommendation-style
   hook — the entire point of the experiment is testing the *framing*, so the hook and
   VO must actually foreground the named discipline (e.g. the hook or VO explicitly
   invokes a psychology/film-craft/philosophy concept, not just the show or "should you
   watch it"). This is not mechanically checkable content-wise; the model attests it
   honestly, same standard as `hook_first_second`/`topic_class` elsewhere in this
   system. The validator only checks the field's presence/well-formedness.
4. **Tracking.** The weekly analytics cron must report `external_lens`-tagged package
   performance separately from the rest of the portfolio, joined against real ledger
   data, starting from the first package that sets this field. No performance claim
   exists yet for Shorts specifically — this rule exists so a real, honest track record
   starts accumulating from the first real use, per `docs/EXPERIMENTS.md`.

## What this law does NOT do
- Does not require any package to use `external_lens`. Zero usage in a given week is
  fully compliant — this is a ceiling, not a floor.
- Does not authorize a long-form/flagship product using this pattern. That would
  require its own separate proposal; Law #146 already establishes zero flagships have
  ever been produced on this channel.
- Does not claim the pattern will work for Shorts. This is explicitly a test of an
  unproven translation from long-form to Shorts, per the evidence-gap disclosure above.
- Does not interact with `format_type` (Law #85). `external_lens` is orthogonal and
  additive — a package can be structurally CHARACTER_DIVE or COMMENTARY (or any other
  format_type) and separately carry an `external_lens` framing tag.

## Cross-references
- Format/structure: Law #85 (format_type is unaffected by this law).
- Topic portfolio: Law #143 (unaffected — `external_lens` usage does not count toward
  or against the timely/evergreen or recurring-series targets).
- Tracking record: `docs/EXPERIMENTS.md`.

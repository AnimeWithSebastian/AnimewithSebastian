# Law #160 — THEORY_SPECULATION (evidence-governed, conclusion-hedged theory content)

**Status:** ACTIVE — IMPLEMENTED (status corrected 2026-08-14 during a full law
audit; see Implementation status below). Design proposal 2026-08-10/11, decisions
confirmed 2026-08-11; Decision 3's mechanism corrected 2026-08-11 after a real bug
was found during user review — see Decision 3 below. 17th
controlled `format_type` token
(alongside `WORTH_WATCHING` Law #158 and `SEASON_ROUNDUP` Law #159), extending
the Law #96 rotation-expansion family. Generalizable across any anime/manga —
NOT scoped to Daemons of the Shadow Realm, which is a test case only, not the
deliverable.

## What this format is

A speculative theory about an unresolved story question (what a symbol means,
what a character's real motive is, what a foreshadowed event will turn out to
be), built from real, sourced evidence, but presented as a *theory* — an
explicit, permanent exception to how every other format's core claim behaves.

## Core structure — two-tier truth handling

1. **Evidence tier — fully governed by the existing chain, unchanged.** Every
   specific fact cited as support (a chapter detail, a character statement, a
   visual clue) must be real, fetched, and sourced exactly like any other
   format tonight — Law #73 (clip verification), Law #147/#148 (claim-source
   matrix, Tier 4 corroboration-only rule, encyclopedic-pairing rule), Law #155
   (independent verification standard). No new sourcing mechanism for this
   tier — it slots directly into `claim_source_matrix`, same as `WORTH_WATCHING`
   (Law #158) and `SEASON_ROUNDUP` (Law #159) did.
2. **Theory tier — the one deliberate exception.** The speculative conclusion
   itself is explicitly and permanently NOT claimed as settled fact. This
   needs to be as clearly stated as `SEASON_ROUNDUP`'s "does not touch Law
   #73's existing behavior elsewhere" — except here the statement runs the
   other way: this format's core theoretical claim is a **named exception**
   to the project's dominant no-hedging rule (see Design tension below), not
   an area the dominant rule never reached.

## Design tension — this format contradicts an existing rule, not just avoids it

Confirmed during design review: `hero_or_villain_master_laws_final.txt`
repeatedly states the opposite default — "total confidence, no hedging...
'maybe' and 'I think' kill the debate signal" (VO Human Voice Law guidance;
Debate-format checklist item "No hedging language (\"I think,\" \"maybe,\"
\"possibly\") in the final line"). `THEORY_SPECULATION` is the first format
to deliberately invert that default, and only for its own core theoretical
claim — every other VO line in a `THEORY_SPECULATION` package (evidence
statements, setup, non-theory context) still follows the normal no-hedging
confidence rules. This scoping is load-bearing: a future editor reading a
generic "hedging found" flag must be able to tell whether it hit the
exempted core-theory claim (fine) or leaked into ordinary VO (a real defect).
Law #149 point 3 ("hedge strength must match source confidence... if the
source itself hedges, the VO's phrasing must carry a comparable hedge") is
the real existing anchor this format's rule extends — not a new concept
invented from nothing, but a mandatory minimum hedge floor layered on top of
that existing principle, scoped specifically to the theory claim.

## Decision 1 — originality check: real research artifact, not self-attestation alone

Confirmed precedent: `hero_or_villain_master_laws_final.txt`'s documented
"Consensus Angle Disguised as a Reframe" failure (~line 2100) — a Maki Zenin
angle passed the Angle Originality Law checklist while being the exact
existing Reddit-consensus take, because "checklist language ≠ actual
originality." The fix adopted at the time was a mandatory live search
(Fandom Gap Research Law's Search 5) producing a real, checkable finding, not
a boolean. This law reapplies that same fix, scoped to theory content:

- `related_existing_theories`: a REQUIRED list (may be empty) of objects,
  each `{"theory_description": str, "source_url": str, "how_this_differs":
  str}` — documenting the actual existing-theory landscape found during
  research, not a boolean originality claim. An empty list is only valid
  paired with a genuine dedicated search attempt (see next field) — it must
  represent "searched and found nothing," never "did not search."
- `originality_search_performed`: REQUIRED object `{"query": str,
  "search_performed": true}` — at least one live search specifically
  targeting "has this exact theory been made before," mirroring Search 5's
  exact query shape (`"[Show] [character/element] theory Reddit YouTube
  [current year]"`-style), not a generic sourcing search repurposed after
  the fact.
- This is a real, checkable research artifact a human reviewer can read —
  not a trust-the-model boolean — same discipline as Law #158's
  self-attestation-plus-mechanical-backstop pattern, adapted for a field
  that cannot be mechanically verified for truth (only for presence/shape).

## Decision 2 — required minimum hedge floor + banned certainty language for the core theory claim

Mirrors `BANNED_COMPARATIVE_LANGUAGE`'s enumerated-pattern approach
(inverted): a defined list, not vibes.

- `theory_claim_line`: REQUIRED string — the exact VO sentence(s) carrying
  the core theoretical conclusion. This is the ONLY text scope the hedge
  floor and certainty ban apply to; the rest of the VO is unaffected (see
  Design tension above).
- `REQUIRED_THEORY_HEDGES`: a curated, non-exhaustive phrase list (mirrors
  `BANNED_COMPARATIVE_LANGUAGE`'s own documented limitation) — `theory_claim_line`
  must contain at least one of: "this theory suggests", "one likely
  explanation", "the evidence points to", "this may explain", "a strong
  possibility is", "this could mean", "the working theory here is", "it's
  possible that", "this points toward", "the leading theory is".
- `BANNED_THEORY_CERTAINTY_LANGUAGE`: mechanically banned from
  `theory_claim_line` (regex, `\b`-anchored, same false-positive discipline
  as Law #158's same-day regex fix): "this is what happened", "the confirmed
  answer is", "this is confirmed", "we now know", "this proves", "the fact
  is this is", "there's no doubt this is". Anchored constructions, not bare
  substrings — e.g. banning bare "confirmed" would false-positive on
  legitimate evidence-tier sourcing language describing a confirmed source
  fact, which is explicitly allowed and unaffected.
- Both checks are self-attestation (`theory_hedge_attested: true`) **and**
  mechanical, same dual-enforcement discipline as Law #158: a false
  self-attestation must not bypass the mechanical scan.

## Decision 3 — disclosure when building on an existing theory (same field, no separate data point)

Confirmed: `related_existing_theories` (Decision 1) does double duty as the
disclosure mechanism — not a second, separately-drifting field. When at
least one entry in `related_existing_theories` has a non-empty
`how_this_differs`, the package's `vo` or `pinned_comment` or
`tiktok_post_text` must surface that credit in viewer-facing language (e.g.
"a popular theory holds X — here's a detail that hasn't been connected
yet"). This is consistent with Law #148's attribution-accuracy posture and
the standing "fix the sourcing, not the claim" rule — crediting the existing
theory being extended is more honest AND better content (viewers who know
the existing theory get real added value), not merely a compliance box.

**BUG FOUND AND FIXED DURING USER REVIEW (2026-08-11):** the first drafted
mechanism checked only for the bare word "theory" anywhere in the three
viewer-facing fields. That is vacuous: `theory_claim_line` is itself part of
`vo`, and several `REQUIRED_THEORY_HEDGES` phrases already contain "theory"
("this theory suggests", "the working theory here is", "the leading theory
is") — so satisfying Decision 2's mandatory hedge floor would, as a side
effect, satisfy the bare-word Decision 3 check with zero connection to
whether an existing theory was actually credited. A package could pass
Decision 3 while never once acknowledging a prior fan theory exists — the
exact failure mode Decision 3 exists to prevent. **Corrected mechanism:** a
`CREDIT_ATTRIBUTION_PATTERN` requiring either (a) a subject+attribution-verb
construction ("fans believe", "viewers think", "theorists suggest", etc.),
or (b) a determiner+theory noun phrase ("a popular theory", "the existing
theory", "a fan theory", etc.), or (c) a theorize/theorist/theorizing form —
verified that none of the 10 `REQUIRED_THEORY_HEDGES` phrases individually
satisfy this pattern, closing off the exact mechanism that caused the bug.
Regression test `test_hedge_phrase_bare_theory_word_does_not_satisfy_credit_check`
constructs the exact bug scenario (a real, non-empty `how_this_differs`
entry, `theory_claim_line` embedded in `vo` per this law's own field
definition, no genuine attribution language) and confirms the corrected
check fails it, where the original implementation would have incorrectly
passed it.

## Decision 4 — blackout/revisit rule: same show+question blocked unless new evidence, sourced

Same self-attested `blackout_conflict`/`recent_send_conflict` pattern as
every other format (real, existing architectural limitation shared by
`WATCH_RANK`'s 14-day, `SEASON_RATING`/`WORTH_WATCHING`'s 7-day, not a new
gap). Extension specific to this format: theory content may reasonably be
revisited when genuinely new evidence emerges, unlike most formats' fixed
cooldowns. A same-show-same-question revisit requires a
`revisit_justification` object: `{"new_evidence_summary": str,
"new_evidence_source_url": str, "new_evidence_date": str}` — reusing the
same real-source-citation shape already required elsewhere (a real URL +
date), not a fresh unverified assertion. Without a `revisit_justification`
carrying a real dated source, the same show+question is blocked exactly like
any other blackout conflict.

## Where this fits (implementation status)

> **STATUS CORRECTED 2026-08-14 (full law audit).** Items 1-6 below were written as
> `NOT YET DONE` with "proposed diff below, not yet applied to any file," but every one
> of them **is in fact shipped and live** in `validators/validate_dual_package.py` and
> `validators/test_validate_dual_package.py`. Verified directly against the code:
> `"THEORY_SPECULATION"` is in `FORMAT_TYPES` (17 tokens); `REQUIRED_THEORY_HEDGES`,
> `BANNED_THEORY_CERTAINTY_LANGUAGE` and `CREDIT_ATTRIBUTION_PATTERN` are all defined
> and applied in the `fmt_raw == "THEORY_SPECULATION"` branch; the full suite passes.
> The individual `NOT YET DONE` markers below are left in place as the historical
> record of what the design pass believed at the time, per this project's standing
> no-retroactive-rewrite rule — but **they are wrong about the current state of the
> code and must not be relied on.** Item 7 (`cron_daily_runtime.txt` format-selection
> guidance) is the ONE item still genuinely outstanding: `THEORY_SPECULATION` is
> accepted by the validator but is not yet offered to the model during selection, so
> in practice the format cannot currently be chosen by a daily run.

1. NOT YET DONE — Validator: `"THEORY_SPECULATION"` added to `FORMAT_TYPES`
   (17 tokens total). Proposed diff below, not yet applied to any file.
2. NOT YET DONE — Validator: `related_existing_theories` +
   `originality_search_performed` presence/shape check (Decision 1), scoped
   to `THEORY_SPECULATION` packages only. Proposed diff below.
3. NOT YET DONE — Validator: `theory_claim_line` present +
   `theory_hedge_attested: true` self-attestation +
   `REQUIRED_THEORY_HEDGES` mechanical minimum-floor scan (>=1 required
   phrase present) + `BANNED_THEORY_CERTAINTY_LANGUAGE` mechanical scan
   (Decision 2), scoped to `THEORY_SPECULATION` packages only. Proposed diff
   below.
4. NOT YET DONE — Validator: disclosure-credit check (Decision 3) — when
   `related_existing_theories` has a non-empty `how_this_differs` entry, at
   least one of `vo`/`pinned_comment`/`tiktok_post_text` must contain
   language crediting an existing theory (a soft, presence-style check, not
   an exact-phrase match, since disclosure language is naturally variable).
   Proposed diff below.
5. NOT YET DONE — Validator: `revisit_justification` shape check (Decision
   4), applied only when a same-show-same-question conflict would otherwise
   be flagged. This mirrors the existing architectural limitation that
   `blackout_conflict`/`recent_send_conflict` are self-attested inputs, not
   independently computed by the validator — `revisit_justification`'s
   presence/shape can be checked, but whether the cited evidence is
   genuinely NEW (vs. already covered by a prior send) still relies on the
   model doing the generation checking `sent_scripts_log.json` honestly,
   same limitation as every other format's blackout rule today.
6. NOT YET DONE — Tests: proposed `TestTheorySpeculationLaw160` class below,
   mirroring `TestWorthWatchingComparativeLanguageLaw158`'s structure
   (clean-package pass, missing/false self-attestation fails closed,
   mechanical backstop catches a false self-attestation, scoping check
   confirms no leakage into other format_types, adversarial innocent-phrase
   tests, and a dedicated test proving the required-minimum-hedge floor
   catches an over-confident theory claim).
7. NOT YET DONE — `cron_daily_runtime.txt`: add `THEORY_SPECULATION` to
   format-selection guidance. Deferred until after user review/approval of
   this law text and the validator diff, per design-before-code discipline
   — same deferral pattern as Law #158 item 5 and Law #159 item 6.

**Honest scope note, matching Law #159's own disclosure pattern:** item 5's
revisit-evidence-genuinely-new check has the same real, pre-existing
architectural limitation every blackout rule on this project already has —
flagging it plainly rather than presenting it as a stronger guarantee than
it is.

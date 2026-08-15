# Law #141 — Seamless Loop: Optional, Not Required (superseded July 27, 2026)

**Status:** SUPERSEDED / RESCINDED. Originally added July 16, 2026 as "Explicit,
Mechanically-Constrained Seamless Loop," then strengthened July 21, 2026 by Law #147
into a mandatory "direct colon handoff." Both the original mandate and the colon-handoff
strengthening are rescinded as of July 27, 2026. This file is rewritten in place (not
deleted) to preserve the law-history record; see "What this law used to require" below
for the full original text of what governed packages produced between July 16 and
July 27, 2026.

## Why this changed

Two independent reasons drove the rescission:

1. **Never platform-proven.** No search of YouTube's or TikTok's official documentation
   found any confirmed statement that a seamless "loop-back" ending measurably improves
   Shorts/TikTok ranking, replay rate, or distribution. The forced-loop mandate was
   adopted on the assumption that looping helps algorithmic performance, but that
   assumption was never independently verified against either platform's own guidance.
2. **Real production cost.** The forced "intentionally incomplete colon setup" ending
   pushed VO writing into an artificial register — endings had to hedge, trail off, or
   set up a colon handoff even when the material called for a clean, direct, complete
   closing statement. This produced genuine register violations in shipped scripts:
   grammatically incomplete final sentences, closings that read as unnatural or
   gimmicky, and self-audit friction (writers forcing a colon handoff to pass the
   validator rather than because the content wanted one).

Given no confirmed platform benefit and a documented writing-quality cost, the mandate
is rescinded.

## Current requirement (July 27, 2026 forward)

- The VO **may end on any clean, complete, natural closing thought** — the same
  plain-statement register standard that governs the rest of the script (Law #149).
  No colon setup, no intentional incompleteness, no forced handoff mechanic.
- `opening_sentence` (alias `opening_line` accepted) **remains required** and must
  still equal the VO's exact first sentence. This requirement is **independent of
  looping** — it exists because the published `hook_line` must equal `opening_sentence`
  (Law #144/#145's first-second hook requirement), not because of any loop mechanic.
- A loop-style ending — where the final line happens to hand naturally into the
  opening — **is not banned**. If one arises naturally in the course of writing a good
  script, and it passes every other register/quality check (Law #149, the AI-slop
  pattern check, redundancy check, etc.), it is a perfectly acceptable ending. It is
  simply **no longer required, no longer mechanically enforced, and no longer specially
  scored** relative to any other clean ending.
- The following fields are **optional and inert**, not required, and not read or
  checked by the validator: `loop_line`, `loop_transition`, `final_to_opening`,
  `loop_read_aloud_pass`, `loop_transition_note`, and the clip-plan field
  `carries_loop_back`. They may still appear on a manifest (e.g. for continuity with
  older tooling, or if an author wants to note a naturally-arising loop for their own
  reference), but nothing enforces their presence, shape, or content. See Option B
  disposition in "Files touched" below.
- There is no longer a clip-plan requirement that any cut carry a loop-back flag, and
  no longer a mandatory "LOOP-BACK:" line in the email. The email may still show one if
  a loop-style ending happens to exist and the author wants to note it, but it is
  optional.

## Law #147 and Law #151 — correspondingly superseded/moot

- **Law #147** (credit-safe mode) is **not rescinded** — its one-pass semantic QA
  self-audit structure remains in force — but its July 21, 2026 "strengthening" of this
  law (the direct colon-handoff mechanic, the `final_to_opening_readaloud` field, and
  the `loop_colon_handoff` check key) is removed by this rescission. See Law #147's
  file for its own targeted edit reflecting this.
- **Law #151** (unfulfilled-promise loop addition, if/when it built on the colon-handoff
  mechanic) is superseded-in-place as moot by this rescission — see its own file for
  the superseded notice. Its historical text is preserved unchanged per the standing
  no-retroactive-rewrite rule; only its status line and a short addendum are updated.

## What this law used to require (July 16 – July 27, 2026, preserved for the record)

> **Status (historical):** ACTIVE. User-approved. Supersedes the weak "shared-anchor-word"
> loop acceptance in the combined daily dual-package workflow (and its expression in
> Law #139 §closer). A genuine seamless loop must now be made explicit and enforced
> mechanically — a mere keyword callback, topic echo, or a complete ending that does
> not feed into the opening is no longer accepted as a loop.
>
> **STRENGTHENED by Law #147 (credit-safe mode, July 21, 2026) — DIRECT GRAMMATICAL
> COLON HANDOFF.** The final VO sentence (`loop_line`) MUST be an intentionally
> INCOMPLETE setup that ends with a colon `":"`, and the exact `opening_sentence` MUST
> complete that setup as ONE continuous thought. This makes the loop mechanically
> checkable in addition to the model attestation: a self-contained final sentence
> ending in `.`/`!`/`?`, a final sentence identical to the opening, or a keyword
> callback are all REJECTED.
>
> **Why it changed (original rationale, now superseded by the rationale above):** The
> prior validator accepted a loop-back if the final line merely shared an anchor word
> with the opening. That let topic echoes ("silence is her whole thing") pass as
> seamless loops even though, read aloud, the video did not loop — it just ended on a
> related word. A Short only loops if the final line flows straight back into the
> first line as one continuous thought.
>
> **Requirement — per package (historical):** `opening_sentence` must equal the VO's
> exact first sentence; `loop_line` must equal the VO's exact final sentence;
> `loop_transition` must equal `loop_line + " " + opening_sentence` (or structured
> `final_to_opening`); `loop_read_aloud_pass` must be `true`; `loop_transition_note`
> must be nonempty.
>
> **Colon-handoff mechanics (historical, Law #147 strengthening):** `loop_line` had to
> end with a colon `":"`; `opening_sentence` could not itself end with a colon;
> `loop_line` and `opening_sentence` could not be identical after stripping trailing
> `: . ! ?`; the pair had to read as one continuous thought when read aloud, recorded
> as `semantic_qa.final_to_opening_readaloud`.
>
> **Requirement — clip plan (historical, ties to Law #140):** exactly one cut carried
> the loop back and had to be the final cut (`carries_loop_back: true` on the last cut,
> `false` on every other cut), with the final cut's `reason` explicitly stating it
> carries the loop back into the opening / CUT 1.
>
> **Email rendering (historical):** the email had to visibly render
> `LOOP-BACK: {final line ending in ":"} -> {opening line that completes it}` plus a
> `NOTE:` line.
>
> **Enforcement (historical):** `validators/validate_dual_package.py` failed closed on
> a wrong first/last sentence, a `loop_transition` mismatch, a missing/false
> read-aloud attestation, an empty note, zero or multiple loop-carrying cuts, a loop
> carrier that was not the final cut, a final-cut reason omitting the loop language, a
> `loop_line` not ending in a colon, an `opening_sentence` ending in a colon, or
> `loop_line`/`opening_sentence` being identical after trimming trailing punctuation.
>
> **Covered by tests (historical):** `validators/test_validate_dual_package.py` tested
> missing loop-transition display, wrong opening sentence, wrong final sentence, loop
> carrier not final, multiple carriers, final-cut reason missing loop language,
> read-aloud false, empty note, structured `final_to_opening` accepted, and the
> keyword-callback fixture (`validators/fixtures/keyword_callback_loop.json`) being
> rejected. These tests are removed as of July 27, 2026 (the retained exception:
> `opening_sentence`'s exact-first-sentence check, which survives under Law #144/#145).

## Files touched by this rescission (July 27, 2026)

- `laws/law_141_seamless_loop_mechanics.md` (this file — full rewrite in place).
- `laws/law_147_credit_safe_mode.md` (targeted edit: checks list, the
  `final_to_opening_readaloud` bullet, and the loop-strengthening paragraph).
- `hero_or_villain_master_laws_final.txt` (Law #151 entry: status line changed to
  SUPERSEDED / MOOT with an explanatory addendum; historical text otherwise preserved).
- `validators/validate_dual_package.py` — `hook_loop_claim_coverage` renamed to
  `hook_claim_coverage`; `ANCHOR_TYPES` reduced to `("hook",)`; the forced-loop
  11-check block reduced to the 2 retained `opening_sentence` checks;
  `final_to_opening_readaloud` consistency check removed; `loop_anchored` matrix
  variable removed; the `carries_loop_back` clip-plan block (3 checks) removed;
  schema/comment documentation updated to Option B (fields documented as
  optional/inert, not deleted from the schema).
- `validators/fixtures/valid_dual_package.json`,
  `validators/fixtures/valid_duration_experiment.json` — `checks` key renamed
  (`loop_colon_handoff` removed, `hook_loop_claim_coverage` → `hook_claim_coverage`);
  the (now-inert) `loop_line`/`loop_transition`/etc. fields are left in place
  unchanged (Option B — harmless either way, lowest-diff choice).
- `validators/fixtures/keyword_callback_loop.json` — DELETED (not left in place).
  Confirmed via a live validator run that once the loop-rejection rule it existed to
  exercise was removed, the fixture failed for reasons that have nothing to do with
  loops (stale `checks{}` keys, missing `anchors_claim` tagging) — a fixture that
  fails "for real" but for the wrong reason is actively misleading, not a neutral
  leftover, so it was deleted rather than left orphaned.
- `validators/test_validate_dual_package.py` — removed the forced-loop test block
  (`test_missing_loop_line`, `test_missing_loop_transition_display`,
  `test_wrong_final_sentence`, `test_loop_carrier_not_final`,
  `test_multiple_loop_carriers`, `test_final_cut_reason_missing_loop_language`,
  `test_loop_read_aloud_false`, `test_loop_transition_note_empty`,
  `test_final_to_opening_structured_accepted`,
  `test_keyword_callback_fixture_rejected`), the entire `TestColonHandoffLoop` class
  (5 tests + helper), `test_readaloud_mismatch_rejected`,
  `test_missing_loop_anchor_rejected`, `test_loop_line_non_string_fails_cleanly`, and
  `test_hook_and_loop_anchors_can_be_the_same_entry_if_it_is_both` (22 removed in
  total, verified against the real diff); renamed
  `TestHookLoopClaimCoverageAndNumericCrossCheck` to
  `TestHookClaimCoverageAndNumericCrossCheck` and its two check-flag tests
  (`test_missing_hook_loop_claim_coverage_check_flag_rejected` →
  `test_missing_hook_claim_coverage_check_flag_rejected`,
  `test_false_hook_loop_claim_coverage_check_flag_rejected` →
  `test_false_hook_claim_coverage_check_flag_rejected`) to reference
  `hook_claim_coverage` (3 renamed, not removed); retained `test_wrong_opening_sentence`
  and `test_opening_sentence_non_string_fails_cleanly` unchanged.
- `cron_daily_runtime.txt` — header/law-list, STEP 5 drafting instructions, M6
  attestation note, STEP 4.5 checklist items 1.5 and 6, the semantic_qa `checks`
  object description, and the STEP 6 validator description all updated to remove the
  forced-loop mandate and reflect the nine-key `checks` set.
- `templates/package_template.txt` — VO section no longer instructs a colon-ending
  close; the LOOP-BACK email section made explicitly optional; clip-plan section no
  longer requires a `carries_loop_back` cut; footer updated.
- `scheduler/daily_dual_package_task.txt` — STEP 5 and 5.5 instructions and the M6
  line updated to mirror `cron_daily_runtime.txt`'s changes (this file is a
  near-duplicate scheduled-task prompt body).
- `docs/MIGRATION_dual_package.md` — rescission addendum added after the historical
  July 16, 2026 Law #141 entry (entry itself preserved verbatim); a flagging note
  added to the Law #146 cross-reference (Shorts-only field rejection on flagships is
  unchanged and out of scope; only the Shorts-side optionality changed); M6 line and
  file-list entries updated.

## Rollback

Restore this file, `laws/law_147_credit_safe_mode.md`, and the Law #151 entry in
`hero_or_villain_master_laws_final.txt` to their pre-July-27-2026 versions (available
in git history at the commit immediately before this rescission), and revert the
validator/fixtures/tests/runtime/template/scheduler/migration-doc files listed above to
their prior versions. No historical send records, prior manifests, or already-shipped
packages are affected by this law either way — this rescission applies going forward
only.

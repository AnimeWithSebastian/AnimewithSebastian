# Law #159 — SEASON_ROUNDUP (multi-show "what's coming out" roundup)

**Status:** ACTIVE. User-approved 2026-08-10 (design proposal turn 840,
decisions confirmed turn "Approved" 2026-08-10). New 16th controlled
`format_type` token (alongside `WORTH_WATCHING`, Law #158), extending the
Law #96 rotation-expansion family. Formally supersedes and retires the
legacy `UPCOMING_HYPE` / `HYPE_PREVIEW` strings (see Retirement section
below).

## What this format is

Several independently-sourced premiere/season announcements in ONE video —
explicitly NOT reducible to a single show's throughline. This is the real
justification for using the existing MULTI-CLAIM EXPLAINER length band
(STEP 3.5, `cron_daily_runtime.txt`: "several independently-verified claims
that don't reduce to one throughline — e.g. a news roundup or multi-thread
update" → up to 180s). This is an exact, already-existing match, not a
stretch of that band's definition.

Distinct from `SEASON_PREVIEW` (Law #96), which is explicitly single-show
by its own text ("why you should watch or look forward to **a new anime**",
singular, one show per video). `SEASON_ROUNDUP` is the multi-show
counterpart Law #96 never covered.

## Per-show sourcing

Each show's premiere claim needs its OWN `claim_source_matrix` entry per
Laws #147/#148 — a real, distinct source per show, never one source waved
across all shows in the roundup. Law #148's Tier 4 corroboration-only rule
and encyclopedic-pairing rule apply per-show, unchanged.

## Clip sourcing — three valid paths

A `SEASON_ROUNDUP` package's bottom-half visual for each show's segment must
come from one of two verified source types (both already-legitimate content
per Law #148's Tier 1 classification, which already lists official trailers
alongside official social accounts/creator interviews):

### 1. Official trailer/PV footage — NEW verification path (`trailer_reference`)

A trailer is not "an aired episode," so Law #73's `clip_locate` (season/
episode number, AIRED/ACCURATE/CURRENTLY-AVAILABLE triad) does not apply —
forcing a trailer through that test is a category error, confirmed during
design (that triad exists specifically to check aired-footage claims, per
`cron_daily_runtime.txt` lines 385–419). Instead, each trailer-sourced clip
carries its own `trailer_reference` object, confirmed exact shape:

```json
"trailer_reference": {
  "trailer_title_or_id": "<the specific named trailer, e.g. 'Kagurabachi Season 2 PV 2'>",
  "claimed_beat": "<the specific moment/shot/line claimed from this trailer>",
  "source_content_confirmed": "<what was actually checked -- the trailer fetched directly, or credible Tier 1-2 coverage per Law #148 describing its content -- and what it showed>",
  "match": true
}
```

`match` must be `true` for the clip to be used. No `clip_locate` object is
attached to a trailer-sourced clip — its absence is correct, not a gap.

**Clip-source label line:** trailer-sourced clips render a new label line in
the clip plan, parallel to the existing manga "CHAPTER 126" convention:
`TRAILER: [trailer_title_or_id]` (e.g. `TRAILER: Kagurabachi Season 2 PV 2`).
This lets Sebastian see at a glance which of the three source types (aired
anime / manga / trailer) backs each cut.

**Known failure mode (real precedent, not hypothetical):** Law #73 UPDATE 7
documents a real, live-published incident (Gachiakuta, Aug 6 2026) where a
package claimed "First Footage Breakdown" of unaired Season 2 PV content,
but every actually-cited clip was Season 1 footage — no real Season 2 PV
existed to cite at the time. Each clip's own narrow claim was independently
true, but the video-level claim was false, and it had to be corrected live
on YouTube after publication. `trailer_reference`'s `claimed_beat` +
`source_content_confirmed` fields exist specifically to catch this failure
mode: if the specific claimed beat cannot be confirmed to actually appear in
the specific named trailer, `match` must be `false` and the clip cannot be
used as a trailer-sourced clip for this format. Law #144.1 point 9.7's
zero-verified-clips title/hook gate extends to this case: if a claimed
trailer beat can't be verified, the fallback is NOT silently dropping to
manga (manga cannot show a trailer's specific framing or announcement) — it
is either finding a real Tier 1–2 source that confirms the specific claimed
beat, or reframing the hook/title away from "footage" language entirely,
exactly as the real Gachiakuta correction did.

### 2. Manga panels — EXISTING path, no new work

Uses the already-built `manga_reference` (chapter/page citation) and
`clip_plan_needs_manga_source` fields unchanged. Confirmed during design:
nothing in their existing definition restricts them to any particular
format_type — they apply cleanly here with zero schema changes.

### 3. Aired anime footage — EXISTING path, no new work

Standard `scene_verified` + `clip_locate` path (Law #73), unchanged, for any
segment referencing already-aired footage (e.g. a returning show's new
season announcement alongside a recap beat).

## Split screen — REQUIRED, no exception

Face-cam split screen (Creator TOP / anime footage BOTTOM, Law #134 Stage 2)
is required for every video under this format — confirmed decision, no
face-only exception. Every package needs real bottom-half visual content
from one of the three sources above for every show segment.

## Multi-show structure

Several independently-sourced premiere announcements per video. Length maps
to the MULTI-CLAIM EXPLAINER band (up to 180s, STEP 3.5) — this is the
correct band because the content genuinely does not reduce to one
throughline, not because the format wants to run long.

## Retirement of UPCOMING_HYPE / HYPE_PREVIEW

**Confirmed decision: formal retirement, no intent folded forward.**
`UPCOMING_HYPE` (6 real sends) and `HYPE_PREVIEW` (2 real sends) are legacy,
pre-`FORMAT_TYPES`-enum strings that predate Law #96's controlled-vocabulary
lock-in. They are not in the current 14-token (soon 16-token) validator
enum and are already rejected fail-closed by today's validator. At least
one send used an explicitly invalid compound label,
`"SEASON_PREVIEW / UPCOMING_HYPE"` — compound/free-text labels are banned
under the current controlled-vocabulary rule.

Effective on this law's approval:

- `UPCOMING_HYPE` and `HYPE_PREVIEW` are dead tokens. No new package may use
  either string as `format_type`, now or in the future.
- Their historical sends remain in `sent_scripts_log.json` exactly as-is —
  this is real historical record, not something to rewrite or purge.
- `SEASON_ROUNDUP` is their properly-built successor for genuinely
  multi-show premiere/hype content, with real per-show sourcing and real
  trailer verification — not an ad-hoc format that predates the sourcing
  discipline this project now requires.

## Where this fits (implementation status)

1. DONE — Validator: `"SEASON_ROUNDUP"` added to `FORMAT_TYPES` (16 tokens
   total, alongside `WORTH_WATCHING`).
2. DONE — Validator: third valid clip-sourcing path check added via the new
   `_validate_season_roundup_clip_sourcing()` function — a clip is valid if
   `scene_verified: true` AND a well-formed `clip_locate` (anime) OR
   `manga_reference` present (manga, existing) OR `trailer_reference.match:
   true` (trailer, NEW). Exactly one of the three must apply per clip; a clip
   carrying both `clip_locate` and `trailer_reference` fails closed (mutual
   exclusivity). Branched at the call site so Law #73's existing behavior for
   all other 15 format_types is provably unchanged (dedicated regression test
   confirms this).
   REAL GAP CLOSED 2026-08-10 (same-day review, before first commit): the
   initial draft counted `scene_verified: true` alone as a valid anime source
   with NO `clip_locate` enforcement at all — unlike every other format_type's
   anime path, which has required a well-formed `clip_locate` object since Law
   #73 UPDATE 5. A SEASON_ROUNDUP anime-sourced clip could have shipped with a
   missing or malformed `clip_locate` and still passed. Fixed by extracting
   the existing shape-check logic (previously a closure private to
   `_validate_clip_verification`) to a shared module-level
   `_clip_locate_shape_ok()` function, now called from BOTH the original Law
   #73 path and this SEASON_ROUNDUP path, with a dedicated named check
   (`clip_locate present and well-formed wherever scene_verified is true (Law
   #73 UPDATE 5, applied to Law #159 anime path)`) so a missing/malformed
   `clip_locate` fails closed exactly as it does everywhere else in the
   system. Manga- and trailer-sourced clips are unaffected — they correctly
   have no `clip_locate` requirement of their own, confirmed by a dedicated
   regression test.
3. **DONE — built 2026-08-14.** [Status corrected 2026-08-14; the original
   NOT-YET-DONE text is preserved verbatim below, per this project's standing
   no-retroactive-rewrite rule.] Implemented as
   `_validate_season_roundup_sourcing()` in `validators/validate_dual_package.py`,
   called for every package immediately after `_validate_semantic_qa`.
   **Schema additions:** `roundup_shows` (array, REQUIRED and fail-closed when
   `format_type == "SEASON_ROUNDUP"`, MUST be absent otherwise; >=2 distinct
   non-empty names) supplies the authoritative denominator, and core
   `claim_source_matrix` entries carry a `show` tag naming one of them.
   **Clip count is deliberately NOT used to infer the show count** — nothing
   enforces 1 clip == 1 show (the >=4-clip floor was removed as arbitrary, F22
   2026-07-28), so inferring from clips would fail OPEN exactly when a show is
   under-covered. **Five fail-closed checks:** roundup_shows well-formed; every
   core claim tagged with a declared show; COVERAGE (every show has >=1 core
   claim); PER-SHOW SOURCING (each show cites >=1 source that is both listed in
   `sources` — hence dated — and non-encyclopedic); and DISTINCTNESS (no source
   URL reused across two shows), which is the check that actually implements
   "a real, distinct source per show, never one source waved across all shows."
   Coverage alone cannot express that: five core claims about one show would
   satisfy a bare count while covering nothing.
   **Scoping:** on all 16 other `format_type` values the function requires
   `roundup_shows` to be absent and reports nothing else, so neither the field
   nor these checks leak.
   **Tests/fixture:** `TestSeasonRoundupPerShowSourcingLaw159` (17 tests, incl. a
   scoping test asserting zero leakage across all 16 other tokens) plus the new
   `validators/fixtures/valid_season_roundup.json` — a realistic 3-show roundup,
   the first fixture this format has ever had. Suites: validators 365, tools 115.
   Like every other Law #73/#147/#159 field check this is presence/shape/domain
   only — it cannot verify a source actually supports its claim, which remains a
   drafting-pass attestation subject to the weekly human spot-check (Law #147 M6).

   > NOT YET DONE — Validator: per-show `claim_source_matrix` entry count
   > check for `SEASON_ROUNDUP` packages (one real source per show claimed,
   > not one source covering multiple shows) was NOT implemented this pass.
   > Today's `_validate_semantic_qa` only checks that `claim_source_matrix` has
   > >=1 core claim overall — it does not yet cross-check entry count against
   > number of shows in a `SEASON_ROUNDUP` roundup. Flagging honestly rather
   > than marking this done: this must be built before `SEASON_ROUNDUP` is
   > used in production, or a roundup could ship with one source waved across
   > several shows undetected.
4. **DONE — 2026-08-15, but the item's own premise was WRONG and is corrected
   below. Original text preserved verbatim at the end of this item.**

   **What was wrong:** this item says the `TRAILER:` label should be built
   "parallel to the existing `CHAPTER N` manga rendering." **There is no
   existing `CHAPTER N` rendering.** Verified 2026-08-15: zero `CHAPTER`
   matches across `tools/`, `validators/`, `templates/` and `scheduler/`;
   `tools/render_clip_descriptions.py` handles neither manga nor trailer, and
   its `ensure_clip_locations()` only appends season/episode tokens for
   `scene_verified=true` clips. `CHAPTER 126` is a **hand-authored prose
   convention**, specified in `cron_daily_runtime.txt`'s CLIP SOURCE LABELED
   LINE block (Law #73, manga-panel addition, 2026-08-03) and written by the
   drafting model — not emitted by code.

   **The real gap** was therefore not "trailer rendering was skipped while
   manga rendering exists." It was that Law #73's label spec defines three
   cases — `SEASON x EPISODE y` (anime), `CHAPTER n` (manga), `UNVERIFIED
   [footage_status]` (neither) — and **Law #159 added `trailer_reference` as a
   fourth clip source without extending that spec**, leaving trailer-sourced
   clips as the only source type with no defined label line.

   **What was done:** the trailer case was added to that spec in
   `cron_daily_runtime.txt`, completing the four-way rule. Prose only, additive,
   **no code change** — deliberately, because building code-side rendering for
   trailers while manga and unverified remain hand-authored would have created
   an inconsistency rather than removed one. The item's underlying observation
   (no `TRAILER:` string exists in the validator) was accurate; only its
   attributed cause was not.

   > NOT YET DONE — Validator: the `TRAILER: [name]` clip-source label line
   > rendering (parallel to the existing `CHAPTER N` manga rendering) was NOT
   > implemented this pass. Grepped `validate_dual_package.py` and confirmed
   > no `TRAILER:` string exists anywhere in the file. The underlying data
   > (`trailer_reference.trailer_title_or_id`) is validated and available, but
   > nothing renders the label line yet.
5. DONE — Tests: `TestSeasonRoundupClipSourcingLaw159` (14 tests: the
   original 10 plus 4 added 2026-08-10) covers (a) valid trailer_reference
   with match=true passes, (b) match=false fails closed, (c) missing all
   three source types on a clip fails closed, (d) a clip with both
   clip_locate AND trailer_reference fails closed (mutual exclusivity), (e)
   malformed trailer_reference (missing claimed_beat) fails closed, (f) empty
   clips list fails closed without crashing, (g) a non-SEASON_ROUNDUP package
   with a bare trailer_reference-only clip still fails under the ORIGINAL Law
   #73 path, proving no leakage into other format types, and NEW (h) an
   anime-sourced clip with `scene_verified: true` and NO `clip_locate` at all
   fails cleanly naming the clip_locate check, (i) the same with a malformed
   `clip_locate` (bare URL in `locate_confirmed_via`), (j) a missing
   `clip_locate` also fails the exactly-one-valid-source check (not silently
   counted as valid), (k) manga- and trailer-sourced clips are confirmed
   unaffected by the new requirement. `UPCOMING_HYPE`/`HYPE_PREVIEW` rejection
   is covered by `TestFormatTypeEnumLaw158Law159` (6 tests) instead, as a
   FORMAT_TYPES enum check rather than inside this class. A new dedicated
   class, `TestClipLocateShapeOkSharedHelperLaw159` (8 tests), confirms the
   module-level extraction of `_clip_locate_shape_ok()` preserved the exact
   original Law #73 UPDATE 5 semantics (well-formed passes; missing, non-dict,
   bare-URL, missing-episode, boolean-episode, and blank-timestamp all fail;
   `approx_timestamp: null` is explicitly allowed). Full suite (296 tests
   total) passes with zero failures.
6. **STATUS CORRECTED 2026-08-14** — this item read "NOT YET DONE," which was
   inaccurate: `cron_daily_runtime.txt` **did** address `SEASON_ROUNDUP`, just not
   in the form this item anticipated. Rather than being absent from the runtime, the
   token was covered by an explicit, named **withholding note** (the SEASON_ROUNDUP
   callout at the end of the format list, plus a pointer to it in the token-count
   note) stating the format `IS NOT YET SELECTABLE FROM THIS STEP` and citing item 3
   above as the precise blocker. That is the opposite of missing guidance — it is a
   deliberate, documented exclusion, and it is what kept the unbuilt item 3 from
   becoming a live production gap. The runtime itself drew the distinction, noting
   `THEORY_SPECULATION`'s absence was "not a deliberate withholding like
   SEASON_ROUNDUP's — it is an outstanding porting gap." Original text preserved:

   > NOT YET DONE — `cron_daily_runtime.txt`: add `SEASON_ROUNDUP` to
   > format-selection guidance with the MULTI-CLAIM EXPLAINER length-band
   > mapping and the three-source-type sourcing rule above. Deferred until
   > after user review/approval, per design-before-code discipline.

   With item 3 now built (2026-08-14), the blocker that withholding note existed to
   enforce is resolved, and the runtime is updated in the same change to make the
   token selectable — see the `cron_daily_runtime.txt` diff accompanying this edit.

**Honest scope note:** items 3 and 4 above are real gaps in this pass, not
oversights being hidden. The clip-sourcing mechanism (item 2) is the load-
bearing mechanical safeguard against the known Gachiakuta-style failure mode
and is fully built and tested; the per-show source-count check and the
label-line rendering are lower-risk polish/completeness items that can be a
follow-up change once this core mechanism is reviewed and approved.

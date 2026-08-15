# Law #158 — WORTH_WATCHING (single-show persuasion, no ranking)

**Status:** ACTIVE. User-approved 2026-08-10 (design proposal turn 840, decisions
confirmed turn "Approved" 2026-08-10). New 15th controlled `format_type` token,
extending the Law #85 monetization hierarchy / Law #96 rotation-expansion family.

## What this format is

A persuasive case for ONE show, on its own merits — mainstream, popular,
top-of-season, or niche. There is no constraint on how well-known the show
already is. This is the explicit differentiator from `HIDDEN_GEM`/`SLEPT_ON`
(Law #85), which are scoped specifically to underrated/overlooked/deep-cut
shows — `WORTH_WATCHING` carries no such restriction and may be used for a
show regardless of its existing popularity.

It is also explicitly distinct from `WATCH_RANK` (Law #98): `WATCH_RANK`
argues a comparative placement among several shows. `WORTH_WATCHING` argues
for exactly one show, in isolation, with zero cross-show positioning.

## Hard rule: no comparative or ranking language

This is a rule of the format's own definition — not merely the absence of a
rank field. A `WORTH_WATCHING` package MUST NOT use comparative or ranking
language anywhere in `vo`, `hook_line`, `hook_onscreen_text`, `youtube_title`,
`tiktok_title`, or `tiktok_post_text`. Banned constructions (non-exhaustive
examples, mechanically enforced — see `BANNED_COMPARATIVE_LANGUAGE` in
`validators/validate_dual_package.py`):

- "better than", "worse than", "beats", "loses to", "over [other show]"
- "#1", "top pick", "number one"
- any explicit or implied placement/ranking mechanic
- any named cross-show comparison of any kind

Enforcement is **both** self-attestation and a mechanical banned-phrase list
(per the confirmed decision — Law #149 point 9's enumerated-pattern approach
is the model, not a vibe-based judgment call):

1. Self-attestation: the manifest must set `no_comparative_language: true`,
   the same self-attestation shape as `hook_first_second` / `loop_read_aloud_pass`
   (Laws #144/#147). This is honest, model-set, and spot-checked weekly by a
   human editor, same discipline as the other self-attestation fields.
2. Mechanical backstop: the validator independently scans the same text
   fields against `BANNED_COMPARATIVE_LANGUAGE` and fails closed if any match
   is found — regardless of what `no_comparative_language` claims. A false
   self-attestation does not bypass the mechanical check.

## Sourcing

Real, source-verified specific reasons — plot/character/craft beats, not
vague praise ("it's really good"). No new sourcing mechanism: this slots
directly into the existing `claim_source_matrix` machinery (Laws #147/#148)
already required for every core claim on every format_type. Law #148's
Tier 4 corroboration-only rule and the encyclopedic-pairing rule both apply
unchanged.

## Length

Maps directly onto the existing variable-length bands (STEP 3.5,
`cron_daily_runtime.txt`) — no new length logic:

- 1 verified reason → SINGLE-FACT/QUICK-TAKE band (20–30s)
- 2–3 connected reasons → MULTI-BEAT ARGUMENT band (45–75s)

## Blackout

**7 days per show** (confirmed decision), matching `SEASON_RATING`'s blackout
— the closest structural sibling (single-show, single-verdict content). A
show that received a `WORTH_WATCHING` package cannot receive a second one
until 7 days have passed. Enforced the same way every other format's
blackout is enforced today: the manifest sets `blackout_conflict: false` and
`recent_send_conflict: false` as a self-attested input (per the real,
existing pattern at `validate_dual_package.py` lines 1018–1022), checked
against `sent_scripts_log.json` by the model doing the generation, not
computed independently by the validator itself. This is a real, existing
architectural limitation shared by every current format's blackout rule
(WATCH_RANK's 14-day, SEASON_RATING's 7-day, EPISODE_MOMENT's 7-day airing
window) — not a new gap introduced by this law.

## Video style / production

No change to Law #134 Stage 2: face-cam split screen (Creator TOP / anime
footage BOTTOM) required, same as every other Shorts format_type. No
anime-only exception for this format either.

## Where this fits (implementation status)

1. DONE — Validator: `"WORTH_WATCHING"` added to `FORMAT_TYPES` (now 16
   tokens total, alongside Law #159's `SEASON_ROUNDUP`).
2. DONE — Validator: `BANNED_COMPARATIVE_LANGUAGE` is a REGEX tuple (not bare
   substrings), scoped to `format_type == "WORTH_WATCHING"` packages only —
   other formats are unaffected. Checked against `vo`, `hook_line`,
   `hook_onscreen_text`, `youtube_title`, `tiktok_title`, `tiktok_post_text`
   via `re.search(pattern, field_norm, re.IGNORECASE)`.
   REAL FIX 2026-08-10 (same-day review, before first commit): the initial
   draft used bare substrings for "over " and "beats", which fire on ordinary
   non-comparative VO language ("changes over time", "hands it over", "the
   hero beats the villain in the final chapter"). Adversarial testing during
   review confirmed the false-positive risk, so the pattern list was rewritten
   as anchored regexes requiring the actual comparative construction, e.g.
   `\bbeats (every|all|the other|other|any other)\b` and `\bover (anything
   else|everything else|the rest|the competition|every other|any other|that
   other|those other)\b`, instead of bare `"beats"` / `"over "` substrings.
   This was NOT shipped and then documented as a known risk — the false
   positives were caught and the pattern was fixed before any commit.
3. DONE — Validator: presence/boolean check for `no_comparative_language` on
   `WORTH_WATCHING` packages only added (mirrors `hook_first_second` presence
   check) — must be explicitly `true`, not merely present.
4. DONE — Tests: `TestWorthWatchingComparativeLanguageLaw158` (25 tests: the
   original 8 plus 17 added 2026-08-10) covers (a) banned phrase correctly
   fails a WORTH_WATCHING package even with a (falsely) true self-attestation,
   (b) clean WORTH_WATCHING package passes, (c) the same banned phrase does
   NOT fail a non-WORTH_WATCHING package (scoping check), (d) missing/false
   `no_comparative_language` field fails closed, (e) the "over " trailing-space
   construction is caught, (f) 9 ADVERSARIAL tests proving realistic innocent
   phrases ("changes over time", "all over again", "hands it over", "the hero
   beats the villain in the final chapter", "it's all over now", "picks up over
   the summer", "climbs over the wall", "watched it over the weekend", "thinks
   it over carefully") do NOT trigger a failure, and (g) 8 tests confirming the
   regex still correctly fires on real comparative/ranking language ("better
   than", "beats every other show", "number one", "loses to", "outranks",
   "top pick", and two "over <object>" comparison constructions). Full suite
   (296 tests total) passes with zero failures.
5. NOT YET DONE — `cron_daily_runtime.txt`: add `WORTH_WATCHING` to the
   format-selection guidance alongside the other 15 tokens, with the
   length-band mapping above. Deferred until after user review/approval of
   this law text and the validator diff, per design-before-code discipline.

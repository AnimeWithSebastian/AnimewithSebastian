# Tracking Doc — Love Unseen Correction Resent in Full-Script Format

**Date:** 2026-08-10 (batch post_date 2026-08-11)
**Batch ID:** 79531612-04d5-4caa-94da-d05490ff994d
**Package ID:** 6b7ad021-c808-4f52-80c7-a6b697182fba (evening — Love Unseen Beneath the Clear Night Sky)
**Type:** Correction resend — format only (content and sourcing unchanged from the prior correction)

## What changed

The earlier same-night correction for this package ("CORRECTION | EVENING | Love Unseen Starts With a White Cane | August 11, 2026 | Verification Note Was Wrong, Real Footage Located") explained the fix in prose only. Per the new standing rule (permanent, effective 2026-08-10 forward), every correction email must be presented in the full standalone script format. This resend replaces that prose-only email with the complete script structure (CORRECTION NOTE, SHOW/ANGLE/FORMAT/STYLE/TOPIC/SERIES/FUNNEL, HOOK, VO, PERFORMANCE SCRIPT, CLIP PLAN, CAPTIONS, TITLES, POST TEXT, PINNED COMMENT, POST TIME, SOURCES, VALIDATOR CONFIRMATION).

Underlying content/sourcing is unchanged: the package's original `verification_note` was factually wrong (claimed no clip-level source could be confirmed), when in fact the official Ani-One India Episode 6 upload (licensed via Medialink Entertainment, uploaded 2026-08-10) was live and findable at send time. All three clips are `scene_verified: true` with real `verification_source_url`, `claim_vs_source_check`, and `clip_locate` fields — this was already correctly built into the manifest; only the stale `verification_note` language needed correcting.

## Mechanism note (important, disclosed in the email itself)

This package's clips are `scene_verified: true`, so Law #73 UPDATE 8's `footage_status` / `footage_search_performed` / `location_pointer` fields (used in tonight's Re:ZERO correction, which has `scene_verified: false` clips) do **not** apply here. UPDATE 8 is scoped by design to `scene_verified=false` clips only. The validator's five UPDATE-8 checks report `[PASS]` for this package, but only vacuously (empty `scene_verified=false` set) — they do not validate anything about this package's real footage verification. The real, applicable, already-enforced checks for this package are the `scene_verified=true` chain (Law #73 / UPDATE 4 / UPDATE 5 / UPDATE 6): `verification_source_url`, `claim_vs_source_check`, `clip_locate`, and clip_descriptions surfacing season/episode — all of which genuinely pass. `footage_status`/`location_pointer` were deliberately NOT added to this package's clips, since doing so would be mechanically inert (unread by the validator on verified clips) and could misrepresent what was actually checked.

## Validator run (real output)

```
python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json
RESULT: PASS — 178 [PASS], 0 [FAIL], exit code 0.
```

Meaningful checks for this package (scene_verified=true chain, all genuinely exercised):
- `[PASS] [evening] each clip has scene_verified (bool) set (Law #73)`
- `[PASS] [evening] verification_source_url present wherever scene_verified is true (Law #73)`
- `[PASS] [evening] claim_vs_source_check present and well-formed wherever scene_verified is true (Law #73 UPDATE 4)`
- `[PASS] [evening] no clip is scene_verified=true with claim_vs_source_check.match=false (Law #73 UPDATE 4)`
- `[PASS] [evening] clip_locate present and well-formed wherever scene_verified is true (Law #73 UPDATE 5)`
- `[PASS] [evening] clip_locate episode number does not contradict claim_vs_source_check when both state one (Law #73 UPDATE 5)`
- `[PASS] [evening] clip_descriptions surfaces clip_locate season/episode for every verified clip (Law #73 UPDATE 6)`

Vacuously-passing checks (disclosed, not claimed as meaningful for this package):
- `[PASS] [evening] footage_status present and a valid enum value wherever scene_verified is false (Law #73 UPDATE 8)` — vacuous, zero scene_verified=false clips
- `[PASS] [evening] no clip has footage_status=aired_not_located (Law #73 UPDATE 8, hard block)` — vacuous
- `[PASS] [evening] footage_search_performed present and names a recognizable video platform wherever scene_verified is false (Law #73 UPDATE 8)` — vacuous
- `[PASS] [evening] location_pointer well-formed (url + description) when present (Law #73 UPDATE 8)` — vacuous
- `[PASS] [evening] location_pointer.url also appears in the package's sources list when present (Law #73 UPDATE 8)` — vacuous

## VO word count

Declared `vo_word_count`: 155. Independently confirmed against the validator's real `_words()` tokenizer: **155** (matches). Naive `.split()` also gives 154/155-adjacent counts depending on punctuation handling; not used as the source of truth.

## Send confirmation (real, mailbox-verified)

- **Sent to:** hero_or_villain@outlook.com (only)
- **Subject:** `CORRECTION | EVENING | Love Unseen Starts With a White Cane | August 11, 2026 | Full-Script Format (Verification Note Was Wrong, Real Footage Located)`
- **Send tool result:** `status: SENT`
- **Mailbox verification (search_email, real query):** 2 email objects found matching this exact subject —
  - `2026-08-11T01:36:57+00:00`, email_id suffix `...ck4AAABC7jDzAAAA`
  - `2026-08-11T01:36:53+00:00`, email_id suffix `...ck4AAABC7i0GAAAA`
  - Same thread_id (`AQQkADAwATM0MDAAMi1h...`)
- **Known issue:** this is the F21 Outlook connector duplicate-dispatch defect (documented in `docs/KNOWN_ISSUES.md`), now observed on every send tonight including this one. Non-blocking, logged per standing practice — not treated as a new bug.

## Logging note

This package_id (`6b7ad021-c808-4f52-80c7-a6b697182fba`) already has a real `sent` row from the earlier correction in `state.json` / `sent_scripts_log.json`. Per instruction, this resend is logged via this tracking doc only — `tools/append_send_batch.py` was NOT run again for this package, to avoid a duplicate log entry for the same package_id.

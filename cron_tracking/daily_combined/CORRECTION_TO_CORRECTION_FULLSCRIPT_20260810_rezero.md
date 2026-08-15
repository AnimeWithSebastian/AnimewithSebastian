# Tracking Doc — Re:ZERO Correction-to-Correction (Full-Script Format Resend)

## Context

This is a **format resend** of the correction-to-correction that was already sent
and logged earlier tonight in `CORRECTION_TO_CORRECTION_20260810_rezero_trailer_source.md`.
The content/sourcing decision (verified official PV replacing two failed sources)
was already correct and already logged. This send exists only to satisfy the new
standing rule (established this segment, permanent): every correction email —
including corrections, correction-to-corrections, and resends — must always be
sent in the full standalone script format (SHOW/ANGLE/FORMAT/STYLE through
SOURCES), never a prose-only explanation of the delta.

**No new `sent_scripts_log.json` / `append_send_batch.py` row is created for this
send.** Per user instruction, this package_id (`d08b72b8-d1ca-4e73-9f63-8c68e36a1df2`,
Re:ZERO / morning) already has a real sent row from the earlier correction. This
is logged via this tracking doc only, following the established pattern used for
the first correction-to-correction.

## Batch / Package Identifiers

- batch_id: `79531612-04d5-4caa-94da-d05490ff994d`
- package_id: `d08b72b8-d1ca-4e73-9f63-8c68e36a1df2` (Re:ZERO, morning slot)
- post_date: August 11, 2026

## Word Count Verification (user-requested, this send)

User independently counted 161 words in the VO and asked which count is correct
against the validator's actual tokenizer.

- Validator tokenizer: `_words()` in `validators/validate_dual_package.py`,
  regex `r"[\w']+"` applied via `re.findall`.
- Ran this exact function against the real VO text pulled live from
  `cron_tracking/daily_combined/run_manifest.json` (not a retyped copy).
- Result: **162** — matches the manifest's declared `vo_word_count` field exactly.
- For reference, a naive `.split()` count on the same text returns 159 (neither
  161 nor 162), confirming the discrepancy was a manual-count variance, not a
  validator or manifest error.
- Both 161 and 162 fall inside the approved 148-162 word band regardless — this
  was a confirmation check only, not a blocker.

## Validator Confirmation (re-run immediately before this send)

```
python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json
```

Result: **178 [PASS], 0 [FAIL], exit code 0.** All four Law #73 UPDATE 8 checks
pass for the Re:ZERO (morning) package:

- [PASS] footage_status present and a valid enum value wherever scene_verified is false
- [PASS] no clip has footage_status=aired_not_located (hard block)
- [PASS] location_pointer well-formed (url + description) when present
- [PASS] location_pointer.url also appears in the package's sources list when present

Raw output saved to `/home/user/workspace/validator_final_before_c2c_send.txt`.

## Send Confirmation

| Field | Value |
|---|---|
| To | hero_or_villain@outlook.com (only) |
| Subject | CORRECTION TO CORRECTION \| Re:ZERO Trailer Source Was Wrong \| August 11, 2026 \| Replaced With Verified Official PV |
| Format | Full standalone script (SHOW/ANGLE/FORMAT/STYLE/TOPIC/SERIES/FUNNEL header through SOURCES + VALIDATOR CONFIRMATION), per the new standing rule |
| Sent | Yes — confirmed via `send_email`, status `SENT` |
| Send timestamp (tool-reported) | 2026-08-11T01:23:00Z |

## Mailbox Verification (real `search_email`, post-send)

Queried `subject:"CORRECTION TO CORRECTION"` and a time-bounded query
(`after:2026-08-11T01:20:00-04:00`). **2 email objects found**, same subject,
same thread_id (`AQQkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoAEAAtq1NzWsd-TYD8Oa7UGIEg`):

| # | email_id (suffix) | Timestamp (UTC) |
|---|---|---|
| 1 | `...AAABC7jDyAAAA` | 2026-08-11T01:23:54Z |
| 2 | `...AAABC7i0FAAAA` | 2026-08-11T01:23:50Z |

This is the same **known F21 duplicate-dispatch issue** documented in
`docs/KNOWN_ISSUES.md` (each Outlook connector send producing 2 email objects
in mailbox search). This is the fourth confirmed instance tonight (Re:ZERO
footage correction, Love Unseen footage correction, Re:ZERO
correction-to-correction #1, and this correction-to-correction resend).
Logged as a known, non-blocking recurrence — not a new bug, not investigated
further per standing guidance.

## Logging Decision Rationale

Per explicit user instruction for this send: do NOT run
`tools/append_send_batch.py` for this resend, because package_id
`d08b72b8-d1ca-4e73-9f63-8c68e36a1df2` already has a real, valid sent row
logged from the earlier correction-to-correction send tonight. Re-running the
append-batch logger here would create a duplicate/conflicting log entry for a
package_id that has already been correctly recorded. This tracking doc is the
complete record of this specific resend (format-only, no content change).

## Sources (unchanged from the sent email)

1. Radio Times — Part 2 begins August 12, eight remaining episodes, follows the
   Loss Arc, confirmed for Crunchyroll —
   https://www.radiotimes.com/tv/fantasy/anime/rezero-starting-life-in-another-world-season-4-part-2-release-schedule/
   (Jul 2026)
2. Collider — return heads to the Pleiades Watchtower through the Auguria
   Dunes, Shaula connected to the search for answers after Priestella —
   https://collider.com/best-anime-series-coming-netflix-crunchyroll-august-2026/
   (Jul 2026)
3. Official Re:ZERO Season 4 Part 2 "Recapture Arc" PV, verified via the
   uploading channel's own 【公式】 branding, not title text —
   https://www.youtube.com/watch?v=2RqqQuy7pgo (Aug 2026)

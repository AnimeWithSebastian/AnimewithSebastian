# Archived — 2 Original Run #9 Packages Replaced for Unverifiable Content (2026-08-02)

## Status: ARCHIVED, NOT DELETED, NOT RESENT, NOT FURTHER REVISED

The following 2 packages were sent as production emails to
hero_or_villain@outlook.com on 2026-08-01T23:45:09 UTC (batch
`c8401ef5-1d1e-48ce-a3f4-39443498caea`), then resent the next day with VO
craft/sourcing corrections under a `CORRECTED SCRIPT |` subject prefix
(see `CORRECTED_SCRIPT_SEND_20260802_run9_onepiece_mha.md`; that resend
was intentionally NOT re-logged in `sent_scripts_events.jsonl` because it
reused the same package_ids and would have violated the dedup rule --
only one logged send event exists for this batch). Both were then found on
independent re-review to rest on content that could not be verified as
actually aired. Both are archived and replaced by two brand-new packages
(new `package_id` values, same `batch_id`, same slots) rather than
corrected in place, because the defect is a premise-level sourcing gap,
not a wording fix.

| Show | package_id | Slot | batch_id | Title at time of archiving |
|---|---|---|---|---|
| One Piece | 4af7ca6d-1545-4eae-8252-dc459afc39f6 | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | "One Piece Just Titled an Episode 'Fear'" |
| My Hero Academia | 8f3552ac-bca7-4a1e-a6ed-8eb4afaa2756 | evening | c8401ef5-1d1e-48ce-a3f4-39443498caea | "My Hero Academia Isn't Actually Over" |

## Why these are archived (root cause, not a wording defect)

**One Piece ("Just Titled an Episode 'Fear'")**: the angle depended on
episode 1172's content (airing 2026-08-02, the same day this package was
originally sent) matching a "nightmares given monstrous form" / "children
as hostages" mechanic. Independent verification this round found only
trailer and manga-chapter-adjacent coverage for that content — no real,
watched, post-air review of episode 1172 existed at any point this
package was live, because the episode had not aired yet when the claims
were written. This is the exact category of gap Law #73 / Law #58 Type F
exists to catch (anime-vs-manga boundary, claim sourced from unaired
content).

**My Hero Academia ("Isn't Actually Over")**: separately flagged and
already corrected once for a sourcing conflict (the "adapts the final
material Horikoshi wrote" superlative, contradicted by ComicBook.com's own
page — see `docs/KNOWN_ISSUES.md` F27). On top of that correction, the
angle itself ("Isn't Actually Over") was replaced this round with a
cleaner, more directly-verifiable angle centered on Eri's Quirk contrast,
since a full angle rebuild was already underway for the paired One Piece
package and the same real-source-only standard was applied to both per
explicit instruction.

## What replaces them

Two new packages, same batch_id `c8401ef5-1d1e-48ce-a3f4-39443498caea`,
same slots, **new package_id values**:

| Show | New package_id | Slot | New angle |
|---|---|---|---|
| One Piece | b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f | morning | "Every single character with a stake in Elbaf begged Luffy not to free Loki -- he did it anyway," grounded entirely in aired episode 1171 (2026-07-26). |
| My Hero Academia | d7c2a4b1-9e8f-4a3c-b1d2-3e4f5a6b7c8d | evening | Eri's Quirk (Rewind) could erase people from existence; the new special gives her a guitar and a concert instead, grounded in the real Anime Expo premiere review. |

Because these are new `package_id` values (not a reuse of the archived
ones), `tools/append_send_batch.py`'s `(batch_id, package_id)` dedup key
treats them as new rows -- the normal logging flow applies (see the
tracking doc for this round for confirmation this ran cleanly, not a
skipped no-op).

## Correction history for the archived (pre-replacement) packages

- Original send (only logged event for this batch): `sent_scripts_log.json` /
  `cron_tracking/sent_scripts_events.jsonl` entries under batch_id
  `c8401ef5-1d1e-48ce-a3f4-39443498caea`, `date_sent`
  2026-08-01T23:45:09.257213+00:00 (both packages share this timestamp).
- VO craft/sourcing correction round: `CORRECTED_SCRIPT_SEND_20260802_run9_onepiece_mha.md`
  (closer rewrites for both packages, MHA sourcing-conflict disclosure).
- Self-audit reliability findings from the same review pass: `docs/KNOWN_ISSUES.md`
  F27 (semantic_qa self-attestation failure) and F28 (captions field
  regression).
- This archival + full replacement: this file, plus the send/logging
  tracking doc for 2026-08-02's replacement round.

## What this file does NOT do

- Does not delete, modify, or resend either archived package or its
  original/corrected emails.
- Does not change `sent_scripts_log.json`, `sent_scripts_events.jsonl`, or
  any prior tracking doc for the archived package_ids.
- Does not mark the archived package_ids as available for reuse, further
  correction, or re-dispatch. Any future action on
  `4af7ca6d-1545-4eae-8252-dc459afc39f6` or
  `8f3552ac-bca7-4a1e-a6ed-8eb4afaa2756` specifically requires a new,
  explicit decision at that time.
- Does not assert either archived package's video was or was not posted
  to YouTube/TikTok -- that is tracked separately in
  `cron_tracking/publication_ledger.jsonl` and is out of scope for this
  file.

Filed: 2026-08-02

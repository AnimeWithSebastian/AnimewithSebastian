# VO structural correction record — One Piece morning (comma-splice + redundancy fix) — 2026-08-02

## Status

This is the tracking record for the "VO STRUCTURAL CORRECTION" send of the One
Piece morning package only (`batch_id c8401ef5-1d1e-48ce-a3f4-39443498caea`,
`package_id b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`). This is the **third**
correction round for this package_id:

1. **First (clip plan):** CLIP PLAN CORRECTION (season/episode location data,
   sent 2026-08-02T14:25:47Z-14:25:49Z), see
   `CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md`.
2. **Second (fragment stacking):** VO CRAFT CORRECTION (merged sequential
   physical-action fragments per new Law #149 point 6, sent
   2026-08-02T23:18:13Z-23:18:17Z), see
   `VO_CRAFT_CORRECTION_20260802_run9_onepiece_fragment_fix.md`. This round's
   fix turned out to be defective — see below.
3. **Third (this record):** a genuine side-by-side comparison against a real,
   well-received script (Berserk_171) found that the second round's "merge"
   was a comma splice, not an actual compound sentence, and separately
   surfaced a redundant sentence pair violating Law #149 point 1. Both are
   fixed together in this round.

The My Hero Academia evening package in the same batch was NOT touched this
round, or any prior round.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f | VO rewritten (Option D of the drafts considered tonight) to (a) replace the second round's comma-spliced action sequence with a genuine causal compound sentence using "because" to connect cause and effect, and (b) remove a redundant restatement of the "everyone warned him" claim, spending the freed word budget on a new, previously-absent detail (the crew's frozen reaction) instead of repeating the warning claim a second time. Word count changed from 108 to 107 (within the 100-108 band). Hook and question line updated for consistency ("them" -> "Luffy", forward-looking question phrasing kept). Clip plan, season/episode location data, titles, captions, TikTok text, pinned comment, sources, and post times all unchanged from the prior correction rounds. |

## Comparison findings that triggered this round

A genuine sentence-by-sentence comparison was run against a real, well-received
script (Berserk_171, full text in `berserk_email_draft.txt`,
`package_id f2b8d9e3-5a4c-4b0f-9d2e-6f7a8b9c0d1e`), checking rhythm,
redundancy, and whether merged clauses actually connect logically — not just
fragment count. Two problems were confirmed real:

1. **Comma splice, not a genuine merge.** The second round's "fixed" sentence
   ("he just stands up, chains gone, weapon in hand, and there's no music yet,
   just silence while everyone realizes what they did") reduced the fragment
   count to zero by replacing periods with commas, but the clauses still had
   no causal or logical connector between them — read aloud, it kept the same
   choppy cadence as the original fragments. It satisfied a naive
   fragment-count check without satisfying the actual intent of Law #149
   point 6. Berserk_171's real compound sentence ("He cannot lead armies or
   live free like he once did, because his own throne is what cages him.")
   uses one causal "because" to genuinely connect two ideas — that connector
   was the missing piece in the second round's draft.
2. **Redundant sentence (Law #149 point 1).** "Every person around Loki told
   them not to do this" (opening) and "Every person in that room warned Luffy
   this was a mistake" (later in the same VO) were the same claim restated in
   different words — a direct violation of point 1's "no redundant sentences"
   rule, a separate defect from the point-6 fragment issue already addressed
   in round two.

## New law text added this round: Law #149 point 6 clarification

Two clarifying paragraphs were added to `hero_or_villain_master_laws_final.txt`,
inserted after the existing ACCEPT EXAMPLE paragraph and before the "END Law
#149" footer (original line ~15462). This is a clarification of the existing
point 6 text added in the prior round, not a new numbered point:

- **"A LOW FRAGMENT COUNT IS NOT THE SAME AS A GENUINE MERGE"** — states that a
  real compound sentence requires an actual causal or logical connector
  (because, so, yet, while, but); replacing periods with commas between the
  same fragments does not satisfy the point even at zero/one fragment count,
  because the result is a comma splice.
- **"INTERNAL ILLUSTRATION"** — uses tonight's own two-draft history on this
  same package_id as the worked example: draft 1 (periods, the existing
  REJECT EXAMPLE) -> draft 2 (comma-spliced, sent and later found
  non-compliant, quoted exactly) -> draft 3 (genuine causal merge via
  "because," quoted exactly) — states only draft 3 satisfies the point, and
  draft 2 is recorded as the new cautionary case for future self-audits to
  check against.

Diff shown to and approved by the user before staging (Option D locked in,
per explicit instruction to add this clarification and use tonight's own
two-draft history as the internal illustration).

## Mid-process catch: unsourced detail caught and corrected before sending

An earlier internal draft of the round-three VO used the phrasing "the entire
crew just goes silent instead of drawing steel" — this was an **unsourced
claim**, implying a near-fight or drawn weapons that no cited source actually
supports. This was self-caught (not user-flagged) before it was written to any
file, surfaced via a clarifying question, and corrected to a phrasing directly
grounded in the same FandomWire review already cited in this package's `clips`
array: "every character just freezes while the music slowly builds instead,"
verbatim-grounded in "Every character freezes as Loki stands, the music
gradually builds, and the atmosphere instantly changes from hopeful to
unsettling" ([FandomWire](https://fandomwire.com/one-piece-episode-1171-review/)).
**This unsourced phrase never appeared in any sent email or committed file** —
it is disclosed here only as a caught-before-ship issue, consistent with this
session's transparency pattern for self-caught defects.

## Why fresh research/verification was not needed for the retained facts

No new factual claims were introduced beyond the already-cited FandomWire
detail used to replace the unsourced phrase above. All other facts in the VO
(Hajrudin's objection, Sanji and Zoro's reactions, Luffy freeing Loki, the
freeze/silence after) remain sourced to the same four URLs already cited in
the prior two correction rounds and unchanged here. No new sources were
fetched for the retained facts.

## Honest validator-limitation note

Ran `python3 validators/validate_dual_package.py` against the corrected
manifest (`run_manifest_20260802_v2_replacement.json`): all 156 existing
mechanical checks PASS for both packages (word count, CTA adjacency, hook/
opening_sentence consistency, clip timing tiling, sourcing, Law #73 clip
verification, `law_149_redundancy_check` attestation). The validator has **no
mechanical check for genuine causal-connector merging versus comma splicing,
or for redundant-sentence detection** — both remain self-audited only. This
correction round is itself direct evidence that self-audit-only checks can
pass a defective draft: the immediately prior "fix" (round two) attested
compliance with Law #149 point 6 while still being a comma splice, and passed
the validator anyway, because the validator only checks presence/schema for
this attestation, not the actual prose quality. This limitation is noted
here plainly rather than glossed over, consistent with the standing rule
never to mark a check true merely to pass validation.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in both prior rounds (see
`CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md` and
`VO_CRAFT_CORRECTION_20260802_run9_onepiece_fragment_fix.md`):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only.
`b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f` already carries a `"status": "sent"`
row in `sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`,
logged at the original 2026-08-02T14:10:54Z send time. Re-running the logger
against this same `(batch_id, package_id)` pair would be a silent no-op
(`events_appended: 0`) and would not reflect this correction. Per the same
established pattern, `sent_scripts_log.json` and `sent_scripts_events.jsonl`
are left untouched — this markdown file, plus the sent email itself, is the
record instead.

## Send and mailbox verification

Email sent to `hero_or_villain@outlook.com` only, subject `VO STRUCTURAL
CORRECTION | One Piece | fixes comma-splice + redundant sentence per Law
#149 point 6 clarification`. Verified via direct `search_email` full-string
`email_id` comparison immediately after sending.

| Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|
| VO STRUCTURAL CORRECTION \| One Piece \| fixes comma-splice + redundant sentence per Law #149 point 6 clarification | 2026-08-02T23:33:12Z, 2026-08-02T23:33:15Z | 2 (genuine duplicate) |

**One Piece (morning): 2 real mailbox copies — genuine F21 duplicate-dispatch
recurrence.** Two distinct full `email_id`s confirmed via direct string
comparison (`...AAA_U3DpAAAA` at 23:33:12Z and `...AAA_U3TUAAAA` at
23:33:15Z), same `thread_id`, ~3 seconds apart. Only one `send_email` tool
call was made for this package (confirmed via this turn's tool-call history).

This occurrence is consistent with F21's established finding that this is a
connector/transport-side defect, not an agent-side double-send. It has been
appended to the F21 history table in `docs/KNOWN_ISSUES.md`, along with an
updated sample-size tally (19 -> 20 real send events, 8 -> 9 confirmed
genuine duplicates).

**No emails were sent to any address other than `hero_or_villain@outlook.com`.**
The prior 2026-08-02T23:18:13Z-23:18:17Z VO-craft-correction copies (still
carrying the comma-splice/redundancy defects fixed in this round) were NOT
re-triggered or removed — they remain present as the honest historical record
of that correction round, per explicit standing user instruction not to touch
existing send records. The My Hero Academia evening package and its mailbox
copies were not touched this round.

## Filed

Date: 2026-08-02T23:33:15Z (UTC) — set to the latest of the confirmed send
timestamps above.

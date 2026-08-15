# Archived — Draw This, Then Die! (Morning, 2026-08-08) Held for Law #148 Single-Source Risk

## Status: ARCHIVED, NOT DELETED, NOT SENT, NOT FURTHER REVISED

This package was drafted during the 2026-08-07 daily_combined manual
review session (targeting 2026-08-08 output) as the morning half of a
dual package alongside Black Torch (evening). It was **never emailed** —
confirmed directly against `sent_scripts_log.json`, which contains 0
entries for this `package_id` (190 total entries, unchanged before and
after this decision). Sebastian held it on 2026-08-08 rather than
approving it for send.

| Show | package_id | Slot | batch_id | Title at time of archiving |
|---|---|---|---|---|
| Draw This, Then Die! | 87f7b103-c9bf-4818-91fc-90fbc37150f0 | morning | cb10a88e-da1d-4238-94a8-9258eb49b16e | "This Show Did Something Most Anime Are Too Scared To Try" |

## Why this is archived (root cause, not a wording defect)

During a 3-item verification review, a Law #148 (Source Authority,
Attribution Accuracy, and Conflict Handling) audit found that 2 of the
morning package's 4 clips — the entire "Sensei's flashback" half of the
30-second edit (clips 1–2, 15 of 30 seconds) — relied on a single Tier 4
source (one Reddit r/anime episode 6 discussion thread) for their core
claimed beats, with no qualifying Tier 1–3 source found after a genuine
search:

- **Clip 1** ("flashback opens — her career still going, before the
  turn"): checked the Anime News Network episode 6 review directly —
  it confirms a Teshima flashback occurs and discusses her
  characterization, but never confirms this specific "before the turn"
  opening framing as its own beat.
- **Clip 2** ("tears, manga cancelled, phone thrown into the ocean"):
  checked the same ANN review directly — it does not mention
  cancellation, crying, or a phone in the ocean anywhere. No second
  source located for this specific detail.

Per Law #148's Tier 4 rule ("NEVER sufficient alone to support a factual
claim — must be paired with a Tier 1-3 source"), both clips were
downgraded from `scene_verified: true` to `scene_verified: false` with a
disclosed `verification_note`, rather than shipped on single-source
attestation. (Clips 3–4, the "girls' first sale" and "Loup Garou" half,
DID have real Tier 2 corroboration found — Anime News Network's episode
6 review and casting announcement — and remained verified; only the
flashback half is at issue.)

Sebastian's explicit decision on 2026-08-08: hold the package entirely
rather than send it with a disclosed single-source risk on its core VO
claim, since a fresh candidate is available for the next real morning
slot instead. This is a premise/evidence-level gap, not a wording fix —
consistent with the "Quality Over Quota" principle (M5) already in the
production runtime: never publish a weak package to hit a quota.

## Validator status at time of holding

The manifest still passed the deterministic validator (exit code 0,
~140/140 checks) after the Law #148 fix, because the F20 fallback
(`scene_verified: false` + `verification_note`) is an explicitly
supported honest state, not a validator failure. The hold decision was
made on evidentiary grounds above and beyond what the mechanical
validator checks — the validator passing is not in tension with holding
this package; it confirms the *mechanical* laws (word count, timing,
CTA, etc.) were fine, while the *sourcing* judgment call to hold was
made independently on Law #148 grounds.

## What this file does NOT do

- Does not delete, modify, or resend this package or generate any email
  for it. No email for this package_id has ever been sent.
- Does not change `sent_scripts_log.json`, `sent_scripts_events.jsonl`,
  `blackout_state.json`, or `publication_ledger.jsonl` — this package
  never reached any of those logs and this archival does not add it to
  them either.
- Does not mark this package_id or the show "Draw This, Then Die!" as
  blocked from future coverage. A future package_id for this show is a
  new, independent decision at that time, subject to the same
  cooldown/blackout rules as any other candidate (this one never
  occupied a blackout/cooldown slot since it was never sent).
- Does not affect or gate tomorrow's daily_combined cron run, which
  will independently research and select a fresh morning candidate for
  the real next slot using the full standard process (Law #148 tier
  compliance, Isolation Test, Law #149 point 8 closer check, etc.) —
  not a same-session rush replacement tonight.
- Does not archive or affect the evening (Black Torch) package, which
  is fully verified and proceeds to send independently tonight.

## Related known-issues entry

See `docs/KNOWN_ISSUES.md` F34 for the process-level writeup of the
Tier 4 single-source finding that led to this hold decision.

Filed: 2026-08-08

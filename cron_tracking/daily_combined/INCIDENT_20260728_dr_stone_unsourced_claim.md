# Incident — Unsourced fan-reaction claim shipped in sent VO — Dr. Stone: Science Future, EVENING slot, post_date 2026-07-28

## Status: SHIPPED. Email already sent. NOT corrected retroactively per standing rule
against rewriting historical records (this is a new incident record about the send,
not a retroactive edit to the send itself).

## What happened

The EVENING package for post_date 2026-07-28 (batch_id
794d00b8-96b5-44d5-b310-f70dff48245f, package_id
711db69c-6ef7-4546-9744-9725e1171793, show: Dr. Stone: Science Future) contains this
line in the sent VO, and in `sent_scripts_log.json`:

> "Fans are split. Some call it shonen's best payoff. Others say it erases everything
> earned."

**This is an unsourced popularity/reaction claim stated as settled fact.** No
attribution, no linked source, no specific commenter, post, review, or platform is
cited anywhere in the package for either side of this claimed split. The manifest and
`sources` field for this package were not found to contain any citation supporting a
real, observed fan reaction to this specific finale beat at time of send.

This falls under the standing rule "Never invent facts, dates, quotations, popularity,
or trends" — a claim about what "fans" are saying, in aggregate, with a specific
two-sided breakdown, is a popularity/trend claim and requires real sourcing the same
way any other factual claim in a VO does. None was present.

## Why it wasn't caught before send

Same class of gap as the Gachiakuta terminology incident
(`INCIDENT_20260727_gachiakuta_terminology.md`): a claim was drafted and approved
without independently verifying that a real, citable source existed for it at the
specific level of detail claimed (a two-sided fan split, not just general reception).
Unlike the Gachiakuta case, there is no single misread source to point to here — this
appears to be an assumed/generic "fans are always split on X" framing inserted without
any sourcing step being attempted for this specific claim at all, rather than a source
being misread. That is a distinct and, in one sense, more basic failure than the
Gachiakuta case: no source was cited or checked, not a wrong source cited and trusted.

## Disposition

- Historical record NOT rewritten: the sent email, `sent_scripts_log.json`, and
  `run_manifest.json` for this batch stand as actually sent, per standing rule against
  retroactively rewriting historical records except for genuine self-referential
  errors in the record-keeping itself (this is a content error in the shipped script,
  not an error in how the send was logged).
- This incident file is the disclosure of that content error, filed the same way
  `INCIDENT_20260727_gachiakuta_terminology.md` disclosed the Gachiakuta terminology
  error — as a permanent, undeleted record.
- No corrective action (correction video, pinned comment edit, etc.) has been taken
  yet. That is a decision for Sebastian, not something to self-authorize.

## Filed

Date: 2026-07-26 (discovered during a fresh close-read scan of today's sent VOs,
requested separately from and in addition to the STEP 4.5 construction-tic review;
applies to the already-sent 2026-07-26 evening batch, post_date 2026-07-28)

## Correction sent (2026-07-27T01:51:27+00:00)

A rewritten version of this package's VO/captions/tiktok_post_text/pinned_comment was
drafted to replace the unsourced "Fans are split" claim with a sourced two-sided
claim: Reddit critical threads
(https://www.reddit.com/r/DrStone/comments/1ugsc0v/i_am_disappointed_with_the_ending_did_you_think/,
Jun 29, 2026; https://www.reddit.com/r/DrStone/comments/1ug48e6/am_i_the_only_one_disappointed_by_the_finale_of/,
Jun 27, 2026) on one side, and FandomWire
(https://fandomwire.com/dr-stone-science-future-ending-explained/, Jun 25, 2026) and
ComicBook.com (https://comicbook.com/anime/list/top-3-anime-of-spring-2026-ranked-by-their-finales/,
Jun 29, 2026) on the other. The rewritten manifest re-passed
`validators/validate_dual_package.py` (exit 0) and the full `validators/` test suite
(198 tests, OK) before send.

The corrected version was emailed to hero_or_villain@outlook.com at
2026-07-27T01:51:27+00:00 UTC (subject: "REWRITTEN SCRIPT | EVENING | Dr. Stone:
Science Future | originally sent 2026-07-26 | Dr Stone's Finale Has Zero Fights In
It"). Mailbox verification via search_email originally reported **2 copies landed** at
2026-07-27T01:51:27+00:00 and 2026-07-27T01:51:24+00:00, attributed to a known Outlook
connector duplicate-send behavior observed on every send that night (all 4 rewritten
packages sent as part of the same batch were originally reported landing as exactly 2
identical copies each) — **this count was overstated.** A direct `search_email` check
during round 2 (2026-07-27 ~22:00 ET, see `REWRITE_SEND_20260727_batch_v2.md`) found
only 1 real copy of this email, not 2. Corrected here rather than in the original
paragraph above, per the standing rule against rewriting historical records. This was
not a new or Dr-Stone-specific issue — the same overstatement applied to all 4
packages in that night's batch.

**No new row was appended to `sent_scripts_log.json` or
`cron_tracking/sent_scripts_events.jsonl` for this correction.** The rewrite manifest
reused the same `batch_id` (794d00b8-96b5-44d5-b310-f70dff48245f) and `package_id`
(711db69c-6ef7-4546-9744-9725e1171793) as the original 2026-07-26 send, and
`tools/append_send_batch.py` dedupes strictly on `(batch_id, package_id)` with no
support for a distinct "rewritten" event type or an annotation field on an existing
row — the code was checked directly (`_event_row()` hardcodes `"event": "sent"`,
and `_existing_keys_jsonl()` ignores the `event` field when building its dedup set),
so appending a second row under those same IDs would either be silently skipped
(no-op) or would double-count the day's quota / poison future dedup, depending on how
it was attempted. Neither outcome is desirable, and no code change was authorized
tonight. This paragraph is that record instead. Adding a proper `--event-type` /
note-field capability to `append_send_batch.py` so corrections like this one can be
logged as a distinct, non-quota-counted event is a backlog item, same treatment as
F15/F16/F17.

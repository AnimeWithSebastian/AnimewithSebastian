# daily_combined — post_date 2026-07-28 (morning, Slime S4) — CONFIRMED duplicate email dispatch

## Status: INCIDENT RECORD (not a live blocker) — workaround already applied correctly, batch completed successfully. Filed per standing rule: "when something doesn't work... it gets rewritten, not just logged" — this is the log entry; the underlying connector defect itself is not owned/fixable from this repo (see "What is NOT being done here" below).

## What happened

During the interactive send of the Slime S4 morning package (batch_id
`794d00b8-96b5-44d5-b310-f70dff48245f`, package_id
`a6cd0642-5205-4e4a-a66e-5dd58bd14b44`, subject "TOMORROW | MORNING | That Time
I Got Reincarnated as a Slime Season 4 | 2026-07-28 | Slime S4: Rimuru vs
Granbell, Same Goal"), a single confirmed `send_email` call to the Outlook
connector (`source_id: outlook`) resulted in **two distinct emails** landing
in the hero_or_villain@outlook.com mailbox, both with identical subject and
body:

- `email_id` ending `...ck4AAAA1_Oz4AAAA`, timestamp `2026-07-26T22:30:11Z`
- `email_id` ending `...ck4AAAA1_TsSAAAA`, timestamp `2026-07-26T22:30:08Z`

Only one `send_email` call was made (confirmed via this session's own tool
call history — no retry, no second confirm, no duplicate-send classifier
trip). This is a genuine one-call-becomes-two-sends connector-side defect,
not an agent-side double-send.

## This is the SAME root cause already diagnosed and filed tonight, not a new investigation

Earlier in this same session, an internal diagnostic was filed for this
identical failure mode. No new pattern was found here — this incident is
the second live occurrence of the already-understood defect:

- Same connector (`outlook`), same tool (`send_email`), same shape: exactly
  one agent-side call, two mailbox-side sends, both identical in
  content/timestamp-adjacent.
- A fresh reconnect/re-auth of the Outlook connector between the first
  occurrence and this one did **not** change the behavior — this incident
  reproduced the identical failure signature on a freshly-authenticated
  connection, which rules out stale-session/stale-token as the cause.
- No code in this repository sends email twice. `tools/append_send_batch.py`
  and the daily_combined workflow only ever construct and dispatch one
  `send_email` call per package, exactly as designed. The defect is
  upstream, inside the Outlook connector/pipe itself, outside this repo's
  control surface.

## How it was actually handled (workaround, applied correctly)

1. Both copies were found via `search_email` against the Outlook connector —
   confirmed identical subject/body, two distinct `email_id`s.
2. Per explicit instruction, the duplicate copy was deleted manually by the
   user directly in their own Outlook client — the Outlook connector
   exposes no delete/archive tool (`search_email`, `draft_email`,
   `send_email`, `search_calendar`, `update_calendar` only), so this could
   not be automated from this session.
3. A re-verification `search_email` call immediately after the manual
   deletion still showed both copies present. The user confirmed this is
   mailbox/search-index lag on Outlook's side, not a failed deletion, and
   explicitly instructed to proceed regardless of the stale index read.
4. The **only thing that actually matters for correctness** — the
   `append_send_batch.py` logger and its downstream logs
   (`sent_scripts_log.json`, `cron_tracking/sent_scripts_events.jsonl`,
   `cron_tracking/publication_ledger.jsonl`) — logs the package exactly
   **once** per package_id, regardless of how many times the underlying
   email transport happened to fire. This was confirmed for tonight's batch:
   `sent_scripts_log.json` gained exactly one new entry for package_id
   `a6cd0642-5205-4e4a-a66e-5dd58bd14b44` (165 total entries confirmed after
   this run; the exact pre-run count was not independently re-checked in
   this session and is not asserted here), and the idempotent re-run of the
   logger (`--emails-sent
   --git-pushed`, state-refresh only) confirmed `skipped 1 already-present;
   legacy_added=0` — the log itself is immune to the mailbox-side duplicate
   by construction, since it keys on package_id/batch_id rather than on
   however many transport-level sends occurred.
5. No second package was affected, no wrong recipient, no wrong content —
   both copies were byte-identical in subject and body, sent to
   hero_or_villain@outlook.com only (never to any other address).

## What is NOT being done here

- Not attempting to patch or work around the connector's send behavior from
  this repo — the defect is in the Outlook connector integration itself
  (outside `SEBLABHRIS/AnimeWithSebastian`'s codebase), and this repo has no
  send-path code to change.
- Not treating this as a new/unknown incident requiring fresh investigation
  — the diagnosis (single call, connector-side double-dispatch, unaffected
  by reconnect, reads-as-lag on re-verification) was already reached and
  filed as an internal diagnostic earlier tonight; this document is the
  incident log entry for the second live occurrence, per the standing rule
  that a recurring failure gets written down rather than silently
  re-handled each time.
- Not deleting anything from a production log to "clean up" the duplicate —
  the duplicate lives in the mailbox (Outlook UI), not in any file this
  repo tracks, so no production log required (or received) any deletion.

## Current state

- Batch `794d00b8-96b5-44d5-b310-f70dff48245f` / package
  `a6cd0642-5205-4e4a-a66e-5dd58bd14b44`: fully sent (mailbox, duplicate
  copy handled per above), fully logged (exactly 1 event, not 2), fully
  committed and pushed to `origin/main` (commits `82aa80b`, `360c240`).
- No open action item from this incident beyond this record. If the
  underlying Outlook connector defect recurs on a future send, this
  document is the reference for "same known issue, same handling" rather
  than a fresh investigation each time.

## Sources / evidence referenced

- This session's own `call_external_tool` / `search_email` outputs
  (workspace-local tool call history for this conversation — not a public
  URL; referenced here as the factual basis for the email_id timestamps and
  counts above, per this session's own confirmed tool outputs).
- `sent_scripts_log.json` (repo root) — entry count before/after this
  batch's logger run, confirmed via this session's own `wc`/`python3 -c`
  checks.
- `cron_tracking/daily_combined/state.json` — reflects `status: "success"`,
  `emails_sent: true`, `log_appended: true`, `git_pushed: true` for this
  batch as of commit `360c240`.

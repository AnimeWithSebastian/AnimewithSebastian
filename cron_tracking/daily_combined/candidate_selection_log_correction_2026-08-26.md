# Correction note — batch 9a7d935f floor-format entries (2026-08-26)

## Status

This is a correction/companion record, not a log mutation. The 5
`candidate_scored` entries it corrects remain **unedited and undeleted** in
`cron_tracking/daily_combined/candidate_selection_log.jsonl`, per the
append-only design of that log and per explicit instruction from Sebastian
(2026-08-26): "Do NOT edit or delete the 5 candidate_scored entries already
appended... that log is append-only by design specifically to prevent this
kind of after-the-fact cleanup, even when the entries were generated under a
mistaken premise. Preserve them exactly as written."

The log's own schema (`tools/candidate_selection_log.py`,
`EVENT_TYPES = ("candidate_scored",)`) does not support a dedicated
correction event type — `build_event()` fail-closed rejects any
`event_type` outside that tuple. Rather than modify the shared validator
module's schema mid-run, this correction lives as a standalone companion
file, per Sebastian's explicit fallback allowance for that case.

## The 5 entries this note corrects

All 5 are real `candidate_scored` events, `batch_id =
9a7d935f-95e6-40ac-8dfc-a6dd1d9a3eb7`, `post_date = 2026-08-26`, appended to
`candidate_selection_log.jsonl` during this run, one each for:
`THEORY_SPECULATION`, `SEASON_ROUNDUP`, `WORTH_WATCHING`, `WATCH_RANK`,
`SEASON_RATING` — all `outcome: "rejected"`, all
`format_eligibility_result: "ineligible"`.

## The premise error

While drafting this batch, the agent believed all 5 minimum-frequency-floor
formats had **never been logged** (`days_since_last_considered = None` for
all 5), which would have made `must_force_consider = true` for all 5 under
the 21-day floor window (`FLOOR_WINDOW_DAYS`). Acting on that belief, the
agent evaluated Hunter x Hunter Ch. 418 and Kagurabachi Ch. 129 against all
5 floor formats and logged 5 real rejection events reflecting that
evaluation.

## The real facts

That premise was **false**. A prior batch, `af6c90bf-b832-474c-ad67-
782f56038368` (post_date `2026-08-23`, committed
`15f25fd4156bb0fe6ac2e8a8886951d3d6bc65a3`), had **already logged genuine
`candidate_scored` events for all 5 of the same floor formats** — verified
directly by reading the raw entries in
`cron_tracking/daily_combined/candidate_selection_log.jsonl`:

```
af6c90bf  2026-08-23  THEORY_SPECULATION  outcome=rejected
af6c90bf  2026-08-23  SEASON_ROUNDUP      outcome=rejected
af6c90bf  2026-08-23  WORTH_WATCHING      outcome=rejected
af6c90bf  2026-08-23  WATCH_RANK          outcome=rejected
af6c90bf  2026-08-23  SEASON_RATING       outcome=rejected
```

`post_date 2026-08-23` to `post_date 2026-08-26` is a real gap of **3
days** — well inside the 21-day `FLOOR_WINDOW_DAYS` window. The correct
values for today's batch, going into this run (i.e. `exclude_batch_id =
9a7d935f...` so the check reflects state before this run's own writes),
were:

| Format | days_since_last_considered | must_force_consider |
|---|---|---|
| THEORY_SPECULATION | 3 | false |
| SEASON_ROUNDUP | 3 | false |
| WORTH_WATCHING | 3 | false |
| WATCH_RANK | 3 | false |
| SEASON_RATING | 3 | false |

None of the 5 formats were actually overdue. The floor mechanism should not
have forced consideration of any of them tonight.

## How this reader should treat the 5 entries

The 5 `candidate_scored` entries for `batch_id 9a7d935f...` /
`post_date 2026-08-26` **are real** — they reflect a genuine evaluation of
today's actual candidates (Hunter x Hunter Ch. 418, Kagurabachi Ch. 129)
against each floor format's eligibility rules, and their `rejected` /
`ineligible` outcomes are honestly reasoned. But they were **not
floor-mandated** — they exist because of this premise error, not because
the minimum-frequency floor genuinely required evaluating these 5 formats
tonight.

**A future reader analyzing format-consideration frequency should NOT
treat these 5 entries as organic, naturally-triggered floor evaluations.**
They should be read as: real evaluations that happened for an incorrect
reason. Anyone computing "how often does the floor force consideration of
format X" using this log should be aware these 5 rows are not a genuine
floor trigger and may skew that specific analysis if counted as one.

## Related record

See `docs/KNOWN_ISSUES.md` entry F69 for the root-cause process gap this
incident revealed (acting on an unverified "never logged" assumption
instead of checking real log history before writing new events).

## Disposition

No log entries edited or deleted. `build_manifest.py`'s
`minimum_frequency_floor` block for batch `9a7d935f` has been corrected to
report the real values (`days_since_last_considered: 3`,
`must_force_consider: false` for all 5 formats), with an inline `_note`
field pointing back to this correction and to F69.

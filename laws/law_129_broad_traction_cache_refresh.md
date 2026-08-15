# Law #129 — Broad Traction Cache Refresh (3-Day Cap)

**Status:** ACTIVE. Documented here for the first time — this law was cited and
enforced in `cron_daily_runtime.txt` prior to this file existing, with no standalone
definition anywhere in the repo. This file records what the live runtime actually
does; it does not introduce new behavior.

## The Rule

Before the shared market sweep runs in the daily dual-package generation, check
`cron_traction_cache.json`:

- If the file is **missing**, OR its timestamp is **older than 3 days** — run the
  full refresh stack (Crunchyroll top 10, MAL seasonal, AniList trending, open-web
  trending) and rewrite the cache with a fresh timestamp.
- If the cache is **under 3 days old** — reuse it as-is. Do NOT re-run the refresh
  stack.
- Log the outcome to the run log as `"Traction cache: CURRENT [date] / REFRESHED
  [date]"`.

This caps how often the broad traction sweep can run, independent of how often the
daily cron itself fires — it exists to avoid re-running the same broad market sweep
every single day when the underlying trending data hasn't meaningfully changed.

## Cache File Shape (as actually produced)

`cron_traction_cache.json` currently contains: `status`, `generated` (ISO8601
timestamp), `note` (free-text refresh rationale), `sweep_summary` (free-text
description of the searches run), `sources[]` (topic/url/publisher/date per
source), `candidates_evaluated_and_excluded[]` (show/reason pairs).

## Enforcement Status

The run manifest schema in `validators/validate_dual_package.py` documents a
`traction_cache: {timestamp, age_days, status}` shape as a comment in the schema
docstring. **This is not currently checked by any validator logic** — there is no
pass/fail assertion on cache age, staleness, or presence. The 3-day rule is
currently followed only as runtime instruction text, not as a machine-enforced gate.
This gap is noted here so future drift (a manifest claiming `CURRENT` with a stale
or missing real cache) has a definition to be checked against, even though nothing
currently catches it automatically.

## Origin

Referenced from `cron_daily_runtime.txt` STEP 2 as "Law #129" prior to this file's
existence. No dated origin note or user statement establishing this law was found
elsewhere in the repo.

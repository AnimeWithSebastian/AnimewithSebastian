# LAW #61 — ANALYTICS FEEDBACK LOOP
**System:** AnimeWithSebastian — v5.1
**Added:** June 2026
**Status:** ACTIVE

---

## THE LAW

The system reads its own results every week. What worked changes what gets made next.

The weekly analytics cron is not a reporting tool. It is a correction tool.

---

## THE CRON

**ID:** 2bb28991
**Schedule:** Sundays at 11:30 PM UTC (7:30 PM ET)
**First run:** Sunday June 14, 2026
**Delivery:** hero_or_villain@outlook.com ONLY

---

## WHAT THE CRON DOES

1. Pulls YouTube analytics via YouTube Analytics API
2. Matches data to sent_scripts_log.json entries (video ID → script record)
3. Grades every video using the scoring system below
4. Saves full report to analytics_performance_log.json
5. Emails complete report to hero_or_villain@outlook.com

---

## SCORING SYSTEM

Each video receives one of five grades:

| Grade | What It Means |
|---|---|
| **LOOP SIGNAL** | High view velocity, strong retention loop, watch-through above average. System prioritizes this format and angle. |
| **STRONG** | Solid retention, good engagement relative to views. Keep producing similar content. |
| **AVERAGE** | Performing at channel baseline. Monitor — if trend continues, reconsider angle. |
| **WEAK** | Below baseline on views, retention, or engagement. Do not repeat this format/angle combination. |
| **DROP** | Clear underperformer across all metrics. Flag for possible deletion review. |

---

## WHAT GETS MEASURED PER VIDEO

- **Views** — raw view count
- **Watch time** — total minutes watched
- **Retention rate** — average percentage viewed (pulled from YouTube Analytics)
- **Likes** — absolute count and like-to-view ratio
- **Comments** — absolute count and comment-to-view ratio
- **Shares** — absolute count
- **Engagement score** — composite of likes + comments + shares relative to views

---

## HOW GRADES UPDATE THE SYSTEM

The cron does not just report. It feeds back into the production system.

### Angle Bank Updates
- LOOP SIGNAL videos → their angle type is flagged as HIGH PRIORITY in the morning and evening crons
- WEAK / DROP videos → their angle type is flagged as AVOID for the following week

### Show Rotation Updates
- If a show's videos consistently grade AVERAGE or below → the show moves to lower rotation
- If a show's videos grade STRONG or LOOP SIGNAL → the show moves to higher rotation

### Format Priority Updates
- If a specific format (e.g. CHARACTER_DIVE) consistently outperforms → that format gets weighted higher in the nightly format recommendation
- If a format consistently underperforms → it drops in priority for 2 weeks before being re-evaluated
(Tracking note: this mechanism has zero code enforcement and no state file currently exists — see docs/UNDERPERFORMANCE_DEPRIORITIZATION_TRACKING.md before treating this rule as actually applied to any real selection.)

---

## THE MEMORY FILE

All grade data is saved to:
~~`/home/user/workspace/analytics_performance_log.json`~~ → `analytics_performance_log.json` (repo-relative)

> **CORRECTED 2026-08-15 during a law audit — TWO problems, one of them substantive.**
>
> 1. **Stale path (mechanical):** the `/home/user/workspace/` prefix is the old sandbox
>    layout and does not resolve in this repo-based checkout. Per Session Fixes FIX 25
>    the GitHub repo is the authoritative source, so the path is repo-relative.
>
> 2. **THE FILE DOES NOT EXIST (substantive):** there is no
>    `analytics_performance_log.json` anywhere in this repo. The paragraph below states
>    that it "accumulates week over week" and that "the cron reads the previous week's
>    data before generating new grades" — describing an accumulating trend history that
>    is not actually being written or read. **Law #65 already carries this caveat**
>    ("This file does not currently exist in the repo; see
>    `docs/UNDERPERFORMANCE_DEPRIORITIZATION_TRACKING.md` Finding 3"); Law #61 — the law
>    that actually DEFINES the file — did not, which made this the more misleading of the
>    two references. Anyone reading #61 alone would reasonably believe week-over-week
>    grade history exists.
>
> The scoring system and feedback-loop rules in this law are UNCHANGED and still apply;
> only the storage claim is inaccurate. Whether to build the file, or to rewrite this
> section around what the weekly cron genuinely persists (`cron_tracking/2bb28991/state.json`
> plus the publication ledger), is a real decision and is deliberately NOT made here.

~~This file accumulates week over week. The cron reads the previous week's data before generating new grades, so trends can be identified across multiple runs.~~

> **STORAGE SECTION REWRITTEN 2026-08-15, on owner decision — this replaces the
> struck claim above with what is actually on disk.** The correction banner above is
> retained as the historical record of when the problem was first caught; this block
> is the fix. Verified by direct inspection of the real files on 2026-08-15.
>
> **`analytics_performance_log.json` does not exist and no code writes it.**
> `find` returns nothing, and `grep -rn "analytics_performance_log" --include="*.py"`
> returns nothing. There is no accumulating log, and nothing reads a previous week's
> data before grading. Grade history is NOT continuous.
>
> **WHAT IS ACTUALLY PERSISTED — two things, neither of them an accumulating log:**
>
> **1. `cron_tracking/2bb28991/state.json` — a single overwritten snapshot, not a
> history.** It holds only the most recent run's summary. Current contents include
> `last_run`, `run_count` (7), `videos_graded` (58), `top_performer` and
> `bottom_performer` as single formatted strings, `tier_breakdown`
> (`{LOOP_SIGNAL: 4, STRONG: 30, AVERAGE: 22, WEAK: 2, DROP: 0}`),
> `analytics_processed_video_ids`, `channel_totals`, `reconciliation`,
> `model_compliance`, `github_sync`, `email_sent`, `notes`, `last_noop_ts`. Each run
> overwrites the previous values. Prior weeks' numbers are not recoverable from it.
>
> **2. `cron_tracking/2bb28991/run<N>_grades.json` — per-run grade arrays, but only
> for SOME runs.** Two exist: `run2_grades.json` (41 entries) and
> `run4_grades.json` (49 entries). `run_count` is 7, so **five of seven runs left no
> grade file at all.** These are the only real per-video grade records in the repo.
>
> **THE TWO GRADE FILES USE DIFFERENT SCHEMAS.** This is a real obstacle to any
> future trend analysis and is recorded here rather than discovered later:
>
> | Concept | `run2_grades.json` | `run4_grades.json` |
> |---|---|---|
> | video identifier | `video_id` | `vid` |
> | retention | `retention` | `avg_pct` |
> | view points | `view_pts` | `v_pts` |
> | retention points | `ret_pts` | `r_pts` |
> | engagement points | `eng_pts` | `e_pts` |
> | only in run4 | — | `subs_lost`, `sub_conv_pct` |
>
> Shared by both: `views`, `likes`, `comments`, `shares`, `mins_watched`,
> `subs_gained`, `eng_per_100`, `score`, `tier`.
>
> **CONSEQUENCE FOR THIS LAW'S FEEDBACK LOOP.** The scoring system, tier
> definitions, and feedback-loop rules in this law are UNCHANGED and still apply to
> a single run's grading. What this law can NOT currently support is any rule that
> depends on comparing a video or a format against previous weeks — the data for
> that is partial (2 of 7 runs), schema-inconsistent between those two, and absent
> from `state.json`, which keeps only the latest snapshot. Treat any cross-week trend
> claim as unsupported until an accumulating store actually exists.
>
> **BUILDING THE ACCUMULATING LOG IS STILL AN OPEN OPTION, NOT A CLOSED ONE.** This
> rewrite documents reality; it does not decide that the capability should be
> abandoned. If it is built later, note that backfill can only draw on those same two
> grade files and would need the schema differences above reconciled first.

Format per entry:
```json
{
  "video_id": "string",
  "title": "string",
  "grade": "LOOP SIGNAL | STRONG | AVERAGE | WEAK | DROP",
  "views": number,
  "watch_time_minutes": number,
  "retention_rate": number,
  "likes": number,
  "comments": number,
  "shares": number,
  "engagement_score": number,
  "week_of": "YYYY-MM-DD",
  "format_type": "string",
  "show": "string"
}
```

---

## ENFORCEMENT

This law is not enforced at VO level. It is a system-level law.

The analytics cron (2bb28991) is its enforcement mechanism. The cron runtime file (cron_analytics_runtime.txt) contains the execution instructions.

If the cron fails to run on a given Sunday → it catches up on the next manual trigger or the following Sunday.

---

## WHY THIS EXISTS

Without this law, the system produces content in the dark. Every show gets equal time. Every format gets equal weight. The channel gets no smarter.

With this law, the system learns. What the audience actually watches changes what the system makes next.

---

## RELATED LAWS
- Law #58 — Pre-Send Verification (content quality before publish)
- Law #53 — Airing Status (show rotation — feeds into this law's rotation updates)
- Law #57 — Hidden Gems Pillar (performance of hidden gem angles tracked here)

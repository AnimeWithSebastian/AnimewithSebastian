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

This file accumulates week over week. The cron reads the previous week's data before generating new grades, so trends can be identified across multiple runs.

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

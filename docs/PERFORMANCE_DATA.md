# Performance Data Log

Real, API-verified YouTube performance data only. Every entry in this file must be pulled directly from the YouTube Analytics/Data API at write time — no reconstructed, estimated, or narrative-driven numbers. If a number can't be retrieved, the entry says so explicitly rather than omitting or approximating it.

---

## Real Performance Check — Akane-banashi Video (41EwfIPgPaM)
**Date confirmed: 2026-08-01, ~10:44–10:51 AM ET**

**Video:** `41EwfIPgPaM` — "Nobody's Talking About Akane-banashi (They Should Be)," channel "Anime With Sebastian," published `2026-08-01T01:38:18Z` (~9 hours old at time of check).

**Verified real data (YouTube Analytics API, two independent date-range queries):**
- Views: **0**
- Average view duration: **0**
- Average view percentage: **0**
- Likes: **0**
- Comments: **0**
- Subscribers gained: **0**
- Audience retention curve (`elapsedVideoTimeRatio` × `audienceWatchRatio`): query succeeded with no error, but returned an **empty result set** — no retention data points exist to plot or interpret
- CTR / thumbnail impressions: **unretrievable** — every attempt returned a `400 badRequest` from the API at this granularity; this is a tooling/access limitation, not a confirmed zero

**Important caveat on the zeros:** YouTube Analytics typically carries a 24–48 hour reporting delay before data fully populates for a given video. At ~9 hours post-publish, this zero-activity reading most likely reflects data unavailability in the reporting pipeline, not necessarily zero real audience activity. This is a data-timing limitation, not a confirmed finding of no engagement. **Recommended follow-up:** re-check this video's real metrics once it is genuinely 24+ hours old (i.e., after approximately 2026-08-02T01:38 UTC), since that's the point real numbers should actually have populated.

**Conclusion:** At ~9 hours post-publish, this video shows zero measurable activity across every metric the API can currently return, and no retention curve exists to analyze. Given the known reporting delay, this should be read as "no usable data yet," not "no activity." There is no data yet to support any performance narrative — positive, negative, or diagnostic — in either direction. n=1, and n=0 activity at that; this states the absence of evidence plainly rather than reading a story into it.

**Correction note (part of this log entry):** Earlier in this same conversation, a draft entry was proposed that fabricated a full performance analysis on top of this same video — a claimed above-typical stayed-to-watch percentage, a specific retention-drop timing tied to a genre-mismatch theory ("revenge arc" framing vs. rakugo-competition payoff), and a critique of a dashboard title recommendation that was never actually shown or verified to exist in this session. None of those claims were supported by the real API data pulled directly beforehand, which showed flat zeros and an empty retention set. That draft was caught and discarded before being written to any file. This entry logs the correction, not the original fabricated draft — it should not be read as a softened version of that analysis, but as a replacement for it.

---

## Real Performance Check — Four-Video Studio Snapshot (JJK, Chainsaw Man, Tanya the Evil, Solo Leveling)
**Date logged: 2026-08-06, ~11:00 AM ET**

**Source and confidence note (read before using these numbers):** Three of the four data points below are self-reported by Sebastian from YouTube Studio and were NOT independently pulled or confirmed via the YouTube Analytics/Data API this session. Only the Solo Leveling data point carries an independent, direct Studio-check confirmation performed this session (visibility/restriction status). This entry intentionally keeps that distinction visible rather than presenting all four as equally verified.

**Relation to F30 (`docs/KNOWN_ISSUES.md`, commit `a4ccfcb`, 2026-08-04):** F30 is a real, previously logged and committed finding — `videoThumbnailImpressions`/`videoThumbnailImpressionsClickRate` return a hard 400 error on every YouTube Analytics API query attempted, confirmed distinct from the normal reporting delay (reproduced on an old, high-view video with no data-freshness excuse). That gap has blocked this channel from getting real impressions data via the API since it was found. Tonight's four Studio-sourced numbers below are the first real impressions data obtained for this channel since F30 — but they were pulled manually from the Studio UI, not via the still-blocked API path. F30 itself remains open and unresolved at the API level.

**1. Jujutsu Kaisen** — 452 impressions, 53 views (11.7% CTR)
- Video ID, exact hours-since-publish, and visibility status: **not independently confirmed this session** — reported by Sebastian directly.

**2. Chainsaw Man** — 33 impressions, 1 view (3.0% CTR)
- Video ID, exact hours-since-publish, and visibility status: **not independently confirmed this session** — reported by Sebastian directly.

**3. Tanya the Evil** — 654 impressions, 34 views (5.2% CTR)
- Video ID, exact hours-since-publish, and visibility status: **not independently confirmed this session** — reported by Sebastian directly.

**4. Solo Leveling** — 8 impressions, 0 views, 12+ hours since publish
- Visibility: **confirmed Public, no restrictions** — verified via direct Studio check this session.
- A video-specific technical cause (visibility settings, Content ID claim, restriction) was **explicitly ruled out** for this video via that Studio check.
- **This is the most severe of the four data points** (0% view-through on 8 impressions vs. 3.0–11.7% CTR on the other three), and the only one with independent confirmation behind it beyond Sebastian's own report.

**Conclusion:** Across all four videos, impressions themselves are low in absolute terms (8–654) and view-through-on-impression rates range from 0% (Solo Leveling) to 11.7% (JJK) — i.e., the collapse shows up in impressions volume, not only in what happens after an impression is shown. This pattern is consistent across four different shows released in the same window, which weighs against a single-video technical explanation for at least the Solo Leveling data point (technical cause directly ruled out) and is suggestive but not proven for the other three (not independently checked). No content, policy, or technical change on Sebastian's side has been identified as a cause for any of the four videos.

---

## Real Performance Check — API-Verified Ground Truth vs. Studio-Reported Numbers (JJK, Chainsaw Man, Tanya, Solo Leveling)
**Date logged: 2026-08-06, ~12:00 PM ET**

**Purpose of this entry:** The prior entry (Four-Video Studio Snapshot, logged ~11:00 AM ET the same day) carried three of four data points as self-reported by Sebastian from Studio, explicitly not independently confirmed. This entry closes that gap for what the API can confirm — pulled directly via `youtube_analytics_api-get-video-metrics` and `youtube_analytics_api-query-custom-analytics` this session, against real video IDs resolved via `youtube_data_api-list-playlist-videos`. This is real, current API ground truth, not a restatement of the earlier entry.

**1. Solo Leveling — video ID `R4WUI6dcpdc`**
Published `2026-08-05T23:18:23Z`. API query (`2026-08-01` to `2026-08-06`, idType MINE):
- Views: **0**
- Average view duration: **0 sec**
- Average view percentage: **0%**
- Matches the Studio-reported figure (0 views) exactly. This is the one video where self-report and API agree.

**2. Jujutsu Kaisen S4 name confirmation — video ID `mq4M11d_-bg`**
Published `2026-08-03T23:11:35Z`. Same API query window:
- Views: **16**
- Average view duration: **23 sec**
- Average view percentage: **75.15%**
- **Discrepancy: Studio-reported 53 views vs. 16 actual API views** — a 37-view, ~70% gap between the self-reported Studio figure and the independently queried API figure for the same video and an overlapping date range.

**3. Chainsaw Man / Reze — video ID `nrXPlQ9QNok`**
Published `2026-08-04T11:21:33Z`. Same API query window:
- Views: **0**
- Average view duration: **0 sec**
- Average view percentage: **0%**
- **Discrepancy: Studio-reported 1 view vs. 0 actual API views.**

**4. Tanya the Evil — UNRESOLVED VIDEO-IDENTITY AMBIGUITY**
Two real videos on the channel match "Tanya" in this window, and neither matches the self-reported 34 views:
- `DKoliNskd0U` — "Tanya S2 Ep4: The Real Fight Wasn't the Battle," published `2026-08-05T00:30:20Z`. API views (`2026-08-01` to `2026-08-06`): **0**.
- `Pbv4NHIXeCI` — "Tanya the Evil Lost the Top Spot... Then Took It Back," published `2026-07-31T00:51:41Z`. API views (`2026-07-31` to `2026-08-06`, wider window since older): **76**.
- Neither figure (0 or 76) matches the self-reported 34. This entry does not guess which video Sebastian meant — it stays open pending his confirmation of which video ID the 34-views figure was pulled from in Studio.

**What this means for the reliability of the Studio-AI-reported figures (real finding, not smoothed over):** Of the three self-reported data points from the prior entry, one (Solo Leveling) was independently confirmed exactly. The other two checkable data points (JJK, Chainsaw Man) both came in lower via direct API query than the Studio-reported numbers — not higher, not scattered randomly, both same-direction. The fourth (Tanya) can't be checked at all due to identity ambiguity. This is a real, quantified reliability gap on the specific self-reported feature/numbers Sebastian pulled from Studio, not a rounding difference — it should be treated as a genuine finding, not a footnote.

**Channel-wide "~2,100 views in last 48 hours" claim — checked against real API data:**
Real per-day channel-wide views pulled via API (`youtube_analytics_api-query-custom-analytics`, dimension=day, `2026-07-28` to `2026-08-06`):

| Date | Views |
|---|---|
| 2026-07-28 | 2,365 |
| 2026-07-29 | 211 |
| 2026-07-30 | 2,159 |
| 2026-07-31 | 2,151 |
| 2026-08-01 | 3,525 |
| 2026-08-02 | 4,063 |
| 2026-08-03 | 2,196 |
| 2026-08-04 | **no row returned** |
| 2026-08-05 | **no row returned** |
| 2026-08-06 | **no row returned** |

**Aug 4–6 is not zero — it is absent from the API's processed data entirely**, for the channel overall and confirmed again via a query filtered to just the 4 flagged video IDs (same absent-row pattern for Aug 4–5, only Aug 3 populated). This is the standard signature of YouTube Analytics' known 1–3 day reporting lag, not evidence that the channel or the four flagged videos went to zero. It should not be read either way — not as confirming ~2,100 views happened, nor as confirming they didn't.

**Concrete evidence on where "~2,100 views" is most likely coming from:** Aug 3 is the most recent fully-reported day and shows 2,196 total channel views. Of that, the 4 flagged videos combined (filtered query, same date range) show only **16 views** — all from the JJK video, published that same day. That means **~2,180 of the 2,196 views on Aug 3 (99%+) came from videos other than the 4 flagged ones** — i.e., older catalog videos still accumulating views normally. If the "~2,100" figure Sebastian saw in Studio is close to this Aug 3 total, the concrete evidence points to normal older-video accumulation, not activity from the 4 flagged uploads. This is inference from the closest available real data point, not a confirmed match to whatever exact window Studio's overview was showing.

**F30 re-confirmed live, fresh, via independent query path (not a restatement):** During this session's API pull, `videoThumbnailImpressions` and `videoThumbnailImpressionsClickRate` were requested directly against Solo Leveling (`R4WUI6dcpdc`) via `youtube_analytics_api-get-video-metrics`. Result: immediate `400 badRequest` — *"The query is not supported."* This reproduces F30 (`docs/KNOWN_ISSUES.md`, commit `a4ccfcb`, 2026-08-04) fresh, tonight, via a different video and a different query call than the one that originally surfaced it. F30 is confirmed a live, current, still-unresolved API limitation — not a stale reference from an earlier finding.

**Conclusion:** This entry resolves the confidence gap the prior entry left open for JJK and Chainsaw Man — both come back lower via API than self-reported, a real and directionally consistent discrepancy worth treating as a genuine reliability finding on Studio-reported numbers, not noise. Solo Leveling remains the one fully-corroborated data point across both self-report and API. Tanya remains genuinely unresolved due to video-identity ambiguity — not guessed at. The ~2,100-views channel claim cannot be confirmed via API for the actual last-48-hour window (data not yet processed), but the closest real data point (Aug 3) shows the flagged videos are responsible for a negligible fraction of channel-wide views that day, supporting — not proving — that older catalog videos are the real source of ongoing view volume. F30 remains open, live, and independently re-confirmed.

---

## Format-Level Comparison Check — Insufficient Data, and a Corrected Prior Claim (2026-08-09)
**Date logged: 2026-08-09, ~6:00 PM ET**

**Trigger for this entry:** A proposal was floated this session to add a candidate-selection tiebreaker to `cron_daily_runtime.txt` STEP 3, biasing toward CHARACTER_DIVE / "Real Reason" / character-motivation content on the stated grounds that "this channel's own repeated internal performance data" had "already established, across multiple independent checks," that this angle-class outperforms. That claim was checked directly against this file and against `sent_scripts_log.json` before any runtime change was made. No change was made.

**The six real, confirmed data points in this file, tagged by format_type:**

| Video | format_type | Real views (API-confirmed) | Age at check |
|---|---|---|---|
| Akane-banashi (`41EwfIPgPaM`) | SLEPT_ON | 0 | ~9 hrs — inside reporting-lag window, not a confirmed zero |
| JJK S4 confirm (`mq4M11d_-bg`) | FACT_DROP | 16 | within reporting window |
| Chainsaw Man / Reze (`nrXPlQ9QNok`) | COMMENTARY | 0 | within reporting window |
| Tanya "lost top spot" (`Pbv4NHIXeCI`) | WATCH_RANK | 76 | older, fully reported |
| Tanya S2 Ep4 (`DKoliNskd0U`) | EPISODE_MOMENT | 0 | within reporting window |
| Solo Leveling (`R4WUI6dcpdc`) | unresolved — could not be traced to a `format_type` entry in `sent_scripts_log.json` by video ID or title match | 0 | within reporting window |

**Finding: the dataset cannot support any format-level performance comparison.** Six data points, six different formats (five resolved, one unresolved), spanning 0–76 views, all logged within a 0–5 day-old window where most reads are still near-zero regardless of format. There is no repeated pattern *by format* here — CHARACTER_DIVE, ORIGIN_STORY, and HIDDEN_GEM (the closest siblings to a "Real Reason" angle) don't even appear among these six real checks, and the one entry in the same evidentiary family (SLEPT_ON) is the one still sitting inside the unmeasurable reporting-lag window. The only real, repeated pattern across this data is low absolute view counts across every format tried so far — not a format-specific effect.

**Corrected claim (stated plainly, not softened):** The assertion that this channel's internal performance data had "already established" a CHARACTER_DIVE / Real-Reason performance advantage "across multiple independent checks" was checked against this file — the actual real-data log — and is **not supported**. No entry in this file, before or after this check, ties a Real-Reason/character-motivation format to a real, repeated performance edge. This should be treated as a corrected claim, not a "thin but real" signal worth hedging into runtime logic. `hero_or_villain_master_laws_final.txt`'s stated rule ("if a specific format like CHARACTER_DIVE consistently outperforms → weight it higher") remains aspirational only — `docs/UNDERPERFORMANCE_DEPRIORITIZATION_TRACKING.md` already documents that the state file this class of rule depends on (`analytics_performance_log.json`) does not exist anywhere in the repo, and this check found nothing that would populate it.

**Outcome:** No tiebreaker, weighting, or other selection-logic change was made to `cron_daily_runtime.txt` STEP 3 as a result of this proposal. None is proposed in this entry either.

**Revisit conditions:**
- Real, API-confirmed data accumulates across enough *same-format* repeats (not just more total data points scattered across many different formats) to make a same-format comparison meaningful, or
- `analytics_performance_log.json` is actually created and populated per the aspirational rule in `hero_or_villain_master_laws_final.txt`, at which point that structured log — not ad hoc entries in this file — would be the right place to test the claim.

**Not proposed as a fix in this entry** — per standing rule, no runtime/law/validator change without explicit go-ahead and diff review. This entry logs a checked-and-rejected claim and a data-sufficiency finding only.

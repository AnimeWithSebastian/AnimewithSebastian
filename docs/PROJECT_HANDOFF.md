# Project Handoff — AnimeWithSebastian (AnimeWithSebastian)

**Purpose:** This is the single consolidated recovery document for this repository.
A future Computer task (or any operator) should be able to fully recover project
state, rules, and history from this file plus the live repo — **without** needing
to read the full historical conversation transcript.

**Status as of:** 2026-07-23. **Authoritative main commit at time of writing:**
`8a4798c9e45b54ed7a187de79e9133311c82aad5` (merge of PR #5, publication-ledger repair tool + this handoff doc).

**Publication-ledger repair status:** DEPLOYED, NOT YET USED. `tools/record_publication.py`
and its 21 unit tests merged to `main` via PR #5
(https://github.com/SEBLABHRIS/AnimeWithSebastian/pull/5, merge commit `8a4798c9e...`).
`cron_tracking/publication_ledger.jsonl` is still 0 lines — the tool has not been invoked
against any real video yet. It remains a manual, explicitly human-invoked step; it is NOT
wired into `cron_daily_runtime.txt` or `cron_analytics_runtime.txt`, and no automatic
YouTube polling has been added. It is a separate post-upload action, never part of daily
content generation. **Awaiting the first verified real upload** before the ledger gets its
first row.

**Operating procedure for recording a real publication (going forward):** when the
channel owner provides a real YouTube URL/video ID and the corresponding `package_id`,
(1) fetch that exact video's metadata live through the connected YouTube Data source,
(2) verify `status.privacyStatus == "public"` from that real response, (3) save the
verified response to a JSON file, then (4) invoke `tools/record_publication.py` with that
file plus the explicit `--package-id` and `--youtube-video-id`. Never infer or match the
package from the video's title — `package_id` is the only valid lookup key, enforced by
the tool itself.

**Convenience wrapper added 2026-07-24: `tools/mark_published.py` (+ 18 unit tests).**
`package_id` is manifest-only and never appears in the actual production email, so
requiring it to be hand-typed wasn't usable. The wrapper accepts `--show` and
`--post-date` instead (both visible in the email subject line) and looks up the
matching `package_id` from `cron_tracking/sent_scripts_events.jsonl` automatically —
or lists every sent-but-unpublished package interactively with `--list` for manual
selection. **This lookup is a convenience filter only** (case-insensitive substring on
`--show`, exact match on `--post-date`) and plays no role in the actual fail-closed
write path: `mark_published.py` calls `record_publication.record_publication()`
unmodified once a `package_id` is resolved, so every one of its checks (video-id
format, sent-event existence, verified-metadata id/public-status match, no-duplicate-
video, no-duplicate-package) still applies exactly as before, with no override or
bypass flag added. Any ambiguous or zero-result lookup (e.g. this repo's own "Bleach:
Thousand-Year Blood War - The Calamity" vs "Bleach TYBW Part 4 — The Calamity" show-
name variants) drops into an interactive picker rather than guessing. Still a manual,
human-invoked step — not wired into either cron runtime.

**Golden rule:** GitHub is the authoritative source for laws, runtimes, validators,
templates, and production state. Never reconstruct rules from memory or from an old
conversation summary when the repo has the real files. This document is a map/index
to the repo, not a replacement for reading the actual law/runtime files it points to.

---

## 1. Brand and channel

- Brand: **AnimeWithSebastian** (handle `@animewithsebastian`). "Hero or Villain"
  and "AnimeWithSebastian" are retired former names, confirmed superseded 2026-07-23 —
  do not use them for the channel going forward. "AnimeWithSebastian" is a
  separate, still-current name: it refers to the automation/production system
  itself (the GitHub repo `AnimeWithSebastian`), not the channel.
- Content: opinionated anime analysis/commentary — not summaries. Challenge
  assumptions, analyze motives, compare heroes/villains, explain hidden themes,
  capitalize on timely anime news. Every idea should give viewers something
  specific to debate.
- Primary platform: **YouTube Shorts**. Secondary: **TikTok**. Editing tool:
  **CapCut**.
- Goal: increase retention, comments/engagement, repeat viewers, subscriber
  conversion; find repeatable formats; build successful 8–12 min flagship
  long-form videos.
- Owner timezone: **America/New_York**.

## 2. Where the rules actually live (read these, not this summary, for exact text)

| Topic | File(s) |
|---|---|
| Full historical law text | `hero_or_villain_master_laws_final.txt` |
| Individual recent laws (#53–#147) | `laws/law_*.md` — **grep this directory first** before searching the master file |
| Daily production runtime (authoritative, what the daily cron actually reads) | `cron_daily_runtime.txt` |
| Weekly analytics runtime | `cron_analytics_runtime.txt` |
| Per-slot email/package shape | `templates/package_template.txt` |
| Scheduled-task prompt text | `scheduler/daily_dual_package_task.txt` |
| Deterministic Shorts validator (fail-closed) | `validators/validate_dual_package.py` (+ tests, fixtures) |
| Deterministic long-form validator | `validators/validate_longform_flagship.py` (+ tests) |
| Atomic dual-event logger | `tools/append_send_batch.py` |
| Weekly no-op gate | `tools/weekly_noop_gate.py` |
| Credit-safe mode policy | `docs/CREDIT_SAFE_MODE.md` |
| Dual-package migration/rollback | `docs/MIGRATION_dual_package.md` |
| Blackout / recent-use tracking | `blackout_state.json` |
| Legacy package send history | `sent_scripts_log.json` |
| Append-only send events | `cron_tracking/sent_scripts_events.jsonl` |
| Publication source of truth (by `youtube_video_id`) | `cron_tracking/publication_ledger.jsonl` |
| Per-cron runtime state | `cron_tracking/<cron_id>/state.json` |

**Authority order when sources conflict:** (1) current production runtimes/validators
→ (2) newest numbered law file → (3) master laws file → (4) templates/docs →
(5) older/superseded language.

## 3. Scheduled tasks (do not duplicate — check `list` before creating/updating)

| Task | ID | Cron (UTC) | Local time (ET) | Notes |
|---|---|---|---|---|
| Daily dual-package | `087efcd5` | `30 22 * * *` | 6:30 PM | One shared Claude Sonnet 5.0 context produces next day's morning + evening Shorts packages. |
| Weekly analytics | `12200bb4` | `30 23 * * 0` | Sunday 7:30 PM | Uses YouTube Data + YouTube Analytics connectors; joins on `youtube_video_id` only. |

Both live in Computer session `bb0ddd08-2998-490f-badb-e9fae683899f` as of
2026-07-23. **Migration history:** the tasks originally lived in session
`30e0c963-bdcb-4eda-a1fe-5036617e54a1` under IDs `322f616a` (daily) and
`2bb28991` (weekly). On 2026-07-23 the user authorized migrating both into the
current conversation: the old IDs were deleted from their owning session first
(cross-session delete is not possible directly), confirmed gone via a
cross-session `list`, then immediately recreated here with byte-identical
names/cron expressions/task bodies/`background=false`/`exact=true` settings
(captured from the live tasks before deletion, not reconstructed from memory).
No run occurred during migration (`run_count=0` on both new tasks immediately
after creation); the daily task's next fire is still today, 2026-07-23 6:30 PM
ET, and the weekly task's next fire is unchanged, Sunday 2026-07-26 7:30 PM ET.
A cross-session `list` after creation confirmed exactly two AnimeWithSebastian
recurring tasks exist platform-wide, both in session `bb0ddd08...`, with no
remaining trace of `322f616a` or `2bb28991`. If citing an old commit or prior
turn that references `322f616a`/`2bb28991`/`30e0c963`, treat those as
historical — the IDs above are current.

## 4. Model routing (Law #137)

- **Claude Sonnet 5.0** — all routine daily work: live research, idea generation,
  research synthesis, format selection, VO drafting, one-pass semantic QA.
- **Highest-quality reasoning model (Claude Fable 5 allowlist)** — ONLY for:
  flagship 8–12 min long-form scripts, major channel strategy decisions, full
  system redesigns, difficult/hard audits, refining an already-proven idea into
  its best version, monthly deep performance reviews.
- Never route routine daily generation to the expensive model. Save credits by
  removing duplicate work, never by lowering research/writing quality or posting
  frequency.

## 5. Shorts production rules (current/final state — see `laws/law_139` through `law_147`)

- Two independent packages/day: morning + evening, different shows/angles/formats/
  hooks/titles, one shared live-market research sweep (Law #139).
- Default edit **exactly 30 seconds**; VO **100–108 words, target ~104**, must fill
  the entire edit, no dead air (Law #138, #131 v3). Optional 45–59s experiment ONLY
  for list/ranking + recurring series, capped at 1/batch (Law #140 extension).
- **Anime footage only. Never face-cam in Shorts** — face is reserved exclusively
  for long-form (this reverses an earlier face-cam experiment; Law #134 final state).
- Every cut needs `duration_sec` + `timeline_start_sec` + `timeline_end_sec`; cuts
  tile the 30s edit contiguously (first starts at 0, last ends at 30, durations sum
  to 30); email renders each cut plus a final `TOTAL CLIP TIME: 30 seconds` line
  (Law #140).
- Hook: assumption-breaking, understandable immediately, must land in the first
  second on-screen and spoken. Generate exactly 2 internal `hook_candidates`,
  publish only the strongest (`selected_hook_index`). Morning/evening published
  hooks must differ (Law #144, #145).
- CTA: one specific question immediately followed by exactly **"Leave your take."**
  "Drop it" is permanently banned.
- Loop — **RESCINDED as a mandate, July 27, 2026 (Law #141, commit `5846da3`)**: the
  direct-colon seamless loop is now OPTIONAL, not required. When a package does
  attempt it, the same mechanics still apply — `loop_line` as an incomplete setup
  ending in a colon `:`, `opening_sentence` completing it as one continuous thought,
  final and opening must not be identical, keyword/topic repetition alone does not
  count, `carries_loop_back: true` on the final cut. A package may omit the loop
  entirely with no penalty.
- Titles (Law #144, **PR #4** final spec):
  - `youtube_title` — hard max **60 chars**, target **35–50**, one punchy idea, no
    hashtags, no explanatory subtitle, show keyword early when natural.
  - `tiktok_title` — separate field, hard max **55 chars**, target **30–45**, no
    hashtags.
  - Both differ from each other, from the published hook, and between morning and
    evening packages. The longer `tiktok_post_text` caption may still carry
    hashtags — the title fields never do.
- Quality over quota (M5): never publish/send a weak package to fill a slot — hold
  it and let the weekly cron flag the miss.
- Self-attestation fields (M6): `hook_first_second`, `loop_read_aloud_pass` (only
  meaningful when a package opts into the loop; ignored otherwise),
  `topic_class`, `hook_family` are model self-reports, not machine-verified facts —
  set honestly, subject to weekly human spot-check.

## 6. Research and semantic QA

- Use current live information; one shared market sweep serves both packages.
  Prefer airing/premiere/chapter/announcement/ranking/active-conversation topics;
  evergreen allowed when genuinely strong.
- Verify each selected idea with **≥2 credible, dated sources**. No core claim may
  rely solely on Wikipedia, Fandom, or MyAnimeList. Map every core claim to a
  source. Never fabricate facts, dates, quotes, or trends.
- Semantic QA (one-pass, same model context, Law #147 Part 1) per package:
  claim-to-source matrix with core/non-core designation, VO word-count check,
  CTA-adjacency check, title check, blackout/recent-send conflict check,
  clip-timing check, colon-loop check (only applicable when the package opts into
  the loop), exact final-to-opening read-aloud string (when applicable),
  honest `audited_before_return` confirmation. **Never mark a check true merely to
  pass validation** — fix the draft in the same context instead.
- Deterministic validator (`validators/validate_dual_package.py`) runs before send
  and **fails closed** — non-zero exit blocks the send; fix and re-run.

## 7. Long-form (separate product — Law #146)

- Target 8–12 minutes. Face footage allowed and encouraged. Requires deeper
  structure, pacing, evidence, transitions — never a stretched 30-second formula.
- A Short may only become a flagship teaser once a real `flagship_url` exists,
  capped at ≤3 teasers/week.
- Validated by `validators/validate_longform_flagship.py`, a separate validator
  from the Shorts one. May use Sonnet 5.0 or the Fable-tier model.

## 8. Weekly analytics (Law #143 targets checked here; Law #147 Part 2 no-op gate)

- Connectors: YouTube Data + YouTube Analytics.
- **`cron_tracking/publication_ledger.jsonl` is the sole publication source of
  truth.** Join packages to published videos ONLY by actual `youtube_video_id` —
  never match by title. `sent_scripts_log.json` is package history only, never
  proof of publication.
- Reports four buckets: `JOINED`, `PUBLISHED-NO-ANALYTICS`, `ANALYTICS-NO-LEDGER`,
  `SENT-NOT-PUBLISHED`.
- **Early no-op gate** (`tools/weekly_noop_gate.py`): if zero new published video
  IDs exist since the last successful run's cutoff, stop before calling any
  connector, model, or sending email — write the no-op state and exit. Fails open
  (missing/corrupt state → run full) — never fails into a wrong no-op.
- **Known unresolved gap:** the publication ledger has been **empty since the
  2026-07-21 baseline**. As of that baseline, 58 analytics rows were
  `ANALYTICS-NO-LEDGER` and 10 sent packages were `SENT-NOT-PUBLISHED` — sent
  content could not be attributed to published videos. **Never invent
  attribution.**
- **Repair status (updated 2026-07-23): DEPLOYED, NOT YET USED.** The fail-closed
  writer `tools/record_publication.py` (+ 21 unit tests) was approved, built, and
  merged to `main` via PR #5. It requires an explicit `--package-id`,
  `--youtube-video-id`, and a `--verified-metadata-file` proving (via a real,
  live YouTube Data API response) that the exact video id exists and is public —
  it never infers or title-matches. It remains a manual, human-invoked step, kept
  deliberately separate from daily content generation; it is not wired into
  either cron runtime and no automatic polling exists. The ledger itself is still
  0 rows — the gap persists in data terms until the first real publication is
  recorded, but the tool needed to close it safely now exists and is tested.

## 9. Credit-safe mode (Law #147, PR #3) — waste prevention, never quality/frequency cuts

- One shared 8-search sweep per daily run; traction cache
  (`cron_traction_cache.json`) refreshed only if missing or >3 days old.
- One-pass semantic QA in the same model context — no second launch, no extra
  sweep.
- Mechanical work (rendering, logging, validation) done by deterministic scripts
  (`validators/`, `tools/`), not extra model contexts.
- Full audits: monthly or incident-driven only, not every run.
- Non-email dry runs: only after a code/runtime change or a validation failure
  that needs reproduction — never "to be safe" on unchanged pipelines.
- **No new scheduled task is added and no existing cadence is increased** by
  credit-safe mode. Schedules for `daily_combined` and `2bb28991` are unchanged.

## 10. Permanent "no dry runs" preference (user-stated, applies to every future task)

- No dry runs, no sample packages, no test generations, no unnecessary repeated
  audits, no duplicate research sweeps, no resending merely to test the system.
- **Allowed exceptions:** mandatory deterministic validation before real sends
  (the fail-closed validators), and mandatory unit tests for actual repository
  code changes.

## 11. Email rules

- All production emails go **only** to `hero_or_villain@outlook.com` — never any
  other address.
- Two separate plain-text emails per day: `TOMORROW | MORNING | ...` and
  `TOMORROW | EVENING | ...` subjects.
- Keep emails slim — compliance/audit/search-log detail goes in the run manifest,
  not the email body.
- **Never send a full "replacement" email for a correction** — corrections must be
  short, change-only updates (credit-waste lesson from an earlier incident).
- Never mark an email as sent unless genuinely confirmed sent. Never mark a batch
  successful before both emails and both log events complete (atomic).

## 12. Production state (as of 2026-07-23, before this recovery task takes any action)

- **Last known successful daily batch:** `9856951f-ea56-4740-8c73-f3eaa5a90728`,
  run 2026-07-21T19:06 ET, **post_date 2026-07-22**.
  - Morning `40fd3ec9-3e53-409e-9e48-06353ba9b239` — "A Livid Lady's Guide to
    Getting Even" (CHARACTER_DIVE).
  - Evening `f04d762f-d4cf-4b56-8b1b-ef5d8b35bc23` — "Draw This, Then Die!"
    (FACT_DROP).
  - `cron_tracking/daily_combined/state.json` confirms `emails_sent`,
    `log_appended`, `git_pushed` all `true`.
- **2026-07-22 scheduled run:** fired (scheduler `run_count` incremented), but
  **produced zero packages** — the Computer session's sandbox stopped responding.
  No manifest, no send events, no reservation, no partial state exists for that
  date anywhere in the repo. Confirmed clean failure, not a stuck/dangling
  reservation. Diagnostic session: `30e0c963-bdcb-4eda-a1fe-5036617e54a1`.
- **2026-07-23:** not yet produced as of this writing. The next scheduled daily
  run (6:30 PM ET today) would generate **2026-07-24** content, which would leave
  2026-07-23 as a skipped day unless separately backfilled — this decision is the
  user's call, not automatic.
- **Publication ledger:** still 0 rows (see §8). Repair tool deployed via PR #5
  (merge commit `8a4798c9e45b54ed7a187de79e9133311c82aad5`); awaiting the first
  verified real upload before it records its first row.

## 13. GitHub history (PRs)

- **PR #1** — fail-closed logging gate; evidence-based topic/packaging/
  measurement laws (#143–145) + long-form separation (#146).
- **PR #2** — persisted weekly attribution; Fable red-team corrections M1–M6
  (duration experiment, series branding, hook-family sequential evaluation,
  quality-over-quota, self-attestation reclassification).
- **PR #3** — Credit-Safe Mode: one-pass semantic QA, colon-loop enforcement,
  claim-to-source matrices, weekly no-op gate, Law #147.
  (https://github.com/SEBLABHRIS/AnimeWithSebastian/pull/3)
- **PR #4** — punchier Shorts titles: YouTube 60/TikTok 55 char hard maxes,
  distinct `tiktok_title` field.
  (https://github.com/SEBLABHRIS/AnimeWithSebastian/pull/4)
- **PR #5** — publication-ledger repair tool (`tools/record_publication.py`,
  fail-closed, manual, 21 unit tests) + this handoff document. Merged
  2026-07-23, merge commit `8a4798c9e45b54ed7a187de79e9133311c82aad5`.
  (https://github.com/SEBLABHRIS/AnimeWithSebastian/pull/5)
- **(unmerged, 2026-07-24)** — `tools/mark_published.py`, a `--show`/`--post-date`
  convenience wrapper around `record_publication.py` (+ 18 unit tests). Lookup-only;
  does not modify or weaken any of `record_publication.py`'s fail-closed checks. See
  "Convenience wrapper added 2026-07-24" above for detail.

## 14. Reliability rules

- GitHub restore before each run is a **soft gate** — a git failure is logged and
  never blocks live research or package delivery; but a git failure must never be
  recorded as a success.
- Never mark a failed email, failed push, or incomplete batch as successful.
  Never fabricate execution that didn't happen.
- Atomic state: both packages' send events + state updates happen together or not
  at all.
- Major changes (strategy pivots, system redesigns, ledger repairs) require the
  user's explicit sign-off before execution — even after a capable audit
  recommending them.

## 15. Recovery checklist for any future task inheriting this project

1. Confirm the workspace can read files and execute commands.
2. Load the relevant prior Computer session(s) for conversation-level context
   (session `30e0c963-bdcb-4eda-a1fe-5036617e54a1` / equivalently the task URL
   above).
3. Clone/pull the latest GitHub `main` — treat it as authoritative over memory.
4. Report the current commit hash.
5. Confirm the authoritative files listed in §2 exist.
6. Inspect `sent_scripts_log.json`, `cron_tracking/sent_scripts_events.jsonl`, and
   `cron_tracking/daily_combined/` for the last successful batch and any
   incomplete/reserved batch.
7. List existing scheduled tasks (`schedule_cron` list, `cross_session=true`) and
   confirm no duplicates of the current daily/weekly IDs in §3 exist before
   creating or updating anything.
8. Check `cron_tracking/publication_ledger.jsonl` row count for the analytics gap.
9. Report everything recovered and any inconsistencies to the user.
10. **Wait for explicit user approval** before generating content, sending email,
    changing schedules, modifying GitHub, or running anything resembling a dry run.

---

*This document should be updated whenever a law, schedule, or major workflow
changes, so it stays a reliable single-file recovery point. It summarizes; it does
not override the actual law/runtime/validator files listed in §2 — when in doubt,
read those.*

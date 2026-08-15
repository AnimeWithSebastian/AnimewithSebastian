# Law #139 — Combined Daily Dual-Package Workflow (added July 15, 2026)

**Status:** ACTIVE. User-approved. Governs routine daily Shorts generation.

## What changed
The two separate daily scheduled runs (morning `d43ab889` + evening `57a3c92e`),
which fired ~1 hour apart and each independently reloaded large split runtimes, ran
a full 8-search stack, launched a model, drafted a long audit-heavy email, validated,
sent, and logged, are **replaced for future daily generation** by ONE combined run
governed by `cron_daily_runtime.txt` (cron id `daily_combined`).

This is a **credit-reduction** change. **Creative quality standards are unchanged.**
Every creative law that governed the morning/evening runs still governs BOTH packages.

## Mandatory architecture
1. **One daily run** researches and creates BOTH the next-day MORNING and EVENING
   Shorts packages.
2. **Claude Sonnet 5.0 is invoked ONCE per daily run** for idea selection, research
   synthesis, format selection, and drafting both VOs/packages. No Claude Fable 5 for
   routine daily generation (Law #137 unchanged).
3. **One shared current-market research sweep per run** (the 8-search stack, run
   once). The broad traction cache (`cron_traction_cache.json`) refreshes **at most
   once every 3 days** (Law #129). Both ideas still receive current
   candidate-specific fact verification and **at least two credible live sources
   each** (Law #78 dates required). Do not repeat identical broad searches.
4. **Two genuinely independent ideas**: different shows, different angles, different
   formats, independent sourcing, and no blackout / recent-send conflicts. Both
   selected in one context to maximize cross-slot diversity. Same-day same-show is
   banned even with different angles.
5. **Two separate plain-text emails** to `hero_or_villain@outlook.com` ONLY — one
   labeled MORNING, one labeled EVENING. They may be sent consecutively by the one run.
6. **All creative laws preserved** (nothing relaxed): fixed 30-second CapCut edit;
   100–108-word VO, target ~104, no filler/dead air; assumption-breaking hook;
   specific question immediately followed by the exact phrase "Leave your take.";
   **explicit seamless loop — the exact final VO sentence flows back into the exact
   first sentence, attested by `loop_read_aloud_pass` + `loop_transition_note`, with
   exactly the final cut carrying the loop-back (Law #141, which supersedes the earlier
   shared-anchor loop check)**; Shorts REQUIRE face-cam split screen — Creator TOP /
   anime footage BOTTOM (Law #134 Stage 2, 2026-08-09, superseding the July 14, 2026
   anime-only rule this point originally stated); **per-cut clip timings REQUIRED — every cut
   carries `duration_sec` + cumulative range, cuts tile the fixed 30s edit
   contiguously, and each package states `total_clip_time_sec` = 30 (Law #140,
   which supersedes the earlier no-timings preference)**; separate titles, TikTok
   post text, captions, clip descriptions, pinned comment, and platform-specific post
   times. Long-form (Law #66/#136) and Fable governance (Law #137) unchanged.
7. **Slimmer recipient emails**: emails carry only actionable production content and
   concise source evidence. Compliance matrices, format-window details, search logs,
   model-routing details, and audit boilerplate move to the run manifest / internal
   run log — the checks are **moved, not removed**.
8. **Deterministic preflight validation** (`validators/validate_dual_package.py`)
   runs before email and **fails closed**. It checks at minimum: both packages exist;
   distinct shows/formats; blackout/recent conflict inputs; VO word counts 100–108;
   CTA exact placement; **explicit seamless loop mechanics (exact first/last sentence,
   `loop_transition` = loop_line + " " + opening_sentence, `loop_read_aloud_pass`=true,
   nonempty note, exactly the final cut carries the loop-back — Law #141)**;
   face-cam split-screen required (Law #134 Stage 2, superseding the earlier
   anime-only/no-face check); **per-cut clip timings
   present and tiling the 30s edit contiguously with `total_clip_time_sec` = 30 (Law
   #140)**; required production sections; source count ≥2 per package; separate
   posting-time lines; recipient exactly correct. No model-based revision is needed
   for routine mechanical issues.
9. **Atomic dual-event logging** (`tools/append_send_batch.py`) appends two send
   events after BOTH emails are confirmed sent, in one merge-safe JSONL write, with a
   shared `batch_id` and distinct `package_id` values, plus legacy
   `sent_scripts_log.json` compatibility and atomic per-run state
   (`cron_tracking/daily_combined/state.json`) with accurate
   `emails_sent`/`log_appended`/`git_pushed` flags. **Never mark success before both
   emails and both log events complete.** The logger also **re-runs the deterministic
   validator on the manifest and fails closed** (appends nothing, writes
   `status="failed"`) if it does not pass — logging is bound to the same mechanical
   gate as the STEP 5 preflight, so a non-conformant manifest can never be recorded as
   a successful send in the logs/ledger the weekly analytics cron reads.
10. **Weekly analytics (cron `2bb28991`) is unchanged in cadence and behavior.** It
    understands the two daily events as **one batch (`batch_id`) but two packages
    (`package_id`)**, and still joins to the publication ledger on `youtube_video_id`
    only. Do not change its schedule.
11. **Concise runtime**: one authoritative combined runtime file
    (`cron_daily_runtime.txt`) + a compact package template
    (`templates/package_template.txt`) + the deterministic validator. Durable law
    prose is **referenced**, not re-pasted daily — enforcement preserved, daily token
    load reduced. The legacy split runtimes and rework files are not loaded for
    routine daily generation.

## Files
- `cron_daily_runtime.txt` — authoritative combined daily runtime (cron `daily_combined`).
- `templates/package_template.txt` — compact per-slot email/package shape.
- `validators/validate_dual_package.py` — deterministic fail-closed preflight validator.
- `validators/test_validate_dual_package.py` + `validators/fixtures/valid_dual_package.json` — tests.
- `tools/append_send_batch.py` — atomic dual-event logger.
- `cron_tracking/daily_combined/` — run manifest + state for this workflow.
- `scheduler/daily_dual_package_task.txt` — the scheduled-task prompt text.
- `docs/MIGRATION_dual_package.md` — migration + rollback.

## Rollback
Re-point the scheduler at the two legacy runtimes (`cron_morning_runtime.txt`,
`cron_evening_runtime.txt`), which are preserved intact (only a SUPERSEDED banner was
added). See `docs/MIGRATION_dual_package.md` for exact steps. No historical runtime,
log, ledger, or state file is deleted by this change.

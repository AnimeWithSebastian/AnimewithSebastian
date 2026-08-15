# cron_tracking/daily_combined/

Runtime state for the combined daily dual-package workflow (cron `daily_combined`,
Law #139). Populated at run time:

- `run_manifest.json` — both packages for the day, machine-readable. Input to the
  deterministic validator (`validators/validate_dual_package.py`) and to the atomic
  logger (`tools/append_send_batch.py`). Schema:
  `python3 validators/validate_dual_package.py --schema`.
- `state.json` — atomic per-run state: shared `batch_id`, both `package_id`s,
  `emails_sent` / `log_appended` / `git_pushed` flags, `status`, `error`.

Send events append to `../sent_scripts_events.jsonl` (append-only JSONL) and the
legacy `../../sent_scripts_log.json` array; the publication ledger
(`../publication_ledger.jsonl`) remains the sole source of truth for "published".

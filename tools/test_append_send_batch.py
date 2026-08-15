#!/usr/bin/env python3
"""Regression tests for the idempotent dual-event logger (append_send_batch).

A production retry once appended the same two package IDs twice. These tests pin
the fix: rerunning the same manifest must never duplicate sent_scripts_events.jsonl
or sent_scripts_log.json, but must still refresh state flags such as git_pushed.
Uses stdlib unittest only, against a throwaway tree — no repo state is touched.

    python3 tools/test_append_send_batch.py
    python3 -m unittest discover  (from inside the tools/ directory)
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr

import append_send_batch as a

FIXTURE = os.path.join(os.path.dirname(__file__), "..", "validators",
                       "fixtures", "valid_dual_package.json")
CRON_ID = "daily_combined"


def load_manifest() -> dict:
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


class LoggerCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tree = self._tmp.name
        self.manifest = load_manifest()
        self.pkg_ids = [p["package_id"] for p in self.manifest["packages"]]
        self.events_path = os.path.join(self.tree, "cron_tracking",
                                        "sent_scripts_events.jsonl")
        self.legacy_path = os.path.join(self.tree, "sent_scripts_log.json")
        self.state_path = os.path.join(self.tree, "cron_tracking", CRON_ID,
                                       "state.json")

    def tearDown(self):
        self._tmp.cleanup()

    # helpers ----------------------------------------------------------------
    def event_keys(self):
        keys = []
        with open(self.events_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    keys.append((r["batch_id"], r["package_id"]))
        return keys

    def legacy_keys(self):
        with open(self.legacy_path, encoding="utf-8") as fh:
            legacy = json.load(fh)
        return [(r["batch_id"], r["package_id"]) for r in legacy]

    def state(self):
        with open(self.state_path, encoding="utf-8") as fh:
            return json.load(fh)

    def write_approval_file(self, *, fetch_review: list | None = None) -> str:
        """Writes an approval.json to the temp tree and returns its path. By
        default writes a minimally-valid approval (Law #164/#165): a
        non-empty fetch_review list where every entry has
        fetched_content_supports_claim == True. Callers testing the gate
        itself (TestApprovalFileGateLaw164165) override fetch_review to
        build the adversarial shapes (missing list, empty list, an
        unsupported entry)."""
        if fetch_review is None:
            fetch_review = [{"claim": "test claim", "url": "https://example.com/source",
                             "fetched_content_supports_claim": True}]
        path = os.path.join(self.tree, "approval_under_test.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"fetch_review": fetch_review}, fh)
        return path

    def run_cli(self, *flags, approval_file: str | None = "__default__"):
        """approval_file="__default__" (the normal case for every test in this
        file predating the --approval-file gate) auto-writes and injects a
        valid approval so those tests keep exercising idempotency/logging
        behavior unaffected by the later gate. Pass approval_file=None to
        omit the flag entirely (to test the gate's missing-flag path), or
        an explicit path string to test a specific approval file."""
        argv = ["append_send_batch.py", FIXTURE, "--tree", self.tree, *flags]
        if approval_file == "__default__":
            argv += ["--approval-file", self.write_approval_file()]
        elif approval_file is not None:
            argv += ["--approval-file", approval_file]
        return a.main(argv)

    def run_cli_manifest(self, manifest: dict, *flags, approval_file: str | None = "__default__"):
        """Write `manifest` to a temp file inside the tree and run the CLI on it.
        See run_cli() for approval_file semantics."""
        path = os.path.join(self.tree, "run_manifest_under_test.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh)
        argv = ["append_send_batch.py", path, "--tree", self.tree, *flags]
        if approval_file == "__default__":
            argv += ["--approval-file", self.write_approval_file()]
        elif approval_file is not None:
            argv += ["--approval-file", approval_file]
        return a.main(argv)


class TestIdempotentAppend(LoggerCase):
    def test_initial_append_writes_one_per_package(self):
        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)
        self.assertCountEqual(self.event_keys(),
                              [(self.manifest["batch_id"], pid) for pid in self.pkg_ids])
        self.assertCountEqual(self.legacy_keys(),
                              [(self.manifest["batch_id"], pid) for pid in self.pkg_ids])
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["emails_sent"] and st["log_appended"])
        self.assertFalse(st["git_pushed"])

    def test_identical_retry_does_not_duplicate(self):
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        # exact same invocation again
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        # still exactly one record per package in BOTH logs
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(len(self.legacy_keys()), 2)
        for pid in self.pkg_ids:
            key = (self.manifest["batch_id"], pid)
            self.assertEqual(self.event_keys().count(key), 1)
            self.assertEqual(self.legacy_keys().count(key), 1)

    def test_retry_with_git_pushed_updates_state_only(self):
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        self.assertFalse(self.state()["git_pushed"])
        # the exact failing scenario: retry after push with --git-pushed
        self.assertEqual(self.run_cli("--emails-sent", "--git-pushed"), 0)
        # logs unchanged, git_pushed now recorded
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(len(self.legacy_keys()), 2)
        st = self.state()
        self.assertTrue(st["git_pushed"])
        self.assertEqual(st["status"], "success")

    def test_partial_existing_package_ids_appends_only_missing(self):
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        # simulate a torn write: drop the second package from BOTH logs
        first_key = (self.manifest["batch_id"], self.pkg_ids[0])
        # rewrite JSONL keeping only the first event
        with open(self.events_path, encoding="utf-8") as fh:
            lines = [ln for ln in fh if ln.strip()]
        keep = [ln for ln in lines if json.loads(ln)["package_id"] == self.pkg_ids[0]]
        with open(self.events_path, "w", encoding="utf-8") as fh:
            fh.writelines(keep)
        # rewrite legacy keeping only the first entry
        with open(self.legacy_path, encoding="utf-8") as fh:
            legacy = [r for r in json.load(fh) if r["package_id"] == self.pkg_ids[0]]
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            json.dump(legacy, fh)
        self.assertEqual(len(self.event_keys()), 1)
        self.assertEqual(len(self.legacy_keys()), 1)
        # rerun: only the missing package should be appended
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(len(self.legacy_keys()), 2)
        self.assertEqual(self.event_keys().count(first_key), 1)

    def test_fail_closed_without_emails_sent_appends_nothing(self):
        rc = self.run_cli()  # no --emails-sent
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        self.assertFalse(os.path.exists(self.legacy_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["emails_sent"] or st["log_appended"])

    def test_exactly_one_record_per_package_after_many_retries(self):
        for _ in range(5):
            self.run_cli("--emails-sent", "--git-pushed")
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(len(self.legacy_keys()), 2)
        self.assertCountEqual(
            {k for k in self.event_keys()},
            {(self.manifest["batch_id"], pid) for pid in self.pkg_ids})


class TestMalformedEventsLineWarnsAndContinues(LoggerCase):
    """F11 fix (production-audit finding, 2026-07-25): a malformed JSONL line in
    sent_scripts_events.jsonl must not silently vanish from duplicate-detection --
    it should warn on stderr and the append must still proceed normally (WARN and
    continue, not fail closed -- blocking the whole run over one unrelated
    historical line would be disproportionate)."""

    def _write_malformed_events_file(self):
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)
        with open(self.events_path, "w", encoding="utf-8") as fh:
            fh.write("{not valid json\n")

    def _parsable_event_keys(self):
        """Like LoggerCase.event_keys(), but tolerates a leading malformed line --
        this test's file starts out deliberately corrupted."""
        keys = []
        with open(self.events_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                keys.append((r["batch_id"], r["package_id"]))
        return keys

    def test_malformed_line_warns_on_stderr(self):
        self._write_malformed_events_file()
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)
        self.assertIn("[WARN]", stderr.getvalue())
        self.assertIn(self.events_path, stderr.getvalue())
        self.assertIn("excluded from duplicate-detection", stderr.getvalue())

    def test_append_still_succeeds_despite_malformed_line(self):
        self._write_malformed_events_file()
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)
        # the malformed line stays untouched (never counted as an existing key),
        # so both real packages get appended as NEW rows right after it
        self.assertCountEqual(self._parsable_event_keys(),
                              [(self.manifest["batch_id"], pid) for pid in self.pkg_ids])
        st = self.state()
        self.assertEqual(st["status"], "success")


class TestLoadLegacyCorruptionRaises(LoggerCase):
    """Regression tests: _load_legacy() must distinguish a MISSING legacy log (normal,
    first-ever run) from a legacy log that EXISTS but fails to parse (dangerous --
    previously both were silently treated as an empty list, which risked the next
    append effectively wiping the log's prior history). Corruption now RAISES
    LegacyLogCorruptedError instead of warning and returning [] (F1 fix)."""

    def test_missing_file_is_silent(self):
        # File genuinely does not exist yet -- this is expected and must NOT warn.
        self.assertFalse(os.path.exists(self.legacy_path))
        buf = io.StringIO()
        with redirect_stderr(buf):
            legacy = a._load_legacy(self.legacy_path)
        self.assertEqual(legacy, [])
        self.assertNotIn("WARN", buf.getvalue())

    def test_corrupted_json_raises_distinctly(self):
        # File EXISTS but is not valid JSON -- must raise, not silently return an
        # empty list as if the file were merely absent (which would let the caller
        # rewrite it with only the current run's rows).
        os.makedirs(os.path.dirname(self.legacy_path), exist_ok=True)
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            fh.write("{not valid json,,,")
        with self.assertRaisesRegex(a.LegacyLogCorruptedError, "CORRUPTED"):
            a._load_legacy(self.legacy_path)

    def test_non_list_json_raises_distinctly(self):
        # File parses as valid JSON but the top-level shape is wrong (not a list) --
        # also must raise, not silently coerce to an empty list unremarked.
        os.makedirs(os.path.dirname(self.legacy_path), exist_ok=True)
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            json.dump({"unexpected": "shape"}, fh)
        with self.assertRaisesRegex(a.LegacyLogCorruptedError, "not a list"):
            a._load_legacy(self.legacy_path)

    def test_well_formed_list_loads_without_warning(self):
        os.makedirs(os.path.dirname(self.legacy_path), exist_ok=True)
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            json.dump([{"package_id": "abc"}], fh)
        buf = io.StringIO()
        with redirect_stderr(buf):
            legacy = a._load_legacy(self.legacy_path)
        self.assertEqual(legacy, [{"package_id": "abc"}])
        self.assertNotIn("WARN", buf.getvalue())


class TestLegacyLogCorruptionFailsClosed(LoggerCase):
    """F1 fix: a corrupted legacy log must not be silently treated as empty and
    overwritten -- append_batch must fail closed instead of wiping history."""

    def test_corrupted_legacy_log_raises_and_is_not_overwritten(self):
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            fh.write("{ this is not valid json at all")
        with open(self.legacy_path, encoding="utf-8") as fh:
            original_content = fh.read()

        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 1)

        with open(self.legacy_path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), original_content)  # untouched, not wiped

        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("corrupt", st["error"].lower())

    def test_non_list_legacy_log_raises_and_is_not_overwritten(self):
        with open(self.legacy_path, "w", encoding="utf-8") as fh:
            json.dump({"not": "a list"}, fh)
        with open(self.legacy_path, encoding="utf-8") as fh:
            original_content = fh.read()

        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 1)
        with open(self.legacy_path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), original_content)
        self.assertFalse(self.state()["log_appended"])

    def test_missing_legacy_log_is_still_fine_and_creates_it(self):
        # sanity: a genuinely missing file must remain unaffected by this fix.
        self.assertFalse(os.path.exists(self.legacy_path))
        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(self.legacy_path))


class TestAttributionFieldsPersisted(LoggerCase):
    """Laws #143-#145 delegate the weekly topic-mix / recurring-series / hook-family /
    funnel-status / single-variant-integrity targets to the weekly analytics cron. That
    cron can only compute them if the per-package attribution is persisted in the send
    log (the publication ledger carries no such fields and the daily manifest is
    overwritten every day). These tests pin that the logger writes the attribution to
    BOTH the JSONL event ledger and the legacy array so the weekly targets cannot be
    silently skipped."""

    ATTR_KEYS = ("topic_class", "topic_signals", "series", "hook_family",
                 "hook_line", "funnel_status",
                 # Item 3 addition (2026-07-25): full VO/loop/CTA archival, so a
                 # future audit of a specific sent package's spoken content doesn't
                 # depend on the daily run_manifest.json, which is overwritten daily.
                 "question_line", "cta_line", "loop_line", "vo")

    def rows_jsonl(self):
        rows = []
        with open(self.events_path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    def rows_legacy(self):
        with open(self.legacy_path, encoding="utf-8") as fh:
            return json.load(fh)

    def _expected_by_pid(self):
        return {p["package_id"]: p for p in self.manifest["packages"]}

    def test_event_rows_carry_attribution_matching_manifest(self):
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        expected = self._expected_by_pid()
        for row in self.rows_jsonl():
            pkg = expected[row["package_id"]]
            for key in self.ATTR_KEYS:
                self.assertIn(key, row, f"event row missing {key}")
                self.assertEqual(row[key], pkg.get(key),
                                 f"event {key} mismatch for {row['package_id']}")

    def test_legacy_rows_carry_attribution_matching_manifest(self):
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        expected = self._expected_by_pid()
        for row in self.rows_legacy():
            pkg = expected[row["package_id"]]
            for key in self.ATTR_KEYS:
                self.assertIn(key, row, f"legacy row missing {key}")
                self.assertEqual(row[key], pkg.get(key),
                                 f"legacy {key} mismatch for {row['package_id']}")

    def test_topic_mix_countable_from_event_log(self):
        # the weekly TOPIC MIX target (>=9/14 timely) must be computable from the log
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        timely = sum(1 for r in self.rows_jsonl() if r.get("topic_class") == "timely")
        self.assertEqual(timely, sum(1 for p in self.manifest["packages"]
                                     if p.get("topic_class") == "timely"))

    def test_recurring_series_countable_from_event_log(self):
        # the weekly RECURRING SERIES target (>=2/week) must be computable from the log
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        recurring = sum(1 for r in self.rows_jsonl()
                        if isinstance(r.get("series"), dict) and r["series"].get("recurring"))
        self.assertEqual(recurring, sum(
            1 for p in self.manifest["packages"]
            if isinstance(p.get("series"), dict) and p["series"].get("recurring")))


class TestManifestRevalidationGate(LoggerCase):
    """The logger must fail closed on a manifest that does not pass the deterministic
    validator, even when --emails-sent is asserted. This is the safeguard against the
    observed incident: a non-conformant manifest recorded as status="success" and
    appended to the sent log / ledger consumed by the weekly analytics cron."""

    def test_valid_manifest_still_passes_the_gate(self):
        # sanity: the untouched fixture passes the gate and logs normally
        self.assertEqual(self.run_cli_manifest(self.manifest, "--emails-sent"), 0)
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(self.state()["status"], "success")

    def test_invalid_manifest_missing_clip_timings_fails_closed(self):
        bad = load_manifest()
        # Law #140 violation: strip per-cut timing fields from a clip
        for c in bad["packages"][0]["clips"]:
            c.pop("duration_sec", None)
            c.pop("timeline_start_sec", None)
            c.pop("timeline_end_sec", None)
        rc = self.run_cli_manifest(bad, "--emails-sent")
        self.assertEqual(rc, 1)
        # nothing appended to either log
        self.assertFalse(os.path.exists(self.events_path))
        self.assertFalse(os.path.exists(self.legacy_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("preflight validation", st["error"])

    def test_invalid_manifest_wrong_opening_sentence_fails_closed(self):
        # REPOINTED 2026-08-14. This test previously asserted a Law #141 violation
        # (loop_read_aloud_pass = False). Law #141's forced-loop mandate was rescinded
        # 2026-07-27 and loop_read_aloud_pass is now an inert, unchecked field, so the
        # old assertion tested nothing -- it failed because the manifest correctly
        # PASSED. The rescission's files-touched list removed the corresponding loop
        # tests from validators/test_validate_dual_package.py but missed this file.
        #
        # Repointed rather than deleted so the revalidation-gate coverage is preserved:
        # opening_sentence is the one check from the old loop block that SURVIVED the
        # rescission (it is retained under Law #144/#145 because published hook_line
        # must equal opening_sentence), so it is the closest still-enforced analogue.
        bad = load_manifest()
        bad["packages"][1]["opening_sentence"] = "This is not the VO's first sentence."
        rc = self.run_cli_manifest(bad, "--emails-sent", "--git-pushed")
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        self.assertEqual(self.state()["status"], "failed")

    def test_invalid_manifest_wrong_recipient_fails_closed(self):
        bad = load_manifest()
        # Audit item #21 (2026-08-14): was a real personal address committed to the repo.
        # Any non-hero_or_villain@outlook.com value exercises this check identically.
        bad["recipient"] = "wrong@example.com"
        rc = self.run_cli_manifest(bad, "--emails-sent")
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.legacy_path))
        self.assertEqual(self.state()["status"], "failed")

    def test_gate_does_not_run_before_emails_sent_check(self):
        # without --emails-sent we still fail closed (emails-not-sent takes precedence)
        bad = load_manifest()
        bad["packages"][0]["cta_line"] = "What do you think?"
        rc = self.run_cli_manifest(bad)  # no --emails-sent
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertIn("not confirmed sent", st["error"])


class TestSinglePackageManifest(LoggerCase):
    """append_batch() must accept a genuine 1-package manifest ONLY when it carries
    a non-empty single_package_reason -- mirroring the same M5 quality-over-quota
    exception validate_dual_package.py already grants. A bare 1-package manifest
    with no (or empty) reason must keep failing exactly as before, since an
    unexplained missing package could mean a real pipeline failure rather than a
    deliberate decision."""

    def _single_package_manifest(self, reason="Quality over quota (M5): the only "
                                  "remaining evening candidate was Law #85 hard-"
                                  "blocked; no other candidate cleared blackout "
                                  "screening."):
        m = load_manifest()
        m["packages"] = [m["packages"][0]]
        m["packages"][0]["slot"] = "morning"
        if reason is not None:
            m["single_package_reason"] = reason
        return m

    def test_valid_single_package_manifest_logs_one_event_not_two(self):
        m = self._single_package_manifest()
        rc = self.run_cli_manifest(m, "--emails-sent")
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.event_keys()), 1)
        self.assertEqual(len(self.legacy_keys()), 1)
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["log_appended"])
        self.assertEqual(len(st["packages"]), 1)

    def test_single_package_missing_reason_still_fails_closed(self):
        m = self._single_package_manifest(reason=None)
        rc = self.run_cli_manifest(m, "--emails-sent")
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        self.assertFalse(os.path.exists(self.legacy_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])

    def test_single_package_empty_string_reason_still_fails_closed(self):
        m = self._single_package_manifest(reason="   ")
        rc = self.run_cli_manifest(m, "--emails-sent")
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")

    def test_normal_two_package_manifest_unaffected(self):
        # sanity: the happy path (untouched dual fixture) must be completely
        # unaffected by this fix.
        rc = self.run_cli_manifest(self.manifest, "--emails-sent")
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.event_keys()), 2)
        self.assertEqual(self.state()["status"], "success")


class TestMalformedManifestFailsClosed(LoggerCase):
    """F10 fix: a missing or malformed manifest.json must not crash with a bare
    traceback -- it must write a real failure state, same as every other
    failure path in this file."""

    def test_missing_manifest_file_writes_failure_state_and_returns_1(self):
        bogus_path = os.path.join(self.tree, "does_not_exist.json")
        argv = ["append_send_batch.py", bogus_path, "--tree", self.tree, "--emails-sent"]
        rc = a.main(argv)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("could not load manifest", st["error"])

    def test_malformed_json_manifest_writes_failure_state_and_returns_1(self):
        bad_path = os.path.join(self.tree, "bad_manifest.json")
        with open(bad_path, "w", encoding="utf-8") as fh:
            fh.write("{ not valid json ,,,")
        argv = ["append_send_batch.py", bad_path, "--tree", self.tree, "--emails-sent"]
        rc = a.main(argv)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertIn("could not load manifest", st["error"])

    def test_well_formed_manifest_still_works_unchanged(self):
        # sanity: the happy path must be completely unaffected by this fix.
        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)


class TestApprovalFileGateLaw164165(LoggerCase):
    """Law #164/#165 (added 2026-08-13): a send may only be logged as
    successful if a real, fetch-based approval.json is supplied via
    --approval-file. This is permanent regression coverage for the gate that
    was previously verified only via ad-hoc manual runs in /tmp/gate_test/
    earlier this session (since cleaned up) -- these tests pin the same
    behavior durably.

    HONEST LIMITATION (documented in append_send_batch.py's own --approval-file
    help text and restated here so the test suite doesn't imply more than the
    gate actually does): this protects the LOG's integrity, not the send
    action itself. By the time this script runs, STEP 7 has already sent the
    emails. The gate can refuse to record a send as successful after the
    fact; it cannot retroactively unsend an email that went out without a
    real approval.json. Every test below asserts log_appended is False and
    status is "failed" on a blocked run -- never that the email itself was
    prevented, since this script has no ability to affect that."""

    # 1. --approval-file not provided at all -- blocks.
    def test_missing_approval_file_flag_blocks(self):
        rc = self.run_cli("--emails-sent", approval_file=None)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))  # nothing ever logged
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("--approval-file not provided", st["error"])

    # 2. --approval-file points at a path that does not exist -- blocks.
    def test_nonexistent_approval_file_path_blocks(self):
        bogus = os.path.join(self.tree, "does_not_exist_approval.json")
        rc = self.run_cli("--emails-sent", approval_file=bogus)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("could not load --approval-file", st["error"])

    # 3. --approval-file points at a file that exists but is not valid JSON -- blocks.
    def test_unparseable_approval_file_blocks(self):
        bad_path = os.path.join(self.tree, "bad_approval.json")
        with open(bad_path, "w", encoding="utf-8") as fh:
            fh.write("{ not valid json ,,,")
        rc = self.run_cli("--emails-sent", approval_file=bad_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("could not load --approval-file", st["error"])

    # 4. approval.json parses but has no fetch_review key at all -- blocks.
    def test_approval_file_missing_fetch_review_key_blocks(self):
        path = os.path.join(self.tree, "approval_no_key.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"note": "reviewed but forgot to record fetch_review"}, fh)
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("no non-empty fetch_review list", st["error"])

    # 5. approval.json has fetch_review present but as an empty list -- blocks.
    #    An approval with zero fetch records is not a completed review.
    def test_approval_file_empty_fetch_review_list_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("no non-empty fetch_review list", st["error"])

    # 6. fetch_review present and non-empty, but at least one entry has
    #    fetched_content_supports_claim explicitly False -- blocks. Guards
    #    against a reviewer fetching a source and honestly recording that it
    #    does NOT support the claim, yet the send still getting logged.
    def test_approval_file_one_entry_explicitly_unsupported_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "claim A", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
            {"claim": "claim B", "url": "https://example.com/b",
             "fetched_content_supports_claim": False},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        # detail-message content (which claim gets named) is pinned separately
        # in test_approval_file_unsupported_entry_error_names_the_claim below

    # 6b. same as above, but pins that the failure message names the
    #     unsupported claim(s), not just a generic rejection.
    def test_approval_file_unsupported_entry_error_names_the_claim(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "the sealed door was always meant to hold something else",
             "url": "https://example.com/b", "fetched_content_supports_claim": False},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertIn("the sealed door was always meant to hold something else", st["error"])

    # 7. fetch_review entry missing the fetched_content_supports_claim key
    #    entirely (not even False) -- must be treated the same as an explicit
    #    False, not silently accepted as "unspecified == fine".
    def test_approval_file_entry_missing_supports_claim_key_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "claim A", "url": "https://example.com/a"},  # key omitted
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])

    # 8. fetch_review entry that isn't a dict at all (e.g. a bare string) --
    #    must fail closed rather than crash with an AttributeError.
    def test_approval_file_non_dict_entry_blocks_without_crashing(self):
        approval_path = self.write_approval_file(fetch_review=["not a dict"])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")

    # 9. fully valid approval.json -- succeeds and logs exactly like the
    #    pre-gate behavior (this is the happy path all pre-existing tests in
    #    this file already rely on via LoggerCase.run_cli()'s default).
    def test_fully_valid_approval_file_succeeds_and_logs(self):
        rc = self.run_cli("--emails-sent")  # default approval_file="__default__"
        self.assertEqual(rc, 0)
        self.assertCountEqual(self.event_keys(),
                              [(self.manifest["batch_id"], pid) for pid in self.pkg_ids])
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["log_appended"])

    # 10. a valid approval.json with MULTIPLE supported entries (not just
    #     one) also succeeds -- confirms the check is "every entry True",
    #     not just "at least one entry True".
    def test_valid_approval_file_with_multiple_supported_entries_succeeds(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "claim A", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
            {"claim": "claim B", "url": "https://example.com/b",
             "fetched_content_supports_claim": True},
            {"claim": "claim C", "url": "https://example.com/c",
             "fetched_content_supports_claim": True},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 0)
        st = self.state()
        self.assertEqual(st["status"], "success")

    # 11. --emails-sent missing AND --approval-file missing at the same time
    #     -- must block on the emails-sent check (checked first in main()),
    #     not silently pass through to the approval check or vice versa.
    def test_both_gates_missing_blocks_on_emails_sent_first(self):
        rc = self.run_cli(approval_file=None)  # no --emails-sent, no --approval-file
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertIn("emails not confirmed sent", st["error"])


class TestCorrectionBatchAttribution(LoggerCase):
    """corrects_batch_id / correction_reason (added 2026-08-13): a correction
    send that amends an already-sent batch's content needs a durable, typed
    pointer back to the original batch_id it corrects, plus a per-package
    reason, persisted into BOTH the JSONL ledger and the legacy log -- not
    just left in the transient run_manifest.json build artifact. This is
    optional, additive metadata: a normal (non-correction) manifest that
    never sets these fields must log corrects_batch_id/correction_reason as
    null without any other behavior change."""

    def test_normal_manifest_logs_null_correction_fields(self):
        # The stock fixture never sets corrects_batch_id/correction_reason.
        rc = self.run_cli("--emails-sent")
        self.assertEqual(rc, 0)
        with open(self.events_path, encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
        for row in rows:
            self.assertIsNone(row["corrects_batch_id"])
            self.assertIsNone(row["correction_reason"])
        with open(self.legacy_path, encoding="utf-8") as fh:
            legacy_rows = json.load(fh)
        for row in legacy_rows:
            self.assertIsNone(row["corrects_batch_id"])
            self.assertIsNone(row["correction_reason"])

    def test_correction_manifest_logs_corrects_batch_id_and_per_package_reason(self):
        manifest = load_manifest()
        manifest["corrects_batch_id"] = "b03ef8b6-d254-442a-aaf9-673a6578a0c5"
        manifest["packages"][0]["correction_reason"] = \
            "source citation did not support claim; claim re-sourced"
        manifest["packages"][1]["correction_reason"] = \
            "clip timestamp pointed to wrong scene; corrected"

        rc = self.run_cli_manifest(manifest, "--emails-sent")
        self.assertEqual(rc, 0)

        with open(self.events_path, encoding="utf-8") as fh:
            rows = {r["package_id"]: r for r in (json.loads(line) for line in fh if line.strip())}
        p0, p1 = manifest["packages"][0], manifest["packages"][1]
        self.assertEqual(rows[p0["package_id"]]["corrects_batch_id"],
                          "b03ef8b6-d254-442a-aaf9-673a6578a0c5")
        self.assertEqual(rows[p0["package_id"]]["correction_reason"],
                          "source citation did not support claim; claim re-sourced")
        self.assertEqual(rows[p1["package_id"]]["corrects_batch_id"],
                          "b03ef8b6-d254-442a-aaf9-673a6578a0c5")
        self.assertEqual(rows[p1["package_id"]]["correction_reason"],
                          "clip timestamp pointed to wrong scene; corrected")

        with open(self.legacy_path, encoding="utf-8") as fh:
            legacy_rows = {r["package_id"]: r for r in json.load(fh)}
        self.assertEqual(legacy_rows[p0["package_id"]]["corrects_batch_id"],
                          "b03ef8b6-d254-442a-aaf9-673a6578a0c5")
        self.assertEqual(legacy_rows[p0["package_id"]]["correction_reason"],
                          "source citation did not support claim; claim re-sourced")
        self.assertEqual(legacy_rows[p1["package_id"]]["correction_reason"],
                          "clip timestamp pointed to wrong scene; corrected")

    def test_correction_reason_is_per_package_not_shared(self):
        """A correction batch may fix the two packages for different reasons
        (as tonight's real Link Click / Slime correction does) -- the field
        must live on each package, not leak the other package's reason."""
        manifest = load_manifest()
        manifest["corrects_batch_id"] = "b03ef8b6-d254-442a-aaf9-673a6578a0c5"
        manifest["packages"][0]["correction_reason"] = "reason A"
        manifest["packages"][1]["correction_reason"] = "reason B"
        rc = self.run_cli_manifest(manifest, "--emails-sent")
        self.assertEqual(rc, 0)
        with open(self.events_path, encoding="utf-8") as fh:
            rows = {r["package_id"]: r for r in (json.loads(line) for line in fh if line.strip())}
        p0, p1 = manifest["packages"][0], manifest["packages"][1]
        self.assertEqual(rows[p0["package_id"]]["correction_reason"], "reason A")
        self.assertEqual(rows[p1["package_id"]]["correction_reason"], "reason B")
        self.assertNotEqual(rows[p0["package_id"]]["correction_reason"],
                             rows[p1["package_id"]]["correction_reason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestPendingStateMirrorF38(LoggerCase):
    """F38 fix (2026-08-15): after a genuinely successful send, the PER-BATCH
    pending/<batch_id>/state.json must flip to a terminal status.

    Before this, STEP 7/8/9 only wrote the TOP-LEVEL state.json, so a batch that
    had really sent still looked -- to Law #166's pending-batch scan, which reads
    exactly that per-batch file -- like an open unreviewed backlog item forever.
    That is F37's mechanical enabler: the next unattended run would skip generating
    a fresh batch with no distinct failure signal. It happened for real to batch
    32e0fcb9 (Link Click, post_date 2026-08-14).

    Fail-safe requirement: a FAILED send must NOT flip anything, so a genuinely
    incomplete batch keeps blocking exactly as intended.
    """

    def pending_dir(self):
        return os.path.join(self.tree, "cron_tracking", CRON_ID, "pending",
                            self.manifest["batch_id"])

    def pending_path(self):
        return os.path.join(self.pending_dir(), "state.json")

    def seed_pending(self, extra: dict | None = None):
        """Write a STEP 6-style per-batch state, as the approval flow would."""
        os.makedirs(self.pending_dir(), exist_ok=True)
        body = {
            "status": "AWAITING_" + "APPROVAL",   # split so this file never
                                                  # trips a naive substring scan
            "emails_sent": False,
            "batch_id": self.manifest["batch_id"],
            "post_date": self.manifest.get("post_date"),
        }
        if extra:
            body.update(extra)
        with open(self.pending_path(), "w", encoding="utf-8") as fh:
            json.dump(body, fh)
        return body

    def pending(self):
        with open(self.pending_path(), encoding="utf-8") as fh:
            return json.load(fh)

    # --- the core fix ---

    def test_successful_send_flips_pending_to_terminal(self):
        self.seed_pending()
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        p = self.pending()
        self.assertEqual(p["status"], "sent")
        self.assertTrue(p["emails_sent"])
        self.assertIn("terminal_state_written_at", p)
        self.assertEqual(p["terminal_state_written_by"],
                         "tools/append_send_batch.py (F38)")

    def test_terminal_pending_no_longer_matches_a_naive_scan(self):
        # Law #166's check is prose that greps for the awaiting-approval status.
        self.seed_pending()
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        with open(self.pending_path(), encoding="utf-8") as fh:
            raw = fh.read()
        self.assertNotIn("AWAITING_" + "APPROVAL", raw,
                         "terminal pending state must not still contain the "
                         "awaiting-approval token, or Law #166 re-blocks on it")

    # --- fail-safe ---

    def test_failed_send_does_not_flip_pending(self):
        seeded = self.seed_pending()
        rc = self.run_cli()          # no --emails-sent -> fail closed
        self.assertEqual(rc, 1)
        self.assertEqual(self.pending(), seeded, "a failed send must leave the "
                         "pending state untouched so Law #166 keeps blocking")

    def test_validator_rejected_manifest_does_not_flip_pending(self):
        seeded = self.seed_pending()
        bad = load_manifest()
        bad["recipient"] = "wrong@example.com"
        rc = self.run_cli_manifest(bad, "--emails-sent")
        self.assertEqual(rc, 1)
        self.assertEqual(self.pending(), seeded)

    # --- preservation: partial batches ---

    def test_step6_fields_are_preserved_not_overwritten(self):
        # 32e0fcb9's real shape: one package sent, one deliberately held.
        held = [{"show": "That Time I Got Reincarnated as a Slime",
                 "disposition": "HELD_NOT_SENT", "tracked_as": "F36",
                 "still_open": True}]
        self.seed_pending({
            "corrects_batch_id": "b03ef8b6-d254-442a-aaf9-673a6578a0c5",
            "single_package_reason": "evening held under Law #165",
            "held_packages": held,
        })
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        p = self.pending()
        self.assertEqual(p["status"], "sent")
        self.assertEqual(p["corrects_batch_id"], "b03ef8b6-d254-442a-aaf9-673a6578a0c5")
        self.assertEqual(p["single_package_reason"], "evening held under Law #165")
        self.assertEqual(p["held_packages"], held,
                         "a held package must survive the batch reaching a terminal "
                         "status -- terminal != the hold was resolved")
        self.assertTrue(p["held_packages"][0]["still_open"])

    # --- no-op paths ---

    def test_no_pending_dir_is_a_clean_noop(self):
        # the overwhelmingly common case: batch never used the approval flow
        self.assertFalse(os.path.isdir(self.pending_dir()))
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        self.assertFalse(os.path.exists(self.pending_path()))
        self.assertEqual(self.state()["status"], "success")

    def test_corrupt_pending_file_still_yields_terminal_state(self):
        os.makedirs(self.pending_dir(), exist_ok=True)
        with open(self.pending_path(), "w", encoding="utf-8") as fh:
            fh.write("{ not valid json,,,")
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        self.assertEqual(self.pending()["status"], "sent")

    def test_mirror_returns_none_when_not_success(self):
        state = {"status": "failed", "run_ts": "x"}
        self.assertIsNone(
            a.mirror_pending_state(self.manifest, self.tree, CRON_ID, state))

    def test_top_level_state_still_written_normally(self):
        # the per-batch mirror must not disturb the authoritative top-level write
        self.seed_pending()
        self.assertEqual(self.run_cli("--emails-sent", "--git-pushed"), 0)
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["git_pushed"])
        self.assertEqual(self.pending()["git_pushed"], True)

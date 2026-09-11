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


class TestSchemaPreCheckLaw173(LoggerCase):
    """Law #173 (added 2026-09-10, directly addressing F78): an approval.json
    authored with a "verdict" string field (or a similar plausible substitute)
    instead of the required "fetched_content_supports_claim" boolean produced
    the SAME generic "unsupported/malformed" error a genuine content-verification
    failure produces -- costing real diagnostic time telling the two apart on a
    real batch. This class pins the new, distinct schema-mismatch error path,
    and separately confirms it never fires for shapes it shouldn't (a genuinely
    unsupported claim using the CORRECT field name, or a missing field with no
    plausible substitute at all -- both must still fall through to the
    pre-existing generic gate, unchanged)."""

    def _approval_path(self, fetch_review):
        path = os.path.join(self.tree, "approval_schema_test.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"fetch_review": fetch_review}, fh)
        return path

    def test_verdict_field_instead_of_real_field_blocks_with_schema_message(self):
        path = self._approval_path([
            {"claim": "Chiaki teases Kunishige's handwriting", "url": "https://example.com/a",
             "verdict": "confirmed"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])
        self.assertIn("schema mismatch (Law #173)", st["error"])
        self.assertIn("verdict", st["error"])
        self.assertIn("fetched_content_supports_claim", st["error"])
        self.assertNotIn("unsupported/malformed", st["error"])

    def test_other_substitute_field_names_also_detected(self):
        for field in ("supported", "confirmed", "status", "result"):
            with self.subTest(field=field):
                path = self._approval_path([
                    {"claim": "test claim", "url": "https://example.com/a", field: "yes"},
                ])
                rc = self.run_cli("--emails-sent", approval_file=path)
                self.assertEqual(rc, 1)
                st = self.state()
                self.assertIn("schema mismatch (Law #173)", st["error"])

    def test_missing_field_with_no_substitute_falls_through_to_generic_error(self):
        path = self._approval_path([
            {"claim": "test claim", "url": "https://example.com/a"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertNotIn("schema mismatch (Law #173)", st["error"])
        self.assertIn("unsupported/malformed", st["error"])

    def test_correct_field_true_passes_schema_check_and_logs_success(self):
        path = self._approval_path([
            {"claim": "test claim", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
        ])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 0)
        st = self.state()
        self.assertEqual(st["status"], "success")

    def test_correct_field_false_skips_schema_check_hits_existing_gate(self):
        path = self._approval_path([
            {"claim": "test claim", "url": "https://example.com/a",
             "fetched_content_supports_claim": False},
        ])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertNotIn("schema mismatch (Law #173)", st["error"])
        self.assertIn("unsupported/malformed", st["error"])

    def test_mix_of_correct_and_verdict_entries_still_flagged(self):
        path = self._approval_path([
            {"claim": "claim A", "url": "https://example.com/a",
             "fetched_content_supports_claim": True},
            {"claim": "claim B", "url": "https://example.com/b",
             "verdict": "confirmed as corrected"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertIn("schema mismatch (Law #173)", st["error"])
        self.assertIn("claim B", st["error"])

    def test_malformed_non_dict_entry_does_not_crash_schema_check(self):
        path = self._approval_path(["not a dict", 12345])
        rc = self.run_cli("--emails-sent", approval_file=path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertNotIn("schema mismatch (Law #173)", st["error"])


class TestCoreAwareApprovalGate(LoggerCase):
    """Core-aware gate fix (2026-08-19): the Law #164/#165 gate in
    TestApprovalFileGateLaw164165 above originally required EVERY
    fetch_review entry to have fetched_content_supports_claim == True,
    with no distinction between core and non-core claims. That blocked a
    real production batch (8ca83216) whose evening package had one
    honestly-disclosed, non-core citation gap (a real note explaining that
    the cited page didn't itself state a secondary date, though the fact
    was independently confirmed elsewhere in the same approval's own
    sources).

    This class pins the narrow fix: a fetch_review entry only needs
    fetched_content_supports_claim == True when it is a CORE claim.
    core/non-core detection precedence, in order:
      1. A structured "core" key present on the entry (True or False) is
         authoritative -- ignores the legacy text-prefix marker entirely
         when present.
      2. Else, a claim string starting with a case-insensitive
         "[NON-CORE" marker is treated as core=False (the legacy
         convention already used in every existing approval.json in this
         repo, since none of them use a structured field).
      3. Else: defaults to core=True (today's strict behavior, unchanged).

    A non-core entry with fetched_content_supports_claim == False only
    passes if it also carries a real, non-empty "note" -- non-core is not
    a free pass to skip disclosure.
    """

    # 1. A core:true entry with fetched_content_supports_claim: False --
    #    MUST still block. This is the actual protection the gate exists
    #    for; the fix must leave it completely untouched.
    def test_core_true_unsupported_entry_still_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "core claim that failed verification", "core": True,
             "url": "https://example.com/a", "fetched_content_supports_claim": False,
             "note": "even with a note, a core claim that fails verification must block"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])

    # 2. A core:false entry with fetched_content_supports_claim: False and a
    #    real, non-empty note -- must NOT block. The actual fix.
    def test_core_false_unsupported_entry_with_real_note_does_not_block(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "non-core claim with an honestly disclosed gap", "core": False,
             "url": "https://example.com/b", "fetched_content_supports_claim": False,
             "note": "the cited page does not itself state this secondary detail, "
                      "though the fact is independently confirmed by another source "
                      "already cited in this same approval"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 0)
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["log_appended"])

    # 3. A core:false entry with fetched_content_supports_claim: False and an
    #    EMPTY/missing note -- MUST still block. Non-core isn't a free pass
    #    to skip disclosure entirely.
    def test_core_false_unsupported_entry_without_note_still_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "non-core claim with no disclosure", "core": False,
             "url": "https://example.com/c", "fetched_content_supports_claim": False},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])

    # 3b. Same as above but with an explicit empty-string note (not just a
    #     missing key) -- still must block, since an empty string is not a
    #     real disclosure.
    def test_core_false_unsupported_entry_with_empty_string_note_still_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "non-core claim with a blank note", "core": False,
             "url": "https://example.com/c2", "fetched_content_supports_claim": False,
             "note": "   "},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        st = self.state()
        self.assertEqual(st["status"], "failed")

    # 4. A mix: one core:true false entry AND one core:false false entry
    #    (with a real note) present together -- MUST block. The core
    #    failure alone is sufficient cause, regardless of the honestly
    #    disclosed non-core entry sitting right next to it.
    def test_mixed_core_true_failure_and_core_false_disclosed_entry_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "core claim that failed verification", "core": True,
             "url": "https://example.com/d1", "fetched_content_supports_claim": False,
             "note": "a note does not rescue a core claim"},
            {"claim": "non-core claim with an honest disclosure", "core": False,
             "url": "https://example.com/d2", "fetched_content_supports_claim": False,
             "note": "genuinely disclosed non-core gap, would pass on its own"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])

    # 5. Backward compatibility: an approval.json with NO core field
    #    anywhere on any entry (pre-dating this schema addition), and no
    #    legacy [NON-CORE] text marker either, behaves exactly as it did
    #    before this fix -- full strict gating, nothing silently loosened
    #    for old data. Reuses the exact same shape as the pre-fix
    #    regression test in TestApprovalFileGateLaw164165.
    def test_backward_compat_no_core_field_anywhere_still_strict(self):
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

    # 6. The actual real-world case: an entry using ONLY the legacy
    #    [NON-CORE] text prefix (no structured "core" field at all),
    #    fetched_content_supports_claim: false, with a real non-empty
    #    note -- must NOT block. Uses the real wording pattern from batch
    #    8ca83216's actual approval.json as the fixture.
    def test_legacy_non_core_text_prefix_with_real_note_does_not_block(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "[NON-CORE, evening] Season runs two cours: first cour "
                      "Oct 2 2026, second cour premieres April 2027.",
             "url": "https://www.cbr.com/the-apothecary-diaries-season-3-october-2-premiere/",
             "fetched_content_supports_claim": False,
             "note": "Fetched fresh this session. CBR confirms the Oct 2, 2026 date "
                      "and a 'two-part release schedule' but does NOT itself state the "
                      "April 2027 second-cour date. However, the underlying fact is "
                      "independently and directly confirmed by the animenewsnetwork.com "
                      "source already cited on the CORE 'two cours' beat."},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 0)
        st = self.state()
        self.assertEqual(st["status"], "success")
        self.assertTrue(st["log_appended"])

    # 7. A structured core:false field where the claim text does NOT start
    #    with [NON-CORE] -- must still NOT block, confirming the structured
    #    field works independently of the text convention.
    def test_structured_core_false_without_text_marker_does_not_block(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "a plainly worded non-core claim with no bracket marker",
             "core": False, "url": "https://example.com/e",
             "fetched_content_supports_claim": False,
             "note": "structured core:false alone is enough, no text marker needed"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 0)
        st = self.state()
        self.assertEqual(st["status"], "success")

    # 8. The claim text starts with [NON-CORE] but structured core: true is
    #    ALSO present -- must block. Confirms the structured field takes
    #    precedence over the text prefix when both exist, so the two
    #    signals can never silently disagree in the permissive direction.
    def test_structured_core_true_overrides_conflicting_text_marker_and_blocks(self):
        approval_path = self.write_approval_file(fetch_review=[
            {"claim": "[NON-CORE] this text says non-core but the field overrides it",
             "core": True, "url": "https://example.com/f",
             "fetched_content_supports_claim": False,
             "note": "even with a note, structured core:true must win and block"},
        ])
        rc = self.run_cli("--emails-sent", approval_file=approval_path)
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.events_path))
        st = self.state()
        self.assertEqual(st["status"], "failed")
        self.assertFalse(st["log_appended"])


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

    # --- F73: pending/ directory not named after the raw batch_id ---

    def human_named_pending_dir(self, dirname):
        return os.path.join(self.tree, "cron_tracking", CRON_ID, "pending", dirname)

    def seed_pending_human_named(self, dirname, extra: dict | None = None):
        """Same as seed_pending(), but under a human-readable directory name
        instead of the raw batch_id -- reproducing batchA_20260901,
        fresh_20260907, etc."""
        d = self.human_named_pending_dir(dirname)
        os.makedirs(d, exist_ok=True)
        body = {
            "status": "AWAITING_" + "APPROVAL",
            "emails_sent": False,
            "batch_id": self.manifest["batch_id"],
            "post_date": self.manifest.get("post_date"),
        }
        if extra:
            body.update(extra)
        with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as fh:
            json.dump(body, fh)
        return d

    def test_human_named_pending_dir_still_flips_to_terminal(self):
        # F73's actual failure mode: dirname != batch_id, so the old fast-path
        # os.path.isdir() check missed it and silently returned None -- no
        # per-batch terminal state was ever written for these real batches.
        d = self.seed_pending_human_named("fresh_20260907")
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        with open(os.path.join(d, "state.json"), encoding="utf-8") as fh:
            mirrored = json.load(fh)
        self.assertEqual(mirrored["status"], "sent")
        self.assertEqual(mirrored["batch_id"], self.manifest["batch_id"])

    def test_human_named_pending_dir_preserves_step6_fields(self):
        # the fallback path must merge exactly like the fast path does --
        # held_packages/corrects_batch_id must survive here too.
        held = [{"show": "Slime", "disposition": "HELD_NOT_SENT",
                 "still_open": True}]
        d = self.seed_pending_human_named("batchB_20260902", {
            "corrects_batch_id": "b03ef8b6-d254-442a-aaf9-673a6578a0c5",
            "held_packages": held,
        })
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        with open(os.path.join(d, "state.json"), encoding="utf-8") as fh:
            mirrored = json.load(fh)
        self.assertEqual(mirrored["status"], "sent")
        self.assertEqual(mirrored["corrects_batch_id"],
                         "b03ef8b6-d254-442a-aaf9-673a6578a0c5")
        self.assertEqual(mirrored["held_packages"], held)

    def test_unrelated_human_named_dirs_are_not_matched(self):
        # the fallback must match by batch_id, not just "first directory
        # found" or "any directory that exists" -- an unrelated pending batch
        # sitting alongside must never get overwritten.
        unrelated_id = "11111111-2222-3333-4444-555555555555"
        unrelated_dir = self.human_named_pending_dir("unrelated_batch")
        os.makedirs(unrelated_dir, exist_ok=True)
        unrelated_body = {"status": "AWAITING_" + "APPROVAL",
                          "batch_id": unrelated_id}
        with open(os.path.join(unrelated_dir, "state.json"), "w",
                 encoding="utf-8") as fh:
            json.dump(unrelated_body, fh)

        target_dir = self.seed_pending_human_named("the_real_batch")
        self.assertEqual(self.run_cli("--emails-sent"), 0)

        with open(os.path.join(target_dir, "state.json"), encoding="utf-8") as fh:
            target_after = json.load(fh)
        self.assertEqual(target_after["status"], "sent")

        with open(os.path.join(unrelated_dir, "state.json"), encoding="utf-8") as fh:
            unrelated_after = json.load(fh)
        self.assertEqual(unrelated_after, unrelated_body,
                         "an unrelated batch's pending state must be left "
                         "completely untouched by another batch's mirror")

    def test_batch_id_can_be_read_from_run_manifest_json(self):
        # some real pending dirs only carry run_manifest.json, not a
        # pre-existing state.json, before a batch is ever sent -- the
        # fallback must still find them via that file.
        d = self.human_named_pending_dir("fresh_20260907")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "run_manifest.json"), "w",
                 encoding="utf-8") as fh:
            json.dump({"batch_id": self.manifest["batch_id"]}, fh)
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        with open(os.path.join(d, "state.json"), encoding="utf-8") as fh:
            mirrored = json.load(fh)
        self.assertEqual(mirrored["status"], "sent")

    def test_no_matching_dir_anywhere_is_still_a_clean_noop(self):
        # if NO pending directory (raw-UUID or human-named) matches this
        # batch_id at all, this must behave exactly like the pre-existing
        # "no pending dir" case -- clean no-op, no crash, no phantom file.
        self.human_named_pending_dir("someone_elses_batch")
        os.makedirs(self.human_named_pending_dir("someone_elses_batch"),
                   exist_ok=True)
        with open(os.path.join(
                self.human_named_pending_dir("someone_elses_batch"),
                "state.json"), "w", encoding="utf-8") as fh:
            json.dump({"batch_id": "99999999-0000-0000-0000-000000000000",
                      "status": "AWAITING_APPROVAL"}, fh)
        self.assertEqual(self.run_cli("--emails-sent"), 0)
        self.assertFalse(os.path.exists(self.pending_path()))
        self.assertEqual(self.state()["status"], "success")


class TestCheckPendingBatchesLaw166(LoggerCase):
    """Item #2 (recurring-failure-patterns audit): Law #166's pending-batch
    check was prose-only (see cron_daily_runtime.txt), enforced only by an
    LLM reading a directory listing. check_pending_batches() ports the exact
    two-part test the prose already specifies into real, testable code."""

    def pending_root(self):
        return os.path.join(self.tree, "cron_tracking", CRON_ID, "pending")

    def seed_pending_state(self, batch_id, status, *, corrects_batch_id=None,
                            dirname=None):
        dirname = dirname or batch_id
        d = os.path.join(self.pending_root(), dirname)
        os.makedirs(d, exist_ok=True)
        payload = {"batch_id": batch_id, "status": status}
        if corrects_batch_id is not None:
            payload["corrects_batch_id"] = corrects_batch_id
        with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def seed_confirmed_send(self, batch_id, package_id="pkg-1"):
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)
        with open(self.events_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"batch_id": batch_id, "package_id": package_id,
                                  "event": "sent"}) + "\n")

    # 1: AWAITING_APPROVAL + no send anywhere -> blocks
    def test_awaiting_approval_no_send_blocks(self):
        self.seed_pending_state("b1", "AWAITING_APPROVAL")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual([r["batch_id"] for r in blocking], ["b1"])

    # 2: AWAITING_VO + no send -> blocks
    def test_awaiting_vo_no_send_blocks(self):
        self.seed_pending_state("b2", "AWAITING_VO")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual([r["batch_id"] for r in blocking], ["b2"])

    # 3: AWAITING_APPROVAL but a real sent row exists (F38 stale-state) -> does not block
    def test_stale_awaiting_status_with_real_send_does_not_block(self):
        self.seed_pending_state("b3", "AWAITING_APPROVAL")
        self.seed_confirmed_send("b3")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 4: corrects_batch_id present + demonstrably sent + still reads AWAITING_* -> F37 carve-out
    def test_correction_batch_carveout_does_not_block(self):
        self.seed_pending_state("b4", "AWAITING_APPROVAL", corrects_batch_id="b0")
        self.seed_confirmed_send("b4")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 5: terminal status "sent" -> does not block
    def test_terminal_sent_status_does_not_block(self):
        self.seed_pending_state("b5", "sent")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 5b: terminal CLOSED_NOTHING_SHIPPED status -> does not block
    def test_terminal_closed_nothing_shipped_does_not_block(self):
        self.seed_pending_state("b5b", "CLOSED_NOTHING_SHIPPED")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 6: missing/corrupt state.json -> fails open, does not block, does not crash
    def test_missing_state_json_fails_open(self):
        os.makedirs(os.path.join(self.pending_root(), "b6"), exist_ok=True)
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    def test_corrupt_state_json_fails_open(self):
        d = os.path.join(self.pending_root(), "b6b")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as fh:
            fh.write("{ not valid json")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 6c: state.json missing the status field entirely -> fails open
    def test_missing_status_field_fails_open(self):
        d = os.path.join(self.pending_root(), "b6c")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as fh:
            json.dump({"batch_id": "b6c"}, fh)
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 6d: substring false-positive guard -- a status string that merely CONTAINS
    # "AWAITING_APPROVAL" as a substring (not an exact match) must not block,
    # proving this is a direct field-equality read, not a grep (the F38 bug class).
    def test_substring_status_is_not_treated_as_exact_match(self):
        self.seed_pending_state("b6d", "PREVIOUSLY_AWAITING_APPROVAL_NOW_CLOSED")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 7: no pending directory at all -> clean empty list, no crash
    def test_no_pending_directory_is_clean_noop(self):
        self.assertFalse(os.path.isdir(self.pending_root()))
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 8: top-level state.json (not the JSONL ledger) carries the confirmed send
    def test_confirmed_send_via_top_level_state_json_does_not_block(self):
        self.seed_pending_state("b8", "AWAITING_APPROVAL")
        top_state_dir = os.path.join(self.tree, "cron_tracking", CRON_ID)
        os.makedirs(top_state_dir, exist_ok=True)
        with open(os.path.join(top_state_dir, "state.json"), "w", encoding="utf-8") as fh:
            json.dump({"batch_id": "b8", "status": "success"}, fh)
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [])

    # 9: multiple pending batches -- only the genuinely blocking ones are returned
    def test_multiple_pending_only_real_blockers_returned(self):
        self.seed_pending_state("ok1", "sent")
        self.seed_pending_state("blocker1", "AWAITING_APPROVAL")
        self.seed_pending_state("blocker2", "AWAITING_VO")
        self.seed_pending_state("stale1", "AWAITING_APPROVAL")
        self.seed_confirmed_send("stale1")
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(sorted(r["batch_id"] for r in blocking),
                         ["blocker1", "blocker2"])

    # 10: real production data -- the 8 actual pending directories from this
    # repo's real cron_tracking tree are all terminal (sent / CLOSED_NOTHING_
    # SHIPPED); reproduced here as a fixture snapshot (not a live filesystem
    # dependency, so the test suite stays hermetic) to prove the function
    # reports zero blockers against that real, current shape.
    def test_real_current_pending_snapshot_reports_zero_blockers(self):
        real_statuses = {
            "32e0fcb9": "sent",
            "8ca83216": "sent",
            "9baf0f49": "CLOSED_NOTHING_SHIPPED",
            "9dc75e78": "sent",
            "d4a8f107": "CLOSED_NOTHING_SHIPPED",
            "de6845d6": "sent",
            "f21e15f0": "sent",
            "f54413d8": "CLOSED_NOTHING_SHIPPED",
        }
        for batch_id, status in real_statuses.items():
            self.seed_pending_state(batch_id, status)
        blocking = a.check_pending_batches(self.tree, CRON_ID)
        self.assertEqual(blocking, [],
                         "real current pending snapshot must report zero blockers")

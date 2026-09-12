from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

import format_frequency_cooldown as ffc


def _row(*, batch_id, show, post_date, format_type, date_sent=None,
         corrects_batch_id=None, status="sent"):
    r = {
        "batch_id": batch_id, "show": show, "post_date": post_date,
        "format_type": format_type, "status": status,
    }
    if date_sent is not None:
        r["date_sent"] = date_sent
    if corrects_batch_id is not None:
        r["corrects_batch_id"] = corrects_batch_id
    return r


def _write_log(tree: str, rows: list[dict]) -> None:
    path = os.path.join(tree, ffc.LOG_RELATIVE_PATH)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh)


class TestSortKey(unittest.TestCase):
    """(b) ordering: file order is not reliable, so sorting must be explicit."""

    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def test_out_of_order_rows_are_sorted_ascending_by_post_date(self):
        rows = [
            _row(batch_id="b1", show="A", post_date="2026-07-08", format_type="FACT_DROP"),
            _row(batch_id="b2", show="B", post_date="2026-07-04", format_type="FACT_DROP"),
            _row(batch_id="b3", show="C", post_date="2026-07-06", format_type="FACT_DROP"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        self.assertEqual([r["show"] for r in normalized], ["B", "C", "A"])

    def test_tbd_post_date_sorts_by_its_own_date_sent(self):
        rows = [
            _row(batch_id="b1", show="Real", post_date="2026-07-15", format_type="FACT_DROP"),
            _row(batch_id="b2", show="TBDShow", post_date="TBD", format_type="FACT_DROP",
                 date_sent="2026-07-12"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        # TBDShow's real date (07-12) precedes Real's post_date (07-15)
        self.assertEqual([r["show"] for r in normalized], ["TBDShow", "Real"])

    def test_same_post_date_tiebreaks_by_date_sent(self):
        rows = [
            _row(batch_id="b1", show="Evening", post_date="2026-09-10",
                 format_type="FACT_DROP", date_sent="2026-09-10T20:00:00Z"),
            _row(batch_id="b1", show="Morning", post_date="2026-09-10",
                 format_type="COMMENTARY", date_sent="2026-09-10T08:00:00Z"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        self.assertEqual([r["show"] for r in normalized], ["Morning", "Evening"])

    def test_null_date_sent_falls_back_to_post_date_for_tiebreak(self):
        """Two rows sharing post_date: one has date_sent, one doesn't. The
        tiebreak falls back to the row's own post_date when date_sent is
        None, so NoDateSent's tiebreak becomes "2026-07-18" (its post_date)
        while WithDateSent's tiebreak is its later same-day timestamp --
        NoDateSent must sort first."""
        rows = [
            _row(batch_id="b1", show="WithDateSent", post_date="2026-07-18",
                 format_type="FACT_DROP", date_sent="2026-07-18T20:00:00Z"),
            _row(batch_id="b2", show="NoDateSent", post_date="2026-07-18", format_type="FACT_DROP"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        self.assertEqual([r["show"] for r in normalized], ["NoDateSent", "WithDateSent"])

    def test_tbd_post_date_without_date_sent_raises(self):
        """A TBD row with no date_sent has no valid ordering signal at all.
        Silently falling through to the literal string "TBD" as a sort key
        (the original bug, caught on review before commit) would let it
        sort lexicographically against real ISO dates. Must raise instead
        of guessing."""
        rows = [
            _row(batch_id="b1", show="Unorderable", post_date="TBD", format_type="FACT_DROP"),
        ]
        _write_log(self.tree, rows)
        with self.assertRaises(ValueError):
            ffc.load_normalized_sends(self.tree)


class TestCorrectionDedup(unittest.TestCase):
    """(d) dedup must match on (corrects_batch_id, show), never batch_id alone --
    the real bug this module's first draft had, caught by testing against the
    real file before shipping."""

    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def test_corrected_row_is_dropped_correction_kept(self):
        rows = [
            _row(batch_id="orig1", show="Link Click", post_date="2026-08-14",
                 format_type="SEASON_PREVIEW"),
            _row(batch_id="corr1", show="Link Click", post_date="2026-08-14",
                 format_type="SEASON_PREVIEW", corrects_batch_id="orig1"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        link_click_rows = [r for r in normalized if r["show"] == "Link Click"]
        self.assertEqual(len(link_click_rows), 1)
        self.assertEqual(link_click_rows[0]["batch_id"], "corr1")

    def test_sibling_package_in_same_batch_is_NOT_dropped(self):
        """The exact real bug: correction targets a batch_id shared by TWO
        packages (morning+evening). Only the matching-show package should be
        dropped -- the sibling package is a real, unrelated ship."""
        rows = [
            _row(batch_id="orig1", show="Link Click", post_date="2026-08-14",
                 format_type="SEASON_PREVIEW"),
            _row(batch_id="orig1", show="Slime S4", post_date="2026-08-14",
                 format_type="EPISODE_MOMENT"),
            _row(batch_id="corr1", show="Link Click", post_date="2026-08-14",
                 format_type="SEASON_PREVIEW", corrects_batch_id="orig1"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        shows = sorted(r["show"] for r in normalized)
        self.assertEqual(shows, ["Link Click", "Slime S4"])
        self.assertEqual(len(normalized), 2)

    def test_two_independent_correction_pairs_both_resolve_correctly(self):
        rows = [
            _row(batch_id="b1", show="Link Click", post_date="2026-08-14", format_type="SEASON_PREVIEW"),
            _row(batch_id="b1", show="Slime S4", post_date="2026-08-14", format_type="EPISODE_MOMENT"),
            _row(batch_id="b2", show="Link Click", post_date="2026-08-14",
                 format_type="SEASON_PREVIEW", corrects_batch_id="b1"),
            _row(batch_id="b3", show="Kingdom Hearts", post_date="2026-08-23", format_type="FACT_DROP"),
            _row(batch_id="b3", show="Bleach TYBW", post_date="2026-08-23", format_type="EPISODE_MOMENT"),
            _row(batch_id="b4", show="Kingdom Hearts", post_date="2026-08-23",
                 format_type="FACT_DROP", corrects_batch_id="b3"),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        self.assertEqual(len(normalized), 4)  # 6 raw - 2 dropped originals
        shows = sorted(r["show"] for r in normalized)
        self.assertEqual(shows, ["Bleach TYBW", "Kingdom Hearts", "Link Click", "Slime S4"])


class TestNoStatusFilter(unittest.TestCase):
    """(c) every row counts as a real send regardless of status value -- no
    status value in the real file means unsent, and filtering would silently
    drop real ships."""

    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def test_all_status_variants_are_counted(self):
        rows = [
            _row(batch_id="b1", show="A", post_date="2026-07-01", format_type="FACT_DROP", status="sent"),
            _row(batch_id="b2", show="B", post_date="2026-07-02", format_type="FACT_DROP", status="SENT"),
            _row(batch_id="b3", show="C", post_date="2026-07-03", format_type="FACT_DROP", status="sent_corrected_v2"),
            _row(batch_id="b4", show="D", post_date="2026-07-04", format_type="FACT_DROP", status=None),
        ]
        _write_log(self.tree, rows)
        normalized = ffc.load_normalized_sends(self.tree)
        self.assertEqual(len(normalized), 4)


class TestTrailingWindowAndCooldown(unittest.TestCase):
    def setUp(self):
        self.tree = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def test_trailing_n_takes_last_n_after_normalization_not_raw_tail(self):
        # 10 rows in scrambled file order; trailing 7 by real post_date
        # ordering should be dates 4-10, not whatever the last 7 array
        # entries happen to be.
        rows = [
            _row(batch_id=f"b{i}", show=f"Show{i}", post_date=f"2026-07-{i:02d}", format_type="FACT_DROP")
            for i in [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]  # scrambled
        ]
        _write_log(self.tree, rows)
        trailing = ffc.get_trailing_n(self.tree, 7)
        self.assertEqual([r["post_date"] for r in trailing],
                          ["2026-07-04", "2026-07-05", "2026-07-06", "2026-07-07",
                           "2026-07-08", "2026-07-09", "2026-07-10"])

    def test_format_counts_and_cooldown_flag(self):
        rows = [
            _row(batch_id="b1", show="A", post_date="2026-07-01", format_type="FACT_DROP"),
            _row(batch_id="b2", show="B", post_date="2026-07-02", format_type="FACT_DROP"),
            _row(batch_id="b3", show="C", post_date="2026-07-03", format_type="COMMENTARY"),
        ]
        _write_log(self.tree, rows)
        counts = ffc.format_counts_in_window(self.tree, 7)
        self.assertEqual(counts, {"FACT_DROP": 2, "COMMENTARY": 1})
        on_cd, cnt = ffc.is_on_cooldown(self.tree, "FACT_DROP", n=7)
        self.assertTrue(on_cd)
        self.assertEqual(cnt, 2)
        on_cd2, cnt2 = ffc.is_on_cooldown(self.tree, "COMMENTARY", n=7)
        self.assertFalse(on_cd2)
        self.assertEqual(cnt2, 1)

    def test_format_not_in_window_is_not_on_cooldown(self):
        rows = [
            _row(batch_id="b1", show="A", post_date="2026-07-01", format_type="FACT_DROP"),
        ]
        _write_log(self.tree, rows)
        on_cd, cnt = ffc.is_on_cooldown(self.tree, "WRONG_TAKE", n=7)
        self.assertFalse(on_cd)
        self.assertEqual(cnt, 0)


if __name__ == "__main__":
    unittest.main()

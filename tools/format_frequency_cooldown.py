#!/usr/bin/env python3
"""Trailing-7 format-frequency cooldown gate (Step 2, added 2026-09-11).

Answers one question: "of the last 7 real sends, how many used format_type X,
and is X therefore on cooldown for today's selection?" This is a genuinely
different question from tools/conflict_check.py's blackout/near-duplicate
checks -- those ask "was THIS SPECIFIC show/angle sent too recently," this
asks "has THIS FORMAT been overused in the recent rotation, regardless of
show." Both can be true or false independently.

DELIBERATE FILE CHOICE -- READ BEFORE CHANGING (per F84,
docs/KNOWN_ISSUES.md): this module reads `sent_scripts_log.json`, NOT
`cron_tracking/sent_scripts_events.jsonl`, even though
tools/conflict_check.py's live checks read the latter. This is intentional,
not an inconsistency to "fix":

  - cron_daily_runtime.txt's own REFRAME prose already specifies
    sent_scripts_log.json as the cooldown source (the "cooldown tracks
    ships, never candidates" correction) -- this module implements that
    existing documented decision rather than reverting to an undocumented
    one.
  - A trailing-7 read is inherently a full-history question. events.jsonl
    is a strict subset of log.json covering only 2026-07-14 onward (97 of
    241 real sends, per F84) -- reading it here would make this new gate
    wrong by construction from day one, not merely exposed to a latent risk
    the way conflict_check.py's date-window blackouts are.
  - F84 explicitly declined to change what EXISTING checks read, because
    that is a live-enforcement behavior change needing its own review. That
    reasoning protects conflict_check.py's current behavior; it does not
    oblige a brand-new check to inherit the same limitation when the wider,
    more complete file is available and sufficient.

  Do not point this module at sent_scripts_events.jsonl to "match"
  conflict_check.py. The divergence is deliberate and each file is correct
  for what it backs.

DATA-QUALITY FINDINGS THIS MODULE'S NORMALIZATION EXISTS TO HANDLE (verified
directly against the real file, 2026-09-11, before writing any of the logic
below -- see docs/KNOWN_ISSUES.md F84's cooldown-gate discussion for the
full verification trace):

  (a) format_type coverage: all 148 pre-batch_id rows (of 241 total) carry a
      real format_type. No blind spot here -- every row is usable.

  (b) ORDERING IS NOT RELIABLE AS FILE ORDER. 11 real inversions exist
      between file order and ascending post_date. 5 rows carry
      post_date == "TBD" (all sharing date_sent == "2026-07-12"). This
      module therefore sorts explicitly -- see _sort_key() -- rather than
      trusting array order or taking a raw tail slice.

  (c) NO STATUS FILTER. status takes four real values in this file --
      "sent", "SENT", "sent_corrected_v2", and None (43 rows, all
      pre-batch_id, all with a real format_type and post_date; they simply
      predate this file consistently carrying a status field). No status
      value anywhere in the file means draft, held, rejected, or cancelled
      -- verified by keyword scan, 2026-09-11. A naive `status == "sent"`
      filter would silently drop the uppercase variant, the corrected
      variant, and all 43 nulls -- none of which represents unshipped
      content. So this module counts every row as a real send and performs
      NO status-based filtering. THIS IS A LOAD-BEARING ASSUMPTION: if a
      future status value is ever introduced that means "not actually
      sent" (e.g. "draft", "held", "superseded"), this module's "count
      every row" behavior becomes wrong and must be revisited alongside
      that change -- it will not fail loudly on its own, since it has no
      status filter to begin with.

  (d) CORRECTION-PAIR DEDUP IS REQUIRED -- BY (corrects_batch_id, show), NOT
      BY batch_id ALONE. Exactly 2 rows in the file carry a
      `corrects_batch_id` (Link Click, post_date 2026-08-14; Kingdom
      Hearts, post_date 2026-08-23). In both cases the original row this
      correction targets is IDENTICAL to the correction in
      show/format_type/post_date and both carry status "sent" -- i.e. this
      is one real ship, corrected once, appearing twice in the raw file.
      Counting both would inflate that format's recent-frequency count by
      one per corrected ship.

      FIRST DRAFT OF THIS DEDUP WAS WRONG, CAUGHT BY TESTING AGAINST THE
      REAL FILE BEFORE SHIPPING (2026-09-11): batch_id is NOT a per-package
      key here -- each daily batch carries TWO packages (morning + evening)
      sharing one batch_id. corrects_batch_id points at a batch_id, not a
      package_id, and that target batch's OTHER (uncorrected) package is a
      real, distinct, unrelated ship that must stay in the count. Matching
      and dropping by batch_id alone (this module's original
      implementation) silently deleted that sibling package too -- for the
      two real pairs, that meant "That Time I Got Reincarnated as a Slime"
      (2026-08-14) and "Bleach: Thousand-Year Blood War - The Calamity"
      (2026-08-23) would have been wrongly dropped alongside the actual
      corrected rows. Running the module against the real file and
      independently checking the resulting row count (237 instead of the
      expected 239) is what surfaced this -- see conflict_check.py's own
      SECOND DESIGN CORRECTION docstring, which hit the identical
      batch-vs-package distinction first and excludes only "the specific
      batch_id AND show" pairing, never a whole batch.

      This module now matches the same way: a row is dropped only when
      BOTH its batch_id equals some other row's corrects_batch_id AND its
      show matches that correcting row's show. This isolates the one
      sibling package that is the real target and leaves the other
      package in that batch untouched.

Together, (b)+(d) mean this module normalizes the raw JSON list once
(dedup, then sort) before ever taking a trailing-N slice. Skipping either
step produces a plausible-looking but wrong answer -- see get_trailing_n()'s
own docstring for why this matters more here than in a typical log read.
"""

from __future__ import annotations

import json
import os
from typing import Any

LOG_RELATIVE_PATH = "sent_scripts_log.json"

# The window size used by the daily runtime's format-diversity gate
# (STEP 3's ACTIVE FORMAT-DIVERSITY WEIGHTING sub-step already reads a
# trailing-14 window from this same file for a related-but-distinct
# purpose; this module's cooldown gate uses a trailing-7 window, per the
# build spec this closes). Kept as a named constant rather than a bare
# literal so a future change to the window size has one place to change it.
TRAILING_WINDOW_SIZE = 7


def _log_path(tree: str) -> str:
    return os.path.join(tree, LOG_RELATIVE_PATH)


def _sort_key(row: dict[str, Any]) -> tuple[str, str]:
    """Sort key: (post_date, date_sent) ascending, with fallbacks for the
    known-bad values found in the real file.

    post_date is the primary key (that's the field the runtime's own
    selection logic keys on for "today vs. recent"). The 5 rows with
    post_date == "TBD" would otherwise sort before every real date
    (since "TBD" > all digit characters is NOT guaranteed lexicographically
    and must not be relied on) -- so a TBD post_date is replaced by that
    row's own date_sent for sort purposes only (all 5 TBD rows share
    date_sent == "2026-07-12", a real, valid date), never for reporting.

    date_sent is the tiebreak for rows sharing the same post_date (morning/
    evening same-day pairs are common and expected). date_sent itself is
    inconsistently formatted (plain "YYYY-MM-DD", ISO with UTC offset, ISO
    with "Z", or None for 11 rows).

    FIRST DRAFT BUG (caught by testing before shipping, 2026-09-11): this
    tiebreak originally used only the first 10 characters of date_sent (the
    YYYY-MM-DD date portion). For a same-day morning/evening pair that
    tiebreak is a no-op by construction -- both rows share the same date
    portion, so the intended chronological tiebreak silently never fires
    and same-day pairs fall back to raw file order (stable sort), which is
    exactly the unreliable ordering this function exists to fix. A real
    same-day pair with distinct times (e.g. "...T08:00:00Z" vs
    "...T20:00:00Z") would have kept file order instead of the correct
    time-of-day order.

    Fix: use the FULL date_sent string as the tiebreak, not a truncated
    prefix. A plain lexicographic compare of the full string is not a
    correct chronological compare across mismatched formats in general
    (e.g. a "+00:00" offset row vs a "Z" row vs a bare-date row could sort
    wrong relative to each other), but this module does not attempt full
    timestamp parsing across four inconsistent shapes -- that is a real,
    open limitation, not solved here. It is safe for the common case this
    tiebreak exists for (two same-day rows written moments apart in the
    SAME batch, which in every real instance checked share an identical
    date_sent format since they come from one daily run) and is strictly
    better than the truncated version for every case it changes. Falls
    back to the row's own post_date when date_sent is None. Python's sort
    is stable, so rows that still tie after both keys keep their original
    relative file order.

    LATENT BUG, CAUGHT ON REVIEW BEFORE COMMIT (2026-09-11, not caught by
    the real-data run or by tests -- found by inspection): the TBD branch
    below originally read
        sort_post_date = date_sent[:10] if post_date == "TBD" and date_sent else post_date
    If a TBD row ever had date_sent == None, the `and date_sent` guard
    fails and sort_post_date falls through to the literal string "TBD" --
    which then sorts lexicographically against real "YYYY-MM-DD" strings,
    the exact failure this branch exists to prevent, and does so silently.
    All 5 real TBD rows in the current file carry a valid date_sent, so
    this could not fire today, but nothing enforces that invariant and a
    future TBD-without-date_sent row would degrade quietly rather than
    loudly.

    Fixed by raising instead of guessing: a TBD row with no date_sent has
    no valid ordering signal at all, and silently placing it somewhere is
    worse than refusing to sort it. This function now raises ValueError
    for that specific combination rather than ever returning "TBD" as a
    sort key.
    """
    post_date = row.get("post_date") or ""
    date_sent = row.get("date_sent")
    if post_date == "TBD" and not date_sent:
        raise ValueError(
            f"Row with post_date == 'TBD' has no date_sent and cannot be "
            f"ordered: {row!r}. Refusing to sort rather than silently "
            f"placing it via a literal 'TBD' string key."
        )
    sort_post_date = date_sent[:10] if post_date == "TBD" and date_sent else post_date
    tiebreak = date_sent or post_date or ""
    return (sort_post_date, tiebreak)


def load_normalized_sends(tree: str) -> list[dict[str, Any]]:
    """Load sent_scripts_log.json, apply correction-pair dedup, and sort
    ascending by (post_date, date_sent). Returns the normalized list -- this
    is the ONLY function in this module that reads the raw file; every
    other function in this module operates on its output, never on the raw
    JSON directly, so the dedup+sort normalization can never be
    accidentally bypassed by a caller reading the file a different way.
    """
    path = _log_path(tree)
    with open(path, encoding="utf-8") as fh:
        rows: list[dict[str, Any]] = json.load(fh)

    # (target_batch_id, show) pairs to drop -- matched on BOTH fields, never
    # batch_id alone. A correction's corrects_batch_id names a whole daily
    # batch, which carries two packages (morning + evening); only the ONE
    # package matching the correcting row's own `show` is the real target.
    # See module docstring (d) for the real case this guards against: an
    # earlier version of this function matched on batch_id alone and
    # silently dropped the batch's OTHER, unrelated package too.
    corrected_away_keys = {
        (row["corrects_batch_id"], row.get("show"))
        for row in rows
        if row.get("corrects_batch_id")
    }
    deduped = [
        row for row in rows
        if (row.get("batch_id"), row.get("show")) not in corrected_away_keys
    ]

    return sorted(deduped, key=_sort_key)


def get_trailing_n(tree: str, n: int = TRAILING_WINDOW_SIZE) -> list[dict[str, Any]]:
    """Return the last `n` real sends, in ascending (oldest-first) order,
    from the normalized (deduped + sorted) sequence.

    Calling this instead of `raw_list[-n:]` on the untouched file matters
    for two independently confirmed reasons (see module docstring (b)/(d)):
    file order has 11 real inversions relative to post_date, and 2 rows are
    corrections whose originals must be dropped first or the same real ship
    is double-counted. Skipping either step silently changes which n rows
    come back.
    """
    normalized = load_normalized_sends(tree)
    return normalized[-n:] if n > 0 else []


def format_counts_in_window(tree: str, n: int = TRAILING_WINDOW_SIZE) -> dict[str, int]:
    """Count how many of the trailing `n` real sends used each format_type.
    Convenience wrapper over get_trailing_n() for the common "what's the
    current distribution" question."""
    window = get_trailing_n(tree, n)
    counts: dict[str, int] = {}
    for row in window:
        ft = row.get("format_type")
        if ft:
            counts[ft] = counts.get(ft, 0) + 1
    return counts


def is_on_cooldown(tree: str, format_type: str, n: int = TRAILING_WINDOW_SIZE,
                    max_allowed: int = 1) -> tuple[bool, int]:
    """Return (on_cooldown, count_in_window) for `format_type` against the
    trailing-`n` window. on_cooldown is True when count_in_window >
    max_allowed (default: more than 1 of the last 7 real sends already used
    this format). This is a frequency/rotation gate, not a same-show or
    same-angle check -- it says nothing about which SHOW used the format,
    only how often the FORMAT itself has recently shipped."""
    counts = format_counts_in_window(tree, n)
    count = counts.get(format_type, 0)
    return (count > max_allowed, count)

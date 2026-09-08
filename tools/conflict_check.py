#!/usr/bin/env python3
"""Item #3+#8 (recurring-failure-patterns audit, 2026-08-18): a real,
data-backed near-duplicate/blackout check, replacing pure self-attestation.

Real incident this fixes (F43, docs/KNOWN_ISSUES.md ~line 2009): a One Piece
"Gaban loses his arm at Ch.1190" package nearly re-shipped six days after an
already-sent package covering the identical chapter/character/beat, because
validate_dual_package.py only ever checked that `blackout_conflict` and
`recent_send_conflict` were PRESENT and `False` -- never opened the send log
or blackout state to check the attestation against reality. The exact same
false attestation recurred a second time the same evening in a different
batch (F43's "second occurrence"), confirming this is systemic, not a
one-off.

Real blackout windows, verified 2026-08-18 against three independent sources
(laws/format_reference_seasonal_types.md, laws/law_96_content_rotation_
expansion.md, and hero_or_villain_master_laws_final.txt's own Law #96 block
-- all three agree exactly) plus laws/law_160_theory_speculation.md Decision
4 for WORTH_WATCHING:

    SEASON_RATING     7 days
    SEASON_PREVIEW     7 days  (separate from its own 45-day premiere-window rule)
    MANGA_VS_ANIME    14 days
    WATCH_RANK        14 days
    WORTH_WATCHING     7 days
    EPISODE_MOMENT    no blackout (7-day airing deadline is a different rule)
    THEORY_SPECULATION  same-show-SAME-QUESTION block, escaped only by a real
                         revisit_justification (new_evidence_summary/url/date)
                         -- NOT a fixed day-count, so handled as its own branch.

The remaining 10 format_type tokens (CHARACTER_DIVE, COMMENTARY, FACT_DROP,
HIDDEN_GEM, ORIGIN_STORY, SEASON_ROUNDUP, SLEPT_ON, THE_MOMENT,
VILLAIN_DEFENSE, WRONG_TAKE -- confirmed via grep, 2026-08-18) have NO
format-specific blackout window documented anywhere in the repo.

DESIGN CORRECTION (2026-08-18, same night, post-backtest): the first draft of
this module used a fixed 7-day date-window fallback (from cron_daily_
runtime.txt:42's "30-day blackout + 7-day no-repeat" language) for these 10
formats. Backtesting against the REAL 69-row send history
(cron_tracking/sent_scripts_events.jsonl) immediately falsified that design:
it would have wrongly blocked two real, legitimate sends --
  - Mushoku Tensei COMMENTARY (marriage backlash) then CHARACTER_DIVE (Sara
    apology) 5 days later -- different stories, same show.
  - Jujutsu Kaisen FACT_DROP (finale domain clash) then FACT_DROP (Juju Fest
    news) 3 days later -- different stories, same show.
Both are genuinely distinct content that happened to land within the
invented 7-day floor. Per Sebastian's explicit correction: there is no real
basis for a specific day-count on these 10 formats, and fabricating one is
itself a stale-count risk (the same failure class as item #9). The corrected
design:
  - Uses a single, generous, LOOSE search window (90 days) purely to bound
    which historical rows are even considered -- a search-scoping
    convenience, not a blocking threshold. Nothing older poses a realistic
    near-duplicate risk regardless of format.
  - Within that window, blocking depends ENTIRELY on angle-similarity
    clearing ANGLE_SIMILARITY_THRESHOLD. Date proximity alone never blocks
    for these 10 formats -- a same-show entry 85 days ago with high
    similarity blocks; one 3 days ago with genuinely low similarity does
    not. This generalizes the F43 lesson correctly: duplication is a
    similarity question, not a date question, when there is no documented
    date rule to enforce in the first place.

THIRD DESIGN CORRECTION (same night, post-backtest of the corrected fallback
itself): re-running the real F43 Gaban fixture through the loose-window /
angle-similarity-only design for undocumented formats revealed it would NOT
have caught the real incident. The two real angle strings --
  "Chapter 1190: Scopper Gaban lands the first confirmed injury on Imu in
  the entire series, then loses his arm for it"
  "Gaban sacrifices his arm to save Luffy from Imu in Ch.1190 -- fate left
  unconfirmed"
-- describe the identical real event (same character, same chapter) but
score only 0.26 on difflib.SequenceMatcher, well below
ANGLE_SIMILARITY_THRESHOLD (0.6). Pure text-sequence similarity cannot catch
heavily-paraphrased same-event repeats; that is a semantic-similarity
problem, not a sequence-matching one, and difflib only does the latter.

Per Sebastian's explicit design: this module now runs a SECOND, INDEPENDENT
signal alongside angle-similarity, not a replacement for it -- a package
flags if EITHER signal fires:

  SHARED-ENTITY SIGNAL: same show (already required) AND at least one
  shared capitalized proper noun (character/place name, extracted via a
  simple consecutive-capitalized-word regex -- same mechanical spirit as the
  existing hollow-phrasing/CREDIT_ATTRIBUTION_PATTERN regexes in
  validators/validate_dual_package.py, no NLP/fuzzy matching) AND an exact
  match on a chapter/episode number (normalized across "Chapter 1190" /
  "Ch.1190" / "Ch 1190" / "chapter 1190" formatting variants down to a bare
  number before comparing). Both the proper-noun overlap AND the number
  match are required together -- a shared character mentioned across two
  angles about genuinely different chapters must NOT fire (see adversarial
  test #3), and neither must a bare number match with no named-entity
  overlap (two different shows could coincidentally both be on "chapter 12").

This signal has EQUAL weight to angle-similarity, not advisory status --
either firing is a hard block. When neither an angle-similarity match nor a
shared-entity match exists, and no date-window rule applies, the package is
clear. This is a real, named, accepted limitation of the module: a
same-event repeat that shares no proper noun AND no extractable chapter/
episode number (e.g. two general-mood commentary angles about the same
episode with no character name or number in either string) would still not
be caught by either signal. That gap is not solved here; see
docs/RECURRING_FAILURE_PATTERNS.md for how it's documented going forward.

SECOND DESIGN CORRECTION (same backtest): the first draft also had no
same-batch or same-correction-target exclusion. Backtesting surfaced batch
c8401ef5 (two same-day/adjacent-day package pairs under one batch_id) and the
real correction pair b03ef8b6 -> 32e0fcb9 (32e0fcb9 carries
corrects_batch_id="b03ef8b6...", re-sourcing a citation for the SAME Link
Click premiere angle one day later) as false positives against the
uncorrected design. Investigation confirmed corrects_batch_id is a real,
intentional field: the correction mechanism is supposed to resend
near-identical content for the specific batch it is fixing, so flagging that
as a conflict would be wrong. This module now:
  - Never compares two rows sharing the same batch_id (candidate's own
    batch_id, when provided, is excluded from history entirely).
  - When the candidate carries a real corrects_batch_id, excludes ONLY that
    specific target batch_id from comparison -- the correction is still
    checked against every OTHER unrelated historical row normally.

This does NOT attempt the harder "did we already tell this exact story"
problem in full (KNOWN_ISSUES.md's own "one honest caveat on scope" already
flags that a date window alone would not have caught Gaban on day 8, since
the chapter/beat was still the same after the 7-day window lapsed). This
module's angle-similarity signal directly closes that gap for the 6
documented formats too (checked independent of the date window, not only as
the undocumented-format fallback).
"""

from __future__ import annotations

import datetime as dt
import difflib
import json
import os
import re
from typing import Any

# Verified 2026-08-18 (adjustment 1 of the recurring-failure-patterns audit)
# against laws/format_reference_seasonal_types.md, laws/law_96_content_
# rotation_expansion.md, and the master file's own Law #96 block -- all three
# agree exactly. Do not hand-edit without re-verifying against those three
# sources; a mismatch here would itself be an instance of item #9's stale-
# count failure pattern.
FORMAT_BLACKOUT_DAYS: dict[str, int] = {
    "SEASON_RATING": 7,
    "SEASON_PREVIEW": 7,
    "MANGA_VS_ANIME": 14,
    "WATCH_RANK": 14,
    "WORTH_WATCHING": 7,
    "EPISODE_MOMENT": 0,  # no blackout -- see module docstring
}

# THEORY_SPECULATION is deliberately excluded from FORMAT_BLACKOUT_DAYS: it
# uses a same-show-SAME-QUESTION block with a revisit_justification escape
# hatch (Decision 4), not a fixed day count. Handled by its own branch below.
THEORY_SPECULATION_FORMAT = "THEORY_SPECULATION"

# Search-scoping only (NOT a blocking threshold) for the 10 format_type
# tokens with no documented blackout window anywhere in the repo. Rows older
# than this are not even considered for the angle-similarity check, since
# nothing realistically stays a near-duplicate risk past this horizon.
# Corrected 2026-08-18 per real-data backtest -- see module docstring.
UNDOCUMENTED_FORMAT_SEARCH_WINDOW_DAYS = 90

# Below this similarity ratio on difflib.SequenceMatcher, two angles are
# treated as coincidentally-similar rather than a real repeat. Chosen
# conservatively (favor false negatives over false positives) since this is
# a NEW check with no tuning history yet; revisit once more real data exists.
ANGLE_SIMILARITY_THRESHOLD = 0.6

# Consecutive-capitalized-word extraction for the shared-entity signal (THIRD
# DESIGN CORRECTION -- see module docstring). Same mechanical spirit as the
# repo's existing hollow-phrasing/CREDIT_ATTRIBUTION_PATTERN regexes: no NLP,
# no fuzzy matching, just a deterministic pattern. Matches 1-3 consecutive
# capitalized words (e.g. "Gaban", "Scopper Gaban", "Xia Fei") to catch both
# single-word and multi-word names without over-matching entire capitalized
# sentences. Common sentence-leading words that are capitalized only because
# they start a sentence are filtered by _PROPER_NOUN_STOPWORDS below.
_PROPER_NOUN_RE = re.compile(
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"
)
_PROPER_NOUN_STOPWORDS = frozenset({
    "chapter", "episode", "season", "the", "this", "that", "so", "every",
    "same", "part", "day", "days",
})

# Chapter/episode number extraction, normalizing "Chapter 1190" / "Ch.1190"
# / "Ch 1190" / "chapter 1190" / "Episode 7" / "Ep. 7" down to a bare digit
# string for comparison.
_CHAPTER_EPISODE_RE = re.compile(
    r"\b(?:chapter|ch\.?|episode|ep\.?)\s*#?\s*(\d+)\b", re.IGNORECASE
)


def _parse_date(value: Any) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def _load_send_history(tree: str) -> list[dict[str, Any]]:
    """Every parseable row from sent_scripts_events.jsonl. Matches
    _existing_keys_jsonl's WARN-and-continue convention (append_send_batch.py)
    for malformed lines -- one bad historical line must never block the scan.
    """
    path = os.path.join(tree, "cron_tracking", "sent_scripts_events.jsonl")
    rows: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        pass
    return rows


def _extract_proper_nouns(text: str) -> set[str]:
    """Consecutive-capitalized-word tokens, lowercased for comparison, minus
    common sentence-leading stopwords. Deliberately crude (no NLP) -- this
    is a cheap secondary signal, not a named-entity recognizer.
    """
    found = set()
    for m in _PROPER_NOUN_RE.finditer(text):
        token = m.group(0).strip().lower()
        # Drop pure-stopword matches (a single stopword capitalized only
        # because it starts a sentence, e.g. "So", "The", "Chapter").
        words = token.split()
        if all(w in _PROPER_NOUN_STOPWORDS for w in words):
            continue
        found.add(token)
    return found


def _extract_chapter_episode_numbers(text: str) -> set[str]:
    """Bare digit strings from every chapter/episode mention, normalized
    across "Chapter 1190" / "Ch.1190" / "Ch 1190" / "Episode 7" / "Ep. 7"
    formatting variants.
    """
    return {m.group(1) for m in _CHAPTER_EPISODE_RE.finditer(text)}


def _shared_entity_signal(angle_a: str, angle_b: str) -> bool:
    """True if both angles share at least one proper noun AND an exact
    chapter/episode number match. Both conditions required together -- see
    module docstring's THIRD DESIGN CORRECTION for why.
    """
    nouns_a = _extract_proper_nouns(angle_a)
    nouns_b = _extract_proper_nouns(angle_b)
    if not (nouns_a & nouns_b):
        return False
    numbers_a = _extract_chapter_episode_numbers(angle_a)
    numbers_b = _extract_chapter_episode_numbers(angle_b)
    if not (numbers_a & numbers_b):
        return False
    return True


def _excluded_batch_ids(pkg: dict[str, Any]) -> set[str]:
    """batch_ids that must never be compared against this candidate: its own
    batch (defensive -- guards against future reuse where a candidate is
    checked against a history list that already includes its own batch's
    other packages) and the specific batch it is correcting, if any.
    """
    excluded: set[str] = set()
    own = pkg.get("batch_id")
    if isinstance(own, str) and own:
        excluded.add(own)
    corrects = pkg.get("corrects_batch_id")
    if isinstance(corrects, str) and corrects:
        excluded.add(corrects)
    return excluded


def check_recent_send_conflict(pkg: dict[str, Any], tree: str,
                                *, history: list[dict[str, Any]] | None = None
                                ) -> dict[str, Any]:
    """Real, data-backed near-duplicate/blackout check for one draft package.

    Signal precedence (checked in this order; first true signal governs).
    Before any signal check, rows sharing the candidate's own batch_id, or
    the specific batch_id named in the candidate's corrects_batch_id (if
    any), are excluded from comparison entirely -- see module docstring's
    "SECOND DESIGN CORRECTION".

      1. THEORY_SPECULATION same-show-SAME-QUESTION block: if format_type is
         THEORY_SPECULATION and a historical row shares `show` AND an exact
         match on the theory `question_line` (case-insensitive), the package
         is blocked UNLESS it carries a well-formed revisit_justification
         (new_evidence_summary, new_evidence_source_url, new_evidence_date
         all present and non-empty) -- mirrors Law #160 Decision 4 exactly.
      2. Same-show date-window blackout (documented formats only): a
         historical row with a matching `show` (case-insensitive) whose
         date_sent falls within the format-specific window
         (FORMAT_BLACKOUT_DAYS) blocks, regardless of angle similarity --
         the existing documented rule, now actually enforced. Formats with
         no entry in FORMAT_BLACKOUT_DAYS never use this signal; see #3.
      3. Same-show angle-similarity OR shared-entity signal, independent of
         date: for a historical row with a matching `show`, within
         UNDOCUMENTED_FORMAT_SEARCH_WINDOW_DAYS of the candidate's post_date
         (or with no post_date on either side, unbounded), EITHER of two
         independent, equal-weight checks blocks:
           (a) angle-similarity: `angle` text is >= ANGLE_SIMILARITY_
               THRESHOLD similar (difflib.SequenceMatcher ratio) to this
               package's `angle`.
           (b) shared-entity: both angles share at least one proper noun
               (character/place name) AND an exact chapter/episode number
               match (see _shared_entity_signal). Added after backtesting
               showed (a) alone scores only 0.26 on the real F43 Gaban
               pair -- text-sequence similarity cannot catch heavily-
               paraphrased same-event repeats.
         These are the ONLY signals used for the 10 undocumented formats (no
         date-window block for them at all, per the corrected design), and
         they also run for documented formats as a second, independent
         check beyond their date window -- closing F43's "one honest caveat
         on scope" (a date window alone would not have caught the real
         Ch.1190 Gaban repeat on day 8+). Different shows are never
         compared by either signal (cross-show phrasing/character overlap
         on shared anime tropes is not the documented failure mode and
         risks false positives). Named limitation: a same-event repeat
         sharing neither a proper noun nor an extractable chapter/episode
         number in either angle is not caught by either signal.
      4. No match on any signal -> clear.

    Returns a dict: {"blocked": bool, "reason": str | None,
    "matched_batch_id": str | None, "signal": str | None}. The "signal"
    field names which precedence tier fired, for testability and for the
    validator's error message.

    A package's own self-attested `recent_send_conflict`/`blackout_conflict`
    fields are NOT read here -- this function is the independent mechanical
    check the validator compares the attestation against; see item #3+#8's
    design (the validator hard-fails if this function blocks regardless of
    what the package attests).
    """
    show = pkg.get("show")
    if not isinstance(show, str) or not show.strip():
        return {"blocked": False, "reason": None, "matched_batch_id": None, "signal": None}
    rows = history if history is not None else _load_send_history(tree)
    excluded = _excluded_batch_ids(pkg)
    same_show = [r for r in rows
                 if isinstance(r.get("show"), str)
                 and r["show"].strip().lower() == show.strip().lower()
                 and r.get("batch_id") not in excluded]
    if not same_show:
        return {"blocked": False, "reason": None, "matched_batch_id": None, "signal": None}

    format_type = pkg.get("format_type")

    # Precedence 1: THEORY_SPECULATION same-question block.
    if format_type == THEORY_SPECULATION_FORMAT:
        question = pkg.get("question_line")
        if isinstance(question, str) and question.strip():
            q_norm = question.strip().lower()
            for row in same_show:
                row_q = row.get("question_line")
                if isinstance(row_q, str) and row_q.strip().lower() == q_norm:
                    rj = pkg.get("revisit_justification")
                    well_formed = (
                        isinstance(rj, dict)
                        and isinstance(rj.get("new_evidence_summary"), str) and rj.get("new_evidence_summary").strip()
                        and isinstance(rj.get("new_evidence_source_url"), str) and rj.get("new_evidence_source_url").strip()
                        and isinstance(rj.get("new_evidence_date"), str) and rj.get("new_evidence_date").strip()
                    )
                    if well_formed:
                        continue  # this specific historical match is excused; keep scanning others
                    return {"blocked": True,
                            "reason": f"same show+question already sent ({row.get('batch_id')}), "
                                      "no well-formed revisit_justification",
                            "matched_batch_id": row.get("batch_id"), "signal": "theory_same_question"}

    # Precedence 2: same-show date-window blackout (documented formats only).
    window_days = FORMAT_BLACKOUT_DAYS.get(format_type)
    pkg_post_date = _parse_date(pkg.get("post_date"))
    if window_days is not None and window_days > 0 and pkg_post_date is not None:
        for row in same_show:
            row_date = _parse_date(row.get("date_sent")) or _parse_date(row.get("post_date"))
            if row_date is None:
                continue
            if 0 <= (pkg_post_date - row_date).days < window_days:
                return {"blocked": True,
                        "reason": f"same show sent {(pkg_post_date - row_date).days}d ago, "
                                  f"inside {window_days}d blackout for format {format_type!r}",
                        "matched_batch_id": row.get("batch_id"), "signal": "date_window_blackout"}

    # Precedence 3: same-show angle-similarity OR shared-entity signal,
    # independent of date. Bounded by the loose search window ONLY when both
    # dates are known; otherwise runs unbounded (a missing date must never
    # silently skip either signal -- see EdgeCases tests). The two signals
    # are independent and equal-weight (THIRD DESIGN CORRECTION): either
    # firing is a hard block.
    angle = pkg.get("angle")
    if isinstance(angle, str) and angle.strip():
        angle_norm = angle.strip()
        for row in same_show:
            row_angle = row.get("angle")
            if not isinstance(row_angle, str) or not row_angle.strip():
                continue
            row_date = _parse_date(row.get("date_sent")) or _parse_date(row.get("post_date"))
            if pkg_post_date is not None and row_date is not None:
                age_days = (pkg_post_date - row_date).days
                if age_days < 0 or age_days > UNDOCUMENTED_FORMAT_SEARCH_WINDOW_DAYS:
                    continue
            row_angle_norm = row_angle.strip()
            ratio = difflib.SequenceMatcher(None, angle_norm.lower(),
                                             row_angle_norm.lower()).ratio()
            if ratio >= ANGLE_SIMILARITY_THRESHOLD:
                return {"blocked": True,
                        "reason": f"same show, angle similarity {ratio:.2f} >= "
                                  f"{ANGLE_SIMILARITY_THRESHOLD} vs already-sent "
                                  f"{row.get('batch_id')}",
                        "matched_batch_id": row.get("batch_id"), "signal": "angle_similarity"}
            if _shared_entity_signal(angle_norm, row_angle_norm):
                return {"blocked": True,
                        "reason": "same show, shared named entity + matching "
                                  f"chapter/episode number vs already-sent {row.get('batch_id')}",
                        "matched_batch_id": row.get("batch_id"), "signal": "shared_entity"}

    return {"blocked": False, "reason": None, "matched_batch_id": None, "signal": None}

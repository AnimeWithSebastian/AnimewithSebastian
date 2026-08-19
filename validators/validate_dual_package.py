#!/usr/bin/env python3
"""Deterministic preflight validator for the combined daily DUAL-PACKAGE run.

The daily cron (cron_daily_runtime.txt) produces ONE run manifest describing BOTH
the next-day MORNING and EVENING Shorts packages, then calls this validator BEFORE
sending any email. The validator is fully deterministic: no model, no network. It
exists so routine mechanical problems (short VO, missing CTA, duplicate show, face
direction, per-cut timing, wrong recipient, too few sources, ...) are caught and
fixed without a model-based revision loop.

FAIL CLOSED: if any check fails the process exits non-zero and the cron MUST NOT
send either email. Success (exit 0) means both packages are mechanically clean and
the run may proceed to send the two plain-text emails.

Usage:
    python3 validators/validate_dual_package.py <run_manifest.json>
    python3 validators/validate_dual_package.py --schema      # print manifest schema

The manifest keeps the recipient email SHORT: it carries only actionable production
content plus concise source evidence. Compliance matrices, search logs, model
routing and audit boilerplate live in the run manifest / internal logs, NOT in the
email body. This validator enforces the mechanical laws against the manifest so the
email does not need to carry the audit.
"""

from __future__ import annotations

import json
import os
import re
import sys

# The clip-description location-surfacing helper lives in the sibling tools/
# directory (same cross-directory import pattern tools/append_send_batch.py
# already uses in reverse to reach this validators/ package).
_TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
try:
    from render_clip_descriptions import _extract_location_tokens, _split_into_cut_segments
except Exception:  # noqa: BLE001 — degrade to "check cannot run", never crash import
    _extract_location_tokens = None
    _split_into_cut_segments = None
from dataclasses import dataclass, field
from typing import Any

RECIPIENT = "hero_or_villain@outlook.com"
CTA_EXACT = "Leave your take."
VO_MIN, VO_MAX, VO_TARGET = 100, 108, 104

# Evidence-based Shorts packaging & attribution (Laws #143-#145). Grounded in the
# channel's own analytics (timely > evergreen; clean/no-hashtag titles outperformed;
# recurring structures like seasonal ranking + episode/scene tests over-performed;
# 0 "regular viewers" = a returning-viewer gap) AND official YouTube guidance
# (search ranks on title/description/content match; tags/hashtags not a reach lever;
# relative watch time + replays dominate Shorts; deceptive packaging discouraged).
TOPIC_CLASSES = ("timely", "evergreen")
TIMELY_SIGNALS = ("currently_airing", "premiere", "chapter", "news", "seasonal_ranking")
FUNNEL_STATUSES = ("standalone", "teaser", "flagship_followup")

# Controlled format_type vocabulary (Law #85's monetization hierarchy + Law #96's
# rotation formats + Law #98's WATCH_RANK — ported into cron_daily_runtime.txt Step 3
# alongside this check; see that file for the restoration note). Free-text or compound
# labels ("industry controversy hybrid", "SEASON_PREVIEW / dub-cast reveal") are no
# longer permitted — every package must declare exactly one of these 17 tokens. Only
# WATCH_RANK is ported from Law #98; that law's other three codes (SEASON_RANK,
# EPISODE_REVIEW, EPISODE_VS_MANGA) remain unported and are deliberately excluded here.
# CLARIFYING CORRECTION to Law #85's own text: Law #85 rank 8 is written as one
# combined format "SLEPT_ON / HIDDEN_GEM", but real production history
# (sent_scripts_log.json) used SLEPT_ON and HIDDEN_GEM as two distinct format_type
# strings. Both are kept as separate tokens here to match actual usage rather than
# the law's combined phrasing — the law text itself should be corrected to reflect
# this the next time law_85_monetization_first.md is touched.
# Law #158/#159 (added 2026-08-10, design proposal turn 840): WORTH_WATCHING
# (single-show persuasion, no ranking) and SEASON_ROUNDUP (multi-show premiere
# roundup) are the 15th/16th tokens. SEASON_ROUNDUP formally retires the legacy,
# pre-enum UPCOMING_HYPE / HYPE_PREVIEW strings still visible in sent_scripts_log.json
# history (6 and 2 real sends respectively) — those two strings are intentionally NOT
# added here and remain correctly rejected by the check below; see law_159 for the
# full retirement rationale.
FORMAT_TYPES = (
    # Law #85 monetization hierarchy (rank 8 split into its two real-world tokens —
    # see clarifying correction above — so this is 9 tokens covering 8 ranks)
    "WRONG_TAKE", "CHARACTER_DIVE", "THE_MOMENT", "FACT_DROP",
    "COMMENTARY", "VILLAIN_DEFENSE", "ORIGIN_STORY", "SLEPT_ON", "HIDDEN_GEM",
    # Law #96 rotation (4)
    "SEASON_RATING", "SEASON_PREVIEW", "MANGA_VS_ANIME", "EPISODE_MOMENT",
    # Law #98 (1 of 4 codes ported)
    "WATCH_RANK",
    # Law #158 (single-show persuasion, no ranking)
    "WORTH_WATCHING",
    # Law #159 (multi-show roundup; retires legacy UPCOMING_HYPE/HYPE_PREVIEW)
    "SEASON_ROUNDUP",
    # Law #160 (evidence-governed, conclusion-hedged theory content)
    "THEORY_SPECULATION",
)  # 17 tokens total

# Punchy title packaging (Law #144, revised July 2026 on production feedback: YouTube
# and TikTok titles were running too long; punchier titles that stand out convert
# better). HARD maxima are enforced fail-closed; the preferred TARGET bands are
# documented guidance the model aims for but the validator does not fail on (a title
# inside the hard cap but above the preferred band still passes).
YT_TITLE_MAX = 60          # YouTube title HARD maximum, chars incl. spaces
YT_TITLE_TARGET = (35, 50) # preferred band (guidance only, not enforced)
TT_TITLE_MAX = 55          # TikTok title HARD maximum, chars incl. spaces
TT_TITLE_TARGET = (30, 45) # preferred band (guidance only, not enforced)
TITLE_MAX = YT_TITLE_MAX   # back-compat alias (YouTube cap)

# Law #140 (supersedes the prior no-timings preference): every CapCut clip plan MUST
# carry per-cut timing. The DEFAULT fixed edit is exactly 30 seconds and the cut
# timeline must tile it contiguously.
CAPCUT_TARGET_SEC = 30

# STAGE 1 REBUILD (2026-08-09, face-cam + variable-length permanent decision):
# the old M1 "list/ranking recurring-series only, 45-59s" experiment gate is retired.
# Variable length up to the real YouTube Shorts ceiling (3 min / 180s, confirmed via
# https://support.google.com/youtube/answer/15424877) is now the PERMANENT default
# framework, not a rare opt-in. EXPERIMENT_MIN_SEC/EXPERIMENT_MAX_SEC are kept only as
# the legacy floor/ceiling constant NAMES for any old fixture/manifest that still reads
# them; MIN_EDIT_SEC/MAX_EDIT_SEC below are the real bounds going forward.
EXPERIMENT_MIN_SEC = 45
EXPERIMENT_MAX_SEC = 59
MIN_EDIT_SEC = 20.0
MAX_EDIT_SEC = 180.0
VO_WPS_MIN = VO_MIN / CAPCUT_TARGET_SEC   # 3.333.. words/sec (yields 100 at 30s)
VO_WPS_MAX = VO_MAX / CAPCUT_TARGET_SEC   # 3.6 words/sec (yields 108 at 30s)

TOL = 1e-6

# Common filler/stopwords that must not be selected as the show's search keyword
# (Law #148-adjacent fix, July 2026): many anime titles start with "The"/"A"/etc.,
# and picking the FIRST word >=3 chars with no stopword filter made the
# "show search keyword appears early in title" check trivially true for almost any
# title beginning with one of these words. Filtering them out forces the check to
# land on an actual content word from the show name.
TITLE_STOPWORDS = frozenset({
    "the", "a", "an", "my", "her", "his", "one", "two", "of", "in", "to",
    "are", "is", "not", "and", "or", "for", "on", "at", "as", "but", "you",
})

# STAGE 1 REBUILD (2026-08-09) NOTE: this constant's name is legacy and its ORIGINAL
# meaning ("these tokens are banned") is INVERTED today — face-cam split screen is now
# the REQUIRED default Shorts format (Law #134 Stage 2), so these tokens are what
# video_style is now required to contain, not banned from containing. Retained only so
# any downstream code/tests still importing the name keep working; it is NOT used
# below to fail a package on these tokens' presence. See the real, current enforcement
# in validate_package() ("face flag is true" / "split_screen flag is true" / "video_style
# declares the face-cam split-screen format" checks). This comment previously read
# "Face / split-screen signals banned for Shorts (anime footage only)", which was
# itself a stale, incorrect description of current behavior — fixed 2026-08-10
# alongside the Law #139/#140/#144/#73/#103 anime-only text corrections.
BANNED_STYLE_TOKENS = ("face", "facecam", "face cam", "face inset", "inset", "split screen", "split-screen")
BANNED_CTA = ("drop it.", "drop your take.", "like and comment", "what do you think")

# Law #158 (WORTH_WATCHING, added 2026-08-10; TIGHTENED 2026-08-10 same-day fix after
# adversarial testing): comparative/ranking language is banned by this format's own
# definition, not merely absent as a field. Checked (for WORTH_WATCHING packages only)
# against vo, hook_line, hook_onscreen_text, youtube_title, tiktok_title, and
# tiktok_post_text. Mirrors BANNED_CTA's enumerated-pattern approach (same discipline
# as Law #149 point 9's checkable pattern list, not a vibe-based judgment call).
#
# FIRST-DRAFT BUG (caught in review, never shipped): the original version of this
# constant was a tuple of BARE SUBSTRINGS, including "beats" and "over " unscoped.
# That is too broad -- "the hero beats the villain in the final chapter" is ordinary
# in-story plot narration, not a comparative-ranking claim about the show itself, and
# "over " as a bare substring fires on "changes over time", "all over again", "hands
# it over", and "the story picks up over the summer". Adversarial testing (see
# TestWorthWatchingComparativeLanguageLaw158's adversarial cases) confirmed both would
# have produced real false positives in production VO. Replaced with REGEX PATTERNS,
# each anchored to the actual comparative/ranking construction rather than a bare
# substring:
#   - "beats"/"beat it" are scoped to an explicit ranking frame ("beats every/all/the
#     other/other/any other [show]", or "beat(s) it" as a direct pronoun-object
#     ranking claim) so ordinary plot narration ("beats the villain") does not match.
#   - "over" is scoped to an explicit comparison-target phrase immediately following
#     it ("over anything else", "over everything else", "over the rest", "over the
#     competition", "over every other", "over any other", "over that other", "over
#     those other") so time/manner uses ("over time", "over the summer", "over the
#     weekend", "thinks it over") do not match.
# This is a curated, non-exhaustive pattern list (same limitation the original
# substring approach had) -- it catches the confirmed real construction, not every
# conceivable comparative phrasing. Each pattern is applied with re.IGNORECASE.
BANNED_COMPARATIVE_LANGUAGE = (
    r"\bbetter than\b",
    r"\bworse than\b",
    r"\bbeats (every|all|the other|other|any other)\b",
    r"\bbeats? it\b",
    r"\bloses to\b",
    r"\blost to\b",
    r"\bover (anything else|everything else|the rest|the competition|every other|any other|that other|those other)\b",
    r"#1\b",
    r"\bnumber one\b",
    r"\btop pick\b",
    r"\boutranks\b",
    r"\boutranked\b",
)

# Law #160 (THEORY_SPECULATION): the core theoretical claim gets a MANDATORY MINIMUM
# HEDGE FLOOR, the inverse of Law #158's banned-language approach -- here a required
# phrase must be PRESENT, not absent. This is the named, explicitly-scoped exception
# to the project's dominant no-hedging rule. Scoped ONLY to `theory_claim_line` --
# every other VO line in a THEORY_SPECULATION package still follows the normal
# no-hedging confidence rules. Extends the existing Law #149 point 3 principle
# ("hedge strength must match source confidence") rather than inventing hedging as a
# new concept. Curated, non-exhaustive phrase list (same documented limitation
# BANNED_COMPARATIVE_LANGUAGE itself carries).
REQUIRED_THEORY_HEDGES = (
    "this theory suggests",
    "one likely explanation",
    "the evidence points to",
    "this may explain",
    "a strong possibility is",
    "this could mean",
    "the working theory here is",
    "it's possible that",
    "this points toward",
    "the leading theory is",
)

# Law #160 (THEORY_SPECULATION): certainty language banned from `theory_claim_line`
# specifically -- mirrors BANNED_COMPARATIVE_LANGUAGE's anchored-regex discipline
# rather than bare substrings. Anchored so it does NOT fire on legitimate evidence-
# tier sourcing language describing a confirmed SOURCE fact (e.g. "the official site
# confirmed the air date") -- the ban applies only to the THEORY claim asserting
# itself as settled.
BANNED_THEORY_CERTAINTY_LANGUAGE = (
    r"\bthis is what happened\b",
    r"\bthe confirmed answer is\b",
    r"\bthis is confirmed\b",
    r"\bwe now know\b",
    r"\bthis proves\b",
    r"\bthe fact is this is\b",
    r"\bthere's no doubt this is\b",
)

# Law #160 (THEORY_SPECULATION, DRAFT/PROPOSED -- fix applied 2026-08-11, found during
# user review): the original Decision 3 credit check matched the BARE word "theory"
# anywhere in vo/pinned_comment/tiktok_post_text. That is vacuous: theory_claim_line is
# itself part of vo, and several REQUIRED_THEORY_HEDGES phrases already contain the word
# "theory" ("this theory suggests", "the working theory here is", "the leading theory
# is") -- so the mandatory hedge floor (Decision 2) would satisfy the bare-word credit
# check on its own, with zero connection to whether an existing theory is actually
# credited. A package could pass Decision 3 while never once acknowledging that a prior
# fan theory exists -- the exact failure mode Decision 3 exists to prevent. Fixed by
# requiring a real attribution cue: either a subject+attribution-verb construction
# ("fans believe", "viewers think", "theorists suggest", etc.) or a determiner+theory
# noun phrase ("a popular theory", "the existing theory", "a fan theory", etc.) or a
# theorize/theorist/theorizing form -- none of which any REQUIRED_THEORY_HEDGES phrase
# satisfies on its own (verified: all 10 hedge phrases individually fail this pattern).
CREDIT_ATTRIBUTION_PATTERN = re.compile(
    r"("
    r"\b(fans?|viewers?|people|many|some|others|theorists)\b[^.?!]{0,40}\b"
    r"(believe[sd]?|think|thought|say[s]?|said|argue[sd]?|suggest(?:s|ed)?|hold[s]?|theorized?)\b"
    r"|\b(a|an|the|another|one)\s+(popular\s+|existing\s+|fan\s+|prior\s+)?(fan\s+)?theory\b"
    r"|\btheor(?:ized|ists?|izing)\b"
    r")",
    re.IGNORECASE,
)

# Encyclopedic/aggregator sources that MUST NOT be the SOLE support for a core claim
# (they are tertiary and frequently stale/edited). A core claim may cite them, but it
# also needs at least one non-encyclopedic dated source. This is a MECHANICAL domain
# check on the self-audited claim-to-source matrix — it does NOT prove the claim true.
ENCYCLOPEDIC_DOMAINS = ("wikipedia.org", "myanimelist.net", "wikia.com", "fandom.com")

# Law #58's six claim types (restored per user decision, July 24 2026 policy review).
# Types B (creator quotes/interviews) and E (cross-show connections) are the highest-
# risk categories -- Law #58 requires 2 sources minimum for these, with at least one
# NON-ENCYCLOPEDIC source standing in for the "named, credible" requirement (a wiki/
# aggregator citation alone cannot satisfy a claim about what a real person said or an
# unconfirmed cross-show influence). Types A/C/D/F keep the flat >=1 non-encyclopedic
# dated source rule already enforced below.
CLAIM_TYPES = ("A", "B", "C", "D", "E", "F")
HIGH_RISK_CLAIM_TYPES = ("B", "E")

# The daily generation context must SELF-AUDIT both packages before returning and record
# the audit in the manifest (NOT the slim email). The validator checks the audit is
# PRESENT and well-SHAPED and that the claim-to-source matrix has the mechanical
# properties below; it explicitly does NOT claim to verify source truth or semantic
# quality — those stay with the model attestation + weekly human spot-check.
# Law #148/#150 production-audit findings (added 2026-07-25, closes a real gap found
# reviewing a sent manifest): 1.5 requires the hook's and the loop's own core claims to
# be individually traceable in the matrix (not just "a core claim exists somewhere");
# 1.6 is a self-attestation, same pattern as the other five, since checking arbitrary
# VO arithmetic against arbitrary source text is a judgment call the validator cannot
# perform mechanically -- it is enforced the same way blackout_recent_conflicts etc.
# already are: presence/shape only, truth verified by the model attestation + weekly
# human spot-check (M6).
SEMANTIC_QA_CHECK_KEYS = (
    "vo_word_count",
    "cta_adjacency",
    "title_search",
    "blackout_recent_conflicts",
    "clip_timing_tiling",
    "hook_claim_coverage",  # renamed from hook_loop_claim_coverage (2026-07-27):
                             # the loop half was rescinded, this is hook-only now (Law
                             # #141 rescission -- see laws/law_141_seamless_loop_mechanics.md)
    "numeric_cross_check",
    "source_content_verification",  # runtime STEP 4.5 point 1.7, added 2026-07-26 (9ad62a1) --
                                     # backfilled here 2026-07-26; validator sync was deferred at
                                     # commit time per that commit's own message.
    "law_149_redundancy_check",     # runtime STEP 4.5 point 8, added 2026-07-26 (9ad62a1) --
                                     # backfilled here 2026-07-26, same deferred-sync reason.
    "ai_slop_pattern_check",        # runtime STEP 4.5 point 9, added 2026-07-26 (this change) --
                                     # seven named hollow-phrasing patterns distinct from point 8's
                                     # literal-restatement-only check.
)

# --- VO-dependent vs VO-independent semantic_qa keys (2026-08-16, VO handoff) ----
# Under the handoff workflow Perplexity does NOT write the VO; it hands validated
# facts to Claude, who writes it. Between those two steps a package legitimately has
# no VO, so the five checks below cannot be evaluated -- they are SKIPPED, never
# assumed. The other five are fully evaluable without a VO and still run for real.
#
# VO_INDEPENDENT is computed by SET SUBTRACTION from the live SEMANTIC_QA_CHECK_KEYS
# tuple rather than being written out by hand: if a key is ever added to that tuple
# and not classified here, it lands in VO_INDEPENDENT and is therefore still ENFORCED
# rather than silently skipped -- the fail-closed direction.
VO_DEPENDENT_QA_KEYS = (
    "vo_word_count",            # counts words in a VO that does not exist yet
    "cta_adjacency",            # CTA placement inside the VO
    "hook_claim_coverage",      # the hook line is part of the VO
    "numeric_cross_check",      # verifies counts as spoken in the VO
    "ai_slop_pattern_check",    # scans VO phrasing
)
VO_INDEPENDENT_QA_KEYS = tuple(
    k for k in SEMANTIC_QA_CHECK_KEYS if k not in VO_DEPENDENT_QA_KEYS
)
assert len(VO_DEPENDENT_QA_KEYS) + len(VO_INDEPENDENT_QA_KEYS) == len(SEMANTIC_QA_CHECK_KEYS)

# vo_status values. Default is "complete" so every pre-existing manifest keeps its
# current meaning and full enforcement -- the new draft stage is strictly opt-in.
VO_STATUS_VALUES = ("pending", "complete")
VO_STATUS_DEFAULT = "complete"


# claim_source_matrix entries that anchor the hook must say so via this field so 1.5
# (hook claim coverage) is mechanically checkable, not merely self-attested.
# NOTE (2026-07-27): previously also covered "loop" -- removed when the forced
# seamless-loop mandate was rescinded (Law #141 rescission). "loop" is no longer a
# meaningful anchor type, but a package MAY still tag an entry anchors_claim="loop"
# harmlessly; nothing reads or requires it anymore.
ANCHOR_TYPES = ("hook",)

# Law #73 UPDATE 8 (added 2026-08-10, same-day fix after the Re:ZERO / Love Unseen
# footage-location correction incident -- docs/KNOWN_ISSUES.md F21 context, laws/
# law_73_clip_verification.md): the F20 fallback (manga_reference OR a bare
# verification_note) let BOTH corrected packages ship tonight with footage that was
# never actually located -- verification_note is a pure self-attestation with no
# mechanical floor, so a copy-pasted or vague note satisfied it exactly as well as a
# real, failed search attempt. footage_status/footage_search_performed/
# location_pointer close that gap for every scene_verified=false clip. This is
# ADDITIVE to F20, not a replacement of it: manga_reference/verification_note keep
# their existing meaning and existing check (line ~575 below) untouched; these three
# new fields are a second, independent layer of enforcement scoped to the same
# scene_verified=false clips.
#
# FOOTAGE_SEARCH_DOMAINS: a curated, non-exhaustive list of recognizable video-platform
# hosts/names used as the mechanical floor for footage_search_performed (decision 2).
# Matched case-insensitively as a bare substring against the free-text search-summary
# string -- deliberately permissive on FORMAT (a full URL, a bare domain mention, or a
# platform name written in prose like "searched Crunchyroll and YouTube" all match) but
# strict on SUBSTANCE (the string must actually name a real video platform somewhere;
# an empty string, whitespace, or platform-agnostic filler like "searched around for
# footage" does not match any pattern here and is correctly rejected). Same curated-list
# limitation BANNED_COMPARATIVE_LANGUAGE and ENCYCLOPEDIC_DOMAINS already carry --
# extend this list if a real search legitimately used a platform not yet named here.
FOOTAGE_SEARCH_DOMAINS = (
    "youtube", "youtu.be", "crunchyroll", "funimation", "hidive", "ani-one",
    "aniplus", "netflix", "hulu", "amazon", "primevideo", "disneyplus", "disney+",
    "bilibili", "niconico", "muse asia", "museasia", "toei", "tiktok", "instagram",
    "twitter.com", "x.com", "facebook",
)

# footage_status enum (decision 1). aired_not_located is the hard-blocking value --
# a clip that has aired but for which no clip-level video source could be located is
# NOT an acceptable third state to ship silently under this new layer, even though
# F20's own manga_reference/verification_note check (unchanged, see below) may still
# separately pass the same clip. unaired_trailer_only and unaired_no_footage are the
# two honest "nothing to locate yet" states for not-yet-aired content (trailer-only
# grounding belongs to Law #159's separate trailer_reference mechanism when the
# format_type is SEASON_ROUNDUP; for every other format_type these two values simply
# document why no clip-level video source exists yet). aired_and_located is the only
# fully-cleared state.
FOOTAGE_STATUS_VALUES = (
    "aired_and_located",
    "aired_not_located",
    "unaired_trailer_only",
    "unaired_no_footage",
)
FOOTAGE_STATUS_HARD_BLOCK = ("aired_not_located",)


# --- check status vocabulary (added 2026-08-16, VO-handoff workflow) ------------
# Result.checks[1] is one of these THREE strings, replacing the old bool. SKIP exists
# because a VO-pending package cannot evaluate its VO-dependent checks yet; folding
# that into PASS would make a draft manifest look sendable, and folding it into FAIL
# would make the normal draft stage look broken.
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"

@dataclass
class Result:
    """A list of (name, status, detail) checks.

    STATUS IS A STRING, NOT A BOOL (changed 2026-08-16 for the VO-handoff workflow).
    checks[1] is one of STATUS_PASS / STATUS_FAIL / STATUS_SKIP. The third state is
    required because a VO-pending package legitimately cannot evaluate its VO-dependent
    checks yet -- and "cannot evaluate yet" is neither a pass nor a failure. Collapsing
    it into either one is what makes a draft-stage manifest look sendable.

    CALLERS BEWARE: any code doing `if not ok` over these tuples is now WRONG, because
    every non-empty string is truthy -- `not "FAIL"` and `not "PASS"` are both False.
    Compare explicitly against STATUS_FAIL / STATUS_SKIP. This exact bug existed in
    tools/append_send_batch.py's validate_manifest_failures() and would have silently
    reported zero failures for every manifest; see that file's dated fix note.
    """

    checks: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, STATUS_PASS if ok else STATUS_FAIL, detail))

    def skip(self, name: str, detail: str = "") -> None:
        """Record a check that could not be evaluated yet (VO not written).

        A skip is NOT a pass. `fully_passed` -- the real send/approval gate -- is
        False whenever any skip is present.
        """
        self.checks.append((name, STATUS_SKIP, detail))

    @property
    def ok(self) -> bool:
        """PERMISSIVE: zero FAILs. Skips do NOT count against it.

        Kept for backward compatibility with existing callers and tests. This is
        deliberately NOT the send gate -- a VO-pending manifest is `ok` while still
        carrying unevaluated checks. Use `fully_passed` to gate a send or an approval.
        """
        return all(status != STATUS_FAIL for _, status, _ in self.checks)

    @property
    def fully_passed(self) -> bool:
        """THE REAL GATE: zero FAILs AND zero SKIPs -- every check actually evaluated
        and actually passed. This is what clears AWAITING_APPROVAL or a send."""
        return all(status == STATUS_PASS for _, status, _ in self.checks)

    def failures(self) -> list[tuple[str, str, str]]:
        return [c for c in self.checks if c[1] == STATUS_FAIL]

    def skips(self) -> list[tuple[str, str, str]]:
        return [c for c in self.checks if c[1] == STATUS_SKIP]


def _vo_status(pkg: dict[str, Any]) -> str:
    """Read a package's vo_status, defaulting to "complete".

    Defaulting to "complete" (not "pending") is deliberate and fail-closed: every
    manifest written before this field existed keeps FULL enforcement. Only a package
    that explicitly opts in to "pending" gets VO-dependent checks skipped.
    """
    raw = pkg.get("vo_status", VO_STATUS_DEFAULT)
    return raw if isinstance(raw, str) else raw


def _vo_is_pending(pkg: dict[str, Any]) -> bool:
    """True only when vo_status is exactly "pending".

    A malformed vo_status returns False, so the package keeps full enforcement AND
    separately fails the vo_status-is-valid check -- it can never buy skips by being
    malformed.
    """
    return _vo_status(pkg) == "pending"


def _words(text: str) -> int:
    # \w alone would drop apostrophes ("doesn't" -> "doesn"+"t", two words instead
    # of one) -- explicitly including ' alongside \w fixes the Unicode/accent case
    # (Pokémon = 1 word, not "Pok"+"mon") WITHOUT breaking contraction counting,
    # which the original [A-Za-z0-9']+ handled correctly.
    return len(re.findall(r"[\w']+", text or ""))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


# F15 fix (docs/KNOWN_ISSUES.md, 2026-07-25 finding / 2026-07-25 fix): a malformed
# manifest can put a non-string value (int, bool, list, dict) on any of ~19 fields
# that downstream code assumed were always strings/lists and fed directly into
# str-only ops (.strip(), .lower(), re.findall()) or list-only ops (len(), iteration).
# That raised an unhandled AttributeError/TypeError instead of a clean named check
# failure, defeating the validator's fail-closed purpose. These typed getters coerce
# to a safe default instead of raising, matching the exact remediation approach
# KNOWN_ISSUES.md proposed. Behavior for already-valid (correctly-typed) input is
# unchanged -- this only changes what happens on already-malformed input that used to
# crash the validator itself.
def _str(pkg: dict, key: str, default: str = "") -> str:
    v = pkg.get(key, default)
    return v if isinstance(v, str) else default


def _list(pkg: dict, key: str, default: tuple = ()) -> list:
    v = pkg.get(key, default)
    return list(v) if isinstance(v, list) else list(default)


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _vo_band(target_sec: float) -> tuple[int, int]:
    """VO word band for a given edit length, scaled from the 30s rule (Law #138).
    _vo_band(30) == (100, 108) exactly, so the default path is unchanged."""
    return (round(VO_WPS_MIN * target_sec), round(VO_WPS_MAX * target_sec))


def _resolve_edit_target(pkg: dict[str, Any], p: str, r: Result) -> tuple[float, bool]:
    """STAGE 1 REBUILD (2026-08-09): variable length up to the real Shorts ceiling is
    now the PERMANENT default framework, not a rare list/ranking-only opt-in. Return
    (target_sec, is_variable_length).

    Resolution order:
    1. If capcut_target_sec is absent entirely, fall back to the CAPCUT_TARGET_SEC
       (30s) default with is_variable_length=False -- this keeps every pre-existing
       simple/quick-take package that never set the field working unchanged.
    2. If capcut_target_sec is present, it MUST be numeric and inside
       [MIN_EDIT_SEC, MAX_EDIT_SEC] (20-180s). This is now an open per-content
       judgment call (Section 3 of the design plan: single-fact -> 20-30s,
       multi-beat -> 45-150s, full multi-claim explainer -> up to 180s) -- there is
       no format_type/series gate anymore. A package exactly at 30.0 is still
       reported as is_variable_length=False (the true legacy default), matching the
       overwhelming majority of real historical sends and keeping downstream
       reporting/analytics language ("is this an experiment?") meaningful.
    3. If capcut_target_sec is present but out of range or non-numeric, this FAILS
       CLOSED: the check is recorded as a failure and we still return the 30s
       default so every other check in this pass runs against a sane target_sec
       instead of crashing on garbage input -- but the run as a whole will not pass
       preflight because the failed check is in the Result.

    NOTE: the legacy field name `duration_experiment` and its per-batch cap are
    fully RETIRED (Stage 2, 2026-08-09) -- not merely unread. Variable length is
    now the unconditional default for every package, so there was no remaining
    "experiment" left to bound or flag. The field is no longer referenced anywhere
    in this validator; a manifest may still carry it as inert leftover data (old
    manifests are not rewritten), but it has zero effect on validation.
    """
    ct = pkg.get("capcut_target_sec")

    if ct is None:
        return float(CAPCUT_TARGET_SEC), False

    in_range = _is_num(ct) and MIN_EDIT_SEC <= ct <= MAX_EDIT_SEC
    r.add(f"{p} capcut_target_sec is numeric and within {int(MIN_EDIT_SEC)}-{int(MAX_EDIT_SEC)}s",
          in_range,
          f"capcut_target_sec={ct!r}; must be numeric in [{MIN_EDIT_SEC}, {MAX_EDIT_SEC}]")
    if not in_range:
        return float(CAPCUT_TARGET_SEC), False

    target = float(ct)
    return target, not (abs(target - CAPCUT_TARGET_SEC) < TOL)


# _loop_transition_ok() REMOVED (2026-07-27) -- the forced seamless-loop mandate
# (Law #141/#147) is rescinded; loop_transition/final_to_opening are no longer
# checked. See laws/law_141_seamless_loop_mechanics.md for the rescission text.


def _validate_clip_timeline(clips: list[Any], capcut_target: Any, target_sec: float,
                            p: str, r: Result) -> None:
    """Every cut must carry per-cut timing (Law #140). The cuts must tile the resolved
    edit contiguously: first starts at 0, each end == next start, last ends at the
    target, end-start == duration_sec, and the durations sum to capcut_target_sec.

    target_sec is whatever _resolve_edit_target returned for THIS package: its own
    capcut_target_sec anywhere in [MIN_EDIT_SEC, MAX_EDIT_SEC] (20-180s), falling back
    to CAPCUT_TARGET_SEC (30s) only when the field is absent entirely.

    [Docstring corrected 2026-08-14 during the Law #159 item 3 build. It previously read
    "target_sec is 30 by default, or the sanctioned experiment length (M1)". The M1
    list/ranking-only 45-59s duration experiment was RETIRED by the Stage 1/2 rebuild on
    2026-08-09, which made open-ended variable length the permanent default framework --
    there is no "experiment length" branch anymore. Stale comment, correct code: the
    implementation below already reads the resolved target and never referenced M1.]"""
    tgt = int(target_sec)
    have_fields = bool(clips) and all(
        isinstance(c, dict) and _is_num(c.get("duration_sec"))
        and _is_num(c.get("timeline_start_sec")) and _is_num(c.get("timeline_end_sec"))
        for c in clips
    )
    r.add(f"{p} each clip has duration_sec + timeline_start_sec + timeline_end_sec",
          have_fields, "every cut needs numeric duration_sec/timeline_start_sec/timeline_end_sec")
    if not have_fields:
        # downstream timeline checks cannot run without the numeric fields
        r.add(f"{p} clip timeline is contiguous 0->{tgt}s (no gaps/overlaps)",
              False, "missing per-cut timing fields")
        return

    r.add(f"{p} each clip duration_sec is positive",
          all(c["duration_sec"] > 0 for c in clips),
          f"durations={[c['duration_sec'] for c in clips]}")

    arithmetic = all(
        abs((c["timeline_end_sec"] - c["timeline_start_sec"]) - c["duration_sec"]) <= TOL
        for c in clips
    )
    r.add(f"{p} each clip: timeline_end_sec - timeline_start_sec == duration_sec",
          arithmetic,
          f"offenders={[i+1 for i, c in enumerate(clips) if abs((c['timeline_end_sec']-c['timeline_start_sec'])-c['duration_sec'])>TOL]}")

    contiguous = abs(clips[0]["timeline_start_sec"] - 0) <= TOL
    for a, b in zip(clips, clips[1:]):
        if abs(a["timeline_end_sec"] - b["timeline_start_sec"]) > TOL:
            contiguous = False
    r.add(f"{p} clip timeline is contiguous 0->{tgt}s (no gaps/overlaps)",
          contiguous,
          f"starts={[c['timeline_start_sec'] for c in clips]} ends={[c['timeline_end_sec'] for c in clips]}")

    r.add(f"{p} final clip ends at {tgt}s",
          abs(clips[-1]["timeline_end_sec"] - target_sec) <= TOL,
          f"final_end={clips[-1]['timeline_end_sec']}")

    total = sum(c["duration_sec"] for c in clips)
    tgt_ok = _is_num(capcut_target) and abs(capcut_target - target_sec) <= TOL
    r.add(f"{p} sum of clip durations == capcut_target_sec == {tgt}",
          tgt_ok and abs(total - target_sec) <= TOL,
          f"sum={total} capcut_target_sec={capcut_target}")


def _clip_locate_shape_ok(c: dict) -> bool:
    """Law #73 UPDATE 5 (2026-07-28): presence/shape check for clip_locate, required
    on every scene_verified=true clip, regardless of format_type. Extracted to module
    level 2026-08-10 (Law #158/#159 same-day fix) so _validate_clip_verification's
    anime path AND _validate_season_roundup_clip_sourcing's anime path share this
    EXACT same shape check -- previously this was a closure defined only inside
    _validate_clip_verification, so the SEASON_ROUNDUP path had no clip_locate
    enforcement at all for its anime-sourced clips (a real gap, not a design choice;
    fixed here rather than duplicating the logic, which would risk drift between the
    two copies). locate_confirmed_via must be a descriptive sentence referring back to
    the same source already cited in claim_vs_source_check (e.g. "the same Anime News
    Network episode 16 review cited above") -- never a bare URL. A bare URL both
    violates the field's own spec (a URL is not "one sentence" naming how the source
    establishes the episode) and silently defeats the episode-token cross-check
    (URL slugs match the episode-number regex inconsistently depending on whether they
    use spaces, hyphens, or underscores -- an accidental non-match, not a real scope
    boundary).
    """
    cl = c.get("clip_locate")
    if not isinstance(cl, dict):
        return False
    season_ok = isinstance(cl.get("season"), (int, str)) and cl.get("season") != ""
    episode_ok = isinstance(cl.get("episode"), int) and not isinstance(cl.get("episode"), bool)
    locate_via = cl.get("locate_confirmed_via")
    locate_via_ok = (
        isinstance(locate_via, str)
        and locate_via.strip() != ""
        and not locate_via.strip().lower().startswith(("http://", "https://"))
    )
    ts = cl.get("approx_timestamp")
    ts_ok = ts is None or (isinstance(ts, str) and ts.strip() != "")

    # episode_source (Law #167, added 2026-08-13): mirrors Law #73 UPDATE 8's
    # footage_status disclosure pattern -- an explicit, self-attested flag on
    # HOW the episode number was determined, not an independent truth check
    # (the validator cannot verify this any more than it can verify
    # claim_vs_source_check's content -- see that check's own documented
    # limitation above). "explicitly_stated" means the source text names the
    # episode number directly (a review, an official episode list, an on-
    # screen episode card); "inferred" means the episode number was worked
    # out from other evidence (air-date ordering, a recap's own numbering,
    # context) rather than a source directly stating it. Both are legitimate
    # provided the field is present and honestly one of the two values --
    # this is a disclosure requirement, not a preference for one value over
    # the other.
    episode_source = cl.get("episode_source")
    episode_source_ok = episode_source in ("explicitly_stated", "inferred")

    return season_ok and episode_ok and locate_via_ok and ts_ok and episode_source_ok


def _validate_clip_verification(clips: list[Any], pkg: dict[str, Any], p: str, r: Result) -> None:
    """Law #73 (restored and extended for daily_combined, July 25, 2026): every
    clips[] entry must be checked against three dimensions -- AIRED, ACCURATE,
    CURRENTLY AVAILABLE -- with a named scene-level source, not show-level or
    arc-level sourcing.

    BOTTOM-HALF-ONLY SCOPING (Law #73 UPDATE 7, added 2026-08-09, face-cam +
    variable-length permanent decision): this function validates ONLY the
    pkg["clips"] array, which under the new face-cam split-screen format
    (creator TOP / anime footage BOTTOM, per Sebastian's confirmed decision)
    represents the BOTTOM-HALF anime footage track exclusively. It has never had,
    and still does not have, any awareness of a top-half creator-on-camera track --
    it takes a bare `clips` list and a `pkg` dict and never reads any field that
    would represent live creator performance (there is no such field in the schema
    yet; that is Stage 3 scope). This means the scoping decision made here is
    almost entirely definitional/documentary, not a code change: Law #73's chain
    (scene_verified, verification_source_url, claim_vs_source_check, clip_locate,
    manga_reference/verification_note, story_point_gate, clip_plan_needs_*_flags)
    continues to apply, completely unchanged, to every entry in clips[]. It
    EXPLICITLY DOES NOT extend to, and must never be made to require, anything
    from a future top-half creator track -- unscripted, on-camera creator
    performance is not sourced from an external show and has no AIRED/ACCURATE/
    CURRENTLY-AVAILABLE dimension to verify. When Stage 3 introduces an actual
    top-track schema field, it must remain outside this function's scope by
    construction, and a dedicated (much lighter) check should be added elsewhere
    for it -- never folded into _validate_clip_verification. This validator checks presence/shape ONLY (Law #147's
    M6 self-attestation pattern): that scene_verified is a boolean on every
    clip, and that verification_source_url is present and non-empty whenever
    scene_verified is true. It cannot verify that a URL actually shows the
    claimed scene -- that truth is attested by the drafting pass and subject
    to the same weekly human spot-check as the other Law #147/#151/#152
    attestations.

    MANGA FALLBACK / F20 THIRD STATE: a clip with scene_verified=false must
    carry a non-empty manga_reference naming the specific verified
    chapter/page, OR a non-empty verification_note (F20, docs/KNOWN_ISSUES.md)
    documenting that real aired anime footage almost certainly exists but no
    clip-level video source could be independently confirmed this pass --
    the third state the original two-state model did not recognize. Exactly
    one of the two must be present and non-empty; having neither is a
    violation, and this validator does not require both. If no clip plan can
    be built entirely from verified, currently-available anime footage, the
    manifest may set the top-level clip_plan_needs_manga_source flag -- this
    validator recognizes it as a valid field but does not require it (it is
    only required when the underlying condition is true, which this
    validator cannot independently judge).

    SCENE-CONTENT SELF-AUDIT / STORY-POINT GATE (Law #73 UPDATE 4, added
    July 28, 2026): whenever a clip is scene_verified=true, it must carry a
    claim_vs_source_check object -- {claimed_beat: str, source_content_confirmed:
    str, match: bool} -- recording the drafting pass's own comparison of what
    the clip claims to show against what its cited source was actually checked
    against. This validator checks presence/shape ONLY (same M6 pattern): that
    the object exists, both string fields are non-empty, and match is a
    boolean. It CANNOT verify claimed_beat or source_content_confirmed are
    truthful -- that remains a drafting-pass attestation and weekly human
    spot-check, same as every other Law #73/#147/#151/#152 field. The ONE
    piece this validator CAN mechanically enforce is the internal
    contradiction: scene_verified=true can never coexist with a self-reported
    claim_vs_source_check.match=false on the same clip -- that combination
    means the drafting pass itself found no match yet still marked the clip
    verified, which is a Law #73 violation regardless of whether the
    underlying claim/source text is true.

    CLIP LOCATE GROUNDING (Law #73 UPDATE 5, added July 28, 2026): whenever a
    clip is scene_verified=true, it must also carry a clip_locate object --
    {season: int|str, episode: int, locate_confirmed_via: str, approx_timestamp:
    optional str}. This validator checks presence/shape ONLY (same M6 pattern):
    season present, episode an int, locate_confirmed_via non-empty, and
    approx_timestamp (when present) non-empty. It CANNOT verify that
    locate_confirmed_via actually points back to the same source used in
    claim_vs_source_check, or that the season/episode is true -- that remains
    a drafting-pass attestation and weekly human spot-check. The ONE piece this
    validator CAN mechanically flag is a narrow, best-effort cross-check: if
    both claim_vs_source_check.source_content_confirmed and
    locate_confirmed_via contain an extractable episode-number token and those
    numbers disagree, that is flagged as an inconsistency. If either field
    lacks an extractable token, the comparison is silently skipped -- absence
    of a mismatch there is not evidence of consistency, only an absence of a
    checkable claim. LIMITATION: the extraction uses a single regex .search()
    per field, so only the FIRST episode-number mention in each field's prose
    is captured and compared -- if a field references more than one episode
    number, any mismatch involving a second-or-later-mentioned number is
    silently missed. This is consistent with the check's best-effort, not
    comprehensive, framing; stated explicitly here alongside its other limits.

    story_point_gate (object, OPTIONAL at the top level) -- required by Law
    #73 UPDATE 4 whenever a package's core content is manga-only or
    recently-released, but this validator cannot independently judge when
    that condition applies, so it only checks SHAPE when the field is
    present: {anime_has_reached_this_point: bool, checked_via: non-empty
    str}. Absence of the field is never itself a failure here.

    THEATRICAL FILM RELEASE-WINDOW CLAUSE (Law #73 3B, added July 26, 2026):
    a confirmed theatrical release date does not satisfy AIRED or CURRENTLY
    AVAILABLE on its own -- the film must have actually reached a
    home-video, digital, or streaming release. The manifest may set the
    top-level clip_plan_needs_release_delay flag when a clip is sourced
    from a theatrical-only film; this validator checks presence/shape only
    (same M6 pattern): that the flag is boolean when present, and that
    film_release_gap_note is a non-empty string whenever the flag is true.
    It cannot judge whether the flag SHOULD be true for a given film --
    that is the drafting pass's attestation, subject to the same weekly
    human spot-check as the other Law #73/#147/#151/#152 attestations.

    FOOTAGE_STATUS / FOOTAGE_SEARCH_PERFORMED / LOCATION_POINTER (Law #73
    UPDATE 8, added 2026-08-10, same-day fix after the Re:ZERO / Love Unseen
    footage-location correction incident -- docs/KNOWN_ISSUES.md F21
    context): F20's own fallback above (manga_reference OR a bare
    verification_note) is UNCHANGED by this update -- it still passes
    exactly as it did before. This update adds a SECOND, INDEPENDENT layer
    of enforcement on every scene_verified=false clip, because F20's
    verification_note is a pure self-attestation with no mechanical floor:
    a copy-pasted or vague note satisfied it exactly as well as a real,
    failed search attempt, which is precisely how both corrected packages
    shipped tonight with footage that was never actually located.

      1. footage_status (required, enum FOOTAGE_STATUS_VALUES) -- every
         scene_verified=false clip must set this. aired_not_located HARD-
         BLOCKS: unlike F20's verification_note fallback, there is no
         attestation that can rescue a clip in this state. The validator
         fails closed on it with the exact same treatment as any other
         required-but-missing field, per explicit user decision -- it is
         not merely flagged or downgraded to a warning.
      2. footage_search_performed (required whenever scene_verified=false,
         non-empty string) -- MECHANICAL FLOOR, not just an attestation:
         the string must contain a case-insensitive substring match against
         FOOTAGE_SEARCH_DOMAINS (a curated list of recognizable video-
         platform hosts/names). This is deliberately a low bar -- it proves
         a real platform was NAMED, not that the search was thorough or
         its claimed outcome is true -- but it is a real floor: an empty
         string, whitespace, or platform-agnostic filler text ALWAYS fails
         this check, regardless of length or confident phrasing.
      3. location_pointer (optional object {url: str, description: str}) --
         when present, checked for a CROSS-FIELD consistency requirement:
         location_pointer.url must also appear (after normalization) among
         the package's own top-level sources[].url entries. A location
         pointer that cites a URL never listed in the package's sources is
         treated as inconsistent and fails. This mirrors the existing
         claim_source_matrix / pkg_source_urls pattern used elsewhere in
         this file (see _validate_semantic_qa) rather than introducing a
         new cross-referencing mechanism.

    These three fields are scoped to scene_verified=false clips only --
    exactly the same population F20 already applies to -- and do not affect
    scene_verified=true clips or SEASON_ROUNDUP's separate trailer_reference
    path (_validate_season_roundup_clip_sourcing), which is untouched."""
    have_scene_verified = bool(clips) and all(
        isinstance(c, dict) and isinstance(c.get("scene_verified"), bool)
        for c in clips
    )
    r.add(f"{p} each clip has scene_verified (bool) set (Law #73)",
          have_scene_verified,
          "every clip needs a scene_verified true/false attestation")

    if not have_scene_verified:
        r.add(f"{p} verification_source_url present wherever scene_verified is true (Law #73)",
              False, "cannot check -- scene_verified missing/non-boolean on one or more clips")
        r.add(f"{p} manga_reference present wherever scene_verified is false (Law #73)",
              False, "cannot check -- scene_verified missing/non-boolean on one or more clips")
        return

    verified_missing_source = [
        i + 1 for i, c in enumerate(clips)
        if c.get("scene_verified") is True
        and not (isinstance(c.get("verification_source_url"), str) and c["verification_source_url"].strip())
    ]
    r.add(f"{p} verification_source_url present wherever scene_verified is true (Law #73)",
          len(verified_missing_source) == 0,
          f"clips missing verification_source_url despite scene_verified=true: {verified_missing_source}")

    unverified_missing_fallback_field = [
        i + 1 for i, c in enumerate(clips)
        if c.get("scene_verified") is False
        and not (isinstance(c.get("manga_reference"), str) and c["manga_reference"].strip())
        and not (isinstance(c.get("verification_note"), str) and c["verification_note"].strip())
    ]
    r.add(f"{p} manga_reference or verification_note present wherever scene_verified is false (Law #73 / F20)",
          len(unverified_missing_fallback_field) == 0,
          f"clips missing both manga_reference and verification_note despite scene_verified=false: {unverified_missing_fallback_field}")

    # Law #73 UPDATE 8 (2026-08-10): footage_status enum, required on every
    # scene_verified=false clip, with aired_not_located hard-blocking (fails
    # closed, same treatment as any other required-but-missing field -- not a
    # warning, not something an attestation elsewhere can rescue).
    unverified_clips = [(i, c) for i, c in enumerate(clips) if c.get("scene_verified") is False]

    unverified_missing_footage_status = [
        i + 1 for i, c in unverified_clips
        if c.get("footage_status") not in FOOTAGE_STATUS_VALUES
    ]
    r.add(f"{p} footage_status present and a valid enum value wherever scene_verified is false (Law #73 UPDATE 8)",
          len(unverified_missing_footage_status) == 0,
          f"clips missing/invalid footage_status despite scene_verified=false: {unverified_missing_footage_status} "
          f"(valid values: {FOOTAGE_STATUS_VALUES})")

    unverified_hard_blocked = [
        i + 1 for i, c in unverified_clips
        if c.get("footage_status") in FOOTAGE_STATUS_HARD_BLOCK
    ]
    r.add(f"{p} no clip has footage_status=aired_not_located (Law #73 UPDATE 8, hard block)",
          len(unverified_hard_blocked) == 0,
          f"clips hard-blocked by footage_status=aired_not_located: {unverified_hard_blocked} -- "
          f"aired-but-unlocated footage cannot ship regardless of manga_reference/verification_note")

    # Law #73 UPDATE 8 (2026-08-10): footage_search_performed is a MECHANICAL FLOOR,
    # not a bare attestation -- the string must actually name a recognizable video
    # platform (FOOTAGE_SEARCH_DOMAINS), so an empty, whitespace, or copy-pasted/
    # platform-agnostic string cannot satisfy it merely by being present and non-empty.
    def _footage_search_performed_ok(c: dict) -> bool:
        fsp = c.get("footage_search_performed")
        if not isinstance(fsp, str) or not fsp.strip():
            return False
        fsp_norm = fsp.strip().lower()
        return any(domain in fsp_norm for domain in FOOTAGE_SEARCH_DOMAINS)

    unverified_missing_search_floor = [
        i + 1 for i, c in unverified_clips
        if not _footage_search_performed_ok(c)
    ]
    r.add(f"{p} footage_search_performed present and names a recognizable video platform wherever scene_verified is false (Law #73 UPDATE 8)",
          len(unverified_missing_search_floor) == 0,
          f"clips with missing/empty/platform-less footage_search_performed despite scene_verified=false: {unverified_missing_search_floor}")

    # Law #73 UPDATE 8 (2026-08-10): location_pointer is optional, but when present
    # its url must also appear in the package's own top-level sources[] -- the same
    # pkg_source_urls cross-referencing pattern _validate_semantic_qa already uses,
    # applied here so a location pointer can never cite a URL the package itself
    # never listed as a source.
    def _location_pointer_shape_ok(c: dict) -> bool:
        lp = c.get("location_pointer")
        if lp is None:
            return True  # optional field -- absence is not a failure
        if not isinstance(lp, dict):
            return False
        url = lp.get("url")
        desc = lp.get("description")
        return (
            isinstance(url, str) and url.strip() != ""
            and isinstance(desc, str) and desc.strip() != ""
        )

    unverified_malformed_location_pointer = [
        i + 1 for i, c in unverified_clips
        if not _location_pointer_shape_ok(c)
    ]
    r.add(f"{p} location_pointer well-formed (url + description) when present (Law #73 UPDATE 8)",
          len(unverified_malformed_location_pointer) == 0,
          f"clips with a malformed location_pointer (present but missing/empty url or description): {unverified_malformed_location_pointer}")

    pkg_source_urls_for_footage = {_norm(s.get("url")) for s in _list(pkg, "sources")
                                    if isinstance(s, dict) and isinstance(s.get("url"), str) and s.get("url")}
    unverified_location_pointer_not_in_sources = [
        i + 1 for i, c in unverified_clips
        if isinstance(c.get("location_pointer"), dict)
        and isinstance(c["location_pointer"].get("url"), str)
        and c["location_pointer"]["url"].strip()
        and _norm(c["location_pointer"]["url"]) not in pkg_source_urls_for_footage
    ]
    r.add(f"{p} location_pointer.url also appears in the package's sources list when present (Law #73 UPDATE 8)",
          len(unverified_location_pointer_not_in_sources) == 0,
          f"clips whose location_pointer.url is not listed in the package's sources: {unverified_location_pointer_not_in_sources}")

    # Law #73 UPDATE 4 (2026-07-28): presence/shape check for claim_vs_source_check,
    # required on every scene_verified=true clip.
    verified_clips = [(i, c) for i, c in enumerate(clips) if c.get("scene_verified") is True]

    def _cvsc_shape_ok(c: dict) -> bool:
        cvsc = c.get("claim_vs_source_check")
        if not isinstance(cvsc, dict):
            return False
        return (
            isinstance(cvsc.get("claimed_beat"), str) and cvsc["claimed_beat"].strip() != ""
            and isinstance(cvsc.get("source_content_confirmed"), str) and cvsc["source_content_confirmed"].strip() != ""
            and isinstance(cvsc.get("match"), bool)
        )

    verified_missing_cvsc = [i + 1 for i, c in verified_clips if not _cvsc_shape_ok(c)]
    r.add(f"{p} claim_vs_source_check present and well-formed wherever scene_verified is true (Law #73 UPDATE 4)",
          len(verified_missing_cvsc) == 0,
          f"clips missing/malformed claim_vs_source_check despite scene_verified=true: {verified_missing_cvsc}")

    # Mechanical contradiction check (Law #73 UPDATE 4): scene_verified=true can
    # never coexist with a self-reported match=false. Only meaningful once the
    # shape check above passed for a given clip -- a clip with a malformed/missing
    # claim_vs_source_check is already flagged by the check above, so this check
    # is restricted to clips where match is well-formed enough to read.
    verified_contradicting_match = [
        i + 1 for i, c in verified_clips
        if isinstance(c.get("claim_vs_source_check"), dict)
        and c["claim_vs_source_check"].get("match") is False
    ]
    r.add(f"{p} no clip is scene_verified=true with claim_vs_source_check.match=false (Law #73 UPDATE 4)",
          len(verified_contradicting_match) == 0,
          f"clips scene_verified=true with a self-reported match=false: {verified_contradicting_match}")

    # Law #73 UPDATE 5 (2026-07-28): presence/shape check for clip_locate,
    # required on every scene_verified=true clip. locate_confirmed_via must
    # be a descriptive sentence referring back to the same source already
    # cited in claim_vs_source_check (e.g. "the same Anime News Network
    # episode 16 review cited above") -- never a bare URL. A bare URL both
    # violates the field's own spec (a URL is not "one sentence" naming how
    # the source establishes the episode) and silently defeats the episode-
    # token cross-check below (URL slugs match the episode-number regex
    # inconsistently depending on whether they use spaces, hyphens, or
    # underscores -- an accidental non-match, not a real scope boundary).
    # Shape check itself moved to the module-level _clip_locate_shape_ok()
    # 2026-08-10 (Law #158/#159 same-day fix) so _validate_season_roundup_
    # clip_sourcing's anime path can share this exact same check -- see that
    # function's own docstring for why this was a real gap, not a design choice.
    verified_missing_clip_locate = [i + 1 for i, c in verified_clips if not _clip_locate_shape_ok(c)]
    r.add(f"{p} clip_locate present and well-formed wherever scene_verified is true (Law #73 UPDATE 5)",
          len(verified_missing_clip_locate) == 0,
          f"clips missing/malformed clip_locate despite scene_verified=true: {verified_missing_clip_locate}")

    # Lightweight best-effort episode-number cross-check (Law #73 UPDATE 5):
    # only compares when BOTH fields contain an extractable episode-number
    # token. Absence of a token in either field silently skips the check --
    # it is not itself evidence of consistency. NOTE: .search() only captures
    # the FIRST match per field -- a second episode-number mention within the
    # same field's prose is never inspected.
    _episode_token_re = re.compile(r"(?:episode|ep\.?)\s*#?\s*(\d+)", re.IGNORECASE)

    def _extract_episode_token(text: Any) -> str | None:
        if not isinstance(text, str):
            return None
        m = _episode_token_re.search(text)
        return m.group(1) if m else None

    clip_locate_episode_mismatch = []
    for i, c in verified_clips:
        cvsc = c.get("claim_vs_source_check")
        cl = c.get("clip_locate")
        if not isinstance(cvsc, dict) or not isinstance(cl, dict):
            continue
        cvsc_token = _extract_episode_token(cvsc.get("source_content_confirmed"))
        locate_token = _extract_episode_token(cl.get("locate_confirmed_via"))
        if cvsc_token is not None and locate_token is not None and cvsc_token != locate_token:
            clip_locate_episode_mismatch.append(i + 1)

    r.add(f"{p} clip_locate episode number does not contradict claim_vs_source_check when both state one (Law #73 UPDATE 5)",
          len(clip_locate_episode_mismatch) == 0,
          f"clips with mismatched episode-number tokens between claim_vs_source_check and clip_locate: {clip_locate_episode_mismatch}")

    # Law #73 UPDATE 6 (2026-08-05): clip_locate is a structured, validator-
    # enforced fact about a verified clip's season/episode (UPDATE 5, above).
    # clip_descriptions is the free-text clip plan that is what actually gets
    # sent in the email. Nothing previously forced the two to agree -- a
    # verified clip's season/episode could be silently dropped from
    # clip_descriptions while every existing check still passed (confirmed
    # twice: 2026-08-02 One Piece/MHA, 2026-08-05 Bleach TYBW). This check
    # closes that gap: every scene_verified=true clip's own CUT segment in
    # clip_descriptions must literally contain its clip_locate season/episode,
    # in one of the fixed set of equivalent formats (S4E41 / Season 4,
    # Episode 41 -- see tools/render_clip_descriptions.py; a third "4x41"
    # alternative was removed there and here, 2026-08-05, as inherently
    # ambiguous with resolutions/dimensions/generic multiplier prose).
    #
    # Segment-to-clip mapping only runs when clip_descriptions uses the real,
    # demonstrated "CUT N ..." format (every real sent manifest since
    # 2026-07-30) with EXACTLY one segment per clip. If it doesn't use CUT
    # markers at all, has fewer CUT segments than clips, or has MORE CUT
    # segments than clips (over-split: a mid-sentence reference to another
    # cut inside a segment's own prose, e.g. "the closing beat mirrors
    # CUT1's establishing shot" inside CUT4's text, causes _CUT_SPLIT_RE to
    # fire an extra time -- flagged in adversarial review, 2026-08-05), this
    # check reports that mismatch itself rather than silently mismapping or
    # skipping -- older free-prose style, and over-split text, are not
    # acceptable formats for a package carrying scene_verified clips.
    clip_desc_missing_location: list[int] = []
    clip_desc_segment_mismatch = False
    if _extract_location_tokens is None or _split_into_cut_segments is None:
        r.add(f"{p} clip_descriptions surfaces clip_locate season/episode for every verified clip (Law #73 UPDATE 6)",
              False,
              "could not import tools/render_clip_descriptions.py -- check cannot run, failing closed")
    else:
        clip_descriptions_text = pkg.get("clip_descriptions") if isinstance(pkg.get("clip_descriptions"), str) else ""
        segments = _split_into_cut_segments(clip_descriptions_text)
        verified_clips_for_desc = [(i, c) for i, c in enumerate(clips) if isinstance(c, dict) and c.get("scene_verified") is True]
        if verified_clips_for_desc and len(segments) != len(clips):
            clip_desc_segment_mismatch = True
        else:
            for i, c in verified_clips_for_desc:
                cl = c.get("clip_locate")
                if not isinstance(cl, dict):
                    continue  # UPDATE 5's own shape check already flags this
                season, episode = cl.get("season"), cl.get("episode")
                if season in (None, "") or not isinstance(episode, int) or isinstance(episode, bool):
                    continue  # UPDATE 5's own shape check already flags this
                wanted = (str(int(season)), str(int(episode))) if str(season).isdigit() else None
                if wanted is None:
                    continue
                segment = segments[i] if i < len(segments) else ""
                if wanted not in _extract_location_tokens(segment):
                    clip_desc_missing_location.append(i + 1)

        if clip_desc_segment_mismatch:
            r.add(f"{p} clip_descriptions surfaces clip_locate season/episode for every verified clip (Law #73 UPDATE 6)",
                  False,
                  f"clip_descriptions CUT segment count ({len(segments)}) does not match clip count ({len(clips)}) -- cannot map segments to clips")
        else:
            r.add(f"{p} clip_descriptions surfaces clip_locate season/episode for every verified clip (Law #73 UPDATE 6)",
                  len(clip_desc_missing_location) == 0,
                  f"verified clips whose season/episode is missing from their clip_descriptions CUT segment: {clip_desc_missing_location}")

    needs_manga = pkg.get("clip_plan_needs_manga_source")
    if needs_manga is not None:
        r.add(f"{p} clip_plan_needs_manga_source is boolean when present (Law #73)",
              isinstance(needs_manga, bool),
              f"clip_plan_needs_manga_source={needs_manga!r}")

    needs_release_delay = pkg.get("clip_plan_needs_release_delay")
    if needs_release_delay is not None:
        r.add(f"{p} clip_plan_needs_release_delay is boolean when present (Law #73 3B)",
              isinstance(needs_release_delay, bool),
              f"clip_plan_needs_release_delay={needs_release_delay!r}")

    if needs_release_delay is True:
        gap_note = pkg.get("film_release_gap_note")
        r.add(f"{p} film_release_gap_note present wherever clip_plan_needs_release_delay is true (Law #73 3B)",
              isinstance(gap_note, str) and gap_note.strip() != "",
              f"film_release_gap_note={gap_note!r}")

    story_point_gate = pkg.get("story_point_gate")
    if story_point_gate is not None:
        gate_ok = (
            isinstance(story_point_gate, dict)
            and isinstance(story_point_gate.get("anime_has_reached_this_point"), bool)
            and isinstance(story_point_gate.get("checked_via"), str)
            and story_point_gate["checked_via"].strip() != ""
        )
        r.add(f"{p} story_point_gate is well-formed when present (Law #73 UPDATE 4)",
              gate_ok,
              f"story_point_gate={story_point_gate!r}")


def _validate_season_roundup_clip_sourcing(clips: list[Any], pkg: dict[str, Any], p: str, r: Result) -> None:
    """Law #159 (SEASON_ROUNDUP, added 2026-08-10): each clip must use exactly ONE
    of three valid source types -- (1) aired anime footage, Law #73's existing
    scene_verified=true + clip_locate chain, unchanged; (2) manga panel, the
    existing manga_reference field, unchanged; (3) official trailer/PV footage,
    the NEW trailer_reference object, confirmed shape:
    {trailer_title_or_id: str, claimed_beat: str, source_content_confirmed: str,
    match: bool}. This validator checks presence/shape ONLY (Law #147's M6
    self-attestation pattern) -- same discipline as every other Law #73 field: it
    cannot verify that source_content_confirmed is truthful, or that the named
    trailer actually contains the claimed beat. That remains a drafting-pass
    attestation subject to weekly human spot-check.

    MUTUAL EXCLUSIVITY: a clip must not declare both clip_locate (aired-footage
    grounding) and trailer_reference (trailer grounding) at once -- these are two
    different source-type claims about the same clip and cannot both be true.

    NO CLIP_LOCATE ON TRAILER CLIPS: a trailer is not "an aired episode," so the
    AIRED/ACCURATE/CURRENTLY-AVAILABLE triad (season/episode/locate_confirmed_via)
    does not apply to it -- clip_locate's absence on a trailer-sourced clip is
    correct, not a gap, and this validator does not require or request it there.

    CLIP_LOCATE REQUIRED ON ANIME-SOURCED CLIPS (fixed 2026-08-10, same-day review
    fix -- this was a real gap in the first draft, not a design choice): a clip with
    scene_verified=true must ALSO carry a well-formed clip_locate object, exactly the
    same requirement Law #73 UPDATE 5 established for every other format_type's
    anime-sourced clips (see the module-level _clip_locate_shape_ok(), shared with
    _validate_clip_verification so the two paths cannot silently drift apart). The
    first-draft version of this function counted scene_verified=true alone as a
    'valid source' with no clip_locate check at all -- a SEASON_ROUNDUP package could
    have shipped an anime-sourced clip with no clip_locate (or a malformed one) and
    passed. This does not apply to manga or trailer clips, which correctly have no
    clip_locate requirement of their own.
    """
    if not clips:
        r.add(f"{p} clip plan is non-empty (clips present)", False, f"clips={clips}")
        return

    bad_shape = []
    mutually_exclusive_violation = []
    unverified_trailer = []
    no_valid_source = []
    anime_missing_clip_locate = []

    for i, c in enumerate(clips):
        if not isinstance(c, dict):
            bad_shape.append(i + 1)
            continue

        has_scene_verified_true = c.get("scene_verified") is True
        has_manga_ref = isinstance(c.get("manga_reference"), str) and c.get("manga_reference").strip() != ""
        tr = c.get("trailer_reference")
        has_trailer_ref = isinstance(tr, dict)
        has_clip_locate = isinstance(c.get("clip_locate"), dict)

        if has_trailer_ref and has_clip_locate:
            mutually_exclusive_violation.append(i + 1)

        if has_trailer_ref:
            tr_shape_ok = (
                isinstance(tr.get("trailer_title_or_id"), str) and tr.get("trailer_title_or_id").strip() != ""
                and isinstance(tr.get("claimed_beat"), str) and tr.get("claimed_beat").strip() != ""
                and isinstance(tr.get("source_content_confirmed"), str) and tr.get("source_content_confirmed").strip() != ""
                and isinstance(tr.get("match"), bool)
            )
            if not tr_shape_ok:
                bad_shape.append(i + 1)
            elif tr.get("match") is not True:
                unverified_trailer.append(i + 1)

        # Law #73 UPDATE 5, applied to the anime path of SEASON_ROUNDUP: a
        # scene_verified=true clip must carry a well-formed clip_locate object.
        # Checked independently of has_trailer_ref's mutual-exclusivity check above
        # (a clip declaring BOTH scene_verified=true and trailer_reference is already
        # caught there; this check fires whenever scene_verified=true regardless).
        anime_clip_locate_ok = True
        if has_scene_verified_true:
            anime_clip_locate_ok = _clip_locate_shape_ok(c)
            if not anime_clip_locate_ok:
                anime_missing_clip_locate.append(i + 1)

        # exactly one of the three source types must yield a valid, verified source.
        # The anime path additionally requires clip_locate to be well-formed --
        # scene_verified=true with a missing/malformed clip_locate does NOT count
        # as a valid source (it is instead caught by the dedicated named check below,
        # same fail-closed pattern as Law #73's existing anime path elsewhere).
        valid_sources = sum([
            bool(has_scene_verified_true and anime_clip_locate_ok),
            bool(has_manga_ref),
            bool(has_trailer_ref and isinstance(tr, dict) and tr.get("match") is True),
        ])
        if valid_sources == 0:
            no_valid_source.append(i + 1)

    r.add(f"{p} every clip has a well-formed source object for its declared type (Law #159)",
          len(bad_shape) == 0,
          f"clips with malformed trailer_reference or missing scene_verified bool: {bad_shape}")
    r.add(f"{p} no clip declares both clip_locate and trailer_reference (Law #159 mutual exclusivity)",
          len(mutually_exclusive_violation) == 0,
          f"clips declaring both aired-footage and trailer grounding: {mutually_exclusive_violation}")
    r.add(f"{p} every trailer_reference has match == true (Law #159)",
          len(unverified_trailer) == 0,
          f"clips with trailer_reference.match=false, cannot be used: {unverified_trailer}")
    r.add(f"{p} clip_locate present and well-formed wherever scene_verified is true (Law #73 UPDATE 5, applied to Law #159 anime path)",
          len(anime_missing_clip_locate) == 0,
          f"anime-sourced clips missing/malformed clip_locate despite scene_verified=true: {anime_missing_clip_locate}")
    r.add(f"{p} every clip has exactly one valid, verified source (anime/manga/trailer) (Law #159)",
          len(no_valid_source) == 0,
          f"clips with no valid verified source of any of the three types: {no_valid_source}")


def _url_is_encyclopedic(url: str) -> bool:
    u = (url or "").lower()
    return any(dom in u for dom in ENCYCLOPEDIC_DOMAINS)


def _validate_season_roundup_sourcing(pkg: dict[str, Any], p: str, r: Result) -> None:
    """Law #159 PER-SHOW SOURCING (implementation item 3 -- BUILT 2026-08-14).

    Law #159: "Each show's premiere claim needs its OWN claim_source_matrix entry ...
    a real, distinct source per show, never one source waved across all shows in the
    roundup." Until this function existed, _validate_semantic_qa only ever asked
    ">=1 core claim exists somewhere in the matrix", so a five-show roundup could ship
    with a single sourced claim about a single show and pass undetected -- a direct
    structural echo of the Gachiakuta incident (Law #73 UPDATE 7) that motivated the
    per-clip verification discipline. cron_daily_runtime.txt named exactly this gap as
    the blocker making SEASON_ROUNDUP non-selectable from the daily run.

    DENOMINATOR: the explicit `roundup_shows` list, NOT the clip count. Nothing
    enforces 1 clip == 1 show (the >=4-clip floor was removed as arbitrary, F22
    2026-07-28), so inferring the count from clips would fail OPEN precisely when a
    show is under-covered -- the exact case this check exists to catch.

    Checks (all fail-closed):
      1. roundup_shows well-formed: list of >=2 non-empty strings, no case-insensitive
         duplicates.
      2. every core:true matrix entry carries a `show` naming one of roundup_shows.
      3. COVERAGE: every roundup_shows name has >=1 core entry tagged to it.
      4. PER-SHOW SOURCING: each show's tagged entries cite, between them, >=1 source
         that is BOTH listed in package `sources` (hence dated) AND non-encyclopedic --
         the same standard _validate_semantic_qa applies globally, applied per show.
      5. DISTINCTNESS: no source URL shared by two different shows. This is the check
         that actually implements "never one source waved across all shows"; coverage
         alone cannot express it (five core claims about one show would satisfy a bare
         count while covering nothing).

    SCOPING: for every non-SEASON_ROUNDUP format_type this requires roundup_shows to be
    ABSENT and reports nothing else, so neither the field nor these checks can leak into
    the other 16 tokens' behavior.

    Like every other Law #73/#147/#159 field check, this is presence/shape/domain only.
    It cannot verify a source actually supports the claim -- that stays a drafting-pass
    attestation subject to the weekly human spot-check (Law #147 M6).
    """
    is_roundup = pkg.get("format_type") == "SEASON_ROUNDUP"
    raw = pkg.get("roundup_shows")

    if not is_roundup:
        r.add(f"{p} roundup_shows absent on non-SEASON_ROUNDUP package (Law #159 scoping)",
              raw is None,
              f"format_type={pkg.get('format_type')!r} roundup_shows={raw!r}")
        return

    shows_ok = (isinstance(raw, list) and len(raw) >= 2
                and all(isinstance(s, str) and s.strip() for s in raw))
    dupes: list[str] = []
    if shows_ok:
        seen: set[str] = set()
        for s in raw:
            k = _norm(s)
            if k in seen:
                dupes.append(s)
            seen.add(k)
        shows_ok = not dupes
    r.add(f"{p} roundup_shows present and well-formed (Law #159: >=2 distinct non-empty names)",
          shows_ok, f"roundup_shows={raw!r} duplicates={dupes}")
    if not shows_ok:
        # Denominator unknown -> the per-show checks below are not evaluable. Record them
        # as failures rather than skipping, so a malformed roundup_shows can never make
        # the per-show discipline silently disappear from the result set.
        for nm in ("every core claim tagged with a roundup show (Law #159)",
                   "every roundup show has >=1 core claim (Law #159 coverage)",
                   "every roundup show cites >=1 listed dated non-encyclopedic source (Law #159)",
                   "no source URL reused across two shows (Law #159 distinctness)"):
            r.add(f"{p} {nm}", False, "roundup_shows malformed/absent -- per-show checks not evaluable")
        return

    show_keys = {_norm(s): s for s in raw}

    qa = pkg.get("semantic_qa")
    matrix = qa.get("claim_source_matrix") if isinstance(qa, dict) else None
    core = ([e for e in matrix if isinstance(e, dict) and e.get("core") is True]
            if isinstance(matrix, list) else [])

    untagged: list[str] = []
    for e in core:
        sv = e.get("show")
        if not (isinstance(sv, str) and _norm(sv) in show_keys):
            untagged.append(f"{sv!r}:{str(e.get('claim', ''))[:32]}")
    r.add(f"{p} every core claim tagged with a roundup show (Law #159)",
          bool(core) and not untagged,
          f"core_claims={len(core)} untagged_or_unknown_show={untagged}")

    by_show: dict[str, list[dict[str, Any]]] = {k: [] for k in show_keys}
    for e in core:
        sv = e.get("show")
        if isinstance(sv, str) and _norm(sv) in show_keys:
            by_show[_norm(sv)].append(e)

    missing = [show_keys[k] for k, v in by_show.items() if not v]
    r.add(f"{p} every roundup show has >=1 core claim (Law #159 coverage)",
          not missing, f"shows_with_no_core_claim={missing}")

    pkg_source_urls = {_norm(s.get("url")) for s in _list(pkg, "sources")
                       if isinstance(s, dict) and isinstance(s.get("url"), str)
                       and s.get("url") and s.get("date")}
    unsourced: list[str] = []
    for k, entries in by_show.items():
        if not entries:
            continue  # already reported by the coverage check above
        qualifying = any(
            isinstance(u, str) and _norm(u) in pkg_source_urls and not _url_is_encyclopedic(u)
            for e in entries for u in (e.get("source_urls") or []))
        if not qualifying:
            unsourced.append(show_keys[k])
    r.add(f"{p} every roundup show cites >=1 listed dated non-encyclopedic source (Law #159)",
          not unsourced, f"shows_without_qualifying_source={unsourced}")

    url_owner: dict[str, str] = {}
    shared: list[str] = []
    for k, entries in by_show.items():
        urls = {_norm(u) for e in entries for u in (e.get("source_urls") or [])
                if isinstance(u, str) and u.strip()}
        for u in sorted(urls):
            prev = url_owner.get(u)
            if prev is not None and prev != k:
                shared.append(f"{u[:60]} shared by {show_keys[prev]!r} and {show_keys[k]!r}")
            else:
                url_owner[u] = k
    r.add(f"{p} no source URL reused across two shows (Law #159 distinctness)",
          not shared, f"shared_sources={shared}")


def _validate_semantic_qa(pkg: dict[str, Any], p: str, r: Result) -> None:
    """Validate the one-pass semantic QA the generation context must self-run before
    returning (Law #147 / credit-safe mode). The daily model launch is single-pass, so
    the audit is folded into that one context and recorded in the manifest (NOT the slim
    email). This validator checks the audit is PRESENT and well-SHAPED, plus two MECHANICAL
    properties of the claim-to-source matrix:
      (a) every core claim cites >=1 source that is also listed in the package `sources`
          (so the support is dated — sources already require url+date), and
      (b) no core claim is supported ONLY by encyclopedic/aggregator sources
          (Wikipedia/MAL/Fandom) — at least one non-encyclopedic dated source is required.
    It does NOT and CANNOT prove the claim is TRUE or that the writing is good; source
    truth and semantic quality remain a model attestation + the weekly human spot-check.

    Two additions (2026-07-25, closes a real production-audit gap): (c) the hook's own
    claim and the loop's own claim must EACH be their own core:true matrix entry tagged
    anchors_claim='hook'/'loop' with a listed source -- checked mechanically here, not
    just self-attested via the checks dict; and (d) numeric_cross_check, a self-
    attestation (like blackout_recent_conflicts etc.) that every count named in the VO
    was arithmetically verified against the cited source's actual enumeration."""
    qa = pkg.get("semantic_qa")
    if not isinstance(qa, dict):
        r.add(f"{p} semantic_qa audit present (self-audit before return)", False,
              "semantic_qa object missing/not an object")
        # downstream shape checks cannot run
        r.add(f"{p} semantic_qa.claim_source_matrix present with >=1 core claim", False,
              "no semantic_qa")
        return
    r.add(f"{p} semantic_qa audit present (self-audit before return)", True, "")
    r.add(f"{p} semantic_qa.audited_before_return attested true",
          qa.get("audited_before_return") is True,
          f"audited_before_return={qa.get('audited_before_return')}")

    # required self-attested check flags present and true (the validator ALSO enforces
    # the mechanical laws independently; this records the model's own audit result).
    checks = qa.get("checks")
    # VO-handoff split (2026-08-16): when vo_status == "pending" the VO does not exist
    # yet, so the five VO-dependent attestations cannot honestly be made and are
    # SKIPPED. The five VO-independent ones are still ENFORCED for real -- a draft-stage
    # package gets no discount on sourcing, timing, titles or clip structure.
    vo_pending = _vo_is_pending(pkg)

    indep_ok = isinstance(checks, dict) and all(
        checks.get(k) is True for k in VO_INDEPENDENT_QA_KEYS)
    indep_missing = [k for k in VO_INDEPENDENT_QA_KEYS
                     if not (isinstance(checks, dict) and checks.get(k) is True)]
    r.add(f"{p} semantic_qa.checks VO-independent attested true "
          f"({', '.join(VO_INDEPENDENT_QA_KEYS)})",
          indep_ok, f"missing/false={indep_missing}")

    dep_label = (f"{p} semantic_qa.checks VO-dependent attested true "
                 f"({', '.join(VO_DEPENDENT_QA_KEYS)})")
    if vo_pending:
        r.skip(dep_label, "vo_status=pending -- VO not written yet, cannot attest")
    else:
        dep_ok = isinstance(checks, dict) and all(
            checks.get(k) is True for k in VO_DEPENDENT_QA_KEYS)
        dep_missing = [k for k in VO_DEPENDENT_QA_KEYS
                       if not (isinstance(checks, dict) and checks.get(k) is True)]
        r.add(dep_label, dep_ok, f"missing/false={dep_missing}")

    # RESCINDED 2026-07-27 (Law #141 rescission): final_to_opening_readaloud
    # consistency check removed along with the rest of the forced-loop mandate.
    # If a manifest still includes final_to_opening_readaloud, it is inert -- not
    # read or checked here.

    # claim-to-source support matrix (MECHANICAL shape + domain checks only).
    # Law #58 restoration (policy decision, July 24 2026): every core entry must also
    # carry a `claim_type` in CLAIM_TYPES so the type-specific minimum below can be
    # applied. Non-core entries are exempt (they carry no source-backing obligation).
    matrix = qa.get("claim_source_matrix")
    well_formed = (isinstance(matrix, list) and len(matrix) >= 1 and all(
        isinstance(e, dict) and isinstance(e.get("claim"), str) and e.get("claim").strip()
        and isinstance(e.get("core"), bool)
        and isinstance(e.get("source_urls"), list)
        and all(isinstance(u, str) and u.strip() for u in e.get("source_urls", []))
        and (e.get("core") is not True or e.get("claim_type") in CLAIM_TYPES)
        for e in matrix))
    core_entries = [e for e in matrix if isinstance(e, dict) and e.get("core") is True] if isinstance(matrix, list) else []
    r.add(f"{p} semantic_qa.claim_source_matrix present with >=1 core claim (each core claim tagged with a Law #58 claim_type)",
          well_formed and len(core_entries) >= 1,
          f"well_formed={well_formed} core_claims={len(core_entries)}")
    if not (well_formed and core_entries):
        r.add(f"{p} every core claim cites a listed dated source", False, "matrix malformed / no core claims")
        r.add(f"{p} no core claim relies solely on Wikipedia/MAL/Fandom", False,
              "matrix malformed / no core claims")
        r.add(f"{p} Law #58 high-risk claims (type B/E) cite >=2 listed sources incl. >=1 named/non-encyclopedic",
              False, "matrix malformed / no core claims")
        return

    # F2 fix (production-audit finding, 2026-07-25): a non-string url in a sources[]
    # entry (e.g. a number) previously crashed _norm()'s .strip()/.lower() call with an
    # unhandled AttributeError. Require url to actually be a string before normalizing.
    # F15 fix (2026-07-25): the outer pkg.get("sources") itself also needed a type
    # guard -- a non-list "sources" (e.g. an int) made "or []" a no-op (12345 or []
    # == 12345), crashing the comprehension's iteration with TypeError. _list()
    # coerces to [] for any non-list value.
    pkg_source_urls = {_norm(s.get("url")) for s in _list(pkg, "sources")
                       if isinstance(s, dict) and isinstance(s.get("url"), str)
                       and s.get("url") and s.get("date")}
    every_core_listed = True
    none_sole_encyclopedic = True
    offenders_unlisted: list[str] = []
    offenders_encyclopedic: list[str] = []
    for e in core_entries:
        urls = [u for u in e.get("source_urls", []) if isinstance(u, str) and u.strip()]
        listed = [u for u in urls if _norm(u) in pkg_source_urls]
        if not listed:
            every_core_listed = False
            offenders_unlisted.append(e.get("claim", "")[:40])
        if not any(not _url_is_encyclopedic(u) for u in urls):
            none_sole_encyclopedic = False
            offenders_encyclopedic.append(e.get("claim", "")[:40])
    r.add(f"{p} every core claim cites a listed dated source",
          every_core_listed, f"unlisted={offenders_unlisted}")
    r.add(f"{p} no core claim relies solely on Wikipedia/MAL/Fandom",
          none_sole_encyclopedic, f"encyclopedic_only={offenders_encyclopedic}")

    # Law #58 restoration: TYPE B (creator quotes/confirmed interviews) and TYPE E
    # (cross-show connections) are the two highest-risk claim types and require >=2
    # listed dated sources, at least one of which is non-encyclopedic (standing in for
    # Law #58's "named, credible" requirement -- a wiki/aggregator citation alone was
    # exactly the failure mode that produced the original Roy Mustang / Naruto-JJK
    # incidents this law exists to prevent). All other claim types keep the flat >=1
    # listed + >=1 non-encyclopedic rule enforced above.
    high_risk_ok = True
    offenders_high_risk: list[str] = []
    for e in core_entries:
        if e.get("claim_type") not in HIGH_RISK_CLAIM_TYPES:
            continue
        urls = [u for u in e.get("source_urls", []) if isinstance(u, str) and u.strip()]
        listed = [u for u in urls if _norm(u) in pkg_source_urls]
        listed_non_encyclopedic = [u for u in listed if not _url_is_encyclopedic(u)]
        if len(listed) < 2 or not listed_non_encyclopedic:
            high_risk_ok = False
            offenders_high_risk.append(f"{e.get('claim_type')}:{e.get('claim', '')[:40]}")
    r.add(f"{p} Law #58 high-risk claims (type B/E) cite >=2 listed sources incl. >=1 named/non-encyclopedic",
          high_risk_ok, f"offenders={offenders_high_risk}")

    # 1.5 HOOK/LOOP CLAIM COVERAGE (2026-07-25 production-audit finding): the specific
    # claim underlying hook_line/opening_sentence, and the specific claim underlying
    # loop_line's promise, must EACH be its own core:true matrix entry tagged
    # anchors_claim="hook"/"loop" with a real listed source -- ">=1 core claim exists
    # somewhere in the matrix" (already checked above) is not sufficient, because a
    # sent package can satisfy that with an unrelated sourced claim while the hook or
    # loop itself rests on an uncited assertion. This does not replace the general
    # core-claim checks above; it adds a targeted one.
    # core_entries is already pre-filtered to core:true items (see above), so no
    # need to re-check e.get("core") here.
    hook_anchored = any(
        e.get("anchors_claim") == "hook"
        and [u for u in e.get("source_urls", []) if _norm(u) in pkg_source_urls]
        for e in core_entries
    )
    r.add(f"{p} hook_line/opening_sentence's claim is its own sourced core matrix entry "
          f"(anchors_claim='hook')", hook_anchored,
          "no core matrix entry tagged anchors_claim='hook' with a listed source")
    # RESCINDED 2026-07-27 (Law #141 rescission): the loop_anchored / anchors_claim="loop"
    # sourcing requirement is removed along with the rest of the forced-loop mandate. A
    # package MAY still tag an entry anchors_claim="loop" harmlessly; nothing requires
    # or checks it anymore.


def validate_package(pkg: dict[str, Any], idx: int, r: Result) -> None:
    """Per-package mechanical checks. `idx` is 0/1; label uses the slot."""
    slot = pkg.get("slot", f"pkg{idx}")
    p = f"[{slot}]"

    # --- format_type is one of the controlled tokens (Law #85 + #96 + WATCH_RANK/#98) ---
    # Free-text/compound labels are no longer permitted — see FORMAT_TYPES above and
    # cron_daily_runtime.txt Step 3 for the restoration note.
    fmt_raw = pkg.get("format_type")
    r.add(f"{p} format_type is one of the controlled tokens",
          isinstance(fmt_raw, str) and fmt_raw in FORMAT_TYPES,
          f"format_type={fmt_raw!r}; allowed={FORMAT_TYPES}")

    # Resolve the edit length: 30s default, or a sanctioned 45-59s experiment (M1).
    target_sec, _is_experiment = _resolve_edit_target(pkg, p, r)
    vo_min, vo_max = _vo_band(target_sec)

    # --- VO word count scaled to the edit length (Law #138; _vo_band(30)==(100,108)) ---
    # F15 fix (2026-07-25): a non-string vo (e.g. an int) made "or \"\"" a no-op
    # (12345 or "" == 12345), crashing downstream re.findall inside _words() with
    # TypeError. _str() coerces to "" for any non-string value.
    vo = _str(pkg, "vo")
    wc = pkg.get("vo_word_count")
    counted = _words(vo)
    # F2 fix (production-audit finding, 2026-07-25): a non-numeric declared
    # vo_word_count (e.g. a string "104") previously crashed the `abs(counted - wc)`
    # comparison with an unhandled TypeError instead of producing a named check
    # failure. Guard the type before doing arithmetic.
    # VO-HANDOFF SKIP GATE (2026-08-16). When vo_status == "pending" the VO has not been
    # written yet, so every check that reads `vo` is SKIPPED rather than evaluated
    # against an empty string -- which would otherwise produce a pile of meaningless
    # FAILs and hide any real structural problem. The word BAND is still reported as the
    # target Claude must hit, in the skip detail, so the handoff carries it.
    vo_pending = _vo_is_pending(pkg)

    if vo_pending:
        r.skip(f"{p} vo_word_count matches VO text",
               "vo_status=pending -- no VO to count yet")
        r.skip(f"{p} VO within {vo_min}-{vo_max} words",
               f"vo_status=pending -- target band for the writer is "
               f"{vo_min}-{vo_max} words at {int(target_sec)}s")
    else:
        if wc is not None and not _is_num(wc):
            r.add(f"{p} vo_word_count matches VO text", False,
                  f"vo_word_count is not numeric: {wc!r}")
        else:
            if wc is None:
                wc = counted
            # the manifest's declared count must match the actual VO text (no fudging)
            r.add(f"{p} vo_word_count matches VO text", abs(counted - wc) <= 1,
                  f"declared={wc} counted={counted}")
        r.add(f"{p} VO within {vo_min}-{vo_max} words", vo_min <= counted <= vo_max,
              f"words={counted} (edit={int(target_sec)}s)")

    # --- CTA exact placement: a specific question immediately followed by "Leave your take." ---
    # F15 fix (2026-07-25): a non-string cta_line previously crashed _norm()'s
    # str-only .strip()/.lower() with an unhandled AttributeError.
    cta = _str(pkg, "cta_line")
    r.add(f"{p} CTA line is exactly '{CTA_EXACT}'", _norm(cta) == _norm(CTA_EXACT),
          f"cta_line={cta!r}")
    # F15 fix (2026-07-25): same non-string crash class for question_line.
    q = _str(pkg, "question_line").strip()
    r.add(f"{p} question_line is a question", q.endswith("?") and len(q) > 5, f"question_line={q!r}")
    # the exact phrase must appear in the VO, immediately after the question
    # Both of these read the VO body, so both skip while it is pending. cta_line and
    # question_line themselves are still enforced above -- the handoff carries the
    # closing STRUCTURE even though the prose does not exist yet.
    if vo_pending:
        r.skip(f"{p} question immediately followed by '{CTA_EXACT}' in VO",
               "vo_status=pending -- writer must place '<question?> Leave your take.' "
               "contiguously at the close")
        r.skip(f"{p} exact CTA phrase present in VO",
               f"vo_status=pending -- writer must include the exact phrase "
               f"'{CTA_EXACT}'")
    else:
        combined_ok = False
        if q:
            pat = re.escape(q) + r"\s+" + re.escape(CTA_EXACT)
            combined_ok = re.search(pat, vo) is not None
        r.add(f"{p} question immediately followed by '{CTA_EXACT}' in VO", combined_ok,
              "expected '<question?> Leave your take.' contiguous in VO")
        r.add(f"{p} exact CTA phrase present in VO", CTA_EXACT in vo, "")

    # --- CTA on-screen text must appear inside the closing window (Law #62 addendum,
    # added 2026-07-27, per YouTube's July 14, 2026 guidance naming a final-5-second
    # CTA as one of three concrete conversion tactics -- that guidance was written
    # against short, ~30s-class videos). STAGE 1 REBUILD (2026-08-09): a literal fixed
    # 5-second tail stops being a meaningful "closing window" once edits run up to
    # 180s (5s of a 180s video is under 3% of the runtime, far tighter than the
    # original guidance's intent for a 30s video, where 5s is ~17%). Replaced with a
    # percentage-of-runtime floor that reproduces the exact original 30s behavior
    # (cta_start >= 25.0) while scaling sanely for longer edits: the window is the
    # LARGER of a flat 5-second tail or the final 15% of the edit, whichever is more
    # seconds. At 30s: max(5.0, 4.5) = 5.0 -> unchanged, cta_start >= 25.0, identical
    # to the pre-Stage-1 check. At 90s: max(5.0, 13.5) = 13.5 -> cta_start >= 76.5. At
    # 180s: max(5.0, 27.0) = 27.0 -> cta_start >= 153.0.
    cta_start = pkg.get("onscreen_cta_start_sec")
    r.add(f"{p} onscreen_cta_start_sec present", _is_num(cta_start),
          f"onscreen_cta_start_sec={cta_start!r}")
    if _is_num(cta_start):
        cta_window = max(5.0, target_sec * 0.15)
        cta_floor = target_sec - cta_window
        r.add(f"{p} onscreen_cta_start_sec within the closing {cta_window:.1f}s of the {int(target_sec)}s edit",
              cta_start >= cta_floor,
              f"onscreen_cta_start_sec={cta_start} target_sec={target_sec} "
              f"required_floor={cta_floor:.2f} (= target_sec - max(5.0, target_sec*0.15))")

    # --- opening_sentence must be the VO's exact first sentence (Law #144/#145) ---
    # RESCINDED 2026-07-27 (Law #141 rescission): the forced seamless-loop mandate
    # (loop_line/loop_transition/final_to_opening/loop_read_aloud_pass/
    # loop_transition_note + the colon-handoff shape checks) is removed. Neither
    # platform's official documentation names loop editing as a ranking signal, and
    # the forced incomplete-colon-setup requirement was producing register violations
    # in production VOs. A VO may now end on any clean, complete, natural closing
    # thought. See laws/law_141_seamless_loop_mechanics.md for the full rescission
    # text. opening_sentence itself is RETAINED (independent of looping) because
    # hook_line must still equal it (Law #144/#145).
    # F15 fix (2026-07-25): non-string opening_sentence/opening_line previously
    # crashed _norm()'s str-only .strip()/.lower() with an unhandled AttributeError.
    # _str() coerces to "" for any non-string value.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", vo) if s.strip()]
    first_sent = sentences[0] if sentences else ""
    opening = (_str(pkg, "opening_sentence") or _str(pkg, "opening_line") or first_sent).strip()

    r.add(f"{p} opening_sentence present",
          bool(_str(pkg, "opening_sentence") or _str(pkg, "opening_line")),
          "provide opening_sentence (or opening_line)")
    if _vo_is_pending(pkg):
        # The proposed opening line IS part of the handoff (Perplexity drafts it),
        # so its PRESENCE stays enforced above. What cannot be checked yet is
        # whether it matches a VO that has not been written.
        r.skip(f"{p} opening_sentence is the VO's exact first sentence",
               "vo_status=pending -- writer must open the VO with this exact sentence")
    else:
        r.add(f"{p} opening_sentence is the VO's exact first sentence",
              bool(opening) and _norm(opening.rstrip(".!?")) == _norm(first_sent.rstrip(".!?")),
              f"opening={opening!r} first={first_sent!r}")

    # --- STAGE 1 REBUILD (2026-08-09): face-cam split-screen (creator TOP / anime
    # BOTTOM, per Sebastian's confirmed permanent decision) is now the REQUIRED
    # default Shorts format -- this INVERTS the prior Law #134 anime-only ban rather
    # than merely relaxing it. face=true and split_screen=true are now the required
    # values; video_style must declare the split-screen format. BANNED_STYLE_TOKENS is
    # retained as a constant (for any downstream code/tests still importing the name)
    # but is no longer used to fail a package -- the tokens it lists ("face",
    # "split screen", "inset", etc.) are exactly the tokens video_style is now
    # REQUIRED to signal, not banned from containing.
    # F15 fix (2026-07-25, still applies): a non-string video_style would otherwise
    # crash _norm()'s str-only .strip()/.lower() with an unhandled AttributeError.
    style = _norm(_str(pkg, "video_style"))
    r.add(f"{p} face flag is true (face-cam split-screen is the required default format)",
          pkg.get("face", None) is True, f"face={pkg.get('face')}")
    r.add(f"{p} split_screen flag is true (face-cam split-screen is the required default format)",
          pkg.get("split_screen", None) is True,
          f"split_screen={pkg.get('split_screen')}")
    r.add(f"{p} video_style declares the face-cam split-screen format",
          any(tok in style for tok in ("face", "split")),
          f"video_style={pkg.get('video_style')!r}; expected it to name the face-cam "
          f"split-screen format (creator top / anime bottom)")

    # --- per-cut timing REQUIRED and must tile the fixed 30s edit (Law #140) ---
    # F15 fix (2026-07-25): a non-list clips (e.g. an int) made "or []" a no-op
    # (12345 or [] == 12345), crashing len(clips) with TypeError. _list() coerces
    # to [] for any non-list value.
    clips = _list(pkg, "clips")
    # F22 fix (2026-07-28): a fixed ">= 4 clips" floor was an arbitrary legacy
    # default with no comment ever justifying the number 4 -- it measured clip
    # COUNT, not clip-plan quality. The real coverage guarantee is
    # _validate_clip_timeline below (contiguous 0->target_sec tiling, no
    # gaps/overlaps, durations sum to capcut_target_sec), which already fails
    # hard on an empty or malformed clip plan (have_fields is False when
    # clips is [], which fails both the per-cut-fields and contiguity checks).
    # A fixed minimum actively penalizes a genuinely-approved, honestly-tiled
    # 3-cut (or fewer) restructure -- e.g. the Sakamoto Days 3-cut manifest
    # (7/13/10s, commit 9284ac2) -- for no substantive reason. Replaced with a
    # non-empty check: it exists only to give a clear, specific failure
    # message if clips is missing/empty, not to impose any count floor.
    r.add(f"{p} clip plan is non-empty (clips present)", len(clips) > 0, f"clips={len(clips)}")
    capcut_target = pkg.get("capcut_target_sec")
    r.add(f"{p} capcut_target_sec == {int(target_sec)}",
          _is_num(capcut_target) and abs(capcut_target - target_sec) <= TOL,
          f"capcut_target_sec={capcut_target}")
    tct = pkg.get("total_clip_time_sec")
    r.add(f"{p} total_clip_time_sec == {int(target_sec)}",
          _is_num(tct) and abs(tct - target_sec) <= TOL,
          f"total_clip_time_sec={tct}")
    _validate_clip_timeline(clips, capcut_target, target_sec, p, r)
    # Law #159 (SEASON_ROUNDUP, added 2026-08-10): a SEASON_ROUNDUP package's clips
    # use a THIRD valid source type (trailer_reference) that Law #73's scene_verified/
    # clip_locate chain was never designed for -- a trailer is not "an aired episode,"
    # so forcing it through AIRED/ACCURATE/CURRENTLY-AVAILABLE is a category error
    # (confirmed during design). Branching here, rather than editing
    # _validate_clip_verification itself, keeps Law #73's existing, heavily-tested
    # behavior completely unchanged for all 15 other format_types.
    if pkg.get("format_type") == "SEASON_ROUNDUP":
        _validate_season_roundup_clip_sourcing(clips, pkg, p, r)
    else:
        _validate_clip_verification(clips, pkg, p, r)

    # RESCINDED 2026-07-27 (Law #141 rescission): the "exactly one final cut carries
    # carries_loop_back=true" clip-plan requirement is removed along with the rest of
    # the forced-loop mandate. carries_loop_back is now an inert, optional clip field --
    # a clip plan may still set it on any cut (or omit it entirely) with no effect on
    # validation.

    # --- required production sections present ---
    required = {
        "youtube_title": "YouTube title",
        "tiktok_post_text": "TikTok post text",
        "captions": "captions",
        "clip_descriptions": "clip descriptions",
        "pinned_comment": "pinned comment",
    }
    for key, label in required.items():
        val = pkg.get(key)
        r.add(f"{p} required section: {label}", isinstance(val, str) and bool(val.strip()), f"{key} empty/missing")

    # --- source count >= 2, each with url + date ---
    # F15 fix (2026-07-25): same non-list crash class as the sources access in
    # semantic-QA above -- _list() coerces to [] for any non-list value.
    sources = _list(pkg, "sources")
    good_sources = [s for s in sources if isinstance(s, dict)
                    and isinstance(s.get("url"), str) and s.get("url").strip()
                    and s.get("date")]
    r.add(f"{p} >=2 credible live sources (url+date each)", len(good_sources) >= 2,
          f"valid_sources={len(good_sources)} of {len(sources)}")

    # --- separate posting-time lines (YouTube and TikTok on their own lines) ---
    # F2 fix (production-audit finding, 2026-07-25): a non-dict post_times (e.g. a
    # list) previously crashed the .get() calls below with an unhandled AttributeError.
    pt_raw = pkg.get("post_times", {})
    pt_is_dict = isinstance(pt_raw, dict)
    r.add(f"{p} post_times is an object with youtube/tiktok keys", pt_is_dict,
          f"post_times={pt_raw!r}")
    pt = pt_raw if pt_is_dict else {}
    yt, tt = pt.get("youtube", ""), pt.get("tiktok", "")
    r.add(f"{p} separate YouTube + TikTok post-time lines",
          bool(str(yt).strip()) and bool(str(tt).strip()) and _norm(yt) != _norm(tt),
          f"youtube={yt!r} tiktok={tt!r}")

    # --- blackout / recent-send conflict inputs must be present and clear ---
    bo = pkg.get("blackout_conflict", None)
    rc = pkg.get("recent_send_conflict", None)
    r.add(f"{p} blackout_conflict input present and clear", bo is False, f"blackout_conflict={bo}")
    r.add(f"{p} recent_send_conflict input present and clear", rc is False, f"recent_send_conflict={rc}")

    # --- strong hook present + no banned filler ---
    # hook_line must be explicitly present BEFORE any fallback. Previously `hook` silently
    # fell back to `opening` when hook_line was missing, so every downstream check using
    # `hook` passed trivially even when the manifest never supplied hook_line at all. This
    # check must run against the RAW field, not the fallback-applied value.
    raw_hook_line = pkg.get("hook_line")
    r.add(f"{p} hook_line present (required field, no silent fallback to opening_sentence)",
          isinstance(raw_hook_line, str) and bool(raw_hook_line.strip()),
          f"hook_line={raw_hook_line!r}")
    # F15 fix (2026-07-25): a non-string hook_line (e.g. an int) made "or opening"
    # a no-op (12345 or opening == 12345), crashing .strip() with AttributeError.
    hook = (_str(pkg, "hook_line") or opening).strip()
    r.add(f"{p} assumption-breaking hook present", len(hook.split()) >= 3, f"hook={hook!r}")
    r.add(f"{p} CTA not a banned phrase", not any(b in _norm(cta) for b in BANNED_CTA), f"cta={cta!r}")
    if _vo_is_pending(pkg):
        r.skip(f"{p} VO contains no banned word 'bro'",
               "vo_status=pending -- re-checked for real once the VO is inserted")
    else:
        r.add(f"{p} VO contains no banned word 'bro'", not re.search(r"\bbro\b", vo, re.I), "")

    # --- Shorts-pipeline guard: this validator governs 30s Shorts only (Law #146) ---
    # Long-form flagships are governed by validators/validate_longform_flagship.py and
    # must NOT be run through the Shorts loop/timing laws. Reject a long-form package
    # that leaks into the Shorts manifest.
    # F4 fix (production-audit finding, 2026-07-25): defaulting an ABSENT content_type
    # to "short" made the check pass silently for a manifest that never declared the
    # field at all. Only the WRONG value was previously caught; a missing field must
    # fail too, since the schema documents this as required.
    # F15 fix (2026-07-25): a non-string content_type previously crashed _norm()'s
    # str-only .strip()/.lower() with an unhandled AttributeError.
    r.add(f"{p} content_type is 'short' (Shorts pipeline only)",
          "content_type" in pkg and _norm(_str(pkg, "content_type")) == "short",
          f"content_type={pkg.get('content_type')!r}")

    # --- vo_status (2026-08-16, VO-handoff workflow) --------------------------------
    # "complete" (default) = VO is written, everything enforced as before.
    # "pending"            = Perplexity has handed off validated facts and Claude has
    #                        not written the VO yet. VO-dependent checks SKIP.
    # Absent is fine and means "complete". Present-but-invalid FAILS -- a malformed
    # value must never be readable as "pending" and must never buy a skip.
    vo_status_raw = pkg.get("vo_status", VO_STATUS_DEFAULT)
    r.add(f"{p} vo_status is one of {VO_STATUS_VALUES} (absent == '{VO_STATUS_DEFAULT}')",
          isinstance(vo_status_raw, str) and vo_status_raw in VO_STATUS_VALUES,
          f"vo_status={pkg.get('vo_status')!r}")

    # --- first-second hook: on-screen assumption-break + spoken hook lead (Law #144) ---
    # The assumption being broken must be visible on screen AND spoken as the very first
    # sentence (the swipe-decision point). Relative watch time dominates Shorts, so the
    # hook has to land in the first second.
    onscreen = pkg.get("hook_onscreen_text", "")
    r.add(f"{p} hook_onscreen_text present (on-screen break in first second)",
          isinstance(onscreen, str) and bool(onscreen.strip()), "hook_onscreen_text empty/missing")
    r.add(f"{p} hook_first_second attested true",
          pkg.get("hook_first_second", None) is True, f"hook_first_second={pkg.get('hook_first_second')}")
    r.add(f"{p} isolation_test_pass attested true (Law #144.1)",
          pkg.get("isolation_test_pass", None) is True, f"isolation_test_pass={pkg.get('isolation_test_pass')}")
    if _vo_is_pending(pkg):
        # Both hook_line and opening_sentence are DRAFT proposals at handoff time;
        # the writer may refine wording, so equality is enforced after insertion.
        # Presence of both stays enforced elsewhere, unconditionally.
        r.skip(f"{p} hook_line equals opening_sentence (break spoken first)",
               "vo_status=pending -- equality enforced once the VO is inserted")
    else:
        r.add(f"{p} hook_line equals opening_sentence (break spoken first)",
              bool(hook) and bool(opening) and _norm(hook.rstrip(".!?")) == _norm(opening.rstrip(".!?")),
              f"hook={hook!r} opening={opening!r}")
    hf = pkg.get("hook_family", "")
    r.add(f"{p} hook_family present (attribution)",
          isinstance(hf, str) and bool(hf.strip()), "hook_family empty/missing")

    # --- external-lens framing experiment (Law #153, added 2026-07-27, BOUNDED) ---
    # Optional field. Weekly cap (<=1/week) is a portfolio-level aggregate, enforced
    # by the weekly analytics cron -- not checkable in a single daily package. This
    # check only validates well-formedness when the field IS present.
    if "external_lens" in pkg:
        el = _str(pkg, "external_lens")
        r.add(f"{p} external_lens is a non-empty string when present (Law #153)",
              bool(el.strip()), f"external_lens={pkg.get('external_lens')!r}")

    # --- single-variant experiment: draft two hooks internally, publish exactly ONE ---
    # (Law #145). Never publish duplicate Shorts of one insight — carry both candidates
    # in the manifest for attribution but ship only the selected one.
    cands = pkg.get("hook_candidates", [])
    cands_ok = (isinstance(cands, list) and len(cands) == 2
                and all(isinstance(c, str) and c.strip() for c in cands))
    r.add(f"{p} exactly 2 internal hook_candidates (single-variant experiment)",
          cands_ok, f"hook_candidates={cands}")
    r.add(f"{p} the two hook_candidates are distinct",
          cands_ok and _norm(cands[0]) != _norm(cands[1]), f"hook_candidates={cands}")
    sel = pkg.get("selected_hook_index", None)
    sel_ok = cands_ok and isinstance(sel, int) and not isinstance(sel, bool) and sel in (0, 1)
    r.add(f"{p} selected_hook_index selects one of the two candidates",
          sel_ok, f"selected_hook_index={sel}")
    selected_hook = cands[sel] if sel_ok else None
    r.add(f"{p} published hook_line matches the selected candidate (publish ONE)",
          sel_ok and _norm(selected_hook) == _norm(hook),
          f"selected={selected_hook!r} hook={hook!r}")

    # --- topic portfolio classification (Law #143) ---
    # F15 fix (2026-07-25): a non-string topic_class previously crashed _norm()'s
    # str-only .strip()/.lower() with an unhandled AttributeError.
    tc = _norm(_str(pkg, "topic_class"))
    r.add(f"{p} topic_class is 'timely' or 'evergreen'", tc in TOPIC_CLASSES,
          f"topic_class={pkg.get('topic_class')!r}")
    # F15 fix (2026-07-25): a non-list topic_signals (e.g. an int) made "or []" a
    # no-op, crashing the list comprehension's iteration with TypeError. _list()
    # coerces to [] for any non-list value.
    signals = [_norm(s) for s in _list(pkg, "topic_signals") if isinstance(s, str)]
    if tc == "timely":
        r.add(f"{p} timely topic declares >=1 valid topic_signal",
              any(s in TIMELY_SIGNALS for s in signals),
              f"topic_signals={pkg.get('topic_signals')} allowed={list(TIMELY_SIGNALS)}")

    # --- recurring-series metadata (Law #143) — machine field, may be null for one-offs ---
    series = pkg.get("series", None)
    if series is not None:
        series_ok = (isinstance(series, dict) and isinstance(series.get("id"), str)
                     and bool(series.get("id", "").strip())
                     and isinstance(series.get("recurring"), bool))
        r.add(f"{p} series metadata well-formed when present", series_ok, f"series={series!r}")

        # M2: a recurring series must be PERCEIVABLE by viewers, not just a machine id.
        # A returning viewer can only form around a series they can see in-feed. When
        # series.recurring is true, require a viewer-facing name that appears in the
        # title or the first-second on-screen text, plus a next-installment line that
        # appears in a published close (captions / pinned_comment / tiktok_post_text).
        if series_ok and series.get("recurring") is True:
            # F15 fix (2026-07-25): non-string series_public_name/youtube_title/
            # hook_onscreen_text/series_next_line previously crashed _norm()'s or
            # .strip()'s str-only methods with an unhandled AttributeError.
            spn = _str(pkg, "series_public_name").strip()
            title_n = _norm(_str(pkg, "youtube_title"))
            onscreen_n = _norm(_str(pkg, "hook_onscreen_text"))
            r.add(f"{p} series_public_name present (viewer-facing series marker)",
                  bool(spn), "series_public_name empty/missing for a recurring series")
            r.add(f"{p} series_public_name shown in title or first-second on-screen text",
                  bool(spn) and (_norm(spn) in title_n or _norm(spn) in onscreen_n),
                  f"series_public_name={spn!r}")
            snl = _str(pkg, "series_next_line").strip()
            close_n = " ".join(_norm(pkg.get(k, "")) for k in
                               ("captions", "pinned_comment", "tiktok_post_text"))
            r.add(f"{p} series_next_line present (next-installment cue)",
                  bool(snl), "series_next_line empty/missing for a recurring series")
            r.add(f"{p} series_next_line appears in a published close",
                  bool(snl) and _norm(snl) in close_n,
                  f"series_next_line={snl!r}")

    # --- funnel attribution + teaser gating (Law #145 / #146) ---
    # F15 fix (2026-07-25): a non-string funnel_status previously crashed _norm()'s
    # str-only .strip()/.lower() with an unhandled AttributeError.
    fs = _norm(_str(pkg, "funnel_status"))
    r.add(f"{p} funnel_status is standalone|teaser|flagship_followup",
          fs in FUNNEL_STATUSES, f"funnel_status={pkg.get('funnel_status')!r}")
    if fs == "teaser":
        fu = pkg.get("flagship_url", "")
        r.add(f"{p} teaser Short carries a flagship_url (teasers only after flagship exists)",
              isinstance(fu, str) and bool(fu.strip()), "flagship_url empty/missing for teaser")

        # DORMANT SCAFFOLDING (Law #145 addendum, added 2026-07-27): this check has
        # NEVER fired on a real package. No flagship has ever been produced on this
        # channel (Law #146's own text), funnel_status has been "teaser" on 0/166 real
        # sends, and flagship_url has been populated on 0/166. The field and check
        # exist now only so the schema is ready the day a real teaser/flagship pair
        # exists -- they carry no evidence of being correct in practice yet. Do not
        # treat this as equivalent in readiness to the onscreen_cta_start_sec or
        # related_video_id additions above, which at least have real (if currently
        # zero/near-zero) usage paths exercised by production tooling.
        hook_for_match = _str(pkg, "hook_line")
        fohm = _str(pkg, "flagship_opening_hook_match")
        r.add(f"{p} teaser flagship_opening_hook_match echoes hook_line (DORMANT scaffolding, Law #145)",
              bool(fohm.strip()) and _norm(hook_for_match.rstrip(".!?")) in _norm(fohm),
              f"flagship_opening_hook_match={pkg.get('flagship_opening_hook_match')!r} hook_line={pkg.get('hook_line')!r}")

    # --- punchy, searchable titles (Law #144, revised) ---
    # ONE punchy idea / curiosity gap per title; no hashtags in EITHER title; tight hard
    # caps (YT<=60, TikTok<=55). The full TikTok caption (tiktok_post_text) may still be
    # longer and carry its hashtag pyramid — these rules are enforced against the distinct
    # tiktok_title FIELD, never the caption. Titles must be distinct from the published
    # hook line and from each other (a title that just repeats the hook is not packaging).
    hook_norm = _norm(hook.rstrip(".!?:"))

    # F15 fix (2026-07-25): a non-string youtube_title made "or \"\"" a no-op
    # (12345 or "" == 12345), crashing len(title)/.rstrip() with TypeError/
    # AttributeError downstream. _str() coerces to "" for any non-string value.
    title = _str(pkg, "youtube_title")
    r.add(f"{p} YouTube title has no hashtags", "#" not in title, f"youtube_title={title!r}")
    r.add(f"{p} YouTube title within {YT_TITLE_MAX} chars", len(title) <= YT_TITLE_MAX, f"len={len(title)}")
    # F_new2 fix (production-audit finding, 2026-07-25): pkg.get("show", "") was fed
    # directly into re.findall with no type check, crashing with TypeError on a
    # non-string show (e.g. a list) instead of failing cleanly -- same crash-instead-
    # of-clean-fail class as F_new (line ~891 above), but a distinct site/function.
    show_raw = pkg.get("show", "")
    show_str = show_raw if isinstance(show_raw, str) else ""
    show_toks = [t.lower() for t in re.findall(r"[A-Za-z0-9']+", show_str)
                 if len(t) >= 3 and t.lower() not in TITLE_STOPWORDS]
    using_fallback = False
    if not show_toks:
        fallback_toks = [t.lower() for t in re.findall(r"[A-Za-z0-9']+", show_str)
                         if t.lower() not in TITLE_STOPWORDS]
        show_toks = fallback_toks or [_norm(show_str)]
        using_fallback = True

    title_norm = _norm(title)
    if using_fallback:
        # Word-boundary match, not substring: fallback tokens can be 1-2 chars
        # (e.g. "86"), and a plain substring check would be nearly vacuous for
        # them -- "k" would match inside "killer". Primary-tier tokens (>=3 chars,
        # already filtered) don't need this stricter check.
        matched_tok = next(
            (t for t in show_toks if t and re.search(rf"\b{re.escape(t)}\b", title_norm)),
            ""
        )
    else:
        matched_tok = next((t for t in show_toks if t in title_norm), "")
    r.add(f"{p} show search keyword appears in title",
          bool(show_toks) and bool(matched_tok),
          f"show_toks={show_toks!r} title={title_norm!r}")
    r.add(f"{p} YouTube title is distinct from the published hook line",
          bool(title.strip()) and bool(hook_norm) and _norm(title.rstrip(".!?:")) != hook_norm,
          f"youtube_title={title!r} hook_line={hook!r}")

    # F15 fix (2026-07-25): same non-string crash class as youtube_title above.
    tt_title = _str(pkg, "tiktok_title")
    r.add(f"{p} TikTok title present (distinct tiktok_title field)",
          isinstance(tt_title, str) and bool(tt_title.strip()), "tiktok_title empty/missing")
    r.add(f"{p} TikTok title has no hashtags", "#" not in tt_title, f"tiktok_title={tt_title!r}")
    r.add(f"{p} TikTok title within {TT_TITLE_MAX} chars", len(tt_title) <= TT_TITLE_MAX, f"len={len(tt_title)}")
    r.add(f"{p} TikTok title is distinct from the published hook line",
          bool(tt_title.strip()) and bool(hook_norm) and _norm(tt_title.rstrip(".!?:")) != hook_norm,
          f"tiktok_title={tt_title!r} hook_line={hook!r}")
    r.add(f"{p} YouTube and TikTok titles are distinct",
          bool(title.strip()) and bool(tt_title.strip())
          and _norm(title.rstrip(".!?:")) != _norm(tt_title.rstrip(".!?:")),
          f"youtube_title={title!r} tiktok_title={tt_title!r}")

    # --- Law #158 (WORTH_WATCHING): no comparative/ranking language, checked BOTH by
    # self-attestation and mechanically (confirmed decision, 2026-08-10 -- a false
    # self-attestation must not bypass the mechanical check). Scoped strictly to
    # WORTH_WATCHING packages; other format_types are unaffected by this check. ---
    if fmt_raw == "WORTH_WATCHING":
        no_comp_flag = pkg.get("no_comparative_language", None)
        r.add(f"{p} no_comparative_language self-attestation present and true (Law #158)",
              no_comp_flag is True,
              f"no_comparative_language={no_comp_flag!r}; WORTH_WATCHING requires this "
              f"self-attestation to be explicitly true")

        comp_fields = {
            "vo": vo,
            "hook_line": hook,
            "hook_onscreen_text": _str(pkg, "hook_onscreen_text"),
            "youtube_title": title,
            "tiktok_title": tt_title,
            "tiktok_post_text": _str(pkg, "tiktok_post_text"),
        }
        # BANNED_COMPARATIVE_LANGUAGE entries are regex patterns, not bare substrings
        # (tightened same-day after adversarial testing found false positives on
        # "beats" and "over " as bare substrings -- see the constant's own comment).
        # re.search against the normalized (lowercased, whitespace-collapsed) field
        # text; each pattern is already \b-anchored to the real construction.
        comp_hits = []
        for field_name, field_val in comp_fields.items():
            field_norm = _norm(field_val)
            for banned_pattern in BANNED_COMPARATIVE_LANGUAGE:
                if re.search(banned_pattern, field_norm, re.IGNORECASE):
                    comp_hits.append(f"{field_name} matches {banned_pattern!r}")
        r.add(f"{p} no banned comparative/ranking language found (Law #158, mechanical check)",
              len(comp_hits) == 0,
              f"WORTH_WATCHING bans comparative/ranking language; violations found: {comp_hits}"
              if comp_hits else "")

    # --- Law #160 (THEORY_SPECULATION): evidence stays fully governed by the existing
    # Law #73/#147/#148/#155 chain (no new check needed -- it already runs via
    # claim_source_matrix below). This block covers the format's own four decisions:
    # (1) real originality-research artifact, not a boolean; (2) mandatory minimum
    # hedge floor + banned certainty language on the core theory claim only; (3)
    # disclosure credit when extending an existing theory; (4) sourced revisit
    # justification. Scoped strictly to THEORY_SPECULATION packages; other
    # format_types are unaffected, same isolation discipline as Law #158/#159. ---
    if fmt_raw == "THEORY_SPECULATION":
        # Decision 1 -- real research artifact, not a self-attested boolean.
        related = pkg.get("related_existing_theories")
        related_well_formed = (
            isinstance(related, list)
            and all(
                isinstance(e, dict)
                and isinstance(e.get("theory_description"), str) and e.get("theory_description").strip()
                and isinstance(e.get("source_url"), str) and e.get("source_url").strip()
                and isinstance(e.get("how_this_differs"), str)
                for e in related
            )
        )
        r.add(f"{p} related_existing_theories present and well-formed (Law #160)",
              related_well_formed,
              f"related_existing_theories={related!r}; THEORY_SPECULATION requires a "
              f"list (possibly empty) of {{theory_description, source_url, how_this_differs}}")

        search = pkg.get("originality_search_performed")
        search_ok = (isinstance(search, dict)
                     and isinstance(search.get("query"), str) and search.get("query").strip()
                     and search.get("search_performed") is True)
        r.add(f"{p} originality_search_performed present and well-formed (Law #160)",
              search_ok,
              f"originality_search_performed={search!r}; requires a real query string "
              f"and search_performed=true")

        # Decision 2 -- theory_claim_line present, hedge-attested, minimum hedge floor
        # met, and certainty language absent. Scoped ONLY to this field.
        claim_line = _str(pkg, "theory_claim_line")
        r.add(f"{p} theory_claim_line present (Law #160)",
              bool(claim_line.strip()), "theory_claim_line empty/missing")

        hedge_attested = pkg.get("theory_hedge_attested", None)
        r.add(f"{p} theory_hedge_attested self-attestation present and true (Law #160)",
              hedge_attested is True,
              f"theory_hedge_attested={hedge_attested!r}; THEORY_SPECULATION requires "
              f"this self-attestation to be explicitly true")

        claim_norm = _norm(claim_line)
        hedge_present = any(h in claim_norm for h in REQUIRED_THEORY_HEDGES)
        r.add(f"{p} theory_claim_line contains a required minimum hedge phrase (Law #160, mechanical floor)",
              bool(claim_line.strip()) and hedge_present,
              f"theory_claim_line={claim_line!r}; must contain >=1 of {REQUIRED_THEORY_HEDGES}")

        certainty_hits = [pat for pat in BANNED_THEORY_CERTAINTY_LANGUAGE
                           if re.search(pat, claim_norm, re.IGNORECASE)]
        r.add(f"{p} theory_claim_line has no banned certainty language (Law #160, mechanical check)",
              len(certainty_hits) == 0,
              f"theory_claim_line={claim_line!r}; violations found: {certainty_hits}"
              if certainty_hits else "")

        # Decision 3 -- disclosure credit is required when related_existing_theories
        # has a non-empty how_this_differs entry (soft presence check across the three
        # viewer-facing fields; disclosure language is naturally variable, unlike the
        # Decision 2 hedge/certainty phrase lists).
        credit_needed = related_well_formed and any(
            isinstance(e, dict) and e.get("how_this_differs", "").strip() for e in (related or [])
        )
        if credit_needed:
            credit_fields_norm = " ".join(_norm(_str(pkg, f)) for f in
                                           ("vo", "pinned_comment", "tiktok_post_text"))
            credit_present = bool(CREDIT_ATTRIBUTION_PATTERN.search(credit_fields_norm))
            r.add(f"{p} existing-theory credit surfaced in viewer-facing text (Law #160)",
                  credit_present,
                  "related_existing_theories has a non-empty how_this_differs entry but "
                  "no viewer-facing field (vo/pinned_comment/tiktok_post_text) contains real "
                  "attribution language crediting an existing theory (bare mention of the "
                  "word 'theory' -- e.g. from the required hedge phrase itself -- is not "
                  "sufficient; found bug during user review 2026-08-11)")

        # Decision 4 -- revisit justification, only checked when a same-show-same-
        # question conflict is flagged (mirrors the real, existing architectural
        # limitation that blackout_conflict/recent_send_conflict are self-attested
        # inputs, not independently computed).
        if pkg.get("blackout_conflict") is True or pkg.get("recent_send_conflict") is True:
            rj = pkg.get("revisit_justification")
            rj_ok = (isinstance(rj, dict)
                     and isinstance(rj.get("new_evidence_summary"), str) and rj.get("new_evidence_summary").strip()
                     and isinstance(rj.get("new_evidence_source_url"), str) and rj.get("new_evidence_source_url").strip()
                     and isinstance(rj.get("new_evidence_date"), str) and rj.get("new_evidence_date").strip())
            r.add(f"{p} revisit_justification present and well-formed when blackout/recent-send flagged (Law #160)",
                  rj_ok,
                  f"revisit_justification={rj!r}; required when blackout_conflict or "
                  f"recent_send_conflict is true for a THEORY_SPECULATION package")

    # --- one-pass semantic QA self-audit (Law #147 / credit-safe mode) ---
    _validate_semantic_qa(pkg, p, r)

    # --- Law #159 per-show sourcing for SEASON_ROUNDUP (item 3, built 2026-08-14) ---
    # Runs for EVERY package, not just roundups: on the non-roundup path it asserts
    # roundup_shows is absent, which is what keeps the field from leaking into the
    # other 16 format_types. Must run AFTER _validate_semantic_qa so the global
    # matrix shape checks are reported first -- this adds the per-show layer on top,
    # it does not replace them.
    _validate_season_roundup_sourcing(pkg, p, r)


def validate_manifest(m: dict[str, Any]) -> Result:
    r = Result()

    # --- recipient exactly correct ---
    r.add("recipient is exactly correct", m.get("recipient") == RECIPIENT,
          f"recipient={m.get('recipient')!r} expected {RECIPIENT!r}")

    # --- package count: normally exactly two, OR exactly one with an explicit,
    # non-empty M5 quality-over-quota justification (F_new fix, 2026-07-26). A bare
    # 1-package manifest with NO reason field still fails exactly as before -- this
    # is intentionally NOT a general "1 or 2, no explanation needed" loosening, since
    # an unexplained missing package could mean a real pipeline failure rather than a
    # deliberate decision. single_package_reason must be a non-empty string.
    pkgs = m.get("packages", []) or []
    single_reason = m.get("single_package_reason")
    is_justified_single = (
        len(pkgs) == 1
        and isinstance(single_reason, str)
        and bool(single_reason.strip())
    )
    r.add("exactly two packages exist, OR exactly one with a non-empty single_package_reason",
          len(pkgs) == 2 or is_justified_single,
          f"count={len(pkgs)}, single_package_reason={single_reason!r}")

    # --- shared batch identity: one batch_id, distinct package_ids across packages ---
    batch_id = m.get("batch_id")
    r.add("shared batch_id present", bool(batch_id), f"batch_id={batch_id!r}")
    pkg_ids = [p.get("package_id") for p in pkgs]
    if len(pkgs) == 1:
        r.add("distinct package_id per package (single-package: just non-empty)",
              bool(pkg_ids) and bool(pkg_ids[0]), f"package_ids={pkg_ids}")
    else:
        r.add("distinct package_id per package",
              len(pkgs) == 2 and all(pkg_ids) and pkg_ids[0] != pkg_ids[1], f"package_ids={pkg_ids}")

    # --- one MORNING and one EVENING slot, OR a single justified package in either slot ---
    # F15 fix (2026-07-25): a non-string slot (e.g. int/bool) crashed _norm()'s
    # str-only .strip()/.lower() with an unhandled AttributeError. _str() coerces to
    # "" for any non-string value, which sorts as neither "evening" nor "morning" and
    # so fails this check cleanly instead of crashing.
    slots = sorted(_norm(_str(p, "slot")) for p in pkgs)
    if is_justified_single:
        r.add("single justified package has a morning or evening slot",
              slots in (["evening"], ["morning"]), f"slots={slots}")
    else:
        r.add("one MORNING and one EVENING slot", slots == ["evening", "morning"], f"slots={slots}")

    if len(pkgs) == 2:
        # --- distinct shows AND distinct formats (independent ideas) ---
        # F_new fix (production-audit finding, 2026-07-25): a non-string show/format_type
        # (e.g. an int or list) previously crashed _norm's str-only .strip()/.lower() with
        # an unhandled AttributeError instead of producing a named check failure -- same
        # crash-instead-of-clean-fail category as the F2/F11 fixes above. Coerce to "" for
        # any non-string value so the check fails cleanly (empty string is never equal for
        # BOTH packages simultaneously in a way that would incorrectly pass "distinct",
        # since all(...) requires both to be truthy) instead of raising.
        raw_shows = [p.get("show", "") for p in pkgs]
        raw_formats = [p.get("format_type", "") for p in pkgs]
        shows = [_norm(s) if isinstance(s, str) else "" for s in raw_shows]
        formats = [_norm(f) if isinstance(f, str) else "" for f in raw_formats]
        r.add("distinct shows (no duplicate)", shows[0] != shows[1] and all(shows),
              f"shows={shows} (raw={raw_shows!r})")
        r.add("distinct formats (no duplicate)", formats[0] != formats[1] and all(formats),
              f"formats={formats} (raw={raw_formats!r})")

        # never publish two Shorts of the same insight in one batch (Law #145)
        # F15 fix (2026-07-25): a non-string hook_line (e.g. an int) previously
        # crashed _norm()'s str-only .strip()/.lower() with an unhandled
        # AttributeError. _str() coerces to "" for any non-string value.
        hooks = [_norm(_str(p, "hook_line")) for p in pkgs]
        r.add("distinct published hooks (no duplicate Short)",
              all(hooks) and hooks[0] != hooks[1], f"hooks={hooks}")

        # titles must be distinct across the two same-day packages (Law #144, revised) —
        # two Shorts posted the same day should not carry the same title on either platform.
        # F15 fix (2026-07-25): a non-string youtube_title/tiktok_title made "or \"\""
        # a no-op, crashing .rstrip() with AttributeError. _str() coerces to "" for
        # any non-string value.
        yt_titles = [_norm(_str(p, "youtube_title").rstrip(".!?:")) for p in pkgs]
        tt_titles = [_norm(_str(p, "tiktok_title").rstrip(".!?:")) for p in pkgs]
        r.add("distinct YouTube titles across the two packages",
              all(yt_titles) and yt_titles[0] != yt_titles[1], f"youtube_titles={yt_titles}")
        r.add("distinct TikTok titles across the two packages",
              all(tt_titles) and tt_titles[0] != tt_titles[1], f"tiktok_titles={tt_titles}")

        # M1 gate RETIRED (Stage 2, 2026-08-09): the "at most one duration_experiment
        # package per batch" cap and the field it read are gone. Variable length in
        # [20,180]s is now the unconditional default for every package -- there is no
        # remaining concept of a bounded "experiment" to cap. See Stage 1's rebuild of
        # _resolve_edit_target for the length logic itself.

    # --- per-package mechanical checks ---
    for i, pkg in enumerate(pkgs):
        validate_package(pkg, i, r)

    return r


def format_report(r: Result) -> str:
    lines = ["DUAL-PACKAGE PREFLIGHT VALIDATION", "=" * 40]
    for name, status, detail in r.checks:
        # SKIP prints its detail too -- for a VO-pending package that detail carries
        # the instruction to the writer (target word band, required closing phrase),
        # so suppressing it would throw away the useful half of the handoff.
        suffix = f"  ({detail})" if detail and status != STATUS_PASS else ""
        lines.append(f"[{status}] {name}{suffix}")
    lines.append("=" * 40)
    n_fail = len(r.failures())
    n_skip = len(r.skips())
    if n_fail:
        verdict = f"BLOCKED — {n_fail} check(s) failed; DO NOT SEND"
    elif n_skip:
        # PARTIAL is the normal, healthy draft state -- not an error. Every evaluable
        # check passed; the VO-dependent ones are waiting on the writer.
        verdict = (f"PARTIAL — {n_skip} check(s) SKIPPED pending VO; 0 failed. "
                   f"NOT cleared to send — re-run after VO insertion")
    else:
        verdict = "PASS — cleared to send both emails"
    lines.append(f"RESULT: {verdict}")
    return "\n".join(lines)


SCHEMA = """RUN MANIFEST SCHEMA (one JSON object per daily dual-package run)
{
  "batch_id": "uuid — shared across both send events",
  "run_ts": "ISO8601",
  "post_date": "YYYY-MM-DD (next day)",
  "recipient": "hero_or_villain@outlook.com",
  "traction_cache": {"timestamp": "ISO8601", "age_days": N, "status": "CURRENT|REFRESHED"},
  "packages": [ PACKAGE, PACKAGE ]   // exactly 2: one morning, one evening. OR exactly
                                      // 1 package (either slot) if the top-level
                                      // single_package_reason field is a non-empty
                                      // string stating the M5 quality-over-quota
                                      // justification for leaving the other slot
                                      // unfilled (F_new fix, 2026-07-26) -- omitting
                                      // this field with only 1 package still fails.
  "single_package_reason": "non-empty string, ONLY when packages has length 1"
}
PACKAGE {
  "package_id": "uuid (distinct per package)",
  "slot": "morning | evening",
  "content_type": "short",          // Shorts pipeline only; long-form uses the flagship validator (Law #146)
  "show": "string", "angle": "string",
  "format_type": "one of FORMAT_TYPES (17 controlled tokens; free-text/compound labels REJECTED)",
  "roundup_shows": ["Show A", "Show B", "Show C"],  // Law #159 implementation item 3 (BUILT 2026-08-14).
                                     // REQUIRED and fail-closed when format_type == "SEASON_ROUNDUP";
                                     // MUST be absent/omitted for every other format_type (a stray
                                     // roundup_shows on a non-roundup package is rejected, so the field
                                     // cannot leak into the other 16 tokens' behavior).
                                     // The AUTHORITATIVE list of shows the roundup claims: >=2 entries,
                                     // each a non-empty string, no duplicates (case-insensitive).
                                     // This is the denominator for the per-show sourcing check. Clip
                                     // count is deliberately NOT used to infer it -- nothing enforces
                                     // 1 clip == 1 show (the >=4-clip floor was removed as arbitrary,
                                     // F22 2026-07-28), so deriving the count from clips would fail
                                     // OPEN exactly when a show is under-covered.
  "topic_class": "timely | evergreen",   // Law #143 (weekly target >=9/14 timely enforced in analytics)
  "topic_signals": ["currently_airing|premiere|chapter|news|seasonal_ranking", ...],  // >=1 when timely
  "series": {"id": "machine-series-id", "recurring": true},  // Law #143; null/omit for one-offs
  "series_public_name": "viewer-facing series name (M2; REQUIRED when series.recurring==true; must appear in youtube_title or hook_onscreen_text)",
  "series_next_line": "next-installment cue (M2; REQUIRED when series.recurring==true; must appear in captions/pinned_comment/tiktok_post_text)",
  "funnel_status": "standalone | teaser | flagship_followup",  // Law #145 attribution
  "flagship_url": "https://... (REQUIRED when funnel_status == 'teaser')",
  "flagship_opening_hook_match": "text echoing hook_line (REQUIRED when funnel_status == 'teaser'; Law #145 addendum, 2026-07-27)",
  // DORMANT as of 2026-07-27: 0 real teasers exist (funnel_status has been "teaser"
  // on 0/166 real sends). The Shorts-side check runs and is real code (see
  // validate_package()'s teaser branch), but has never fired on a real package.
  // Shorts-side scaffolding only -- validate_longform_flagship.py has no matching
  // field today.
  "external_lens": "psychology|film_craft|philosophy|history|... (OPTIONAL, Law #153,
                     2026-07-27, BOUNDED EXPERIMENT). Free text, non-empty string when
                     present. Weekly cap <=1/week enforced by the analytics cron, not
                     here. 0/166 real sends have ever set this -- brand new field.",
  "hook_family": "question|revelation|contradiction|observation|... (attribution, Law #145)",
  "hook_onscreen_text": "the assumption-break shown on-screen in the first second (Law #144)",
  "hook_first_second": true,        // model attests VO hook + on-screen text land in the first second
  "isolation_test_pass": true,      // model attests the Law #144.1 Isolation Test was run on hook_onscreen_text/hook_line and passed
  "hook_candidates": ["hook A", "hook B"],   // exactly 2 drafted internally (Law #145)
  "selected_hook_index": 0,         // 0 or 1; the published hook_line must equal this candidate
  "capcut_target_sec": 30,          // edit length; numeric in [20,180]s, open-ended for every package; 30 is the default when absent
  "total_clip_time_sec": 30,        // must equal capcut_target_sec
  "hook_line": "assumption-breaking first line (== opening_sentence == the selected candidate)",
  "opening_sentence": "EXACT first sentence of the VO (opening_line accepted as alias)",
  "vo": "full VO text (100-108 words; contains '<question?> Leave your take.'); may end on any clean, complete, natural closing thought -- same plain-statement standard as the rest of the VO (Law #141 rescission, 2026-07-27: the forced incomplete-colon-setup loop ending is no longer required or specially scored; a loop-style ending is still allowed if it arises naturally and passes every other register check)",
  "vo_word_count": 104,
  "question_line": "the specific question immediately before the CTA (ends with ?)",
  "cta_line": "Leave your take.",
  "onscreen_cta_start_sec": 26,     // Law #62 addendum, 2026-07-27, generalized Stage 1 (2026-08-09):
                                     // REQUIRED, numeric; must be >= target_sec - max(5.0, target_sec*0.15)
                                     // (i.e. inside the resolved edit length's closing window -- a flat 5s
                                     // floor at short lengths, scaling to 15% of the edit for longer ones).
                                     // Fail-closed.
  // loop_line / loop_transition / final_to_opening / loop_read_aloud_pass /
  // loop_transition_note -- OPTIONAL, INERT (Law #141 rescission, 2026-07-27). These
  // fields are no longer required, read, or checked by the validator. They may still
  // appear on a manifest (e.g. if a loop-style ending happens to arise naturally and
  // the author wants to note it for continuity with older manifests), but nothing
  // enforces their presence, shape, or content anymore. Example (all optional):
  // "loop_line": "a final sentence that happens to hand into the opening",
  // "loop_transition": "loop_line + ' ' + opening_sentence",
  // "final_to_opening": {"final": "...", "opening": "..."},
  // "loop_read_aloud_pass": true, "loop_transition_note": "why it reads seamless",
  "semantic_qa": {                // Law #147: one-pass self-audit recorded in the manifest, NOT the email
    "audited_before_return": true,
    "claim_source_matrix": [      // every CORE claim needs >=1 listed dated source AND >=1 non-encyclopedic source
      {"claim": "core factual/narrative claim", "core": true, "source_urls": ["https://... (also in sources[])"],
       "anchors_claim": "hook",   // OPTIONAL on other entries; REQUIRED on exactly one core:true
                                  // entry so the hook_line/opening_sentence claim is individually
                                  // sourced, not just ">=1 core claim exists somewhere" (Law #148/#150
                                  // fix, 2026-07-25). anchors_claim="loop" is accepted but no longer
                                  // required or checked (Law #141 rescission, 2026-07-27).
       "show": "Show A"},         // Law #159 implementation item 3 (BUILT 2026-08-14). OPTIONAL and
                                  // ignored for the other 16 format_types; REQUIRED on EVERY core:true
                                  // entry when format_type == "SEASON_ROUNDUP", where it must name one
                                  // of roundup_shows (case-insensitive). This per-entry attribution is
                                  // what makes "a real, DISTINCT source per show" (Law #159) expressible
                                  // at all: a bare coverage count cannot tell five core claims about one
                                  // show apart from one core claim about each of five shows.
      {"claim": "minor/color claim", "core": false, "source_urls": []}
    ],
    "checks": {                   // model self-attested audit results (validator also enforces the mechanics)
      "vo_word_count": true, "cta_adjacency": true, "title_search": true,
      "blackout_recent_conflicts": true, "clip_timing_tiling": true,
      "hook_claim_coverage": true,  // 1.5: hook's claim is sourced (also mechanically checked above).
                                     // Renamed from hook_loop_claim_coverage (2026-07-27) -- the loop
                                     // half was rescinded (Law #141 rescission); this is hook-only now.
      "numeric_cross_check": true,       // 1.6: every VO count (e.g. "three more") arithmetically verified against source enumeration, not estimated
      "source_content_verification": true,  // 1.7: every core claim's cited URL actually fetched+read during this audit, not trusted by URL presence alone
      "law_149_redundancy_check": true,     // point 8: no VO sentence merely restates a prior sentence in different words (Law #149 point 1)
      "ai_slop_pattern_check": true          // point 9: none of the 7 named hollow-phrasing patterns present (hollow significance, poetic restatement-as-insight, rule-of-three padding, rhetorical scaffolding phrases, stacked intensifiers with no fact, "it's not just X it's Y", generic urgency framing)
    }
    // final_to_opening_readaloud -- OPTIONAL, INERT (Law #141 rescission, 2026-07-27).
    // No longer required, read, or checked.
  },
  "video_style": "Anime Clips Only (anime footage only; no face/split/inset)",
  "face": false, "split_screen": false,
  "sources": [{"claim": "...", "url": "...", "date": "Mon YYYY"}, ...],   // >=2, url+date each
  "clips": [   // any clip count (F22, no fixed minimum); per-cut timing REQUIRED;
               // must tile 0->30s contiguously
    {"scene": "...", "reason": "...",
     "duration_sec": 6, "timeline_start_sec": 0, "timeline_end_sec": 6,
     "scene_verified": true,               // Law #73 (restored+extended): named scene-level check, not show/arc-level
     "verification_source_url": "https://... (REQUIRED when scene_verified is true)",
     "manga_reference": "chapter/page (REQUIRED when scene_verified is false AND no verification_note is set; F20)",
     "verification_note": "string (F20 alternate to manga_reference when scene_verified is false: real footage almost certainly exists but no clip-level source confirmed this pass; exactly one of manga_reference/verification_note required)",
     "claim_vs_source_check": {            // Law #73 UPDATE 4: REQUIRED whenever scene_verified is true
       "claimed_beat": "one sentence: the specific action/moment this clip claims to show",
       "source_content_confirmed": "one sentence: what verification_source_url was actually checked against and found to show",
       "match": true                       // must be true when scene_verified is true -- match:false + scene_verified:true is a validator-caught contradiction
     }},
    ...  // first starts at 0, each end == next start, last ends at 30,
         // end-start == duration_sec, sum(duration_sec) == 30.
         // carries_loop_back -- OPTIONAL, INERT (Law #141 rescission, 2026-07-27). May
         // still be set true/false on any cut for continuity with older manifests, but
         // no longer required, read, or checked -- there is no longer a "must be exactly
         // the final cut" rule.
         // EVERY clip needs scene_verified (bool); the paired
         // verification_source_url/manga_reference-or-verification_note field is
         // required depending on its value (Law #73 / F20). A manga-sourced clip
         // is a flagged exception, not
         // compliance with the anime-footage-only rule below.
  ],
  "clip_plan_needs_manga_source": false,  // OPTIONAL top-level flag (Law #73); set true only if no valid all-anime clip plan is possible
  "clip_plan_needs_release_delay": false, // OPTIONAL top-level flag (Law #73 3B); set true only if a clip is sourced from a theatrical-only film with no home/streaming release yet
  "film_release_gap_note": "string (REQUIRED when clip_plan_needs_release_delay is true; e.g. \"theatrical-only as of run date, no home/streaming release yet\")",
  "story_point_gate": {                   // OPTIONAL top-level object (Law #73 UPDATE 4); required only when core content is manga-only/recently-released
    "anime_has_reached_this_point": false,
    "checked_via": "https://... (live source checked this session)"
  },
  "clip_descriptions": "string", "captions": "string",
  "youtube_title": "ONE punchy idea; <=60 chars (target 35-50); show keyword early where natural; NO hashtags; distinct from hook_line and from the other package's title (Law #144)",
  "tiktok_title": "ONE punchy idea; <=55 chars (target 30-45); NO hashtags; distinct from youtube_title, hook_line, and the other package's tiktok_title (Law #144). NOTE: this is the SHORT on-platform title, NOT the tiktok_post_text caption (which may stay longer + keep its hashtag pyramid).",
  "tiktok_post_text": "full TikTok caption/post text — may be longer and carry the hashtag pyramid (NOT the title)", "pinned_comment": "string",
  "post_times": {"youtube": "... ET", "tiktok": "... ET"},   // two separate lines
  "blackout_conflict": false, "recent_send_conflict": false,
  // OPTIONAL, null-safe, added 2026-08-11 (design proposal approved same day) --
  // audit visibility ONLY for the two ACTIVE WEIGHTING mechanisms in
  // cron_daily_runtime.txt STEP 3 (format-diversity downweighting, evergreen
  // upweighting). Neither key is validated or enforced today -- there is no check
  // requiring their presence, shape, or internal consistency, and writing them does
  // NOT change STEP 3's selection logic in any way. The runtime is NOT YET
  // instructed to compute or populate these fields (that computation wiring is a
  // separate, deferred design round -- see docs/FORMAT_DIVERSITY_WEIGHTING_TRACKING.md
  // and docs/EVERGREEN_WEIGHTING_TRACKING.md for the real, currently-unconfirmed
  // status of both mechanisms). This is schema documentation of the field SHAPE a
  // future run may populate, nothing more.
  "format_diversity_weighting": {
    "trailing_format_counts": {"FORMAT_TYPE_TOKEN": 0},  // counts over the trailing 14 sent_scripts_log.json entries, one key per format_type observed
    "threshold": 5,                                       // the >=5-of-14 trigger from cron_daily_runtime.txt STEP 3
    "overused_format": "FORMAT_TYPE_TOKEN or null",       // the format_type that hit/exceeded threshold this run, or null if none did
    "downweighting_applied": false,                        // true only if the rule was actually consulted AND had >1 eligible candidate to choose between
    "eligible_candidates": ["FORMAT_TYPE_TOKEN", "..."],  // the monetization-eligible candidate set the downweight rule chose among
    "selected_format": "FORMAT_TYPE_TOKEN",                // the format_type this package actually shipped with
    "changed_outcome": false                               // true ONLY if downweighting caused a DIFFERENT candidate to win than would have won on Law #85 hierarchy rank alone -- this is the field that actually answers "did the mechanism ever do anything," not just "was it consulted"
  },
  "evergreen_weighting": {
    "trailing_evergreen_count": 0,                          // count of topic_class=="evergreen" over the trailing 14 sent_scripts_log.json entries
    "threshold": 5,                                         // the Law #143 evergreen ceiling this run checked against
    "upweighting_eligible": false,                          // true only if trailing_evergreen_count < threshold, making upweighting available this run
    "eligible_candidate_format": "ORIGIN_STORY | SLEPT_ON | HIDDEN_GEM | null",  // the evergreen-fitting candidate format, if any existed this run
    "upweighting_applied": false,                           // true only if the rule was actually consulted AND had a real eligible candidate to upweight
    "selected_topic_class": "timely | evergreen",           // the topic_class this package actually shipped with
    "changed_outcome": false                                // true ONLY if upweighting caused an evergreen candidate to win a slot that would otherwise have gone timely -- same discipline as format_diversity_weighting.changed_outcome above
  }
}
"""


def main(argv: list[str]) -> int:
    if "--schema" in argv:
        print(SCHEMA)
        return 0
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: validate_dual_package.py <run_manifest.json> | --schema", file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[FAIL] could not load manifest: {e}", file=sys.stderr)
        return 2
    r = validate_manifest(manifest)
    print(format_report(r))
    # EXIT CODES (2026-08-16, VO handoff). 2 is PRE-EXISTING (usage / load error)
    # and is deliberately NOT reused here.
    #   0 = fully_passed -- zero FAILs AND zero SKIPs. The ONLY code that clears
    #       AWAITING_APPROVAL or a send.
    #   1 = at least one real FAIL.
    #   3 = PARTIAL -- no FAILs but >=1 SKIP (the vo_status='pending' draft stage).
    #       Distinct from 1 so a caller can tell 'waiting on the writer' from
    #       'genuinely broken', and distinct from 0 so nothing reads it as sendable.
    if r.failures():
        return 1
    if r.skips():
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

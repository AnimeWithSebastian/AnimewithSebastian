#!/usr/bin/env python3
"""REFRAME DESTINATION GUARD (Section 2, added 2026-09-11).

Validates a candidate's reframe_from/reframe_to pairing (a natural-fit
format_type that was on cooldown or hard-blacked-out, mapped to a
substitute format_type per the FORMAT-COOLDOWN CONTENT-FIRST REFRAME
mapping in cron_daily_runtime.txt), and separately validates that a
reframe's logged rejection_reason carries the required machine-readable
"cooldown_reframe: " / "blackout_reframe: " prefix (the V-71 check).

THREE OUTCOMES, NOT TWO -- this is the central design decision and the
reason this module exists instead of a plain boolean allow-list:

  PASS              -- the pairing is unconditionally permitted by the
                        REFRAME MAPPING prose. No further review needed
                        from this mechanism.
  PASS_WITH_CONDITION -- the pairing is permitted, but the prose attaches
                        a judgment call this module cannot mechanically
                        evaluate (e.g. "is this character genuinely
                        disliked," "does every named show have a
                        qualifying source"). This is NOT a fail-closed
                        case: fail-closed is for evidence that didn't
                        check out, not for a question this mechanism was
                        never able to answer while a different mechanism
                        (Law #165 fetch-and-confirm review, which already
                        runs on every batch) already exists to answer it.
                        A guard that rejected these would make the
                        mechanism silently NARROWER than the law it
                        enforces -- eliminating a pairing in code that
                        the prose still authorizes. The condition text is
                        carried into the result so it surfaces in the
                        report and names exactly what the Law #165
                        reviewer needs to confirm.
  FAIL              -- either the pairing does not appear in the allowed
                        set for that source format at all, or the source
                        format's allowed-destination list is empty
                        (WORTH_WATCHING only, see REFRAME_MAP below). This
                        IS categorically wrong, not merely unverifiable:
                        the prose checked and explicitly rejected a
                        destination for WORTH_WATCHING, so there is no
                        judgment call left to defer -- there is no valid
                        answer at all.

TRANSCRIPTION, NOT A LIVE PARSE OF THE PROSE FILE (read this before
changing REFRAME_MAP): cron_daily_runtime.txt's REFRAME MAPPING (the
block beginning "REFRAME MAPPING — apply ONLY when the content's
natural format is on" and ending just before "FORMAT BLUEPRINTS (F81,
added 2026-09-11") is narrative law text -- conditions, exceptions, and
cross-references in prose, not a table or any structured format.
REFRAME_MAP below is a HAND TRANSCRIPTION of that prose into a static
dict, done once, by a human reading the law text. It is not generated
from the file and cannot detect a future edit to the prose on its own --
see test_reframe_destination_guard.py's TestMapStaysInSyncWithProse
class, which asserts every key in REFRAME_MAP still appears as a "->
reframe" source token somewhere in cron_daily_runtime.txt, so a rename
or removal in the prose fails the test loudly instead of leaving this
dict silently stale. That test catches DELETIONS/RENAMES in the prose;
it cannot catch a prose edit that changes a pairing's condition or
destination while keeping the same source token name -- that class of
drift still requires a human re-reading both sides on any REFRAME
MAPPING edit.

F89 (2026-09-12): every in-file citation below used to be a line number
("cron_daily_runtime.txt lines N-M" or "Lines N-M."), and all 17 of them
had already gone stale by the time this was audited -- the file gets
edited and nothing checked whether the cited ranges still resolved to
the described content. Citations are now CONTENT ANCHORS: a short, verbatim quoted
fragment from the cited passage, looked up in REFRAME_CITATION_ANCHORS
below by an id. An anchor breaks LOUDLY (the anchor test fails to find
the string) instead of silently pointing at whatever now happens to sit
at some stale line number. See TestReframeCitationAnchorsResolve in
test_reframe_destination_guard.py, modeled directly on
TestMapStaysInSyncWithProse's same shape: read the runtime file once,
assert every anchor string is still `in` it.
"""

from __future__ import annotations

from typing import Any

# CONTENT ANCHORS (F89, 2026-09-12) -- replaces the old REFRAME_MAPPING_BLOCK
# line-number tuple, which had to be hand-updated on every edit to
# cron_daily_runtime.txt and was never checked for staleness (that constant
# was ALSO, separately, never read by any code -- it was pure documentation
# wearing a tuple's clothing). Each entry here is a short, verbatim string
# guaranteed present in cron_daily_runtime.txt as of this commit.
# TestReframeCitationAnchorsResolve (test_reframe_destination_guard.py)
# asserts every value here is still `in` the runtime file; if that test
# fails, re-read the REFRAME MAPPING section (search "REFRAME MAPPING —")
# and update BOTH the anchor string here and whatever this docstring/entry
# claims about it.
REFRAME_CITATION_ANCHORS: dict[str, str] = {
    # The whole REFRAME MAPPING block. Too broad to quote in full, so
    # anchored on its header line and its terminator (the next section)
    # rather than the content between.
    "reframe_mapping_block_header": (
        "REFRAME MAPPING — apply ONLY when the content's natural format is on"
    ),
    "reframe_mapping_block_terminator": (
        "FORMAT BLUEPRINTS (F81, added 2026-09-11"
    ),
    # EPISODE_MOMENT / THE_MOMENT -> CHARACTER_DIVE / THEORY_SPECULATION / COMMENTARY
    "episode_moment_the_moment_unconditional": (
        "EPISODE_MOMENT / THE_MOMENT on cooldown -> reframe as CHARACTER_DIVE"
    ),
    # VILLAIN_DEFENSE / ORIGIN_STORY -> WRONG_TAKE
    "villain_defense_origin_story_to_wrong_take": (
        "VILLAIN_DEFENSE / ORIGIN_STORY on cooldown -> reframe as WRONG_TAKE"
    ),
    # SEASON_RATING / SEASON_ROUNDUP -> WATCH_RANK / WORTH_WATCHING
    "season_rating_season_roundup_to_watch_rank": (
        "SEASON_RATING / SEASON_ROUNDUP on cooldown -> reframe as WATCH_RANK"
    ),
    # THEORY_SPECULATION -> COMMENTARY / CHARACTER_DIVE
    "theory_speculation_to_commentary_character_dive": (
        "THEORY_SPECULATION on cooldown -> reframe as COMMENTARY or"
    ),
    # The CONFIRMED VIABLE 2026-09-11 note resolving THEORY_SPECULATION's
    # reframe as unconditional rather than a third judgment-call case.
    "theory_speculation_confirmed_viable_note": (
        "CONFIRMED VIABLE 2026-09-11 now that CHARACTER_DIVE has its own"
    ),
    # WATCH_RANK -> SEASON_ROUNDUP's per-candidate source-availability
    # condition. F89 (2026-09-12): originally anchored on the fragments
    # "a WATCH_RANK candidate may only reframe into" and "not a guarantee
    # the mapping table" -- both unique only incidentally (nothing else
    # happens to phrase it that way today), not because the fragment
    # itself carries the cited meaning. Replaced with clauses that state
    # the actual condition and its actual consequence, so a reword of
    # nearby boilerplate can't silently leave a now-meaningless anchor
    # matching by accident, and a genuine change to the condition or its
    # consequence breaks the anchor as it should.
    "watch_rank_to_season_roundup_condition": (
        "EVERY show that would appear in the roundup's"
    ),
    # The actual per-candidate consequence when the condition above is not
    # met: the pairing is unavailable and the mechanism falls back to
    # existing behavior. This is the clause that would have to survive for
    # the citation to still be pointing at a real, current conditional
    # gate rather than a stale or since-removed one.
    "watch_rank_to_season_roundup_no_source_consequence": (
        "lacks a qualifying independent source, this pairing is NOT available"
    ),
    # CHARACTER_DIVE -> VILLAIN_DEFENSE's "genuinely disliked or debate-magnet" condition.
    "character_dive_to_villain_defense_condition": (
        "applies when the character is genuinely disliked or a debate-magnet"
    ),
    # WORTH_WATCHING's deliberate empty reframe list ("DROPPED, CHECKED AND REJECTED").
    "worth_watching_no_reframe_destination": (
        "No reframe destination exists for WORTH_WATCHING in this"
    ),
    # V-71's required rejection_reason prefix rule.
    "reframe_log_prefix_rule": (
        "blackout_reframe: \" (hard per-show blackout), followed by the real detail"
    ),
}

# format_type (str) -> list of destination entries. Each destination entry
# is either:
#   ("FORMAT_NAME", None)       -- unconditionally permitted (PASS)
#   ("FORMAT_NAME", "condition text")  -- permitted, but carries a judgment
#                                          call this module cannot evaluate
#                                          (PASS_WITH_CONDITION); condition
#                                          text is surfaced verbatim in the
#                                          check detail.
#
# A source format_type not present as a key here at all is a schema gap in
# this transcription, not a real "no reframe path" -- see
# guard_reframe_pairing()'s handling of missing keys, which raises rather
# than silently treating "not transcribed" the same as WORTH_WATCHING's
# real, deliberate empty list.
REFRAME_MAP: dict[str, list[tuple[str, str | None]]] = {
    # Anchor: episode_moment_the_moment_unconditional. All three
    # destinations are unconditional in the prose -- no "only if" language
    # attached to any.
    "EPISODE_MOMENT": [
        ("CHARACTER_DIVE", None),
        ("THEORY_SPECULATION", None),
        ("COMMENTARY", None),
    ],
    "THE_MOMENT": [
        ("CHARACTER_DIVE", None),
        ("THEORY_SPECULATION", None),
        ("COMMENTARY", None),
    ],
    # Anchor: villain_defense_origin_story_to_wrong_take. Single, unconditional destination.
    "VILLAIN_DEFENSE": [
        ("WRONG_TAKE", None),
    ],
    "ORIGIN_STORY": [
        ("WRONG_TAKE", None),
    ],
    # Anchor: season_rating_season_roundup_to_watch_rank. Both destinations
    # unconditional (the prose reminds the reader that Law #98's/#158's OWN
    # rules still apply in full to the new format, but that is true of every
    # reframe per the prefix rule anchor below and is not a reframe-specific
    # condition -- so it is not encoded as one here).
    "SEASON_RATING": [
        ("WATCH_RANK", None),
        ("WORTH_WATCHING", None),
    ],
    "SEASON_ROUNDUP": [
        ("WATCH_RANK", None),
        ("WORTH_WATCHING", None),
    ],
    # Anchor: theory_speculation_to_commentary_character_dive. Both
    # destinations unconditional as reframe PAIRINGS -- the prose's caveat
    # here is about what the reframed VO must DROP (the speculative
    # conclusion), not about a precondition on whether the pairing is
    # allowed to fire at all. That is a content-authoring constraint on the
    # new format (applies to every reframe, per the reframe_log_prefix_rule
    # anchor's surrounding passage), not a per-pairing judgment call like
    # the two real conditional cases below -- so this is PASS, not
    # PASS_WITH_CONDITION.
    #
    # THE OTHER READING WAS CONSIDERED AND REJECTED, not just unweighed: a
    # reframe that requires discarding the candidate's central claim
    # entirely (the speculative conclusion itself, not merely its framing)
    # is arguably different IN KIND from a reframe that only changes angle
    # while keeping the same underlying claim -- e.g. EPISODE_MOMENT ->
    # COMMENTARY keeps "this scene happened and here's the industry angle,"
    # while THEORY_SPECULATION -> COMMENTARY/CHARACTER_DIVE drops the one
    # thing that made it a THEORY_SPECULATION candidate at all. That
    # argument would treat this as a third real conditional case
    # ("permitted only if the underlying evidence can support a
    # non-speculative claim on its own"). It is rejected here because the
    # prose's own CONFIRMED VIABLE note (anchor:
    # theory_speculation_confirmed_viable_note) already resolves
    # this affirmatively and unconditionally for both destinations: it
    # states the Catalyst Event / Internal Conflict beats "can hold the
    # same underlying evidence a theory would have used without needing to
    # state or hedge a speculative conclusion at all" -- i.e. the prose
    # itself already did the per-candidate evidentiary check this module
    # would otherwise defer, and reached a general, unconditional answer,
    # not a per-candidate one left open. If a future prose edit walks back
    # or narrows that CONFIRMED VIABLE note, this entry should be revisited
    # and may need to become conditional.
    "THEORY_SPECULATION": [
        ("COMMENTARY", None),
        ("CHARACTER_DIVE", None),
    ],
    # Anchor: watch_rank_to_season_roundup_condition /
    # watch_rank_to_season_roundup_no_source_consequence. WORTH_WATCHING is
    # unconditional. SEASON_ROUNDUP is the first REAL conditional case: the
    # prose explicitly states "this is a per-candidate check at draft time,
    # not a guarantee the mapping table can make in advance" -- every named
    # show needing its own distinct, non-reused, non-encyclopedic, dated
    # source is a genuine per-candidate fact-verification question, not a
    # static lookup.
    "WATCH_RANK": [
        ("WORTH_WATCHING", None),
        (
            "SEASON_ROUNDUP",
            "valid only if EVERY show that would appear in the roundup's "
            "MVPs/Fumbles beats has its own distinct, non-reused, "
            "non-encyclopedic, dated source available -- a per-candidate "
            "check at draft time, not something this table can guarantee "
            "in advance (cron_daily_runtime.txt, anchor: "
            "watch_rank_to_season_roundup_no_source_consequence).",
        ),
    ],
    # Anchor: character_dive_to_villain_defense_condition. ORIGIN_STORY is
    # unconditional. VILLAIN_DEFENSE is the second REAL conditional case:
    # the prose says explicitly "not a default: it only applies when the
    # character is genuinely disliked or a debate-magnet subject" -- a
    # subjective content judgment about a specific character, not a lookup
    # this module can perform.
    "CHARACTER_DIVE": [
        ("ORIGIN_STORY", None),
        (
            "VILLAIN_DEFENSE",
            "conditional, not a default: valid only if the character is "
            "genuinely disliked or a debate-magnet subject (Law #85 item "
            "6's own scope). Do not force a well-liked or neutral "
            "character into this frame just to hit the format "
            "(cron_daily_runtime.txt, anchor: "
            "character_dive_to_villain_defense_condition).",
        ),
    ],
    # Lines added 2026-09-12 (FIX 1, F86 closure). FACT_DROP had NO reframe
    # entry at all until now -- not a deliberate empty list like
    # WORTH_WATCHING below, just a genuine gap (F86): the format's own
    # blueprint (Law #85 hierarchy rank 4) states outright that its 42 real
    # sends "span lore explainers and breaking-news facts alike," i.e. it
    # covers two content shapes under one format_type. That split is exactly
    # what determines the two destinations here -- each takes the HALF of
    # FACT_DROP's real usage that matches its own real objective, not an
    # arbitrary pairing added for symmetry with the other entries:
    #   - COMMENTARY takes the breaking-news half. COMMENTARY's own
    #     blueprint objective ("industry, production, and business events...
    #     as the primary use case," citing a Crunchyroll exclusivity change,
    #     an AoT Day announcement, a Jump circulation drop) already covers a
    #     breaking-news FACT_DROP candidate's shape directly -- this is not a
    #     stretch pairing, it is the SAME kind of content COMMENTARY already
    #     documents real usage for. No condition attached: nothing about a
    #     breaking-news fact reframed as COMMENTARY requires a judgment call
    #     this module can't make -- unlike WRONG_TAKE below, every
    #     breaking-news FACT_DROP candidate qualifies, since COMMENTARY's
    #     objective is not restricted to some subset of news.
    #   - WRONG_TAKE takes the lore-explainer half, CONDITIONALLY, same shape
    #     as CHARACTER_DIVE -> VILLAIN_DEFENSE above. WRONG_TAKE's own
    #     blueprint objective requires "a popular, incorrect community
    #     take/myth... using a specific sourced correction" -- not every
    #     lore-explainer FACT_DROP fact corrects a real, existing community
    #     myth (some are simply reveals nobody had gotten wrong yet). Where
    #     one does, the reframe is a clean fit; where one doesn't, forcing it
    #     would fabricate a myth to debunk, which WRONG_TAKE's own objective
    #     does not permit. Checked against WRONG_TAKE's other rule too: its
    #     14-day same-myth blackout is a pre-existing WRONG_TAKE constraint,
    #     not a new one this pairing introduces -- it applies here exactly as
    #     it already applies to every other WRONG_TAKE candidate, reframed or
    #     not.
    # Neither pairing was added by assuming symmetry with the two-destination
    # shape used elsewhere in this table -- both were checked against the
    # destination format's own real objective first, per this module's
    # stated transcription discipline (module docstring, "a pairing that
    # would force a rule violation is omitted rather than included for
    # symmetry").
    "FACT_DROP": [
        ("COMMENTARY", None),
        (
            "WRONG_TAKE",
            "valid only if the underlying fact actually corrects a real, "
            "existing community myth or widespread incorrect take -- not "
            "every FACT_DROP reveal has one. Do not fabricate a myth to "
            "debunk just to fit this format (cron_daily_runtime.txt "
            "FACT_DROP blueprint, 'Objective' clause). WRONG_TAKE's own "
            "14-day same-myth blackout still applies in full to the "
            "reframed candidate, unchanged by this pairing.",
        ),
    ],
    # Anchor: worth_watching_no_reframe_destination. DELIBERATE EMPTY LIST
    # -- READ BEFORE "FIXING." The prose title for this entry is literally
    # "DROPPED, CHECKED AND
    # REJECTED": SLEPT_ON/HIDDEN_GEM was considered as a destination and
    # explicitly rejected on two independent grounds -- (1) SLEPT_ON/
    # HIDDEN_GEM's own scope is restricted to underrated/overlooked shows,
    # which is a real content-eligibility constraint a rewritten VO cannot
    # satisfy for a WORTH_WATCHING candidate without fabricating obscurity;
    # (2) SLEPT_ON/HIDDEN_GEM's Call-Out Hook and Masterclass Breakdown
    # beats are comparative BY DESIGN, while Law #158 mechanically BANS
    # comparative language in WORTH_WATCHING's own fields -- so the two
    # formats are incompatible in MECHANISM, not just scope. The prose
    # states outright: "No reframe destination exists for WORTH_WATCHING in
    # this mapping." This is why WORTH_WATCHING is the one FAIL case in
    # this module rather than a PASS_WITH_CONDITION: there is no judgment
    # call to defer to Law #165 review here, because there is no candidate
    # destination at all, not even a conditional one. If a future prose
    # edit adds a real destination for WORTH_WATCHING, update this entry
    # AND update guard_reframe_pairing()'s WORTH_WATCHING-specific FAIL
    # messaging below, which currently asserts this is permanent.
    "WORTH_WATCHING": [],
}


class ReframeGuardResult:
    """Result of guard_reframe_pairing(). `outcome` is one of "PASS",
    "PASS_WITH_CONDITION", or "FAIL". `detail` is a human-readable string
    suitable for direct inclusion in a validator report line."""

    def __init__(self, outcome: str, detail: str):
        if outcome not in ("PASS", "PASS_WITH_CONDITION", "FAIL"):
            raise ValueError(f"invalid outcome: {outcome!r}")
        self.outcome = outcome
        self.detail = detail

    def __repr__(self) -> str:
        return f"ReframeGuardResult({self.outcome!r}, {self.detail!r})"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ReframeGuardResult)
            and self.outcome == other.outcome
            and self.detail == other.detail
        )


def guard_reframe_pairing(reframe_from: str, reframe_to: str) -> ReframeGuardResult:
    """Check whether reframing FROM `reframe_from` TO `reframe_to` is
    permitted per REFRAME_MAP, and return one of the three outcomes.

    Raises ValueError if `reframe_from` is not a key in REFRAME_MAP at
    all -- that is a transcription gap in this module (a format_type the
    hand-transcription never covered), not a real "no destination exists"
    finding. Only WORTH_WATCHING's real, deliberate empty list produces a
    FAIL; every other untranscribed format_type is a bug in this module,
    surfaced loudly rather than silently treated as equivalent to
    WORTH_WATCHING's checked-and-rejected case.
    """
    if reframe_from not in REFRAME_MAP:
        raise ValueError(
            f"{reframe_from!r} is not a key in REFRAME_MAP -- this is a gap "
            f"in the hand transcription (see module docstring), not a real "
            f"finding that no reframe destination exists. Only "
            f"WORTH_WATCHING has a genuine, deliberate empty destination "
            f"list. Add {reframe_from!r} to REFRAME_MAP by re-reading "
            f"cron_daily_runtime.txt's REFRAME MAPPING section before "
            f"treating this pairing as invalid."
        )

    destinations = REFRAME_MAP[reframe_from]

    if not destinations:
        # The one genuine hard FAIL: a checked-and-rejected empty list.
        return ReframeGuardResult(
            "FAIL",
            f"{reframe_from} -> {reframe_to} is not permitted: "
            f"{reframe_from} has NO valid reframe destination "
            f"(cron_daily_runtime.txt, anchor: "
            f"worth_watching_no_reframe_destination -- checked and "
            f"rejected SLEPT_ON/HIDDEN_GEM on scope AND mechanism "
            f"grounds; this is categorical, not a per-candidate judgment "
            f"call). A candidate whose natural format is {reframe_from} "
            f"and is on cooldown or blacked out cannot be reframed at "
            f"all -- existing fallback behavior applies (a different "
            f"show, or holding the slot).",
        )

    for dest_format, condition in destinations:
        if dest_format == reframe_to:
            if condition is None:
                return ReframeGuardResult(
                    "PASS",
                    f"{reframe_from} -> {reframe_to} is an unconditionally "
                    f"permitted reframe pairing.",
                )
            return ReframeGuardResult(
                "PASS_WITH_CONDITION",
                f"{reframe_from} -> {reframe_to} is a conditional pairing: "
                f"{condition} Not mechanically verifiable; confirm during "
                f"Law #165 review.",
            )

    allowed = ", ".join(d for d, _ in destinations)
    return ReframeGuardResult(
        "FAIL",
        f"{reframe_from} -> {reframe_to} is not in the allowed reframe "
        f"set for {reframe_from}. Allowed destination(s): {allowed}.",
    )


# --- V-71: reframe rejection_reason prefix enforcement ---------------------

REQUIRED_REFRAME_PREFIXES = ("cooldown_reframe: ", "blackout_reframe: ")


def check_reframe_log_prefix(rejection_reason: str) -> ReframeGuardResult:
    """V-71: when a reframe fires, the REJECTED natural-fit event's
    rejection_reason MUST start with the literal prefix "cooldown_reframe: "
    or "blackout_reframe: " (cron_daily_runtime.txt, anchor:
    reframe_log_prefix_rule). This is a plain, unconditional string-prefix
    check -- there is no judgment call here, so this function only ever
    returns PASS or FAIL, never PASS_WITH_CONDITION.

    This function does not decide WHETHER a given rejection was a reframe
    in the first place -- that is determined by the caller (typically: a
    rejection immediately followed by a "selected" event for the mapped
    destination format in the same slot). This function only checks that,
    given a rejection_reason the caller has already identified as
    reframe-driven, the required machine-distinguishable prefix is
    present.
    """
    if rejection_reason is None:
        return ReframeGuardResult(
            "FAIL",
            "V-71: reframe rejection_reason is missing entirely -- cannot "
            "carry the required 'cooldown_reframe: ' / 'blackout_reframe: ' "
            "prefix.",
        )
    if rejection_reason.startswith(REQUIRED_REFRAME_PREFIXES):
        return ReframeGuardResult(
            "PASS",
            "V-71: reframe rejection_reason carries a required "
            "machine-distinguishable prefix.",
        )
    return ReframeGuardResult(
        "FAIL",
        f"V-71: reframe rejection_reason does not start with "
        f"'cooldown_reframe: ' or 'blackout_reframe: ' "
        f"(cron_daily_runtime.txt, anchor: reframe_log_prefix_rule). "
        f"Got: {rejection_reason!r}. "
        f"Without one of these exact prefixes, this reads to a future "
        f"auditor as a genuine merit-based rejection, not a "
        f"format-unavailability reframe.",
    )

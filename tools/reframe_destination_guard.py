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
changing REFRAME_MAP): cron_daily_runtime.txt's REFRAME MAPPING
(lines 678-758 as of the commit that added this module) is narrative law
text -- conditions, exceptions, and cross-references in prose, not a
table or any structured format. REFRAME_MAP below is a HAND
TRANSCRIPTION of that prose into a static dict, done once, by a human
reading the law text. It is not generated from the file and cannot
detect a future edit to the prose on its own -- see
test_reframe_destination_guard.py's TestMapStaysInSyncWithProse class,
which asserts every key in REFRAME_MAP still appears as a "-> reframe"
source token somewhere in cron_daily_runtime.txt, so a rename or removal
in the prose fails the test loudly instead of leaving this dict silently
stale. That test catches DELETIONS/RENAMES in the prose; it cannot catch
a prose edit that changes a pairing's condition or destination while
keeping the same source token name -- that class of drift still requires
a human re-reading both sides on any REFRAME MAPPING edit.

Each entry below cites the exact cron_daily_runtime.txt line range it was
transcribed from, as of the same commit.
"""

from __future__ import annotations

from typing import Any

# Source line anchor for the whole REFRAME MAPPING block, as of the commit
# that added this module -- if this drifts significantly, the per-entry
# line citations below should be re-checked too.
REFRAME_MAPPING_BLOCK = ("cron_daily_runtime.txt", 678, 758)

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
    # Lines 688-693. All three destinations are unconditional in the prose --
    # no "only if" language attached to any of them.
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
    # Lines 694-696. Single, unconditional destination.
    "VILLAIN_DEFENSE": [
        ("WRONG_TAKE", None),
    ],
    "ORIGIN_STORY": [
        ("WRONG_TAKE", None),
    ],
    # Lines 697-701. Both destinations unconditional (the prose reminds the
    # reader that Law #98's/#158's OWN rules still apply in full to the new
    # format, but that is true of every reframe per lines 759-763 and is not
    # a reframe-specific condition -- so it is not encoded as one here).
    "SEASON_RATING": [
        ("WATCH_RANK", None),
        ("WORTH_WATCHING", None),
    ],
    "SEASON_ROUNDUP": [
        ("WATCH_RANK", None),
        ("WORTH_WATCHING", None),
    ],
    # Lines 702-713. Both destinations unconditional as reframe PAIRINGS --
    # the prose's caveat here is about what the reframed VO must DROP
    # (the speculative conclusion), not about a precondition on whether the
    # pairing is allowed to fire at all. That is a content-authoring
    # constraint on the new format (see lines 759-763, applies to every
    # reframe), not a per-pairing judgment call like the two real
    # conditional cases below -- so this is PASS, not PASS_WITH_CONDITION.
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
    # prose's own CONFIRMED VIABLE note (lines 708-713) already resolves
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
    # Lines 714-728. WORTH_WATCHING is unconditional. SEASON_ROUNDUP is the
    # first REAL conditional case: the prose explicitly states at line 727
    # "this is a per-candidate check at draft time, not a guarantee the
    # mapping table can make in advance" -- every named show needing its own
    # distinct, non-reused, non-encyclopedic, dated source is a genuine
    # per-candidate fact-verification question, not a static lookup.
    "WATCH_RANK": [
        ("WORTH_WATCHING", None),
        (
            "SEASON_ROUNDUP",
            "valid only if EVERY show that would appear in the roundup's "
            "MVPs/Fumbles beats has its own distinct, non-reused, "
            "non-encyclopedic, dated source available -- a per-candidate "
            "check at draft time, not something this table can guarantee "
            "in advance (cron_daily_runtime.txt lines 719-727).",
        ),
    ],
    # Lines 729-737. ORIGIN_STORY is unconditional. VILLAIN_DEFENSE is the
    # second REAL conditional case: the prose says explicitly "not a
    # default: it only applies when the character is genuinely disliked or
    # a debate-magnet subject" -- a subjective content judgment about a
    # specific character, not a lookup this module can perform.
    "CHARACTER_DIVE": [
        ("ORIGIN_STORY", None),
        (
            "VILLAIN_DEFENSE",
            "conditional, not a default: valid only if the character is "
            "genuinely disliked or a debate-magnet subject (Law #85 item "
            "6's own scope). Do not force a well-liked or neutral "
            "character into this frame just to hit the format "
            "(cron_daily_runtime.txt lines 732-737).",
        ),
    ],
    # Lines 738-758. DELIBERATE EMPTY LIST -- READ BEFORE "FIXING." The
    # prose title for this entry is literally "DROPPED, CHECKED AND
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
            f"(cron_daily_runtime.txt lines 738-758 -- checked and "
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
    or "blackout_reframe: " (cron_daily_runtime.txt lines 764-779). This
    is a plain, unconditional string-prefix check -- there is no judgment
    call here, so this function only ever returns PASS or FAIL, never
    PASS_WITH_CONDITION.

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
        f"(cron_daily_runtime.txt lines 771-775). Got: {rejection_reason!r}. "
        f"Without one of these exact prefixes, this reads to a future "
        f"auditor as a genuine merit-based rejection, not a "
        f"format-unavailability reframe.",
    )

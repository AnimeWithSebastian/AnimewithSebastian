"""
Deterministic clip_descriptions rendering helper (permanent pipeline fix,
2026-08-05, third occurrence of the season/episode surfacing gap first found
2026-08-02 for One Piece/MHA, recurred 2026-08-05 for Bleach TYBW).

ROOT CAUSE THIS FIXES: clips[].clip_locate (structured, validator-enforced
under Law #73 UPDATE 5) and clip_descriptions (free text, the field the
email actually sends) are two independent representations of the same fact.
Nothing forced them to agree, so a verified clip's season/episode could be
dropped from the sent email while still passing every existing check.

WHAT THIS MODULE DOES: given a package's clips[] list and an already-drafted
base clip_descriptions string containing one CUT block per clip (the real,
demonstrated shape across every real sent manifest since 2026-07-30 --
confirmed via repo history spanning One Piece/MHA, Black Clover/Akane-banashi,
HxH/Berserk, JJK/Chainsaw Man, Tanya/Link Click), this module verifies that
each scene_verified=true clip's season/episode already appears in its own
CUT segment, and appends a normalized " -- S{season}E{episode}" tag to any
CUT segment that is missing one. It does NOT rewrite scene/reason text, does
NOT touch clips with scene_verified=false (correctly: no clip_locate exists
for them, nothing to surface), and never invents a location -- it only ever
copies clip_locate's own season/episode straight from the structured field.

WHAT THIS MODULE DOES NOT DO: it does not replace free-text authoring of
clip_descriptions. The scene/reason/why-this-cut prose is still written by
the drafting pass, same as always. This is a post-processing safety net
that runs AFTER drafting and BEFORE the manifest is considered final --
exactly the same relationship append_send_batch.py has to the send step:
a deterministic, mechanical pass that cannot silently regress no matter
who or what wrote the free text it is checking.

USAGE (intended call site: the manifest-building step, right before the
manifest is written / the validator is run):

    from tools.render_clip_descriptions import ensure_clip_locations

    pkg["clip_descriptions"] = ensure_clip_locations(
        pkg["clip_descriptions"], pkg["clips"]
    )

This is idempotent: calling it twice on already-correct text is a no-op.
"""

from __future__ import annotations

import re
from typing import Any

# Recognizes only the location-token formats actually demonstrated across
# real sent packages: "S4E41" / "S 4 E 41" and "Season 4, Episode 41" /
# "Season 4 Episode 41".
#
# BUG FIX (2026-08-05, flagged in adversarial review): this regex previously
# had a third alternative for a bare "NxN" format ("4x41"). It had no word
# boundaries at all, so ordinary prose like "a 4x4 truck kicks up dust" or a
# resolution/aspect-ratio mention like "1920x1080" or "16x9" false-positived
# as a location tag. Adding word boundaries alone did not fix this: "4x4"
# and "1920x1080" both have clean boundaries and would still false-positive
# on any boundary-only fix. A repo-wide check of every sent script and the
# live production manifest confirmed the bare NxN format has never actually
# been used as a real clip-location tag in production (the only literal
# "NxN"-shaped substring found anywhere, "1x41", was embedded inside a
# source URL slug, not a clip_descriptions tag) -- so the alternative is
# removed entirely rather than patched, eliminating the false-positive risk
# with zero loss of real functionality.
_LOCATION_TOKEN_RE = re.compile(
    r"""
    (?:
        S\s*(?P<s1>\d+)\s*E\s*(?P<e1>\d+)                       # S4E41 / S 4 E 41
      | Season\s+(?P<s2>\d+)\s*,?\s*Episode\s+(?P<e2>\d+)        # Season 4, Episode 41
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Splits a clip_descriptions string into one segment per CUT. Matches the
# real demonstrated shapes: "CUT 1 ...", "CUT1 ...", "CUT 1 (...)". Segments
# run up to (not including) the next CUT marker or end of string.
_CUT_SPLIT_RE = re.compile(r"(?=CUT\s*\d+\b)", re.IGNORECASE)
_CUT_LABEL_RE = re.compile(r"^CUT\s*(\d+)\b", re.IGNORECASE)

# Matches ONLY the exact tag shape this module itself appends (" \u2014 S{n}E{n}",
# optionally followed by a trailing period). Used to safely replace a stale
# machine-generated tag on re-verification without ever touching
# hand-authored prose this module did not write.
_GENERATED_TAG_RE = re.compile(r"\s\u2014\sS(?P<s>\d+)E(?P<e>\d+)\.?$")


def _extract_location_tokens(text: str) -> set[tuple[str, str]]:
    """Returns the set of (season, episode) tuples literally present in text,
    normalized to plain digit strings so '04' and '4' compare equal."""
    tokens: set[tuple[str, str]] = set()
    for m in _LOCATION_TOKEN_RE.finditer(text or ""):
        season = m.group("s1") or m.group("s2")
        episode = m.group("e1") or m.group("e2")
        if season is not None and episode is not None:
            tokens.add((str(int(season)), str(int(episode))))
    return tokens


def _split_into_cut_segments(clip_descriptions: str) -> list[str]:
    """Splits free text into per-CUT segments. If no 'CUT N' markers are
    found at all (older non-CUT-labeled prose style), returns a single
    segment containing the whole string -- callers should treat that as
    'cannot map segments to clips' rather than force a split."""
    if not clip_descriptions:
        return []
    parts = [seg for seg in _CUT_SPLIT_RE.split(clip_descriptions) if seg.strip()]
    return parts if parts else [clip_descriptions]


def ensure_clip_locations(clip_descriptions: str, clips: list[dict[str, Any]]) -> str:
    """Given the drafted clip_descriptions text and the package's clips[],
    returns a version of clip_descriptions where every scene_verified=true
    clip's own CUT segment contains its season/episode as a literal token.

    Matching a CUT segment to a clip is done by CUT number (1-indexed,
    matching clips[] order) when the text uses 'CUT N' markers -- the
    real, demonstrated format across every sent manifest since 2026-07-30.
    If the text does not use CUT markers at all, this function returns the
    text unchanged and relies on the caller/validator to flag the gap
    separately, rather than guessing where to insert a tag.

    Re-verification safe: if a segment already carries a machine-appended
    tag from a PRIOR call to this function (recognizable by the
    _GENERATED_TAG_RE marker below) and clip_locate has since changed
    (e.g. a correction moved a clip from episode 9 to episode 41), the
    stale generated tag is replaced rather than left alongside the new
    one. Hand-authored location text that was part of the original prose
    (not appended by this function) is never touched or removed -- if it
    already contains the CURRENT wanted token, ensure_clip_locations
    leaves the segment alone (idempotent); if it contains a DIFFERENT
    hand-authored token, this function still appends the current one
    rather than risk deleting authored prose it did not write.
    """
    segments = _split_into_cut_segments(clip_descriptions)
    if len(segments) != len(clips):
        # Can't safely map segments 1:1 to clips. len < len(clips) is the
        # older prose style or a genuine count mismatch. len > len(clips) is
        # an over-split: _CUT_SPLIT_RE fires on every "CUT\s*\d+" occurrence,
        # including a mid-sentence reference in another cut's own prose (e.g.
        # "the closing beat mirrors CUT1's establishing shot" inside CUT4's
        # segment) -- a real phrasing style already used in sent scripts.
        # Either direction means the mapping is unsafe -- do not guess.
        return clip_descriptions

    rebuilt: list[str] = []
    for i, clip in enumerate(clips):
        segment = segments[i] if i < len(segments) else ""
        if not isinstance(clip, dict) or clip.get("scene_verified") is not True:
            rebuilt.append(segment)
            continue

        clip_locate = clip.get("clip_locate")
        if not isinstance(clip_locate, dict):
            # Shape violation is the validator's job (Law #73 UPDATE 5) --
            # this function only surfaces data that already exists.
            rebuilt.append(segment)
            continue

        season, episode = clip_locate.get("season"), clip_locate.get("episode")
        if season in (None, "") or not isinstance(episode, int) or isinstance(episode, bool):
            rebuilt.append(segment)
            continue

        wanted = (str(int(season)), str(int(episode))) if str(season).isdigit() else None
        if wanted is None:
            rebuilt.append(segment)
            continue

        # Strip a stale MACHINE-GENERATED tag first (safe: this function is
        # the only writer of this exact marker shape), so a re-verification
        # that changes clip_locate doesn't leave two generated tags stacked.
        generated_match = _GENERATED_TAG_RE.search(segment)
        working_segment = segment
        had_trailing_period = False
        if generated_match:
            existing_generated_token = (generated_match.group("s"), generated_match.group("e"))
            if existing_generated_token != wanted:
                had_trailing_period = segment.rstrip().endswith(".")
                working_segment = _GENERATED_TAG_RE.sub("", segment).rstrip()
                if had_trailing_period:
                    working_segment += "."
            else:
                rebuilt.append(segment)  # already correct -- idempotent, no change
                continue

        existing_tokens = _extract_location_tokens(working_segment)
        if wanted in existing_tokens:
            rebuilt.append(working_segment)  # hand-authored text already has it
            continue

        tag = f" \u2014 S{season}E{episode}"
        stripped = working_segment.rstrip()
        if stripped.endswith("."):
            rebuilt.append(stripped[:-1] + tag + ".")
        else:
            rebuilt.append(stripped + tag)

    return " ".join(seg.strip() for seg in rebuilt if seg.strip())

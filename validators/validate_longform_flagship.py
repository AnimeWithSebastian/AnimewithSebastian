#!/usr/bin/env python3
"""Deterministic preflight validator for a LONG-FORM FLAGSHIP video (Law #146).

Long-form flagships are a DIFFERENT product from the 30-second Shorts and must NOT
be graded by the Shorts laws. The Shorts validator (validate_dual_package.py) enforces
a fixed 30s edit, per-cut timings that tile 0->30s (Law #140), and an explicit
seamless loop (Law #141); NONE of those apply here. This validator instead enforces
the flagship requirements grounded in the channel's own analytics (no long-form
baseline exists yet; absolute watch time is the goal) and official YouTube guidance
(descriptions/chapters/playlists drive search + retention; face-cam is permitted for
long-form; keyword-first descriptions help discovery).

FAIL CLOSED: any failed check exits non-zero. This validator is intentionally separate
from the Shorts pipeline so the two products can never be cross-checked with the wrong
laws.

Requirements enforced:
  - content_type == "longform"; duration in the 8-12 min band (absolute watch time).
  - NO Shorts-only fields required (no capcut_target_sec / clips-tiling / loop_line).
    If a Shorts loop/timing field is present it is flagged (wrong product).
  - Chapters: >=3, the first at 0:00, strictly increasing start times.
  - Description: keyword-rich first lines (>=1 primary keyword in the first line).
  - A playlist link AND a pinned next-video/playlist link (follow-on retention).
  - An explicit comment prompt (question).
  - Teaser Shorts (0, or 1-3 — M5 cap) may be planned ONLY after the flagship URL exists.
  - Model routing: Claude Fable 5 is permitted for a flagship script (Law #137
    allowlist); if model is set it must be Sonnet 5.0 or Fable 5.
  - Recipient exactly hero_or_villain@outlook.com.

Usage:
    python3 validators/validate_longform_flagship.py <flagship_manifest.json>
    python3 validators/validate_longform_flagship.py --schema
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

RECIPIENT = "hero_or_villain@outlook.com"
LONGFORM_MIN_SEC = 8 * 60   # 480
LONGFORM_MAX_SEC = 12 * 60  # 720
ALLOWED_MODELS = ("claude sonnet 5.0", "claude fable 5")
# M5: teasers are capped at <=3/week until funnel evidence justifies more. The feed
# audience is ~99% new viewers with no attachment to the flagship, so a large teaser
# block spends Shorts slots on derivative content before any funnel signal exists. A
# teaser plan is optional (0), but if present it must be 1-3.
TEASER_MIN, TEASER_MAX = 1, 3

# Shorts-only fields that must NOT appear on a flagship (wrong product if present).
SHORTS_ONLY_FIELDS = ("capcut_target_sec", "total_clip_time_sec", "loop_line",
                      "loop_transition", "loop_read_aloud_pass")


@dataclass
class Result:
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, bool(ok), detail))

    @property
    def ok(self) -> bool:
        return all(ok for _, ok, _ in self.checks)

    def failures(self) -> list[tuple[str, bool, str]]:
        return [c for c in self.checks if not c[1]]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_flagship(m: dict[str, Any]) -> Result:
    r = Result()

    r.add("recipient is exactly correct", m.get("recipient") == RECIPIENT,
          f"recipient={m.get('recipient')!r}")
    r.add("content_type is 'longform'", _norm(m.get("content_type", "")) == "longform",
          f"content_type={m.get('content_type')!r}")

    dur = m.get("duration_sec")
    r.add(f"duration in the {LONGFORM_MIN_SEC//60}-{LONGFORM_MAX_SEC//60} min band",
          _is_num(dur) and LONGFORM_MIN_SEC <= dur <= LONGFORM_MAX_SEC,
          f"duration_sec={dur}")

    # this is NOT a Short: none of the Shorts loop/timing fields belong here
    leaked = [f for f in SHORTS_ONLY_FIELDS if f in m]
    r.add("no Shorts-only loop/timing fields present (wrong product)",
          not leaked, f"leaked_fields={leaked}")

    # face-cam is PERMITTED (and recommended) for long-form — never require face=false.
    # We only assert the flag, if present, is a bool (documentation of the choice).
    if "face" in m:
        r.add("face flag is a boolean (face-cam allowed for long-form)",
              isinstance(m.get("face"), bool), f"face={m.get('face')!r}")

    # chapters: >=3, first at 0, strictly increasing
    chapters = m.get("chapters", []) or []
    starts = [c.get("start_sec") for c in chapters if isinstance(c, dict)]
    # F6 fix (production-audit finding, 2026-07-25): a non-dict entry in `chapters`
    # (e.g. a bare string) previously crashed this line with an unhandled
    # AttributeError, since c.get("title") assumes every entry is a dict. `starts`
    # above is already dict-filtered; this check must be too.
    chapters_shaped = (len(chapters) >= 3 and all(_is_num(s) for s in starts)
                       and all(isinstance(c, dict) and isinstance(c.get("title"), str)
                               and c.get("title", "").strip()
                               for c in chapters))
    r.add("at least 3 chapters, each with title + numeric start_sec",
          chapters_shaped, f"chapters={len(chapters)}")
    if chapters_shaped:
        r.add("first chapter starts at 0:00", abs(starts[0]) < 1e-6, f"first_start={starts[0]}")
        r.add("chapter start times strictly increase",
              all(b > a for a, b in zip(starts, starts[1:])), f"starts={starts}")

    # keyword-rich first description line
    desc = m.get("description", "") or ""
    first_line = _norm(desc.splitlines()[0]) if desc.strip() else ""
    kws = [_norm(k) for k in (m.get("primary_keywords", []) or []) if isinstance(k, str)]
    r.add("1-2 primary_keywords declared", 1 <= len(kws) <= 2, f"primary_keywords={m.get('primary_keywords')}")
    # Word-boundary-aware match (not plain substring containment): a short keyword like
    # "one" must not match inside an unrelated word like "someone". Escaped per-keyword
    # regex with \b on both sides.
    def _kw_in_line(kw: str, line: str) -> bool:
        return bool(kw) and re.search(r"\b" + re.escape(kw) + r"\b", line) is not None

    r.add("first description line contains a primary keyword",
          bool(first_line) and any(_kw_in_line(k, first_line) for k in kws),
          f"first_line={first_line!r} keywords={kws}")

    # follow-on retention: playlist link + pinned next link
    r.add("playlist_link present",
          isinstance(m.get("playlist_link"), str) and bool(m.get("playlist_link", "").strip()),
          "playlist_link empty/missing")
    r.add("pinned_next_link present (next video or playlist)",
          isinstance(m.get("pinned_next_link"), str) and bool(m.get("pinned_next_link", "").strip()),
          "pinned_next_link empty/missing")

    # explicit comment prompt (a question)
    cp = (m.get("comment_prompt", "") or "").strip()
    r.add("explicit comment_prompt question present", cp.endswith("?") and len(cp) > 5,
          f"comment_prompt={cp!r}")

    # teaser Shorts only after the flagship URL exists
    n_teasers = m.get("teaser_shorts_planned", 0)
    r.add("teaser_shorts_planned is a non-negative integer",
          isinstance(n_teasers, int) and not isinstance(n_teasers, bool) and n_teasers >= 0,
          f"teaser_shorts_planned={n_teasers!r}")
    if isinstance(n_teasers, int) and not isinstance(n_teasers, bool) and n_teasers > 0:
        r.add(f"teaser count within {TEASER_MIN}-{TEASER_MAX}",
              TEASER_MIN <= n_teasers <= TEASER_MAX, f"teaser_shorts_planned={n_teasers}")
        fu = m.get("flagship_url", "")
        r.add("teasers planned only after flagship_url exists",
              isinstance(fu, str) and bool(fu.strip()), "flagship_url empty/missing but teasers planned")

    # model routing (Law #137): Fable 5 permitted for a flagship script
    model = _norm(m.get("model", ""))
    if model:
        r.add("model is Sonnet 5.0 or Fable 5 (Law #137 flagship allowlist)",
              model in ALLOWED_MODELS, f"model={m.get('model')!r}")

    return r


def format_report(r: Result) -> str:
    lines = ["LONG-FORM FLAGSHIP PREFLIGHT VALIDATION", "=" * 40]
    for name, ok, detail in r.checks:
        tag = "PASS" if ok else "FAIL"
        suffix = f"  ({detail})" if detail and not ok else ""
        lines.append(f"[{tag}] {name}{suffix}")
    lines.append("=" * 40)
    n_fail = len(r.failures())
    verdict = "PASS — flagship cleared" if r.ok else f"BLOCKED — {n_fail} check(s) failed"
    lines.append(f"RESULT: {verdict}")
    return "\n".join(lines)


SCHEMA = """LONG-FORM FLAGSHIP MANIFEST SCHEMA (Law #146 — distinct from Shorts)
{
  "content_type": "longform",
  "recipient": "hero_or_villain@outlook.com",
  "show": "string", "angle": "string",
  "duration_sec": 600,                 // 480-720 (8-12 min); absolute watch time is the goal
  "face": true,                        // face-cam PERMITTED/recommended for long-form
  "model": "Claude Fable 5",           // Fable 5 allowed for flagship script (Law #137)
  "primary_keywords": ["kw1", "kw2"],  // 1-2; must feature in the first description line
                                        // (F7 fix, 2026-07-25: corrected -- no title
                                        // field exists in this manifest or is read by
                                        // this validator; only the description's first
                                        // line is actually checked, see below)
  "description": "First line leads with kw1 ... (keyword-rich first lines).",
  "chapters": [                        // >=3; first at 0; strictly increasing
    {"title": "Intro", "start_sec": 0},
    {"title": "...", "start_sec": 120},
    {"title": "...", "start_sec": 360}
  ],
  "playlist_link": "https://www.youtube.com/playlist?list=...",
  "pinned_next_link": "https://youtu.be/... (next video or playlist)",
  "comment_prompt": "A specific question ending with '?'",
  "teaser_shorts_planned": 3,          // 0, or 1-3 (M5 cap) — and ONLY if flagship_url exists
  "flagship_url": "https://youtu.be/... (REQUIRED once teasers are planned)"
}
NOTE: Shorts-only fields (capcut_target_sec, total_clip_time_sec, loop_line,
loop_transition, loop_read_aloud_pass) must NOT appear here — long-form is not bound
by the 30s loop/timing laws (#140/#141).
"""


def main(argv: list[str]) -> int:
    if "--schema" in argv:
        print(SCHEMA)
        return 0
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: validate_longform_flagship.py <manifest.json> | --schema", file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[FAIL] could not load manifest: {e}", file=sys.stderr)
        return 2
    r = validate_flagship(manifest)
    print(format_report(r))
    return 0 if r.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

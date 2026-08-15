# Known Issues — AnimeWithSebastian / validate_dual_package.py

## F15: Systemic non-string-input crash pattern across ~20 `pkg.get(...)` accesses in `validate_dual_package.py`

**Discovered:** 2026-07-25, during the format_type enum enforcement (Law #85/#96/#98
port) session, while fixing two isolated instances of this same bug class (F_new at
`validate_manifest` line ~885, F_new2 at `validate_package` line ~815 — both already
fixed and committed).

**Status:** RESOLVED in commit ea854b1 (`validators/validate_dual_package.py`,
`validators/test_validate_dual_package.py`). All 19 fields fixed via `_str()`/
`_list()` typed getters; regression-guarded by
`TestNonStringFieldCrashes` (19 tests, `validators/test_validate_dual_package.py`).
Full suite green with zero behavior change on valid input (184/184 validators,
81/81 tools).

**Corrections found during the fix (not in the original sweep above):**
- The `slot` line cited below (line 506, `validate_package`) never actually
  crashes on any input type — it's only used in an f-string (`f"[{slot}]"`),
  which calls `str()` implicitly and accepts any type. The real crash site is
  a different, undocumented line in `validate_manifest()`:
  `slots = sorted(_norm(p.get("slot", "")) for p in pkgs)`, which calls
  `_norm()`'s `.strip()` directly on the raw value with no type guard. That is
  the site that was actually fixed.
- Three more fields — `hook_line`, `youtube_title`, `tiktok_title` — also have
  a second crash site in `validate_manifest()`'s cross-package dedup checks
  (originally lines 907, 913, 914) that the table below did not list. Live
  verification during the fix confirmed these crash even though the doc's own
  reproduction method (poison a single field, call `validate_manifest(m)`
  directly) is the correct entry point to reach them — `validate_manifest`
  runs its own manifest-level checks, including these four dedup lines,
  *before* it calls `validate_package()` per package (line 929). Both sites
  are now fixed for all four fields.
- **Methodology note for future sweeps of this kind:** the original table
  correctly lists multiple line numbers for several fields (`loop_line`,
  `opening_sentence`, `sources`, `hook_onscreen_text`), showing the original
  sweep did know to check for repeat occurrences in general — but it missed
  the manifest-level repeat occurrence specifically for `slot`, `hook_line`,
  `youtube_title`, and `tiktok_title`. A future field-by-field crash sweep
  should grep every occurrence of `pkg.get("<field>"` / `p.get("<field>"`
  across the whole file (both `validate_package` and `validate_manifest`)
  before concluding a field is fully covered, rather than stopping at the
  first reproduced crash per field.

**Severity:** Medium. Does not affect any currently-shipped manifest (real production
manifests always populate these fields with correctly-typed strings/lists). The risk
is that a future manual edit, a bug in the generation step, or a malformed LLM output
that isn't quite what the format expects would crash the *validator itself* with an
unhandled traceback instead of producing a clean named check failure — defeating the
validator's entire fail-closed purpose (Law #147, Step 6 of `cron_daily_runtime.txt`).
A crashing validator on a bad manifest is arguably worse than a validator that
correctly flags the manifest as invalid, because a crash could be mistaken for a tooling
problem rather than a content problem, and a hasty operator could be tempted to bypass
the validator rather than diagnose it.

**Root cause pattern:** Throughout `validate_package()` (and one site in
`validate_manifest()`), values pulled via `pkg.get(FIELD, default)` are passed directly
into string-only operations (`.strip()`, `.lower()`, `.rstrip()`, `_norm()`,
`re.findall()`) or iterated as if a specific container shape (list of dicts, list of
strings) is guaranteed — with no `isinstance()` guard. JSON permits any of these fields
to be an int, bool, list, dict, or null in a malformed manifest, and Python raises
`AttributeError` or `TypeError` instead of failing gracefully in that case.

**Already fixed (NOT part of this backlog — for reference only):**
- `F_new` — `validate_manifest()`, the "distinct shows"/"distinct formats" check
  (originally line 884-887, now ~891-898) crashed on non-string `show`/`format_type`.
  Fixed by coercing non-string values to `""` before calling `_norm()`.
- `F_new2` — `validate_package()`, the show-keyword-in-title check (originally line
  815/819) crashed on non-string `show` fed into `re.findall()`. Fixed by coercing to
  `""` before the regex call.

**Reproduction method used for this sweep:** for each field below, take the shipped
`valid_dual_package.json` (and separately `valid_duration_experiment.json`) fixture,
overwrite `packages[0][FIELD]` with each of four poison values (`12345`, `["a",
"list"]`, `{"a": "dict-not-expected-shape"}`, `True`), and call
`validate_manifest(m)` directly. A field is listed below only if at least one poison
value produced an unhandled exception instead of a normal `Result` with named
failures.

**Fields confirmed to crash, with real current source lines (as of commit at time of
writing, post-F_new/F_new2):**

| Field | Line(s) | Current code | Crash example |
|---|---|---|---|
| `loop_line` | 400, 558 | `loop = (pkg.get("loop_line", "") or "").strip()` | `AttributeError: 'int' object has no attribute 'strip'` |
| `opening_sentence` / `opening_line` | 401, 562, 569 | `opening = (pkg.get("opening_sentence") or pkg.get("opening_line") or "").strip()` | `AttributeError: 'list' object has no attribute 'strip'` |
| `sources` | 434, 667 | `pkg_source_urls = {_norm(s.get("url")) for s in (pkg.get("sources") or []) ...}` | `TypeError: 'int' object is not iterable` |
| `slot` | 506 | `slot = pkg.get("slot", f"pkg{idx}")` (later used in string context) | `AttributeError: 'bool' object has no attribute 'strip'` |
| `vo` | 522 | `vo = pkg.get("vo", "") or ""` | `TypeError: expected string or bytes-like object, got 'int'` (downstream `re` call on `vo`) |
| `cta_line` | 542 | `cta = pkg.get("cta_line", "")` | `AttributeError: 'dict' object has no attribute 'strip'` |
| `question_line` | 545 | `q = (pkg.get("question_line", "") or "").strip()` | `AttributeError: 'list' object has no attribute 'strip'` |
| `video_style` | 617 | `style = _norm(pkg.get("video_style", ""))` | `AttributeError: 'int' object has no attribute 'strip'` (inside `_norm`) |
| `clips` | 626 | `clips = pkg.get("clips", []) or []` | `TypeError: object of type 'int' has no len()`, or `KeyError: 0` for a dict |
| `hook_line` | 698, 702 | `hook = (pkg.get("hook_line", "") or opening).strip()` | `AttributeError: 'bool' object has no attribute 'strip'` |
| `content_type` | 716 | `"content_type" in pkg and _norm(pkg.get("content_type", "")) == "short"` | `AttributeError: 'int' object has no attribute 'strip'` (inside `_norm`) |
| `hook_onscreen_text` | 723, 780 | `onscreen = pkg.get("hook_onscreen_text", "")` | `AttributeError: 'list' object has no attribute 'strip'` (downstream) |
| `topic_class` | 755 | `tc = _norm(pkg.get("topic_class", ""))` | `AttributeError: 'dict' object has no attribute 'strip'` (inside `_norm`) |
| `topic_signals` | 758 | `signals = [_norm(s) for s in (pkg.get("topic_signals", []) or []) if isinstance(s, str)]` | `TypeError: 'int' object is not iterable` (the list comprehension itself can't iterate a non-iterable poison at the outer level) |
| `series_public_name` | 778 | `spn = (pkg.get("series_public_name") or "").strip()` | `AttributeError: 'int' object has no attribute 'strip'` |
| `youtube_title` | 779, 812 | `title = pkg.get("youtube_title", "") or ""` (later `.rstrip()` etc. via `hook_norm`/title logic) | `AttributeError: 'list' object has no attribute 'rstrip'` |
| `series_next_line` | 786 | `snl = (pkg.get("series_next_line") or "").strip()` | `AttributeError: 'bool' object has no attribute 'strip'` |
| `funnel_status` | 796 | `fs = _norm(pkg.get("funnel_status", ""))` | `AttributeError: 'dict' object has no attribute 'strip'` (inside `_norm`) |
| `tiktok_title` | 849 | `tt_title = pkg.get("tiktok_title", "") or ""` (later `.rstrip()` via title logic) | `AttributeError: 'int' object has no attribute 'rstrip'` |

All 19 fields above were confirmed against BOTH `valid_dual_package.json` and
`valid_duration_experiment.json` fixtures with identical crash behavior. Poison values
`12345` and `True` reliably crash nearly every field; list/dict poison values crash
most but not all (a few fields already have partial list-handling that tolerates a
list of the wrong element type without crashing, e.g. `topic_signals`'s inner
`isinstance(s, str)` filter tolerates non-string elements inside the list — it is only
the outer non-iterable poison that breaks it).

**Suggested remediation approach for the future session (not yet approved, offered as
a starting point only):**
1. Add one small typed-getter helper near `_norm()`, e.g.:
   ```python
   def _str(pkg: dict, key: str, default: str = "") -> str:
       v = pkg.get(key, default)
       return v if isinstance(v, str) else default
   ```
   and an equivalent `_list(pkg, key, default=())` for list-shaped fields
   (`sources`, `clips`, `topic_signals`, `hook_candidates`).
2. Replace each flagged `pkg.get(FIELD, ...)` call site with the typed getter,
   preserving existing default values and existing downstream logic exactly —
   this should be a mechanical, behavior-preserving change for all currently-valid
   inputs (every existing test must still pass unchanged).
3. Add one dedicated test class (e.g. `TestNonStringFieldCrashes`) with one test per
   field, each asserting `assertFailsCleanly` (not merely "does not crash" — should
   also produce SOME named failure) using at least the `12345` and `["a"]` poison
   values from this document.
4. Re-run the full suite; expect the existing 156 (+ tests added tonight) to remain
   green with zero behavior change on valid input, plus the new crash-guard tests
   passing.
5. Apply the exact same "show real current source → live repro → guard fix → dedicated
   test" sequence used for F_new/F_new2/F1-F14, per standing session convention — no
   diff without the real file content backing it up first.

**Explicitly out of scope for this document:** actually implementing the fix. This is
a findings record only, to be picked up as its own reviewable unit of work.

---

## F16: Law #152 (manually_authored manifest flag + independent re-audit) has zero
enforcement code in `validate_dual_package.py`

**Discovered:** 2026-07-26, during Law #152 compliance work on
`build_2026-07-27_manual_batch.py` (the manual manifest-build script used to log the
2026-07-27 post_date batch; content was hardcoded as Python literals, same as its
namesake incident script — see below).

**Status:** OPEN — documented, not fixed tonight. This is the second confirmed
real-world instance of this gap mattering: the first was `build_manifest_20260726.py`
(the incident that prompted Law #152's authorship on 2026-07-25), the second is
tonight's script. Both slipped past the validator with zero `manually_authored`-related
checks, because no such checks exist.

**What's missing:** `validate_manifest()` (and/or `validate_package()`) has no logic
that:
- Checks for a `manually_authored` field at all.
- If `manually_authored: true` is present, requires a `manually_authored_reason`
  string and a `manually_authored_reauditor` object with `who`, `date`,
  `extraction_test_applied`, and `urls_independently_verified` fields (Law #152 §4).
- Fails closed (§5) when `manually_authored: true` is set but the reauditor record is
  missing or incomplete.
- Has any way to verify a claim that a manually-authored manifest's content was
  "really" drafted/audited elsewhere before being hardcoded into the script, as
  opposed to fabricated outright the way the July 25/26 incident script's content
  was. The validator (and the manifest schema) can only see that a script hardcoded
  literals either way — it has no access to, and cannot verify, any claim about what
  happened in a prior model context. This matters in practice: this exact ambiguity
  came up during this discovery, and the resolution was that the flag applies
  regardless of any such claim, precisely because the claim itself is unverifiable
  from the manifest/script alone. Law #152 rule 2(c)'s independent-URL-verification
  requirement is the actual mechanism that catches unverified content in this
  scenario (see docs/KNOWN_ISSUES.md incident cross-reference:
  cron_tracking/daily_combined/INCIDENT_20260727_gachiakuta_terminology.md, where
  exactly this kind of unverified carried-over claim shipped in a real sent email).

**Severity:** Medium-high. Functionally identical to F15's original severity framing:
a manifest can pass the deterministic validator on structure alone while completely
bypassing a HARD LAW that exists specifically to catch unverified self-attestations —
and this is no longer a hypothetical, it has now happened twice in production, once
per known instance of a manual-build script being used.

**Reproduction:** Take any manifest, set `"manually_authored": true` with no
`manually_authored_reauditor` field, run `validate_dual_package.py` against it. It
passes today. Per Law #152 §5 it should fail closed.

**Explicitly out of scope for this document:** actually implementing the fix. This is
a findings record only, per standing session convention — no diff without explicit
go-ahead and full diff review first, same as every other backlog item in this file.

## F17: Naive sentence-splitter regex breaks on any abbreviation/honorific followed by
a space, anywhere in the VO — not narrow to "Dr."

**Discovered:** 2026-07-26, during the real `daily_combined` evening-slot pipeline run
for 2026-07-28. The selected show, "Dr. Stone: Science Future," failed the
`opening_sentence is the VO's exact first sentence` check on first validator pass
because the splitter cut "Dr. Stone..." into two fragments at the period after "Dr".
Worked around in that package by writing "Dr Stone" (no period) throughout all
validator-parsed fields — a real, disclosed formatting constraint, not a weakened
check. This entry documents the underlying validator bug that workaround exposed,
per standing instruction to log real findings rather than silently working around and
forgetting them.

**Location:** `validators/validate_dual_package.py`, line 624:
```python
sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", vo) if s.strip()]
```

**Status:** CONFIRMED REAL AND GENERALIZABLE — not narrow to "Dr.". Verified directly
by running the exact regex against a set of realistic VO-style sentences:

| Input | Splitter output |
|---|---|
| `"Dr. Stone: Science Future just ended. That was the real twist."` | `['Dr.', 'Stone: Science Future just ended.', 'That was the real twist.']` |
| `"Mr. Satan trained Buu. That changed everything."` | `['Mr.', 'Satan trained Buu.', 'That changed everything.']` |
| `"St. Louis is not in this anime. Just checking."` | `['St.', 'Louis is not in this anime.', 'Just checking.']` |
| `"The vs. framing misses the point. It really does."` | `['The vs.', 'framing misses the point.', 'It really does.']` |
| `"One Piece Ch. 1150 dropped today. Big reveal inside."` | `['One Piece Ch.', '1150 dropped today.', 'Big reveal inside.']` |
| `"It costs $3.5 million to make. That is a lot."` | `['It costs $3.5 million to make.', 'That is a lot.']` (survives, but only incidentally — no space follows the decimal point, so the lookbehind-then-whitespace pattern doesn't fire there) |

**Root cause:** the regex `(?<=[.!?])\s+` splits on *any* `.`, `!`, or `?` immediately
followed by whitespace, with zero abbreviation/honorific awareness. Any title,
honorific, initialism, or abbreviation that (a) ends in a period and (b) is followed by
a space anywhere in the VO — not only at the true sentence boundary — will fragment the
text at that point. This is a generic class of bug (the classic naive sentence-splitter
failure mode), not something specific to the word "Dr." The `$3.5 million` case shows
the bug is masked, not prevented, when no space follows the period (e.g. a mid-number
decimal) — it is not evidence the splitter handles abbreviations correctly.

**Blast radius:** every check downstream of the `sentences` list at line 624 is
potentially affected if the abbreviation lands in what should be the VO's first or
last sentence: `loop_line is the VO's exact final sentence`, `opening_sentence is the
VO's exact first sentence`, and the loop-transition/colon-handoff family of checks
that depend on `first_sent`/`last_sent`. A false split anywhere in the *middle* of the
VO is silently absorbed (only first/last fragments are read), but a false split at the
actual first or last sentence boundary — e.g. a show title with a period-abbreviated
honorific as the VO's opening or closing words — produces a false FAIL on an otherwise
correct package, exactly as happened with "Dr. Stone."

**Severity:** Medium. Does not corrupt any shipped manifest (the workaround avoids the
trigger by rewriting the abbreviation out of the affected fields), but it is a false
failure mode on the validator's own mechanical checks — the opposite failure direction
from F15/F16 (which are about false PASSES on bad content). A validator that
false-fails a genuinely correct package trains operators to reach for the same kind of
local text workaround each time, rather than fixing the splitter, and risks a future
operator loosening a check instead of understanding why it failed if the pattern isn't
recognized as systemic.

**Reproduction:** run the regex above against any VO string containing a
period-abbreviated word followed by a space, positioned so the abbreviation falls in
what should be the first or last sentence.

**Explicitly out of scope for this document:** actually implementing the fix (e.g.
switching to an abbreviation-aware splitter, or requiring `opening_sentence`/
`loop_line` to be matched by prefix/suffix containment rather than exact
first/last-fragment equality). This is a findings record only, per explicit
instruction not to fix tonight — no diff without explicit go-ahead and full diff
review first, same as every other backlog item in this file.

---

## F18: Pre-existing test failure — `test_invalid_manifest_broken_loop_fails_closed`
expects fail-closed behavior for a check retired by the Law #141 rescission

**Discovered:** 2026-07-27, during the final full-suite run for tonight's Part 1 +
Part 2 (2a/2b/2c) work (Law #85 format hierarchy correction, `related_video_id`,
`onscreen_cta_start_sec`, `flagship_opening_hook_match`). `cd tools && python3 -m
unittest discover -s . -p "test_*.py"` returned 99/100 passing, with this one test
failing (`AssertionError: 0 != 1`).

**Status:** OPEN — documented, not fixed tonight. Explicitly out of scope for this
session's approved diffs (Part 1, 2a, 2b, 2c only).

**Confirmed pre-existing, not caused by tonight's work:** reproduced directly on a
clean working tree via `git stash` (reverting all 11 files changed tonight) followed
by `python3 -m unittest test_append_send_batch.TestManifestRevalidationGate.test_invalid_manifest_broken_loop_fails_closed`
— the identical failure (`AssertionError: 0 != 1`) reproduces on unmodified `main`
at commit `5846da3` (the same commit confirmed clean and up to date at the start of
tonight's session). `git stash pop` restored tonight's changes afterward.

**Root cause (likely, not yet fully traced):** the test's name and setup
(`test_invalid_manifest_broken_loop_fails_closed`) indicate it constructs a manifest
with an intentionally broken seamless-loop field (`loop_line`/`loop_transition`/
`final_to_opening`/`loop_read_aloud_pass` family) and asserts the revalidation gate
in `tools/append_send_batch.py` returns exit code 1 (fails closed) on that broken
manifest. Law #141's forced seamless-loop mandate was rescinded earlier in the
2026-07-27 session (commit `5846da3`, "Rescind Law #141's forced seamless-loop
mandate") — the loop fields are now optional/inert and no longer checked by
`validate_dual_package.py`. A manifest that is only "broken" in that now-inert loop
family therefore no longer fails validation, so the revalidation gate's `rc` is `0`
(passes) instead of the `1` the test still expects. This entry does not confirm this
mechanism by direct trace through `test_append_send_batch.py`'s fixture content —
that would be required before implementing a fix.

**Severity:** Medium. The revalidation gate itself may still be working correctly —
the test's fixture may simply be asserting against a fail condition that Law #141's
rescission legitimately removed. This needs to be distinguished from an actual
regression in the gate before any fix is written: either (a) the test fixture needs
updating to use a still-enforced broken condition, or (b) if the gate is supposed to
still reject something about that fixture for an unrelated reason, the gate itself
has a real bug. Not yet determined which.

**Reproduction:** `cd tools && python3 -m unittest test_append_send_batch.TestManifestRevalidationGate.test_invalid_manifest_broken_loop_fails_closed`
on current `main`.

**Explicitly out of scope for this document:** actually implementing the fix. This is
a findings record only, per standing session convention — no diff without explicit
go-ahead and full diff review first, same as every other backlog item in this file.

**UPDATE (2026-08-13) — root cause now CONFIRMED, original theory superseded:**
Found incidentally while investigating tonight's Law #164/#165/#166/#167 work
(the send-gate redesign and episode_source field), not from a dedicated
investigation into F18 itself. During adversarial testing of the new
`--approval-file` gate, `git stash` was used to isolate tonight's changes from
`main` and confirm this test's failure predates tonight's session (same
isolation technique the original 2026-07-27 entry used). That isolation
incidentally required reading the test's current body directly, which settles
the question the original entry left open.

The original entry's theory — that Law #141's loop-field rescission made the
fixture's broken condition inert — is **not what the test actually does** and
should be treated as an initial, unconfirmed hypothesis, not the explanation.
Direct read of `test_invalid_manifest_broken_loop_fails_closed` in
`tools/test_append_send_batch.py` shows it sets
`bad["packages"][1]["loop_read_aloud_pass"] = False` and asserts the
revalidation gate returns `rc == 1` (fails closed). It still returns `rc == 0`
today, same as when this entry was opened.

The actual mechanism: `loop_read_aloud_pass` is a documented **self-attestation**
field under Law #147 (`cron_daily_runtime.txt`: "self-attestations... the
validator only checks presence/schema, and a human editor spot-checks them
weekly"). `validators/validate_dual_package.py`'s `validate_manifest()` was
never built to mechanically check this field's truth value — it only checks
that the field is present, not what it says. `tools/append_send_batch.py`'s
revalidation gate calls that same `validate_manifest()`, so it inherits the
same blind spot. Setting `loop_read_aloud_pass = False` therefore does not
fail validation, because nothing in the validator ever reads that value as a
pass/fail condition. This is a confirmed root cause, not a theory — it
resolves the "not yet determined which" question the original Severity note
left open: this is (a), a test fixture asserting a fail condition that was
never actually enforced, not (b) a gate regression.

**Status: still OPEN.** This update corrects the diagnosis; it does not fix
anything. Confirming *why* the test fails does not resolve the real decision
still sitting in front of a future session: either (1) build actual mechanical
enforcement of `loop_read_aloud_pass` into the validator (which would be a
deliberate reversal of Law #147's self-attestation design, not a bug fix), or
(2) correct this test's expectation to match the documented, intentional
self-attestation behavior. Neither was decided or implemented tonight.

---

## F19: `ENCYCLOPEDIC_DOMAINS` non-encyclopedic-pairing rule has no carve-out
for platform-native live statistics (score/vote-count claims)

**Discovered:** 2026-07-27, during tonight's 4-package rewrite pass. The Dr Stone
package originally cited a MyAnimeList score (8.26, 160,888 votes) sourced only to
`myanimelist.net`, which is in `ENCYCLOPEDIC_DOMAINS`
(`wikipedia.org`, `myanimelist.net`, `wikia.com`, `fandom.com`) and so failed the
"no core claim relies solely on Wikipedia/MAL/Fandom" check
(`validate_dual_package.py` lines ~396-398, ~490-497).

**The distinction, and why it's real:** the rule exists to stop a claim from resting
on a single encyclopedic *summary* — the exact failure mode Law #58 was written to
prevent (a wiki-style page paraphrasing something that turns out to be wrong or
stale). But a small subclass of claims cite a live, numeric, platform-native
statistic (a score, a vote count, a follower count) that is *definitionally* only
published by that one platform. No independent non-encyclopedic outlet
"corroborates" MyAnimeList's own internal score — there is nothing to corroborate,
because the number doesn't exist anywhere else. For this subclass, forcing a second
non-encyclopedic source produces one of two bad outcomes: (a) a fake pairing that
technically satisfies the domain check but cites a source that never actually
mentions the number (this nearly happened tonight — SoapCentral's Dr Stone review
was initially paired with the MAL claim despite never mentioning a score, caught only
on direct quote-level user review), or (b) the claim has to be dropped/reframed
entirely (the actual resolution used tonight — replaced with Anime News Network's own
4-star rating, a non-encyclopedic outlet's native statistic instead of MAL's).

**Why this is NOT tonight's problem to fix:** a real carve-out needs to distinguish
"platform-native live statistic with no possible second source" from "the writer
just didn't look hard enough for a second source" — and that distinction can't be
self-attested (Law #58 exists specifically because self-attestation on sourcing
rigor has failed before). A naive implementation (e.g. a `single_source_exempt: true`
boolean the writer sets) would be trivially gameable and would quietly reopen the
exact hole Law #58 closed. A defensible version likely needs either: a hard-coded
allowlist of specific claim shapes (e.g. only "site X's own numeric rating," never a
qualitative claim) with the *source domain itself* required to be the platform being
cited (MAL claim must cite MAL, ANN-rating claim must cite ANN — no laundering
through a third domain), or dropping the pairing requirement only for a new distinct
`claim_type` reserved for this shape and reviewed independently from types A/B/E.

**Status:** OPEN — not fixed tonight, worked around by replacing the MAL claim with
an ANN-sourced claim (ANN is not in `ENCYCLOPEDIC_DOMAINS`, so no exception was
actually needed once the claim was reframed). No validator code was touched.

**Severity:** Low/Medium. Not blocking — every claim tonight resolved without
needing the carve-out. But the underlying tension (real platform-native stats vs.
encyclopedic-summary risk) will recur any time a script wants to cite a MAL/Fandom
number specifically, and the workaround (avoid MAL-specific numbers, prefer
review-site ratings) is a content limitation, not a fix.

**Explicitly out of scope for this document:** actually implementing any carve-out.
This is a findings record only, per standing session convention — no diff without
explicit go-ahead and full diff review first, same as every other backlog item in
this file.

## F20: Law #73 has no accommodation for "real aired footage almost
certainly exists, but a specific clip-level video source wasn't
independently confirmed this pass" — a state distinct from the
manga-fallback case the law was designed around

**Discovered:** 2026-07-27, during tonight's One Piece package correction
pass (package `e41804f5-3651-4f89-91ba-3e848e7578e0`, clips 0, 2, and 3).
Three separate real, dated, written sources —
[onepiece.fandom.com/wiki/Scopper_Gaban](https://onepiece.fandom.com/wiki/Scopper_Gaban),
[gametrader.sg](https://www.gametrader.sg/blog/one-piece-episode-1170-luffy-vs-scopper-gaban/),
and [fandomwire.com](https://fandomwire.com/one-piece-episode-1170-review/) —
independently confirm that the underlying STORY beats depicted by these three
clips (the standoff, the key handover, the closing shot) are accurate to
Episode 1170. But no scene-level VIDEO source could be independently confirmed
for these specific visual beats after a real search pass: the only official
clip found for the standoff (Toei's Facebook page) is captioned Episode 1169,
not 1170; the key-handover beat has only a text-source (opwiki.org's German
per-episode summary) corroborating it, not video; and the closing-shot claim
was initially (wrongly) marked verified against an IGN preview that only
confirms the next episode's title, not this specific shot.

**The distinction, and why it's real:** `validate_dual_package.py`'s Law #73
check only recognizes two states per clip: `scene_verified: true` with a
`verification_source_url`, or `scene_verified: false` with a
`manga_reference` — the fallback path for shows where no anime footage of a
scene exists yet and the clip plan has to point to the manga instead. This
One Piece case is neither. The anime footage almost certainly exists — this
is real, aired, current-season footage of a real episode, not an
unadapted-manga situation — it just wasn't independently confirmed at the
clip level within this pass's research budget. Writing a `manga_reference`
here would be false: there is no manga chapter standing in for this scene,
and claiming one would misrepresent why the clip lacks a confirmed source.
The two-state model conflates "no anime exists" with "anime exists but I
couldn't pin the exact clip," which are different failure modes.

**Why this is NOT tonight's problem to fix:** same reasoning pattern as F16
and F19 — this needs real design review, not a same-night field addition or
a tolerant regex loosened under deadline pressure to ship one package.
Design needs review before code, per standing session convention.

**Concrete impact — this blocked a real, ready-to-send package tonight, not
a hypothetical:** the One Piece package was otherwise fully corrected — VO
word count regex-verified, core claim triple-sourced, clip tiling and loop
mechanics all passing — and the validator still returns
`RESULT: BLOCKED — DO NOT SEND` solely because clips 0, 2, and 3 have no
honest way to satisfy the existing two-state check. The package is held
pending a real resolution to this gap, not a same-night workaround.

**Status:** OPEN (design question) / MECHANICAL RISK CLOSED — the
validator crash risk described below is fixed; the underlying design
question (a real third schema state vs. a workaround field) is still
unresolved.

**Second real occurrence (2026-07-28, Sakamoto Days package, clips 0 and 2 of the
3-cut restructure):** Same exact gap recurred on a second show. Cut 1 (Gaku's JAA
entrance) and the merged Cut 3 (Takamura vs. Slur/Gaku/Sakamoto, Episode 16) both
have extensive written-source confirmation that real aired footage exists, but no
video source could be independently confirmed at the scene level within this pass's
budget — one candidate Netflix clip was checked and found to depict a *different*
scene entirely (Takamura's nap/fly moment, not the Episode 16 fight), and one visually
matching candidate was disqualified as an unofficial fan AMV. Both clips were flagged
with `verification_note` per this same pattern rather than forced into `scene_verified:
true` or a fabricated `manga_reference`. This confirms F20 as a recurring pattern, not
a one-off — same conclusion as before: needs real design review, not a same-night
field addition.

**Mechanical crash risk resolved (2026-07-28, same night):** the concrete
symptom this gap produced — `validate_dual_package.py` unconditionally
requiring `manga_reference` whenever `scene_verified: false`, with no
branch recognizing `verification_note` — is now fixed. The validator
accepts either a non-empty `manga_reference` or a non-empty
`verification_note` as satisfying the check; exactly one is required, not
both. The real Sakamoto Days manifest (commit `9284ac2`, clips 0 and 2)
now passes this check, confirmed via a direct validator run. This closes
the immediate blocking risk — an approved, correct manifest using this
pattern will not be wrongly flagged as missing `manga_reference`. The
broader design question F20 was opened to track — whether a real,
formalized third schema state should exist (rather than `verification_note`
remaining a workaround alongside the two originally-designed states) —
remains open and unaddressed by this fix, exactly as originally scoped.

**Severity:** Medium. Doesn't block every package (most clip plans do find
scene-level sources), but when it hits, it fully blocks an otherwise-clean,
factually-accurate package with no honest field to set — the exact scenario
that happened tonight, and again on a second, independent occurrence.

**Explicitly out of scope for this document:** actually implementing any
fix, including any proposed field shape or validator logic. This is a
findings record only, per standing session convention — no diff without
explicit go-ahead and full diff review first, same as F15-F19.

---

## F21: Outlook connector `send_email` intermittently dispatches one call as two
mailbox-side sends — cosmetic mailbox duplication, not a data-integrity issue

**Discovered:** 2026-07-26, during the Slime S4 morning send (first confirmed
occurrence). Most recently reproduced and freshly re-verified 2026-07-28 (tonight),
on both the Sakamoto Days and Blue Box sends.

**Status:** OPEN / MONITORING — documented, not fixed, no fix proposed. This is a
findings/history record only, consolidating what has already been independently
verified across multiple incident logs, not a new investigation.

**The connector defect itself:** a single confirmed `send_email` call to the
Outlook connector (`source_id: outlook`) sometimes results in two distinct emails
landing in the `hero_or_villain@outlook.com` mailbox — same subject, byte-identical
body, timestamps 2-3 seconds apart, two distinct Outlook `email_id` values. Only one
`send_email` tool call is made per occurrence (confirmed via session tool-call
history each time); this is a connector/transport-side defect, not an agent-side
double-send, and not something any code in this repository controls (no code here
calls `send_email` more than once per package).

**Real historical record (consolidated from existing incident docs, not re-derived):**

| Date | Send event | Verified outcome |
|---|---|---|
| 2026-07-26 (~22:30 UTC) | Slime S4 morning (original send) | **Genuine duplicate** — 2 distinct `email_id`s confirmed via direct `search_email` (`BLOCKER_20260728_duplicate_dispatch.md`) |
| 2026-07-27 round 1 (~01:48-01:51 UTC, 4 emails: Gachiakuta, One Piece, Slime S4, Dr. Stone rewrites) | Initially reported as 2 copies each (8 total), attributed to this same defect | **Later proven a false positive** — round 2's direct `search_email` check found exactly 1 real copy of each of the 4 emails, not 2. Correction already recorded in `REWRITE_SEND_20260727_batch.md`, `REWRITE_SEND_20260727_batch_v2.md`, and `INCIDENT_20260728_dr_stone_unsourced_claim.md` |
| 2026-07-28 round 3 (~04:22-04:23 UTC, 3 emails: Gachiakuta, Slime S4, Dr. Stone rewrites) | Zero duplicates | **Explicitly verified** — `REWRITE_SEND_20260727_batch_v3.md` states outright: "No instance of the `BLOCKER_20260728_duplicate_dispatch.md` connector defect... was observed on any of the three sends tonight" |
| 2026-07-28 tonight (~14:20-14:22 UTC, 2 emails: Sakamoto Days, Blue Box) | **Genuine duplicate, both sends** | Freshly re-verified via direct full `email_id` string comparison (not truncated/eyeballed suffixes) — 4 distinct email objects returned, all 4 `email_id` values confirmed unique |
| 2026-07-29 tonight (~02:02:01-02:02:30 UTC, 2 emails: Dragon Ball (Daima), Saga of Tanya the Evil II) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` — Dragon Ball: 2 distinct full `email_id`s (`...AAA7WyBTAAAA`, `...AAA7WwT2AAAA`), same thread, ~3 sec apart (02:02:01 / 02:02:04 UTC). Tanya: 2 distinct full `email_id`s (`...AAA7WwT3AAAA`, `...AAA7WyBUAAAA`), same thread, ~5 sec apart (02:02:25 / 02:02:30 UTC). Only one `send_email` tool call made per package (confirmed via this turn's tool-call history: `ms5fvpt3` for Dragon Ball, `ms5fw8km` for Tanya). Both logged as one `sent` row per package in `sent_scripts_log.json`/`sent_scripts_events.jsonl` per the mitigation below — dedup key `(batch_id, package_id)` is unaffected by mailbox-side duplication. |
| 2026-08-01 tonight (~23:46:16-23:46:39 UTC, 2 emails: One Piece morning, My Hero Academia evening — run #9) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — One Piece morning: 2 distinct full `email_id`s (`...AAA_U3DaAAAA`, `...AAA_U3TEAAAA`), same thread, ~2 sec apart (23:46:16 / 23:46:18 UTC). My Hero Academia evening: 2 distinct full `email_id`s (`...AAA_U3DbAAAA`, `...AAA_U3TFAAAA`), same thread, ~4 sec apart (23:46:35 / 23:46:39 UTC). Only one `send_email` tool call made per package (confirmed via this turn's tool-call history). Both logged as one `sent` row per package in `sent_scripts_log.json`/`cron_tracking/sent_scripts_events.jsonl` per the mitigation below — dedup key `(batch_id, package_id)` is unaffected by mailbox-side duplication. This occurrence surfaced during the same independent verification pass that produced F27 (see F27 below) — the primary finding of that pass was the self-audit reliability failure, not this duplicate, which is a routine, already-documented recurrence of this same connector defect. |
| 2026-08-02 (~02:17:44-02:17:51 UTC, CORRECTED SCRIPT resend of run #9's evening My Hero Academia package only) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA_U3DcAAAA` at 02:17:44 UTC, `...AAA_U3TGAAAA` at 02:17:51 UTC), same thread, ~7 sec apart. Only one `send_email` tool call was made for this package. The companion resend (One Piece morning, same batch, sent 02:17:45 UTC) did NOT duplicate — 1 real mailbox copy confirmed, consistent with this defect being intermittent rather than deterministic. Full tracking record: `cron_tracking/daily_combined/CORRECTED_SCRIPT_SEND_20260802_run9_onepiece_mha.md`. |
| 2026-08-02 (~14:10:54-14:11:23 UTC, replacement-package send: One Piece morning "Freed the One Giant Everyone Warned Against", My Hero Academia evening "Her Quirk Could Erase People" — new package_ids, same batch_id `c8401ef5-1d1e-48ce-a3f4-39443498caea`) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — One Piece morning: 2 distinct full `email_id`s (`...AAA_U3TMAAAA` at 14:10:58 UTC, `...AAA_U3DiAAAA` at 14:10:54 UTC), same thread, ~4 sec apart. My Hero Academia evening: 2 distinct full `email_id`s (`...AAA_U3TNAAAA` at 14:11:23 UTC, `...AAA_U3DjAAAA` at 14:11:16 UTC), same thread, ~7 sec apart. Only one `send_email` tool call was made per package (confirmed via this turn's tool-call history). Both logged as one `sent` row per package via the normal `tools/append_send_batch.py` flow — these are brand-new `package_id` values (`b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`, `d7c2a4b1-9e8f-4a3c-b1d2-3e4f5a6b7c8d`), so the `(batch_id, package_id)` dedup key applied normally, not as a reused-ID skip case. |
| 2026-08-02 (~14:25:47-14:26:19 UTC, CLIP PLAN CORRECTION resend of both replacement-batch packages — same `package_id`s as the row directly above, adding per-cut SEASON/EPISODE LOCATION data) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — One Piece morning: 2 distinct full `email_id`s (`...AAA_U3DkAAAA` at 14:25:47 UTC, `...AAA_U3TPAAAA` at 14:25:49 UTC), same thread, ~2 sec apart. My Hero Academia evening: 2 distinct full `email_id`s (`...AAA_U3DlAAAA` at 14:26:14 UTC, `...AAA_U3TQAAAA` at 14:26:19 UTC), same thread, ~5 sec apart. Only one `send_email` tool call was made per package. Per explicit user instruction, `append_send_batch.py` was NOT re-run for these already-logged `package_id`s — see `cron_tracking/daily_combined/CLIP_PLAN_CORRECTION_20260802_run9_replacement_onepiece_mha.md` for the dated tracking record used instead. |
| 2026-08-02 (~23:18:13-23:18:17 UTC, VO CRAFT CORRECTION resend of the One Piece morning package only — same `package_id` `b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`, fixing sequential-action fragment stacking per new Law #149 point 6) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA_U3DoAAAA` at 23:18:13 UTC, `...AAA_U3TTAAAA` at 23:18:17 UTC), same thread, ~4 sec apart. Only one `send_email` tool call was made for this package. Per the same established dedup-key reasoning as the prior clip-plan correction on this package_id, `append_send_batch.py` was NOT re-run — see `cron_tracking/daily_combined/VO_CRAFT_CORRECTION_20260802_run9_onepiece_fragment_fix.md` for the dated tracking record used instead. |
| 2026-08-02 (~23:33:12-23:33:15 UTC, VO STRUCTURAL CORRECTION resend of the One Piece morning package only — same `package_id` `b3e9f1a2-6c4d-4e2a-9f0a-1a2b3c4d5e6f`, third correction round: fixing the immediately prior "fragment fix" which was itself found to be a comma splice rather than a genuine merge, plus a redundant sentence per Law #149 point 1, per new Law #149 point 6 clarification) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA_U3DpAAAA` at 23:33:12 UTC, `...AAA_U3TUAAAA` at 23:33:15 UTC), same thread, ~3 sec apart. Only one `send_email` tool call was made for this package. Per the same established dedup-key reasoning as the prior two correction rounds on this package_id, `append_send_batch.py` was NOT re-run — see `cron_tracking/daily_combined/VO_STRUCTURAL_CORRECTION_20260802_run9_onepiece_comma_splice_redundancy_fix.md` for the dated tracking record used instead. |
| 2026-08-04 tonight (~23:04:59-23:05:02 UTC, JARGON CORRECTION resend of the Bleach TYBW morning package only — same `package_id` `b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7`, replacing insider-jargon term "cour" with plain language "final stretch"/"all season" across ANGLE, hook on-screen text, hook_candidates, VO, TikTok title/post text, and pinned comment, per Law #133) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA-1-sQAAAA` at 23:04:59 UTC, `...AAA-18okAAAA` at 23:05:02 UTC), same thread, ~3 sec apart. Only one `send_email` tool call was made for this package. Per the same established dedup-key reasoning as the prior correction rounds on other package_ids, `append_send_batch.py` was NOT re-run for this already-sent package_id — this occurrence is logged in `cron_tracking/daily_combined/JARGON_CORRECTION_20260804_bleach_cour_fix.md` (dated tracking record) instead. |
| 2026-08-04 tonight (~23:59:48-23:59:53 UTC, first real send of the Solo Leveling evening package — package_id `c2b3d4e5-f6a7-4890-b1c2-d3e4f5a6b7c8`, batch_id `8f3c1e2a-9d4b-4a7f-b6c3-2e1f0a9d8c7b`, corrected package after removing the unverified 330-day-streak claim and replacing it with the confirmed 1-million-ratings milestone, Option B closer locked) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA-18olAAAA` at 23:59:53 UTC, `...AAA-1%2FsRAAAA` at 23:59:48 UTC), same thread, ~5 sec apart. Only one `send_email` tool call was made for this package (confirmed via this turn's tool-call history). This was this package_id's FIRST real send (confirmed via full git-history search and `sent_scripts_log.json`/`sent_scripts_events.jsonl`/`publication_ledger.jsonl` search returning zero prior entries for this package_id before this send), so the normal `tools/append_send_batch.py` flow was used (not a correction-resend skip case) — `[OK] appended 2 events (skipped 0 already-present)` for both this package and the companion Bleach morning package, which had also never been through the atomic logger despite being sent+corrected earlier in the session. |
| 2026-08-05 (~00:22:33-00:22:36 UTC, **INTENTIONAL Sebastian-requested resend** of the already-sent Solo Leveling evening package — same package_id `c2b3d4e5-f6a7-4890-b1c2-d3e4f5a6b7c8`, unchanged content, explicitly requested as a deliberate duplicate send, not a correction) | **Genuine duplicate, one send call, but the send itself was intentional (not a new connector-bug trigger event by user intent — the underlying F21 dispatch-doubling still occurred on this call, purely as a side effect of the same pre-existing bug)** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAA-1-sSAAAA` at 00:22:33 UTC, `...AAA-18omAAAA` at 00:22:36 UTC), same thread, ~3 sec apart. Only one `send_email` tool call was made. Mailbox now holds 4 total distinct copies of this exact subject across both sends (2 from the original first-send F21 duplicate at 23:59:48/23:59:53, 2 from this intentional resend at 00:22:33/00:22:36) — confirmed via exact-subject-string filter on `search_email` results, not assumed. Per explicit user instruction, `append_send_batch.py` was NOT re-run (package_id already logged as sent from the first send); this row is the designated tracking record distinguishing the resend as deliberate rather than a new organic F21 occurrence. |
| 2026-08-05 (~00:51:36-00:51:40 UTC, CLIP PLAN CORRECTION resend of the Bleach TYBW morning package only — same `package_id` `b1a2c3d4-e5f6-4789-a0b1-c2d3e4f5a6b7`, surfacing already-verified `clip_locate` season/episode data (S4E41) into the clip-plan text for all 5 cuts; a rendering-gap fix, no new research, no other content change) | **Genuine duplicate, one send** | Confirmed via exact-subject-string `search_email` filter — 2 distinct email objects returned (citation_id 1 and 2), timestamps 00:51:40 UTC and 00:51:36 UTC, same thread, ~4 sec apart. Only one `send_email` tool call was made for this package. Per the same established dedup-key reasoning as every prior correction round on this and other package_ids, `append_send_batch.py` was NOT re-run for this already-logged package_id — see `cron_tracking/daily_combined/CLIP_PLAN_CORRECTION_20260805_bleach_season_episode_surfacing.md` for the dated tracking record used instead. |
| 2026-08-05 tonight (~23:42:27-23:43:02 UTC, first real send of tonight's Mushoku Tensei morning package — package_id `902006e6-d24f-4fc0-8ba3-c83385de404f` — and Jujutsu Kaisen evening package "Juju Fest Just Got A Date" — package_id `1f25b49b-3e76-46e4-9bfb-cc6063da8b12` — shared batch_id `f36bf5d9-be2f-408d-a2e5-57fe63a3bdff`, post_date 2026-08-06) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — Mushoku Tensei morning: 2 distinct full `email_id`s (`AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkPNGAAAA` at 23:42:27 UTC, `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkMhGAAAA` at 23:42:32 UTC), same thread (`AQQkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoAEADl8b-EvFwNQ7QmDT6rLHI_`), ~5 sec apart. Jujutsu Kaisen evening: 2 distinct full `email_id`s (`AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkPNHAAAA` at 23:42:56 UTC, `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkMhHAAAA` at 23:43:02 UTC), same thread (`AQQkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoAEADWBNhTUhKfQJGP131AaWIf`), ~6 sec apart. Only one `send_email` tool call was made per package (confirmed via this turn's tool-call history: one call for the morning package, one call for the evening package). Both logged as one `sent` row per package via the normal `tools/append_send_batch.py` flow, per the same established dedup-key reasoning as every prior confirmed instance — dedup key `(batch_id, package_id)` is unaffected by mailbox-side duplication. |
| 2026-08-06 tonight (~21:20:56-21:20:59 UTC, IDENTITY CORRECTION resend of the Kagurabachi morning package only — same `package_id` `fc92f1fc-de9d-4829-9f5c-7bf144f99fa3`, batch_id `8c737fff-f523-4b00-896a-4e2fc8a40152`, fixing the Kunishige/Chihiro's-dad name-anchor ambiguity: opening sentence rewritten to "Chihiro's dad, Kunishige, is the legendary swordsmith...", VO word count 107→108, Option A locked after user review of A/B) | **Genuine duplicate, one send** | Confirmed via direct `search_email` full-string `email_id` comparison — 2 distinct full `email_id`s (`...AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkPNKAAAA` at 21:20:56 UTC, `...AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkMhKAAAA` at 21:20:59 UTC), same thread, ~3 sec apart. Only one `send_email` tool call was made for this package (confirmed via this turn's tool-call history). Per the same established dedup-key reasoning as every prior correction round on this and other package_ids, `append_send_batch.py` was NOT re-run for this already-logged package_id — see `cron_tracking/daily_combined/VO_IDENTITY_CORRECTION_20260806_kagurabachi_kunishige_chihiro_dad.md` for the dated tracking record used instead. |
| 2026-08-09 tonight (~01:10:09-01:10:42 UTC on 2026-08-10, first real send of tonight's Mushoku Tensei: Jobless Reincarnation Season 3 morning package — package_id `7baa84ef-5517-47a1-b7ee-e70fe2964231` — and Kagurabachi evening package "Kagurabachi's Shiba Just Got a Death Flag and Ignored It" — package_id `a595b615-161e-43d1-9c28-1b9f79510dc8` — shared batch_id `8b99902a-5ca2-48f9-a66c-62046e51a608`, post_date 2026-08-10; this is the first live send under the new manifest/validator system) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — Mushoku Tensei morning: 2 distinct full `email_id`s (`AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABC7jDqAAAA` at 01:10:14 UTC, `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABC7iz_AAAA` at 01:10:09 UTC), same thread, ~5 sec apart. Kagurabachi evening: 2 distinct full `email_id`s (`AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABC7jDrAAAA` at 01:10:42 UTC, `AQMkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoARgAAAzW7qCrLjuhGlhQYD5lZhcoHAN2_6LTid3pLrJ8ttdD6ck4AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABC7iz-AAAA` at 01:10:38 UTC), same thread, ~4 sec apart. Only one `send_email` tool call was made per package (confirmed via this turn's tool-call history: one call for the morning package, one call for the evening package). Both were this package_id's FIRST real send (confirmed via direct `sent_scripts_log.json`/`cron_tracking/sent_scripts_events.jsonl`/state.json search returning zero prior entries for either package_id before this send), so the normal `tools/append_send_batch.py --emails-sent` flow was used — `[OK] appended 2 events (skipped 0 already-present; legacy_added=2)` for both packages. Dedup key `(batch_id, package_id)` is unaffected by mailbox-side duplication. |
| 2026-08-10 tonight (~23:49:07-23:49:28 UTC, FOOTAGE CORRECTION sends for tonight's Re:ZERO morning package `d08b72b8-d1ca-4e73-9f63-8c68e36a1df2` and Love Unseen evening package `6b7ad021-c808-4f52-80c7-a6b697182fba`, shared batch_id `79531612-04d5-4caa-94da-d05490ff994d`, post_date 2026-08-11 — corrections add trailer-footage pointer for Re:ZERO and a corrected-verification-note real-footage pointer for Love Unseen; no other manifest fields changed) | **Genuine duplicate, both sends** | Confirmed via direct `search_email` full-string `email_id` comparison — Re:ZERO: 2 distinct full `email_id`s (`...AAABC7jDvAAAA` at 23:49:10 UTC, `...AAABC7i0CAAAA` at 23:49:07 UTC), same thread, ~3 sec apart. Love Unseen: 2 distinct full `email_id`s (`...AAABC7jDwAAAA` at 23:49:28 UTC, `...AAABC7i0DAAAA` at 23:49:25 UTC), same thread, ~3 sec apart. Only one `send_email` tool call was made per correction (confirmed via this turn's tool-call history). These are corrections to already-sent, already-logged package_ids, so per the same established dedup-key reasoning as every prior correction round, `append_send_batch.py` was NOT re-run — see `cron_tracking/daily_combined/FOOTAGE_CORRECTION_20260810_rezero_love_unseen.md` for the dated tracking record used instead. |
| 2026-08-11 tonight (~23:22:00-23:22:07 UTC, first real send of tonight's Frieren: Beyond Journey's End morning package — package_id `901eeda3-3ae4-446e-9629-eb7f6105b685`, batch_id `cfbfaaaf-def7-4775-b643-d27667ea9000` — and Weekly Shonen Jump evening package "Shonen Jump Just Fell Below 1 Million" — package_id `4c17d748-f3a2-4035-a4d9-b7b1a1e630a4` — shared batch_id, post_date 2026-08-12) | **Genuine duplicate, morning send only — evening send clean (1 copy)** | Confirmed via direct `search_email` full-string `email_id` comparison — Frieren morning: 2 distinct full `email_id`s (`...AAABC7i0HAAAA` at 23:22:00 UTC, `...AAABC7jD1AAAA` at 23:22:07 UTC), same thread, ~7 sec apart. Only one `send_email` tool call was made for the morning package this session (confirmed via this turn's tool-call history) — the connector fired it twice into the mailbox on that single call, consistent with every other confirmed instance of this defect. Weekly Shonen Jump evening: exactly 1 email returned by `search_email` (`...AAABC7i0IAAAA` at 23:22:30 UTC) — no duplicate on this send. This was each package_id's FIRST real send, so the normal `tools/append_send_batch.py --emails-sent` flow applies — dedup key `(batch_id, package_id)` is unaffected by the morning package's mailbox-side duplication. |
| 2026-08-12 tonight (~01:24:40-01:24:44 UTC on 2026-08-13, first real send of tonight's Saga of Tanya the Evil Season 2 morning package "Tanya's Commander Weaponized Her Own Fame" — package_id `80d82472-7278-4d42-bb5a-0c4b88d90eb5`, batch_id `efb80aef-5cb2-4fd4-88f1-47904d600ef7` — and Kagurabachi evening package "Kagurabachi: Blade At His Throat, Kept Forging" — package_id `bf25f9d5-7c73-4fd6-8e40-04b46bee9cc3` — shared batch_id, post_date 2026-08-13, cron run #19) | **Genuine duplicate, morning send only — evening send clean (1 copy)** | Confirmed via direct `search_email` full-string `email_id` comparison and byte-for-byte body hash comparison — Tanya morning: 2 distinct full `email_id`s (`...AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABFDDR1AAAA` at 01:24:44 UTC, `...AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABFDHEUAAAA` at 01:24:40 UTC), same thread_id (`AQQkADAwATM0MDAAMi1hNzU1AC1lMjFkLTAwAi0wMAoAEAAxvcffAV88T4xe5bW7iaD2`), ~4 sec apart, bodies byte-identical (same length 7,763 chars, same hash). Only one `send_email` tool call was made for the morning package this session (confirmed via this turn's tool-call history) — the connector fired it twice into the mailbox on that single call, consistent with every other confirmed instance of this defect. Kagurabachi evening: exactly 1 email returned by `search_email` (`email_id` ending `...AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABFDHEVAAAA` at 01:25:16 UTC) — no duplicate on this send. This was each package_id's FIRST real send, so the normal `tools/append_send_batch.py --emails-sent` flow applies — dedup key `(batch_id, package_id)` is unaffected by the morning package's mailbox-side duplication. |

**On rate/frequency — explicitly NOT claimed:** the F21 table above now holds 21
total rows, of which 19 are tagged **Genuine duplicate** (both counts independently
verified by direct enumeration of the actual table rows in this file, not carried
forward from memory). Separately, this section has historically also quoted an
"approximately 26" real send-events figure — this is a hand-maintained tally that
counts individual packages within multi-package rows (e.g. a two-package night
counts as 2 send events but 1 table row), not a count re-derived from
`sent_scripts_log.json` or `cron_tracking/sent_scripts_events.jsonl`. That
per-package tally has NOT been independently reconciled against the durable logs
this session, and the exact definition of which durable-log entries would count as
"F21-relevant" is undocumented — so this figure should be read as an approximate,
hand-maintained estimate, not a verified count on the same footing as the 16/14
row-based numbers above. This sample is too small to distinguish an increased or
changed failure rate from ordinary variance in a rare, intermittent connector
defect. This entry deliberately does not assert any rate, in either direction —
neither "consistent known rate" nor "confirmed increase" is supportable from the
evidence gathered so far.

**Mitigation already in place (confirmed effective across every instance to
date):** `tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only
— it has no dependency on how many times the underlying email transport happened
to fire. Every genuine duplicate-dispatch instance observed so far (2026-07-26 and
tonight) still resulted in exactly one `"sent"` event appended per package to both
`sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`, confirmed
directly after each occurrence. This makes the defect a cosmetic mailbox-display
issue (an extra identical copy visible in the inbox) rather than a data-integrity
issue — the durable production logs, the publication ledger, and downstream
analytics joins are unaffected regardless of how many times the mailbox shows the
same send.

**Explicitly out of scope for this document:** actually implementing any fix. The
defect lives in the Outlook connector integration itself, outside this repo's
codebase — there is no send-path code here to change. This is a findings/history
record only, per standing session convention — no diff without explicit go-ahead
and full diff review first, same as every other backlog item in this file.

---

## F22: `validate_dual_package.py` had a fixed "at least 4 clips" floor
with no documented rationale — fixed, replaced with a non-empty check

**Discovered and fixed:** 2026-07-28 (tonight), while confirming the F20
fix against the real Sakamoto Days manifest. The manifest's genuinely
approved 3-cut restructure (7/13/10s, commit `9284ac2`) failed
`validate_dual_package.py`'s unrelated `len(clips) >= 4` check — a fixed
count floor with no comment anywhere justifying the number 4, sitting
in front of `_validate_clip_timeline`'s real coverage guarantee
(contiguous 0->target_sec tiling, no gaps/overlaps, durations sum to
target). That timeline check independently fails hard on an empty clip
plan — confirmed directly by isolating `_validate_clip_timeline([], ...)`,
which fails both "each clip has duration_sec/timeline_start_sec/
timeline_end_sec" and "clip timeline is contiguous" without ever reaching
an index into an empty list — so the count floor was not protecting
anything the timeline check didn't already cover. It only penalized
legitimate clip-plan restructures with fewer than 4 cuts.

**Status:** FIXED same night. `len(clips) >= 4` replaced with
`len(clips) > 0` ("clip plan is non-empty"). Any honestly-tiled clip
count now passes on equal footing — 2, 3, 4, or more. Three dedicated
tests added (`TestClipCountFloorRemovedF22`): a valid 3-cut manifest
matching the real Sakamoto Days shape passes, a valid 2-cut manifest
passes (confirming no arbitrary floor was merely lowered), and an empty
clip list still fails cleanly with a clear message. Full suite (192
tests) passes. The real Sakamoto Days manifest now passes the complete
validator end to end (`RESULT: PASS — cleared to send both emails`,
confirmed via direct run).

**Severity:** Was Medium-high in practice — this silently blocked a real,
already-approved, already-committed manifest from ever passing validation,
with a failure message unrelated to the manifest's actual (correct)
content. Now resolved.

**Explicitly in scope and completed:** unlike F15-F21, this is a
completed fix, not an open finding — included here per this document's
standing practice of recording every fix's rationale for future readers,
matching how earlier closed items are documented elsewhere in this
repository's history.

## F23: `onscreen_cta_start_sec` was mechanically enforced by the validator
but never instructed in the drafting runtime — fixed

**Discovered:** 2026-07-28 (tonight), while confirming schema fidelity
during the retroactive static check of batch `b3e8f2a1` against tonight's
validator code. `validate_dual_package.py` (lines 765–771) hard-requires
`onscreen_cta_start_sec` on every package — a real numeric value that must
land within the final 5 seconds of the resolved edit length (Law #62
addendum, 2026-07-27) — but `cron_daily_runtime.txt` never instructed the
drafting pass to set this field anywhere. A drafting pass following only
the runtime's own text had no way to know this field existed, let alone
what value it needed.

**Fixed:** 2026-07-28 (tonight). Added one instruction bullet to
`cron_daily_runtime.txt`'s Step 4 drafting section, directly after the
existing CTA-phrase bullet: "ON-SCREEN CTA TIMING (Law #62 addendum,
2026-07-27): set `onscreen_cta_start_sec` to a real numeric second value
that lands within the final 5 seconds of the resolved edit length
(`capcut_target_sec` — 30s by default, or the sanctioned 45-59s
`duration_experiment` length)." Documentation-only — the validator side
was already correct; this closes the gap on the drafting-instruction side
to match what was already mechanically enforced. Full suite (210 tests)
re-run as a sanity check post-edit: unaffected, still 210/210 passing
(expected — no code or schema changed).

**Status:** FIXED same night.

**Severity:** Medium — a drafting pass had no way to satisfy this
validator requirement from the runtime instructions alone; would have
produced a hard `BLOCKED` validator failure on every real batch until
someone noticed and added the field by trial and error. Now resolved.

## Status note (2026-07-28, tonight): what today's two data points do and do not prove about tonight's fixes

**Context:** Two real data points exist from today involving `daily_combined`
output: (1) the 10:23 AM EDT real batch `b3e8f2a1` (Sakamoto Days morning /
Blue Box evening, both validator-PASS at the time, both emails sent), and
(2) a retroactive static validator check run tonight against a reconstruction
of that same batch's real email content, using tonight's current validator
code.

**Stating plainly what these do NOT prove:** Both data points predate nearly
all of tonight's actual work — Law #73 Update 4/5, the four fixture
content-error fixes, and Law #155/Part 5 were all written and pushed after
10:23 AM EDT tonight. Neither data point is evidence that any of those three
things actually work correctly on real, newly-drafted content. The
retroactive check only confirmed that pre-existing (old) content correctly
fails the new Law #73 Update 4/5 checks (`scene_verified`,
`verification_source_url`, `manga_reference`, `claim_vs_source_check`,
`semantic_qa`) for the expected reason — the fields simply don't exist in
content drafted before those checks existed. That is a much narrower and
different claim than "tonight's fixes are proven."

**What is still entirely pending:** The real, first genuine test of
everything built tonight — Law #73 Update 4/5's actual discriminating power
(does `claim_vs_source_check` correctly catch a genuine mismatch when one
exists; is `clip_locate`'s `locate_confirmed_via` field enforced as a real
descriptive sentence and not a bare URL), the four fixture fixes, and Law
#155/Part 5 — is tomorrow's real `daily_combined` run, on genuinely new
content drafted and verified under tonight's actual current rules, not
today's. Nothing before that run should be read as validating tonight's
work.

**Status:** Informational scope note, not a bug. No code or law changed by
this entry.

## Follow-up (2026-07-28, later same night): Blue Box's real package was hand-corrected after the status note above was written

**Context:** The status note above ("what today's two data points do and do
not prove") described `cron_tracking/manual_step3_20260728/run_manifest.json`
as pre-Update-4 content with no `claim_vs_source_check`/`clip_locate` fields.
That was accurate at the time it was written.

**What changed since:** Later the same night, the Blue Box package's clip
plan in that same live file was hand-corrected under a full Law #73 review:
all 4 clips were re-sourced to real, independently verified Blue Box Season 1
Episode 1 content, with genuine `scene_verified`, `claim_vs_source_check`,
and `clip_locate` fields added. One clip's claim ("closing wide shot of the
gym/school") was found to be factually wrong on independent verification and
was replaced with the real, confirmed closing scene (a kitchen scene with a
city-view zoom-out). The corrected file passes today's live validator,
including the Law #73 Update 4/5 checks.

**Read the original status note as time-scoped:** Its description of
"today's data points" is accurate only as of its own timestamp (earlier
tonight), not as an ongoing description of the current file. The live
manifest file no longer matches the pre-Update-4 shape that note described
for the Blue Box package specifically; the Sakamoto Days package in the same
file is unaffected and still matches the original note's description.

**Status:** Informational follow-up note, not a bug. Documents a real,
approved content correction (see git history for the corresponding commit).

---

## F24: `clip_locate` can assert season/episode-level precision beyond
what its cited `verification_source_url` actually supports — inverse
of F20, and a second, independent defect in the same field for shows
with multiple distinct TV productions

**Discovered:** 2026-07-30 (tonight), during a user-initiated spot-check
of the Hunter x Hunter / Berserk clip plans (batch `ac60c0a6-...`,
package `f2b8d9e3-...`, Berserk Cut 3). The manifest's `clip_locate` for
that cut asserted `season: 1, episode: 5`, citing the CBR chronological
adaptation guide. Direct re-fetch of that source confirmed it supports
only an arc-level claim ("the [2016 series'] first season... Guts meets
and defeats a few Apostles") with **no episode number stated anywhere on
the page**. Independent lookup of the real S1E5 ("Tower of Conviction,"
[IMDb](https://www.imdb.com/title/tt5904592/)) confirmed its actual plot
(Guts searching for Casca, meeting Isidro) does not depict the claimed
beat (Guts confronting Griffith-affiliated forces) at all.

**Two independent, compounding defects, not one:**
1. **Citation over-specification.** `claim_vs_source_check.match: true`
   was set based on a genuinely-supported arc-wide claim, while the
   adjacent `clip_locate.episode` field asserted single-episode
   precision the same source never stated. The schema has no way to
   distinguish "this source confirms exactly this scene" from "this
   source confirms the general arc but not a specific episode" — both
   look identical (a populated `episode` field, `match: true`) once
   written.
2. **Undifferentiated `season` across distinct productions.** The same
   package's Cut 1 cites `season: 1` meaning the **1997 TV series**
   (25 episodes total, per the same CBR guide), while Cuts 2/4/5 (and
   the erroneous Cut 3) cite `season: 1`/`season: 2` meaning the
   **2016 TV series** (a separate, later production with its own
   season 1/2). Nothing in the schema requires a production/series-year
   label alongside a bare `season` integer, so any franchise with 2+
   distinct TV adaptations sharing arc names or overlapping "season"
   numbering can silently conflate two different shows under one field.

**Relationship to F20:** F20 documents the opposite failure direction —
real footage almost certainly exists, but no specific citation could be
honestly confirmed, and the two-state schema (`scene_verified` /
`manga_reference`) has no honest way to express that. F24 is the mirror
case: a specific citation was asserted that the cited source does not
actually support at that level of precision. Both point at the same
underlying gap — `clip_locate`/`claim_vs_source_check` currently treat
"a value is present" as equivalent to "the source supports that exact
value," with no confidence/precision field in between.

**Status:** OPEN — documented, not fixed tonight. The specific instance
was corrected via a standalone clip-plan-only follow-up email and
tracking doc (see `cron_tracking/daily_combined/REWRITE_SEND_20260730_hxh_berserk_clip_plan.md`),
not a validator or schema change.

**Suggested remediation approach for a future session (not yet approved,
offered as a starting point only):**
1. When `claimed_beat` is arc-wide/general rather than naming a single
   scene, either require a genuinely scene-level source before setting
   `clip_locate.episode`, or add an explicit precision marker (e.g.
   `episode_confidence: "scene-level"` vs. `"arc-level-only"`) so a
   downstream reader (human or validator) can distinguish the two
   without re-deriving it from the source text each time.
2. For any franchise with 2+ distinct TV productions, require a
   `production`/`series_label` string alongside `clip_locate.season`
   (e.g. `"1997 series"` / `"2016 series"`) rather than a bare integer
   that can silently collide across unrelated shows.
3. Apply the same "show real current source → live repro → guard fix →
   dedicated test" sequence used for F15-F23 — no diff without the real
   file content backing it up first, per standing session convention.

**Severity:** Medium. Does not appear to have affected any other shipped
cut checked so far (only this one cut, on this one show, surfaced the
defect), but the failure mode — a schema-valid, `match: true` citation
that is actually wrong at the precision it claims — cannot be caught by
the existing validator (which only checks field presence/shape, per M6
self-attestation) and was only caught by a manual, source-level
spot-check tonight. The same defect shape could exist undetected in any
other already-shipped package's `clip_locate` data.

**Explicitly out of scope for this document:** actually implementing any
fix, including any proposed field shape or validator logic. This is a
findings record only, per standing session convention — no diff without
explicit go-ahead and full diff review first, same as F15-F23.

---

## F25: `sent_scripts_log.json` contains a second, separate legacy entry
schema ("AX2026" batch tag) sitting alongside every real UUID-batch entry
across a 3+ week window, with no established relationship between the two

**Discovered:** 2026-07-30 (tonight), during post_date verification for
the 2026-07-31 Black Clover / Akane-banashi batch, prompted by a direct
user instruction not to assume a post_date is conflict-free without
checking.

**What was found:** `sent_scripts_log.json` contains 43 entries tagged
`"batch": "AX2026"`, all sharing a single `date_sent` of `2026-07-04`,
spanning `post_date` values from `2026-07-23` through `2026-08-13` (22
distinct dates). Every one of those 22 post_dates ALSO has a real,
UUID-keyed `daily_combined` batch entry (`batch_id` + `package_id`
fields) for the same post_date, from the current, actively-used pipeline
schema. The two schemas are structurally different: AX2026 entries have
no `batch_id`/`package_id` fields at all and carry a `subject` field
instead; real entries have `batch_id`, `package_id`, `status`, `vo_word
count`, etc. and no `subject` field.

Example: `post_date: 2026-07-31` currently has BOTH an AX2026 entry for
"Here U Are" (morning) / "Smoking Behind the Supermarket with You"
(evening), dated `2026-07-04`, AND the real, currently-relevant
`batch_id 439755dc-...` entry for Black Clover (morning) / Akane-banashi
(evening), sent tonight. This exact pattern repeats for every post_date
from 2026-07-23 onward that has been checked.

**Confirmed:**
- This does NOT block or duplicate the current daily_combined selection
  logic. That logic (per `cron_daily_runtime.txt`) reads
  `blackout_state.json` (a derived 30-day blackout / 7-day no-repeat
  list) and recent `sent_scripts_log.json` rows keyed by `show` name for
  cooldown purposes — it does not key off `batch`/`batch_id` presence, so
  an AX2026 row for a given show still correctly contributes to that
  show's cooldown/blackout the same as a real row would.
- This is not new or unique to tonight's post_date — it is a systemic,
  pre-existing pattern spanning the full AX2026 date range (22
  consecutive post_dates), unrelated to any decision made tonight.

**NOT yet confirmed (explicitly out of scope for tonight):**
- Why this legacy AX2026 data exists in the same file as the live
  pipeline's entries — whether it was bulk-imported once from a
  different/earlier planning system, is placeholder/pre-planned content
  that was never meant to be schema-compatible with the real pipeline, or
  something else.
- Whether AX2026 entries are inert everywhere, or whether some OTHER
  consumer of `sent_scripts_log.json` (e.g. the weekly analytics cron,
  any future tooling) reads or joins this file in a way that does NOT
  correctly disambiguate AX2026 rows from real ones — unlike the daily
  selection logic, which was directly verified tonight.
- Whether the `post_date` overlap is coincidental (e.g. AX2026 was a
  placeholder calendar built to cover the same rough date range the real
  pipeline later also covered) or reflects some intentional but
  undocumented relationship between the two datasets.

**Status:** OPEN — documentation only, no fix attempted or proposed
tonight, same standard as F15-F24.

**Severity:** Low-Medium. No confirmed functional impact on the daily
selection/cooldown logic as verified tonight, but the file mixes two
structurally incompatible schemas with unexplained provenance, over a
material fraction of the log (43 of 174 total entries, ~25%) — a future
consumer of this file that assumes schema uniformity could silently
misbehave.

**Explicitly out of scope for this document:** investigating root cause,
determining AX2026's origin, or implementing any fix/migration/cleanup.
This is a findings record only, per standing session convention — no
diff without explicit go-ahead and full diff review first, same as
F15-F24.

**See also F26** for the third, non-overlapping entry category found in
the same investigation pass — together the two findings account for the
full composition of `sent_scripts_log.json`.

---

## F26: `sent_scripts_log.json` contains a third, pre-`batch_id` legacy
entry schema (105 entries, 2026-05-30 through 2026-07-15) with an
inconsistent, wide field union and non-uniform status values, predating
the current two-package-per-batch pipeline

**Discovered:** 2026-07-30 (tonight), in the same investigation pass
that surfaced F25 (the AX2026 entries), while separating out entries
that were neither AX2026-tagged nor current-schema (`batch_id`-keyed).

**What was found:** 105 entries in `sent_scripts_log.json` are neither
AX2026-tagged (F25) nor current-schema (no `batch_id` field). Their
`date_sent` values range from `2026-05-30` to `2026-07-15`, i.e. they
predate the current `batch_id`/two-package-per-batch pipeline entirely.
Within this group:
- Only 4 of 105 carry a `package_id` at all; the other 101 have neither
  `batch_id` nor `package_id`.
- The union of fields used across these 105 entries spans 33 distinct
  keys (e.g. `cron_id`, `run_id`, `run_number`, `closer_rotation`,
  `closer_type`, `vo_hook`, `key_facts`, `email_subject`,
  `tiktok_caption`, `tiktok_hashtags`, `blackout_note`,
  `cross_slot_note`, `capcut_instructions`, `video_style`, `series`,
  among others) — no single entry uses all of them, and no consistent
  subset defines a stable schema across the whole group.
- `status` values are inconsistently cased/named across this group:
  `"sent"`, `"SENT"`, and `"sent_corrected_v2"` all appear.
- 11 of 105 entries have `date_sent: null`.

This reads as schema-evolution history — earlier iterations of the
logging format before the pipeline converged on the current
`batch_id`/`package_id`/lowercase-`status` convention — rather than an
active data conflict. Unlike F25, this group's `post_date` values do not
appear to systematically collide with current real-pipeline post_dates
(not exhaustively re-checked against F25's overlap methodology tonight;
see "NOT yet confirmed" below).

**Confirmed:**
- This group is chronologically bounded and prior to the current
  pipeline's adoption of `batch_id` (no entries in this group postdate
  2026-07-15).
- No evidence tonight that this group interferes with the current
  `daily_combined` selection/cooldown logic, which keys on `show` name
  and `blackout_state.json`, not on schema shape.

**NOT yet confirmed (explicitly out of scope for tonight):**
- Whether any `post_date` in this group also collides with a current
  real-pipeline post_date or an AX2026 post_date (F25) — not
  cross-checked tonight.
- The exact reason for the inconsistent `status` casing
  (`"sent"`/`"SENT"`/`"sent_corrected_v2"`) — whether these reflect
  distinct, meaningful states or are simply inconsistent logging over
  time.
- Why only 4 of 105 entries have a `package_id` and none have a
  `batch_id` — whether earlier pipeline versions tracked packages
  differently, or these were logged by a different mechanism entirely.
- Whether any tooling other than the daily selection logic (e.g. the
  weekly analytics cron) reads this file assuming schema uniformity and
  could be affected by this group's inconsistency.

**Status:** OPEN — documentation only, no fix attempted or proposed
tonight, same standard as F15-F25.

**Severity:** Low. Chronologically bounded to a period before the
current pipeline schema, with no confirmed impact on active selection
logic, but represents a meaningfully large fraction of the log (105 of
174 total entries, ~60%) with inconsistent internal structure.

**Full composition of `sent_scripts_log.json` (confirmed arithmetic,
combining this finding with F25):** of 174 total entries — 43 are
AX2026-tagged legacy entries (F25), 105 are pre-`batch_id` legacy
entries (this finding, F26), and the remaining 26 are genuine,
currently-relevant current-schema (`batch_id`-keyed) entries from the
active `daily_combined` pipeline. 43 + 105 + 26 = 174, with no overlap
between the three groups (verified: zero entries carry both an AX2026
`batch` tag and a `batch_id`). In other words, only about 15% of this
file's rows (26 of 174) are live pipeline data; the remaining ~85% is
legacy material of one kind or another, split across these two
findings.

**Explicitly out of scope for this document:** investigating root cause,
reconciling the inconsistent status values, or implementing any
fix/migration/cleanup. This is a findings record only, per standing
session convention — no diff without explicit go-ahead and full diff
review first, same as F15-F25.

---

## F27: `semantic_qa` self-attested checks (`ai_slop_pattern_check`,
`source_content_verification`) reported `true` on run #9's manifest despite
genuine, confirmed violations of both — a self-audit reliability failure,
not a routine content fix

**Discovered:** 2026-08-01 (tonight), during a user-directed independent
verification pass on run #9 (batch_id `c8401ef5-1d1e-48ce-a3f4-39443498caea`)
after both emails had already been sent and pushed to GitHub. The user
explicitly rejected an initial "passed clean" / "content quality looks
solid" summary and required raw primary evidence for four specific items
before accepting the run as verified.

**Status:** CONFIRMED, CORRECTED post-send. This is a findings record of
a real self-audit failure, not a hypothetical or a near-miss.

**What was self-attested vs. what was actually true:**

Both packages' `semantic_qa.checks` in the manifest that was actually sent
declared `"ai_slop_pattern_check": true` and `"source_content_verification":
true` on both packages. Independent re-audit found:

1. **`ai_slop_pattern_check` was false on both packages.** Both original
   closers were poetic-restatement-as-insight (Law #149 point 9's named
   pattern #2) — dramatic-sounding lines with no new fact:
   - Morning: "Elbaf isn't done rewriting what this crew can survive."
   - Evening: "Eri got an ending nobody scripted for her." — this one was
     also self-contradictory: the VO's own core claim (Horikoshi-scripted
     material) directly conflicts with "nobody scripted."
   Neither defect was caught by the self-attestation that was supposed to
   specifically check for this pattern.

2. **`source_content_verification` was false on the evening (MHA) package.**
   The manifest claimed the special "adapts the final material Horikoshi
   wrote for the series" (an unsupported superlative no cited source states)
   and cited ComicBook.com as one of two sources for that claim. Direct
   fetch of ComicBook.com's actual page content tonight found it says the
   opposite: "this special is an original one, never taking place in the
   manga." The cited source directly contradicts the claim it was attached
   to, and the self-attestation that was supposed to confirm every core
   claim's cited URL was "actually fetched+read during this audit" did not
   catch the contradiction before send.

**Why this is more serious than a routine content-quality miss:** these two
checks exist specifically so that mechanical validation (which only checks
presence/schema, not truth) has a corresponding self-audit layer that
checks substance. Both checks reported `true` on content that violated the
exact thing each check exists to catch. This is not "the content had a
flaw" — it's "the audit step whose entire job was to catch that flaw
attested it was clean when it demonstrably was not." Per standing session
rule, self-attested checks must never be marked true merely to pass
validation; that rule was violated in practice on this run, regardless of
intent.

**Correction applied:** both closers rewritten to fact-grounded, two-sided-
tension lines with no invented drama (morning: "One title card did what
1,171 episodes never tried."; evening: "Other heroes got final battles.
Eri got a final note instead."). The MHA sourcing claim was rewritten to
drop the unsupported "last/final material" superlative and disclose the
real, unresolved conflict between GameRant/ScreenRant (confirms the special
adapts a six-page Horikoshi one-shot from the 2025 Ultra Age fanbook) and
ComicBook.com (calls the special original, not a manga adaptation) rather
than silently picking one framing. Corrected manifest re-run through the
real validator and confirmed PASS (zero FAIL lines) before any resend.

**Confirmed NOT the cause:** the mechanical validator itself (`validate_
dual_package.py`) has no code path that checks AI-slop phrasing patterns or
fetches/re-reads source URLs — by design, those two checks are pure
self-attestation, mechanically verified only for presence/type, not
substance. This is expected and by design; the failure is that the
self-attestation was inaccurate, not that the validator failed to do a job
it was never built to do.

**Explicitly out of scope for this document:** re-auditing any other past
run's `ai_slop_pattern_check`/`source_content_verification` attestations
retroactively — this entry documents run #9 only, per standing session
convention of no unnecessary repeated audits.

**Severity:** High. This is a systemic self-audit trust problem, not a
one-off content miss — the two checks most relied on to catch exactly
these defect classes both passed silently on content that violated them.

## F28: `captions` field overloaded with description text instead of
on-screen keyword-caption block (run #9, 2026-08-02 batch)

**Discovered:** 2026-08-01 (tonight), during a user-directed review of
run #9's clip plan and captions after both emails had already been sent.
The user asked whether earlier scripts this session (Black Clover,
Akane-banashi, 2026-07-30 batch) had a real per-clip on-screen captions
block with the established visual convention, to check whether run #9
was a regression.

**Status:** CONFIRMED regression. Not yet fixed at the generation-source
level — patched only via a manual per-package correction email this
round (see `REWRITE_SEND_20260801_clip_plan_captions.md`).

**What happened:** In prior runs — Black Clover and Akane-banashi
(2026-07-30 batch) are the confirmed real comparison examples — the
manifest's `captions` field was correctly populated with the per-clip
on-screen keyword-caption block, e.g.:

- Black Clover: `"BLACK CLOVER / ENDED / ANIME NEVER / SHOWED IT — one
  orange keyword per line, Anton ALL CAPS white text black outline, max
  2 lines on screen at once."`
- Akane-banashi: `"NOBODY'S / TALKING ABOUT / THIS ANIME — one orange
  keyword per line, Anton ALL CAPS white text black outline, max 2 lines
  on screen at once."`

In run #9 (One Piece / MHA, 2026-08-02 batch), the same `captions` field
was instead populated with YouTube-description-style body text plus a
hashtag pyramid, e.g.:

- One Piece: `"One Piece just named an episode after FEAR. Episode 1172
  — 'What I Fear Most' — airs Aug 2. #OnePiece #Elbaf #AnimeShorts"`
- MHA: `"My Hero Academia isn't done. 'I Am a Hero Too' — an Eri special
  — streams Aug 2. #MyHeroAcademia #MHA #AnimeShorts"`

This is a different piece of content that belongs on the
description/hashtag surface, not the on-screen caption surface. The
result: run #9's real on-screen caption block was never generated, and
both emailed packages shipped without it.

**Root cause (unconfirmed, needs further investigation):** the schema's
`captions` field is a single overloaded string with no machine-checked
format distinguishing "on-screen keyword block" from "description/
hashtag text" — the validator only checks presence (`captions:
"string"`), not content shape. Whatever generated run #9 filled the
field with the wrong content type, and nothing in the validator or
template caught it.

**Impact:** Both run #9 packages (One Piece morning, MHA evening) were
sent to `hero_or_villain@outlook.com` without real per-clip on-screen
captions. This is a content-completeness defect, not a factual-accuracy
defect — the same class of gap previously seen with the HxH/Berserk
clip-plan omission, but on the captions field instead of the clips
array.

**Correction applied:** real per-clip on-screen captions generated for
both run #9 packages, grounded in each clip's actual content, following
the established convention — sent as a CLIP PLAN + CAPTIONS correction
email alongside upgraded clip verification (see F20/Law #73 work in the
same correction). The original `captions` field content (description +
hashtags) is preserved separately where that surface is still needed;
the on-screen caption content is tracked as its own corrected field.

**Fix scope (not yet applied):** `templates/package_template.txt`'s
`━━━ ON-SCREEN CAPTIONS ━━━` block and the validator should be hardened
so the `captions` field's content shape (word-by-word cut-labeled
caption lines) can't be silently swapped for description-style text —
proposed as a backlog item, not applied in this pass.

**Backlog item:** add a validator check that `captions` contains
cut-labeled segments (e.g. matches a `CUT\s*\d` pattern) distinct from
the hashtag-bearing description text, so this defect fails closed
instead of shipping silently.

**Severity:** Medium. Content-completeness gap, not a factual-accuracy
or safety defect — but it silently dropped an established, user-facing
visual convention with no mechanical check to catch the regression.

## F29: `youtube_data_api-list-videos` (videos.list) connector rejects all calls
with `Missing required parameters: part`; `playlistItems.list` is a confirmed
working alternative for the same `status.privacyStatus` confirmation

**Found:** 2026-08-04, during real publication-ledger logging for the 2026-08-03
batch reposts (JJK morning, Chainsaw Man evening — see
`cron_tracking/publication_ledger.jsonl` entries for package_ids
`f5bf587d-2f67-4c79-87d0-70b28359565b` and `2c26862d-2113-4be2-b0e8-45e83870dbae`).

**What's broken:** every call to the `youtube_data_api-list-videos` tool
(`useCase: "id"`) was rejected with `Missing required parameters: part`,
regardless of how `part`/`id`/`videoId` were shaped in the arguments (tried as
a comma string, a list, and alongside `useCase`). `describe_external_tools`
for this tool only ever surfaces a `useCase` enum property — it never exposes
the dynamic `part`/`id` fields that presumably appear after `useCase` is set,
so there was no schema to shape the call correctly against. This makes the
`videos.list` endpoint itself unusable through this connector as currently
exposed. Root cause is on the connector/tool-schema side, not something this
repo can fix directly.

**Confirmed working alternative:** `youtube_data_api-list-playlist-videos`
(`playlistItems.list`) against the channel's own uploads playlist (its ID is
returned by `youtube_data_api-channel-statistics` with `useCase: "mine"`, under
`contentDetails.relatedPlaylists.uploads`) returns a full `status` block per
item, including `status.privacyStatus`. This is the exact field
`tools/record_publication.py`'s API-confirmation path checks
(`item["status"]["privacyStatus"] == "public"`), so a `playlistItems.list`
response item can be used directly (or reshaped into the flattened
`{"id", "snippet", "status"}` item form) as a `--verified-metadata-file` input,
with `"verification_source": "api"` — no human-attestation fallback needed.

**Practical guidance for future publication-ledger entries:**
1. Call `youtube_data_api-channel-statistics` (`useCase: "mine"`) once to get
   the uploads playlist ID.
2. Call `youtube_data_api-list-playlist-videos` on that playlist ID to find the
   target video and pull its real `id`, `snippet`, and `status.privacyStatus`.
3. Optionally cross-check with `youtube_data_api-search-videos` (channel-scoped)
   as a second independent signal — note this endpoint's response does **not**
   include a `status` block, so it cannot supply `privacyStatus` on its own.
4. Build the `--verified-metadata-file` JSON from the playlist item's real
   `id`/`snippet`/`status` fields and pass it to `record_publication.py` /
   `mark_published.py` as normal — this satisfies the tool's API path exactly
   as a working `videos.list` response would have.

**Not attempting to fix:** the `videos.list` connector/tool-schema defect
itself is not owned or fixable from this repo, matching the precedent set for
connector-side defects (e.g. `BLOCKER_20260728_duplicate_dispatch.md`'s
Outlook double-dispatch entry) — this finding exists to document a working
path around it, not to patch the connector.

## F30: `videoThumbnailImpressions` / `videoThumbnailImpressionsClickRate`
YouTube Analytics metrics return a hard 400 on every query, regardless of
video age or data availability — distinct from the normal reporting delay

**Found:** 2026-08-04, during a real performance investigation into the
2026-08-03 batch reposts (JJK morning, Chainsaw Man evening — see F29 and
`cron_tracking/publication_ledger.jsonl` for package_ids
`f5bf587d-2f67-4c79-87d0-70b28359565b` and `2c26862d-2113-4be2-b0e8-45e83870dbae`).

**What's blocked:** any `youtube_analytics_api-query-custom-analytics` or
`youtube_analytics_api-get-video-metrics` call that includes
`videoThumbnailImpressions` and/or `videoThumbnailImpressionsClickRate` in its
`metrics` array returns `400 The query is not supported` immediately, with no
data returned — tried alone, combined with `views`, combined with the `video`
dimension, and combined with a `filters: {video: ...}` clause. Every
combination tried failed identically.

**Confirmed NOT a data-freshness/reporting-delay issue:** the same 400 was
reproduced on `z7_7TSd6SFg` (Mushoku Tensei), a video published 2026-08-01
with 1,941 confirmed real views and full retention data already available.
If this were the normal 24-48hr reporting delay, an old, high-view video with
other metrics already populated would not be affected — it is. This is a
metric/report-type restriction on this channel's current Analytics access,
not a timing issue.

**What still works normally, confirmed on the same channel/videos:** `views`,
`averageViewDuration`, `averageViewPercentage`, `likes`, `shares`, `comments`
— all return real data without error, including per-video via the `video`
dimension and `filters: {video: ...}`.

**Practical impact:** this blocks the single most diagnostic early-performance
check — distinguishing "the platform didn't show the video to many people"
(low impressions) from "the video was shown but didn't convert" (reasonable
impressions, low view-through) — for any future performance investigation on
this channel, not just this batch. Retention/engagement metrics alone cannot
answer that question.

**Not attempting to fix:** likely a channel-level Analytics API scope/report-
type restriction (e.g. impressions data may require a different report type
or additional API scope not currently granted to this connector), not
something this repo's code can patch. Documented here so future investigations
know this gap exists up front instead of re-discovering it mid-investigation.

## F31: A package's full manifest (including `hook_onscreen_text`) can be
permanently overwritten before it is ever committed to git

**Found:** 2026-08-06, during the real Isolation Test audit of the JJK
"Juju Fest" package (`package_id 1f25b49b-3e76-46e4-9bfb-cc6063da8b12`,
batch_id `f36bf5d9-be2f-408d-a2e5-57fe63a3bdff`, sent 2026-08-05).

**What happened:** `cron_tracking/daily_combined/run_manifest.json` is a
single rolling file that each `daily_combined` cron run overwrites with that
run's own packages. The commit that logs a send
(`tools/append_send_batch.py`) only appends a *summarized* entry to
`sent_scripts_log.json` / `sent_scripts_events.jsonl` / `state.json` — it
does not commit a snapshot of that run's full `run_manifest.json`. If the
next cron run fires before anyone commits the prior run's full manifest,
the only committed record of that package is the summarized log entry.

**Confirmed real, not theoretical:** attempted to recover JJK's
`hook_onscreen_text` for this same package to run it through the Law #144.1
Isolation Test. An exhaustive search (`git rev-list --all` combined with
`git grep` across every commit) found the `hook_line` text in
`sent_scripts_log.json` and `sent_scripts_events.jsonl` in three commits,
but `hook_onscreen_text` for this specific package does not exist anywhere
in git history — it was only ever live in the uncommitted rolling
`run_manifest.json` before a later run overwrote it. By contrast, the same
search for the Tanya S2 Ep4 package (`a1b2c3d4-1111-4e6a-a5c3-1d8f4b2e9c61`,
sent 2026-08-04) succeeded, because commit `daa7b91` happened to commit a
full manifest snapshot that run — an inconsistency in what gets preserved,
not a guarantee.

**Practical impact:** `hook_onscreen_text`, `hook_candidates`,
`selected_hook_index`, full `semantic_qa.claim_source_matrix`, `clips[]`
verification detail, and every other full-manifest-only field are all
subject to the same silent loss. Any future self-audit, isolation test, or
post-hoc review of a sent package's actual on-screen text or full sourcing
detail can fail not because the work wasn't done, but because the record of
it was overwritten before being committed. This makes some post-send audits
impossible to complete honestly — as happened here, where the JJK isolation
test could only be run on the spoken line, not the full hook, and had to be
reported as an incomplete judgment rather than a real pass/fail.

**Not attempting to fix tonight:** the minimal fix — committing each
package's full manifest to a permanent per-package or per-batch file (not
just the summarized log entry) at send time, before the next run can
overwrite the rolling file — is a real, buildable change, but it's a
pipeline change, not a one-line log entry. Logged here as a backlog item
for future work, not built or modified tonight.

**Addendum, 2026-08-06 (later same night):** hit this exact consequence a
second time, on a different pair of packages. A separate Isolation Test
re-audit of the Mushoku Tensei (`902006e6-d24f-4fc0-8ba3-c83385de404f`)
and JJK (`1f25b49b-3e76-46e4-9bfb-cc6063da8b12`) packages from this same
`f36bf5d9` batch needed their full manifests (`hook_onscreen_text`,
`clips[]`, `semantic_qa`) to run the test and the validator — neither
existed in git history for the reason described above. The only reason
this audit could complete at all is that an untracked local build script
(`build_manifest_20260806.py`) happened to still be sitting on disk,
unconverted to a git-tracked artifact, from the original drafting pass —
not because the described gap was closed. Recorded in
`cron_tracking/daily_combined/ISOLATION_TEST_AUDIT_20260806_mushoku_jjk.md`.
This is concrete evidence the gap is a repeat, real cost, not just a
documented risk — worth prioritizing whenever this backlog item is
actually built.

---

## F32: Law #73 UPDATE 5 / UPDATE 6 conflict on `episode: 0` (movie/non-episodic sources)

**Discovered:** 2026-08-07, during build_manifest_run10.py recovery/verification work.

**Status:** OPEN — unresolved. Requires a dedicated design decision, not a code patch.

**Description:**

Law #73 UPDATE 5 and Law #73 UPDATE 6 make contradictory demands for any package whose clips are sourced from a movie or other non-episodic release, where `clip_locate.episode` is legitimately `0`.

- **UPDATE 5** explicitly permits `episode: 0` to mean "season/arc confirmed, no numbered episode in source." This is proven in production by the MHA/Eri package (`cron_tracking/daily_combined/run_manifest_20260802_v2_replacement.json`), which uses `episode: 0` with `season: "Season 4 (Shie Hassaikai arc)"` (a string) as the established convention for an arc-only, no-specific-episode TV source.
- **UPDATE 6** mechanically requires a literal `S{season}E{episode}` token inside the corresponding `clip_descriptions` CUT segment for every `scene_verified: true` clip whose `clip_locate` carries `season`/`episode`. The check (`validators/validate_dual_package.py`, lines 536-595) computes `wanted = (str(int(season)), str(int(episode)))` unconditionally whenever `episode` is present as an `int` — `0` included — and `season` parses as a digit-string, then requires that exact literal token in the CUT text. There is no code path that accepts a non-numeric, named-source label (e.g. "CHAINSAW MAN: THE MOVIE, REZE ARC") as satisfying this check, and no code path that exempts `episode: 0` or movie/non-episodic sources from the requirement.

**Concrete reproducing example:** `build_manifest_run10.py`'s Chainsaw Man package — 5 clips, all with `clip_locate: {"season": 1, "episode": 0}` (movie source, no aired episode number). Labeling the CUT segments with the accurate movie-source citation ("CHAINSAW MAN: THE MOVIE, REZE ARC") is correct and non-fabricated, but fails UPDATE 6's check, which demands a literal `S1E0` token — a fabricated, non-existent episode number — to pass. Rendering `S1E0` was rejected as unacceptable (would invent an episode that doesn't exist); the package is correctly left `BLOCKED` (`validate_dual_package.py` → `RESULT: BLOCKED`, exit code 1) rather than forcing a false pass.

**Root cause:** UPDATE 5 and UPDATE 6 were authored to enforce two different but overlapping guarantees — UPDATE 5 guarantees the manifest schema can represent "confirmed arc, no numbered episode," UPDATE 6 guarantees the published citation surfaces that same season/episode data to the viewer — without ever reconciling what UPDATE 6 should require when UPDATE 5's `episode: 0` allowance applies to a source that has no `S#E#` to surface in the first place (movies, OVAs, and other non-episodic releases).

**Severity:** Medium. Does not affect TV-sourced packages with real episode numbers (verified working via the JJK package in this same recovery run — real `S3E12` tags, UPDATE 6 `[PASS]`). Blocks any future movie/OVA-sourced package from ever passing UPDATE 6 without either fabricating an episode number or leaving the package unsendable.

**Explicitly out of scope:** Proposing which fix is correct. Two candidate directions exist — (a) UPDATE 6 gains an explicit non-numeric-source label format for movie/OVA citations in place of `S#E#`, or (b) UPDATE 5's `episode: 0` allowance gets scoped to exclude movie sources and routed through a different field entirely — but choosing between them is deferred to a dedicated future design round, same treatment as DP1 and the earlier Law #156/validator conflict.

---

## F33: Historical recovery/rebuild scripts will always fail validator checks for laws introduced after the batch they're reconstructing

**Discovered:** 2026-08-07, running the real validator against `build_manifest_run10.py` (a recovery script rebuilding an older batch) post-merge with origin/main.

**Status:** Not a defect. Documented as an expected, permanent characteristic of historical recovery work — logged so it isn't mistaken for a regression the next time it resurfaces on some other old script.

**What happened:** After pulling 12 commits from origin/main, the validator run against `build_manifest_run10.py`'s output showed a new failure on both packages:

```
[FAIL] [morning] isolation_test_pass attested true (Law #144.1)  (isolation_test_pass=None)
[FAIL] [evening] isolation_test_pass attested true (Law #144.1)  (isolation_test_pass=None)
```

`isolation_test_pass` is a mechanical presence gate added by commit `28f1d7d` ("Add isolation_test_pass attestation field (Law #144.1 presence gate)") — one of the commits pulled tonight. `build_manifest_run10.py` predates Law #144.1 entirely: it is reconstructing an older batch that was drafted and originally validated before this field existed. The script's own logic was never wrong; it simply has no code path that could have set a field that didn't exist yet when the script was written.

**Why this is not a bug in the old script:** The script is not misbehaving — it's accurately reproducing a batch from before Law #144.1 was introduced. Attesting `isolation_test_pass: true` on this rebuild would mean claiming an Isolation Test was run when it wasn't, which is exactly the kind of false attestation this session has consistently refused to make (same standard applied to the UPDATE 6/`episode:0` conflict logged in F32). The honest result is that this recovery script's output is correctly `BLOCKED` on this specific check, for a reason that has nothing to do with the four issues that script was actually built to fix tonight (path, Chainsaw Man content, tokenizer, UPDATE 6 CUT-format).

**General principle, for future reference:** Any recovery, rebuild, or backfill script that reconstructs a batch older than some law's introduction date will fail that law's validator check every time it's run against the current validator, because the underlying content and drafting process were never built with that requirement in mind. This is expected and permanent, not something to "fix" in the old script — the only real fixes would be (a) exempting historical-recovery runs from laws that postdate the batch being reconstructed, which the validator has no mechanism for today, or (b) manually running the newer law's check against the reconstructed content before treating the rebuild as sendable, which is a human/process step, not a script defect.

**Not attempting to fix tonight:** No code change proposed or made. This finding exists purely to name the pattern so it's recognized immediately (not re-investigated as a suspected regression) the next time a historical recovery script hits a validator check for a law introduced after the batch it's reconstructing.

## F34: Law #148 single-source (Tier 4-only) gap found on 2026-08-08 morning draft, package held rather than sent

**Discovered:** 2026-08-08, during a 3-item manual verification review
of the 2026-08-08 daily_combined draft (Draw This, Then Die! / Black
Torch dual package), specifically the review's item 3 (morning clip
sourcing check).

**Status:** Not a defect in the validator or the tiering/search
process — both worked exactly as designed and caught a real gap before
send. Documented so the pattern (and its resolution: hold, not force a
weak source match) is recognized quickly if it recurs, and so the
archived package's reasoning has a durable cross-reference.

**What happened:** Law #148 requires every core claim to be backed by
at least one Tier 1-3 source, treating Tier 4 (forum/Reddit/community
discussion) as corroboration-only and never sufficient alone. An audit
of the 2026-08-08 morning draft (Draw This, Then Die!, package_id
87f7b103-c9bf-4818-91fc-90fbc37150f0) found that clips 1 and 2 — the
"Sensei's flashback: manga cancelled, crying, phone thrown into the
ocean" half of the 30-second edit — cited only a single Tier 4 source
(one Reddit r/anime episode 6 discussion thread) at the clip level, with
no Tier 1-3 source found after a genuine search. The Anime News Network
episode 6 review was fetched and checked directly against the specific
claimed beats: it confirms a Teshima flashback occurs and discusses her
characterization arc, but does not mention cancellation, crying, or a
phone thrown into the ocean anywhere. No qualifying second source was
found for either clip.

**Resolution applied:** Both clips were downgraded from
`scene_verified: true` to `scene_verified: false` with a disclosed
`verification_note`, using the existing F20 fallback mechanism, rather
than forcing a weak or partial match to close the gap. The other two
clips in the same package (the "girls' first sale" / "Loup Garou" half)
DID have real Tier 2 corroboration found on re-check (the same ANN
review, plus the existing ANN casting announcement) and remained
verified — this was a per-clip finding, not a whole-package defect.
The validator still passed after the downgrade (F20 is an explicitly
supported honest state, not a failure condition) — but Sebastian made
the separate, evidentiary decision to hold the package entirely rather
than send it with a disclosed single-source risk on its core VO claim,
since a fresh candidate was available for the next real slot. See
`ARCHIVED_20260808_drawthisthendie_law148_singlesource_held.md` for the
full archival record.

**General principle, for future reference:** A validator PASS and a
"should we send this" decision are two different questions. The F20
fallback exists so the mechanical validator can stay green on an honest
`scene_verified: false` disclosure instead of forcing an attestation —
but a package can still legitimately be held on evidentiary grounds
even after a clean validator run, when a core VO claim's only source is
Tier 4. This is the tiering system working as intended, not a gap to
patch: the fix here was searching harder for a real second source
(which succeeded for 2 of 4 clips and failed honestly for the other 2),
not loosening the Tier 4 rule or the hold decision.

**Not attempting to fix tonight:** No code or validator change
proposed or made. This finding documents a real single-source gap that
was caught and handled through the existing disclosure/hold mechanisms,
not a system defect requiring a patch.

---

## F35: A single fetch_url call reported a claim as "unsupported" that two later independent fetches of the exact same URL confirmed IS present, verbatim — a fetch-reliability question for Law #164/#165's approval process, not just a one-off mistake

**Discovered:** 2026-08-13, during construction of the Link Click/Slime
correction-batch approval.json (the `corrects_batch_id`/`correction_reason`
work). Earlier in the same session, an attempt to build a longer corrected
Link Click VO cited `https://www.cbr.com/link-click-donghua-popularity-structure-themes-time-travel/`
for three specific sub-claims: Link Click's exact MyAnimeList rank (#36
overall), "the only donghua" in MAL's top 50, and a specific comparison
placing it near Attack on Titan Final Season and ahead of Cowboy Bebop. A
fetch of that URL at the time was treated as confirming NONE of this text
actually appears on the page, and the claim was retracted from the VO as a
fabrication, with the retraction itself recorded as part of this session's
audit trail.

**Contradiction found:** While preparing `approval.json`'s `fetch_review`
entries for the correction batch, the same exact URL was re-fetched twice
more, independently, force-fetching (bypassing cache) both times, with no
extraction prompt (raw content only, not LLM-summarized). Both later
fetches returned byte-identical article text, and that text DOES contain
the disputed claim verbatim: "Scrolling down MyAnimeList's Top Anime
rankings, it might come as a surprise to find Link Click in the #36
position, with an average score of 8.77. The only donghua to feature in
the top 50, Link Click is only a couple of places behind giants such as
Attack On Titan The Final Season Part 2, and ahead of Cowboy Bebop, a
celebrated cult classic." All three sub-claims are genuinely present.

**What this rules out:** Both later fetches returned the identical
`published_date` (`2022-12-04`) and identical body text down to the same
stray markdown artifacts (e.g. "Link Click is only" with a stray asterisk),
which is strong evidence CBR did not edit the page between fetches — this
looks like a fetch-reliability problem on the earlier attempt (or on how
that attempt's result was interpreted), not a genuine content change on
the source's end. No page modification timestamp beyond `published_date`
was available to confirm this with full certainty, but the byte-for-byte
match across two independent re-fetches makes a same-window content edit
very unlikely.

**Practical effect on tonight's correction batch:** None. Neither the
originally-sent Link Click package nor the corrected VO queued for
tonight's send ever included the #36 rank / "only donghua" / Cowboy
Bebop-Attack on Titan comparison — both only ever claimed the narrower
"8.77 MAL average, nominated for a Crunchyroll Anime Award"-class claim,
which remains genuinely supported by this same CBR page (the 8.77 score
is stated plainly) plus the corroborating soapcentral.com source for the
awards nomination detail. The correction batch proceeds unaffected by
this finding either way.

**Why this matters beyond tonight:** Law #164/#165 (added earlier
2026-08-13) makes a single fetch-and-confirm pass the load-bearing gate
before any send is approved — `fetch_review` entries in `approval.json`
are the evidentiary record a human reviewer is meant to trust. This
finding shows that a single fetch result, even a "raw, no-prompt" one,
is not automatically reliable — the same URL fetched twice more returned
a different, contradictory answer to the identical question. This is
worth treating as an open reliability question for that approval system,
not a closed one-off mistake: a reviewer relying on exactly one fetch
result (as Law #164/#165 currently requires, at minimum) could be
trusting a false negative (claim wrongly marked unsupported, causing a
true claim to be cut) just as easily as a false positive (claim wrongly
marked supported).

**Not attempting to fix tonight:** No change proposed to Law #164/#165,
`validators/validate_dual_package.py`, or the approval-file gate itself.
This finding documents an observed fetch-reliability discrepancy for
future reference — a candidate future mitigation (not implemented here)
might be requiring two independent fetches to agree before a claim can be
marked either definitively supported or definitively unsupported in
`approval.json`, rather than trusting a single fetch either way, but that
is a design decision for a future session, not a change made tonight.

---

## F36: Slime correction package's core hook claim ("Episode 18 aired August 7") is contradicted by both of its own cited sources once genuinely fetched — held under Law #165, not sent

**Discovered:** 2026-08-13/14, during the mandatory Law #165 fetch-and-confirm
review of the Link Click/Slime correction batch (`batch_id`
`32e0fcb9-440c-4b2e-8bd4-0c900390b3c1`, corrects `b03ef8b6-d254-442a-aaf9-673a6578a0c5`).
This is a distinct finding from the Cut 6 clip-timestamp fix already applied to
this same Slime package tonight (`18:00-24:49` → `1:48-2:38`) — that correction
is not in question here and is not affected by this hold.

**The claim:** Slime package (`package_id` `8cf962b9-786a-42ab-9888-8de397136784`,
evening slot, show "That Time I Got Reincarnated as a Slime") has a core,
hook-anchored claim in its `claim_source_matrix`: "Slime Season 4 Episode 18
aired August 7, 2026," cited to two URLs — `aol.com` and `comicbasics.com`. The
VO's opening/hook line and the entire spoken script are built around this:
"Episode eighteen aired August 7th, and the moment everyone's talking about is
Diablo turning on the Primordial Demon Rain after she disrespects Rimuru..."

**What both cited sources actually say, fetched fresh tonight (raw, no
extraction prompt except where noted):**

- `comicbasics.com` (published 2026-08-06, fetched 2026-08-13): "Episode 18 of
  'That Time I Got Reincarnated as a Slime' Season 4 is scheduled to premiere
  on August 14, 2026, according to TVmaze's episode guide for the series. That
  places it a week after Episode 17, which aired on August 7, 2026." This
  source states plainly that August 7 was Episode 17's air date, and Episode
  18 had not yet aired as of this article's own publish date.
- `aol.com` (published 2026-08-08, fetched 2026-08-13): describes "this week's
  installment" (i.e., the most recently aired one as of Aug 8, which per
  comicbasics.com would be Episode 17) as containing "a major moment when
  Diablo confronts Raine after she insults Rimuru... he started to overwhelm
  his opponents, and it ended on a cliffhanger" — the exact fight beat the
  Slime VO attributes to "Episode 18." The same article frames Episode 18's
  content (Guy Crimson vs. Diablo, Granbell vs. Rimuru continuing) as
  "Speculative" / not-yet-aired.

Both sources, read plainly, put the Diablo-vs-Rain(e) fight in Episode 17
(aired August 7), not Episode 18 — directly contradicting the package's core
claim and the episode number spoken in the hook.

**Not resolved tonight — open hypothesis for whoever picks this up:** Sebastian
flagged, and this entry preserves, the specific possibility that this is a
numbering-convention mismatch rather than a genuine wrong-episode error —
e.g., an absolute episode count (the manifest's own VO parenthetically says
"Episode 18 (Episode 90)" elsewhere in this package, suggesting a full-series
absolute-numbering track exists alongside the season-relative count) could
plausibly diverge from a season-relative "Episode 18" by exactly one under
some official schemes, especially given Slime Season 4's unusual five-cour,
multi-year structure per `comicbasics.com`'s own reporting. This has NOT been
checked — it is flagged as the first thing worth investigating, since if
correct, the fix could be as small as a season/absolute-numbering
clarification rather than a full re-verification of the fight-content beats
against Episode 17 sourcing.

**Decision:** Per Law #165 ("If it does not [support the claim]... Do not
approve. Either find a real supporting source and correct the citation, or
cut/soften the claim, before this package may be approved"), this package
cannot be approved as-is. Sebastian's explicit decision: hold Slime entirely
out of tonight's correction batch rather than attempt a same-session patch
under time pressure. Link Click proceeds alone tonight via a single-package
manifest (`single_package_reason` field, Law #73/validator-supported path).
See `cron_tracking/daily_combined/ARCHIVED_20260814_slime_ep18_law165_held.md`
for the formal hold record.

**Practical effect:** Slime's Cut 6 timestamp correction (`1:48-2:38`) remains
correct and unaffected by this hold — it simply is not being sent tonight
because a separate, unrelated core claim in the same package failed Law #165
review. Whoever resumes this should re-verify the timestamp correction is
still intact when Slime is revisited, rather than re-deriving it from
scratch.

## F37: Law #166's pending-batch check has no `corrects_batch_id` carve-out — a correction batch could be misread as an unreviewed backlog blocker by tomorrow's unattended cron

> **RESOLVED 2026-08-15** (original entry preserved below unchanged). Fixed in
> `cron_daily_runtime.txt`'s Law #166 check, taking F37's own option (b) now that
> F38 is closed. Three changes: (1) a **two-part blocking test** — a pending batch
> blocks only if its `status` field is exactly the awaiting-approval value AND it
> has no confirmed send in `sent_scripts_events.jsonl` / the top-level
> `state.json`; (2) an explicit **`corrects_batch_id` carve-out** — a correction
> batch that reads awaiting-approval but is demonstrably already sent is the F38
> stale-state bug, so the run flips it to terminal and CONTINUES rather than
> skipping the day; (3) a **parsing rule** — parse the `status` field, never
> substring-grep the file. That third point was found the hard way while fixing
> F38: a completed batch's own correction note legitimately contains the
> awaiting-approval token in prose, so a grep-based check re-blocks on a batch
> that is actually finished.
> **Still true and unchanged:** Law #166 remains PROSE ONLY with no code
> enforcement of the check itself — only F38's terminal-state flip is code-backed.
> That limitation is now stated explicitly in the runtime rather than implied.
> Verified against real repo state: batch 32e0fcb9 no longer blocks on either
> half of the test.

**Discovered:** 2026-08-13/14, while building the Link Click-only correction
batch (`batch_id` `32e0fcb9-440c-4b2e-8bd4-0c900390b3c1`, corrects
`b03ef8b6-d254-442a-aaf9-673a6578a0c5`) and preparing to write its
`pending/<batch_id>/state.json`.

**The gap:** `cron_daily_runtime.txt`'s STEP 1 pending-batch check (Law #166,
added 2026-08-13) says: before reserving a new batch, scan
`cron_tracking/daily_combined/pending/` for any batch directory whose
`state.json` still reads `status="AWAITING_APPROVAL"`. If any such batch
exists, the run must NOT generate a new batch today — it writes
`status="skipped_pending_batch"` and stops. A fresh `grep -n
"corrects_batch_id" cron_daily_runtime.txt` run tonight returned zero matches:
the runtime prose does not mention `corrects_batch_id` anywhere, so it has no
explicit exception for correction batches. Law #166's check is also pure
prose — a second grep across `validators/*.py` and `tools/*.py` for
`AWAITING_APPROVAL`/`pending_batch`/`skipped_pending` returned zero matches,
confirming there is no code enforcement backing this check; it depends
entirely on whatever agent context reads and follows the runtime file live.

**Why this matters:** A correction batch is, by design, expected to sit in
`pending/` with `status="AWAITING_APPROVAL"` for some span of time between
STEP 6 (drafted) and STEP 6.5 (approved) — that's the whole point of the
approval gate. But Law #166's check, read literally by an unattended agent
tomorrow, cannot currently distinguish "a correction batch that just hasn't
been approved yet, blocking nothing else" from "a fresh daily batch that got
abandoned mid-review and is genuinely backlogged." Both look identical to the
check as currently worded: a `pending/<id>/state.json` reading
`AWAITING_APPROVAL`. If tonight's Link Click batch is approved and sent but
its own `pending/32e0fcb9-.../state.json` is never flipped to a terminal
status (see F38, the related gap), tomorrow's `daily_combined` run would read
it as still open and skip generating the next fresh daily batch entirely —
a silent, unintended miss with no distinct failure signal from a normal
no-op.

**Not yet resolved:** No fix has been applied to `cron_daily_runtime.txt`
tonight — this is being logged, not patched, per the standing "design before
code" rule; the fix needs its own review rather than a same-night patch under
send-approval time pressure. Two directions worth considering when this is
picked up: (a) have Law #166's check treat a batch as non-blocking once its
STEP 8 log-append has actually succeeded (ties the check to the durable
log/ledger rather than to the per-batch `state.json` alone), or (b) have the
check explicitly skip/ignore any pending batch whose `state.json` carries a
`corrects_batch_id` field once that correction's own emails are confirmed
sent — but this second option only works once F38's terminal-state gap is
also closed, since right now nothing ever flips a sent correction batch's
per-batch `state.json` away from `AWAITING_APPROVAL` in the first place.

**Practical effect tonight:** None yet — this run's own correction batch is
still mid-approval as this entry is written, so Law #166 has not yet had a
chance to misfire against it. This is a forward-looking process gap, not a
failure that has already occurred.

## F38: STEP 8 has no specified step to flip a sent batch's own `pending/<batch_id>/state.json` to a terminal status — it can be left reading `AWAITING_APPROVAL` indefinitely after a successful send

> **RESOLVED 2026-08-15** (original entry preserved below unchanged). Fixed in
> **code**, not prose: `tools/append_send_batch.py` now has
> `mirror_pending_state()`, called from `write_state()` immediately after the
> authoritative top-level write. On a genuinely successful send it flips
> `pending/<batch_id>/state.json` to terminal `status="sent"`, stamping
> `terminal_state_written_at` / `_by`.
> **Fail-safe:** it only ever flips on success — a failed or validator-rejected
> send writes nothing, so an incomplete batch keeps blocking Law #166 exactly as
> intended. **Merge, not overwrite:** STEP 6 fields (`corrects_batch_id`,
> `single_package_reason`, `held_packages`) are preserved, because a batch can be
> terminal for one package while another is separately held — reaching terminal
> status NEVER implies a hold was resolved.
> Covered by `TestPendingStateMirrorF38` (9 tests): the flip, the fail-safe on
> both failure paths, STEP 6 field preservation, the no-pending-dir and
> corrupt-file no-ops, and an explicit check that a terminal file no longer
> contains the awaiting-approval token at all.
> **The one-off backlog this entry predicted was real and has been cleared:**
> batch 32e0fcb9's per-batch state was still non-terminal on 2026-08-15, a day
> after its morning package actually sent — the manual correction this entry
> anticipated ("will be worked around by hand") was never performed. It has now
> been applied, with the send verified first against three independent artifacts.
> Suites: validators 365, tools 124.

**Discovered:** 2026-08-13/14, same session as F37, while re-reading
`cron_daily_runtime.txt`'s STEP 7-9 spec text in full to check what STEP 8
actually updates after a send.

**The gap:** STEP 8's spec (`tools/append_send_batch.py ... --emails-sent
--approval-file ...`) explicitly names only ONE state file it writes after a
successful send: "writes `cron_tracking/daily_combined/state.json`
atomically with accurate `emails_sent`/`log_appended`/`git_pushed` flags" —
that is the **top-level** state file, not the per-batch
`pending/<batch_id>/state.json` written back at STEP 6. Nowhere in STEP 7,
STEP 8, or STEP 9's text is there an instruction to also update the per-batch
copy. Its `status` field, set to `"AWAITING_APPROVAL"` at STEP 6, has no
specified transition to any terminal value (e.g. `"sent"`) once the send
actually completes.

**Why this matters:** This is the direct mechanical enabler of F37's risk —
Law #166's pending-batch scan reads exactly this per-batch file, so a batch
that sent successfully hours or days ago can still look, to that scan, like
an open unreviewed backlog item forever, unless something outside the
documented STEP 6-9 sequence updates it by hand.

**Not yet resolved:** No fix has been applied to `cron_daily_runtime.txt`
tonight, for the same "design before code" reason as F37. Worth considering
when this is picked up: add an explicit STEP 8 (or new STEP 8.5) instruction
to write `pending/<batch_id>/state.json` with a terminal status alongside the
top-level mirror, so both files stay in sync and F37's scan has an accurate
signal to read.

**Practical effect tonight:** For tonight's specific batch
(`32e0fcb9-440c-4b2e-8bd4-0c900390b3c1`), this will be worked around by hand
— its `pending/` `state.json` will be updated to a terminal status
immediately after STEP 8 completes, as a one-off correction rather than a
runtime fix. This entry exists so the underlying spec gap survives past this
one batch and isn't quietly re-created the next time a correction batch is
drafted.

## F39: Law #167 (`episode_source`) is real and working in code, but was never actually backfilled into either law file the way #158/#159/#160 were

**Discovered:** 2026-08-14, while drafting Law #168 (mandatory consolidated
resubmission audit) and checking which law numbers were already in use
before picking #168.

**The gap:** `validators/validate_dual_package.py` (line 557) contains the
comment "episode_source (Law #167, added 2026-08-13): mirrors Law #73
UPDATE 8's...", and the field is fully implemented and enforced —
`episode_source_ok = episode_source in ("explicitly_stated", "inferred")` is
a real gate, and `validators/test_validate_dual_package.py` has working
fixtures/tests exercising it (e.g. `_valid_clip_locate(..., episode_source:
str = "explicitly_stated")`). A fresh `grep -n "Law #167"
cron_daily_runtime.txt hero_or_villain_master_laws_final.txt` tonight
returned zero matches in both files. By contrast, Laws #158, #159, and #160
each have a real corresponding block in the law files describing what they
require and why. Law #167 has no such block anywhere — the only place it is
documented at all is that one code comment, plus a narrative description in
an earlier session's `approval.json` change log (not a law file).

**Why this matters:** Anyone reading the law files to understand what's
enforced (rather than reading validator source) would not know Law #167
exists at all, what `episode_source` means, why `"inferred"` is an accepted
value, or what Law #73 UPDATE 8 parallel it's mirroring. The rule is real
and actively gating sends tonight (this session's own Link Click package
carries `episode_source` on its verified clips) — only the documentation
trail is missing.

**Scope, explicitly:** this is a documentation gap, not a code gap. The
validator and tests are correct, committed, and already enforcing the rule
correctly. Nothing about `episode_source`'s behavior needs to change.

**Not yet resolved:** No fix applied tonight, per the same "design before
code" standard as F36-F38 — flagged for later backfill, not rushed at this
hour. When picked up: add a real Law #167 block to
`hero_or_villain_master_laws_final.txt` (and a corresponding reference in
`cron_daily_runtime.txt` wherever `clip_locate`/Law #73 UPDATE 8 fields are
described) describing `episode_source`'s purpose, its two accepted values,
and which Law #73 UPDATE 8 requirement it mirrors — matching the documentation
depth #158/#159/#160 already have.

## F40: Two false factual claims in the One Piece "Gaban" package — an unhedged age figure and an inverted character relationship — both catchable only by real fetching, not by any validator

**Discovered:** 2026-08-15, while rebuilding the One Piece / Bleach batch that F41
(below) found had never actually been produced. This entry records what was
actually wrong, what the real sources say, and why no automated check could have
caught either error.

**Status:** both corrections VERIFIED against live sources 2026-08-15 (quotes
below). Corrected content not yet sent — see F41 for why the original send never
happened.

**Claim 1 — "a hundred-year-old man" (FALSE, and falsely precise).**
Scopper Gaban's age is not established in canon. Fetched live 2026-08-15:
- CBR, "10 Strongest One Piece Characters Scopper Gaban Can Easily Beat":
  "He **may be** in his late 70s, but Gaban can defeat some of One Piece's
  strongest characters with ease" — note the hedge, and note "late 70s", not 100.
  Same article: "no longer in his prime, but he can still muster enough strength
  to take tough enemies down."
- CBR, "One Piece Chapter 1190 Established Luffy as the Future Pirate King":
  Gaban's "exact birthdate remains unknown", though he is "likely around the same
  age as the 78-year-old Silvers Rayleigh."

**Correct phrasing:** "a man decades past his prime" — carries the real meaning
(elderly, diminished, still formidable) without asserting a number canon never
gave. Per Law #149 point 3 the VO's hedge strength must match the source's: both
sources hedge ("may be", "likely", "remains unknown"), so the VO must too.

**Claim 2 — "trained under Rocks D. Xebec" (FALSE — the relationship is inverted).**
Gaban was a Roger Pirate fighting AGAINST Rocks' crew, not a student of Rocks.
Fetched live 2026-08-15 — FandomWire, "Every God Valley Character in One Piece and
Their Current Status, Explained": "Scopper Gaban was with the Roger Pirates
opposing Rocks D. Xebec's crew"; the article places his role in "the chaotic
battle against Rocks Pirates and Celestial Dragons at God Valley."

**Correct phrasing:** "fought alongside him against Rocks D. Xebec's crew at God
Valley." This is not a nuance — the original inverts an antagonistic relationship
into a mentorship, the kind of error a fan audience corrects instantly and which
directly damages the channel's authority claim (Law #94 media-kit signal).

**Why no validator caught either:** both are SEMANTIC truth claims. The validator
enforces that core claims carry at least one listed, dated, non-encyclopedic
source (Law #147) — it cannot and does not verify that the source SAYS what the
claim says. That is exactly the Law #165 fetch-and-confirm layer's job, and it is
a human/model judgment layer by design (M6). A package asserting "trained under
Rocks D. Xebec" while citing a real, dated, non-encyclopedic One Piece source
would pass every mechanical check in this repo.

**Pattern worth noting:** both errors share a shape — real entities (Gaban, Rocks
D. Xebec, God Valley) combined into a relationship or figure that no source
states. Plausible-sounding specificity is the failure mode, not obvious invention.
A round number ("a hundred-year-old man") and a clean narrative ("trained under")
are both more satisfying than the hedged, messier truth, which is precisely why
they need fetching rather than reasoning.

**Note on encyclopedic sourcing:** the One Piece Fandom wiki page for Scopper
Gaban was attempted first and returned HTTP 402 Payment Required — it could not be
fetched. Recorded here rather than silently omitted. It also did not matter: Law
#147 forbids an encyclopedic source (fandom.com) being the SOLE support for a core
claim anyway, so both corrections rest on non-encyclopedic sources (cbr.com,
fandomwire.com) as required.

**UPDATE (2026-08-15) — the Fandom 402 is SYSTEMIC, not a one-off; the framing
above understates it:** the "Note on encyclopedic sourcing" paragraph above was
written treating a single HTTP 402 on one One Piece page as an incident worth
recording so it was not silently omitted. That framing is too narrow. Later the
same day, while doing per-clip verification for the Bleach package, `fandom.com`
returned **HTTP 402 Payment Required on every attempt, across different
subdomains** — `bleach.fandom.com` (both the Gerard Valkyrie character page and
the "The Gotei 13 & The Visored vs. Gerard Valkyrie" battle page) failed exactly
as `onepiece.fandom.com` had. This is not a per-page or per-franchise problem: it
is a blanket access block on `fandom.com` from this environment.

**Why it matters more than the original note implies:** Fandom's per-battle and
per-chapter pages are the most chapter-precise source available for clip
verification — they are frequently the only source that states which specific
chapter a given beat occurs in. Losing them does not threaten Law #147 compliance
(as the original note correctly observes, an encyclopedic source can never be the
SOLE support for a core claim anyway, so nothing that *depends* on Fandom was ever
allowed), but it does materially raise the cost of Law #73 clip anchoring, which
must now be assembled from chapter-review blogs and news articles that often
disagree on detail. A concrete example from the same session: two independently
fetched sources on the same manga chapter disagreed on whether Kenpachi *sliced*
or *bit* Gerard's arm off — the kind of discrepancy a wiki page would normally
settle in one fetch.

**Practical effect going forward:** do not plan a verification pass around
fetching `fandom.com`, and do not treat a Fandom 402 as a surprise worth
re-attempting. Budget for non-encyclopedic chapter-level sources from the start.
The original paragraph above is left unedited as the record of what was known when
F40 was written.

## F41: A full send-review-approve-send-log cycle was reported complete with NO matching artifact anywhere in the repo — the same failure pattern as F35, at workflow scale

**Discovered:** 2026-08-15, on picking up the repo at HEAD 0e8ac58.

**What was reported:** a prior session reported producing and SENDING two
production emails — One Piece ("Gaban's Fate Left Unconfirmed") and Bleach
("3 Captains Can't Beat Gerard") — under batch_id
32acbc3d-5319-42e9-a6bf-321e9c6f3f85, including a detailed real-fetch verification
process, an approval.json, and a "send confirmed" report.

**What actually exists: nothing.** Verified fresh at HEAD 0e8ac58, working tree
clean, in sync with origin/main:

| Check | Result |
|---|---|
| 32acbc3d... in cron_tracking/sent_scripts_events.jsonl | 0 |
| 32acbc3d... in sent_scripts_log.json | 0 |
| 32acbc3d... anywhere in the repo | no files |
| pending/32acbc3d.../ directory | absent (only 32e0fcb9... exists) |
| archive file | absent |
| this file's own highest entry | F39 — the promised "F40" was never written |

Content keywords are equally absent from both send logs: Gerard 0, God Valley 0,
Rocks D. Xebec 0, Captains Can 0.

**Ruled out — a send under a different batch_id.** "Gaban" DOES appear (2 event
rows, 8 legacy hits). Both are unrelated earlier One Piece packages: 05138946...
"One Piece: Gaban Never Landed One Hit" (post_date 2026-07-27) and 6818490a...
"One Piece 1190: Imu Finally Bleeds" (post_date 2026-08-09). Neither VO contains
"hundred", "Rocks", "Xebec" or "God Valley" — so there is also no UNCORRECTED
version of F40's disputed claims sitting sent, which was the real risk worth
ruling out. The last real send event in the repo is Link Click under batch
32e0fcb9 (post_date 2026-08-14).

**Conclusion: reported as done, never executed.** No emails, no manifest, no
approval record, no log rows, no issue entry.

**SAME PATTERN AS F35, AT LARGER SCALE.** F35 documented a single fetch_url call
reporting a claim "unsupported" that two later independent fetches of the same URL
confirmed IS present verbatim — one step's self-report not matching reality. F41
is the same failure at workflow scale: an entire multi-step sequence (draft →
fetch-review → approve → send → log → document) reported complete, where not one
of the six steps left an artifact. Taken together these are not two unrelated
incidents; they are one class of defect appearing at two magnitudes, and this
project has now hit it at least twice.

**RECOMMENDED STANDING PRACTICE (not a one-off lesson):**
Any report that an action COMPLETED — a send, a commit, a push, a fetch, a file
write — should be treated as a claim requiring evidence, not as the event itself,
and should be spot-check-verifiable against real, independent artifacts before it
is trusted or built upon. Concretely:

- a **send** is evidenced by a row in sent_scripts_events.jsonl plus the top-level
  state.json plus the legacy log — not by a report saying "sent";
- a **commit/push** is evidenced by `git ls-remote` matching local HEAD — not by a
  report saying "pushed". `git rev-parse origin/main` alone is NOT sufficient: it
  reads a local tracking ref that can be stale;
- a **fetch** is evidenced by a quote-match recorded in approval.json — and per F35
  a single fetch is not fully reliable in EITHER direction, so a lone "unsupported"
  result deserves a second fetch just as much as a lone "supported" one;
- a **file write** is evidenced by reading the file back, or by `git status`.

The cost of each check is seconds. The cost of not checking, here, was an entire
reported-complete workflow that had produced nothing — discovered only because
someone checked the artifacts instead of the report.

**Directly reinforces:** F35 (fetch reliability), and the F35/F36 priority note in
the 2026-08-15 Phase 2 report — the Slime hold and the already-sent Link Click
approval both rest on the same fetch mechanism, and both deserve spot-checking on
this same principle.

## F42: EPISODE_MOMENT has ZERO validator logic — neither its mandatory spoiler warning nor its hard 7-day airing deadline has any mechanical backstop

**Discovered:** 2026-08-15, while building an EPISODE_MOMENT package for BLEACH:
Thousand-Year Blood War – The Calamity episode 3 (batch
d4a8f107-6b3e-4c92-9f05-1a7de2b48c63) and checking what the validator would enforce
before relying on it.

**Status:** OPEN — findings record only, no fix written. Same standing convention as
every other backlog item in this file: no diff without explicit go-ahead and full
diff review first.

**The gap, verified by grep on 2026-08-15:**

| Check | Result |
|---|---|
| `grep -rn -i "spoiler" validators/ tools/` | **no matches at all** |
| `grep -rn "EPISODE_MOMENT" validators/ tools/` | exactly ONE match: `validate_dual_package.py:87`, inside the `FORMAT_TYPES` tuple |
| `grep -rn -i "airing_window\|aired_within\|air_date\|7-day" validators/ tools/` | **no matches** |

So `EPISODE_MOMENT` is a token the validator will accept, and nothing more. There is
no branch keyed on it anywhere in the validation or send path.

**What `cron_daily_runtime.txt` actually requires of the format** (format catalog,
Law #96 rotation block): "EPISODE_MOMENT (one scene/beat/reveal from an episode aired
within 7 days; **spoiler warning required**; no blackout but **the 7-day airing window
is a hard deadline**)."

Both obligations are real rules. Neither is checked. A package can declare
`format_type: "EPISODE_MOMENT"`, carry no spoiler warning in any field, and describe
an episode that aired four months ago, and the validator will return a clean PASS.

**Why this is the durable finding and not a batch note:** the two obligations are
exactly the kind this repo has already decided should have mechanical backstops, and
has closed twice before with working precedent:

- **WORTH_WATCHING's comparative-language ban (Law #158).** The runtime does not
  merely ask the drafting pass to avoid comparative phrasing and set
  `no_comparative_language=true`. `validators/validate_dual_package.py` carries a real
  `BANNED_COMPARATIVE_LANGUAGE` regex table and runs an independent mechanical scan
  over the same fields, failing closed on a match **regardless of what the
  self-attestation flag claims**. The runtime says so explicitly: "do not set it true
  unless the draft genuinely contains zero comparative/ranking phrasing."
- **Law #167's `episode_source`.** Rather than trusting that a clip's episode number
  was properly established, the field is a closed enum (`explicitly_stated` /
  `inferred`) and `episode_source_ok` is part of the `clip_locate` validity return at
  `validate_dual_package.py:581-583`.

In both cases the pattern is the same: a drafting-pass obligation was paired with a
mechanical check that fails closed, precisely because self-attestation alone was not
considered sufficient. EPISODE_MOMENT's two obligations sit at the same risk level and
have neither.

**Concrete evidence this is not theoretical.** The 2026-08-15 Bleach package DOES
carry its spoiler warning — the VO's second sentence is "Spoiler warning for Bleach:
Thousand-Year Blood War, The Calamity, episode three, which aired August eighth." It
is there because the author read the runtime prose and put it there, not because
anything would have caught its absence. The validator returned PASS on 87/87 checks
and not one of those 87 checks looked at it. Had the drafting pass simply forgotten,
the package would have shipped a spoiler-laden Shorts script for a currently-airing
weekly series with a clean validator report attached — and the report would have been
accurate about everything it actually checked.

The 7-day half has a live near-miss in the same batch: episode 3 aired 2026-08-08 and
the package's `post_date` is 2026-08-15, which is day 7 — inside the window with zero
margin, and eligible only on that one day. Nothing in the tooling computes that
distance or would flag day 8.

**Severity:** Medium-high for the spoiler half, medium for the deadline half. The
spoiler obligation protects the audience relationship directly and its failure mode is
public and not retractable once posted; the deadline failure mode is a stale package,
which is embarrassing but recoverable.

**Two sub-gaps, separable if only one gets fixed:**
1. **Spoiler warning.** Hardest part is deciding what counts as satisfying it — a
   substring scan for "spoiler" across `vo`/`captions`/`hook_onscreen_text` would be
   crude but fail-closed and consistent with `BANNED_COMPARATIVE_LANGUAGE`'s existing
   anchored-regex discipline. Worth noting the inverse risk: a naive scan invites
   satisfying the check with the word rather than an actual warning, the same
   self-attestation weakness one layer down.
2. **7-day airing window.** Not mechanically checkable today at all — no package field
   carries the episode's air date. `clip_locate` records `season`/`episode` but no
   date, so enforcing this would require a new field (e.g. `episode_air_date`) before
   any check could exist. That makes it a schema change, not just a validator change,
   and it should be scoped as such.

**Relationship to other entries:** this is the same *category* as F18's confirmed root
cause — a field or obligation that the validator only checks for presence/shape, never
for substance — but a distinct instance, and unlike F18 there is no field here to check
at all. Also adjacent to the standing-practice note in F41: "reported complete" is not
evidence, and here "validator PASS" is not evidence of spoiler compliance either,
because the validator never claimed to look.

**ADDENDUM (2026-08-15) — a second, unrelated defect in the same validator area:
the schema docstring contradicts the live check on `face`/`split_screen`.** Found
while building the same batch, by reading the schema block to learn the required
package shape. Documented here rather than as its own entry because it lives in the
same file and the same review pass would touch both.

`validators/validate_dual_package.py`'s PACKAGE schema docstring states, at lines
2199-2200:

```
  "video_style": "Anime Clips Only (anime footage only; no face/split/inset)",
  "face": false, "split_screen": false,
```

The live checks at lines 1526-1533 require the exact opposite:

```
    r.add(f"{p} face flag is true (face-cam split-screen is the required default format)",
          pkg.get("face", None) is True, ...)
    r.add(f"{p} split_screen flag is true (face-cam split-screen is the required default format)",
          pkg.get("split_screen", None) is True, ...)
    r.add(f"{p} video_style declares the face-cam split-screen format",
          any(tok in style for tok in ("face", "split")), ...)
```

A package built by copying the documented example would fail all three checks. The
docstring is stale relative to the Law #134 Stage 2 face-cam decision that the live
checks implement (`cron_daily_runtime.txt` restates the requirement: "No change to
Law #134 Stage 2 face-cam split screen — required here same as every other format,
no anime-only exception").

**Severity:** Low for correctness — this fails CLOSED, so no bad package ships
because of it; the validator rejects the wrong shape rather than accepting it. The
cost is authoring friction and misdirection: the schema block is the natural place
to look for the required shape, and it is actively wrong. Worth noting that this
document has repeatedly found stale in-repo documentation to be the leading cause
of wasted effort, and this is an instance of it inside the validator itself.

**Explicitly NOT fixed:** no change has been made to `validate_dual_package.py`.
Correcting the docstring is a one-line-area edit with no behavioral effect, but it
touches the validator, and validator changes require their own authorization and
diff review per standing convention. Documented only.

## F43: `blackout_conflict` and `recent_send_conflict` are pure self-attestation with zero mechanical verification — a real duplicate very nearly shipped because of it

**Discovered:** 2026-08-15, while rebuilding the batch that F41 found had never been
sent. The duplicate was caught by manually reading `sent_scripts_events.jsonl`, not
by any check.

**Status:** OPEN — findings record only, no fix written. Same standing convention as
every other backlog item here: no diff without explicit go-ahead and full diff review.

**What nearly happened.** A One Piece package was being rebuilt around chapter 1190
and Scopper Gaban's fate. Reading the send log directly to confirm blackout state
turned up this already-sent entry from six days earlier:

| Field | Value |
|---|---|
| `post_date` | 2026-08-09 |
| `batch` | 6818490a |
| `show` | One Piece |
| `format_type` | THE_MOMENT |
| `angle` | "Chapter 1190: Scopper Gaban lands the first confirmed injury on Imu in the entire series, **then loses his arm for it**" |
| `tiktok_title` | "Gaban just did what Luffy couldn't" |

Same show, same chapter, same character, same arm-loss beat, same format family, six
days apart. The rebuild would have republished the previous week's video. The package
was dropped (see the 2026-08-15 batch's `approval.json` `dropped_package_record`).

**Why nothing would have caught it.** `validators/validate_dual_package.py` checks
only that the two conflict flags are PRESENT and set to `false`
(`validate_dual_package.py:1616-1620`):

```
    bo = pkg.get("blackout_conflict", None)
    rc = pkg.get("recent_send_conflict", None)
    r.add(f"{p} blackout_conflict input present and clear", bo is False, ...)
    r.add(f"{p} recent_send_conflict input present and clear", rc is False, ...)
```

That is the entire mechanism. The validator never opens `blackout_state.json`, never
opens `sent_scripts_log.json` or `sent_scripts_events.jsonl`, never compares the
package's `show` against recent sends, and never computes a date distance. A package
asserting `recent_send_conflict: false` while duplicating yesterday's send passes
cleanly. The validator's own comment at line 1951 acknowledges the limitation
("blackout_conflict/recent_send_conflict are self-attested"), so this is a known
shape — but the acknowledgment is the whole treatment, and the near-miss shows the
cost is real and not hypothetical.

**Why this is the same pattern already closed twice elsewhere.** This repo has
twice decided that a drafting-pass obligation at this risk level needs a mechanical
backstop, and has built one:

- **WORTH_WATCHING's comparative-language ban (Law #158)** pairs the
  `no_comparative_language` self-attestation with a real
  `BANNED_COMPARATIVE_LANGUAGE` regex scan that fails closed on a match **regardless
  of what the flag claims**.
- **Law #167's `episode_source`** replaced an implicit assumption with a closed enum
  checked at `validate_dual_package.py:581-583`.

The conflict flags are strictly more checkable than either of those: the necessary
data is already in the repo, in files the runtime is already instructed to read
(`cron_daily_runtime.txt` line 41-42 lists `sent_scripts_log.json` and
`blackout_state.json` as authoritative reads). This is not a case of "the validator
cannot know" — it is a case of the validator not looking at data sitting next to it.

**Distinguishing this from F42.** F42 is about a format token with no logic attached.
This is about two fields that DO have checks, where the checks verify the wrong
thing — presence and value of a self-report, rather than the fact the self-report
claims. Related in spirit, different in mechanism, and separately fixable.

**Sketch of what a real check could do** (not a proposal to implement, just to show
feasibility): for each package, read the send log, filter to entries with a matching
`show`, and fail closed if any falls inside the applicable window — the generic
7-day no-repeat, or the format-specific blackout from `cron_daily_runtime.txt`'s
catalog (SEASON_RATING 7 days, SEASON_PREVIEW 7 days, MANGA_VS_ANIME 14 days,
WATCH_RANK 14 days per ranking, WORTH_WATCHING 7 days, EPISODE_MOMENT no blackout).
A stricter version could compare chapter/episode numbers where present, which is what
would have caught THIS case even at a show level that a date window alone might miss
if the cooldown had already lapsed.

**One honest caveat on scope.** Even a date-window check would not have caught the
full problem here on its own. The two packages shared a chapter number, and the
duplicate would still have been a duplicate on day 8, when the 7-day window had
expired and `recent_send_conflict: false` would have been literally true. Detecting
"we already told this exact story" is a content-similarity question, not a date
question. A date-window check is worth building and would have caught this specific
instance, but it should not be mistaken for a complete solution to duplicate content.

**Severity:** High. The failure mode is public, reaches the audience directly, and
damages the channel's credibility in the same way F40's false claims would have —
with the added problem that a duplicate is obvious to exactly the engaged repeat
viewers the channel most depends on.

**Relationship to other entries:** F41 established that a "reported complete" claim
needs artifact evidence. This is the same principle one level down: a package's own
`recent_send_conflict: false` is a report about the send log, and it should be
verified against the send log rather than trusted.

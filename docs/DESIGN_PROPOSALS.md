# Design Proposals — AnimeWithSebastian

Tracks proposed process/validator/law-enforcement designs that are not bugs and have
no incident behind them — distinct from docs/KNOWN_ISSUES.md (bugs/gaps in existing,
supposedly-working systems) and docs/EXPERIMENTS.md (bounded content-pattern tests
with a defined cap and tracked outcome). An entry here is something not yet built,
explicitly deferred to its own future review round before any code is written — same
treatment Law #73's mechanical enforcement (Updates 4/5) got before it existed:
principle first, design proposal second, code only after a dedicated approval round.

---

## DP1: Mechanical enforcement for Law #155 (Independent Second-Party Verification)

**Status:** PROPOSED, NOT IMPLEMENTED — awaiting its own dedicated review round,
same as Law #73 Update 4/5 originally did before being built out. No code written.

**Why this exists:** Law #155 (added 2026-07-28) states its principle — mandatory
second-party verification, the "where else" sweep, the named banned shortcut
(verification by title/description/URL alone) — with zero mechanical enforcement.
It works only when actively invoked. This entry proposes what enforcement could look
like, without committing to build it tonight.

**2026-07-30 update:** This entry is now grounded in real, tonight-specific
incidents — not the single Fern/Aura example alone. That includes a self-caught
false-verification claim (the assistant itself asserting "confirmed via direct git
log search" with no real command behind it, then catching and reversing that on
re-check), which is direct evidence of exactly the failure mode Part 1 below exists
to close. It is also worth noting explicitly: the "where else" sweep already fired
successfully a second time tonight — independent of this proposal existing in any
enforced form yet — when the Berserk World Tree correction's own sweep step caught
a second live instance of the same wrong claim in `clip_descriptions`, fixed in the
same round (commit `3f93e80`). Tonight is now two real, separate confirmations that
the trigger in Part 2 is not hypothetical.

### 1. Validator-level check for "was this independently re-verified"

Add an optional-but-checked object to the manifest schema, e.g.
`independent_verification`, structured per artifact (script/law/fixture change)
rather than per-claim, since Law #155 operates at the change level, not the claim
level (that's already Law #58/#73's job):

```json
"independent_verification": {
  "performed": true,
  "method": "git_pickaxe_search",
  "method_detail": "git log --all --oneline -S \"STEP 4.5 point 9\" -- cron_daily_runtime.txt",
  "artifacts_checked": ["cron_daily_runtime.txt"],
  "sources_refetched": ["commit 1e6b7c2, live file line 555 re-grepped after merge-base ancestor check"],
  "where_else_swept": true,
  "where_else_scope": "n/a for this check",
  "where_else_findings": [],
  "banned_shortcut_check": "confirmed: not resolved by re-reading a prior claim about the commit -- resolved by re-running the exact-string search live against current HEAD"
}
```

Modeled on `claim_vs_source_check` (Law #73): the validator would fail closed if
`performed:true` but `sources_refetched` is empty — a self-attestation without any
evidence of the actual re-fetch, the same pattern Law #73 uses requiring a
`verification_source_url` alongside `scene_verified:true`. It cannot verify the
refetch *actually happened* — no mechanism can prove that — but it can require the
schema to *name* what was refetched, forcing an artifact trail instead of a bare
boolean.

**`method_detail` (2026-07-30 addition):** the field above is not new in kind, but
is now specified more precisely: it must contain the literal command run, the exact
search string used, or the specific transcript excerpt checked — not a category
label like `"method": "git_pickaxe_search"` alone. This distinction is what
separated two real incidents in the same conversation tonight:

- **REJECT** — an assertion that "the STEP 4.5 point 9 AI-slop check does not exist
  in the real repo — confirmed via direct git log search" was stated as fact with
  no `method_detail` ever produced: no command shown, no output pasted. A restated
  conclusion, not a checkable trail. This was the assistant's own error, caught only
  because a live re-check was insisted upon before proceeding.
- **ACCEPT** — the correction to the above: before proceeding on that claim, a live
  re-verification was run and shown in full — `git log --all --oneline -S "STEP 4.5
  point 9" -- cron_daily_runtime.txt` returning commit `1e6b7c2`; `git merge-base
  --is-ancestor 1e6b7c2 HEAD` confirming it's a real ancestor of current HEAD, not an
  abandoned branch; a direct `grep`/`sed` of the live file at line 555 showing the
  content present verbatim. Each step names its exact command and exact result — a
  second reader can literally re-run all three and get the same three answers.
- **ACCEPT** — the Berserk World Tree claim: rather than trusting two YouTube
  sources' titles/descriptions, the actual transcripts of both videos
  ([Hajime no Raju](https://www.youtube.com/watch?v=7qaZwslFmK8),
  [Anime Balls Deep](https://www.youtube.com/watch?v=CXRurHplECc)) were pulled and
  searched for the specific term "World Tree" and any physical-distance/tether
  language — zero occurrences in either. `method_detail` here reads as a falsifiable,
  re-runnable claim, not "confirmed against sources."
- **ACCEPT** — the Hunter x Hunter 421/430 claim: rather than picking a side between
  two contradicting sources, the check explicitly recorded the contradiction itself
  as the finding — [animefanatika.co.za](https://animefanatika.co.za/bento-news-july-2026-the-ultimate-anime-news-roundup/)
  and [respawn.outlookindia.com](https://respawn.outlookindia.com/pop-culture/pop-culture-news/hunter-x-hunter-volume-39-set-for-july-release-after-22-month-gap)
  both confirm "well past ch.420, backlog of 20+ chapters" but diverge on the
  specific 421-vs-430 stage split, and no attempt was made to resolve that
  divergence by picking one source over the other. This is the accept case for
  **honest non-resolution** — the object records a genuine limit found, not a
  manufactured single answer.

### 2. Operationalizing the "where else" sweep (Part 2)

Two bounded options:

- **Option A (log-only, cheap):** require `where_else_scope` (what was searched) and
  `where_else_findings` (empty array is a valid, honest answer) whenever any
  error-correction commit touches a fixture/law/script. Enforceable via a commit-
  message-linked checklist item requiring this field be non-null on any commit
  tagged as a "fix." Cannot confirm the sweep was thorough — only that one was
  declared with a stated scope. Same self-attestation ceiling as every other M6
  field.

  **2026-07-30 promotion:** given tonight is now a second real incident confirming
  this trigger fires in practice (see below), `where_else_swept` and
  `where_else_scope` are proposed to move from optional-if-present to
  **hard-required on any commit explicitly tagged as a correction/fix** — not
  merely encouraged. One incident could be treated as a one-off; two independent
  real firings of the same trigger in one session is enough to justify promoting it.

- **Option B (semi-mechanical, narrower):** for a specific, narrow class of errors —
  wrong factual claims about named entities (like the Fern/Aura case) — a script
  could grep the repo for the exact wrong string post-fix and fail the validator on
  a nonzero count. Only works for exact-string errors, not paraphrased or conceptual
  ones — a narrow net, not a general "where else" mechanism. This is the one part of
  Law #155 that is actually mechanically checkable in a meaningful way (unlike
  Part 1, which fundamentally cannot be proven) — recommended starting point if any
  teeth are wanted soon, with Option A's schema running alongside it.

**Worked examples for the trigger itself, now two incidents deep:**

- **Fern/Aura** (why this must be mandatory, not optional): a single wrong belief —
  that Fern fights Aura in Frieren — was found independently copied into the
  Frieren fixture's `claimed_beat`, `scene`, `claim_vs_source_check.
  source_content_confirmed`, and `clip_locate` fields across all 5 clips, only fully
  surfaced because "where else does this appear?" was asked explicitly after the
  first instance was caught via an unrelated `clip_locate` cross-check. Nothing
  about finding the first instance would have surfaced the other three without the
  explicit sweep step.
- **Tonight's HxH/Berserk correction round** (the sweep firing a second time,
  independently, with no enforcement mechanism yet in place): after correcting the
  World Tree claim in the Berserk VO, the same "where else" step was applied by
  habit, not by any validator requirement — and found one more live instance of the
  same wrong claim in the `clip_descriptions` field, fixed in the same round
  (commit `3f93e80`). This happened before any part of this proposal was built or
  enforced — proof the underlying discipline works when applied, and exactly the
  gap this proposal is trying to make structural rather than incidental.

### 3. Honest enforcement ceiling — stated plainly

Any mechanism proposed here CAN enforce:
- That an `independent_verification` object exists and is structurally non-empty
  (schema presence — same ceiling as every other self-attestation field tonight).
- That it names specific files/URLs claimed to have been re-fetched, and — per the
  `method_detail` addition — the literal command, search string, or transcript
  excerpt used (a step up from a bare boolean, since it forces an artifact trail).
- For Option B's narrow exact-string case only: that the specific known-wrong string
  no longer appears elsewhere in the repo.

It CANNOT enforce:
- That the second pass was performed by an actually separate context/session —
  nothing distinguishes "I opened a new context" from "I wrote this object in the
  same continuous pass and called it independent." Tonight's own turn-496 incident
  is direct proof of this ceiling in practice: a fluent, confident, wrong claim of
  verification ("confirmed via direct git log search") was produced with no real
  command behind it, by the same assistant this proposal would apply to.
- That the refetch happened at all versus being fabricated — the same limitation
  `claim_vs_source_check` already has for Law #73/#58: a URL, or now a
  `method_detail` string, can be written without confirming the underlying command
  was really run.
- That the second pass's conclusion was itself correct — a second pass can
  independently re-check something and still be wrong.
- That a "where else" sweep's stated scope was actually broad enough — a sweep can
  honestly report "none found" while missing a rephrased instance of the same
  error, exactly as Law #155's own Part 4 already states.

This is a real form-vs-substance ceiling, identical in kind to every other M6 field
in this repo: structure and presence are checkable; genuine independence and
correctness are not. No softening: this raises the cost of asserting an unearned
"verified," it does not make a false "verified" impossible.

### 4. Validator implications (new section, 2026-07-30)

**Recommendation: presence/shape-only schema fields (M6 pattern) for the
verification object itself; a genuine mechanical check only for the narrow
"where else" exact-string case — not deeper validation across the board.**

Reasoning:
- `independent_verification.method_detail` cannot be mechanically checked for
  truthfulness by any script — a validator can confirm the string is non-empty,
  but confirming a pasted git command was *actually run* requires re-running it,
  which is a runtime/process discipline, not a schema check. This mirrors
  `claim_vs_source_check`'s own existing ceiling exactly.
- The one piece that IS mechanically meaningful, per Option B above: a **post-fix
  grep for the known-wrong exact string**, run by the validator itself, failing
  closed on a nonzero match count. This is narrow (exact strings only, not
  paraphrases) but it is the one part of this whole proposal that doesn't rely on
  trusting a self-attestation — a script can independently re-derive "0 matches" or
  "3 matches" itself, the same way tonight's `clip_descriptions` echo could have
  been caught mechanically instead of by habit.
- Given that, the concrete validator change worth scoping (not building tonight) is
  narrow: extend `validators/validate_dual_package.py` with an optional
  `where_else_check: {banned_strings: [...], swept_paths: [...]}` field that the
  validator itself greps for post-fix, alongside — not replacing — the
  presence-only `independent_verification`/`where_else_swept` self-attestation
  fields. Everything else in this proposal stays a process/runtime instruction,
  same as Law #155's own text today.

**Recommended path, not yet approved:** ship Option A's schema fields (now
including `method_detail` and the promoted hard-required `where_else_swept`/
`where_else_scope`) if any teeth are wanted soon, hold Option B and the narrow
validator `where_else_check` grep for a dedicated review round given its scope —
mirroring Law #73's own evolution (principle first 2026-06-14, mechanical teeth
added later only in Updates 4/5 once the pattern was proven). No implementation
timeline is set by this entry; it exists so the proposal is not lost, not to
schedule its build.

**Next step:** none scheduled. This entry stays PROPOSED until a future session
explicitly opens a review round for it, the same way Law #73 Update 4/5 got its own
dedicated round rather than being folded into an unrelated night's work.

## Conditional CTA requirement for Law #156 ism-based endings (2026-07-30)

**Context:** Law #156 (added 2026-07-29) codifies four structural voice patterns
("isms" — Structural Reveal, Lore Justification, Hidden Gem Curator, Ancestry) as
an alternate ending shape a script can use INSTEAD OF the standard question + "Leave
your take." closer. This was confirmed as intentional during tonight's closer
rewrite work: the Hunter x Hunter script's first draft used a pure Structural Reveal
closer with no question and no CTA phrase at all, by design.

**The real conflict, found by running the actual validator, not assumed:**
`validators/validate_dual_package.py` currently hard-requires, for every package
with no exception:
  - `[PASS/FAIL] question_line is a question`
  - `[PASS/FAIL] question immediately followed by 'Leave your take.' in VO`
  - `[PASS/FAIL] exact CTA phrase present in VO`

When the Hunter x Hunter package was drafted with a pure ism-based closer (no
question, no "Leave your take."), the validator produced two real, live FAILs
tonight:
  - `[FAIL] [morning] question immediately followed by 'Leave your take.' in VO`
  - `[FAIL] [morning] exact CTA phrase present in VO`

This is a genuine schema gap, not a bug in the ism concept or in Law #156's text:
the validator was written before Law #156 existed and has no field or branch that
recognizes an ism-based ending as a valid alternative to the question+CTA shape.

**What was done tonight instead (not a fix, a scoped workaround):** the Hunter x
Hunter package was reverted to a question-format closer for tonight's actual send
so it would validate clean under the CURRENT validator as written. The ism-based
closer that was drafted and reviewed is real, approved conceptually, and already
demonstrated in a rejected test run — but it could not ship tonight because no
schema currently allows a CTA-free package to pass.

**Proposed direction, not yet built or approved:**
- Add an optional `ism` field to the PACKAGE schema (e.g.
  `"ism": {"name": "structural_reveal|lore_justification|hidden_gem_curator|ancestry",
  "source_video_id": "...", "source_line_excluded_reason": "..." }` — the last
  field only needed if a real source line had to be excluded, as happened with
  `nqDfM07WexQ`'s point-9(f) line during this same session).
- When `ism` is present and non-null: the CTA-related checks
  (`question_line is a question`, `question immediately followed by CTA`, `exact CTA
  phrase present`) become CONDITIONAL — skipped or replaced with an ism-specific
  check instead (e.g. confirm the closer sentence still contains a genuine
  structural claim, not just any non-question ending).
- When `ism` is absent or null: all existing CTA checks remain mandatory exactly as
  they are today. This is a strictly additive schema change — no existing package
  or check changes behavior unless a package opts into an ism-based ending.

**Honest enforcement ceiling, stated plainly (same standard as every other
self-attestation field in this repo):** any mechanical check here can confirm the
`ism` field is present, structurally well-formed, and names one of the four Law
#156 patterns. It CANNOT confirm the closer sentence genuinely executes that
specific structural move rather than just being non-question prose that claims the
label — that judgment call remains a human-editor spot-check, same ceiling as
`hook_family`, `topic_class`, and every other self-attested field already in this
schema.

**Recommended path, not yet approved:** this needs its own dedicated design pass —
exact field schema, which of the CTA checks become conditional vs. replaced, and
whether an ism-specific replacement check is worth building now or left as a
schema-presence-only gate initially (mirroring how Law #73's mechanical teeth were
added in a later, separate update round rather than all at once). Not fixed
tonight — this is a real, deliberate deferral so a genuinely new ending shape isn't
rushed into validator logic under time pressure.

**Next step:** none scheduled. This entry stays PROPOSED until a future session
explicitly opens a review round for it, the same pattern as the entry directly
above this one.

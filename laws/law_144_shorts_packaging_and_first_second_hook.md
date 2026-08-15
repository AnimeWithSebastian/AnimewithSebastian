# Law #144 — Shorts Packaging & First-Second Hook (added July 17, 2026)

**Status:** ACTIVE. User-approved. Governs the packaging of every 30s Short. Does not
relax any existing creative law (VO 100-108 words, exact "Leave your take.", 30s
per-cut timings #140, seamless loop #141, face-cam split-screen layout #134 Stage 2
(2026-08-09, superseding the earlier anime-only rule) all still apply).

## Evidence base (both must agree)
- **Channel analytics:** clean titles (no hashtags) outperformed hashtagged ones
  (1,739 vs 1,447 avg views on this channel's Shorts); "stayed to watch" is the
  swipe-decision gate (winners 60-72%, weak <40%).
- **Official/benchmark research:** YouTube's own guidance says **metadata *tags* are a
  minor/negligible reach lever** and search ranks on title/description/content match;
  relative watch time + replays dominate Shorts, so the hook must land in the first
  second; deceptive / clickbait packaging is explicitly discouraged.

## Evidence grade / correction
- **Distinguish the two hashtag findings — they are NOT the same source.** The
  "no hashtags in the title wins" rule (rule 2) rests on **this channel's own cohort
  data** (1,739 vs 1,447). YouTube's official guidance is about *metadata tags*, not
  specifically title hashtags; do not cite the official doc as proof that title hashtags
  hurt. The enforced no-title-hashtag rule is grounded in the channel cohort; the
  official guidance only corroborates that tags/hashtags are not a growth lever.
- **`hook_first_second` is a model attestation, not a verified fact (M6).** The validator
  checks the flag is present/true and that `hook_line == opening_sentence`; it cannot
  verify the hook actually lands within second 1 on screen and in the VO. Treat it as a
  self-report subject to weekly human spot-check, never as machine-verified.

## Rules (per package; deterministic, fail-closed)
1. **First-second hook.** The assumption being broken must be present in the first
   second both **on screen** and **spoken**:
   - `hook_onscreen_text` — the on-screen assumption-break shown immediately (nonempty).
   - `hook_first_second` = true — **model attestation** that VO hook + on-screen text land
     in the first second. The validator enforces presence/truth only; the *semantic* claim
     is a self-report the weekly cron spot-checks (M6), not a machine-verified fact.
   - `hook_line` must equal `opening_sentence` (the break is the VO's first sentence).
2. **Punchy, searchable platform titles (revised July 2026 — production feedback).**
   Titles were running too long; YouTube performance feedback wants punchier titles
   that stand out. Each package now carries TWO distinct short title fields:
   - `youtube_title` — **hard maximum 60 characters** (incl. spaces); **preferred target
     35–50**.
   - `tiktok_title` — a DISTINCT field, **hard maximum 55 characters** (incl. spaces);
     **preferred target 30–45**. This is the short on-platform title, NOT the
     `tiktok_post_text` caption (see Notes).
   - **ONE punchy idea / curiosity gap only.** No explanatory subtitle, no stacked
     clauses, and no title that summarizes the entire argument. The old
     `[Show]: [full explanatory sentence, extra clause]` shape is retired for Shorts.
   - **No hashtags** (`#`) in EITHER title.
   - The show/anime **search keyword appears early** in the `youtube_title` (within the
     first 40 chars) where natural — but **punchiness wins over awkward keyword
     stuffing**. `tiktok_title` optimizes for punch, not keyword placement.
   - Titles must be **distinct** from the published hook line and from each other
     (`youtube_title` ≠ `tiktok_title` within a package; and each title distinct across
     the two same-day packages).
   - Titles must accurately represent content — no deceptive/clickbait overpromising
     (creative-law judgment; the mechanical checks above are the enforced floor).
   - **Enforced deterministically (fail-closed):** the hard char caps, no-hashtags on
     both titles, `tiktok_title` presence, title ≠ hook, and cross-package distinctness.
     The preferred target bands and the "one idea / no subtitle" rule are guidance the
     model applies (the hard caps make long subtitles structurally impossible); the
     weekly human spot-check verifies punch/quality.
3. **Hook family for attribution.** `hook_family` (e.g. question / revelation /
   contradiction / observation) is recorded per package so the weekly analytics cron
   can attribute performance by hook family (Law #145).
4. **The Isolation Test (added August 5, 2026, self-audit judgment call — not
   validator-enforced).** Before finalizing `hook_onscreen_text` and `hook_line`,
   isolate them from the rest of the VO and ask: does a reasonable viewer, seeing
   ONLY the on-screen text and the spoken first line — nothing else — walk away with
   an accurate understanding of what was actually confirmed or happened?

   This is necessary because most Shorts viewers decide whether to keep watching
   within the first 1-2 seconds, before any disambiguation later in the VO can land.
   A hook can be technically defensible by the end of a fully-watched VO while still
   being misleading to the (majority of) viewers who only see the first second.

   **FAIL condition:** the hook implies something stronger, different, or more
   definitive than what the full VO ultimately delivers — even if a later sentence
   explicitly corrects or caveats it. A correction arriving after the misleading
   impression has already landed does not cure the isolation-test failure.

   **Worked example (real, caught instance, August 5, 2026):** the draft hook
   "Jujutsu Kaisen Season 4's Date Just Got Real" implies a release date has been
   confirmed. Read in isolation, that is the only reasonable takeaway. The actual
   content is a convention/event date (Juju Fest, Aug 29-30) where Season 4 news is
   expected — and the VO explicitly states "No release date yet" five sentences
   later. The correction exists, but arrives too late to prevent the initial
   misleading impression a 1-2 second viewer would form. This hook FAILS the
   isolation test and was rewritten to lead with the actual confirmed thing (the
   event) rather than a word ("date") that carries a different dominant meaning.

   **Second worked example (real, caught instance, August 6, 2026):** the sent
   hook "This 'easy' battle wasn't the real fight" (Tanya S2 Ep4) implies a
   bigger, harder combat confrontation is coming — "the real fight." Read in
   isolation, that is the only reasonable takeaway from the word "fight." The
   actual content is a political rejection of a peace deal by profit-driven
   leadership — no second battle occurs. This hook FAILED the isolation test and
   was rewritten to lead with the actual confirmed contrast ("They won the war.
   Then they voted against peace.") rather than a word ("fight") that carries a
   different dominant meaning.

   **The general pattern, confirmed by two independent instances across two
   unrelated shows:** both failures share the same underlying shape — a single
   word in the hook ("date" in the JJK case, "fight" in the Tanya case) carries a
   common, dominant meaning to a viewer seeing it in isolation, while the actual
   content resolves to something adjacent but materially different (an event, not
   a confirmed date; a political vote, not a battle). This is not a rule about
   dates, or about combat language specifically — it is a rule about any word
   whose most natural reading promises something the content doesn't deliver.
   When drafting a hook, ask what the SINGLE MOST LIKELY reading of its key
   word/phrase is to someone with zero other context, and check that reading —
   not just a defensible reading — against what the VO actually delivers.

   **Enforcement:** like the AI-slop pattern check (STEP 4.5 point 9 in
   `cron_daily_runtime.txt`) and Law #149 point 2, this is a mandatory explicit
   self-audit question during drafting, not a mechanically validated field. Record
   the pass/fail judgment honestly; if FAIL, rewrite the hook/title before returning
   the manifest — do not attest a pass with a known instance present. The
   deterministic validator cannot check this (same honest limitation as every other
   judgment-based check in this law set); it is caught at drafting time and
   spot-checked weekly by the human reviewer, same treatment as `hook_first_second`
   and the AI-slop checks.

5. **Load-bearing vs. supporting-cast identity (added August 6, 2026, self-audit
   judgment call — not validator-enforced).** Not every name requires identifying
   context — whether it does depends on whether the video's core claim is
   unfollowable without it, not on general viewer familiarity. Applies to any
   named character mentioned in a VO body, not limited to `hook_line`/
   `hook_onscreen_text` (unlike rules 1-4 of this law).

   **Load-bearing identity** (always clarify, regardless of audience familiarity):
   a name whose relationship to the hook/core claim is REQUIRED for the story to
   make sense at all — e.g., whether a named person IS the person the hook
   referred to. Real example: Kagurabachi's Kunishige required "Chihiro's dad"
   because the entire video's premise depended on that identity link (August 6,
   2026 correction).

   **Supporting-cast mention** (creator's judgment call, not a hard rule): a name
   that adds color or specificity to a fact-drop but isn't required for the core
   claim to be understood — clarifying it or not is the creator's call based on
   their own read of audience anime-literacy, and self-audits must NOT flag either
   choice as an error. Real example: Gachiakuta's "Enjin" in a new-footage
   fact-drop (August 6, 2026) is supporting-cast, not load-bearing — leaving it
   unclarified is not a defect.

   **Distinct from Law #133** (General Audience Language Standard): Law #133
   governs anime-industry/fan-culture jargon (terms like "cour," "sakuga,"
   "seiyuu") requiring a fixed define-or-replace remedy tied to vocabulary
   comprehension. This rule governs character names within the show itself being
   covered, where the remedy is a judgment call tied to narrative dependency, not
   vocabulary comprehension. The two are checked independently and neither
   supersedes the other.

   **Enforcement:** like rule 4 and the AI-slop pattern check, this is a mandatory
   explicit self-audit question during drafting, not a mechanically validated
   field. Record the judgment honestly; the deterministic validator cannot check
   this; it is caught at drafting time and spot-checked weekly by the human
   reviewer.

6. **Zero-verified-clips title gate (added August 6, 2026, self-audit judgment
   call — not validator-enforced, but tied to a mechanical finding from Law
   #73 UPDATE 7).** If a package's `video_level_claim_check` (Law #73 UPDATE 7)
   shows zero clips verified against the specific new/unaired content the
   title claims to show (all clips are honest stand-ins once correctly
   classified under UPDATE 7), the `youtube_title`/`hook_line` must not use
   words that promise a "breakdown," "footage," or "look" at that new content
   — this is the same isolation-test failure shape as this law's existing
   worked examples: a word in the hook carries a dominant meaning ("you are
   about to see this specific new thing") that the video does not deliver.
   Reframe the hook/title around what IS actually delivered — e.g. a recap
   building toward confirmed news — rather than the unaired content itself.

   **Real example** (August 6, 2026): Gachiakuta package
   `88dff475-d267-46d1-946f-f65bdaf5c785`, corrected live on YouTube (video ID
   `OiVOi2wjVcI`) from "Gachiakuta Season 2: First Footage Breakdown" to
   "Gachiakuta Season 2: What We Actually Know" — read back and confirmed via
   the YouTube Data API the same night.

   **Enforcement:** like rules 4 and 5, this is a mandatory explicit
   self-audit question during drafting, not a mechanically validated field,
   though it is triggered by UPDATE 7's `video_level_claim_check` counts where
   that field is present. Record the judgment honestly; spot-checked weekly by
   the human reviewer, same treatment as the rest of this law.

## Notes
- **`tiktok_title` vs `tiktok_post_text`.** `tiktok_title` is the short, punchy,
  no-hashtag on-platform title (≤55 chars). The separate `tiktok_post_text` caption may
  still be **longer** and carry its platform-native **hashtag pyramid** — the no-hashtag
  and length rules are enforced against the `tiktok_title` FIELD, never the caption. Do
  NOT truncate the full caption to fake a title; populate the distinct `tiktok_title`.
- The no-hashtag-in-title rule (both platforms) rests on this channel's own cohort data
  (clean titles outperformed) with official guidance corroborating that tags/hashtags are
  not a reach lever.
- No unverifiable performance claims are asserted; these are packaging hygiene rules
  grounded in the two evidence files and YouTube's own guidance.

## Cross-references
- Loop/timing (unchanged): Law #140, #141. Anime-only: Law #134.
- Topic portfolio/series: Law #143. Measurement/experiment: Law #145.

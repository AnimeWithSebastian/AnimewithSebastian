# LAW #62 — CUT 7 CLOSER LAW
**System:** AnimeWithSebastian — v5.1
**Added:** June 2026
**Status:** ACTIVE (narrowed — see SUPERSESSION NOTE below)

---

## SUPERSESSION NOTE (added July 24, 2026 — policy decision)

The **question-closer rule only** — the standalone "ending with a question is
banned" structural rule (the "QUESTION CLOSERS ARE BANNED" section below, and
ENFORCEMENT check #3 "Does it end with a question? → HARD STOP") — is **superseded
for Shorts closers** by the current CTA law (Law #139 / `cron_daily_runtime.txt`):
the VO body ends with a specific question immediately followed by the exact phrase
"Leave your take." That structure necessarily ends the VO on a question, so the flat
ban cannot coexist with it. Where the two conflict, the current CTA law governs.

This narrowing is **scoped to the question-vs-declarative-statement structural rule
only**. Law #62's other two violation types are **UNCHANGED and remain in FULL
force**:
- the **implication closer** (e.g. "so yeah... he's been through it") is still banned;
- the **vague-feeling closer** (a general sentiment with no specific claim) is still
  banned.

In practice under the current CTA law, the specific question itself must still state
a real, singular claim/stance (not a vague sentiment) before the "Leave your take."
handoff — the question closer is no longer HARD-STOPPED for being a question, but it
is still HARD-STOPPED if it is vague or implicational rather than a specific, single-
reading claim framed as a question. Nothing else about Law #62 is weakened.

---

## THE LAW

The final line of the VO must state the argument's conclusion directly.

Not an implication. Not a question. Not a vague feeling. A direct statement.

---

## WHAT TRIGGERED THIS LAW

A viewer commented on a published video asking "are you saying X?" after the final cut.

The VO had made an argument across 6–7 cuts. The final line did not close it. It drifted — a vague impression of a conclusion without actually saying the thing.

The viewer was left doing the math. That is a failure of the closer.

---

## THE CORE RULE

**CUT 7 (or whichever cut is last) must state what you are saying.**

The viewer should never finish a video and have to ask: "what was the point?"

If they could reply "are you saying X?" after your final line → the closer failed. Rewrite it.

---

## THE TEST

After writing the final line, apply this test:

**"Could a viewer reply 'are you saying X?' after this line?"**

- If YES → the line is an implication, not a conclusion. Rewrite.
- If NO → the line states the point. Pass.

---

## HARD EXAMPLES

### VIOLATION (implication)
> "So yeah... Guts has been through it."

The viewer asks: "Are you saying he's the best written character? Are you saying the suffering is the point? Are you saying he's stronger than people think?"

Too many possible readings. The closer failed.

### FIXED
> "Guts doesn't have a happy ending coming — and the manga earned that. Every scar he's carrying has a chapter behind it."

One conclusion. No ambiguity. Pass.

---

### VIOLATION (vague feeling)
> "Mob Psycho kind of does something different with power that most shows don't."

Viewer asks: "Are you saying it's better than other shows? Are you saying power isn't the point? Are you saying Mob is underrated?"

Failure. Too vague.

### FIXED
> "Mob Psycho never lets the powers be the reason Mob matters. That's why it hits different from every other psychic anime."

Direct conclusion. No follow-up question needed. Pass.

---

### VIOLATION (question closer)
> "So is Itadori Yuji the most tragic character in JJK?"

This is a question. The viewer is left without an answer. Banned.

### FIXED
> "Itadori gets no breaks, no clean victories, and no one to blame. That's not a redemption arc. That's just loss."

States the conclusion. Pass.

---

## QUESTION CLOSERS ARE BANNED [SUPERSEDED for Shorts — see SUPERSESSION NOTE at top]

*As originally written, this section banned ending the VO with a question. It is
superseded for Shorts closers by the current CTA law (Law #139), which ends the VO
body on a specific question immediately followed by "Leave your take." Kept below
for historical record only — do not enforce this section as written.*

Ending the VO with a question directed at the viewer is banned as a closer.

Engagement questions ("drop your answer below") belong in on-screen text or at the end of a CTA, not in the VO itself as the conclusion.

The VO closer must state something. It cannot ask something.

---

## FORMAT NOTES

Not every VO has 7 cuts. Some have 5. Some have 4. The law applies to the final cut regardless of cut count.

"CUT 7" is the name of this law, but it governs whatever cut is last.

---

## ENFORCEMENT

**Pre-send check (Law #58):** Before any VO is sent, it is reviewed against Law #62.

Reviewer reads the final line only and applies the test:
1. Does it state a conclusion? → PASS
2. Does it imply a conclusion without stating it? → HARD STOP
3. [SUPERSEDED for Shorts — see SUPERSESSION NOTE] Does it end with a question? → no
   longer a HARD STOP on its own; the current CTA law (Law #139) requires the VO
   body to end on a specific question immediately followed by "Leave your take."
   Instead check: is the question a specific, single-reading claim/stance (not vague,
   not merely implicational)? If NO → HARD STOP under check #2 or #4 below.
4. Is it a vague feeling or general sentiment with no specific claim? → HARD STOP

If the final line fails → rewrite the closer. Do not adjust the full VO. Just the final line.

Then re-apply the test. Repeat until pass.

---

## Final-5-Seconds Placement Addendum (added 2026-07-27)

YouTube's own current guidance names a final-5-seconds on-screen CTA as one of
three concrete tactics for converting Shorts-only viewers (blog.youtube, July 14,
2026 -- cited in the 2026-07-27 research report). This is a placement rule, not a
rewrite of the CTA content rule above: the VO-level closer (specific question
immediately followed by the exact phrase "Leave your take.") is unchanged.

A manifest must now also set `onscreen_cta_start_sec` (numeric), naming the second
at which the on-screen CTA visual appears. UPDATED Stage 2 (2026-08-09): the
validator now requires `onscreen_cta_start_sec >= target_sec - max(5.0, target_sec * 0.15)`,
where `target_sec` is the resolved edit length -- now open-ended across [20,180]s
for every package (the old 30s default / sanctioned 45-59s duration_experiment
split no longer exists; see Law #140 and the retired M1 gate). The formula
reproduces the original 5-second floor exactly at 30s (floor=25.0s) while scaling
to 15% of the edit for longer lengths, so the CTA always lands within the edit's
closing window rather than a fixed final-5-seconds band.
This rule is enforced fail-closed: a package missing the field, or placing the CTA
earlier than that closing window, does not pass validation.

---

## RELATED LAWS
- Law #58 — Pre-Send Verification (enforces this check)
- Law #59 — VO Length / No Essay Rule (Clean Conclusion from essay structure is banned — this law governs what the actual closer must do)
- Law #60 — Dangling Claims (the closer is also a claim — it must not dangle)
- Law #139 — Combined Daily Dual-Package Workflow (current CTA law — supersedes this
  law's question-closer rule specifically; see SUPERSESSION NOTE at top)

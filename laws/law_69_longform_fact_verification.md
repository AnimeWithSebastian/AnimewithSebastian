# LAW #69 — LONG-FORM FACT VERIFICATION
**System:** AnimeWithSebastian — v5.2
**Added:** June 2026
**Status:** ACTIVE
**Source:** Law #58 (Shorts Pre-Send Verification) adapted for long-form
**Applies to:** All long-form videos ~~(5–8 minutes)~~ — see the length note below.
This law's FACT-VERIFICATION rules are unaffected by length and still apply in full.

> **LENGTH FIGURE SUPERSEDED — note added 2026-08-15 during a law audit. Original
> "(5–8 minutes)" preserved above via strikethrough; nothing else in this law changes.**
>
> "5–8 minutes" is Law #66's original June 2026 target. **Law #146's July 26, 2026
> correction explicitly supersedes it** (and Law #136's 6–12 min figure). Law #146 now
> states: **FLOOR** — the video must simply not be classified as a YouTube Short (a 16:9
> video is long-form at any length, so this channel's flagships satisfy the floor by
> format, not by runtime); **TARGET** — reach 8:00 (480s) where the material genuinely
> supports it, because that is the current threshold for mid-roll ads, explicitly
> "recommended, not mandatory"; **NEVER pad** to reach 8:00 if the material doesn't
> support it. Law #146 also states in terms: *"The old fixed 480-720s (8-12 min) band is
> retired as a mandatory range... No upper bound is reinstated."*
>
> **UNRESOLVED LAW-vs-CODE CONFLICT — do not treat the above as the operative gate.**
> `validators/validate_longform_flagship.py` still hard-enforces the retired band:
> `LONGFORM_MIN_SEC = 480`, `LONGFORM_MAX_SEC = 720`, checked as "duration in the 8-12
> min band". Per this repo's authority order (running validators outrank law text), the
> VALIDATOR governs in practice: a flagship at, say, 6 minutes is explicitly permitted by
> Law #146 but **would fail validation today**. Reconciling the two — relax the validator
> to match Law #146, or reinstate the band in Law #146 to match the validator — is a real
> decision, not a text correction, and is deliberately NOT made here. Flagged for the
> owner. Check the validator before planning any flagship length.
>
> Note this law is length-SENSITIVE in one respect worth stating: a longer video carries
> more claims, so the per-claim verification burden scales with runtime rather than with
> any fixed band. That principle is unchanged by the supersession.

---

## THE LAW

Long-form contains more claims than a Short.
More claims = more chances for one wrong fact to collapse the entire video.

Every specific claim in a long-form video must be verified via live source
before the video is scripted, filmed, or published.

Law #52: NEVER source factual claims from memory. This applies with more
force in long-form — a wrong fact in a 7-minute video sits on screen longer,
reaches more of the audience, and generates more correction comments than a
wrong fact in a 45-second Short.

---

## CLAIM TYPES (same as Law #58, extended for long-form volume)

### TYPE A — GENERAL CHARACTER/SHOW FACT
Example: "Guts uses a sword called the Dragonslayer."
Verification: 1 live search minimum.
These are everywhere in long-form. Do not skip because they seem obvious.
Memory-confirmed ≠ verified.

### TYPE B — CORE CLAIM (COLLAPSE TEST)
The central argument of the video. If this is wrong, the whole video falls apart.
Example: "Berserk's Eclipse arc was the turning point that defined Guts's entire trajectory."
Verification: 2 live searches minimum. Cross-referenced.
Every long-form has exactly one core claim. Find it. Verify it twice.

### TYPE C — YEAR/TIMELINE/NUMBER CLAIM
Example: "Berserk the manga started in 1989."
Verification: 1 live search minimum. These fail silently — a wrong year
in a Short gets 3 comments. A wrong year in a long-form with 1,000 views
gets 40 comments and tanks the credibility of everything else said.

### TYPE D — REAL-WORLD CONNECTION CLAIM
Example: "Kentaro Miura based the Band of the Hawk on medieval European mercenary companies."
Verification: 2 live searches minimum. These are the highest-risk claim type
in long-form because they are the most impressive and the hardest to verify.
If verification fails after 2 searches → REMOVE THE CLAIM. Do not guess.

### TYPE E — COMPARISON CLAIM (long-form only)
Example: "Guts's trauma response is more detailed than any other anime protagonist's."
These appear frequently in long-form arguments and almost never in Shorts.
Verification: Search specifically for counterexamples before making this claim.
If a clear counterexample exists → qualify or remove the claim.
"More detailed than most" is defensible. "More detailed than any" is not.

---

## LONG-FORM FACT BLOCK FORMAT

Every long-form script must include a fact verification block before filming.
Format:

LONG-FORM FACT VERIFICATION BLOCK
Video: [Title]
Core claim (Type B): [claim] — Source: [URL] — Cross-check: [URL]

Supporting claims:
[Claim 1] — Type [A/C/D/E] — Source: [URL]
[Claim 2] — Type [A/C/D/E] — Source: [URL]
[Claim 3] — Type [A/C/D/E] — Source: [URL]
[...]

Any BLOCKED claim (unverified after 2 searches): REMOVED. Replaced with: [replacement or cut]

OVERALL STATUS: PASS — all claims verified
OR: HARD STOP — [claim] blocked, video cannot publish until resolved

---

## THE CORRECTION COMMENT RULE

Long-form videos are watched by more invested fans than Shorts.
Invested fans are more likely to know when a fact is wrong.
A correction comment on a long-form video is more damaging than on a Short
because it sits under a video people are already spending 7 minutes with.

Every correction comment is a failed Law #69 check.
If a long-form video generates a correction comment → identify which claim
failed verification and why. Update the law with the failure case.

---

## AUTO-FAIL CHECK

Before filming or publishing:
[ ] Is the core claim (Type B) verified with 2 live sources?
[ ] Are all Type C (year/number) claims verified?
[ ] Are all Type D (real-world connection) claims verified with 2 sources?
[ ] Are Type E (comparison) claims qualified — not absolute?
[ ] Is the full fact verification block written and attached to the script?
[ ] Are there zero unverified claims remaining?

If any item is NO → do not film. Resolve first.

---

## RELATED LAWS
- Law #52 — Never source from memory (foundational rule this law enforces)
- Law #58 — Pre-Send Verification (Shorts version — same principle)
- Law #60 — Dangling Claims (unverified claims often become dangling claims)
- Law #72 — Long-Form Pre-Publish Checklist (enforcement gate)

# LAW #68 — LONG-FORM COMMENT ENGINEERING
**System:** AnimeWithSebastian — v5.2
**Added:** June 2026
**Status:** ACTIVE
**Source:** Law #55 (Shorts) adapted for long-form format
**Applies to:** All long-form videos ~~(5–8 minutes)~~ — see the length note below.
This law's COMMENT-ENGINEERING rules are unaffected by length and still apply in full.

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
> Length-specific guidance inside THIS law (e.g. "every 2–3 minutes of long-form should
> contain a mid-video comment trigger") should be read proportionally to the video's
> actual runtime, not against the retired 5–8 minute assumption.

---

## THE LAW

Long-form comments are deeper than Short comments.
A viewer who watched 7 minutes has more invested. Their comment is longer,
more specific, and more likely to start a thread.

The same 5 community levers from Law #55 apply — but long-form has additional
tools that Shorts do not have. Use them.

---

## THE 5 COMMUNITY LEVERS (same as Law #55 — required)

Minimum 3 active per long-form video. Same rules as Law #55.

**LEVER 1 — THE OPEN POSITION:** State the take clearly. A neutral take gets no comment.
**LEVER 2 — THE DEBATE SPLIT:** Create two named sides. Both camps need something to say.
**LEVER 3 — THE SPECIFIC DETAIL:** Drop one thing real fans either know or don't know.
**LEVER 4 — THE UNFINISHED THOUGHT:** Closer leaves one thread open. Viewer finishes it.
**LEVER 5 — THE PINNED COMMENT POSITION:** States the creator's position + leaves a specific open thread.

---

## LONG-FORM SPECIFIC ADDITIONS

### THE MID-VIDEO COMMENT TRIGGER
Shorts have one shot at triggering a comment — the closer.
Long-form has multiple shots.

Every 2–3 minutes of long-form should contain at least one line that
could make a viewer pause the video and think "I need to respond to that."

These are mid-video comment triggers. They do not replace the closer.
They stack on top of it.

Types of mid-video comment triggers:
- A claim the viewer disagrees with strongly enough to respond mid-watch
- A specific detail they want to confirm or correct
- A question the creator poses to themselves and does not immediately answer
  (setup for the answer that comes later — but the viewer starts forming their response)

### THE CHAPTER DEBATE
Long-form videos on YouTube can use chapters (timestamps).
Each chapter title is a micro-hook — the viewer reads them before watching.
Chapter titles that contain a stated position generate comments before the video even plays.

Wrong chapter title: "Guts's Backstory"
Right chapter title: "Why Guts Never Actually Gets to Grieve"

The chapter title is a claim. Make every chapter title a claim, not a label.

### THE DESCRIPTION COMMENT SEED
The video description is read by a different viewer than the one watching.
It is often the first thing a subscriber sees in their feed.

The description must contain:
1. The core claim of the video in one sentence (not a summary — the take)
2. One open question that seeds the comment section before anyone watches

Wrong: "In this video I break down why Guts is such a tragic character in Berserk."
Right: "Guts never gets to grieve. Every time he gets close — something takes it from him.
Is that strength or just what's left? Drop your answer below."

### THE REPLY WINDOW
Same rule as Law #55 — reply to every strong comment within the first hour.
Long-form comments are longer and more thoughtful — they deserve a longer reply.
One reply in the first hour signals to the algorithm that the comment section is active.

For long-form specifically:
- Pin the most contested comment (not the most positive — the most argued-about)
- Heart the comments that name a specific detail from the video (signals to the algorithm
  that viewers are watching closely)

---

## COMMUNITY ACTION — IN EVERY LONG-FORM PLANNING SESSION

LONG-FORM COMMUNITY PLAN:
Mid-video triggers: [list the 2–3 lines designed to generate mid-watch responses]
Chapter titles: [confirm each chapter title is a claim, not a label]
Description claim: [one sentence — the take, not the summary]
Description question: [one open question to seed comments]
Pinned comment: [position + open thread — specific to this video]
Reply window: within 1 hour of publishing

---

## AUTO-FAIL CHECK

Before publishing:
[ ] Are at least 3 of the 5 community levers active?
[ ] Are there 2–3 mid-video comment trigger lines?
[ ] Does every chapter title state a claim — not a label?
[ ] Does the description contain the take in one sentence + an open question?
[ ] Is the pinned comment written — not left to post-publish?
[ ] Is the reply window scheduled (within 1 hour of publishing)?

---

## RELATED LAWS
- Law #55 — Community Comment Law (Shorts version — this law is the long-form equivalent)
- Law #62 — CUT 7 Closer (the long-form closer is the final comment trigger)
- Law #72 — Long-Form Pre-Publish Checklist (enforcement gate)

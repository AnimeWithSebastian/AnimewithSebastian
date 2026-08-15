# Law #75 — Research Before Recommendations
**Added:** June 16, 2026
**Triggered by:** Agent offered 4 video options based on memory and pattern-matching. None were verified against live data before being presented. User caught it.

---

## The Law

**Every video idea, show recommendation, format suggestion, or content option presented to the user must be grounded in live research run in that session — not memory, not pattern-matching, not training data.**

Before presenting any video options, the following must be completed first:

1. **SEARCH 1 — What is trending in the anime community right now?**
   Run a live search. Pull actual Reddit threads, YouTube activity, AniTrendz, Anime Corner, or equivalent sources dated within the last 7 days. Do not use memory of "what tends to trend."

2. **SEARCH 2 — What are the active fandom debates this week?**
   Specific shows, specific arguments. Verified by live Reddit or community source. Not assumed from past knowledge of what fandoms typically argue about.

3. **SEARCH 3 — Competitor check.**
   Has this angle already been posted by a competitor this week? Check before recommending it. A good angle that already exists is not a good option.

Only after these three searches are complete may options be presented to the user.

---

## What This Covers

- Show picks for any video slot (morning, evening, manual)
- Format suggestions tied to a specific show
- "Here are some options" responses
- Angle ideas for any format type
- Any statement like "this show is trending" or "this fandom is active right now"

---

## The Failure Pattern

**WRONG:**
Agent thinks: "Naruto's Pain is a popular villain debate. Death Note Light Yagami is always discussed. HxH Chimera Ant is controversial. Vinland Saga S2 is underrated."
Agent presents these as options.

None of these were verified as active this week. They are memory. They may be stale, already covered by competitors, or not trending at all right now.

**RIGHT:**
Agent runs SEARCH 1 (trending this week), SEARCH 2 (active fandom debates with live sources), SEARCH 3 (competitor check) — then presents options with sources attached to each one.

---

## What Each Option Must Include When Presented

Every option given to the user must have:
- The show name
- Why it's relevant RIGHT NOW — with a live source and date
- The format recommendation — and why that format fits this show at this moment
- Competitor check result — CLEAR or BLOCKED

If any of these cannot be sourced from live research, the option does not get presented.

---

## Applies To
- All video recommendations in any context
- Cron-generated show picks (already covered by the runtime research stack — this law reinforces it)
- Manual video requests where the user asks "give me options" or "what should I make today"
- Any proactive suggestion the agent makes about content direction

---

## Connection to Other Laws
- Law #52: Never source factual claims from memory — every specific claim verified via live source. This law extends Law #52 specifically to content recommendations and video ideas.
- Law #73: Every clip reference must be verified via live source. Same principle applied upstream — to the idea selection phase, not just the clip phase.

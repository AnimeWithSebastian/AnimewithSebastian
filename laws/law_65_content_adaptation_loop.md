# LAW #65 — CONTENT ADAPTATION LOOP
**System:** AnimeWithSebastian — v5.1
**Added:** June 2026
**Status:** ACTIVE

---

## THE LAW

The system does not run on instinct. It runs on data.

Every content decision — show selection, format choice, angle type, VO structure —
is informed by three live inputs that are checked and updated on a regular cycle:

1. **Your own YouTube analytics** (what your audience is actually watching)
2. **What is working in your niche right now** (what anime Shorts creators are doing that's landing)
3. **Competitor behavior** (what popular channels in the anime Shorts space are doing)

None of these are checked once and forgotten. They feed back into the system weekly.

---

## THE THREE INPUTS

### INPUT 1 — YOUR OWN ANALYTICS (Weekly — Sunday cron, Law #61)

**What gets read:**
- Views, watch time, retention rate, likes, comments, shares per video
- Grade per video: LOOP SIGNAL / STRONG / AVERAGE / WEAK / DROP
- Format type and show per entry

**What gets adjusted based on analytics:**
- Shows whose videos consistently grade WEAK or DROP → lower rotation or hold
- Shows whose videos grade LOOP SIGNAL or STRONG → higher rotation, more angles banked
- Format types that consistently outperform → weighted higher in nightly format recommendation
- Format types that consistently underperform → deprioritized for 2 weeks
(Tracking note: this mechanism has zero code enforcement and no state file currently exists — see docs/UNDERPERFORMANCE_DEPRIORITIZATION_TRACKING.md before treating this rule as actually applied to any real selection.)

**Where this lives:**
`/home/user/workspace/analytics_performance_log.json`
This file does not currently exist in the repo; see docs/UNDERPERFORMANCE_DEPRIORITIZATION_TRACKING.md Finding 3.
Updated every Sunday by cron 2bb28991.

**Rule:** No show stays in high rotation based on assumption.
If the data says a show is performing → it stays high.
If the data says a show is not converting → it moves down.
The creator's preference for a show does not override the data.
The data informs. The creator decides. The system records.

---

### INPUT 2 — NICHE TRACTION RESEARCH (Daily — every cron run)

This is already embedded in the cron as SEARCH 5 (FORMAT RESEARCH) and
SEARCH 6 (TRACTION CONFIRMATION). Law #65 formalizes what those searches
must find and how the findings must affect the package.

**What gets searched:**
- SEARCH 5: `[show] YouTube Shorts [current year] most viewed format`
  → Identifies which of the 8 format types is performing best for this show right now
- SEARCH 6: `[show] anime [current month year] site:reddit.com OR site:youtube.com`
  → Confirms the show has active fandom discussion (not dormant)

**Additional niche search (NEW — added by Law #65):**
- SEARCH 7: `anime Shorts [current month year] most viewed format`
  → Identifies what format type is performing best across anime Shorts as a whole right now
  → Not just for the selected show — for the entire niche
  → Result informs the format recommendation as a secondary signal

**What gets adjusted based on traction research:**
- If a format is trending across anime Shorts broadly (SEARCH 7) AND for the selected show (SEARCH 5) → that format gets priority recommendation
- If a format is trending broadly but not for the selected show → flag it as an alternative format option
- If the selected show has low traction (SEARCH 6) → switch to a higher-traction show before generating VO

**Rule:** Format recommendation is never made from assumption.
Every format recommendation cites the search result that informed it.
"Format recommended: CHARACTER_DIVE — [Source: [channel] posted [show] CHARACTER_DIVE [date], X views]"

---

### INPUT 3 — COMPETITOR BEHAVIOR (Weekly — integrated into Sunday analytics review)

**What gets researched:**
Popular anime Shorts channels are checked weekly to identify what is working
in the niche that the system can learn from — not copy.

**Known niche channels to monitor (as of June 2026):**
- AnimeUproar
- AnimeBallsDeep
- Kito Senpai (673K)
- BAKA
- Orewashimo / Shimo. (@OrewaShimo) — 200K subs, top Short 12M views
  Key formats: "Every Year" timeline lists, trivia/fact drops, hypothetical polls, One Piece deep dives
  Pattern: Shorts are almost entirely data-driven lists and fact drops. Long-form is personality/commentary.
  Strongest hook type: year-by-year ranking format ("anime of the year, every year") — massive curiosity click
  Primary show pillar: One Piece (dozens of Shorts + all long-form)
  Learning: LIST and FACT_DROP formats with curiosity-gap titles ("Don't watch these with your parents",
  "Are these physiques attainable") consistently outperform deep analysis on Shorts.
  Competitor overlap rule: if angle matches an Orewashimo Short with 1M+ views → it is consensus. Find gap beneath it.

**What gets noted per channel:**
- What format type did their recent top-performing Short use?
- What show? What angle type?
- What did the comment section respond to?

**The distinction — SIGNAL vs. RECREATION (user instruction June 12, 2026):**

Competitor research is for SIGNAL ONLY. Never for recreation. Originality is non-negotiable.

SIGNAL (correct use):
- "AnimeUproar's CHARACTER_DIVE on Killua got 400K views."
  → CHARACTER_DIVE is working for HxH right now. Use that format for a completely original HxH angle.
- "Orewashimo's curiosity-gap LIST titles are hitting 7M+ views."
  → Curiosity-gap LIST hook structure is working. Apply it to a different show, different claim.
- "One Piece is getting massive views across all competitors."
  → One Piece audience is active. Find a gap they haven’t touched.

RECREATION (hard stop):
- "AnimeUproar made a video about Killua's training scene. Make the same angle."
  → HARD STOP. That video exists. The audience already saw it. Find the gap beneath it.
- "Orewashimo made 'Don't watch these anime with your parents.' Make something similar."
  → HARD STOP. That title + concept is now owned by that video. Zero original value.

The rule: take the format, take the hook structure, take the topic signal.
Never take the angle, the specific question, or the framing.
Their video already exists. The audience already saw it.
Making the same thing is not competition — it is redundancy.

The goal is to understand what is landing in the niche — not what specific claim to repeat.

**What gets adjusted based on competitor behavior:**
- If a competitor's format type is consistently outperforming across multiple videos → that format type gets weighted higher for that show in the next 2 weeks
- If a competitor's angle on a show has already been made → that show + angle concept goes into the no-repeat blackout regardless of whether the creator made a video on it
  (The audience has already seen that take. It is consensus now.)
- If competitors are avoiding a show entirely → investigate why before assigning that show to a slot

**Where this gets logged:**
The Sunday analytics cron (2bb28991) includes a competitor behavior note section in its report.
Format: `COMPETITOR NOTE: [Channel] — [Format] — [Show] — [Views] — [Learning]`
This note is included in the weekly email to hero_or_villain@outlook.com.

---

## THE ADAPTATION CYCLE

This is the full loop. It runs on a weekly rhythm.

```
SUNDAY NIGHT
├── Cron 2bb28991 runs
├── Reads YouTube analytics for all videos
├── Grades every video (LOOP SIGNAL / STRONG / AVERAGE / WEAK / DROP)
├── Reads competitor behavior from that week
├── Updates rotation priorities based on grades
├── Saves to analytics_performance_log.json
└── Emails full report to hero_or_villain@outlook.com

DAILY (every cron run)
├── SEARCH 5: What format is working for THIS SHOW right now?
├── SEARCH 6: Does this show have active traction?
├── SEARCH 7 (NEW): What format is working across anime Shorts right now?
├── Format recommendation cites source
├── VO draft matches recommended format
└── Package sent → logged → loop continues
```

---

## WHAT THIS LAW PREVENTS

**Without Law #65:**
- The system produces the same formats week after week because nothing tells it to change
- A show stops performing but stays in high rotation because nobody checked
- A format is trending in the niche but the system keeps recommending something else
- A competitor made the same angle last week but the system doesn't know

**With Law #65:**
- Rotation adjusts weekly based on real performance data
- Format recommendations are informed by what is working in the niche today
- Competitor angles are tracked to prevent overlap with what's already been made
- The system gets smarter every Sunday

---

## THE HARD RULE

**Data informs. Creator decides.**

Law #65 does not automate content decisions. It ensures the system has the right
information before any decision is made.

If the data says CHARACTER_DIVE is working for JJK and the creator wants to make
a FACT_DROP instead — the creator can make that call. The law's job is to make
sure the creator is not making that call in the dark.

Every nightly package email must include:
- What the analytics data says about the selected show's recent performance
- What format is trending for this show (SEARCH 5 result)
- What format is trending in the niche broadly (SEARCH 7 result)
- What competitors have recently done with this show (if anything)

The creator reads it. Makes the call. The system records the outcome.
The following Sunday, the data tells whether the call was right.

---

## ENFORCEMENT

**Daily:** SEARCH 7 added to every cron run. Format recommendation must cite source.
**Weekly:** Sunday cron (2bb28991) includes competitor behavior section in its report.
**Monthly:** If analytics_performance_log.json shows a consistent pattern across 4+ weeks → the rotation priorities are manually reviewed and updated in the runtime files.

---

## RELATED LAWS
- Law #61 — Analytics Feedback Loop (the weekly grading system this law depends on)
- Law #53 — Airing Status (show rotation — feeds into adaptation decisions)
- Deep Research Law — daily angle research (separate from format/performance research)
- No-Repeat Rule — competitor angles that become consensus trigger the blackout

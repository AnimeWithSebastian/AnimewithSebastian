# Law #89 — Comment Generation System (Closer + CTA + Pinned Comment)

**Added:** June 29, 2026
**Sources:**
- YouTubeNiches.com — June 4, 2026 (comment-to-view ratio benchmarks; 3-5x lift from open question or wrong answer on purpose; reply within 60 min doubles count; pinned comment 8-12x engagement)
- AIR Media-Tech — June 18, 2026 (200-channel audit; pinned comment +30% replies vs generic CTA; meaningful comments outweigh one-word replies in 2026 algorithm; YouTube NLP reads comment sentiment)
- EvolveAMZ — June 19, 2026 (50 comments per 1,000 views treated as significantly more valuable than 200 likes per 1,000 views; binary question format 3-5x comment rate)
**Applies to:** Every VO and every email package — both runtime slots, every manual send
**Enforced in:** STEP 10 (Comment System Check) + STEP 13 (Pinned Comment) + EMAIL ASSEMBLY

## Why This Law Exists

Comments are the #1 algorithm signal on YouTube Shorts in 2026 — stronger than likes.
The channel's current comment-to-view ratio across top videos is near zero: 2 comments on 3,006 views (0.07%) and 0 comments on 2,611 views (0%) on the two highest-reaching videos.

**2026 benchmarks (YouTubeNiches June 4 2026):**
| Performance Tier | Comment-to-View Ratio | Algorithm Signal |
|---|---|---|
| Underperforming | Below 0.1% | Limited reach expansion |
| Average | 0.1% – 0.3% | Standard behavior |
| Strong | 0.3% – 0.6% | Algorithm likely expands distribution |
| Viral-trigger | 0.6%+ | Feed acceleration |

**Target for AnimeWithSebastian: 0.3% or above on every upload.**
Current channel average is below 0.1% on most videos. This law closes that gap.

The first 60 minutes after posting are the critical window. If a Short collects significant comments in that window, the algorithm reads it as momentum and expands distribution. Comments spread over days signal nothing.

## The Three-Part System

All three parts are REQUIRED in every package. Missing any one = the system fails.

---

### PART 1 — THE CLOSER (VO Final Line)

The last line of the VO must do one of two things:

**OPTION A — Open Question**
A binary or near-binary question the viewer can answer in 1–5 words.
Two real sides must exist. No clean answer. Cannot be resolved without commenting.
The question must be tied to THIS video's specific argument — not a generic prompt.

STRONG: "Was Gojo wasted — or was that always the point?"
STRONG: "Who was actually right — Erwin or Armin?"
STRONG: "Did they earn that ending, or did they just survive it?"
WEAK: "What do you think?" (no sides, no friction, no reason to comment)
WEAK: "Let me know in the comments." (instruction with no content)

**OPTION B — Wrong Answer on Purpose**
A deliberately incorrect or provocative claim the fandom cannot let stand.
Used sparingly — maximum once every 8–10 videos. Overuse burns credibility.
Works best when the audience prides itself on knowing more than the general viewer.
Example: Misframe a character's motivation in a way hardcore fans will immediately correct.

**BANNED from closer:**
- A clean conclusion ("That's why X is the best character.")
- A restatement of the hook ("So yeah, that's what makes X different.")
- A generic instruction ("Like and subscribe if you agree.")

---

### PART 2 — THE CTA (Inside the VO, 1 line before the closer)

One sentence before the final line. Specific to this video's emotional register.
The CTA plants the debate before the closer opens it.

**Format:** Identity/opinion tap — low friction, binary, tied to THIS video.

STRONG: "If you watched this show, you already have an answer."
STRONG: "Drop your take — I'm reading every one."
STRONG: "Come fight me in the comments."
WEAK: "Like and comment below."
WEAK: "What do you think about this?"

The CTA and the Closer work together as a two-sentence sequence at the end of every VO.
CTA plants the invitation. Closer delivers the question or the provocation.

---

### PART 3 — THE PINNED COMMENT

Pinned comment must be posted immediately after upload.
It must NOT restate the VO. It must ADD something — a second angle, a harder question, or a direct challenge.

**Four formats that work (AIR Media-Tech June 18 2026):**

1. **Polarizing question** — harder version of the closer. One sentence, two sides, no correct answer.
   "I'll start: [Sebastian's take]. Now come prove me wrong."

2. **Micro-poll** — A vs B framing. Viewer answers in one word.
   "Team [X] or Team [Y] — no fence-sitting."

3. **Debate seed** — Pin a counterargument to the video's main claim.
   Forces the audience to pick a side and defend the VO's position — or challenge it.

4. **Wrong answer trap** — State something slightly off. Anime audiences correct immediately.
   Use max once every 8–10 videos. Same sparingly rule as Part 1 Option B.

**What the pinned comment must NOT be:**
- A restatement of what the video said
- A generic "What did you think?" with no specific content
- Empty — the pin slot must never go unused

**Reply within 60 minutes of posting.** Reply to every comment in the first hour.
Early replies trigger notification loops that pull viewers back — doubling comment count in the critical first-hour window (YouTubeNiches June 4 2026).

---

## Enforcement — Comment System Check

Added to STEP 10 as CHECK 6 (after Hook Tension at Check 5):

**CHECK 6 — Comment Generation System**

Part 1 — Closer:
  Type: OPEN_QUESTION / WRONG_ANSWER / [MISSING]
  Two sides exist: YES / NO
  Specific to this video's argument: YES / NO
  Banned pattern present: YES / NO
  STATUS: PASS / FAIL

Part 2 — CTA:
  Present (1 line before closer): YES / NO
  Specific to this video's register: YES / NO
  STATUS: PASS / FAIL

Part 3 — Pinned Comment:
  Draft included in email: YES / NO
  Format: POLARIZING_Q / MICRO_POLL / DEBATE_SEED / WRONG_ANSWER_TRAP
  Adds something not in VO: YES / NO
  STATUS: PASS / FAIL

COMMENT SYSTEM RESULT: PASS (all 3 parts pass) / FAIL (any part fails)
If FAIL → rewrite the failing part before sending. Do not send a package with a failing closer.

---

## Target Metric

**Comment-to-view ratio target: 0.3% per upload.**
This is the threshold where the algorithm begins expanding distribution (YouTubeNiches June 4 2026).
On a 1,000-view Short: 3 comments minimum. On a 3,000-view Short: 9 comments.
Track this in the weekly analytics feedback run (cron 2bb28991).

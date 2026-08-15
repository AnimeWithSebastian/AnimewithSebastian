# LAW #95 — TITLE CONVERSION STANDARD

**Status:** ACTIVE — June 30, 2026
**Research basis:** Alan Spicer YouTube Title Framework 2026 | OpusClip 13.5M TikTok Clip Study (April 2026) | TTS Vibes Hashtag Quantity Performance Data (Jan 2026) | Sprout Social TikTok Guide 2026 | TikTok-enforced 5-tag max (August 2025)

> **CHARACTER TARGETS SUPERSEDED FOR 30s SHORTS by Law #144 (revised July 2026).**
> Production feedback: titles were too long. For Shorts, the `youtube_title` hard cap is
> **60 chars** (preferred 35–50) and there is a **distinct `tiktok_title` ≤55 chars**
> (preferred 30–45) — ONE punchy idea each, no explanatory subtitle/stacked clauses, no
> hashtags in either title. The "55–70 character" target and the `[Show]: [full sentence]`
> subtitle patterns below are retired for Shorts (keep the show-keyword-early and
> curiosity-gap principles). The TikTok CAPTION structure/hashtag guidance below still
> applies to `tiktok_post_text`. Where they conflict for a Short, **Law #144 wins.**

---

## THE RULE

Every title must do two jobs at the same time:
1. **Algorithm job:** Put the show name OR a real search term in the first 50 characters
2. **Click job:** Break an assumption OR create a curiosity gap in the same line

A title that does only one of these is a half-title. It either ranks but doesn't get clicked, or gets clicked but can't be found.

---

## YOUTUBE SHORTS — TITLE STRUCTURE

### REQUIRED FORMAT (Primary Title)
```
[Show Name]: [Broken Assumption or Curiosity Hook]
```

**Why:** First 50–60 characters display on mobile. Show name in front = algorithm indexes it for show-specific searches. Hook after the colon = human earns the click.

### APPROVED TITLE PATTERNS (research-verified)

| Pattern | Example |
|---|---|
| `[Show Name]: [Wrong Take Corrected]` | `Black Torch: The Canceled Manga Nobody Expected to Get an Anime` |
| `[Show Name]: [Specific Tension Nobody Asked]` | `Tanya the Evil: She's Not Fighting the War. She's Fighting God.` |
| `[Show Name]: [Outcome That Breaks Assumption]` | `Jaadugar: Science SARU Made Something That Looks Warm. It's Not.` |
| `[Year] [Show Name] [Modifier]` | `Black Torch 2026: The Canceled Manga That Came Back From the Dead` |
| `[What Nobody's Asking]: [Show Name]` | `The Question Nobody's Asking About Black Torch` |

### BANNED TITLE PATTERNS

| Pattern | Why banned |
|---|---|
| Pure hook with no show name in first 50 chars | Algorithm can't index it. Zero search traffic. |
| Show name buried after character 50 | Truncated on mobile. Name never seen. |
| Vague mystery with no payoff signal | "It's Getting an Anime Anyway" — doesn't signal what the video is about |
| Title that mirrors the thumbnail | Thumbnail creates hook, title must add context — not repeat it |
| Generic superlatives ("The Best", "Amazing") | No curiosity gap. Nothing to click for. |
| "Follow and Subscribe" or any platform CTA in title | Banned per channel law |

### THREE-QUESTION TEST (before publishing)
1. Does the show name appear in the first 50 characters?
2. If someone searched "[Show Name] anime" — would this title surface?
3. If someone saw this next to 9 competitor titles — would they click this one?

All three must be YES. If any is NO, rewrite.

### CHARACTER TARGETS
- Primary title: 55–70 characters total
- Show name + colon in first 30 characters
- Hook lands in characters 30–70
- No hashtags in YouTube title

---

## TIKTOK CAPTION — STRUCTURE

### REQUIRED FORMAT
```
[Hook sentence that matches VO line 1 — 100 chars max before "more"] [Show name keyword naturally in text] [Hashtags at end]
```

**Why:** TikTok is now a search engine. First 100–150 characters show before "more" on mobile — the hook and the keyword both need to live there. Hashtags at end of caption after the hook text.

### HASHTAG COUNT: 3–5 (HARD RULE)
TikTok enforced a 5-tag maximum in August 2025. Research consensus across multiple 2026 studies confirms 3–5 is optimal.

**Pyramid formula for anime niche:**
```
#[ShowName]          ← 1 show-specific tag (the target)
#animeshorts         ← 1 mid-tier niche tag (100K–1M posts)
#[FormatOrAngle]     ← 1 niche angle tag (e.g. #characterdive, #sleepinanime)
#anime               ← 1 broad community tag
#FYP                 ← 1 discovery tag (confirmed 2.2× median view lift vs. no FYP tag)
```

Total: 5 tags maximum. Never exceed 5. Never use fewer than 3.

### APPROVED CAPTION OPENING PATTERNS

| Pattern | Example |
|---|---|
| Statement that breaks assumption (matches VO line 1) | `This manga was canceled in 2018. Somehow it's getting a full anime before half the ones that finished.` |
| Reframe with show name in first sentence | `People call Tanya the Evil a loli war anime. That's not what it is.` |
| Discovery urgency + show name | `Jaadugar premieres July 4 and nobody's talking about what actually happens in episode 1.` |

### BANNED CAPTION PATTERNS

| Pattern | Why banned |
|---|---|
| Caption starts directly with hashtags | No hook = no reason to stop scrolling |
| "Follow for more" or "Subscribe" as CTA | Banned channel-wide per Law against platform CTA |
| Show name not in caption text | TikTok search can't find it by show name |
| Pure hype with no claim ("This is crazy 🔥") | No curiosity gap. Nothing to engage with. |
| More than 5 hashtags | Dilutes algorithm signal. Violates TikTok 5-tag max. |
| Repeating the same hashtag set every video | Algorithm suppresses repeat-tag stacks. Rotate per video. |

---

## STEP 10 APPLICATION

**Check added to STEP 10 as CHECK 10 (Title Conversion Check):**

```
CHECK 10 — TITLE CONVERSION STANDARD (Law #95):
  YOUTUBE PRIMARY TITLE:
    Show name in first 50 characters? [YES/NO]
    Broken assumption OR curiosity gap present? [YES/NO]
    Three-Question Test: all three YES? [YES/NO]
    CHARACTER COUNT: [X] — within 55–70? [YES/NO]
  TIKTOK CAPTION:
    Hook sentence in first 100 characters? [YES/NO]
    Show name keyword in caption text (not just hashtag)? [YES/NO]
    Hashtag count: [X] — within 3–5? [YES/NO]
    Hashtag pyramid: show tag + niche + angle + broad + FYP? [YES/NO]
  STATUS: [PASS / FAIL — list specific issue]
```

**Pass threshold:** All four YouTube checks = YES AND all four TikTok checks = YES.
**Fail action:** Rewrite title or caption before building full package. Do not proceed to BLOCK 9.

---

## RETROACTIVE CORRECTION GUIDANCE

If a package has already been sent with a title that fails Check 10:
- Do not resend the email
- Note the issue in state.json under `title_correction_note`
- Apply corrected title when the video is actually posted (the email package is a starting point — creator rewrites before posting)
- Log the correction pattern so the cron learns from it

---

## SOURCES
- [Alan Spicer — How to Write YouTube Titles That Get Clicked (2026)](https://alanspicer.com/how-to-write-youtube-titles-2026/)
- [OpusClip — Anatomy of a Viral TikTok in 2026 | 13.5M Clips Analyzed](https://opus.pro/blog/anatomy-of-a-viral-tiktok-2026)
- [TTS Vibes — TikTok Hashtag Quantity Performance Statistics 2026](https://insights.ttsvibes.com/tiktok-hashtag-quantity-performance/)
- [Sprout Social — How to Use Hashtags on TikTok in 2026](https://sproutsocial.com/insights/tiktok-hashtags/)
- [Buffer — Top 250 TikTok Hashtags for 2026](https://buffer.com/resources/tiktok-hashtags/)
- [Packapop — Anime YouTube Video Ideas That Explode Small Channels In 2026](https://packapop.com/blogs/youtube-success-blog/anime-youtube-video-ideas)


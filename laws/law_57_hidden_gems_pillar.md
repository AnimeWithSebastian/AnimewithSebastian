================================================================================
HIDDEN GEMS PILLAR LAW — LAW #57
VERSION: 1.0 — June 7, 2026
APPLIES TO: All crons (57a3c92e, d43ab889) + manual runs
CREATED: Channel rebrand to AnimeWithSebastian. Three content pillars defined.
PURPOSE: At least one Hidden Gem video per week. Niche, underrated anime
         and manga the creator actually believes in. Hard stop at 7 days
         without one. Manga track minimum 1 per month.
================================================================================

## WHAT HIDDEN GEM CONTENT IS

Anime and manga that are genuinely underrated — not just unpopular, but
actually worth watching and underrepresented in the conversation.

The creator has to actually believe in the show. This is not "here's a
random anime nobody knows." It is: "this exists and you are missing it."

The angle is always discovery — giving the viewer something they can't get
from any mainstream anime channel.

## WHAT QUALIFIES AS A HIDDEN GEM

Three criteria — all three must be true:
1. LOW VISIBILITY: Under 200K MAL members OR not in mainstream anime discourse
2. GENUINE QUALITY: The creator has watched it and believes it is worth someone's time
3. CLEAR HOOK: There is a specific scene, character, or moment that makes it worth the video

Examples of valid Hidden Gem angles:
- Vinland Saga S2 (before it blew up) — the pacifism arc nobody expected
- Berserk 1997 — the original anime that most people have only heard about
- Dorohedoro — the world is insane and nothing makes sense and it's perfect
- Apothecary Diaries — she's not the chosen one, she's just smarter
- Dungeon Meshi — eating monsters as a love letter to the world-building
- Kaiji — the purest anxiety you will ever feel watching anime
- Ping Pong the Animation — the most honest sports anime ever made
- Rainbow: Nisha Rokubō no Shichinin — nobody talks about this and they should

## MANGA TRACK

Minimum 1 manga-focused video per month.
Manga track = showing the source material for a known anime, OR
              introducing a manga that has no anime adaptation yet.

Valid manga angles:
- "the anime cut this and it changes everything"
- "this manga has no anime and it should"
- "the manga ended differently and it was better / worse"

Manga content must still pass Law #53 — never frame manga content
as "in the anime" unless it has been animated.

## THE ROTATION RULE

Minimum 1 Hidden Gem per week across both slots combined.
Hard stop: if 7 days pass with no Hidden Gem content — next package MUST be Hidden Gem.
Manga track: if 30 days pass with no manga-focused video — next Hidden Gem MUST be manga.

Check sent_scripts_log.json gap_type field for last HIDDEN_GEM entry.

## WHAT SHOWS UP IN THE EMAIL

Add to Research Note block:
HIDDEN GEM CHECK: Last Hidden Gem was [date] — [N] days ago — [WITHIN LIMIT / HARD STOP TRIGGERED]
MANGA TRACK: Last manga video was [date] — [N] days ago — [WITHIN LIMIT / HARD STOP TRIGGERED]

## AUTO-FAIL CHECK

Before every send:
[ ] When was the last Hidden Gem video (check sent_scripts_log.json)?
[ ] If 7+ days — this package must be Hidden Gem
[ ] Does the show genuinely qualify — low visibility, real quality, clear hook?
[ ] If manga: is it framed as manga content, not "in the anime"?
[ ] Has the manga track limit (30 days) been hit?

SELF-HEAL SOURCE: /home/user/workspace/laws/law_57_hidden_gems_pillar.md
================================================================================
END OF HIDDEN GEMS PILLAR LAW — LAW #57
================================================================================

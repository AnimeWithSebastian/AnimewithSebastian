# LAW #73 — CLIP VERIFICATION

> **SUPERSEDED — 2026-07-28.** This file describes only the original two-state
> model ("VERIFIED" or "FLAGGED — UNVERIFIED," no third option) as it existed on
> 2026-06-14. It predates the July 25, 2026 restoration/extension into
> `daily_combined`, and predates Updates 3B, 4, and 5 (theatrical release-window
> clause; scene-content self-audit and story-point gate; clip_locate grounding).
> It is preserved here as a historical record only and is not loaded by any
> runtime. For the current, authoritative Law #73 text, see the Law #73 sections
> of `hero_or_villain_master_laws_final.txt`.

**Status:** SUPERSEDED (historical record only — see banner above)  
**Version:** 1.0  
**Channel:** AnimeWithSebastian (@animewithsebastian)  
**Applies To:** ALL video formats — Shorts and Long-Form  
**Companion Laws:** Law #52 (no guessing facts), Law #69 (fact verification gate)  
**Date Added:** 2026-06-14  
**Reason Added:** Agent wrote "Luffy at Laugh Tale" as a clip suggestion — that scene does not exist. Luffy has not been to Laugh Tale in current canon. This law prevents that class of error from recurring.

---

## CORE RULE

Every clip reference in a production package must be either:

1. **VERIFIED** — confirmed via a live source that the scene exists (episode number, chapter number, or named arc), OR
2. **FLAGGED** — explicitly marked `[UNVERIFIED — confirm before using]` so the creator knows to check before editing

There is no third option. A clip suggestion that is neither verified nor flagged is a Law 73 violation.

---

## WHAT COUNTS AS A CLIP REFERENCE

Any of the following in a CapCut edit order, script, or production package:

- Episode numbers (e.g. "Ep 968", "Ep 1071")
- Chapter numbers (e.g. "Ch 967", "Ch 1045")
- Scene descriptions tied to a specific moment (e.g. "Roger laughing at Laugh Tale")
- Character locations (e.g. "Luffy at Laugh Tale", "Zoro in Wano")
- Visual moments described as fact (e.g. "Gear 5 transformation", "sake cup exchange")
- Any footage described as existing in the anime or manga

---

## VERIFICATION STANDARD

A clip reference is VERIFIED only if one of the following is true:

- The episode or chapter number was confirmed via a live source (One Piece Wiki, Fandom, verified YouTube timestamp, or equivalent) in the current session
- The scene is so foundational it has been confirmed in prior verified research already documented in this session (e.g. Chapter 1 / Shanks bottle — confirmed via onepiece.fandom.com/wiki/Chapter_1)
- The agent personally searched for and found the clip reference during this session

**Memory is not verification.** The agent's knowledge of One Piece does not count as a source. If the agent cannot point to a live source that was checked in the current session — the clip must be flagged.

---

## THE FLAG FORMAT

When a clip cannot be verified, it must appear in the production package exactly like this:

```
Cut X — [SCENE DESCRIPTION]
Caption: "[CAPTION TEXT]"
Duration: X–X sec
STATUS: UNVERIFIED — confirm this scene exists before using.
```

The flag must be on its own line. It must say UNVERIFIED. It must not be buried in a note or softened with "may" or "possibly."

---

## WHAT TRIGGERED THIS LAW

June 14, 2026 — Agent wrote the following in a Shorts production package:

> Cut 5 — Luffy at Laugh Tale or Gear 5 moment

Luffy has not been to Laugh Tale in current canon (as of June 2026). This is not footage that exists. The agent generated this suggestion from reasoning — "the video is about Laugh Tale, so Luffy + Laugh Tale" — without verifying that the scene exists.

The correct clip was Gear 5 / Ep 1071, which was verified earlier in the session.

The error required a correction email and broke creator trust.

---

## HOW THIS LAW APPLIES IN PRACTICE

### During CapCut edit order construction:

For each cut, the agent must ask: *"Do I have a live source from this session confirming this scene exists?"*

- YES → write the cut normally, note the source
- NO → add the UNVERIFIED flag

### Common One Piece traps to check before writing:

- Luffy has NOT been to Laugh Tale (as of June 2026)
- Roger's treasure at Laugh Tale is NOT clearly shown — its form is deliberately hidden
- Flashback scenes (Roger era, Void Century, Joy Boy) exist only in specific episodes — do not assume they exist without checking
- Character deaths, transformations, and arc-ending moments all have specific episodes — verify the number, do not guess

---

## ENFORCEMENT

This law applies to every production package — Shorts and Long-Form.

The clip verification check runs as part of the pre-send gate alongside Law #58 (Shorts) and Law #72 (Long-Form).

A package does not get sent if it contains an unverified clip reference that was not flagged.

If the agent cannot verify a clip and does not flag it — that is a Law 73 violation. The package must be corrected and a correction email sent before the creator begins editing.

# SESSION FIXES LAW
VERSION: 2.6 — Updated July 23, 2026

---
FIX 1 — CHANNEL CONCEPT: Established Anime with Sebastian channel concept. Short-form anime
content focused on character moral alignment, powers, and debate angles.
Status: FOUNDATIONAL — superseded by rebrand (Fix 21).

---
FIX 2 — INITIAL FORMAT LOCK: Hard 7-cut structure established as the only allowed format.
Every VO required exactly 7 cuts. No exceptions.
Status: REMOVED in Fix 24 (v5.0).

---
FIX 3 — 75-WORD CAP: Hard cap of 75 words per VO established to prevent Long-form
structure bleeding into Short format.
Status: REMOVED in Fix 24 (v5.0). Replaced by conversational length guidance (Law #59).

---
FIX 4 — LIST/RANKING BAN: Top 10 and ranking formats banned. Concern was that
list content would read as generic and undifferentiated.
Status: REMOVED in Fix 24 (v5.0). Lists and rankings unlocked under Open Format System.

---
FIX 5 — ESSAY STRUCTURE BAN: Banned Essay Opener, Evidence Sequence, Clean Conclusion
from all VOs. These three structures made the VO sound like a paper.
Status: KEPT. Codified in Law #59 (VO Length / No Essay Rule).

---
FIX 6 — ARGUMENT/DEBATE REQUIREMENT: Every VO required a clear argument or position.
Neutral or informational content was not allowed.
Status: MODIFIED. Argument optional under Open Format System. FACT_DROP and TRIVIA
formats do not require a debate position.

---
FIX 7 — HASHTAG SPEC v1: First hashtag spec established. Show name + #anime required.
Status: EVOLVED into current 5-hashtag spec (Law active in all runtimes).

---
FIX 8 — SHOW BLACKOUT SYSTEM: Airing shows blocked from production until episode count
and community sentiment could be assessed. Blackout state tracked in blackout_state.json.
Status: ACTIVE. Codified in Law #53 (Airing Status).

---
FIX 9 — VOICE AUDIT v1: First VO Human Voice Audit introduced. Checked for AI-sounding
phrasing, formal language, and unnatural sentence structure.
Status: EVOLVED into VO Quality Check 5-point gate (Fix 24 / v5.0).

---
FIX 10 — FACT VERIFICATION REQUIREMENT: Every specific claim in a VO must be verified
against a live source before send. No sourcing from memory.
Status: ACTIVE. Codified in Law #52 and Law #58 (Pre-Send Verification).

---
FIX 11 — SENT SCRIPTS LOG: sent_scripts_log.json established to track every sent VO.
Fields: video title, show, format, date sent, YouTube video ID (added later).
Status: ACTIVE. File rebuilt in June 2026 session.

---
FIX 12 — CREATOR VOICE SPEC v1: First definition of the creator voice standard.
Conversational, not formal. Casual, not academic. No "hey do you know" opener.
Status: EVOLVED. Codified in Law #54 (Creator Voice).

---
FIX 13 — CLIP INSTRUCTIONS ADDED: Crons began providing specific clip instructions
alongside VO drafts. What to show, when, how long to hold.
Status: ACTIVE in all cron packages.

---
FIX 14 — TITLE SPEC: 3 title options per package. Under 60 characters. No clickbait
promise that the VO does not deliver. Keyword-first when possible.
Status: ACTIVE in all cron packages.

---
FIX 15 — COMMUNITY COMMENT REQUIREMENT: Each package required one comment-starter
question or engagement prompt designed to seed early comments.
Status: EVOLVED. Codified in Law #55 (Community Comment).

---
FIX 16 — ORIGINS PILLAR: Origin Story format established as a dedicated content pillar.
How a character was designed, what the author based them on.
Status: ACTIVE. Codified in Law #56 (Origins Pillar).

---
FIX 17 — HIDDEN GEMS PILLAR: Hidden Gem format established as a dedicated content pillar.
Underrated shows and characters, content that cut through on low competition.
Status: ACTIVE. Codified in Law #57 (Hidden Gems Pillar).

---
FIX 18 — HOLD LIST: Steel Ball Run and Kagurabachi added to formal hold list.
SBR: Hold until Fall 2026. Kagurabachi: manga only, no anime confirmed.
Status: ACTIVE. Hold list lives in all runtime files.

---
FIX 19 — DANGLING CLAIMS IDENTIFIED: Viewer comment triggered identification of
dangling claims as a systemic issue. "You said DitF did something the fans never forgave
but never said what it was."
Status: ACTIVE. Codified in Law #60 (Dangling Claims Law).

---
FIX 20 — CUT 7 CLOSER ISSUE IDENTIFIED: Viewer comment on a published video:
"are you saying X?" after the final cut. Closer did not state the conclusion.
Status: ACTIVE. Codified in Law #62 (CUT 7 Closer Law).

---
FIX 21 — REBRAND TO ANIMEWITHSEBASTIAN: Channel rebranded from Anime with Sebastian to
AnimeWithSebastian. Handle: @animewithsebastian. Email delivery: hero_or_villain@outlook.com.
All system files updated to reflect rebrand. GitHub repo: AnimeWithSebastian.
Status: ACTIVE — current channel identity.

---
FIX 22 — CREATOR VO TAKEOVER (v4.0) — June 9, 2026
Trigger: TikTok comments identifying content as AI-generated.
Change: Removed all VO generation from crons. Fuel-only package.
Crons provide: angle, research stack, clip instructions, titles, hashtags.
Creator writes all VO from scratch.
Status: SUPERSEDED by Fix 23.

---
FIX 23 — HYBRID MODE (v4.1) — June 9, 2026
Trigger: Creator wanted draft VO as starting point to rewrite.
Change: Restored VO generation as draft only. Creator rewrites before posting.
Crons provide: full package + draft VO clearly labeled as starting point.
Status: SUPERSEDED by Fix 24.

---
FIX 24 — OPEN FORMAT SYSTEM (v5.0) — June 9, 2026
Trigger: Creator wants full format freedom. Not tied to single structure.
Change: Removed all format locks. 8 format types unlocked.
Added SEARCH 5 — format research identifies best performing format for selected
show right now via live traction data.
Draft VO matches the recommended format exactly.
VO Quality Check (5 points) replaces VO Human Voice Audit.
REMOVED: 3-structure lock, list/ranking hard block, 7-cut requirement,
         75-word hard cap, essay/argument ban, Law #59/#60/#62 enforcement.
KEPT: Fact verification (Law #52/#58), show blackout, hashtag spec, hold list.
NEW: STEP 5 FORMAT RESEARCH (SEARCH 5), STEP 6 FORMAT RECOMMENDATION,
     8 format types, VO Quality Check 5-point gate.
Post-send log fields updated: format_type, format_reason, vo_draft_included.
Status: ACTIVE — current version.

---
FIX 25 — GITHUB PERSISTENCE (v5.1) — June 12, 2026
Trigger: Workspace reset between sessions causing cron file loss.
Change: All critical system files stored in GitHub repo AnimeWithSebastian.
Crons pull from GitHub at STEP ZERO before reading any local files.
After sending email and updating log, crons push changes back to GitHub.
Files persisted: cron_evening_runtime.txt, cron_morning_runtime.txt,
  cron_evening_rework.txt, cron_morning_rework.txt,
  sent_scripts_log.json, blackout_state.json, laws/, channel_history.json.
Status: ACTIVE.

---
FIX 26 — REBRAND CONFIRMED: AnimeWithSebastian (v5.2) — July 23, 2026
Trigger: Channel owner confirmed the current, final channel identity in a live
session, explicitly superseding the Fix 21 rebrand to "AnimeWithSebastian" (channel).
Change: Channel brand/name is AnimeWithSebastian, handle @animewithsebastian.
"Hero or Villain" and "AnimeWithSebastian" (as a CHANNEL name) are retired and must
not be used in new docs, laws, or templates going forward. "AnimeWithSebastian
System" remains the separate, still-current name of the automation/production
system itself (GitHub repo AnimeWithSebastian) — that name was NOT changed.
Functional identifiers intentionally left untouched by this rebrand (renaming
them would break the running system): the production inbox
hero_or_villain@outlook.com, the file hero_or_villain_master_laws_final.txt,
the daily_combined cron id, and any JSON/log data recorded under prior names
(historical records, not renamed retroactively).
Status: ACTIVE — current channel identity.

---
NOTE (added July 24, 2026, policy decision — no historical backfill performed):
There is a known documentation gap between FIX 25 (June 12, 2026) and FIX 26
(July 23, 2026) in this changelog. `hero_or_villain_master_laws_final.txt` is the
authoritative source for changes made during that window, not this file.

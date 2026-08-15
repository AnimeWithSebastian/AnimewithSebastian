================================================================================
PRE-SEND VERIFICATION LAW — LAW #58
VERSION: 1.0 — June 7, 2026
APPLIES TO: All crons (57a3c92e, d43ab889) + manual runs
CREATED: After a script went out with wrong facts about Roy Mustang (FMA) and
         a Naruto/JJK content mix-up was sent in the same package.
PURPOSE: ZERO factual claims in any VO can be sourced from memory.
         Every claim is verified via live search before the email sends.
         If a claim cannot be verified — it is cut. Full stop.
================================================================================

## WHY THIS LAW EXISTS

Two incidents created this law:
1. A script claimed Roy Mustang "went blind on the Promised Day, he earned it,
   he used his alchemy, he went back to the battlefield" — three of those facts
   were wrong. It went out and got posted.
2. A package mixed Naruto and JJK content in the same script — verified claims
   from one show were applied to another.

These are not edge cases. They are what happens when any claim is sourced from
memory instead of a live search. Memory is wrong. Research is not.

This law makes live verification non-negotiable for every single claim.

## THE SIX CLAIM TYPES — ALL REQUIRE VERIFICATION

TYPE A — Episode or scene specifics
"In episode 58..." / "during the Chimera Ant arc..." / "after the Eclipse..."
Verify: episode number, arc name, scene description matches what actually aired.
Minimum: 1 live search. Source must be a wiki, MAL, or official page.

TYPE B — Real-world creator quotes or confirmed interviews
"Kishimoto confirmed..." / "Miura said in an interview..."
Verify: named source, named publication, year.
Minimum: 2 live searches. Reddit inference does not pass. Fan speculation does not pass.
If source cannot be found — DO NOT USE THIS CLAIM. Cut it.

TYPE C — Year and timeline claims
"This aired in 1994..." / "The manga started before the anime..."
Verify: exact year from MAL, Wikipedia, or AniList.
Minimum: 1 live search.

TYPE D — Character actions
"Hiei never said his sister's name out loud..." / "Guts didn't speak for the first arc..."
Verify: confirm against episode recap or fandom wiki.
Minimum: 1 live search.

TYPE E — Cross-show connections
"Sasuke was based on Hiei..." / "Geto's design echoes Sensui..."
These are the highest-risk claims. They are also the most engaging.
Verify: named confirmation from creator (Kishimoto on Hiei/Sasuke confirmed via interview)
        OR documented influence via credible source (not fan theory).
Minimum: 2 live searches. One must be a named source, not inference.
If only fan speculation exists — frame it as fan theory, not confirmed fact.

TYPE F — Anime vs manga boundary
Any claim that exists in manga but may not yet be in the anime.
Cross-reference with Law #53 airing status check.
If the scene or event hasn't aired — DO NOT USE in the VO as anime content.

## THE CONSISTENCY CHECK

After verification, run this check:
- Show in the subject line matches the show in every VO line
- Episode references are from the correct show
- Character names are from the correct show
- No cross-contamination between two shows researched in the same session

This is the Naruto/JJK rule. When two shows are researched back to back,
content from one can bleed into the other. Check every line.

## THE DANGLING CLAIM RULE (from Law #60)

Every claim that is opened in the VO must be expanded in the VO.
No name-dropping without follow-through.
No "Darling in the Franxx did something controversial" without saying what it was.
No teasing a fact without delivering the fact.

If the claim is opened, the claim must be closed in the same video.

## WHAT SHOWS UP IN EVERY EMAIL

Every package must include a FACT VERIFICATION BLOCK:

FACT VERIFICATION BLOCK:
Claim 1: [exact claim from VO] — Type [A/B/C/D/E/F]
Source: [URL or publication name]
Status: VERIFIED ✓ / BLOCKED ✗

Claim 2: [exact claim] — Type [A/B/C/D/E/F]
Source: [URL or publication name]
Status: VERIFIED ✓ / BLOCKED ✗

[repeat for every claim in the VO]

OVERALL STATUS: PASS — all claims verified / HARD STOP — [claim] blocked, see above

If HARD STOP: do not send. Fix the claim or cut it. Then re-run the block.

## AUTO-FAIL CHECK

Before every send:
[ ] Every factual claim in the VO has a verified source listed in the block
[ ] No claim is sourced from memory alone
[ ] TYPE B claims have 2 sources minimum — named, credible
[ ] TYPE E claims have 2 sources minimum — one named confirmation
[ ] Show in subject line matches every show reference in the VO
[ ] No dangling claims — every opened claim is closed in the same VO
[ ] OVERALL STATUS reads PASS before email sends

## ENFORCEMENT STATUS (crosswalk, added 2026-07-28 per Law #155 Part 5)

This law's literal "FACT VERIFICATION BLOCK" format (Claim N / Source / Status:
VERIFIED-or-BLOCKED, OVERALL STATUS: PASS/HARD STOP) is not implemented verbatim
in the current runtime or validator. Its substantive requirement — every core
claim sourced and typed, high-risk claim types requiring 2+ sources — IS
mechanically enforced today via `claim_source_matrix` / `claim_type` /
`semantic_qa` in cron_daily_runtime.txt and validators/validate_dual_package.py.
Treat that mechanism as satisfying this law; it is a field-name crosswalk, not
a gap. See Law #155 Part 5 for the full verification of this claim.

## COMPANION LAW

Law #155 (Independent Second-Party Verification, added 2026-07-28) generalizes
this law's pre-send verification requirement across all artifact types — scripts,
law changes, fixtures, and reference documents — and defines what counts as a
genuinely independent check.

SELF-HEAL SOURCE: /home/user/workspace/laws/law_58_pre_send_verification.md
================================================================================
END OF PRE-SEND VERIFICATION LAW — LAW #58
================================================================================

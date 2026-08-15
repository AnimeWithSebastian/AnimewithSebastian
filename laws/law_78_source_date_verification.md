================================================================================
SOURCE DATE VERIFICATION LAW — LAW #78
VERSION: 1.0 — June 25, 2026
APPLIES TO: All crons + manual runs. [Cron IDs corrected 2026-08-14 during a full
            law audit: this line named the retired morning/evening crons
            `57a3c92e` and `d43ab889`, which Law #139 replaced on 2026-07-15 with
            the single `daily_combined` run. The law itself still applies in full —
            only the cron identifiers were stale.]
CREATED: After a Dandadan Season 2 package was built using 2025 sources that were
         treated as current 2026 data. The episode dates in those articles had already
         passed — the season was over — but the cron presented them as upcoming.
PURPOSE: Force verification of WHEN a source was published before using it to support
         any time-sensitive claim (episode dates, premiere windows, airing status).
================================================================================

## WHY THIS LAW EXISTS

June 25, 2026 — A Dandadan S2 package was sent citing episode dates from sources
published in 2025. Those dates were correct in 2025. By June 2026, Dandadan S2 had
already finished airing. The package treated completed past content as upcoming content.

This is not a fact error — the sources were accurate WHEN written.
This is a SOURCE DATE error — using a time-decayed source without checking its age.

Law #52 says never use memory. This law adds: never use a search result without
checking when that result was published.

## THE RULE

Before citing any source to support a time-sensitive claim, the agent must:

STEP 1 — Check the publication date of the source.
  Look for: date in the URL, byline date, or "Published:" field on the page.

STEP 2 — Apply the age threshold:
  Source published within 90 days → use freely.
  Source published 91–180 days ago → flag with a note: "[Source dated X — double-check still current]"
  Source published more than 180 days ago → REQUIRES a second current source to confirm.
    If no second current source found → DO NOT USE this claim as a current fact.
    Reframe the claim as historical: "as of [source date]" — OR cut the claim entirely.

STEP 3 — In the FACT VERIFICATION BLOCK, every citation must include its publication date:
  Claim: [claim text] — Type [A/B/C/D/E/F/G]
  Source: [URL]
  Source Date: [Month Year or exact date if visible]
  Status: VERIFIED ✓ / DATE-FLAGGED ⚠ / BLOCKED ✗

## TIME-SENSITIVE CLAIM TYPES (always require source date check)

- Episode air dates (past or upcoming)
- Season premiere or finale dates
- Streaming platform availability ("now on Crunchyroll / Hulu")
- Show status (airing / finished / cancelled / announced)
- Chapter release dates
- Theatrical window dates
- Any claim involving a date, "this week," "this month," "upcoming," "recent"

## STATIC CLAIM TYPES (source date check recommended, not mandatory)

- Character relationships and motivations (don't change)
- Creator interview quotes (cite year of interview)
- Episode episode plot descriptions from already-aired content

## WHAT THIS CATCHES

Scenario that created this law:
  Search result title: "Dandadan Season 2 Episode Schedule — All Release Dates"
  Published: August 2025
  Content: Lists every S2 episode date through September 2025
  Problem: By June 2026, all those dates have passed. S2 is over.
  Without this law: Agent reads dates → writes "Dandadan S2 Episode X drops [date]" → WRONG.
  With this law: Agent sees August 2025 publish date → 10+ months old → requires 2nd source → 
                 2nd source shows S2 finished → claim gets cut → correct package goes out.

## IN THE FACT VERIFICATION BLOCK

Add source date to every citation. Flag any source over 90 days old.

Example:
  Claim: "Witch Hat Atelier Episode 13 airs June 29" — Type G (status)
  Source: https://example.com/witch-hat-schedule
  Source Date: March 2026
  Status: DATE-FLAGGED ⚠ — 3 months old, requires confirmation search
  
  Confirmation search result: Witch Hat Atelier finale aired June 22, 2026 (confirmed)
  Final Status: BLOCKED ✗ — original claim false, finale already aired

## ENFORCEMENT

This law runs as part of STEP 8 (Fact Verification Block).
Every source used in the verification block must include its publication date.
Any source over 180 days old with no current backup → claim is blocked, cannot be used.

Missing source dates in the verification block = LAW #78 VIOLATION.

SELF-HEAL SOURCE: laws/law_78_source_date_verification.md
  [Path corrected 2026-08-15 during a law audit. This read
  "/home/user/workspace/laws/law_78_source_date_verification.md" — the old sandbox
  layout, which does not resolve in this repo-based checkout. Per Session Fixes
  FIX 25 the GitHub repo is the authoritative source, so the path is now
  repo-relative. The self-heal instruction itself is UNCHANGED — only the path
  was stale.]
================================================================================
END OF SOURCE DATE VERIFICATION LAW — LAW #78
================================================================================

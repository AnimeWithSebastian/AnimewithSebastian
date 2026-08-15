================================================================================
VO STATUS LOCK LAW — LAW #79
VERSION: 1.0 — June 25, 2026
APPLIES TO: All crons (57a3c92e, d43ab889) + manual runs
CREATED: After a Witch Hat Atelier VO was sent with the line "Episode 13 drops Monday"
         when the finale had already aired June 22, 2026 — 3 days before the package
         was sent. No status verification was run before writing the VO.
PURPOSE: Any VO line that references a show's current status must be verified via
         a live source BEFORE the VO draft is written. Status is not assumed from
         research done for angle generation — it requires its own dedicated check.
================================================================================

## WHY THIS LAW EXISTS

June 25, 2026 — A Witch Hat Atelier HIDDEN_GEM package was built. The angle was
correct. The facts about the show's quality were correct. But one line in the VO said:

  "Episode 13 drops Monday."

That was false. The finale (Episode 13) aired June 22, 2026 — three days before the
package was sent. The show was completely finished.

The Fact Verification Block verified plot claims but never checked: "Is this episode
still upcoming, or has it already aired?"

Status was assumed from context, not verified from a live source. This law closes that gap.

## THE RULE

Any VO line that makes a STATUS CLAIM about a show requires a dedicated STATUS VERIFICATION
search BEFORE the VO draft is written. This is separate from STEP 4 (traction research)
and separate from STEP 8 (fact verification).

A STATUS CLAIM is any line that asserts:
  - An episode is upcoming ("drops Monday," "premieres this week," "Episode X coming")
  - A season is currently airing ("airing now," "new episodes dropping," "in its final arc")
  - A show is available somewhere ("streaming now on," "just hit Crunchyroll")
  - A season is upcoming ("Season 2 announced for," "returns in")
  - A finale is coming ("wraps up this month," "final episode incoming")

STATUS CLAIMS are Type G claims (see STEP 8 addition below).

## STATUS VERIFICATION PROCEDURE

Before writing any VO line that contains a status claim:

SEARCH: "[Show name] current status [current month year]"
         "[Show name] episode schedule [current year]"

Confirm from the search result:
  - Is the show currently airing, finished, or announced?
  - If an episode date is cited — has that date already passed?
  - If "streaming now" is claimed — confirm the platform and that it is currently available.

If the status search contradicts the planned VO line → STOP. Rewrite the VO line to match
the confirmed status before continuing.

## TYPE G — SHOW STATUS CLAIM (added to STEP 8 Fact Verification Block)

Existing claim types: A (general) | B (core) | C (year/number) | D (real-world connection)
                      E (cross-show) | F (anime vs manga boundary)

NEW: TYPE G — SHOW STATUS (airing status, episode availability, streaming status)
  Verify: current airing status from MAL, AniList, official streaming page, or recent article
  Minimum: 1 live search — source must be dated within 30 days
  If source is older than 30 days: run a second search to confirm status is unchanged
  If status cannot be confirmed via a source dated within 30 days → DO NOT make the status claim.
    Remove the time-sensitive line from the VO entirely.
    Replace with a non-time-sensitive alternative (e.g., "all 13 episodes are on Crunchyroll now").

## SAFE VO LINE PATTERNS (use when status is uncertain)

INSTEAD OF: "Episode 13 drops Monday" (time-sensitive, requires exact current verification)
USE: "All 13 episodes are available now on Crunchyroll"

INSTEAD OF: "Season 2 premieres this summer" (requires confirmed date)
USE: "Season 2 is in production" (if only production, not premiere, is confirmed)

INSTEAD OF: "New episodes drop every Sunday" (requires schedule verification)
USE: "It's currently airing" (if airing is confirmed but schedule is not locked)

## IN THE FACT VERIFICATION BLOCK

Add Type G claims alongside other claims:

  Claim: "Episode 13 drops Monday" — Type G (status)
  Search: "Witch Hat Atelier episode 13 release date June 2026"
  Source: [URL]
  Source Date: [Date]
  Status: BLOCKED ✗ — Episode 13 already aired June 22, 2026. VO line must be rewritten.

## ENFORCEMENT

Type G claims must appear in the Fact Verification Block.
Any status claim in the VO that is not listed as Type G in the block = LAW #79 VIOLATION.
Any Type G claim using a source older than 30 days without a second current confirmation = LAW #79 VIOLATION.
A VO with a status claim and no Type G entry = package CANNOT SEND.

## WHAT THIS PREVENTS

The Witch Hat incident:
  VO written: "Episode 13 drops Monday"
  Status check not run → claim not in fact block → package sent → false claim posted

With this law:
  VO planned with status claim → Type G search required before draft is written →
  Search result: finale aired June 22 → VO line removed before draft →
  Package goes out with correct status ("all 13 episodes available now") → no false claim

SELF-HEAL SOURCE: /home/user/workspace/laws/law_79_vo_status_lock.md
================================================================================
END OF VO STATUS LOCK LAW — LAW #79
================================================================================

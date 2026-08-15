# Experiments — AnimeWithSebastian

Tracks deliberate, bounded tests of unproven-for-this-channel patterns — a different
category from `docs/KNOWN_ISSUES.md` (which logs bugs/gaps in existing, supposedly-
working systems). An experiment here is expected to be unproven at the time it starts;
that is the point of logging it, not a defect.

---

## E1: External-Lens Framing (Law #153, added 2026-07-27)

**What's being tested:** framing anime content through a non-anime discipline
(psychology, film-craft, philosophy, history, etc.) instead of a "why you should
watch this show" recommendation frame, on Shorts specifically.

**Why:** the best-evidenced growth mechanism found in the 2026-07-27 research pass —
but proven only in long-form, never in a sub-60-second format.

**Evidence for the pattern (long-form only):**
- Super Eyepatch Wolf (@SuperEyepatchWolf, retrieved 2026-07-27): Punpun through a
  depression/mental-health lens — 6.37M views. Junji Ito through a horror-craft lens —
  5.40M views. Akira through a film-history lens — 4.60M views. His "Why You Should
  Watch [X]" recommendation-framed videos land at 2.36M-2.64M views. Non-anime framing
  outperforms recommendation framing by roughly 2.4x, same channel, same audience.
- Cinema Therapy (@CinemaTherapy): *A Silent Voice*, framed through clinical
  psychology, is the channel's #2 video of all time at 4.31M views — outperforming
  *Spirited Away* (1.37M) and *The Boy and the Heron* (368K) despite both having far
  greater mainstream source-material recognition.

**Evidence gap (why this is capped, not adopted):** zero verified examples of this
pattern exist under 60 seconds anywhere in public record as of 2026-07-27. This
channel's real volume is ~100% Shorts (166/166 real historical sends; Law #146
confirms zero flagships have ever been produced) — so the only way to get
Shorts-specific evidence is to run the experiment on Shorts, where the pattern has
never been tried, rather than starting on long-form where the evidence already exists
but where this channel has no real product yet.

**Mechanism:** `external_lens` field, set on the manifest package (see Law #153 rule
2). Free text naming the discipline used (e.g. `"psychology"`, `"film_craft"`,
`"philosophy"`, `"history"`). Orthogonal to `format_type` (Law #85) — a package can be
CHARACTER_DIVE or COMMENTARY in structure and separately carry an `external_lens` tag.

**Cap:** ≤1 package/week (Law #153 rule 1). Hard ceiling, not a target. 0/week is
fully compliant.

**Status as of 2026-07-27:** 0 real packages have ever set `external_lens` (law just
added, no daily run has occurred under it yet).

**Tracking going forward:** the weekly analytics cron must report `external_lens`-
tagged package performance separately from the rest of the portfolio (day-7 views,
stayed-to-watch, subs/1k), joined against real ledger data (`publication_ledger.jsonl`
by `youtube_video_id`), starting from the first package that sets this field. Update
this entry's status line each week the cron runs, whether or not any package used the
tag that week — a real "0 used again this week" is also a tracked fact, not a gap in
tracking.

**Explicitly out of scope for this document:** claiming this pattern works for Shorts
before real data exists. This entry records the test design and its evidence base; it
does not assert an outcome.

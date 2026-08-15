# Rewrite send record — One Piece / My Hero Academia clip-plan + captions correction (2026-08-01/02)

## Status

This round corrects the clip plan and on-screen captions for the same daily_combined
batch originally sent 2026-08-01 (evening delivery, targeting `post_date` 2026-08-02)
for One Piece (morning) and My Hero Academia (evening). Two distinct findings
prompted this round, both surfaced by a user-directed review after the original send:

1. **Unverified clip citations (Cuts 2-4).** The original send left all four clips in
   both packages `scene_verified: false` with only generic "almost certainly exists"
   fallback notes — no real `claim_vs_source_check` against actual episode content had
   been performed for the specific claims each cut makes. This round performed that
   check directly against fetched review/wiki content (not title-only lookups) for
   Cuts 2 and 3 in both packages, and added a general arc-level citation to each
   package's Cut 4 even though it carries no single specific claim requiring
   scene-level sourcing. Cut 1 in both packages stays honestly unverified — One Piece
   Cut 1 depicts Episode 1172 (airs 2026-08-02, no clip-level source can exist before
   air) and MHA Cut 1 depicts the "I Am a Hero Too" special (streams 2026-08-02, same
   reasoning).
2. **`captions` field regression (new finding, filed as F28).** A user-initiated
   comparison against the Black Clover and Akane-banashi packages (2026-07-30 batch)
   found that run #9's `captions` field held YouTube-description-style text with a
   hashtag pyramid instead of the per-clip on-screen keyword-caption block used in
   every prior confirmed send. Root cause is unconfirmed (schema allows an overloaded
   string with no content-shape check); documented in full in `docs/KNOWN_ISSUES.md`
   F28. Real per-clip on-screen captions have been generated for both packages this
   round, grounded in each clip's actual content, following the established visual
   convention (one orange keyword per line, Anton ALL CAPS white text black outline,
   max 2 lines on screen at once).

No VO, hook, title, or any other package content was changed in this round — only the
clip-plan verification/citations and the on-screen captions field.

## Packages corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| One Piece | morning | c8401ef5-1d1e-48ce-a3f4-39443498caea | 4af7ca6d-1545-4eae-8252-dc459afc39f6 | Cuts 2/3 upgraded to `scene_verified: true` with real citations (Episode 1170 review); Cut 4 given a general arc-level citation; Cut 1 stays honest F20 fallback (unaired Ep. 1172). Real on-screen captions generated (F28 fix). |
| My Hero Academia | evening | c8401ef5-1d1e-48ce-a3f4-39443498caea | 8f3552ac-bca7-4a1e-a6ed-8eb4afaa2756 | Cuts 2/3 upgraded to `scene_verified: true` with real citations (Episode 77, Episode 170); Cut 4 given a general character citation; Cut 1 stays honest F20 fallback (unstreamed special). Real on-screen captions generated (F28 fix). |

Both packages share `batch_id c8401ef5-1d1e-48ce-a3f4-39443498caea` and `post_date
2026-08-02` — this is the original daily_combined batch's clip plan and captions
being corrected in place via `run_manifest.json` edits plus a standalone correction
email, not a new batch.

### Corrected clip plan — One Piece (morning)

| Cut | Time | Scene | Verification | Source |
|---|---|---|---|---|
| 1 | 0:00–0:08 | Episode 1172 title card / key visual, "Monsters Appear in Elbaf: What I Fear Most" | UNVERIFIED (honest F20 fallback — airs 2026-08-02, no pre-air clip source possible) | [X/@Eiichiro_Staff](https://x.com/Eiichiro_Staff/status/2081390787745726801) confirms Ep. 1172 is the 8/2 episode |
| 2 | 0:08–0:16 | Recent Elbaf arc footage — giants, Elbaf's scale establishing shots | VERIFIED | Episode 1170 review, [But Why Tho?](https://butwhytho.net/2026/07/one-piece-episode-1170-review/) |
| 3 | 0:16–0:24 | Luffy reaction shots from recent Elbaf episodes | VERIFIED | Episode 1170 review, [But Why Tho?](https://butwhytho.net/2026/07/one-piece-episode-1170-review/) |
| 4 | 0:24–0:30 | Elbaf arc wide shot / crew ensemble footage | VERIFIED (generic B-roll, citation added though not strictly required) | [ComicBook.com Elbaf schedule](https://comicbook.com/anime/news/one-piece-confirms-the-full-elbaph-schedule-for-2026/) |

TOTAL CLIP TIME: 30 seconds

### Corrected clip plan — My Hero Academia (evening)

| Cut | Time | Scene | Verification | Source |
|---|---|---|---|---|
| 1 | 0:00–0:08 | "I Am a Hero Too" key visual / teaser preview art | UNVERIFIED (honest F20 fallback — streams 2026-08-02, no pre-release clip source possible) | n/a |
| 2 | 0:08–0:16 | Overhaul arc — Eri's rescue by Deku and Mirio | VERIFIED | S4E77 "Bright Future" — [MHA Fandom](https://myheroacademia.fandom.com/wiki/Episode_77), [Wikipedia](https://en.wikipedia.org/wiki/List_of_My_Hero_Academia_episodes), [Anime News Network](https://www.animenewsnetwork.com/review/my-hero-academia/episode-77/.155517) |
| 3 | 0:16–0:24 | Season 8 finale footage — series' emotional send-off | VERIFIED | S8E170 "My Hero Academia" — [MHA Fandom](https://myheroacademia.fandom.com/wiki/Episode_170), [Wikipedia](https://en.wikipedia.org/wiki/My_Hero_Academia_season_8) |
| 4 | 0:24–0:30 | Eri close-up / calm character shot from prior seasons | VERIFIED (generic B-roll, citation added though not strictly required) | [Heroes Wiki/Fandom — Eri](https://hero.fandom.com/wiki/Eri_(My_Hero_Academia)) |

TOTAL CLIP TIME: 30 seconds

## Corrected on-screen captions

- **One Piece:** `CUT 1: EPISODE 1172 / NAMES FEAR. CUT 2: ELBAF'S / GIANTS. CUT 3:
  LUFFY / REACTS. CUT 4: THE ARC / WIDENS.`
- **My Hero Academia:** `CUT 1: ONE MORE / SPECIAL. CUT 2: ERI'S / RESCUE. CUT 3: THE
  / FINALE. CUT 4: A QUIET / GOODBYE.`

Both follow the established convention: one orange keyword per line, Anton ALL CAPS
white text black outline, max 2 lines on screen at once.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`REWRITE_SEND_20260730_hxh_berserk_clip_plan.md`, `REWRITE_SEND_20260730_hxh_berserk.md`):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only.

Both `4af7ca6d-...` and `8f3552ac-...` already carry a `"status": "sent"` row in
`sent_scripts_log.json` under the original batch_id `c8401ef5-...` from the original
2026-08-01 send. Re-running the logger against this same `(batch_id, package_id)` pair
would be a silent no-op or an ambiguous duplicate. This markdown file is the record
instead. The original `sent_scripts_log.json` / `sent_scripts_events.jsonl` entries for
these two package_ids are NOT modified, duplicated, or appended to.

## New finding filed

`docs/KNOWN_ISSUES.md` F28: `captions` field overloaded with description text instead
of the on-screen keyword-caption block for run #9 (2026-08-02 batch). Status:
CONFIRMED regression, patched via this standalone correction round (manifest edit +
this email), not yet fixed at the generation-source/validator level. Backlog item
proposed: validator check that `captions` contains cut-labeled segments distinct from
hashtag-bearing description text.

## Sends and mailbox verification

Both sent to `hero_or_villain@outlook.com` only. Verified via a direct `search_email`
query immediately after sending, filtered to the exact subject strings, comparing full
(untruncated) `email_id` strings.

| Show | Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|---|
| One Piece | `CLIP PLAN + CAPTIONS CORRECTION \| MORNING \| One Piece \| originally sent 2026-08-02 \| One Piece Just Titled an Episode 'Fear'` | 2026-08-02T02:51:23Z and 2026-08-02T02:51:21Z | **2** — confirmed via `search_email`, two distinct full `email_id` strings ending `...U3TIAAAA` and `...U3DeAAAA`. |
| My Hero Academia | `CLIP PLAN + CAPTIONS CORRECTION \| EVENING \| My Hero Academia \| originally sent 2026-08-02 \| My Hero Academia Isn't Actually Over` | 2026-08-02T02:51:24Z and 2026-08-02T02:51:22Z | **2** — confirmed via `search_email`, two distinct full `email_id` strings ending `...U3TJAAAA` and `...U3DfAAAA`. |

**F21 duplicate-dispatch defect observed on BOTH sends tonight.** One `send_email`
tool call was made for each show; each produced two mailbox-side copies with distinct
full `email_id` strings, 1-2 seconds apart, both from `hero_or_villain@outlook.com` to
`hero_or_villain@outlook.com`, both carrying the exact corrected content approved by
the user. This matches the known connector-side duplicate-dispatch pattern already
documented in `docs/KNOWN_ISSUES.md` (F21) and observed in prior correction rounds —
not a new defect, and not evidence of a second distinct send action on this side. No
emails were sent to any address other than `hero_or_villain@outlook.com`.

## Filed

Date: 2026-08-02T02:51:24Z (UTC) — set to the latest of the confirmed send timestamps
above.

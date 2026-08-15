# Factual correction record — Chainsaw Man evening (stage-play date error) — 2026-08-02

## Status

This is the tracking record for a **FACTUAL CORRECTION** email sent for the
Chainsaw Man evening package (`batch_id fedf466c-243a-4fe2-b151-38f72d9febb5`,
`package_id 2c26862d-2113-4be2-b0e8-45e83870dbae`), originally generated and
sent by the autonomous `daily_combined` cron run at 2026-08-02T22:30Z UTC
for `post_date` 2026-08-03. This is the **first** correction round for this
package_id.

The Jujutsu Kaisen morning package in the same batch
(`package_id f5bf587d-2f67-4c79-87d0-70b28359565b`) was explicitly reviewed
and approved by the user as clean and was NOT touched — no changes, no
correction, no resend.

## What was wrong

The original VO's timely-hook sentence read: "That ending is being restaged
live on a Tokyo stage right now, moving to Kyoto next week." This was
inaccurate as of the actual 2026-08-03 post date. The script's own source #6
([Anime News Network, Apr 2026](https://www.animenewsnetwork.com/news/2026-04-22/chainsaw-man-reze-arc-stage-play-reveals-cast-trailer-dates/.236674))
states the Tokyo run of "Chainsaw Man The Stage: Reze Arc" runs July 25 -
August 2, 2026, and the Kyoto transfer runs August 7-12, 2026. The post date
(2026-08-03) is one day AFTER the Tokyo run already ended, so "right now" was
false, and August 7th is not "next week" from a same-day framing. This was
identified and reported by the user, not self-caught.

The pinned comment ("...putting in front of a live audience this week") and
the TikTok post text ("Restaged live in Japan right now") carried the same
false-immediacy error and required the same fix for consistency.

## Package corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Chainsaw Man | evening | fedf466c-243a-4fe2-b151-38f72d9febb5 | 2c26862d-2113-4be2-b0e8-45e83870dbae | VO's final content sentence rewritten from false-immediacy ("is being restaged live... right now, moving to Kyoto next week") to accurate past/future framing ("just wrapped a live Tokyo stage run, and it heads to Kyoto on August 7th"). Pinned comment and TikTok post text given the same date-accuracy fix. Word count unchanged at 108 (independently verified via regex word-boundary count, matching the existing `vo_word_count` field). Hook line, opening sentence, question line, CTA, clip plan (all 5 cuts/timings/scene verification), YouTube title, TikTok title, captions, clip descriptions, sources, and post times are all unchanged. |

## Corrected content

**VO (108 words):**
"Reze was sent to steal Denji's heart, and every soft moment at that café
started as the job. She reveals herself as the Bomb Devil right before the
fight breaks loose. Denji ties her up, then offers to run away together
anyway. She refuses and knocks him out cold. But she never actually leaves.
Reze heads for a train alone, changes her mind mid escape, and runs back to
that same café instead. Makima and Angel are already waiting there. That
ending just wrapped a live Tokyo stage run, and it heads to Kyoto on August
7th. Was her turnaround real, or one more con? Leave your take."

**Pinned comment:**
"People remember the bomb fight. Almost nobody brings up that she was
already gone, on the train, and chose to come back to a café instead of
freedom. That's the version the stage play just put in front of a live
Tokyo audience, before it heads to Kyoto on August 7th."

**TikTok post text:**
"Reze had a train ticket out and used it, then turned around anyway. The
Bomb Girl arc's real twist isn't the fight, it's the café. Just restaged
live in Tokyo, heading to Kyoto next. #ChainsawMan #Reze #AnimeShorts
#AnimeTok #Denji"

## Files edited

`cron_tracking/daily_combined/run_manifest.json` — the three fields above
(`vo`, `pinned_comment`, `tiktok_post_text` for the Chainsaw Man evening
package) were edited in place. No other fields in this manifest were
touched.

## Validator re-run

Ran `python3 validators/validate_dual_package.py cron_tracking/daily_combined/run_manifest.json`
against the corrected manifest: **full PASS**, all mechanical checks green
for both packages (JJK morning + Chainsaw Man evening), including
"VO within 100-108 words" and "vo_word_count matches VO text" for the
corrected package. Exit code 0.

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in every prior correction round this
session (see `VO_STRUCTURAL_CORRECTION_20260802_run9_onepiece_comma_splice_redundancy_fix.md`,
`REWRITE_SEND_20260730_hxh_berserk_clip_plan.md`, and others):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only.
`2c26862d-2113-4be2-b0e8-45e83870dbae` already carries a `"status": "sent"`
row in `sent_scripts_log.json`, logged at the original autonomous cron send
time `2026-08-02T22:30:00Z`. Re-running the logger against this same
`(batch_id, package_id)` pair would be a silent no-op (`events_appended: 0`)
and would not reflect this correction. Per the established pattern,
`sent_scripts_log.json` and `sent_scripts_events.jsonl` are left untouched —
this markdown file, plus the sent correction email itself, is the record
instead.

## Send and mailbox verification

Email sent to `hero_or_villain@outlook.com` only, subject `FACTUAL
CORRECTION | EVENING | Chainsaw Man | originally sent 2026-08-02 | Chainsaw
Man: Reze Was Already Gone. She Came Back`. Verified via direct
`search_email` immediately after sending.

| Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|
| FACTUAL CORRECTION \| EVENING \| Chainsaw Man \| originally sent 2026-08-02 \| Chainsaw Man: Reze Was Already Gone. She Came Back | 2026-08-03T00:21:36Z | 1 |

**Chainsaw Man (evening): 1 real mailbox copy — no F21 duplicate-dispatch
this time.** Single distinct `email_id` (`...U3DqAAAA`) confirmed via
`search_email`. Only one `send_email` tool call was made for this package.

**No emails were sent to any address other than `hero_or_villain@outlook.com`.**
The original 2026-08-02T22:43:37Z-22:43:40Z autonomous-cron copies (still
carrying the false-immediacy defect) were NOT re-triggered or removed — they
remain present as the honest historical record of the original send, per
standing user instruction not to touch existing send records. The Jujutsu
Kaisen morning package and its mailbox copies were not touched this round.

## Original flawed send (for reference, unmodified)

The original autonomous `daily_combined` cron run sent both packages at
2026-08-02T22:30Z UTC with confirmed F21 duplicate-dispatch (2 mailbox
copies each):
- JJK morning: subject "TOMORROW | MORNING | Jujutsu Kaisen | 2026-08-03 |
  Jujutsu Kaisen Just Confirmed Season 4" — 22:43:09Z and 22:43:14Z (clean,
  no correction needed, approved as-is by user).
- Chainsaw Man evening: subject "TOMORROW | EVENING | Chainsaw Man |
  2026-08-03 | Chainsaw Man: Reze Was Already Gone. She Came Back" —
  22:43:37Z and 22:43:40Z (flawed, corrected by this record).

## Filed

Date: 2026-08-03T00:21:36Z (UTC) — set to the confirmed send timestamp above.

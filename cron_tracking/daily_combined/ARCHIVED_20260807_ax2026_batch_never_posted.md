# Archived — 43 AX2026 Batch Scripts Never Posted (2026-07-04 batch)

## Status: ARCHIVED, NOT DELETED, NOT RESENT, NOT FURTHER REVISED

The following 43 packages were emailed to hero_or_villain@outlook.com on a
single date, 2026-07-04, under the legacy `batch: "AX2026"` tag (pre-dating
the current UUID `batch_id`/`package_id` schema). They were pre-written to
cover every morning/evening slot from 2026-07-23 through 2026-08-13 in one
shot, tied to Anime Expo 2026 news. Sebastian confirmed directly on
2026-08-07 that he received these emails but never recorded, edited, or
uploaded any of them to YouTube or TikTok — they sat unused. This was
independently corroborated before he was asked: `cron_tracking/publication_ledger.jsonl`
(the real source of truth for what is actually live on YouTube) contains
exactly 3 entries in its entire history (Though I Am an Inept Villainess
7/26, Jujutsu Kaisen 8/3, Chainsaw Man 8/4), and none of the 43 AX2026
package_ids/shows appear in it.

This surfaced during the 2026-08-07 daily_combined cron run (targeting
2026-08-08 output) when the AX2026 log entries for Steel Ball Run
Stages 2+3 (morning) and Witch Hat Atelier Season 2 (evening) were found
already logged against 2026-08-08 — before this file existed, this looked
like a possible duplicate/no-op condition for that date. It is not: the
real daily_combined pipeline had never produced anything for 2026-08-08,
and nothing from AX2026 was ever actually published. The 2026-08-08 date is
open and the daily_combined run proceeded normally to produce genuinely new
content for it.

| Show | post_date | slot | format_type |
|---|---|---|---|
| Solo Leveling: Beyond the System | 2026-07-23 | morning | WRONG_TAKE |
| Demon Slayer: Infinity Castle Movie 1 | 2026-07-23 | evening | SEASON_PREVIEW |
| Witch on the Holy Night (Film) | 2026-07-24 | morning | NEW_ANIME_INTRO |
| The Apothecary Diaries Movie | 2026-07-24 | evening | SEASON_PREVIEW |
| Akira 4K/IMAX Re-Release | 2026-07-25 | morning | WRONG_TAKE |
| Rascal Does Not Dream Final Movie | 2026-07-25 | evening | SEASON_PREVIEW |
| Kaguya-sama Original Movie | 2026-07-26 | morning | WRONG_TAKE |
| The Guy She Was Interested In Wasn't a Guy At All | 2026-07-26 | evening | WRONG_TAKE |
| Ghost of Tsushima: Legends (Anime) | 2026-07-27 | morning | NEW_ANIME_INTRO |
| Kagurabachi | 2026-07-27 | evening | SEASON_PREVIEW |
| Fate Rewinder | 2026-07-28 | morning | NEW_ANIME_INTRO |
| Magical Buffs | 2026-07-28 | evening | HIDDEN_GEM |
| Gacha Girls Corps | 2026-07-29 | morning | HIDDEN_GEM |
| The Vermilion Mask | 2026-07-29 | evening | NEW_ANIME_INTRO |
| You and I Are Polar Opposites | 2026-07-30 | morning | HIDDEN_GEM |
| ALIEN STAGE | 2026-07-30 | evening | NEW_ANIME_INTRO |
| Here U Are | 2026-07-31 | morning | HIDDEN_GEM |
| Smoking Behind the Supermarket with You | 2026-07-31 | evening | WRONG_TAKE |
| Fist of the North Star (Cour 2) | 2026-08-01 | morning | SEASON_PREVIEW |
| Eleceed | 2026-08-01 | evening | HIDDEN_GEM |
| Grow Up Show: Sunflower Circus | 2026-08-02 | morning | HIDDEN_GEM |
| Sword Art Online: Unanswered//butterfly | 2026-08-02 | evening | WRONG_TAKE |
| Star Wars: Visions – The Ninth Jedi | 2026-08-03 | morning | NEW_ANIME_INTRO |
| Dengeki Daisy | 2026-08-03 | evening | HIDDEN_GEM |
| Akane-banashi | 2026-08-04 | morning | HIDDEN_GEM |
| Marriage Toxin | 2026-08-04 | evening | HIDDEN_GEM |
| Black Clover Season 2 | 2026-08-05 | morning | SEASON_PREVIEW |
| Cyberpunk: Edgerunners Season 2 | 2026-08-05 | evening | WRONG_TAKE |
| Bleach TYBW Part 4 — The Calamity | 2026-08-06 | morning | SEASON_PREVIEW |
| The Apothecary Diaries Season 3 | 2026-08-06 | evening | SEASON_PREVIEW |
| Mashle Season 3 | 2026-08-07 | morning | SEASON_PREVIEW |
| The Elusive Samurai Season 2 | 2026-08-07 | evening | HIDDEN_GEM |
| Steel Ball Run Stages 2+3 | 2026-08-08 | morning | SEASON_PREVIEW |
| Witch Hat Atelier Season 2 | 2026-08-08 | evening | WRONG_TAKE |
| Rising of the Shield Hero Season 5 | 2026-08-09 | morning | SEASON_PREVIEW |
| Overgeared | 2026-08-09 | evening | WRONG_TAKE |
| Aoashi Season 2 | 2026-08-10 | morning | HIDDEN_GEM |
| Gachiakuta Season 2 | 2026-08-10 | evening | SEASON_PREVIEW |
| Delicious in Dungeon Season 2 | 2026-08-11 | morning | WRONG_TAKE |
| Dragon Striker Season 2 | 2026-08-11 | evening | NEW_ANIME_INTRO |
| Tougen Anki Season 2 | 2026-08-12 | morning | SEASON_PREVIEW |
| Re:Zero Season 4 Part 2 | 2026-08-12 | evening | SEASON_PREVIEW |
| Blue Lock Season 3 | 2026-08-13 | morning | WRONG_TAKE |

All 43 entries share `date_sent: "2026-07-04"` in `sent_scripts_log.json`
and carry no `batch_id`/`package_id` UUIDs (legacy schema). Real, verbatim
sent-email confirmation was pulled directly from the mailbox for the two
2026-08-08 entries (Steel Ball Run, Witch Hat Atelier) as part of this
investigation; the other 41 were not individually re-verified by email
lookup but share the identical `date_sent`/`batch` signature and the same
absence from the publication ledger.

## Note for future blackout/cooldown checks

Two shows in this archived batch were later independently covered by the
real daily_combined pipeline on dates *different* from their AX2026 slot,
under different angles:
- **Kagurabachi** — AX2026 logged it for 2026-07-27 evening (SEASON_PREVIEW,
  never posted); the real pipeline actually sent Kagurabachi on 2026-08-07
  morning (CHARACTER_DIVE, Chihiro's father backstory) — a real, separate,
  already-published-content decision, not a duplicate of the archived
  script.
- **Black Clover** — AX2026 logged "Black Clover Season 2" for 2026-08-05
  morning (SEASON_PREVIEW, never posted); the real pipeline's actual
  Black Clover coverage is tracked separately elsewhere in
  `sent_scripts_log.json` (manga-ending angle, already logged/audited in an
  earlier segment of this project).

Because none of the 43 AX2026 scripts were ever published, they do not
occupy any real 30-day blackout or 7-day no-repeat slot under
`blackout_state.json`'s actual enforcement logic (which keys off real sends).
Any future coincidental overlap between an AX2026 show and a live pipeline
pick — like Kagurabachi above — is not a conflict; it only becomes a
conflict if the *live* pipeline itself already covered that exact show
within the real cooldown window.

## What this file does NOT do

- Does not delete, modify, or resend any of the 43 packages or their
  original 2026-07-04 emails.
- Does not change `sent_scripts_log.json`, `sent_scripts_events.jsonl`,
  `blackout_state.json`, or any other prior tracking doc for this batch.
- Does not mark these packages as available for reuse, further correction,
  or re-dispatch. Any future action on these specific shows requires a new,
  explicit decision at that time, evaluated against the real (non-AX2026)
  send history.
- Does not affect or gate the 2026-08-08 daily_combined run, which proceeds
  independently using genuinely new research and genuinely new candidate
  selection.

Filed: 2026-08-07

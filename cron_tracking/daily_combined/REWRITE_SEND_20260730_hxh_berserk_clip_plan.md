# Rewrite send record — Hunter x Hunter / Berserk clip-plan correction (2026-07-30)

## Status

This round corrects the clip plan `season`/`episode` tags for the same daily_combined
batch originally sent 2026-07-29 for Hunter x Hunter (morning) and Berserk (evening).
Two distinct findings prompted this round:

1. **Dropped tags.** The original 2026-07-29 send's clip plan included season/episode
   tags on every cut. The later 2026-07-30 VO-only fact-verification resend (see
   `REWRITE_SEND_20260730_hxh_berserk.md`) inadvertently dropped those tags from the
   emailed clip plan. This round restores them for both shows.
2. **Berserk Cut 3 citation defect (new finding, filed as F24).** A user-initiated
   spot-check of Berserk Cut 3 found it cited `season 1, episode 5` ("Tower of
   Conviction"), sourced to the CBR chronological adaptation guide. Direct re-fetch of
   that source confirmed it supports only an arc-level claim (the 2016 series' first
   season broadly involves Guts fighting Apostles) with no episode number stated
   anywhere on the page. Independent lookup of the real S1E5
   ([IMDb](https://www.imdb.com/title/tt5904592/)) confirmed its actual plot (Guts
   searching for Casca, meeting Isidro) does not depict the claimed beat (Guts
   confronting Griffith-affiliated forces) at all. A second, compounding defect was
   also found: the same package's Cut 1 uses `season: 1` to mean the 1997 TV series,
   while Cuts 2/4/5 (and the erroneous Cut 3) use `season: 1`/`season: 2` to mean the
   separate 2016 TV series — an undifferentiated `season` integer silently conflating
   two distinct productions. The corrected citation for Cut 3 is 2016 series S1E8
   ("Reunion in the Den of Evil," [Berserk Wiki](https://berserk.fandom.com/wiki/Episode_8_(2016_Anime))),
   a confirmed, specific scene of Guts fighting an Apostle (the Great Goat) while Holy
   Iron Chain Knights close in, during the Conviction arc — the closest
   concretely-sourced match to the claimed beat, though the source does not explicitly
   confirm this Apostle is God-Hand/Griffith-directed. Both findings are documented in
   full in `docs/KNOWN_ISSUES.md` F24 (commit `35d3f92`), cross-referenced to F20.

Per the user's explicit direction, production labels ("1997 series" / "2016 series")
are now included inline on every cut in both emails, as a direct fix for the root
cause of the Cut 3 defect (not merely a formatting preference) — this prevents the
same season-number collision from recurring for any franchise with multiple distinct
TV productions.

No VO, hook, caption, title, or any other package content was changed in this round —
only the clip-plan season/episode/production tags.

## Packages corrected this round

| Show | Slot | batch_id | package_id | What changed |
|---|---|---|---|---|
| Hunter x Hunter | morning | ac60c0a6-a81b-4033-ba5f-a431fa98b10d | d1a7c8e2-4f3b-4a9e-8c1d-5e6f7a8b9c0d | Clip plan season/episode tags restored (dropped in the 2026-07-30 VO-only resend); production label "2011 series" added inline to every cut for consistency. No factual correction needed — all five citations confirmed accurate. |
| Berserk | evening | ac60c0a6-a81b-4033-ba5f-a431fa98b10d | f2b8d9e3-5a4c-4b0f-9d2e-6f7a8b9c0d1e | Clip plan season/episode tags restored, INCLUDING a factual fix to Cut 3 (season 1/episode 5 → 2016 series S1E8, corrected citation); production labels ("1997 series" / "2016 series") added inline to every cut to resolve the season-number conflation that caused the Cut 3 defect. |

Both packages share `batch_id ac60c0a6-a81b-4033-ba5f-a431fa98b10d` and `post_date
2026-07-30` — this is the original daily_combined batch's clip plan being corrected in
place via a standalone email, not a new batch and not a manifest field edit in this
round.

### Corrected clip plan — Hunter x Hunter (morning)

| Cut | Time | Scene | Production/S-E |
|---|---|---|---|
| 1 | 0:00–0:06 | Gon and Killua meeting at the Hunter Exam | 2011 series, S1E1 |
| 2 | 0:06–0:12 | Kurapika/Phantom Troupe confrontation, Yorknew City arc | 2011 series, S1E37 |
| 3 | 0:12–0:18 | Chimera Ant arc, Meruem and the Royal Guard | 2011 series, S1E76 |
| 4 | 0:18–0:24 | 13th Hunter Chairman Election arc, final anime episodes | 2011 series, S1E137 |
| 5 | 0:24–0:30 | Gon/Ging reunion tease at the World Tree, final anime scene | 2011 series, S1E148 |

### Corrected clip plan — Berserk (evening)

| Cut | Time | Scene | Production/S-E |
|---|---|---|---|
| 1 | 0:00–0:06 | Griffith's Eclipse transformation into Femto, Golden Age Arc | 1997 series, S1E25 — [CBR](https://www.cbr.com/berserk-every-anime-adaptation-chronological-order/) |
| 2 | 0:06–0:12 | Griffith leading the Band of the Falcon as Falconia's ruler | 2016 series, S2E1 — [Wikipedia](https://en.wikipedia.org/wiki/Berserk_(2016_TV_series)) |
| 3 | 0:12–0:18 | Guts confronting Griffith-affiliated forces, Conviction arc | **2016 series, S1E8** (corrected from a prior, incorrect S1E5 citation) — [Berserk Wiki Episode 8](https://berserk.fandom.com/wiki/Episode_8_(2016_Anime)), cross-checked against [IMDb S1E5 "Tower of Conviction"](https://www.imdb.com/title/tt5904592/) which disconfirms the old citation |
| 4 | 0:18–0:24 | Casca's Brand of Sacrifice reaction near Griffith, Millennium Falcon arc | 2016 series, S2E8 — [Wikipedia](https://en.wikipedia.org/wiki/Berserk_(2016_TV_series)) |
| 5 | 0:24–0:30 | Griffith alone on the Falconia balcony, arc finale | 2016 series, S2E12 — [Wikipedia](https://en.wikipedia.org/wiki/Berserk_(2016_TV_series)) |

## Why `append_send_batch.py` is not being run

Same dedup-key reasoning established in prior rounds (see
`REWRITE_SEND_20260727_batch_v3.md`, `REWRITE_SEND_20260730_hxh_berserk.md`):
`tools/append_send_batch.py`'s dedup key is `(batch_id, package_id)` only.

Both `d1a7c8e2-...` and `f2b8d9e3-...` already carry a `"status": "sent"` row in
`sent_scripts_log.json` under the original batch_id `ac60c0a6-...` from
2026-07-29T18:56:00-04:00. Re-running the logger against this same `(batch_id,
package_id)` pair would be a silent no-op (`events_appended: 0`). This markdown file
is the record instead. The original `sent_scripts_log.json` /
`sent_scripts_events.jsonl` entries for these two package_ids are NOT modified,
duplicated, or appended to.

## New finding filed

`docs/KNOWN_ISSUES.md` F24 (commit `35d3f92`): `clip_locate` can assert
season/episode-level precision beyond what its cited `verification_source_url`
actually supports, and separately can conflate distinct TV productions under a bare
`season` integer. Cross-referenced to F20 as the inverse failure mode. Status: OPEN —
documented tonight, not fixed; the specific Berserk Cut 3 instance was corrected via
this standalone email, not a validator or schema change.

## Sends and mailbox verification

Both sent to `hero_or_villain@outlook.com` only. Verified via a direct `search_email`
query immediately after sending, filtered to the exact subject strings.

| Show | Subject | Sent (per Outlook, UTC) | Mailbox copies found |
|---|---|---|---|
| Hunter x Hunter | `CLIP PLAN CORRECTION \| MORNING \| Hunter x Hunter \| originally sent 2026-07-29 \| Griffith Didn't Become a God` | 2026-07-31T01:59:50Z and 2026-07-31T01:59:46Z | **2** — confirmed via direct `search_email`, two distinct `email_id`s under this exact subject. |
| Berserk | `CLIP PLAN CORRECTION \| EVENING \| Berserk \| originally sent 2026-07-29 \| Griffith Didn't Become a God` | 2026-07-31T02:00:04Z and 2026-07-31T02:00:01Z | **2** — confirmed via direct `search_email`, two distinct `email_id`s under this exact subject. |

**F21 duplicate-dispatch defect observed on BOTH sends tonight.** One `send_email`
tool call was made for each show; each produced two mailbox-side copies with distinct
`email_id`s, 3-4 seconds apart, both from `hero_or_villain@outlook.com` to
`hero_or_villain@outlook.com`, both carrying the exact corrected content approved by
the user. This matches the known connector-side duplicate-dispatch pattern referenced
in `docs/KNOWN_ISSUES.md` (F21) and observed in the prior round's tracking doc
(`REWRITE_SEND_20260730_hxh_berserk.md`) — not a new defect, and not evidence of a
second distinct send action on this side. No emails were sent to any address other
than `hero_or_villain@outlook.com`.

## Filed

Date: 2026-07-31T02:00:04Z (UTC) — set to the latest of the confirmed send timestamps
above.

# VO Fact Package — Replacement Evening Candidate (post_date 2026-08-24)

**Replaces:** batch `da1a6d5f`'s evening Skeleton Knight package (dropped per Sebastian's direction — see KNOWN_ISSUES F67. That send record stays untouched/unlogged as-is; this is a net-new package, not a correction.)

**package_id:** `a7e8e502-ae71-469e-a675-005049e8a78e`
**post_date:** 2026-08-24 (Monday)
**show:** Dandadan
**format_type:** EPISODE_MOMENT (cliffhanger/anticipation angle — chapter 245 itself has not released or leaked as of this fact package; see Verification Notes)
**vo_status:** pending — Sebastian writes the VO
**topic_class:** timely (manga chapter releases day-of-post, weekly Shonen Jump schedule)

---

## Double-Method Conflict Check — CLEAR

- **Method 1 (manual grep):** Searched `sent_scripts_log.json` (222 flat entries, full channel history) for "Dandadan" / "Dan Da Dan" — **zero matches.** Show has never been covered.
- **Method 2 (mechanical):** Ran the repo's own `tools/conflict_check.py::check_recent_send_conflict()` against `sent_scripts_events.jsonl` (78 rows) with candidate `{show: "Dandadan", format_type: "EPISODE_MOMENT", post_date: "2026-08-24"}`. Result: `{"blocked": false, "reason": null, "matched_batch_id": null, "signal": null}`.
- **Same-day check:** Morning slot for 2026-08-24 is One Piece Ch. 1191 (unchanged, batch `da1a6d5f`) — different show, no conflict.
- **Blackout list cross-check (shows sent 8/10–8/23):** Dandadan not present.

Both methods agree independently: **clear, no conflict.**

---

## Core Claims (with independent, dated, non-fandom sources)

1. **Dandadan Chapter 245 is expected to release Monday, August 24, 2026** on its regular weekly schedule (Shueisha Manga Plus / Viz Media).
   - Source: [AOL — "Dandadan Chapter 245: Release date and everything we need to know"](https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html) (published 2026-08-18/19)
   - Source: [otakuontheway.com — "Dandadan Chapter 245 Release Date, Spoilers, Recap and What Happens Next"](https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/) (published 2026-08-19)
   - Both explicitly state this is the *expected* date based on the manga's regular weekly cadence, not an official Shueisha announcement of that specific date — standard caveat both articles carry, consistent with how weekly Shonen Jump titles are covered.

2. **Chapter 244's ending (confirmed, not speculative) — the cliffhanger this candidate's hook is built on:**
   - Momo and Okarun's battle against the Dragon Knights continues; Okarun surrenders after being overwhelmed.
   - The Dragon Knights test him with the "Acura Blade," which fails to extract Turbo Granny's powers from him — they don't believe he's really lost them.
   - Hase takes Momo hostage and threatens to kiss her to psychologically break Okarun.
   - Before Hase can go further, **Kinta arrives** aboard a nanoskin vehicle/battle-cart with allies Bamora, Mantisian, Chiquitita, and Rokuro Serpo, declaring he's come to rescue Momo and Okarun.
   - Sources: [AOL](https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html), [otakuontheway.com](https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/) — both agree on this recap independently. Cross-checked against a third, independent source: [Reddit r/Dandadan "Let's talk about Chapter 244"](https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/) (posted 2026-08-18), which confirms the same beats (Okarun's surrender, Hase taking Momo hostage, Kinta's cart arrival with the same named allies) from a fan-recap angle, independently corroborating the two news-article sources.

3. **No confirmed Chapter 245 plot content exists yet as of this fact package (Aug 23 evening).** Both primary sources explicitly separate their "confirmed" release-date section from a clearly labeled "speculation" section about what might happen next (Kinta vs. Hase confrontation, whether Okarun secretly retains power). I checked directly for any leak/early release that would change this: a "Chapter 245" page on a scan-aggregator site (Kayn Scan / Mgeko) resolved to nothing but a login/registration screen — not real chapter content — confirming no leak is circulating. This candidate is built entirely on the confirmed Ch. 244 cliffhanger + confirmed Ch. 245 release date, not on any invented or speculative plot content.

---

## Suggested Angle for Sebastian's VO

Anticipation/cliffhanger format, not a spoiler-reveal: frame around the fact that Ch. 244 ended with Okarun defeated, Momo held hostage, and Hase seconds from a forced kiss — right when Kinta crashed in with a jury-rigged battle-cart to save them both — and Chapter 245 (dropping the same day this posts) picks up exactly there. This avoids asserting anything about 245's actual content while still being a same-day-relevant hook tied to a real release date.

**Note on format_type:** Tagged EPISODE_MOMENT since the hook is a specific narrative beat (Kinta's rescue arrival) rather than a ranking/list. If Sebastian prefers, this could also work as a straight "recap + what's coming" angle — his call once he writes the VO.

---

## Sources (full list)

- [AOL — Dandadan Chapter 245: Release date and everything we need to know](https://www.aol.com/articles/dandadan-chapter-245-release-date-153000000.html)
- [otakuontheway.com — Dandadan Chapter 245 Release Date, Spoilers, Recap and What Happens Next](https://otakuontheway.com/dandadan-chapter-245-release-date-spoilers-recap-and-what-happens-next/)
- [Reddit r/Dandadan — "Let's talk about Chapter 244"](https://www.reddit.com/r/Dandadan/comments/1vruaa3/lets_talk_about_chapter_244/)

Explicitly avoided as sources: fandom.com wikis, Amino-style fan wikis (per standing rule).

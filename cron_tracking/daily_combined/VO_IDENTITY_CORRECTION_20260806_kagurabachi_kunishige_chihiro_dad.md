# VO identity correction record — Kagurabachi (Kunishige = Chihiro's dad) — 2026-08-06

## Status

This is the tracking record for the "VO IDENTITY CORRECTION" of the
Kagurabachi morning package (`batch_id
8c737fff-f523-4b00-896a-4e2fc8a40152`, `package_id
fc92f1fc-de9d-4829-9f5c-7bf144f99fa3`, originally sent
2026-08-06T18:45:00Z, for post_date 2026-08-07). This is the first
correction round for this package_id.

**SENT.** Correction email confirmed sent 2026-08-06T21:20:59Z (5:20 PM
ET) to hero_or_villain@outlook.com. Mailbox-verified via `search_email`
— see Send section below for full confirmation, including a disclosed
F21 duplicate-dispatch occurrence on this send.

## What triggered this round

Sebastian flagged a real, serious clarity problem in the already-sent VO:
the character named "Kunishige" is introduced in sentence 2 with no
established link back to "Chihiro's dad" (the subject named in the hook,
sentence 1). A cold viewer unfamiliar with the cast has no way to know
whether Kunishige IS Chihiro's dad, or a separate person.

Tracing the pronoun chain in the original VO confirmed the bug is real and
worse than a naming gap — it also creates a false referent collision:

> "Chihiro's dad is the legendary swordsmith Kagurabachi fans call a
> hero... His drunk father beat them both, so when he died, Kunishige
> remembers her looking relieved, not sad."

Here "His"/"he died" grammatically refers to Chihiro's dad's own father
(a distinct, unnamed grandfather-generation figure), and then "Kunishige"
is introduced immediately afterward with zero anchor to either "Chihiro's
dad" or the father just mentioned. The story is unfollowable for anyone
who doesn't already know from outside context that Kunishige is Chihiro's
father.

## Fields corrected this round — Kagurabachi (morning)

| Field | Before | After |
|---|---|---|
| `opening_sentence` / `hook_line` | "Chihiro's dad is the legendary swordsmith Kagurabachi fans call a hero, but chapter 126 reveals a tragic childhood." | "Chihiro's dad, Kunishige, is the legendary swordsmith Kagurabachi fans call a hero, but chapter 126 reveals a tragic childhood." |
| `hook_candidates[0]` | (same as old hook_line) | (same as new hook_line, kept in sync per `selected_hook_index: 0`) |
| `vo` | 107-word version with the unanchored "Kunishige" reference (full text below) | 108-word version with the name anchored in sentence 1 and the pronoun chain re-tightened in sentence 2 (full text below) |
| `vo_word_count` | 107 | 108 |
| `isolation_test_note` | Original PASS note (still valid in substance) | Re-verified PASS note, appended with a dated correction note explaining the appositive addition doesn't change what the hook promises |

**Fields reviewed and confirmed NOT needing a fix:**
- `question_line` ("Does this change how you see his dad?") and `cta_line`
  ("Leave your take.") — unchanged, both still resolve correctly since
  "his dad" now clearly traces back to Kunishige.
- `captions`, `clip_descriptions`, `pinned_comment`, `youtube_title`,
  `tiktok_title` — all already referred to "Kunishige" only in contexts
  where the name is not the first introduction (e.g. clip_descriptions
  labels frames, it doesn't narrate the story cold), so none carried the
  ambiguity. Checked individually, no edits needed.
- `semantic_qa.claim_source_matrix` — the hook-anchored claim was already
  stored correctly as "Kunishige Rokuhira is Chihiro's father and the
  legendary swordsmith fans regard as a hero" with its two sources
  (YouTube panel read + Kagurabachi Fandom wiki). The underlying sourcing
  was correct all along; only the spoken VO prose failed to make the
  identification explicit to a cold viewer. `source_urls` and
  `verbatim_quote` unchanged.

## Original (buggy) VO — full text, 107 words

"Chihiro's dad is the legendary swordsmith Kagurabachi fans call a hero,
but chapter 126 reveals a tragic childhood. His drunk father beat them
both, so when he died, Kunishige remembers her looking relieved, not sad.
The abuse had broken her, and she grabbed at his eyes, and he cried out
that she was hurting him, the same eyes he inherited from his father. She
later left an apology note and took her own life. Kunishige isolated
himself for years until Chiaki stood in the rain and cooked him a meal.
He cried at the first bite. Does this change how you see his dad? Leave
your take."

## Corrected VO — full text, 108 words

"Chihiro's dad, Kunishige, is the legendary swordsmith Kagurabachi fans
call a hero, but chapter 126 reveals a tragic childhood. His drunk father
beat him and his mother, and when he died, Kunishige remembers her
looking relieved, not sad. The abuse had broken her, and she grabbed at
his eyes while he cried out that she was hurting him, the same eyes he
inherited from his father. She later left an apology note and took her
own life. Kunishige isolated himself until Chiaki stood in the rain and
cooked him a meal. He cried at the first bite. Does this change how you
see his dad? Leave your take."

## Rewrite process

Three options were drafted, each anchoring "Kunishige" to "Chihiro's dad"
in the opening sentence. All three initially ran over the 100-108 word
cap (110-117 words) once the name-anchor words were added, requiring
several trim passes on connective tissue in sentence 2 (tightening
"beat them both, so when he died" -> "beat him and his mother, and when
he died"; merging two "and"-clauses into one "while"-clause in the
abuse/eyes sentence; dropping the filler "for years" from "isolated
himself for years until") without cutting any sourced/verified claim.

Two options reached the required word band at exactly 108 words:

- **Option A:** "Chihiro's dad, Kunishige, is the legendary swordsmith..."
- **Option B:** "Kunishige, Chihiro's dad, is the legendary swordsmith..."

Both were shown to Sebastian in full, with independently re-verified
regex word counts, before any file was edited. **Sebastian selected
Option A.**

## Pronoun-chain re-verification (full VO, sentence by sentence)

1. "Chihiro's dad, Kunishige, is the legendary swordsmith..." —
   **Kunishige = Chihiro's dad**, established via appositive at first
   use. No ambiguity.
2. "His drunk father beat him and his mother, and when he died, Kunishige
   remembers her looking relieved, not sad." — "His" = Kunishige
   (nearest antecedent, subject of sentence 1). "father" = a new,
   distinct figure (Kunishige's own father, i.e. Chihiro's grandfather),
   correctly disambiguated because Kunishige now has a name distinct from
   "father." "him and his mother" = Kunishige and Kunishige's mother.
   "when he died" = the father (nearest antecedent). "Kunishige remembers
   her" = clean, named reference. "her" = his mother, now established.
   No collision with sentence 1's "Kunishige."
3. "The abuse had broken her, and she grabbed at his eyes while he cried
   out that she was hurting him, the same eyes he inherited from his
   father." — "her"/"she" = mother throughout. "his eyes"/"he cried
   out"/"him" = Kunishige throughout. "his father" = the same
   grandfather-generation figure from sentence 2. Consistent, no new
   ambiguity.
4. "She later left an apology note and took her own life." — "She" =
   mother. Clean.
5. "Kunishige isolated himself until Chiaki stood in the rain and cooked
   him a meal." — "Kunishige" named directly. "him" = Kunishige. Clean.
6. "He cried at the first bite." — "He" = Kunishige. Clean.
7. "Does this change how you see his dad?" — "his dad" now clearly
   resolves to Kunishige, and Kunishige was established in sentence 1 as
   Chihiro's dad. The question closes the loop the original VO opened
   with in the hook.
8. "Leave your take." — CTA, unchanged.

Every pronoun resolves to exactly one antecedent throughout the corrected
VO. No generational ambiguity remains.

## Isolation Test re-verification (Law #144.1)

- **Onscreen text (unchanged):** "His hero dad's past just got dark"
- **New hook_line:** "Chihiro's dad, Kunishige, is the legendary
  swordsmith Kagurabachi fans call a hero, but chapter 126 reveals a
  tragic childhood."
- Isolated from the rest of the VO, the hook promises only that a
  revered "hero dad" figure (now named Kunishige) has a dark/tragic
  revealed past — no specific act, direction, or outcome is implied.
  Adding "Kunishige" as an appositive is an identity label, not a new
  plot claim, so it does not raise or lower what the hook promises
  relative to the original hook wording.
- The VO still delivers exactly this: an abusive father, the mother's
  death, a traumatic incident involving his eyes, the mother's suicide,
  Kunishige's isolation, and reconciliation with Chiaki — all consistent
  with "a dark/tragic past," no specific detail oversold by the hook.
- **RESULT: PASS.**

This is treated as a structural re-verification, not a wording-only
check, per Sebastian's explicit instruction, because the hook_line itself
changed (name added), not just surrounding VO prose.

## Word count re-verification

Independently re-computed via the same regex tokenizer the validator uses
(`len(re.findall(r"[\w']+", text))`):

- Original VO: 107 words (confirmed, matches original `vo_word_count`).
- Corrected VO (Option A, selected): **108 words**, computed independently
  twice (once during option drafting, once again immediately before
  finalizing) — both runs agree.

## Validator

Ran `python3 validators/validate_dual_package.py
cron_tracking/daily_combined/run_manifest.json` against the full
two-package manifest (Kagurabachi morning corrected, Gachiakuta evening
untouched) on 2026-08-06:

**RESULT: PASS — cleared to send both emails.** All checks green for both
packages, including `[morning] vo_word_count matches VO text`,
`[morning] VO within 100-108 words`, `[morning] opening_sentence is the
VO's exact first sentence`, `[morning] hook_line equals opening_sentence`,
and `[morning] isolation_test_pass attested true (Law #144.1)`.

The live rolling `run_manifest.json` still correctly contains this
batch (`batch_id 8c737fff-f523-4b00-896a-4e2fc8a40152`) — unlike the F31
gap documented for the Tanya S2 Ep4 correction, no manifest-loss recovery
was needed here.

## Original sent-log entry — left untouched, by design

`sent_scripts_log.json` and `cron_tracking/sent_scripts_events.jsonl`
retain their original entries for this package_id
(`fc92f1fc-de9d-4829-9f5c-7bf144f99fa3`) exactly as they were at the time
of the original 2026-08-06T18:45:00Z send (`vo_word_count: 107`, old
`hook_line`, old `vo` text unchanged). This is intentional: those logs
are a historical record of what was actually sent at that time, not a
live/current-state field. `tools/append_send_batch.py` is not used for
this correction, since it is designed to log a new original send, not
amend a package_id that already has a real "sent" row — using it here
would either create a confusing duplicate entry or require unsafely
mutating history. This markdown tracking record is the correction-of-record
instead, following the same convention used by
`HOOK_CORRECTION_20260806_tanya_s2ep4_real_fight_promise.md` earlier
tonight.

## Send

**Sent:** 2026-08-06T21:20:59Z (5:20 PM ET), via the Outlook connector
`send_email` tool. Only one `send_email` tool call was made for this
package.

- **Subject:** `CORRECTION | Kagurabachi | 2026-08-07 | Kagurabachi Ch. 126: Chihiro's Dad's Dark Past`
- **Recipient:** hero_or_villain@outlook.com (only)
- **From:** hero_or_villain@outlook.com
- **Body:** full disclosed-correction pattern — correction notice, what
  was wrong, what changed, full corrected 108-word VO, hook, clip plan,
  captions, titles, TikTok post text, pinned comment, post times, 7
  dated sources, validator result. Matches the drafted/approved text
  exactly, byte-for-byte, as returned by the send tool.

**Mailbox verification (real `search_email` results):** searched the
mailbox directly after sending. Found **2 distinct email objects**, both
with this exact subject and byte-identical body, in the same thread:

| # | Timestamp (UTC) | Full `email_id` (tail) |
|---|---|---|
| 1 | 2026-08-06T21:20:56Z | `...AAAIBCQAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkPNKAAAA` |
| 2 | 2026-08-06T21:20:59Z | `...AAAIBDAAAAN2_6LTid3pLrJ8ttdD6ck4AAABAkMhKAAAA` |

Two distinct full `email_id` values confirmed, ~3 seconds apart, same
thread — this is a **genuine F21 duplicate-dispatch** (the Outlook
connector's known intermittent one-call-becomes-two-mailbox-sends defect;
see `docs/KNOWN_ISSUES.md` F21). Only one `send_email` tool call was made
(confirmed via this turn's tool-call history), so this is a
connector/transport-side duplication, not an agent-side resend. Logged as
a new row in the F21 table in `docs/KNOWN_ISSUES.md` (table now 17 rows,
15 tagged Genuine duplicate), following the exact same format as every
prior confirmed F21 instance tonight and in prior sessions.

**Logging:** per explicit user instruction, `tools/append_send_batch.py`
was **NOT** re-run for this send — `package_id fc92f1fc-de9d-4829-9f5c-7bf144f99fa3`
already has a real `sent` row from the original 2026-08-06T18:45:00Z send.
This dated tracking document is the correction-of-record for this round,
following the same convention as
`HOOK_CORRECTION_20260806_tanya_s2ep4_real_fight_promise.md`. The mailbox-side
F21 duplication does not affect the `(batch_id, package_id)` dedup key used
by the durable send logs.

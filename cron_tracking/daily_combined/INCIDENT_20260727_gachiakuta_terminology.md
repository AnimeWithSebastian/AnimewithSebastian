# Incident — Fabricated ability terminology shipped in sent VO — Gachiakuta, MORNING slot, post_date 2026-07-27

## Status: SHIPPED. Email already sent. NOT corrected retroactively per standing rule
against rewriting historical records (this is a new incident record about the send,
not a retroactive edit to the send itself).

## What happened

The MORNING package for post_date 2026-07-27 (batch_id
05138946-731b-482c-bb1b-5533c17e062b, package_id
f967a456-6831-404d-934f-173c7fc4e3f2, show: Gachiakuta) contains this line in the sent
VO, and in `sent_scripts_log.json`:

> "So the story hands him actual garbage as his only weapon, scrap turned into gear
> through his Trash Cleaner ability. That is the entire point of the show."

**"Trash Cleaner" is not a real Gachiakuta term.** It does not appear anywhere in the
source material. Independently verified via Wikipedia and confirmed via broader source
sweep (TV Tropes, Fandom wiki, CBR, Gosu, Boomzappow, GachiakutaMerch, Sportskeeda — 7
sources total, cross-checked directly, not re-trusted from the manifest's own
description of them):

- Rudo's actual power framework is the **Vital Instrument** (人器, *Jinki*) system: an
  everyday object infused with Anima from a **Giver**'s (人通者, *Gibā*) own attachment
  to it, which awakens and turns it into a weapon effective against Trash Beasts.
- Rudo's specific Vital Instrument is his gloves, referred to as **"3R."**
- "Trash Cleaner" appears to be a fabricated conflation of two real-but-different
  terms: **"The Cleaners"** (an organization in the series) and **"Trash Raider"**
  (Rudo's crime label/accusation) — neither of which is the name of the ability itself.

This is not a minor label mismatch — it is the VO's central claim ("That is the entire
point of the show") resting on an invented mechanism name.

**Additional finding on the specific cited source (confirmed 2026-07-26):** the claim's
sole cited source, `wherever-i-look.com/tv-shows/anime/gachiakuta-season-1-episode-1-recap-and-review`,
was independently fetched and read directly. That page does **not** contain the term
"Trash Cleaner" anywhere. It contains the unrelated term **"Trash Raider"** — Rudo's
crime label, not an ability name — which appears to be the actual origin of the
fabrication: the source's real term was misread or conflated into a different,
invented ability name at drafting time, and that invented name was then cited back to
a source that never said it. This is a stronger, more specific finding than "the source
was trusted without being opened" — the source WAS available to open, and reading it
would have shown the exact word it actually contains has nothing to do with the claim
it was attached to support.

## Why it wasn't caught before send

The Gachiakuta package went through a real rewrite cycle earlier in this session after
an unrelated claim (a ranking claim) was flagged as unsupported and rejected, requiring
a full redraft with newly verified sources before approval. That redraft, and the
approval that followed it, checked that the *replacement* sources supported the
*replacement* claims they were attached to — but did not re-open and independently
re-verify the ability-name claim itself, which had carried over unchanged from the
original draft. The approval trusted that a claim already sitting in the manifest with
a source URL attached was sound, rather than independently confirming the source
actually said what the claim said. That is exactly the gap Law #152 rule 2(c) exists to
close, and it is exactly what caught this: applying that rule for real, after the fact,
during Law #152 compliance work on the manual-build script, surfaced the error.

**Root cause, stated plainly:** a source was cited and its description trusted, without
the source itself being opened and read at citation time. The URL was present and
looked legitimate; nobody who approved the claim actually loaded the page and checked
that its content matched the claim attached to it.

**This means the first approval pass on this package did not satisfy Law #152 rule
2(c)**, even informally — it is being recorded honestly as incomplete, not merged into
a single "audit happened" claim alongside the follow-up check that actually caught the
problem.

## Disposition

- Historical record NOT rewritten: the sent email, `sent_scripts_log.json`, and
  `run_manifest.json` for this batch stand as actually sent, per standing rule against
  retroactively rewriting historical records except for genuine self-referential
  errors in the record-keeping itself (this is a content error in the shipped script,
  not an error in how the send was logged).
- This incident file is the disclosure of that content error, filed the same way
  `BLOCKER_20260726.md` disclosed a process blocker — as a permanent, undeleted record.
- No corrective action (correction video, pinned comment edit, etc.) has been taken yet.
  That is a decision for Sebastian, not something to self-authorize.

## Verification trail (independent, this session)

- Wikipedia (`en.wikipedia.org/wiki/Gachiakuta`) fetched directly and read for the
  Vital Instrument / Jinki / Giver terminology — see citation in the response to
  Sebastian in this session, dated 2026-07-26.
- Cross-referenced against TV Tropes, Fandom wiki, CBR, Gosu, Boomzappow,
  GachiakutaMerch, and Sportskeeda (7 sources) per the initial finding that prompted
  this file.

## Filed

Date: 2026-07-26 (discovered during Law #152 compliance work on
`build_2026-07-27_manual_batch.py`, applied to the already-sent 2026-07-27 batch)

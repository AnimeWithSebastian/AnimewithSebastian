# Law #83 — Morning Slot Reservation + Cross-Slot Conflict Check

> **SUPERSEDED / INERT as of 2026-07-15 — marker added 2026-08-15 during a law audit.
> Original text below preserved unchanged.**
>
> **The mechanism this law exists to protect no longer exists.** Law #83 solves a race
> between TWO simultaneously-firing crons: the morning cron writes a `RESERVED` entry so
> the evening cron can pull it and pick a different show. **Law #139 (2026-07-15)
> collapsed both slots into ONE `daily_combined` run** that selects both ideas in a
> single model context — so there is no second cron to race with, and nothing to reserve
> against. The morning cron `d43ab889` named in the header line below, and the evening
> cron `57a3c92e` this law deconflicts against, are both retired.
>
> **DO NOT execute the STEP 1 / STEP 4B Python below.** Beyond being unnecessary, it
> writes to `/home/user/workspace/sent_scripts_log.json` — a path that does not exist in
> this repo-based layout (see the workspace-path note further down) — and it appends
> `status: "reserved"` rows to the live send log, which the weekly analytics cron reads.
>
> **What still applies, and where it lives now:** the *same-day same-show ban* and the
> cross-slot diversity requirement this law protected are preserved in Law #139 §4 and
> enforced by `validators/validate_dual_package.py`'s distinct-shows / distinct-formats
> checks — a package pair that repeats a show now fails validation outright, which is a
> stronger guarantee than the reservation handshake ever provided.
>
> Kept rather than deleted for the historical record and because the reasoning still
> documents *why* same-day duplication is unacceptable.

**Status:** ~~ACTIVE~~ **SUPERSEDED by Law #139 (2026-07-15)** — see banner above.
**Added:** June 2026
**Applies to:** ~~Morning cron runtime (d43ab889) — STEP 1~~ — retired cron; no current
runtime executes this law. [Cron ID and applicability corrected 2026-08-15.]

## Rule

The morning and evening crons fire simultaneously every night. Without a reservation system, both slots can select the same show — producing duplicate content on the same date.

**Morning cron MUST write a RESERVATION entry to sent_scripts_log.json immediately at STEP 1 — before any research begins.**

Evening cron MUST pull fresh from GitHub before finalizing show selection to see the morning reservation.

## Morning Reservation — STEP 1 Code

Run immediately after reading sent_scripts_log.json:

```python
import json, datetime
log = json.load(open('/home/user/workspace/sent_scripts_log.json'))
today = datetime.date.today().isoformat()
existing = [e for e in log if e.get('date_sent')==today and e.get('slot')=='morning']
if not existing:
    log.append({
        'date_sent': today,
        'slot': 'morning',
        'show': 'RESERVED',
        'status': 'reserved',
        'notes': 'Morning cron reservation — show TBD. Blocks evening duplicate.'
    })
    json.dump(log, open('/home/user/workspace/sent_scripts_log.json','w'), indent=2)
    print('RESERVED')
else:
    print('ALREADY EXISTS')
```

Then push to GitHub immediately so evening cron can see it.

## Update Reservation After Show Selection (STEP 4B)

After show is confirmed by research, update the RESERVED entry with actual show name.
Push update to GitHub so evening cron sees the real show — not just RESERVED.

## Evening Cross-Slot Check

Before finalizing show selection:
1. Pull latest log from GitHub (morning may have just written its reservation)
2. Check for any entry where date_sent = TODAY and slot = "morning"
3. If morning entry has show = "RESERVED" — treat as unknown. Pick a different show as a precaution.
4. If morning entry has an actual show name — that show is BLOCKED for evening.
5. If conflict detected → discard that show, select next best candidate from research.

## Why This Exists

Both crons run the same night. Same show in both slots = duplicate content sent to user.
Morning writes first. Evening reads and deconflicts. This is the only reliable check.

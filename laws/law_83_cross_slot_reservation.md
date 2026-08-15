# Law #83 — Morning Slot Reservation + Cross-Slot Conflict Check

**Status:** ACTIVE
**Added:** June 2026
**Applies to:** Morning cron runtime (d43ab889) — STEP 1

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

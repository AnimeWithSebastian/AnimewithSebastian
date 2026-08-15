# Law #80 — Caption Text Block (Mandatory in Every Email Package)

**Status:** ACTIVE — June 28, 2026

## Rule
Every email package (morning and evening) MUST include a standalone CAPTION TEXT block.

## What It Is
The caption text block is the actual voiceover script broken out word-by-word, with orange highlight words marked inline, exactly as they will appear on screen in CapCut.

## What It Is NOT
- The caption SPEC (font/size/color settings) is a separate block and does NOT replace the caption text block
- The caption spec must still appear as its own block
- Both blocks are required in every email

## Format
```
CAPTION TEXT (word-by-word)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE [SHOW_NAME] [ORANGE]
IS [word] [word]
[ORANGE WORD] [ORANGE]
...
```

Orange highlight words are marked with [ORANGE] immediately after the word.

## Enforcement
- Applies to: ALL email packages — morning, evening, and any manual sends
- Cron must generate caption text block at STEP 11B alongside clip plan
- If caption text block is missing → email CANNOT be sent
- This is not optional based on format type — ALL 19 formats require it

## Origin
User flagged June 28, 2026: videos sent June 27 included caption spec but not caption text. Law created to prevent recurrence.

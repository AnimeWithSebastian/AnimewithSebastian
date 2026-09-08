"""render_emails.py -- renders BOTH packages of the SHARED top-level
cron_tracking/daily_combined/run_manifest.json into email text.

WARNING (added 2026-09-08 audit): this script always reads the shared
top-level manifest, by design -- it is NOT scoped to any specific batch.
If you're working on a specific batch that has its own
pending/<batch_id>/render_emails_scoped.py, use THAT script instead; running
this one by mistake will silently render whatever batch currently happens to
be at the top-level path, which may be unrelated to the batch you're actually
working on, and can overwrite email_morning.txt/email_evening.txt with the
wrong content. This already happened once for real (2026-09-02 session) when
this script was run by mistake and briefly overwrote an unrelated batch's
tracked email file before being caught and reverted.
"""
import json

m = json.load(open("cron_tracking/daily_combined/run_manifest.json"))
post_date = m["post_date"]

def render(pkg):
    slot = pkg["slot"].upper()
    subject = f"TOMORROW | {slot} | {pkg['show']} | {post_date} | {pkg['youtube_title']}"

    lines = []
    lines.append(f"━━━ {slot} — {post_date} ━━━")
    lines.append(f"SHOW:    {pkg['show']}")
    lines.append(f"ANGLE:   {pkg['angle']}")
    lines.append(f"FORMAT:  {pkg['format_type']}")
    lines.append("STYLE:   Face-Cam Split Screen  (Creator TOP / anime footage BOTTOM)")
    signals = pkg.get("topic_signals") or []
    sig_str = f" — signals: {'/'.join(signals)}" if signals else ""
    lines.append(f"TOPIC:   {pkg['topic_class']}{sig_str}")
    lines.append("SERIES:  one-off")
    fs = pkg["funnel_status"]
    lines.append(f"FUNNEL:  {fs}")
    if pkg.get("spoiler_warning"):
        # 2026-09-08 audit fix: this line was hardcoded to one specific past
        # batch (Slime S4E18, Aug 7 2026) and would have silently rendered
        # that same wrong show/episode/date into any future package's spoiler
        # warning. Several per-batch render_emails_scoped.py copies had
        # already independently worked around this by parameterizing or
        # genericizing it; fixed here at the shared source so future copies
        # don't inherit the stale hardcoded text again.
        lines.append(f"SPOILER WARNING: Yes — covers {pkg['show']} episode content")
    lines.append("")
    lines.append("━━━ FIRST-SECOND HOOK ━━━")
    lines.append(f"ON-SCREEN (second 1): {pkg['hook_onscreen_text']}")
    lines.append(f"SPOKEN (VO first line): {pkg['hook_line']}")
    lines.append(f"HOOK FAMILY: {pkg['hook_family']}")
    cands = pkg["hook_candidates"]
    sel = pkg["selected_hook_index"]
    lines.append(f"(candidate A: {cands[0]}")
    lines.append(f" candidate B: {cands[1]}")
    lines.append(f" SELECTED: {sel})")
    lines.append("")
    lines.append(f"━━━ VO ({pkg['vo_word_count']} words — fills the resolved {pkg['capcut_target_sec']}s CapCut edit) ━━━")
    lines.append(pkg["vo"])
    lines.append("")
    lines.append("━━━ PERFORMANCE SCRIPT (render-time-only view) ━━━")
    sentences = [s.strip() for s in pkg["vo"].split(". ") if s.strip()]
    perf_parts = []
    for i, s in enumerate(sentences):
        if not s.endswith((".", "?", "!")):
            s += "."
        tag = "[FACE: direct-to-camera, lean in]" if i == 0 else "[FACE: glance-down-at-footage]"
        perf_parts.append(f"{tag} {s}")
    lines.append(" ".join(perf_parts))
    lines.append("")
    lines.append("━━━ CLIP PLAN (face-cam split screen; per-cut timings) ━━━")
    for i, c in enumerate(pkg["clips"], 1):
        start = c["timeline_start_sec"]
        end = c["timeline_end_sec"]
        dur = c["duration_sec"]
        def fmt(t):
            return f"0:{t:02d}"
        label = f"CUT {i}" if i < len(pkg["clips"]) else f"CUT {i} (final)"
        lines.append(f"{label} — {dur} sec ({fmt(start)}–{fmt(end)}): {c['scene']} — {c['reason']}")
    lines.append(f"TOTAL CLIP TIME: {pkg['total_clip_time_sec']} seconds")
    lines.append("")
    lines.append("━━━ ON-SCREEN CAPTIONS ━━━")
    lines.append(pkg["captions"])
    lines.append("")
    lines.append("━━━ YOUTUBE TITLE ━━━")
    lines.append(pkg["youtube_title"])
    lines.append("")
    lines.append("━━━ TIKTOK TITLE ━━━")
    lines.append(pkg["tiktok_title"])
    lines.append("")
    lines.append("━━━ TIKTOK POST TEXT (caption) ━━━")
    lines.append(pkg["tiktok_post_text"])
    lines.append("")
    lines.append("━━━ PINNED COMMENT ━━━")
    lines.append(pkg["pinned_comment"])
    lines.append("")
    lines.append("━━━ RECOMMENDED POST TIME ━━━")
    lines.append(f"YouTube Shorts — post {pkg['post_times']['youtube']}")
    lines.append(f"TikTok — post {pkg['post_times']['tiktok']}")
    lines.append("")
    lines.append("━━━ SOURCES ━━━")
    for i, s in enumerate(pkg["sources"], 1):
        lines.append(f"{i}. {s['claim']} — {s['url']} ({s['date']})")
    lines.append("")
    lines.append(f"━━━ END {slot} ━━━")

    body = "\n".join(lines)
    return subject, body

for pkg in m["packages"]:
    subject, body = render(pkg)
    fname = f"cron_tracking/daily_combined/email_{pkg['slot']}.txt"
    with open(fname, "w") as f:
        f.write(f"SUBJECT: {subject}\n\n{body}")
    print("wrote", fname)
    print("SUBJECT:", subject)
    print("---")

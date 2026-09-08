import json

manifest = json.load(open("run_manifest.json"))
pm = [p for p in manifest["packages"] if p["slot"] == "morning"][0]
pe = [p for p in manifest["packages"] if p["slot"] == "evening"][0]


def render_email(pkg, post_date):
    slot = pkg["slot"].upper()
    lines = []
    lines.append(f"━━━ {slot} — {post_date} ━━━")
    lines.append(f"SHOW:    {pkg['show']}")
    lines.append(f"ANGLE:   {pkg['angle']}")
    lines.append(f"FORMAT:  {pkg['format_type']}")
    lines.append("STYLE:   Face-Cam Split Screen  (Creator TOP / anime footage BOTTOM — Law #134 Stage 2; manga panels allowed within the anime-footage half for manga-based formats)")
    topic_line = f"TOPIC:   {pkg['topic_class']}"
    if pkg["topic_class"] == "timely" and pkg.get("topic_signals"):
        topic_line += " — signals: " + "/".join(pkg["topic_signals"])
    lines.append(topic_line)
    lines.append("SERIES:  one-off")
    lines.append(f"FUNNEL:  {pkg['funnel_status']}")
    lines.append("")
    lines.append("━━━ FIRST-SECOND HOOK (Law #144 — on screen + spoken in second 1) ━━━")
    lines.append(f"ON-SCREEN (second 1): {pkg['hook_onscreen_text']}")
    lines.append(f"SPOKEN (VO first line): {pkg['hook_line']}")
    lines.append(f"HOOK FAMILY: {pkg['hook_family']}")
    lines.append("(Draft two hook candidates internally — Law #145 — publish ONLY the selected one:")
    lines.append(f"  candidate A: {pkg['hook_candidates'][0]}")
    lines.append(f"  candidate B: {pkg['hook_candidates'][1]}")
    lines.append(f"  SELECTED: {pkg['selected_hook_index']} — this is the published hook; the loser is not posted.)")
    lines.append("")
    lines.append(f"━━━ VO ({pkg['vo_word_count']} words — fills the resolved {pkg['capcut_target_sec']}s CapCut edit) ━━━")
    lines.append(pkg["vo"])
    lines.append("")
    lines.append("━━━ CLOSING LINE NOTE (Law #141 rescinded 2026-07-27) ━━━")
    lines.append(pkg.get("loop_transition_note", ""))
    lines.append("")
    lines.append("━━━ CLIP PLAN (face-cam split screen; per-cut timings REQUIRED — Law #140) ━━━")
    clips = pkg["clips"]
    for i, c in enumerate(clips):
        start_m, start_s = divmod(c["timeline_start_sec"], 60)
        end_m, end_s = divmod(c["timeline_end_sec"], 60)
        start_str = f"{start_m}:{start_s:02d}"
        end_str = f"{end_m}:{end_s:02d}"
        cut_label = f"CUT {i+1}" + (" (final)" if i == len(clips) - 1 else "")
        ref = ""
        if c.get("scene_verified"):
            cl = c.get("clip_locate", {})
            ref = f" (S {cl.get('season')} E{cl.get('episode')})"
        elif c.get("manga_reference"):
            ref = f" ({c['manga_reference']})"
        elif c.get("footage_status"):
            ref = f" ({c['footage_status']})"
        lines.append(f"{cut_label} — {c['duration_sec']} sec ({start_str}–{end_str}): {c['scene']}{ref} — {c['reason']}")
    lines.append(f"TOTAL CLIP TIME: {pkg['total_clip_time_sec']} seconds")
    lines.append("")
    lines.append("━━━ ON-SCREEN CAPTIONS ━━━")
    lines.append(pkg["captions"])
    lines.append("")
    lines.append("━━━ YOUTUBE TITLE (Law #144 — punchy, searchable) ━━━")
    lines.append(pkg["youtube_title"])
    lines.append("")
    lines.append("━━━ TIKTOK TITLE (Law #144 — punchy; distinct from the caption below) ━━━")
    lines.append(pkg["tiktok_title"])
    lines.append("")
    lines.append("━━━ TIKTOK POST TEXT (caption — may be longer; hashtags live HERE, not in the title) ━━━")
    lines.append(pkg["tiktok_post_text"])
    lines.append("")
    lines.append("━━━ PINNED COMMENT ━━━")
    lines.append(pkg["pinned_comment"])
    lines.append("")
    lines.append("━━━ RECOMMENDED POST TIME ━━━")
    lines.append(pkg['post_times']['youtube'])
    lines.append(pkg['post_times']['tiktok'])
    lines.append("")
    lines.append("━━━ SOURCES (concise evidence — >=2, each dated) ━━━")
    for i, s in enumerate(pkg["sources"], 1):
        lines.append(f"{i}. {s['claim']} — {s['url']} ({s['date']})")
    lines.append("")
    lines.append(f"━━━ END {slot} ━━━")
    return "\n".join(lines)


post_date = manifest["post_date"]

subject_morning = f"TOMORROW | MORNING | {pm['show']} | {post_date} | {pm['youtube_title']}"
subject_evening = f"TOMORROW | EVENING | {pe['show']} | {post_date} | {pe['youtube_title']}"

email_morning = f"Subject: {subject_morning}\n\n" + render_email(pm, post_date)
email_evening = f"Subject: {subject_evening}\n\n" + render_email(pe, post_date)

with open("email_morning.txt", "w") as f:
    f.write(email_morning + "\n")
with open("email_evening.txt", "w") as f:
    f.write(email_evening + "\n")

print("=== MORNING SUBJECT ===")
print(subject_morning)
print()
print("=== EVENING SUBJECT ===")
print(subject_evening)
print()
print("Morning email length (chars):", len(email_morning))
print("Evening email length (chars):", len(email_evening))

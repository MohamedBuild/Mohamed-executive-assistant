---
name: morning-brief
description: Generate the daily morning briefing from local task, focus, and schedule files. Prints to terminal and saves to briefings/. No external calls.
when_to_use: Triggered by '/morning-brief' or when Mohamed says "morning brief", "what's on today", "daily brief", "what do I have today", or "start of day".
argument-hint: (no arguments needed)
disable-model-invocation: false
allowed-tools: Bash Write
---

Run `equipment/morning-brief.py` to generate today's briefing from local files. No inputs needed. No API calls. Output printed to terminal and saved to `briefings/YYYY-MM-DD.md`.

---

## Steps

**1. Pre-flight check**
Confirm `equipment/morning-brief.py` exists. If not, stop and say: "morning-brief.py not found in equipment/."

**2. Run the script**
```bash
python "equipment/morning-brief.py"
```

Run from the project root directory.

The script reads:
- `live/tasks.md` — open tasks with due dates
- `intel/focus.md` — top priorities and hard deadlines
- `live/schedule.md` — today's calendar events

Missing files generate warnings but do not stop the script.

**3. Report**
After the script runs, say: "Morning brief saved to `briefings/[YYYY-MM-DD].md`."

If any source files were missing (script warns), mention them: "Note: [file] was not found — that section was skipped."

---

## Failure Handling

| Problem | Action |
|---------|--------|
| Script not found | "morning-brief.py not found in equipment/. Check the file path." |
| All source files missing | Script will still run and output an empty brief — report it and suggest checking `live/tasks.md` and `intel/focus.md` |
| Encoding error on Windows | Script has built-in UTF-8 handling — if it still fails, report the error verbatim |

---

## Notes
- Read-only. No writes except saving the briefing to `briefings/`.
- The "INTENTIONS FOR TODAY" section at the bottom is intentionally blank — Mohamed fills it in.
- To update what shows: edit `live/tasks.md` (tasks) or `intel/focus.md` (priorities).

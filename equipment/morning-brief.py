#!/usr/bin/env python3
"""
morning-brief.py
Generate your daily briefing from live/tasks.md, intel/focus.md,
and live/schedule.md. Prints to terminal and saves to briefings/YYYY-MM-DD.md.

Usage:
  python equipment/morning-brief.py

Alias (add to ~/.bashrc from the project directory):
  alias brief="python 'equipment/morning-brief.py'"

Or run from anywhere:
  alias brief="python 'C:/Users/Dell/Desktop/Mohamed excecutive assistant/equipment/morning-brief.py'"
"""

import io
import re
import sys
from datetime import date
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TODAY = date.today()
BASE_DIR = Path(__file__).parent.parent

TASKS_FILE = BASE_DIR / "live" / "tasks.md"
FOCUS_FILE = BASE_DIR / "intel" / "focus.md"
SCHEDULE_FILE = BASE_DIR / "live" / "schedule.md"
BRIEFINGS_DIR = BASE_DIR / "briefings"


def parse_tasks(path: Path):
    """Parse tasks.md. Returns (overdue, due_today, upcoming, no_date, done)."""
    if not path.exists():
        print(f"WARNING: {path} not found", file=sys.stderr)
        return [], [], [], [], []

    overdue, due_today, upcoming, no_date, done = [], [], [], [], []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            open_match = re.match(r"^- \[ \] (.+)", line)
            if open_match:
                content = open_match.group(1)
                desc = content.split(" | ")[0].strip()
                due_match = re.search(r"\| Due: (\d{4}-\d{2}-\d{2})", content)

                if due_match:
                    due = date.fromisoformat(due_match.group(1))
                    if due < TODAY:
                        overdue.append((desc, due))
                    elif due == TODAY:
                        due_today.append((desc, due))
                    else:
                        upcoming.append((desc, due))
                else:
                    no_date.append(desc)
                continue

            done_match = re.match(r"^- \[x\] (.+)", line, re.IGNORECASE)
            if done_match:
                done.append(done_match.group(1).split(" | ")[0].strip())

    overdue.sort(key=lambda x: x[1])
    upcoming.sort(key=lambda x: x[1])
    return overdue, due_today, upcoming, no_date, done


def parse_focus(path: Path):
    """Extract top priorities and deadlines from focus.md."""
    if not path.exists():
        print(f"WARNING: {path} not found", file=sys.stderr)
        return [], []

    priorities, deadlines = [], []
    section = None

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if re.match(r"^## Top Priorities", line):
                section = "priorities"
                continue
            if re.match(r"^## Hard Deadlines", line):
                section = "deadlines"
                continue
            if re.match(r"^## ", line):
                section = None
                continue

            if section == "priorities" and line.strip():
                m = re.match(r"^\d+\. (.+)", line)
                if m:
                    priorities.append(m.group(1).strip())

            if section == "deadlines" and line.strip():
                m = re.match(r"^- (.+)", line)
                if m:
                    deadlines.append(clean(m.group(1)))

    return priorities[:3], deadlines


def parse_schedule(path: Path):
    """Read today's calendar from live/schedule.md."""
    if not path.exists():
        return None

    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if re.match(r"^- .+", line) or re.match(r"^\d{1,2}:\d{2}", line):
                events.append(line.lstrip("- ").strip())

    return events or None


def clean(text: str) -> str:
    """Strip basic markdown formatting from parsed content."""
    return re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text).strip()


def divider(char="-", width=60):
    return char * width


def build_brief() -> str:
    overdue, due_today, upcoming, no_date, done = parse_tasks(TASKS_FILE)
    priorities, deadlines = parse_focus(FOCUS_FILE)
    schedule = parse_schedule(SCHEDULE_FILE)

    date_label = TODAY.strftime("%A, %d %B %Y")
    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        divider("="),
        f"  MORNING BRIEF — {date_label}",
        divider("="),
        "",
    ]

    # ── Overdue (top, flagged) ─────────────────────────────────────────────────
    if overdue:
        lines += [divider(), "  [OVERDUE]", divider(), ""]
        for desc, due in overdue:
            days = (TODAY - due).days
            lines.append(f"  [ ] {desc}")
            lines.append(f"      Was due {due.strftime('%d %b %Y')} — {days} day{'s' if days != 1 else ''} ago")
            lines.append("")

    # ── Today's schedule ──────────────────────────────────────────────────────
    lines += [divider(), "  TODAY'S SCHEDULE", divider(), ""]
    if due_today:
        lines.append("  Due today:")
        for desc, _ in due_today:
            lines.append(f"    [ ] {desc}")
        lines.append("")
    if schedule:
        lines.append("  Calendar:")
        for event in schedule:
            lines.append(f"    {event}")
        lines.append("")
    if not due_today and not schedule:
        lines.append("  No events. Update live/schedule.md or connect Google Calendar.")
        lines.append("")

    # ── Priorities ────────────────────────────────────────────────────────────
    lines += [divider(), "  PRIORITIES", divider(), ""]
    if priorities:
        for i, p in enumerate(priorities, 1):
            lines.append(f"  {i}. {p}")
        lines.append("")
    if deadlines:
        lines.append("  Deadlines:")
        for d in deadlines:
            lines.append(f"    {d}")
        lines.append("")

    # ── Open tasks ────────────────────────────────────────────────────────────
    lines += [divider(), "  OPEN TASKS", divider(), ""]

    task_count = len(upcoming) + len(no_date)
    if task_count == 0 and not due_today:
        lines.append("  No open tasks.")
        lines.append("")
    else:
        if upcoming:
            lines.append("  Upcoming:")
            for desc, due in upcoming:
                lines.append(f"    [ ] {desc}  ({due.strftime('%d %b')})")
            lines.append("")
        if no_date:
            lines.append("  No due date:")
            for desc in no_date:
                lines.append(f"    [ ] {desc}")
            lines.append("")

    if done:
        lines.append(f"  Done: {len(done)} task{'s' if len(done) != 1 else ''} complete")
        lines.append("")

    # ── Intentions ────────────────────────────────────────────────────────────
    lines += [divider(), "  INTENTIONS FOR TODAY", divider(), ""]
    lines += [
        "  What are the 1-3 things that would make today a win?",
        "",
        "  1.",
        "  2.",
        "  3.",
        "",
        divider("="),
        "",
    ]

    return "\n".join(lines)


def main():
    brief = build_brief()

    # Print to terminal
    print(brief)

    # Save to briefings/
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRIEFINGS_DIR / f"{TODAY.isoformat()}.md"
    out_path.write_text(brief, encoding="utf-8")
    print(f"Saved: briefings/{TODAY.isoformat()}.md")


if __name__ == "__main__":
    main()

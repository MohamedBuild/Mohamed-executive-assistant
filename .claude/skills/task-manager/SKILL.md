---
name: task-manager
description: Manage tasks in live/tasks.md — add, complete, list, and clear tasks. Single source of truth for all open work at AGENCINA.
when_to_use: Triggered by '/task-manager' or when Mohamed says "add task", "new task", "mark done", "complete task", "tick off", "what are my tasks", "show tasks", "show open tasks", "clear completed", or "update task".
argument-hint: (optional) "add [task]", "done [task description]", "list", "list overdue", "clear completed", "update [task]"
disable-model-invocation: false
allowed-tools: Read Edit Write Bash
---

Manage `live/tasks.md` — the persistent task tracker for AGENCINA. Supports four modes: **Add**, **Done**, **List**, and **Clear**.

---

## Mode A — Add a task

Triggered when Mohamed says "add task", "new task", or describes something that needs tracking.

**1. Collect inputs**

| Input | Required | Default |
|-------|----------|---------|
| Task description | Yes | — |
| Source | No | "manual" |
| Due date | No | "none" |

If no due date is given, ask once: "Due date, or none?" Accept natural language (e.g. "Friday", "15 May") and convert to YYYY-MM-DD.

**2. Append to tasks.md**

Read `live/tasks.md` first. Append a new line in this exact format:
```
- [ ] [Task description] | Source: [source] | Due: [YYYY-MM-DD or "none"]
```

**3. Report**
Say: "Added: [task description]. Due: [date or 'none']."

---

## Mode B — Mark a task done

Triggered when Mohamed says "mark done", "complete", "tick off", or "done with [task]".

**1. Identify the task**
Read `live/tasks.md`. If the task isn't clear from what Mohamed said, list open tasks (numbered) and ask which one.

**2. Mark complete**
Change `- [ ]` to `- [x]` on the matching line. Use Edit tool — match the full line to avoid false positives.

**3. Report**
Say: "Done: [task description]."

---

## Mode C — List tasks

Triggered when Mohamed says "show tasks", "what are my tasks", "what's open", or "list overdue".

**1. Read `live/tasks.md`**

**2. Parse and display**

Default (no filter): show all open `[ ]` tasks, grouped by due date:
- **Overdue** — due date is before today (2026-05-04)
- **Due this week** — due date is 2026-05-04 to 2026-05-10
- **Due later** — due date beyond this week
- **No due date** — due: none

Show counts at the top: "X open tasks — Y overdue."

If Mohamed says "list all", include completed tasks too, greyed out at the bottom.

---

## Mode D — Clear completed tasks

Triggered when Mohamed says "clear completed", "archive done tasks", or "clean up tasks".

**1. Confirm**
Say: "Move all completed tasks to `archive/tasks-cleared-YYYY-MM-DD.md`? They won't be deleted."
Wait for confirmation.

**2. Move completed tasks**
- Read `live/tasks.md`
- Separate `[x]` lines from `[ ]` lines
- Write completed lines to `archive/tasks-cleared-[today].md` (create if needed, append if exists)
- Rewrite `live/tasks.md` with only the open `[ ]` tasks (keep the header intact)

**3. Report**
Say: "Cleared X completed tasks → archived to `archive/tasks-cleared-[date].md`."

---

## Mode E — Update a task

Triggered when Mohamed says "update task", "change due date", or "edit task".

**1. Identify the task**
List open tasks (numbered) if not clear from context.

**2. Collect what's changing**
Ask: "What should change — description, source, due date?"

**3. Apply the edit**
Use Edit tool to replace the full line with the updated version.

**4. Report**
Say: "Updated: [new task line]."

---

## Task file format

`live/tasks.md` uses this structure:
```
# Task Tracker

*Persistent task list. Updated during and between sessions.*
*Format: - [ ] Task description | Source: [where it came from] | Due: [date or "none"]*

---

- [ ] Task description | Source: source | Due: YYYY-MM-DD
- [x] Completed task | Source: source | Due: none
```

Never change the header block. Never delete lines — use Mode D to archive.

---

## Failure handling

| Problem | Action |
|---------|--------|
| `live/tasks.md` not found | "tasks.md not found at live/tasks.md — should I create it?" |
| Task not found for "done" | List open tasks numbered. Ask Mohamed to pick. |
| Ambiguous task match | Show matching lines and ask which one. |
| `archive/` directory missing | Create it before writing the archive file. |

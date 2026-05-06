---
name: weekly-plan
description: Generate a prioritised weekly execution plan for AGENCINA. Reads Gmail, Google Calendar, Google Sheets CRM, and local task files. Scores every item by urgency and deal value. Outputs atomic tasks with concrete actions, "Done when" criteria, and a PDF saved to docs/superpowers/plans/.
when_to_use: Triggered by '/weekly-plan' or when Mohamed says "plan my week", "weekly plan", "prioritise my week", "what should I focus on this week", or "create a weekly plan".
argument-hint: (optional) date range, e.g. "4–10 May" — defaults to current week
disable-model-invocation: false
allowed-tools: Bash Read Write Edit
---

I'm using the weekly-plan skill to generate this week's execution plan.

Announce this upfront, then execute the steps below in order.

---

## Step 1 — Gather all sources

Read these in parallel:

**Local:**
- `live/state.md` — open tasks, priorities, active projects
- `intel/focus.md` — quarterly priorities and hard deadlines
- `live/tasks.md` — persistent task tracker

**Live (via MCP tools):**
- **Gmail** — search `newer_than:7d -from:me -is:spam` (inbox) + list all drafts
- **Google Calendar** — list all events for the current week (Mon–Sun)
- **Google Sheets** — search Drive for "AGENCINA" or "LEAD" or "PIPELINE" spreadsheet; read the most recently modified one

Note what is missing. If any source fails, continue without it and flag the gap at the top of the plan.

---

## Step 2 — Score every item

For each item found (email, calendar event, pipeline row, open task), assign two scores:

**Urgency score (1–3):**
- 3 = due today or overdue, or a call is happening this week
- 2 = due within 7 days, or a warm prospect going cold (last contact >7 days)
- 1 = important but no near-term deadline

**Impact score (1–3):**
- 3 = deal value ≥ $5,000, or active client at risk, or hard deadline (launch, legal, compliance)
- 2 = deal value $1,000–$4,999, or existing client relationship, or unblocks other work
- 1 = deal value < $1,000, or cold/low-priority, or admin

**Priority = Urgency × Impact.** Sort descending. Ties: urgency wins.

| Score | Label |
|-------|-------|
| 9 | P0 — Do first, today |
| 6–8 | P1 — Do this week, early |
| 3–5 | P2 — Do this week, later |
| 1–2 | P3 — Defer or skip |

---

## Step 3 — Build the task list

Group tasks by day (Mon → Fri). Each task must follow this structure:

```
## TASK [N] — [Short title] ([deal or context])

**Why:** One sentence on why this is the highest-leverage action right now.
**Priority:** P[0–3] (Urgency [1–3] × Impact [1–3])
**Time required:** [realistic estimate]

Steps:
1. [Concrete verb + object — no vague language]
2. [If email: include exact subject line and verbatim body or explicit instruction to write one]
3. [If pipeline update: specify the row, fields, and exact values]

**Done when:** [Single measurable outcome — no ambiguity]
```

**Antipatterns — never write these:**
- "Follow up with [client]" → write the exact email or specify the exact action
- "Push forward on [project]" → name the specific next step
- "Check in on [deal]" → what are you checking, what's the decision
- "Work on [task]" → what is the output
- TBD, "as needed", "if time allows", "circle back"

---

## Step 4 — Map prep blocks

For every client call or meeting on the calendar:
- Add a PREP task the day before (or earlier that day if same-day)
- Prep tasks must include: what to have ready, what questions to ask, what your position is on any open negotiation point

---

## Step 5 — Add an Execution Order table

At the end of the plan, add a summary table:

| Order | Task | Deadline | Priority |
|-------|------|----------|----------|
| 1 | [task title] | [date/time] | P0 |
| ... | | | |

---

## Step 6 — Self-review checklist

Before finalising, verify:

- [ ] Every task has a concrete first action (verb + object, no vague language)
- [ ] Every task that involves an email has either a verbatim draft or an explicit instruction to write one
- [ ] Every pipeline update specifies the row, fields, and values
- [ ] Every call on the calendar has a PREP task
- [ ] No TBDs, no "figure out later", no "similar to Task N"
- [ ] Every task has a "Done when:" definition
- [ ] Overdue items are ranked P0 or P1 — nothing overdue is below P2
- [ ] The highest-value open deals appear in the first 3 tasks
- [ ] Hard deadlines (website launch, client commitments) are explicitly flagged
- [ ] All items from state.md open tasks are accounted for (scheduled or explicitly deferred)

If any check fails, fix the plan before proceeding.

---

## Step 7 — Save the plan

**Save markdown:**
```
docs/superpowers/plans/YYYY-MM-DD-weekly-plan.md
```
Use today's date. Overwrite if the file already exists for this week.

**Generate PDF:**
Use this Python snippet (run from project root):
```python
import importlib.util, json, pathlib
spec = importlib.util.spec_from_file_location('wp', 'equipment/generate-weekly-plan.py')
# If script doesn't exist, use fpdf2 directly to render the markdown as a clean PDF
```

If `equipment/generate-weekly-plan.py` does not exist, render the plan as a PDF using fpdf2:
- Title: "Weekly Execution Plan — [date range]"
- Sections: one per day, tasks numbered
- Footer: "AGENCINA | [email]"
- Save to: `docs/superpowers/plans/YYYY-MM-DD-weekly-plan.pdf`

**Report:**
Say: "Weekly plan saved — [N] tasks across [N] days. [N] overdue items. Top priority: [P0 task title]. PDF at docs/superpowers/plans/[filename].pdf."

---

## Failure handling

| Problem | Action |
|---------|--------|
| Gmail returns no results | Note "Gmail: no new threads" — continue with other sources |
| Calendar returns no events | Note "Calendar: no events found" — flag that calls may be untracked |
| Sheets not found | Use pipeline data from state.md if available — flag the gap |
| fpdf2 not installed | "Run: pip install fpdf2" — save markdown only and report PDF skipped |
| No open tasks anywhere | Still produce a plan — flag that all sources were empty |

---

## Notes

- Prioritisation methodology: Urgency × Impact matrix. Simple, fast, consistent.
- Inspired by obra/superpowers/writing-plans atomic task decomposition — adapted for business execution.
- The plan is a tool, not a document. If something changes mid-week, re-run the skill.
- Never skip the self-review. The checklist catches vague tasks before they waste time.

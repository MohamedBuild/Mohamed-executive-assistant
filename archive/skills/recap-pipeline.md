# Skill: recap-pipeline

Pull the full pipeline from Google Sheets and produce a structured summary. Save to `briefings/`. Nothing sent automatically.

---

## Steps

**1. Check Zapier actions**
Call `list_enabled_zapier_actions`. Find a Google Sheets read/find-rows action.
- If none: call `discover_zapier_actions` with query `"Google Sheets find rows"`, then `enable_zapier_action`. Confirm with Mohamed before enabling.
- If Zapier is unreachable: stop — "Zapier MCP not responding. Check settings.local.json."

**2. Read the pipeline**
Call `execute_zapier_read_action`:
- app: Google Sheets
- action: `get_data_range`
- instructions: "Read the spreadsheet 'Leads & Pipeline (Sample)', range A1:K20, return all rows and columns including the header row."
- output: "every row with all column values"

Inspect the raw response — note the exact column names returned before parsing. The correct columns are: company, contact_name, role, email, source, stage, deal_value_usd, last_contact, next_step, notes.

**3. Parse**
- Group leads by stage, count per group
- Sum deal values for active stages only: Quote sent + Discovery booked + Audit in progress
- Rank all leads by deal value descending; pick top 3 with strongest urgency signals (high value + near-term next steps)
- Skip leads with missing or non-numeric deal values from the total — note them explicitly

**4. Format the output**

```
PIPELINE RECAP — [DATE]
════════════════════════════════════════════════════════════

STAGE BREAKDOWN
────────────────────────────────────────────────────────────
Quote sent:            [N] leads
Discovery booked:      [N] leads
Audit in progress:     [N] leads
Won:                   [N] leads
[Other stages]:        [N] leads

ACTIVE PIPELINE VALUE
────────────────────────────────────────────────────────────
Stages counted: Quote sent · Discovery booked · Audit in progress
Total: $[X,XXX]

TOP 3 LEADS THIS WEEK
────────────────────────────────────────────────────────────
1. [Client name] — $[value] — Stage: [stage]
   Next step: [planned action]

2. [Client name] — $[value] — Stage: [stage]
   Next step: [planned action]

3. [Client name] — $[value] — Stage: [stage]
   Next step: [planned action]

════════════════════════════════════════════════════════════
```

If fewer than 3 leads exist, show all — no padding.

**5. Save**
Create `briefings/` if it does not exist.
Save output to `briefings/pipeline-[YYYY-MM-DD].md`.

**6. Report**
Print the formatted summary to terminal.
Say: "Pipeline recap saved to briefings/pipeline-[date].md."

---

## Failure Handling

| Problem | Action |
|---------|--------|
| No Google Sheets action enabled | Run discover + enable. Confirm with Mohamed which to enable if multiple match. |
| Sheet returns empty | "Sheet returned no data. Confirm the sheet name is exactly 'Leads & Pipeline (Sample)'." |
| Deal value missing or non-numeric | Exclude from total. Note: "[Client]: value missing — excluded from total." |
| No next steps field | Use stage as proxy: "Next step not recorded — stage is [X]." |
| Fewer than 3 leads | Show all. No padding. |

---

## Notes
- Read-only. No writes to the sheet.
- Won leads: show in stage breakdown, exclude from active pipeline total.
- Dollar values shown are pipeline estimates — pricing is not finalised as of Q2 2026.

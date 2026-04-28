# Blueprint: Pipeline Summary — Monday Morning Brief

## Goal
Read the full pipeline from Google Sheets via Zapier MCP, then produce a structured Monday morning summary: lead count per stage, total dollar value of active stages, and the three hottest leads with their planned next steps this week. Output printed to terminal and saved to `briefings/`. Nothing sent automatically.

## Trigger
Every Monday morning, before the work day begins. Run manually — say "Run pipeline summary" or "Monday brief".

## Required Inputs
None. All data comes from the Google Sheet "Leads & Pipeline (Sample)" via Zapier read action.

## Optional Inputs
- Custom stage filter: specify which stages count as "active" (default: Quote sent, Discovery booked, Audit in progress)
- `--week` context: manually frame the summary against a specific week (defaults to current week)

## Pre-flight Checks
1. Run `list_enabled_zapier_actions` — confirm a Google Sheets read action is present
2. If none found: run `discover_zapier_actions` with query `"Google Sheets find rows"`, then `enable_zapier_action` with the matching action ID
3. Confirm the action is now active before proceeding
4. If Zapier MCP is unreachable: stop and report "Zapier MCP not responding. Check settings.local.json for correct SSE transport and token."

## Equipment
None. Blueprint-only workflow — analysis and briefing per the three-engine-model guide.

## Sequence
1. Call `list_enabled_zapier_actions` — note the name of the Google Sheets read action
2. Call `execute_zapier_read_action`:
   ```
   action: "[Google Sheets — Find Row(s) action name from step 1]"
   instructions: "Read all rows from the spreadsheet named 'Leads & Pipeline (Sample)'. Return client name, pipeline stage, deal value, contact name, and next steps for every row."
   ```
3. Inspect the raw response — note the exact column names returned (they may differ from defaults)
4. Parse the data:
   - Group leads by stage, count per group
   - Sum deal values for active stages only: Quote sent + Discovery booked + Audit in progress
   - Rank all leads by deal value descending; select the top 3 with the strongest urgency signals (high value + near-term next steps)
5. Compose the summary in this format:

   ```
   PIPELINE SUMMARY — [DATE]
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

   TOP 3 HOTTEST LEADS THIS WEEK
   ────────────────────────────────────────────────────────────
   1. [Client name] — $[value] — Stage: [stage]
      Next step: [planned action this week]

   2. [Client name] — $[value] — Stage: [stage]
      Next step: [planned action this week]

   3. [Client name] — $[value] — Stage: [stage]
      Next step: [planned action this week]

   ════════════════════════════════════════════════════════════
   ```

6. Save the summary to `briefings/pipeline-[YYYY-MM-DD].md`
7. Report: "Pipeline summary saved to briefings/pipeline-[date].md. Review and confirm next steps for this week."

## Expected Output
- Terminal output of the formatted summary
- `briefings/pipeline-YYYY-MM-DD.md` — saved copy for the record

## Failure Handling
| Problem | Action |
|---------|--------|
| No Google Sheets action enabled | Run discover + enable sequence. Confirm with Mohamed which action to enable if multiple match. |
| Zapier read returns empty rows | "Sheet returned no data. Confirm the sheet name is exactly 'Leads & Pipeline (Sample)'." |
| Zapier MCP not reachable | "Zapier MCP not responding. Check settings.local.json for correct SSE transport and token." |
| Deal value field missing or non-numeric | Skip that lead from the active total. Note: "[Client]: value missing — excluded from total." |
| No next steps field in the sheet | Use the stage name as the proxy: "Next step not recorded — stage is [X]." |
| Fewer than 3 leads in the pipeline | Show all leads available. No padding. |

## Notes
- This is read-only. No writes to the sheet.
- Won leads are excluded from the active pipeline total but shown in the stage breakdown.
- Pricing is not finalised as of Q2 2026 — dollar values shown are pipeline estimates, not confirmed fees.
- If column names in the sheet differ from what's expected, inspect the raw Zapier response first and adjust the parse logic before composing the summary.
- `briefings/` directory: create it if it does not exist.

# Blueprint: Lead Update + Follow-up Email Draft

## Goal
Two jobs, one workflow: (1) add a follow-up note to a lead's row in Google Sheets via Zapier write action, and (2) draft a professional follow-up email to the lead contact. Email draft saved locally for Mohamed's review. Nothing sent automatically.

## Trigger
On-demand. Run when a lead needs a follow-up action. Say "Draft follow-up for [client]" or "Log follow-up for [client]".

## Required Inputs
Collect these before running:
- Client name (exact match to the sheet — case-sensitive)
- Contact name (for email salutation)
- Contact email address
- Context: what was last sent or discussed, and what Mohamed wants to communicate now
- Proposed next step (e.g. "Schedule a 30-minute call this week", "Confirm proposal feedback by Friday")

## Optional Inputs
- Note to log in the CRM row (defaults to a timestamp + "Follow-up sent")
- Specific deadline or date to reference in the email body
- Tone hint: `warmer` | `firmer` | `neutral` (default: neutral, AGENCINA voice standard)

## Pre-flight Checks
1. Confirm all Required Inputs with Mohamed — do not assume any field
2. Run `list_enabled_zapier_actions` — confirm a Google Sheets read action and a Google Sheets update/write action are both present
3. If either is missing: run `discover_zapier_actions` with `"Google Sheets update row"` or `"Google Sheets find rows"`, then `enable_zapier_action`
4. Check whether a Gmail Create Draft action is available (optional — local `.md` save is the fallback if absent)
5. Confirm the `live/comms/` directory exists — create it if not

## Equipment
None. Email drafting is a blueprint-only task (analysis and drafting per the three-engine-model guide). Zapier MCP write actions handle the CRM update.

## Sequence — Step 1: Log Follow-up in Pipeline

1. Call `execute_zapier_read_action` to locate the lead's row:
   ```
   action: "[Google Sheets — Find Row(s) action name]"
   instructions: "Find the row where the client name is '[CLIENT NAME]' in the sheet 'Leads & Pipeline (Sample)'. Return the row ID, current stage, deal value, and any existing notes."
   ```
2. Report the match back to Mohamed — confirm it is the correct row before writing
3. If multiple rows match: show all matches with their current stages; ask Mohamed which one to update
4. Call `execute_zapier_write_action` to log the follow-up note:
   ```
   action: "[Google Sheets — Update Row action name]"
   instructions: "In the sheet 'Leads & Pipeline (Sample)', update the row for '[CLIENT NAME]'. Set the Notes field to: '[NOTE TEXT or default: Follow-up sent — YYYY-MM-DD]'. Do not change the Stage field."
   ```
5. Confirm write success. Report: "CRM updated — follow-up note logged for [CLIENT NAME]. Stage unchanged: [CURRENT STAGE]."

## Sequence — Step 2: Draft Follow-up Email

1. Using the confirmed context, compose the email draft in AGENCINA voice:
   - Subject line: specific, not generic ("Following up — [Proposal/Project name]", not "Quick follow-up")
   - Opening: contact name + a short, direct reference to the last touch point (no preamble)
   - Body: one clear statement of where things stand + one concrete ask
   - Close: Mohamed's name, AGENCINA — no fluff
   - Footer line: `[DRAFT — Mohamed to review before sending]`
2. Save the draft to `live/comms/followup-[client-slug]-[YYYY-MM-DD].md`
3. If Gmail Create Draft action is enabled, ask Mohamed: "Save to Gmail drafts as well?"
   - If yes: call `execute_zapier_write_action`:
     ```
     action: "[Gmail — Create Draft action name]"
     instructions: "Create a Gmail draft to [CONTACT EMAIL] with subject '[SUBJECT]' and body '[BODY]'"
     ```
4. Report: "Email draft saved to live/comms/[filename]. [If Gmail: Also saved to Gmail drafts.] Review before sending."

## Expected Output
- CRM row updated with follow-up note (stage unchanged)
- `live/comms/followup-[client-slug]-YYYY-MM-DD.md` — email draft for Mohamed's review
- (Optional) Gmail draft created, pending Mohamed's review and send

## Failure Handling
| Problem | Action |
|---------|--------|
| Client name not found in sheet | Report the exact name searched. Ask Mohamed to confirm spelling. Do not create a new row. |
| Multiple rows match | Show all matches with stage and value. Ask Mohamed to confirm which row to update. |
| Zapier write action fails | Report the error. Do not retry without confirmation: "Write failed — retry?" |
| Gmail Draft action not enabled | Save to `live/comms/` only. Note: "Gmail draft action not active — email saved locally." |
| Context for the email is vague or incomplete | Stop. Ask: "What specifically happened last, and what do you want [contact] to do next?" Do not draft from thin context. |

## Notes
- Never auto-send. The workflow ends at draft creation, regardless of which actions are available.
- The local `.md` file is the primary output. Gmail draft is secondary and optional.
- Stage is never changed by this blueprint — only a follow-up note is logged. Use a different workflow to move a lead between stages.
- For Foster & Marsh Legal: stage remains "Quote sent". The $12,000 value should only be referenced in the email if Mohamed explicitly includes it in the context provided.
- `live/comms/` directory: create it if it does not exist before saving the draft.

# Blueprint: Proposal Document Generation

## Goal
Generate a formatted PDF proposal for a client whose scope needs confirming in writing. Covers: scope, deliverables, investment, timeline, legal mentions, and AGENCINA branding. Saves PDF + JSON sidecar to `live/proposals/`. Nothing sent automatically — Mohamed reviews before it goes out.

## Trigger
On-demand. Run when a deal closes or a formal proposal document is required. Say "Generate proposal for [client]".

## Required Inputs
Collect these before running:
- Client name
- Contact name
- Project name
- Scope description — detailed, used verbatim in the PDF
- Deliverables list — each with a description and whether it is included or optional
- Project fee — must be confirmed explicitly by Mohamed (pricing not finalised — do not derive or estimate)
- Payment structure: `upfront` | `50-50` | `on-delivery`
- Timeline — e.g. "6 weeks from project start"
- Start date — confirmed or estimated

## Optional Inputs
- Assumptions — conditions this proposal depends on (e.g. "Client provides brand assets by day 1")
- Revision rounds (default: 2)
- Proposal number (auto-generated as `PROP-YYYYMMDD-HHMM` if omitted)
- Issue date (defaults to today)
- VAT: yes / no + rate
- Legal text override — custom legal clause (default: standard AGENCINA boilerplate)
- Output directory (default: `live/proposals/`)

## Pre-flight Checks
1. `.env` exists with `BUSINESS_NAME` and `BUSINESS_EMAIL` filled — if either is missing, stop and report exactly what is missing
2. `equipment/generate-proposal.py` is present
3. Dependencies installed: `pip install fpdf2 python-dotenv`
4. Project fee confirmed explicitly by Mohamed — do not proceed without it
5. (Optional) If pulling pipeline context: run `list_enabled_zapier_actions` and confirm a Google Sheets read action is available

## Equipment
`equipment/generate-proposal.py` — generates PDF and JSON sidecar

## Sequence
1. Confirm all Required Inputs with Mohamed — do not proceed with any unknowns
2. (Optional) If reading pipeline data to pre-fill context, call `execute_zapier_read_action`:
   ```
   action: "[Google Sheets — Find Row(s) action name]"
   instructions: "Find the row for '[CLIENT NAME]' in 'Leads & Pipeline (Sample)'. Return stage, deal value, contact name, and notes."
   ```
   Use returned data for context only — do not use the pipeline value as the proposal fee without explicit confirmation from Mohamed
3. Run:
   ```
   python equipment/generate-proposal.py \
     --client "[CLIENT NAME]" \
     --contact "[CONTACT NAME]" \
     --project "[PROJECT NAME]" \
     --scope "[SCOPE DESCRIPTION]" \
     --deliverables '[{"description": "Deliverable 1", "optional": false}, {"description": "Add-on item", "optional": true}]' \
     --value [CONFIRMED FEE] \
     --payment "50-50" \
     --timeline "[TIMELINE]" \
     --start-date "[DD Month YYYY]" \
     [--assumptions "Client provides assets by day 1"] \
     [--revision-rounds 2] \
     [--vat] [--vat-rate 15] \
     [--proposal-number "PROP-001"] \
     [--legal-text "Custom legal clause if needed"]
   ```
4. Script outputs to `live/proposals/PROP-XXXXXX_client-name.pdf` + `.json` sidecar
5. Report: proposal filename, confirmed fee, payment structure, start date
6. Say: "Proposal saved at live/proposals/[filename]. Review before sending."

## Expected Output
- `live/proposals/PROP-YYYYMMDD-HHMM_client-name.pdf` — client-facing proposal document
- `live/proposals/PROP-YYYYMMDD-HHMM_client-name.json` — JSON sidecar for records

## Failure Handling
| Problem | Action |
|---------|--------|
| `BUSINESS_NAME` or `BUSINESS_EMAIL` missing from `.env` | Report exactly what is missing. Do not generate. |
| `fpdf2` not installed | "Run: pip install fpdf2 python-dotenv" |
| `--value` not provided | Stop. "Project fee required. Mohamed must confirm the fee before generating." |
| Invalid deliverables JSON | Show correct format: `[{"description": "...", "optional": false}]` |
| `generate-proposal.py` not found | "Equipment script missing. Build it first." |
| Output directory unwritable | Report the error. Check folder permissions. |

## Notes
- This is a proposal, not a quote. It confirms scope and fees post-agreement, not pre-agreement. Use `generate-quote.py` for pre-agreement estimates.
- JSON sidecar is the record of what was generated — do not edit the PDF manually.
- Pricing is not finalised as of Q2 2026 — the `--value` parameter is mandatory and must always come from Mohamed directly.
- For Sahel Cafe Group: pipeline shows $12,000. Confirm the actual fee with Mohamed before running — do not use the pipeline figure without asking.
- Legal section uses standard AGENCINA boilerplate from `.env` (`DEFAULT_LEGAL_TEXT`) or a hardcoded fallback. Override with `--legal-text` if project-specific terms apply.
- `live/proposals/` directory is created automatically by the script on first run.

# Blueprint: Quote Generation

## Goal
Generate a professional PDF quote for a prospective AGENCINA client. Save PDF + JSON sidecar to `live/quotes/`. Nothing gets sent automatically — Mohamed reviews before it goes out. Once accepted, convert to invoice with a single command.

## Required Inputs
Collect these before running:
- Client name
- Project name
- Scope / notes — detailed description of what's included
- Timeline — e.g. "4 weeks from project start"
- Assumptions — conditions the quote depends on (prevents scope creep)
- T&Cs — payment terms, revision policy, etc. (or use default from .env)
- Services list — each with description, amount, and whether it's optional
- Validity period (default: 30 days)
- VAT applicable? (yes / no)
- Quote number (optional — auto-generated as `QUO-YYYYMMDD-HHMM` if omitted)

## Pre-flight Checks
1. `.env` exists with `BUSINESS_NAME` and `BUSINESS_EMAIL` filled
2. `equipment/generate-quote.py` is present
3. Dependencies installed: `pip install fpdf2 python-dotenv`

## Equipment
`equipment/generate-quote.py` — generates PDF and JSON sidecar
`equipment/convert-quote.py` — converts accepted quote to invoice

## Sequence — Generate Quote
1. Confirm all inputs with Mohamed
2. Run:
   ```
   python equipment/generate-quote.py \
     --client "Client Name" \
     --project "Project Name" \
     --scope "Detailed scope description" \
     --timeline "4 weeks from project start" \
     --assumptions "Client provides all assets by day 1; max 2 revision rounds" \
     --terms "50% upfront, 50% on delivery. Net 14 payment." \
     --services '[{"description": "Workflow build", "amount": 2500, "optional": false}, {"description": "Training session", "amount": 500, "optional": true}]' \
     [--vat] [--vat-rate 15]
   ```
3. Outputs to `live/quotes/QUO-XXXXXX_client-name.pdf` + `live/quotes/QUO-XXXXXX_client-name.json`
4. Report: filename, total (required only), valid until date
5. Say: "Quote saved at live/quotes/[filename]. Review and send when ready."

## Sequence — Convert to Invoice
Once client accepts:
1. Confirm with Mohamed which optional items (if any) to include
2. Run:
   ```
   # Exclude all optional items (default):
   python equipment/convert-quote.py --quote live/quotes/QUO-XXXXXX_client-name.json

   # Include all optional items:
   python equipment/convert-quote.py --quote live/quotes/QUO-XXXXXX_client-name.json --accept-optional
   ```
3. Invoice generates in `live/invoices/` with all accepted line items and final pricing
4. Report: invoice filename and total

## Expected Output
- `live/quotes/QUO-YYYYMMDD-HHMM_client-name.pdf` — client-facing quote
- `live/quotes/QUO-YYYYMMDD-HHMM_client-name.json` — machine-readable sidecar for conversion
- On conversion: `live/invoices/INV-YYYYMMDD-HHMM_client-name.pdf`

## Failure Handling
| Problem | Action |
|---------|--------|
| Missing .env values | Report what's missing — do not generate |
| fpdf2 not installed | "Run: pip install fpdf2 python-dotenv" |
| Invalid services JSON | Show correct format example |
| JSON sidecar not found for conversion | "Can't find quote file. Check path and try again." |

## Notes
- Optional items appear in the PDF clearly marked "(Optional)" — client can see what's included vs. add-on
- JSON sidecar is the source of truth for conversion — do not edit the PDF manually
- Validity defaults to 30 days from issue date; override with `--validity-days`

# Blueprint: Invoice Creation

## Goal
Generate a professional PDF invoice for an AGENCINA client. Save locally, flag for Google Drive upload. Nothing gets sent automatically — Mohamed reviews before anything goes out.

## Required Inputs
Collect these before running:
- Client name
- Project name
- Services list — each with a description and amount
- Due date
- VAT applicable? (yes / no — confirm before including)
- Invoice number (optional — auto-generated as `INV-YYYYMMDD-HHMM` if omitted)
- Issue date (optional — defaults to today)

## Pre-flight Checks
Before running Equipment:
1. `.env` exists and `BUSINESS_NAME`, `BUSINESS_EMAIL`, `BANK_IBAN` are filled — if any are blank, stop and report what's missing
2. `equipment/generate-invoice.py` is present
3. Dependencies installed: `pip install fpdf2 python-dotenv`

## Equipment
`equipment/generate-invoice.py`

## Sequence
1. Confirm all inputs with Mohamed — do not assume anything
2. Run the script:
   ```
   python equipment/generate-invoice.py \
     --client "Client Name" \
     --project "Project Name" \
     --services '[{"description": "Service", "amount": 1000}]' \
     --due-date "30 May 2026" \
     [--invoice-number "INV-001"] \
     [--vat] [--vat-rate 15]
   ```
3. Invoice saves to `live/invoices/`
4. Report to Mohamed: filename, total amount, due date
5. Say: "Invoice saved at live/invoices/[filename]. Upload to Google Drive when ready. Nothing has been sent."

## Expected Output
- PDF at `live/invoices/INV-YYYYMMDD-HHMM_client-name.pdf`
- Console confirmation with full filepath and total

## Failure Handling
| Problem | Action |
|---------|--------|
| Missing .env values | Report exactly what's missing — do not generate a partial invoice |
| fpdf2 not installed | "Run: pip install fpdf2 python-dotenv" |
| Invalid services format | Show correct JSON example |
| Output directory unwritable | Report the error, suggest checking folder permissions |

## Notes
- VAT: only apply if client or project requires it — always confirm first
- Google Drive is the source of truth. Local copy is a working draft.
- Override auto-generated invoice number with `--invoice-number` for sequential numbering
- Currency defaults to USD — set `CURRENCY` in `.env` to change

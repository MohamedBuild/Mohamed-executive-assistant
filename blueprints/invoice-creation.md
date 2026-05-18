# Blueprint: Invoice Creation

## Goal
Generate professional PDF invoices for AGENCINA clients from Google Sheet data. Each paid invoice gets a diagonal green **PAID** watermark. Nothing gets sent automatically — Mohamed reviews before anything goes out.

## Required Inputs
- Invoice data from the "AAA Operations — Internal Dashboard" sheet (Invoices tab)
- `.env` with `BUSINESS_NAME`, `BUSINESS_EMAIL`, `BANK_IBAN` filled

## Pre-flight Checks
1. `.env` exists and `BUSINESS_NAME`, `BUSINESS_EMAIL`, `BANK_IBAN` are filled — stop if any are blank
2. `equipment/generate-invoice.py` is present
3. Template exists at `templates/invoice_reference/invoice_template.docx` — if missing, run `--setup-template`
4. Dependencies installed: `pip install -r equipment/requirements.txt`

## Equipment
`equipment/generate-invoice.py`

## Sequence

### One-time setup (first run only)
```
python equipment/generate-invoice.py --setup-template
```
Creates `templates/invoice_reference/invoice_template.docx` with `{{TOKEN}}` placeholders. Open in Word to review or adjust the layout before generating PDFs.

### Batch generation from Google Sheet
1. Read all rows from the Invoices tab via Zapier Google Sheets MCP
2. Save to `live/invoices/_batch_input.json`
3. Run:
   ```
   python equipment/generate-invoice.py --batch-file live/invoices/_batch_input.json
   ```
4. PDFs save to `live/invoices/`
5. Report to Mohamed: count generated, list of filenames and totals

## PAID Watermark
- Invoices with `status: "paid"` automatically receive a diagonal green **PAID** watermark across the page
- Invoices with `status: "unpaid"` or `status: "overdue"` have no watermark
- Watermark is injected into the Word header before PDF conversion — no extra tools needed

## Expected Output
- PDF at `live/invoices/{INVOICE_NUMBER}_{client-slug}.pdf`
- Paid invoices: diagonal green PAID watermark
- Console confirmation with filename and total per invoice

## Template Placeholders
The editable template lives at `templates/invoice_reference/invoice_template.docx`.
Open it in Word to adjust layout. Do not change the `{{TOKEN}}` names — the script depends on exact matches.

| Token | Value |
|---|---|
| `{{INVOICE_NUMBER}}` | e.g. AAA-INV-2026-001 |
| `{{ISSUE_DATE}}` | formatted DD Month YYYY |
| `{{DUE_DATE}}` | formatted DD Month YYYY |
| `{{STATUS}}` | PAID / OUTSTANDING |
| `{{CLIENT_COMPANY}}` | company name from sheet |
| `{{DESCRIPTION}}` | service description |
| `{{SUBTOTAL}}` | pre-VAT amount |
| `{{VAT_PCT}}` | VAT percentage |
| `{{VAT_AMOUNT}}` | computed VAT amount |
| `{{TOTAL}}` | final amount due |
| `{{CURRENCY}}` | USD / AED etc. |
| `{{BUSINESS_NAME}}` | from `.env` |
| `{{BUSINESS_ADDRESS}}` | from `.env` |
| `{{BUSINESS_EMAIL}}` | from `.env` |
| `{{BUSINESS_PHONE}}` | from `.env` |
| `{{BANK_NAME}}` | from `.env` |
| `{{BANK_ACCOUNT}}` | from `.env` |
| `{{BANK_IBAN}}` | from `.env` |
| `{{BANK_SWIFT}}` | from `.env` |

## Failure Handling
| Problem | Action |
|---|---|
| Missing `.env` values | Report exactly what's missing — do not generate a partial invoice |
| Template missing | Run `python equipment/generate-invoice.py --setup-template` |
| Dependencies missing | Run `pip install -r equipment/requirements.txt` |
| Microsoft Word not installed | `docx2pdf` requires Word on Windows — install Word or use LibreOffice headless |
| Output directory unwritable | Report the error, check folder permissions |

## Notes
- VAT: applied per invoice row from the sheet — always confirm before sending to client
- Google Drive is the source of truth. Local PDFs are working drafts.
- Currency defaults to USD — set `CURRENCY` in `.env` to change global default
- Re-run at any time to regenerate all PDFs (idempotent — overwrites existing files)

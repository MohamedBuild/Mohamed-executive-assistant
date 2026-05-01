---
name: generate-invoice
description: Generate a professional PDF invoice for an AGENCINA client. Saves locally to live/invoices/. Nothing is sent automatically.
when_to_use: Triggered by '/generate-invoice' or when Mohamed says "generate invoice", "create invoice", "invoice for [client]", or "bill [client]".
argument-hint: (optional) client name, project name, or any detail to pre-fill
disable-model-invocation: false
allowed-tools: Bash Write
---

Generate a professional PDF invoice using `equipment/generate-invoice.py`. Collect all inputs, run pre-flight checks, execute the script, and report back. Nothing is sent automatically — Mohamed reviews the PDF before uploading to Google Drive.

---

## Steps

**1. Pre-flight checks**
Before collecting inputs:
- Confirm `equipment/generate-invoice.py` exists
- Confirm `.env` exists and contains `BUSINESS_NAME`, `BUSINESS_EMAIL`, `BANK_IBAN` — if any are blank or missing, stop and list exactly what's needed
- If dependencies are missing, say: "Run: pip install fpdf2 python-dotenv"

**2. Collect inputs**
Ask Mohamed for any inputs not already provided:

| Input | Required | Default |
|-------|----------|---------|
| Client name | Yes | — |
| Project name | Yes | — |
| Services list (description + amount per line) | Yes | — |
| Due date | Yes | — |
| VAT applicable? | Yes (confirm explicitly) | No |
| VAT rate | Only if VAT = yes | — |
| Invoice number | No | Auto: `INV-YYYYMMDD-HHMM` |
| Issue date | No | Today |

For services: collect them conversationally (e.g. "Workflow build — $2,500") and format as JSON internally. Show the list back to Mohamed and confirm before running.

**3. Confirm before running**
Show a summary of all inputs. Wait for confirmation. Do not run the script until Mohamed says yes.

**4. Run the script**
```bash
python "equipment/generate-invoice.py" \
  --client "CLIENT_NAME" \
  --project "PROJECT_NAME" \
  --services '[{"description": "...", "amount": 0}]' \
  --due-date "DD Month YYYY" \
  [--invoice-number "INV-XXX"] \
  [--issue-date "DD Month YYYY"] \
  [--vat] [--vat-rate 15]
```

Run from the project root directory.

**5. Report**
Say: "Invoice saved at `live/invoices/[filename]`. Total: [amount]. Due: [date]. Upload to Google Drive when ready — nothing has been sent."

---

## Failure Handling

| Problem | Action |
|---------|--------|
| Missing .env values | List exactly what's missing. Stop. |
| `fpdf2` not installed | "Run: pip install fpdf2 python-dotenv" |
| Invalid services format | Show correct JSON example: `[{"description": "Service name", "amount": 1000}]` |
| Script error / unwritable dir | Report the error verbatim. Do not retry without checking the root cause. |

---

## Notes
- VAT: always confirm explicitly — do not assume
- Currency defaults to USD; override by setting `CURRENCY` in `.env`
- Override auto-generated invoice number with `--invoice-number` for sequential numbering
- Google Drive is the final destination. Local copy is a working draft.

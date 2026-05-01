---
name: generate-quote
description: Generate a professional PDF quote for a prospective AGENCINA client. Saves PDF + JSON sidecar to live/quotes/. Also handles converting an accepted quote to an invoice.
when_to_use: Triggered by '/generate-quote' or when Mohamed says "generate quote", "create quote", "quote for [client]", "send a quote", or "convert quote to invoice".
argument-hint: (optional) client name, project name, or "convert [quote file]"
disable-model-invocation: false
allowed-tools: Bash Write
---

Generate a professional PDF quote using `equipment/generate-quote.py`. On acceptance, convert to invoice using `equipment/convert-quote.py`. Collect all inputs, run pre-flight checks, execute the script, report back. Nothing is sent automatically.

---

## Mode A — Generate Quote

**1. Pre-flight checks**
- Confirm `equipment/generate-quote.py` exists
- Confirm `.env` has `BUSINESS_NAME` and `BUSINESS_EMAIL` — if missing, stop and list what's needed
- If dependencies missing: "Run: pip install fpdf2 python-dotenv"

**2. Collect inputs**

| Input | Required | Default |
|-------|----------|---------|
| Client name | Yes | — |
| Project name | Yes | — |
| Scope / notes | Yes | — |
| Timeline | Yes | — |
| Assumptions | Yes | — |
| T&Cs | No | `.env` `DEFAULT_TERMS` |
| Services list (description, amount, optional?) | Yes | — |
| Validity period | No | 30 days |
| VAT applicable? | Yes (confirm explicitly) | No |
| VAT rate | Only if VAT = yes | — |
| Quote number | No | Auto: `QUO-YYYYMMDD-HHMM` |

For services: collect conversationally, ask whether each item is required or optional. Show the full list back to Mohamed and confirm before running.

**3. Confirm before running**
Show a full summary. Wait for explicit confirmation.

**4. Run the script**
```bash
python "equipment/generate-quote.py" \
  --client "CLIENT_NAME" \
  --project "PROJECT_NAME" \
  --scope "SCOPE" \
  --timeline "TIMELINE" \
  --assumptions "ASSUMPTIONS" \
  --terms "TERMS" \
  --services '[{"description": "...", "amount": 0, "optional": false}]' \
  [--validity-days 30] \
  [--vat] [--vat-rate 15]
```

Run from the project root directory.

**5. Report**
Say: "Quote saved at `live/quotes/[filename]`. Required total: [amount]. Valid until: [date]. JSON sidecar also saved for conversion. Review and send when ready — nothing has been sent."

---

## Mode B — Convert Accepted Quote to Invoice

Triggered when Mohamed says "convert quote", "[client] accepted", or "make invoice from quote".

**1. Identify the quote file**
If not specified: list files in `live/quotes/` and ask which to convert.

**2. Confirm optional items**
Ask: "Include all optional items, or required only?"

**3. Run conversion**
```bash
# Required items only (default):
python "equipment/convert-quote.py" --quote "live/quotes/QUO-XXXXXX_client-name.json"

# Include optional items:
python "equipment/convert-quote.py" --quote "live/quotes/QUO-XXXXXX_client-name.json" --accept-optional

# Custom due date:
python "equipment/convert-quote.py" --quote "..." [--due-date "DD Month YYYY"]
```

**4. Report**
Say: "Invoice saved at `live/invoices/[filename]`. Total: [amount]. Due date: [date]. Upload to Google Drive when ready."

---

## Failure Handling

| Problem | Action |
|---------|--------|
| Missing .env values | List what's missing. Stop. |
| `fpdf2` not installed | "Run: pip install fpdf2 python-dotenv" |
| Invalid services JSON | Show correct format: `[{"description": "Workflow build", "amount": 2500, "optional": false}]` |
| JSON sidecar not found (conversion) | "Can't find quote file. Check path: live/quotes/" |
| Script error | Report verbatim. Do not retry without checking root cause. |

---

## Notes
- Optional items appear in the PDF marked "(Optional)" — client sees included vs. add-on
- JSON sidecar is the source of truth for conversion — do not edit the PDF manually
- Validity defaults to 30 days; override with `--validity-days`
- Currency defaults to USD; override with `CURRENCY` in `.env`

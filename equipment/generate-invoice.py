#!/usr/bin/env python3
"""
generate-invoice.py
Generate a PDF invoice for AGENCINA clients.

Usage (direct args):
  python generate-invoice.py --client "Acme Corp" --project "CRM Automation" \
    --services '[{"description": "Workflow build", "amount": 2500}]' \
    --due-date "30 May 2026"

Usage (JSON input file):
  python generate-invoice.py --input invoice_data.json

Dependencies: fpdf2, python-dotenv
Install: pip install fpdf2 python-dotenv
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

BUSINESS_NAME = os.getenv("BUSINESS_NAME", "AGENCINA")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "")
BANK_NAME = os.getenv("BANK_NAME", "")
BANK_ACCOUNT = os.getenv("BANK_ACCOUNT", "")
BANK_IBAN = os.getenv("BANK_IBAN", "")
BANK_SWIFT = os.getenv("BANK_SWIFT", "")
CURRENCY = os.getenv("CURRENCY", "USD")
DEFAULT_VAT_RATE = float(os.getenv("DEFAULT_VAT_RATE", "0"))

REQUIRED_ENV = ["BUSINESS_NAME", "BUSINESS_EMAIL", "BANK_IBAN"]


def check_env():
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        print("ERROR: Missing required .env values:")
        for k in missing:
            print(f"  {k}=")
        print("\nFill these in your .env file before generating invoices.")
        sys.exit(1)


class InvoicePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"{BUSINESS_NAME}  |  {BUSINESS_EMAIL}", align="C")


def generate_invoice(
    client_name: str,
    project_name: str,
    services: list,
    due_date: str,
    invoice_number: str = None,
    issue_date: str = None,
    apply_vat: bool = False,
    vat_rate: float = None,
    output_dir: str = "live/invoices",
) -> str:
    check_env()

    if not invoice_number:
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M')}"
    if not issue_date:
        issue_date = date.today().strftime("%d %B %Y")
    if vat_rate is None:
        vat_rate = DEFAULT_VAT_RATE

    C_DARK = (30, 30, 30)
    C_MID = (110, 110, 110)
    C_LIGHT = (220, 220, 220)
    C_BLACK = (10, 10, 10)
    C_WHITE = (255, 255, 255)
    C_ROW_ALT = (248, 248, 248)

    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ── Business header ──────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 12, BUSINESS_NAME, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    for detail in [BUSINESS_ADDRESS, BUSINESS_EMAIL, BUSINESS_PHONE]:
        if detail:
            pdf.cell(0, 5, detail, ln=True)

    pdf.ln(6)
    pdf.set_draw_color(*C_LIGHT)
    pdf.set_line_width(0.4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── Invoice meta ─────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_DARK)
    pdf.cell(100, 10, "INVOICE", ln=False)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    meta_x = 130
    for label, value in [
        ("Invoice No:", invoice_number),
        ("Issue Date:", issue_date),
        ("Due Date:", due_date),
    ]:
        pdf.set_x(meta_x)
        pdf.cell(35, 6, label, ln=False)
        pdf.set_text_color(*C_DARK)
        pdf.cell(0, 6, value, ln=True)
        pdf.set_text_color(*C_MID)

    pdf.ln(6)

    # ── Bill To ───────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "BILL TO", ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 6, client_name, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, f"Project: {project_name}", ln=True)

    pdf.ln(8)

    # ── Services table ────────────────────────────────────────────────────────
    pdf.set_fill_color(*C_BLACK)
    pdf.set_text_color(*C_WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(140, 8, "  Description", fill=True, ln=False)
    pdf.cell(0, 8, f"Amount ({CURRENCY})", fill=True, ln=True, align="R")

    subtotal = 0.0
    for i, svc in enumerate(services):
        pdf.set_fill_color(*C_ROW_ALT) if i % 2 else pdf.set_fill_color(*C_WHITE)
        pdf.set_text_color(*C_DARK)
        pdf.set_font("Helvetica", "", 9)
        amount = float(svc["amount"])
        subtotal += amount
        pdf.cell(140, 7, f"  {svc['description']}", fill=True, ln=False)
        pdf.cell(0, 7, f"{amount:,.2f}", fill=True, ln=True, align="R")

    pdf.ln(3)

    # ── Totals ────────────────────────────────────────────────────────────────
    col_w = 140
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(col_w, 6, "Subtotal", ln=False, align="R")
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 6, f"{CURRENCY} {subtotal:,.2f}", ln=True, align="R")

    total = subtotal
    if apply_vat and vat_rate > 0:
        vat_amount = subtotal * (vat_rate / 100)
        total += vat_amount
        pdf.set_text_color(*C_MID)
        pdf.cell(col_w, 6, f"VAT ({vat_rate:.0f}%)", ln=False, align="R")
        pdf.set_text_color(*C_DARK)
        pdf.cell(0, 6, f"{CURRENCY} {vat_amount:,.2f}", ln=True, align="R")

    pdf.set_draw_color(*C_LIGHT)
    pdf.line(col_w + 20, pdf.get_y() + 1, 190, pdf.get_y() + 1)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_DARK)
    pdf.cell(col_w, 8, "TOTAL DUE", ln=False, align="R")
    pdf.cell(0, 8, f"{CURRENCY} {total:,.2f}", ln=True, align="R")

    pdf.ln(12)

    # ── Payment details ───────────────────────────────────────────────────────
    if any([BANK_NAME, BANK_ACCOUNT, BANK_IBAN, BANK_SWIFT]):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*C_MID)
        pdf.cell(0, 5, "PAYMENT DETAILS", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*C_DARK)
        for label, value in [
            ("Bank:", BANK_NAME),
            ("Account:", BANK_ACCOUNT),
            ("IBAN:", BANK_IBAN),
            ("SWIFT/BIC:", BANK_SWIFT),
            ("Reference:", invoice_number),
        ]:
            if value:
                pdf.cell(30, 5, label, ln=False)
                pdf.cell(0, 5, value, ln=True)

    # ── Save ──────────────────────────────────────────────────────────────────
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_client = "".join(c if c.isalnum() else "-" for c in client_name).lower().strip("-")
    filename = f"{invoice_number}_{safe_client}.pdf"
    filepath = Path(output_dir) / filename
    pdf.output(str(filepath))

    print(f"\nInvoice generated: {filepath}")
    print(f"  Client:   {client_name}")
    print(f"  Project:  {project_name}")
    print(f"  Total:    {CURRENCY} {total:,.2f}")
    print(f"  Due:      {due_date}")
    print(f"\nReady for review. Upload to Google Drive when approved.")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Generate AGENCINA invoice PDF")
    parser.add_argument("--input", help="Path to JSON file with invoice data")
    parser.add_argument("--client", help="Client name")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--services", help='JSON array: [{"description": "...", "amount": 1000}]')
    parser.add_argument("--due-date", dest="due_date", help="Due date (e.g. '30 May 2026')")
    parser.add_argument("--invoice-number", dest="invoice_number", help="Invoice number (auto if omitted)")
    parser.add_argument("--issue-date", dest="issue_date", help="Issue date (defaults to today)")
    parser.add_argument("--vat", action="store_true", help="Apply VAT")
    parser.add_argument("--vat-rate", dest="vat_rate", type=float, help="VAT rate as a percentage (e.g. 15)")
    parser.add_argument("--output-dir", dest="output_dir", default="live/invoices", help="Output directory")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        if not all([args.client, args.project, args.services, args.due_date]):
            parser.error("Provide --client, --project, --services, and --due-date (or use --input with a JSON file).")
        try:
            services = json.loads(args.services)
        except json.JSONDecodeError:
            print('ERROR: --services must be valid JSON, e.g. \'[{"description": "Workflow build", "amount": 2500}]\'')
            sys.exit(1)
        data = {
            "client_name": args.client,
            "project_name": args.project,
            "services": services,
            "due_date": args.due_date,
            "invoice_number": args.invoice_number,
            "issue_date": args.issue_date,
            "apply_vat": args.vat,
            "vat_rate": args.vat_rate,
            "output_dir": args.output_dir,
        }

    generate_invoice(**{k: v for k, v in data.items() if v is not None})


if __name__ == "__main__":
    main()

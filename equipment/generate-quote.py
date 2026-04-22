#!/usr/bin/env python3
"""
generate-quote.py
Generate a PDF quote + JSON sidecar for AGENCINA clients.

Usage:
  python generate-quote.py \
    --client "Acme Corp" --project "CRM Automation" \
    --scope "Build a smart CRM workflow..." \
    --timeline "4 weeks from project start" \
    --assumptions "Client provides all assets by day 1" \
    --terms "50% upfront, 50% on delivery. Net 14." \
    --services '[{"description": "Workflow build", "amount": 2500, "optional": false}]'

Dependencies: fpdf2, python-dotenv
Install: pip install fpdf2 python-dotenv
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

BUSINESS_NAME = os.getenv("BUSINESS_NAME", "AGENCINA")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "")
CURRENCY = os.getenv("CURRENCY", "USD")
DEFAULT_VAT_RATE = float(os.getenv("DEFAULT_VAT_RATE", "0"))
DEFAULT_TERMS = os.getenv(
    "DEFAULT_TERMS",
    "50% due upon project start. Remaining 50% due on delivery. Net 14 payment terms. "
    "Quote valid for 30 days from issue date. Up to 2 rounds of revisions included.",
)

REQUIRED_ENV = ["BUSINESS_NAME", "BUSINESS_EMAIL"]


def check_env():
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        print("ERROR: Missing required .env values:")
        for k in missing:
            print(f"  {k}=")
        print("\nFill these in your .env file before generating quotes.")
        sys.exit(1)


class QuotePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"{BUSINESS_NAME}  |  {BUSINESS_EMAIL}", align="C")


def generate_quote(
    client_name: str,
    project_name: str,
    services: list,
    scope: str,
    timeline: str,
    assumptions: str,
    terms: str = None,
    quote_number: str = None,
    issue_date: str = None,
    validity_days: int = 30,
    apply_vat: bool = False,
    vat_rate: float = None,
    output_dir: str = "live/quotes",
) -> dict:
    check_env()

    if not quote_number:
        quote_number = f"QUO-{datetime.now().strftime('%Y%m%d-%H%M')}"
    if not issue_date:
        issue_date_obj = date.today()
        issue_date = issue_date_obj.strftime("%d %B %Y")
    else:
        issue_date_obj = datetime.strptime(issue_date, "%d %B %Y").date()
    if vat_rate is None:
        vat_rate = DEFAULT_VAT_RATE
    if not terms:
        terms = DEFAULT_TERMS

    valid_until = (issue_date_obj + timedelta(days=validity_days)).strftime("%d %B %Y")

    C_DARK = (30, 30, 30)
    C_MID = (110, 110, 110)
    C_LIGHT = (220, 220, 220)
    C_BLACK = (10, 10, 10)
    C_WHITE = (255, 255, 255)
    C_ROW_ALT = (248, 248, 248)
    C_OPTIONAL = (160, 160, 160)

    pdf = QuotePDF()
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

    # ── Quote title + meta ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_DARK)
    pdf.cell(100, 10, "QUOTATION", ln=False)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    meta_x = 130
    for label, value in [
        ("Quote No:", quote_number),
        ("Issue Date:", issue_date),
        ("Valid Until:", valid_until),
    ]:
        pdf.set_x(meta_x)
        pdf.cell(35, 6, label, ln=False)
        pdf.set_text_color(*C_DARK)
        pdf.cell(0, 6, value, ln=True)
        pdf.set_text_color(*C_MID)

    pdf.ln(6)

    # ── Prepared for ─────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "PREPARED FOR", ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 6, client_name, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, f"Project: {project_name}", ln=True)

    pdf.ln(8)

    # ── Scope ─────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "SCOPE OF WORK", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_DARK)
    pdf.multi_cell(0, 5, scope)
    pdf.ln(4)

    # ── Timeline ──────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "TIMELINE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_DARK)
    pdf.multi_cell(0, 5, timeline)
    pdf.ln(4)

    # ── Assumptions ───────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "ASSUMPTIONS", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_DARK)
    pdf.multi_cell(0, 5, assumptions)
    pdf.ln(6)

    # ── Services table ────────────────────────────────────────────────────────
    pdf.set_fill_color(*C_BLACK)
    pdf.set_text_color(*C_WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(130, 8, "  Service", fill=True, ln=False)
    pdf.cell(20, 8, "Type", fill=True, ln=False, align="C")
    pdf.cell(0, 8, f"Amount ({CURRENCY})", fill=True, ln=True, align="R")

    required_total = 0.0
    optional_total = 0.0

    for i, svc in enumerate(services):
        is_optional = svc.get("optional", False)
        pdf.set_fill_color(*C_ROW_ALT) if i % 2 else pdf.set_fill_color(*C_WHITE)
        amount = float(svc["amount"])

        if is_optional:
            pdf.set_text_color(*C_OPTIONAL)
            optional_total += amount
            type_label = "Optional"
        else:
            pdf.set_text_color(*C_DARK)
            required_total += amount
            type_label = "Included"

        pdf.set_font("Helvetica", "", 9)
        pdf.cell(130, 7, f"  {svc['description']}", fill=True, ln=False)
        pdf.cell(20, 7, type_label, fill=True, ln=False, align="C")
        pdf.cell(0, 7, f"{amount:,.2f}", fill=True, ln=True, align="R")

    pdf.ln(3)

    # ── Totals ────────────────────────────────────────────────────────────────
    col_w = 150
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)

    pdf.cell(col_w, 6, "Required subtotal", ln=False, align="R")
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 6, f"{CURRENCY} {required_total:,.2f}", ln=True, align="R")

    if optional_total > 0:
        pdf.set_text_color(*C_OPTIONAL)
        pdf.cell(col_w, 6, "Optional subtotal", ln=False, align="R")
        pdf.cell(0, 6, f"{CURRENCY} {optional_total:,.2f}", ln=True, align="R")

    total = required_total
    if apply_vat and vat_rate > 0:
        vat_amount = total * (vat_rate / 100)
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
    pdf.cell(col_w, 8, "TOTAL (required)", ln=False, align="R")
    pdf.cell(0, 8, f"{CURRENCY} {total:,.2f}", ln=True, align="R")

    pdf.ln(10)

    # ── T&Cs ─────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "TERMS & CONDITIONS", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*C_MID)
    pdf.multi_cell(0, 4, terms)

    # ── Save PDF ──────────────────────────────────────────────────────────────
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_client = "".join(c if c.isalnum() else "-" for c in client_name).lower().strip("-")
    base_name = f"{quote_number}_{safe_client}"
    pdf_path = Path(output_dir) / f"{base_name}.pdf"
    json_path = Path(output_dir) / f"{base_name}.json"
    pdf.output(str(pdf_path))

    # ── Save JSON sidecar ─────────────────────────────────────────────────────
    sidecar = {
        "quote_number": quote_number,
        "client_name": client_name,
        "project_name": project_name,
        "issue_date": issue_date,
        "valid_until": valid_until,
        "scope": scope,
        "timeline": timeline,
        "assumptions": assumptions,
        "terms": terms,
        "services": services,
        "apply_vat": apply_vat,
        "vat_rate": vat_rate,
        "currency": CURRENCY,
        "required_total": required_total,
        "optional_total": optional_total,
    }
    with open(json_path, "w") as f:
        json.dump(sidecar, f, indent=2)

    print(f"\nQuote generated:")
    print(f"  PDF:    {pdf_path}")
    print(f"  JSON:   {json_path}")
    print(f"  Client: {client_name}")
    print(f"  Total (required): {CURRENCY} {total:,.2f}")
    if optional_total > 0:
        print(f"  Optional add-ons: {CURRENCY} {optional_total:,.2f}")
    print(f"  Valid until: {valid_until}")
    print(f"\nReview and send when ready. To convert to invoice: python equipment/convert-quote.py --quote {json_path}")

    return {"pdf": str(pdf_path), "json": str(json_path)}


def main():
    parser = argparse.ArgumentParser(description="Generate AGENCINA quote PDF")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--scope", required=True, help="Scope of work description")
    parser.add_argument("--timeline", required=True, help="Project timeline")
    parser.add_argument("--assumptions", required=True, help="Assumptions and conditions")
    parser.add_argument("--services", required=True, help='JSON: [{"description":"...", "amount": 1000, "optional": false}]')
    parser.add_argument("--terms", help="T&Cs (uses DEFAULT_TERMS from .env if omitted)")
    parser.add_argument("--quote-number", dest="quote_number", help="Quote number (auto if omitted)")
    parser.add_argument("--issue-date", dest="issue_date", help="Issue date (defaults to today)")
    parser.add_argument("--validity-days", dest="validity_days", type=int, default=30, help="Days quote is valid (default: 30)")
    parser.add_argument("--vat", action="store_true", help="Apply VAT")
    parser.add_argument("--vat-rate", dest="vat_rate", type=float, help="VAT rate as percentage")
    parser.add_argument("--output-dir", dest="output_dir", default="live/quotes")
    args = parser.parse_args()

    try:
        services = json.loads(args.services)
    except json.JSONDecodeError:
        print('ERROR: --services must be valid JSON, e.g. \'[{"description": "Build", "amount": 2500, "optional": false}]\'')
        sys.exit(1)

    generate_quote(
        client_name=args.client,
        project_name=args.project,
        services=services,
        scope=args.scope,
        timeline=args.timeline,
        assumptions=args.assumptions,
        terms=args.terms,
        quote_number=args.quote_number,
        issue_date=args.issue_date,
        validity_days=args.validity_days,
        apply_vat=args.vat,
        vat_rate=args.vat_rate,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

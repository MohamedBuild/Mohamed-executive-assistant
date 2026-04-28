#!/usr/bin/env python3
"""
generate-proposal.py
Generate a PDF proposal + JSON sidecar for AGENCINA clients.

Usage:
  python generate-proposal.py \
    --client "Sahel Cafe Group" --contact "Karim Aoun" --project "Ops Automation" \
    --scope "Build end-to-end order and inventory workflows..." \
    --deliverables '[{"description": "Workflow build", "optional": false}, {"description": "Training", "optional": true}]' \
    --value 12000 --payment "50-50" \
    --timeline "6 weeks from project start" --start-date "12 May 2026"

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
CURRENCY = os.getenv("CURRENCY", "USD")
DEFAULT_LEGAL_TEXT = os.getenv(
    "DEFAULT_LEGAL_TEXT",
    "Payment terms as per payment structure above. All deliverables remain the intellectual "
    "property of AGENCINA until final payment is received in full. This proposal is valid for "
    "14 days from issue date. AGENCINA reserves the right to pause work if payment milestones "
    "are missed by more than 7 days. Up to [REVISION_ROUNDS] rounds of revisions are included "
    "within the agreed scope. Changes outside the agreed scope will be quoted separately.",
)

REQUIRED_ENV = ["BUSINESS_NAME", "BUSINESS_EMAIL"]

PAYMENT_LABELS = {
    "upfront": "100% due upon project start.",
    "50-50": "50% due upon project start. Remaining 50% due on delivery.",
    "on-delivery": "100% due on final delivery.",
}


def check_env():
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        print("ERROR: Missing required .env values:")
        for k in missing:
            print(f"  {k}=")
        print("\nFill these in your .env file before generating proposals.")
        sys.exit(1)


def slugify(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text).lower().strip("-")


def s(text: str) -> str:
    """Replace Unicode characters unsupported by fpdf2's built-in Helvetica font."""
    return (
        str(text)
        .replace("—", "-")
        .replace("–", "-")
        .replace("‘", "'")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
    )


class ProposalPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"{BUSINESS_NAME}  |  {BUSINESS_EMAIL}", align="C")


def generate_proposal(
    client_name: str,
    contact_name: str,
    project_name: str,
    scope: str,
    deliverables: list,
    value: float,
    payment: str,
    timeline: str,
    start_date: str,
    assumptions: str = "",
    revision_rounds: int = 2,
    proposal_number: str = None,
    issue_date: str = None,
    apply_vat: bool = False,
    vat_rate: float = 0.0,
    legal_text: str = None,
    output_dir: str = "live/proposals",
) -> dict:
    check_env()

    if not proposal_number:
        proposal_number = f"PROP-{datetime.now().strftime('%Y%m%d-%H%M')}"
    if not issue_date:
        issue_date = date.today().strftime("%d %B %Y")
    if not legal_text:
        legal_text = DEFAULT_LEGAL_TEXT.replace("[REVISION_ROUNDS]", str(revision_rounds))

    payment_label = PAYMENT_LABELS.get(payment, payment)

    vat_amount = 0.0
    total = value
    if apply_vat and vat_rate > 0:
        vat_amount = value * (vat_rate / 100)
        total = value + vat_amount

    C_DARK = (30, 30, 30)
    C_MID = (110, 110, 110)
    C_LIGHT = (220, 220, 220)
    C_BLACK = (10, 10, 10)
    C_WHITE = (255, 255, 255)
    C_ROW_ALT = (248, 248, 248)
    C_OPTIONAL = (160, 160, 160)

    pdf = ProposalPDF()
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

    # ── Proposal title + meta ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_DARK)
    pdf.cell(100, 10, "PROPOSAL", ln=False)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    meta_x = 130
    for label, val in [
        ("Proposal No:", proposal_number),
        ("Issue Date:", issue_date),
        ("Prepared for:", client_name),
        ("Contact:", contact_name),
    ]:
        pdf.set_x(meta_x)
        pdf.cell(35, 6, label, ln=False)
        pdf.set_text_color(*C_DARK)
        pdf.cell(0, 6, val, ln=True)
        pdf.set_text_color(*C_MID)

    pdf.ln(8)

    # ── Scope of Work ─────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "SCOPE OF WORK", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_DARK)
    pdf.multi_cell(0, 5, s(scope))
    pdf.ln(6)

    # ── Deliverables table ────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "DELIVERABLES", ln=True)
    pdf.ln(2)

    pdf.set_fill_color(*C_BLACK)
    pdf.set_text_color(*C_WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(150, 8, "  Deliverable", fill=True, ln=False)
    pdf.cell(0, 8, "Type", fill=True, ln=True, align="C")

    for i, item in enumerate(deliverables):
        is_optional = item.get("optional", False)
        pdf.set_fill_color(*C_ROW_ALT) if i % 2 else pdf.set_fill_color(*C_WHITE)

        if is_optional:
            pdf.set_text_color(*C_OPTIONAL)
            type_label = "Optional"
        else:
            pdf.set_text_color(*C_DARK)
            type_label = "Included"

        pdf.set_font("Helvetica", "", 9)
        pdf.cell(150, 7, s(f"  {item['description']}"), fill=True, ln=False)
        pdf.cell(0, 7, type_label, fill=True, ln=True, align="C")

    pdf.ln(6)

    # ── Investment ────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "INVESTMENT", ln=True)
    pdf.ln(2)

    col_w = 150
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(col_w, 6, "Project fee", ln=False, align="R")
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 6, f"{CURRENCY} {value:,.2f}", ln=True, align="R")

    if apply_vat and vat_rate > 0:
        pdf.set_text_color(*C_MID)
        pdf.cell(col_w, 6, f"VAT ({vat_rate:.0f}%)", ln=False, align="R")
        pdf.set_text_color(*C_DARK)
        pdf.cell(0, 6, f"{CURRENCY} {vat_amount:,.2f}", ln=True, align="R")

    pdf.set_draw_color(*C_LIGHT)
    pdf.line(col_w + 20, pdf.get_y() + 1, 190, pdf.get_y() + 1)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*C_DARK)
    pdf.cell(col_w, 8, "TOTAL", ln=False, align="R")
    pdf.cell(0, 8, f"{CURRENCY} {total:,.2f}", ln=True, align="R")

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, s(f"Payment: {payment_label}"), ln=True)
    pdf.cell(0, 5, f"Revisions: Up to {revision_rounds} rounds included.", ln=True)
    pdf.ln(4)

    # ── Timeline ──────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "TIMELINE", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_DARK)
    pdf.multi_cell(0, 5, s(timeline))
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, s(f"Estimated start: {start_date}"), ln=True)
    pdf.ln(4)

    # ── Assumptions (only if provided) ───────────────────────────────────────
    if assumptions:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*C_MID)
        pdf.cell(0, 5, "ASSUMPTIONS", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*C_DARK)
        pdf.multi_cell(0, 5, s(assumptions))
        pdf.ln(4)

    # ── Legal ─────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "TERMS & CONDITIONS", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*C_MID)
    pdf.multi_cell(0, 4, s(legal_text))

    # ── Save PDF ──────────────────────────────────────────────────────────────
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    base_name = f"{proposal_number}_{slugify(client_name)}"
    pdf_path = Path(output_dir) / f"{base_name}.pdf"
    json_path = Path(output_dir) / f"{base_name}.json"
    pdf.output(str(pdf_path))

    # ── Save JSON sidecar ─────────────────────────────────────────────────────
    sidecar = {
        "proposal_number": proposal_number,
        "client_name": client_name,
        "contact_name": contact_name,
        "project_name": project_name,
        "issue_date": issue_date,
        "start_date": start_date,
        "scope": scope,
        "deliverables": deliverables,
        "value": value,
        "payment_structure": payment,
        "timeline": timeline,
        "assumptions": assumptions,
        "revision_rounds": revision_rounds,
        "apply_vat": apply_vat,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "total": total,
        "currency": CURRENCY,
        "legal_text": legal_text,
    }
    with open(json_path, "w") as f:
        json.dump(sidecar, f, indent=2)

    print(f"\nProposal generated:")
    print(f"  PDF:     {pdf_path}")
    print(f"  JSON:    {json_path}")
    print(f"  Client:  {client_name}")
    print(f"  Contact: {contact_name}")
    print(f"  Fee:     {CURRENCY} {total:,.2f}")
    print(f"  Payment: {payment_label}")
    print(f"  Start:   {start_date}")
    print(f"\nReview before sending.")

    return {"pdf": str(pdf_path), "json": str(json_path)}


def main():
    parser = argparse.ArgumentParser(description="Generate AGENCINA proposal PDF")
    parser.add_argument("--client", required=True, help="Client business name")
    parser.add_argument("--contact", required=True, help="Contact person name")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--scope", required=True, help="Scope of work description")
    parser.add_argument("--deliverables", required=True, help='JSON: [{"description":"...", "optional": false}]')
    parser.add_argument("--value", required=True, type=float, help="Total project fee (no default — must be confirmed)")
    parser.add_argument("--payment", required=True, choices=["upfront", "50-50", "on-delivery"], help="Payment structure")
    parser.add_argument("--timeline", required=True, help="Project timeline string")
    parser.add_argument("--start-date", dest="start_date", required=True, help="Estimated or confirmed start date (DD Month YYYY)")
    parser.add_argument("--assumptions", default="", help="Conditions this proposal depends on")
    parser.add_argument("--revision-rounds", dest="revision_rounds", type=int, default=2, help="Revision rounds included (default: 2)")
    parser.add_argument("--proposal-number", dest="proposal_number", help="Proposal number (auto if omitted)")
    parser.add_argument("--issue-date", dest="issue_date", help="Issue date (defaults to today)")
    parser.add_argument("--vat", action="store_true", help="Apply VAT")
    parser.add_argument("--vat-rate", dest="vat_rate", type=float, default=0.0, help="VAT rate as percentage")
    parser.add_argument("--legal-text", dest="legal_text", help="Override default legal boilerplate")
    parser.add_argument("--output-dir", dest="output_dir", default="live/proposals")
    args = parser.parse_args()

    try:
        deliverables = json.loads(args.deliverables)
    except json.JSONDecodeError:
        print('ERROR: --deliverables must be valid JSON, e.g. \'[{"description": "Workflow build", "optional": false}]\'')
        sys.exit(1)

    generate_proposal(
        client_name=args.client,
        contact_name=args.contact,
        project_name=args.project,
        scope=args.scope,
        deliverables=deliverables,
        value=args.value,
        payment=args.payment,
        timeline=args.timeline,
        start_date=args.start_date,
        assumptions=args.assumptions,
        revision_rounds=args.revision_rounds,
        proposal_number=args.proposal_number,
        issue_date=args.issue_date,
        apply_vat=args.vat,
        vat_rate=args.vat_rate,
        legal_text=args.legal_text,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

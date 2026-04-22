#!/usr/bin/env python3
"""
generate-onboarding-pack.py
Generate a client onboarding pack: project folder structure, onboarding
questionnaire PDF, welcome email draft, and CRM entry.

Usage:
  python equipment/generate-onboarding-pack.py \
    --client "Acme Corp" --contact "Jane Smith" --email "jane@acme.com" \
    --project "CRM Automation" --project-type "Agentic Workflow" \
    --goals "Automate lead tracking and follow-ups" \
    --timeline "6 weeks from project start" \
    --phone "+1234567890" --scope "..." --budget "5000" \
    --payment 50-50 [--nda]

Dependencies: fpdf2, python-dotenv
"""

import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

BUSINESS_NAME = os.getenv("BUSINESS_NAME", "AGENCINA")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "")

REQUIRED_ENV = ["BUSINESS_NAME", "BUSINESS_EMAIL"]

CRM_PATH = "live/crm.csv"
CRM_HEADERS = [
    "date_added", "client", "contact", "email", "phone",
    "project_name", "project_type", "goals", "timeline", "budget",
    "payment_structure", "status", "project_folder",
]

C_DARK = (30, 30, 30)
C_MID = (110, 110, 110)
C_LIGHT = (220, 220, 220)
C_BLACK = (10, 10, 10)
C_WHITE = (255, 255, 255)


def check_env():
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        print("ERROR: Missing required .env values:")
        for k in missing:
            print(f"  {k}=")
        print("\nFill these in your .env file before running.")
        sys.exit(1)


def slugify(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name).lower().strip("-")


class OnboardingPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"{BUSINESS_NAME}  |  {BUSINESS_EMAIL}", align="C")


def _section_header(pdf: FPDF, title: str):
    pdf.set_fill_color(*C_BLACK)
    pdf.set_text_color(*C_WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 8, f"  {title}", fill=True, ln=True)
    pdf.ln(2)


def _field(pdf: FPDF, label: str, prefilled: str = "", lines: int = 1):
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, label, ln=True)

    if prefilled:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*C_DARK)
        pdf.multi_cell(0, 5, prefilled)
    else:
        pdf.set_draw_color(*C_LIGHT)
        pdf.set_line_width(0.3)
        for _ in range(lines):
            y = pdf.get_y() + 7
            pdf.line(20, y, 190, y)
            pdf.ln(8)

    pdf.ln(2)


def generate_questionnaire(
    client_name: str,
    contact_name: str,
    project_name: str,
    project_type: str,
    goals: str,
    timeline: str,
    scope: str,
    output_path: Path,
) -> None:
    pdf = OnboardingPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Business header
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 12, BUSINESS_NAME, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    if BUSINESS_EMAIL:
        pdf.cell(0, 5, BUSINESS_EMAIL, ln=True)

    pdf.ln(4)
    pdf.set_draw_color(*C_LIGHT)
    pdf.set_line_width(0.4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C_DARK)
    pdf.cell(0, 10, "CLIENT ONBOARDING FORM", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 6, f"Project: {project_name}  |  {date.today().strftime('%d %B %Y')}", ln=True)
    pdf.ln(8)

    # Section 1 — Business details
    _section_header(pdf, "YOUR BUSINESS")
    _field(pdf, "Business / Organisation Name", client_name)
    _field(pdf, "Contact Name", contact_name)
    _field(pdf, "Email Address")
    _field(pdf, "Phone Number")
    _field(pdf, "Website")
    _field(pdf, "Business Address (if relevant)")

    # Section 2 — Project
    _section_header(pdf, "PROJECT DETAILS")
    _field(pdf, "Project / Engagement Type", project_type)
    _field(pdf, "Goals & Objectives", goals)
    _field(pdf, "Scope of Work", scope if scope else "", lines=3)
    _field(pdf, "Expected Timeline / Key Deadlines", timeline)
    _field(pdf, "Budget Range (if applicable)")
    _field(pdf, "Existing tools or systems we'll be working with?", lines=2)

    # Section 3 — Assets
    _section_header(pdf, "ASSETS & ACCESS REQUIRED")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*C_MID)
    pdf.cell(0, 5, "Tick what you'll be providing and add access notes below:", ln=True)
    pdf.ln(2)

    for item in [
        "Logo files (PNG / SVG / AI)",
        "Brand guidelines",
        "Website / platform access",
        "CRM or database access",
        "Social media account access",
        "Google Workspace / Drive access",
        "Other (specify below)",
    ]:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*C_DARK)
        pdf.cell(6, 6, "[ ]", ln=False)
        pdf.cell(0, 6, item, ln=True)

    pdf.ln(2)
    _field(pdf, "Access notes (share credentials separately — never in this form)", lines=2)

    # Section 4 — Communication
    _section_header(pdf, "COMMUNICATION PREFERENCES")
    _field(pdf, "Preferred channel  (Email / WhatsApp / Slack / Other)")
    _field(pdf, "Expected response time from your side")
    _field(pdf, "Main point of contact on your team")
    _field(pdf, "Other stakeholders to keep in the loop?")

    # Section 5 — Anything else
    _section_header(pdf, "ANYTHING ELSE?")
    _field(pdf, "Constraints, preferences, or context we should know", lines=2)
    _field(pdf, "Questions for AGENCINA?", lines=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))


def create_welcome_email(
    contact_name: str,
    project_name: str,
    payment_structure: str,
    nda: bool,
    output_path: Path,
) -> None:
    first_name = contact_name.split()[0] if contact_name else "there"

    if payment_structure == "upfront":
        payment_step = "3. Complete payment to lock in your start date."
    elif payment_structure == "50-50":
        payment_step = "3. The 50% project start invoice is attached — payment confirms your start date."
    else:
        payment_step = "3. Invoice will follow on delivery as agreed."

    nda_line = "\n- NDA — please sign and return before we exchange any sensitive materials" if nda else ""

    content = f"""Subject: Welcome to AGENCINA — {project_name} kickoff

Hi {first_name},

Really glad to have you on board. Here's what you need to get us started.

**Attached:**
- Onboarding questionnaire — please fill this in and send it back
- Contract (your signed copy){nda_line}

**Next steps:**
1. Complete the onboarding questionnaire and return it.
2. Return the signed contract if you haven't already.
{payment_step}

Once I have those back I'll confirm your start date and we'll kick things off.

Any questions, just reply here.

Mohamed
AGENCINA
{BUSINESS_EMAIL}{chr(10) + BUSINESS_PHONE if BUSINESS_PHONE else ""}

---
[DRAFT — review and attach documents before sending]
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content.strip(), encoding="utf-8")


def create_project_readme(
    client_name: str,
    contact_name: str,
    email: str,
    phone: str,
    project_name: str,
    project_type: str,
    goals: str,
    scope: str,
    timeline: str,
    budget: str,
    payment_structure: str,
    project_dir: Path,
) -> None:
    content = f"""# {project_name}

**Client:** {client_name}
**Contact:** {contact_name} — {email}{f' / {phone}' if phone else ''}
**Project Type:** {project_type}
**Started:** {date.today().strftime('%d %B %Y')}
**Status:** Onboarding

## Goals
{goals}

## Scope
{scope if scope else '— to be confirmed from onboarding form'}

## Timeline
{timeline}

## Budget / Payment
{budget if budget else '— see quote'} | {payment_structure.replace('-', '/')}

## Folder Structure
```
{project_dir.name}/
├── assets/          — logos, brand files, access notes
├── deliverables/    — completed work
├── comms/           — email drafts, meeting notes
└── onboarding/      — questionnaire PDF and client responses
```

## Notes
—
"""
    (project_dir / "README.md").write_text(content.strip(), encoding="utf-8")


def add_crm_row(
    client_name: str,
    contact_name: str,
    email: str,
    phone: str,
    project_name: str,
    project_type: str,
    goals: str,
    timeline: str,
    budget: str,
    payment_structure: str,
    project_folder: str,
) -> None:
    crm_path = Path(CRM_PATH)
    crm_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not crm_path.exists() or crm_path.stat().st_size == 0

    with open(crm_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CRM_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "date_added": date.today().isoformat(),
            "client": client_name,
            "contact": contact_name,
            "email": email,
            "phone": phone,
            "project_name": project_name,
            "project_type": project_type,
            "goals": goals,
            "timeline": timeline,
            "budget": budget,
            "payment_structure": payment_structure,
            "status": "Onboarding",
            "project_folder": project_folder,
        })


def generate_onboarding_pack(
    client_name: str,
    contact_name: str,
    email: str,
    project_name: str,
    project_type: str,
    goals: str,
    timeline: str,
    phone: str = "",
    scope: str = "",
    budget: str = "",
    payment_structure: str = "50-50",
    nda: bool = False,
    live_dir: str = "live",
) -> dict:
    check_env()

    project_slug = slugify(project_name)
    project_dir = Path(live_dir) / project_slug

    # Create folder structure
    for subfolder in ["assets", "deliverables", "comms", "onboarding"]:
        (project_dir / subfolder).mkdir(parents=True, exist_ok=True)

    # Questionnaire PDF
    form_path = project_dir / "onboarding" / f"onboarding-form_{project_slug}.pdf"
    generate_questionnaire(
        client_name=client_name,
        contact_name=contact_name,
        project_name=project_name,
        project_type=project_type,
        goals=goals,
        timeline=timeline,
        scope=scope,
        output_path=form_path,
    )

    # Welcome email draft
    email_path = project_dir / "comms" / "welcome-email.md"
    create_welcome_email(
        contact_name=contact_name,
        project_name=project_name,
        payment_structure=payment_structure,
        nda=nda,
        output_path=email_path,
    )

    # Project README
    create_project_readme(
        client_name=client_name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        project_name=project_name,
        project_type=project_type,
        goals=goals,
        scope=scope,
        timeline=timeline,
        budget=budget,
        payment_structure=payment_structure,
        project_dir=project_dir,
    )

    # CRM entry
    add_crm_row(
        client_name=client_name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        project_name=project_name,
        project_type=project_type,
        goals=goals,
        timeline=timeline,
        budget=budget,
        payment_structure=payment_structure,
        project_folder=str(project_dir),
    )

    print(f"\nOnboarding pack generated:")
    print(f"  Project folder: {project_dir}/")
    print(f"  Questionnaire:  {form_path}")
    print(f"  Welcome email:  {email_path}")
    print(f"  CRM:            {CRM_PATH} (row added)")
    print(f"\nNext steps:")
    print(f"  1. Review {email_path}")
    print(f"  2. Copy templates/contract.md, fill in scope/fees, save to {project_dir}/")
    print(f"  3. Attach contract + questionnaire PDF and send from Gmail")
    if nda:
        print(f"  4. Copy templates/nda.md (if you have one), fill in, and attach")

    return {
        "project_dir": str(project_dir),
        "questionnaire": str(form_path),
        "welcome_email": str(email_path),
        "crm": CRM_PATH,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate AGENCINA client onboarding pack")
    parser.add_argument("--client", required=True, help="Client business name")
    parser.add_argument("--contact", required=True, help="Contact person full name")
    parser.add_argument("--email", required=True, help="Client email address")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--project-type", dest="project_type", required=True,
                        help='Project type (e.g. "Agentic Workflow")')
    parser.add_argument("--goals", required=True, help="Project goals and objectives")
    parser.add_argument("--timeline", required=True, help="Expected timeline and deadlines")
    parser.add_argument("--phone", default="", help="Client phone number")
    parser.add_argument("--scope", default="", help="Scope of work details")
    parser.add_argument("--budget", default="", help="Budget range")
    parser.add_argument("--payment", dest="payment_structure", default="50-50",
                        choices=["upfront", "50-50", "on-delivery"],
                        help="Payment structure (default: 50-50)")
    parser.add_argument("--nda", action="store_true", help="Add NDA note to welcome email")
    parser.add_argument("--live-dir", dest="live_dir", default="live")
    args = parser.parse_args()

    generate_onboarding_pack(
        client_name=args.client,
        contact_name=args.contact,
        email=args.email,
        project_name=args.project,
        project_type=args.project_type,
        goals=args.goals,
        timeline=args.timeline,
        phone=args.phone,
        scope=args.scope,
        budget=args.budget,
        payment_structure=args.payment_structure,
        nda=args.nda,
        live_dir=args.live_dir,
    )


if __name__ == "__main__":
    main()

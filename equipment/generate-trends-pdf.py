"""
generate-trends-pdf.py
Generates a branded AGENCINA research PDF from structured findings data.
Email delivery is handled by the calling agent via Zapier MCP.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

# ── Brand colours ─────────────────────────────────────────────────────────────
DARK    = (15, 15, 25)
ACCENT  = (99, 102, 241)
BG_HERO = (245, 245, 252)
TEXT    = (30, 30, 45)
MUTED   = (120, 120, 144)
WHY_BG  = (235, 235, 250)
DIV     = (210, 210, 228)
WHITE   = (255, 255, 255)


# ── PDF class ─────────────────────────────────────────────────────────────────

class TrendsPDF(FPDF):
    def header(self):
        self.set_fill_color(*DARK)
        self.rect(0, 0, 210, 16, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.set_xy(12, 4)
        self.cell(0, 8, "AGENCINA  —  Research Intelligence", ln=False)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(160, 160, 190)
        self.set_xy(0, 4)
        date_str = datetime.now().strftime("%d %B %Y")
        self.cell(198, 8, date_str, align="R", ln=True)

    def footer(self):
        self.set_y(-13)
        self.set_fill_color(*DARK)
        self.rect(0, self.get_y(), 210, 13, "F")
        self.set_text_color(110, 110, 150)
        self.set_font("Helvetica", "", 7)
        self.set_y(-10)
        self.cell(
            0, 6,
            f"Confidential  —  AGENCINA Internal Research   |   Page {self.page_no()}",
            align="C",
        )


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(data: dict, output_path: Path) -> None:
    pdf = TrendsPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(14, 20, 14)

    title    = data["title"]
    subtitle = data.get("subtitle", "")
    intro    = data.get("intro", "")
    findings = data["findings"]

    # ── Hero block ────────────────────────────────────────────────────────────
    hero_top = 16
    hero_h   = 56
    pdf.set_fill_color(*BG_HERO)
    pdf.rect(0, hero_top, 210, hero_h, "F")

    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, hero_top, 4, hero_h, "F")

    pdf.set_xy(14, hero_top + 8)
    pdf.set_text_color(*ACCENT)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(0, 5, "CONTENT MARKETING  —  TREND REPORT", ln=True)

    pdf.set_x(14)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(182, 9, title, ln=True)

    if subtitle:
        pdf.set_x(14)
        pdf.set_text_color(*MUTED)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(182, 5, subtitle, ln=True)

    pdf.set_y(hero_top + hero_h + 8)

    # ── Intro paragraph ───────────────────────────────────────────────────────
    if intro:
        pdf.set_x(14)
        pdf.set_text_color(*TEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(182, 5.5, intro, ln=True)
        pdf.ln(5)

    # Section divider + label
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.5)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(5)

    pdf.set_x(14)
    pdf.set_text_color(*MUTED)
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(0, 4, "TOP 3 FINDINGS", ln=True)
    pdf.ln(5)

    # ── Findings ──────────────────────────────────────────────────────────────
    for i, f in enumerate(findings):
        rank    = f["rank"]
        heading = f["heading"]
        body    = f["body"]
        why     = f.get("why_it_matters", "")

        start_y = pdf.get_y()

        pdf.set_fill_color(*ACCENT)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_xy(14, start_y)
        pdf.cell(10, 11, str(rank), align="C", fill=True)

        pdf.set_xy(27, start_y + 1)
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(169, 6.5, heading, ln=True)

        pdf.set_x(27)
        pdf.set_text_color(*TEXT)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.multi_cell(169, 5.5, body, ln=True)
        pdf.ln(3)

        if why:
            pdf.set_fill_color(*WHY_BG)
            pdf.set_text_color(*ACCENT)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_x(27)
            pdf.cell(169, 5, "  WHY IT MATTERS", fill=True, ln=True)
            pdf.set_fill_color(*WHY_BG)
            pdf.set_text_color(*TEXT)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(27)
            pdf.multi_cell(169, 5, why, fill=True, ln=True)
            pdf.ln(2)

        pdf.ln(4)

        if i < len(findings) - 1:
            pdf.set_draw_color(*DIV)
            pdf.set_line_width(0.2)
            pdf.line(27, pdf.get_y(), 196, pdf.get_y())
            pdf.ln(6)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate branded trends PDF.")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--data",      help="JSON string with research data")
    group.add_argument("--data-file", help="Path to JSON file with research data")
    args = parser.parse_args()

    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = json.loads(args.data)

    date_tag    = datetime.now().strftime("%Y%m%d-%H%M")
    output_path = Path(f"briefings/trends-{date_tag}.pdf")

    print(f"Generating PDF ...")
    build_pdf(data, output_path)
    print(f"PDF_PATH:{output_path}")


if __name__ == "__main__":
    main()

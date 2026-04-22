#!/usr/bin/env python3
"""
convert-quote.py
Convert an accepted AGENCINA quote to an invoice.
Reads the JSON sidecar from generate-quote.py and calls generate-invoice logic.

Usage:
  # Required items only (optional excluded):
  python equipment/convert-quote.py --quote live/quotes/QUO-xxx_client.json

  # Include all optional items:
  python equipment/convert-quote.py --quote live/quotes/QUO-xxx_client.json --accept-optional

  # Custom due date (default: 14 days from today):
  python equipment/convert-quote.py --quote live/quotes/QUO-xxx_client.json --due-date "30 May 2026"

Dependencies: fpdf2, python-dotenv (same as generate-invoice.py)
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location("generate_invoice", pathlib.Path(__file__).parent / "generate-invoice.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
generate_invoice = _mod.generate_invoice


def convert_quote(
    quote_path: str,
    accept_optional: bool = False,
    due_date: str = None,
    invoice_number: str = None,
    output_dir: str = "live/invoices",
) -> str:
    path = Path(quote_path)
    if not path.exists():
        print(f"ERROR: Quote file not found: {quote_path}")
        print("Check the path and try again.")
        sys.exit(1)

    with open(path) as f:
        quote = json.load(f)

    # Filter services
    services = [
        {"description": s["description"], "amount": s["amount"]}
        for s in quote["services"]
        if not s.get("optional", False) or accept_optional
    ]

    if not services:
        print("ERROR: No services to invoice (all items were optional and --accept-optional was not set).")
        sys.exit(1)

    if not due_date:
        due_date = (date.today() + timedelta(days=14)).strftime("%d %B %Y")

    included = [s for s in quote["services"] if not s.get("optional", False)]
    optional_included = [s for s in quote["services"] if s.get("optional", False)] if accept_optional else []

    print(f"\nConverting quote {quote['quote_number']} → invoice")
    print(f"  Required items: {len(included)}")
    print(f"  Optional items included: {len(optional_included)}")
    print(f"  Due date: {due_date}")

    invoice_path = generate_invoice(
        client_name=quote["client_name"],
        project_name=quote["project_name"],
        services=services,
        due_date=due_date,
        invoice_number=invoice_number,
        apply_vat=quote.get("apply_vat", False),
        vat_rate=quote.get("vat_rate"),
        output_dir=output_dir,
    )

    return invoice_path


def main():
    parser = argparse.ArgumentParser(description="Convert accepted AGENCINA quote to invoice")
    parser.add_argument("--quote", required=True, help="Path to quote JSON sidecar file")
    parser.add_argument("--accept-optional", dest="accept_optional", action="store_true",
                        help="Include optional line items in the invoice")
    parser.add_argument("--due-date", dest="due_date", help="Invoice due date (default: 14 days from today)")
    parser.add_argument("--invoice-number", dest="invoice_number", help="Invoice number (auto if omitted)")
    parser.add_argument("--output-dir", dest="output_dir", default="live/invoices")
    args = parser.parse_args()

    convert_quote(
        quote_path=args.quote,
        accept_optional=args.accept_optional,
        due_date=args.due_date,
        invoice_number=args.invoice_number,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

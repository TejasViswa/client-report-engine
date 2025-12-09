import argparse
import json
from pathlib import Path

from .renderer import render_docx
from .pdf import docx_to_pdf


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate client reports from templates.")
    parser.add_argument("--template", required=True, help="Template DOCX file name, e.g. sample_report.docx")
    parser.add_argument("--data", required=True, help="JSON file with context data")
    parser.add_argument("--docx-out", help="Output DOCX filename")
    parser.add_argument("--pdf", action="store_true", help="Also convert to PDF")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        context = json.load(f)

    docx_path = render_docx(args.template, context, args.docx_out)

    if args.pdf:
        pdf_path = docx_to_pdf(docx_path)
        print(f"PDF generated at: {pdf_path}")
    else:
        print(f"DOCX generated at: {docx_path}")

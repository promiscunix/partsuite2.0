from io import BytesIO
from pathlib import Path
from typing import Dict, List

from PyPDF2 import PdfMerger, PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


def _render_summary_page(invoice_info: Dict) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    text_y = height - inch
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, text_y, "Invoice summary + mapping")

    c.setFont("Helvetica", 12)
    meta_lines = [
        f"Invoice key: {invoice_info.get('invoice_key_norm', '')}",
        f"Invoice number: {invoice_info.get('invoice_number_raw', '')}",
        f"Invoice type: {invoice_info.get('invoice_type_code', '')} - {invoice_info.get('invoice_type_desc', '')}",
        f"Invoice date: {invoice_info.get('invoice_date_iso', '')}",
    ]
    text_y -= 0.4 * inch
    for line in meta_lines:
        c.drawString(inch, text_y, line)
        text_y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, text_y, "Account mapping")
    text_y -= 0.3 * inch

    mapped_accounts: List[Dict] = invoice_info.get("mapped_accounts", [])
    table_data = [["FCA code", "Description", "Amount", "Internal GL", "Label"]]
    for entry in mapped_accounts:
        table_data.append(
            [
                entry.get("fca_code", ""),
                entry.get("fca_description", ""),
                f"{entry.get('fca_amount', 0):,.2f}",
                entry.get("internal_gl_account", ""),
                entry.get("internal_label", ""),
            ]
        )

    table = Table(table_data, colWidths=[1.1 * inch, 2.7 * inch, 1.1 * inch, 1 * inch, 1.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("ALIGN", (3, 1), (3, -1), "CENTER"),
            ]
        )
    )

    table_width, table_height = table.wrapOn(c, width - 2 * inch, height)
    table.drawOn(c, inch, text_y - table_height)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def build_summary_mapping_pdf(invoice_info: Dict, summary_pdf: Path, output_path: Path) -> None:
    summary_pdf = Path(summary_pdf)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # First page: rendered summary + mapping
    summary_buffer = _render_summary_page(invoice_info)

    merger = PdfMerger()
    merger.append(PdfReader(summary_buffer))
    merger.append(str(summary_pdf))

    with output_path.open("wb") as f:
        merger.write(f)
    merger.close()

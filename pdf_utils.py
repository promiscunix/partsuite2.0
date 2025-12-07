import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

from mapping_pdf import build_summary_mapping_pdf
from parsers.fca import (
    detect_invoice_start,
    map_accounts_to_internal,
    parse_invoice_metadata,
    parse_summary,
)


class InvoiceProcessingError(Exception):
    """Raised when invoice data cannot be parsed."""


def save_pdf_subset(reader: PdfReader, page_indices: List[int], output_path: Path) -> None:
    writer = PdfWriter()
    for idx in page_indices:
        writer.add_page(reader.pages[idx])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        writer.write(f)


def _finalize_invoice(
    reader: PdfReader,
    invoice_pages: List[int],
    page_texts: List[str],
    output_base: Path,
) -> Optional[Dict]:
    if not invoice_pages:
        return None

    first_page_text = page_texts[0]
    summary_page_text = page_texts[-1]
    metadata = parse_invoice_metadata(first_page_text)
    summary_data = parse_summary(summary_page_text)
    mapped_accounts = map_accounts_to_internal(summary_data)

    invoice_key_norm = metadata["invoice_key_norm"]

    invoice_pdf_path = output_base / "invoices" / f"{invoice_key_norm}.pdf"
    summary_pdf_path = output_base / "summaries" / f"{invoice_key_norm}_summary.pdf"
    mapping_pdf_path = output_base / "mappings" / f"{invoice_key_norm}_mapping.pdf"
    base_parent = output_base.parent

    save_pdf_subset(reader, invoice_pages, invoice_pdf_path)
    save_pdf_subset(reader, [invoice_pages[-1]], summary_pdf_path)

    invoice_info = {
        **metadata,
        "summary": summary_data,
        "mapped_accounts": mapped_accounts,
        "files": {
            # URLs are relative so they can be served by StaticFiles mounted at /output.
            "invoice_pdf": str(invoice_pdf_path.relative_to(base_parent)),
            "summary_pdf": str(summary_pdf_path.relative_to(base_parent)),
            "summary_mapping_pdf": str(mapping_pdf_path.relative_to(base_parent)),
        },
    }

    build_summary_mapping_pdf(invoice_info, summary_pdf_path, mapping_pdf_path)
    return invoice_info


def process_combined_pdf(pdf_path: Path, output_base: Path) -> List[Dict]:
    output_base.mkdir(parents=True, exist_ok=True)

    invoice_results: List[Dict] = []
    reader = PdfReader(str(pdf_path))

    with pdfplumber.open(str(pdf_path)) as pdf:
        current_page_indices: List[int] = []
        current_texts: List[str] = []

        for idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            is_start = detect_invoice_start(text)

            if is_start and current_page_indices:
                result = _finalize_invoice(reader, current_page_indices, current_texts, output_base)
                if result:
                    invoice_results.append(result)
                current_page_indices = []
                current_texts = []

            if is_start or current_page_indices:
                current_page_indices.append(idx)
                current_texts.append(text)

        if current_page_indices:
            result = _finalize_invoice(reader, current_page_indices, current_texts, output_base)
            if result:
                invoice_results.append(result)

    return invoice_results

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from typing import Iterable, List

from invoices.ingestion import extract_pdf_text

INVOICE_PREFIX = "09308000"
INVOICE_KIND_LABELS = {
  "W": "Weekly invoice",
  "CF": "Fleet credit memo",
  "DM": "Debit memo",
  "C": "Credit memo",
}

ACCOUNT_MAP = {
  "ARC01012": ("604190", "Warranty chargebacks"),
  "ARC01217": ("704004", "Freight (dealer generated return)"),
  "ARC01224": ("104000", "Parts (D2D obsolete)"),
  "ARC01002": ("104000", "Parts (core return)"),
  "ARC01003": ("104000", "Parts (late return)"),
  "ARC01004": ("604190", "Warranty deduction"),
  "ARC01007": ("704004", "Freight deduction"),
  "ARC01010": ("704000", "Handling charge"),
  "ARC01017": ("604190", "Warranty adjustment"),
  "ARC01221": ("104000", "Parts (price protection)"),
  "ENV.CONTAINER": ("704005", "Environmental containers"),
}

SUMMARY_LINE_RE = re.compile(
  r"(?P<code>[A-Z0-9./]+)\s+(?P<amount>[(),0-9\-]+\.\d{2})",
  re.IGNORECASE,
)

INVOICE_START_RE = re.compile(rf"{INVOICE_PREFIX}(?P<kind>[A-Z]+)")


def _clean_amount(raw: str) -> Decimal:
  cleaned = raw.replace(",", "").strip()
  if cleaned.startswith("(") and cleaned.endswith(")"):
    cleaned = cleaned.strip("()")
    return Decimal(cleaned) * Decimal("-1")
  return Decimal(cleaned)


def _escape_pdf_text(text: str) -> str:
  return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(lines: Iterable[str], title: str) -> bytes:
  y = 780
  content_lines = [f"BT /F1 16 Tf 50 {y} Td ({_escape_pdf_text(title)}) Tj ET"]
  y -= 26
  for line in lines:
    content_lines.append(f"BT /F1 12 Tf 50 {y} Td ({_escape_pdf_text(line)}) Tj ET")
    y -= 16
  content_stream = "\n".join(content_lines).encode("utf-8")

  parts: List[bytes] = []
  offsets: List[int] = []

  def _add(obj: str):
    offsets.append(sum(len(p) for p in parts))
    parts.append(obj.encode("utf-8") + b"\n")

  parts.append(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

  _add("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
  _add("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
  _add(
    "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
    "/Resources << /Font << /F1 5 0 R >> >> >> endobj"
  )
  _add(f"4 0 obj << /Length {len(content_stream)} >> stream\n" + content_stream.decode("utf-8") + "\nendstream endobj")
  _add("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")

  xref_offset = sum(len(p) for p in parts)
  xref_lines = ["xref", f"0 {len(offsets) + 1}", "0000000000 65535 f "]
  for off in offsets:
    xref_lines.append(f"{off:010d} 00000 n ")

  trailer = (
    "trailer << /Size {size} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF".format(
      size=len(offsets) + 1, start=xref_offset
    )
  )

  parts.append("\n".join(xref_lines).encode("utf-8") + b"\n")
  parts.append(trailer.encode("utf-8"))
  return b"".join(parts)


@dataclass
class SummaryAccountLine:
  source_code: str
  amount: Decimal
  gl_account: str | None
  description: str
  note: str | None = None


@dataclass
class ParsedFCAInvoice:
  invoice_code: str | None
  invoice_type: str
  summary_page: str
  accounts: List[SummaryAccountLine]

  @property
  def title(self) -> str:
    label = self.invoice_type or "Unknown invoice"
    suffix = f" ({self.invoice_code})" if self.invoice_code else ""
    return f"{label}{suffix}"


class FCAInvoiceParser:
  def __init__(self, pdf_path: Path):
    self.pdf_path = pdf_path

  def parse(self) -> List[ParsedFCAInvoice]:
    pages = extract_pdf_text(str(self.pdf_path))
    sections = self._split_into_invoices(pages)
    return [self._parse_section(section) for section in sections]

  def _split_into_invoices(self, pages: List[str]) -> List[List[str]]:
    start_indices = []
    for idx, page in enumerate(pages):
      if INVOICE_START_RE.search(page):
        start_indices.append(idx)

    if not start_indices:
      return [pages]

    slices: List[List[str]] = []
    for i, start in enumerate(start_indices):
      end = start_indices[i + 1] if i + 1 < len(start_indices) else len(pages)
      slices.append(pages[start:end])
    return slices

  def _parse_section(self, pages: List[str]) -> ParsedFCAInvoice:
    invoice_code = None
    invoice_type = "Unknown"

    for page in pages:
      match = INVOICE_START_RE.search(page)
      if match:
        invoice_code = match.group("kind")
        invoice_type = INVOICE_KIND_LABELS.get(invoice_code, "Unknown")
        break

    summary_text = pages[-1]
    accounts = self._parse_summary(summary_text)

    return ParsedFCAInvoice(
      invoice_code=invoice_code,
      invoice_type=invoice_type,
      summary_page=summary_text,
      accounts=accounts,
    )

  def _parse_summary(self, summary_text: str) -> List[SummaryAccountLine]:
    lines: List[SummaryAccountLine] = []
    for raw_line in summary_text.splitlines():
      match = SUMMARY_LINE_RE.search(raw_line)
      if not match:
        continue

      code = match.group("code").upper()
      amount = _clean_amount(match.group("amount"))
      gl_account, desc = self._map_account(code, amount)
      note = None if gl_account else "No mapping configured"
      lines.append(
        SummaryAccountLine(
          source_code=code,
          amount=amount,
          gl_account=gl_account,
          description=desc,
          note=note,
        )
      )
    return lines

  def _map_account(self, code: str, amount: Decimal) -> tuple[str | None, str]:
    if code == "GST/HST":
      if amount >= 0:
        return "201105", "GST/HST payable"
      return "201100", "GST/HST tax credit"

    if code in ACCOUNT_MAP:
      mapped_account, desc = ACCOUNT_MAP[code]
      return mapped_account, desc

    return None, "Unmapped"


def render_summary_pdf(invoice: ParsedFCAInvoice, output_dir: Path) -> Path:
  output_dir.mkdir(parents=True, exist_ok=True)
  timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
  filename = f"{invoice.invoice_code or 'invoice'}_{timestamp}_summary.pdf"
  pdf_bytes = _simple_pdf(invoice.summary_page.splitlines(), title=invoice.title)
  output_path = output_dir / filename
  output_path.write_bytes(pdf_bytes)
  return output_path


def render_mapping_pdf(invoice: ParsedFCAInvoice, output_dir: Path) -> Path:
  output_dir.mkdir(parents=True, exist_ok=True)
  timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
  filename = f"{invoice.invoice_code or 'invoice'}_{timestamp}_mapping.pdf"
  mapping_lines = [
    f"{line.source_code}: {line.amount} -> {line.gl_account or 'Unmapped'} ({line.description})"
    for line in invoice.accounts
  ]
  pdf_bytes = _simple_pdf(mapping_lines, title=f"GL mapping for {invoice.title}")
  output_path = output_dir / filename
  output_path.write_bytes(pdf_bytes)
  return output_path


def encode_pdf_for_download(path: Path) -> str:
  return base64.b64encode(path.read_bytes()).decode("utf-8")

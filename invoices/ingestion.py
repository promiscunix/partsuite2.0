import json
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List


def _run(cmd: str, input_bytes: bytes | None = None, timeout: int = 60) -> subprocess.CompletedProcess:
  return subprocess.run(
    shlex.split(cmd),
    input=input_bytes,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=timeout,
  )


def extract_text_with_poppler(pdf_path: Path) -> List[str]:
  """
  Try to extract text using pdftotext; returns list of pages (single string split by form feed).
  """
  proc = _run(f"pdftotext -layout {shlex.quote(str(pdf_path))} -")
  if proc.returncode != 0:
    raise RuntimeError(f"pdftotext failed: {proc.stderr.decode('utf-8', 'ignore')}")
  text = proc.stdout.decode("utf-8", "ignore")
  pages = text.split("\f")
  return [p.strip() for p in pages if p.strip()]


def extract_text_with_tesseract(pdf_path: Path, dpi: int = 300) -> List[str]:
  """
  OCR fallback: convert PDF pages to PNG with pdftoppm, run tesseract per page.
  """
  pages_text: List[str] = []
  with tempfile.TemporaryDirectory() as tmpdir:
    ppm_prefix = Path(tmpdir) / "page"
    proc = _run(f"pdftoppm -r {dpi} -png {shlex.quote(str(pdf_path))} {ppm_prefix}")
    if proc.returncode != 0:
      raise RuntimeError(f"pdftoppm failed: {proc.stderr.decode('utf-8', 'ignore')}")
    for png_path in sorted(Path(tmpdir).glob("page-*.png")):
      tess = _run(f"tesseract {shlex.quote(str(png_path))} stdout --psm 6")
      if tess.returncode != 0:
        raise RuntimeError(f"tesseract failed: {tess.stderr.decode('utf-8', 'ignore')}")
      pages_text.append(tess.stdout.decode("utf-8", "ignore").strip())
  return pages_text


def extract_text_with_pypdf(pdf_path: Path) -> List[str]:
  """
  Pure-Python fallback using pypdf. This avoids external binaries when available.
  """
  from pypdf import PdfReader

  reader = PdfReader(str(pdf_path))
  pages: List[str] = []
  for page in reader.pages:
    text = (page.extract_text() or "").strip()
    if text:
      pages.append(text)
  return pages


def extract_pdf_text(pdf_path: str) -> List[str]:
  """
  Extract text from a PDF. Try pdftotext first; if mostly empty, fallback to OCR.
  """
  path = Path(pdf_path)
  try:
    pages = extract_text_with_pypdf(path)
    if pages:
      return pages
  except ImportError:
    # Optional dependency not installed; continue to system tools
    pages = []
  except Exception:
    pages = []

  try:
    pages = extract_text_with_poppler(path)
    if pages and any(len(p) > 40 for p in pages):
      return pages
  except Exception:
    pages = []

  # OCR fallback
  try:
    return extract_text_with_tesseract(path)
  except FileNotFoundError as exc:
    raise RuntimeError("pdftoppm and tesseract are required for OCR fallback") from exc


def parse_text_cache(raw: str) -> List[str]:
  try:
    data = json.loads(raw)
    if isinstance(data, list):
      return [str(x) for x in data]
  except Exception:
    pass
  return []

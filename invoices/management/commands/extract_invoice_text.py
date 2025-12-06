from django.core.management.base import BaseCommand, CommandError

from invoices.ingestion import extract_pdf_text
from invoices.models import InvoiceFile


class Command(BaseCommand):
  help = "Extract text from invoice files (pdftotext then OCR fallback) and store in text_cache."

  def add_arguments(self, parser):
    parser.add_argument("--file-id", type=int, help="Specific InvoiceFile id to process")
    parser.add_argument("--limit", type=int, default=50, help="Limit number of files to process (when no file-id)")

  def handle(self, *args, **options):
    qs = InvoiceFile.objects.all().order_by("id")
    if options["file_id"]:
      qs = qs.filter(id=options["file_id"])
    else:
      qs = qs.filter(text_cache=[])[: options["limit"]]

    if not qs.exists():
      self.stdout.write(self.style.WARNING("No files to process."))
      return

    for f in qs:
      try:
        pages = extract_pdf_text(f.file_path)
        f.text_cache = pages
        f.save(update_fields=["text_cache", "updated_at"])
        self.stdout.write(self.style.SUCCESS(f"Processed InvoiceFile {f.id} ({len(pages)} pages)"))
      except Exception as exc:
        raise CommandError(f"Failed on InvoiceFile {f.id}: {exc}")

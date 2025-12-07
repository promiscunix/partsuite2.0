import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pdf_utils import process_combined_pdf

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

app = FastAPI(title="FCA Invoice Parser")

# Ensure output directories exist early.
for sub in [OUTPUT_DIR / "invoices", OUTPUT_DIR / "summaries", OUTPUT_DIR / "mappings"]:
    sub.mkdir(parents=True, exist_ok=True)

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("fca_upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    # Save uploaded file to a temporary location.
    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / file.filename
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        invoices = process_combined_pdf(tmp_path, OUTPUT_DIR)
    finally:
        # Clean up uploaded file
        try:
            tmp_path.unlink(missing_ok=True)
            Path(tmp_dir).rmdir()
        except OSError:
            pass

    return templates.TemplateResponse(
        "fca_results.html", {"request": request, "invoices": invoices}
    )


@app.get("/health", response_class=HTMLResponse)
async def healthcheck():
    return "ok"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

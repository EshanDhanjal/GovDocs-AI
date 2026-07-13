from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ocr import extract_text_from_pdf
from services.classifier import classify_document

app = FastAPI(title="GovDocs-AI API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "GovDocs-AI backend is running"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    original_filename = file.filename or ""
    file_extension = Path(original_filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, PNG, JPG, or JPEG file.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    document_id = str(uuid4())
    stored_filename = f"{document_id}{file_extension}"
    file_path = UPLOAD_DIR / stored_filename
    uploaded_at = datetime.now(timezone.utc).isoformat()

    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    extracted_text = ""

    if file_extension == ".pdf":
        extracted_text = extract_text_from_pdf(str(file_path))

    classification = classify_document(extracted_text) if extracted_text else None

    return {
        "success": True,
        "message": "File uploaded and processed successfully.",
        "document_id": document_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_extension": file_extension,
        "file_path": str(file_path),
        "content_type": file.content_type,
        "size_bytes": len(file_bytes),
        "uploaded_at": uploaded_at,
        "status": "classified" if classification else "uploaded",
        "extracted_text_preview": extracted_text[:1000],
        "extracted_text_length": len(extracted_text),
        "classification": classification
    }
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ocr import extract_text_from_pdf
from services.classifier import classify_document
from services.llm_classifier import classify_document_with_llm
from services.llm_extractor import extract_fields_with_llm
from services.llm_summarizer import summarize_document_with_llm

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
        "message": "GovDocs-AI backend is running",
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    original_filename = file.filename or ""
    file_extension = Path(original_filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a PDF, PNG, JPG, or JPEG file."
            ),
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    document_id = str(uuid4())
    stored_filename = f"{document_id}{file_extension}"
    file_path = UPLOAD_DIR / stored_filename
    uploaded_at = datetime.now(timezone.utc).isoformat()

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_bytes)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="The uploaded file could not be saved.",
        ) from exc

    extracted_text = ""

    if file_extension == ".pdf":
        try:
            extracted_text = extract_text_from_pdf(str(file_path))
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Text extraction failed for the uploaded PDF.",
            ) from exc

    classification = None

    if extracted_text:
        try:
            classification = classify_document_with_llm(extracted_text)
        except Exception:
            classification = classify_document(extracted_text)

        if (
            not classification
            or classification.get("document_type") == "UNKNOWN"
        ):
            classification = classify_document(extracted_text)

    extracted_fields = None

    if (
        extracted_text
        and classification
        and classification.get("document_type") != "UNKNOWN"
    ):
        try:
            extracted_fields = extract_fields_with_llm(
                extracted_text,
                classification,
            )
        except Exception as exc:
            extracted_fields = {
                "error": "Field extraction failed.",
                "details": str(exc),
            }

    summary = None

    if (
        extracted_text
        and classification
        and extracted_fields
        and "error" not in extracted_fields
    ):
        try:
            summary = summarize_document_with_llm(
                extracted_text,
                classification,
                extracted_fields,
            )
        except Exception as exc:
            summary = {
                "error": "Document summarization failed.",
                "details": str(exc),
            }

    if summary and "error" not in summary:
        processing_status = "summarized"
    elif extracted_fields and "error" not in extracted_fields:
        processing_status = "extracted"
    elif classification:
        processing_status = "classified"
    elif extracted_text:
        processing_status = "ocr_complete"
    else:
        processing_status = "uploaded"

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
        "status": processing_status,
        "extracted_text_preview": extracted_text[:1000],
        "extracted_text_length": len(extracted_text),
        "classification": classification,
        "extracted_fields": extracted_fields,
        "summary": summary,
    }
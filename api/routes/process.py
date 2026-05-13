import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from src.pipeline import LegalWorkflowPipeline

router = APIRouter()
pipeline = LegalWorkflowPipeline()


@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = pipeline.process_document(tmp_path)
        return {
            "file_name": result["file_name"],
            "used_ocr": result["used_ocr"],
            "num_chunks": result["num_chunks"],
            "structured_fields": result["structured_fields"],
            "raw_text_preview": result["raw_text"][:500] + ("..." if len(result["raw_text"]) > 500 else ""),
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.pipeline import LegalWorkflowPipeline

router = APIRouter()
pipeline = LegalWorkflowPipeline()


class DraftRequest(BaseModel):
    file_name: str
    raw_text: str
    structured_fields: dict
    query: str = ""


@router.post("/draft")
async def generate_draft(request: DraftRequest):
    try:
        doc_result = {
            "file_name": request.file_name,
            "raw_text": request.raw_text,
            "structured_fields": request.structured_fields,
            "used_ocr": False,
            "num_chunks": 0,
            "num_indexed": 0,
        }
        draft = pipeline.generate_draft(doc_result, request.query or None)
        return {"draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

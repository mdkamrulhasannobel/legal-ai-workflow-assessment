from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.feedback.diff_engine import DiffEngine
from src.feedback.pattern_extractor import PatternExtractor
from src.feedback.pattern_store import PatternStore

router = APIRouter()
diff_engine = DiffEngine()
pattern_extractor = PatternExtractor()
pattern_store = PatternStore()


class FeedbackRequest(BaseModel):
    draft_id: str
    original_draft: str
    edited_draft: str


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        diff_result = diff_engine.compute_diff(request.original_draft, request.edited_draft)
        pattern = pattern_extractor.extract_pattern(
            diff_result["diff_text"],
            diff_result["additions"],
            diff_result["deletions"],
        )
        patterns = pattern_store.add_pattern(pattern)
        return {
            "diff": diff_result,
            "extracted_pattern": pattern,
            "total_patterns": len(patterns),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def list_patterns():
    return {"patterns": pattern_store.load_patterns()}

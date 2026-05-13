from fastapi import FastAPI
from api.routes.process import router as process_router
from api.routes.draft import router as draft_router
from api.routes.feedback import router as feedback_router

app = FastAPI(
    title="Legal AI Workflow API",
    description="Pearson Specter Litt — Internal AI Document Processing & Drafting System",
    version="1.0.0",
)

app.include_router(process_router, prefix="/api/v1")
app.include_router(draft_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}

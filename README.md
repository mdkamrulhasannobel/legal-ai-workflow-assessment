# Legal AI Workflow — Pearson Specter Litt

This submission is a practical, offline-friendly workflow for messy legal-style documents. It extracts text from scanned or noisy inputs, pulls out structured fields, retrieves supporting evidence from the same uploaded document, generates a grounded first-pass case fact summary, and learns reusable editing patterns from operator changes.

The implementation is intentionally scoped to run on a normal laptop without paid APIs or large local models.

## What This Project Demonstrates

- Document processing with text-layer extraction and OCR fallback
- Structured field extraction for parties, dates, clauses, jurisdiction, and OCR warnings
- Lightweight grounded retrieval with inspectable chunk citations
- Deterministic draft generation so reviewers can run it locally
- Improvement loop that stores reusable editing preferences

## Architecture Overview

```text
Document (PDF/Image)
    |
    v
Document Processing
  - pdfplumber / pdfminer text extraction
  - Tesseract OCR fallback
  - regex-based field extraction
    |
    v
Grounded Retrieval
  - paragraph chunking
  - local hashed embeddings
  - JSON-backed retrieval store
    |
    v
Draft Generation
  - grounded case-fact template
  - citations per fact: [SOURCE: chunk_id]
  - learned editor preferences applied
    |
    v
Edit Feedback Loop
  - diff original vs edited draft
  - infer reusable pattern
  - save pattern for future drafts
```

## Setup

### Prerequisites

- Python 3.10+
- Tesseract OCR
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `apt install tesseract-ocr`

### Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No OpenAI key is required.

## Run

### CLI / Pipeline

```python
from src.pipeline import LegalWorkflowPipeline

pipeline = LegalWorkflowPipeline()
result = pipeline.run_end_to_end("data/sample_inputs/contract_scan.pdf")
print(result["draft"])
```

### API Server

```bash
uvicorn api.main:app --reload
```

Endpoints:

- `POST /api/v1/process`
- `POST /api/v1/draft`
- `POST /api/v1/feedback`
- `GET /api/v1/patterns`

### UI

```bash
streamlit run ui/app.py
```

## Tests

```bash
pytest tests/ -v
```

## Evaluation

```bash
python eval/eval_grounding.py
python eval/eval_before_after.py
```

## Rubric Alignment

| Component | Status |
|-----------|--------|
| Document Processing | Implemented |
| Retrieval and Grounding | Implemented with local lightweight retrieval |
| Draft Quality | Implemented as grounded first-pass summary |
| Improvement from Edits | Implemented |
| Code Quality and System Design | Modular and low-spec friendly |
| Documentation and Clarity | README + ARCHITECTURE + ASSUMPTIONS |

## Project Structure

```text
src/
  processing/   extraction + OCR + structuring
  retrieval/    chunking + local embeddings + JSON store
  generation/   grounded draft assembly
  feedback/     diff + pattern learning + pattern storage
api/            optional FastAPI endpoints
ui/             optional Streamlit app
tests/          unit tests
eval/           evaluation scripts
data/           sample inputs and outputs
```

## Reviewer Notes

- This is intentionally scoped for reliability and reviewer experience rather than heavy-model sophistication.
- The draft output is deterministic and evidence-linked so the behavior is easy to inspect.
- Sample PDFs are synthetic and included to make the workflow easy to verify.

# Architecture Document

## System Design

The Legal AI Workflow is organized as a four-stage pipeline that can run on a modest laptop without paid API access.

## Stage 1: Document Processing

Goal: convert messy legal-style documents into usable text plus structured fields.

Approach:

1. Try text-layer extraction with `pdfplumber`
2. Fall back to `pdfminer.six` if needed
3. If text is still missing, use OCR through `pdf2image` + `pytesseract`
4. Run regex-based extraction for:
   - parties
   - dates
   - clause markers
   - jurisdiction
   - document type
   - low-confidence OCR regions

This stage produces output that downstream retrieval and drafting can use immediately.

## Stage 2: Grounded Retrieval

Goal: surface the most relevant passages from the same uploaded document.

Approach:

1. Split extracted text into paragraph-oriented chunks
2. Convert each chunk into a lightweight 384-dimension hashed-token vector
3. Persist chunks in a small JSON-backed local store
4. Query the same document only and rank chunks by cosine similarity

Why this design:

- no model download required
- no paid embeddings API
- predictable reviewer setup
- enough grounding support for the scope of the take-home

## Stage 3: Draft Generation

Goal: generate a useful first-pass case fact summary grounded in retrieved evidence.

Approach:

- The draft is assembled from structured fields plus top retrieved chunks
- Each factual line includes `[SOURCE: chunk_id]`
- Missing information is explicitly called out instead of invented
- OCR uncertainty is surfaced in the final output
- Learned editor preferences are included on future runs

This is deterministic instead of LLM-based by design, so the project remains easy to run and inspect locally.

## Stage 4: Improvement from Operator Edits

Goal: turn edits into reusable drafting guidance.

Approach:

1. Compare original and edited draft with a diff
2. Inspect the added content
3. Convert those additions into a reusable rule
4. Save the rule in `edit_patterns.json`
5. Apply active rules to future drafts

This satisfies the requirement for a real improvement loop without depending on external inference.

## API Layer

Optional FastAPI endpoints:

- `POST /api/v1/process`
- `POST /api/v1/draft`
- `POST /api/v1/feedback`
- `GET /api/v1/patterns`

## UI Layer

Optional Streamlit interface with three stages:

1. Upload and process document
2. Generate grounded draft
3. Edit draft and learn a reusable pattern

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Text-layer first, OCR second | Keeps clean documents fast while still handling scans |
| Regex-based structuring | Deterministic, low-cost, easy to explain |
| Hashed local embeddings | No large model, no network dependency |
| JSON-backed retrieval store | Small, inspectable, easy for reviewers |
| Deterministic drafting | Always runnable on low-spec hardware |
| Pattern storage in JSON | Simple improvement loop with visible outputs |
| Case fact summary output | Clear structure and easy grounding evaluation |

## Tradeoff Summary

This architecture gives up some sophistication compared with a hosted LLM + vector database stack, but it improves portability, honesty, and reviewer experience. For a take-home assessment, that is a worthwhile tradeoff because the core behaviors remain visible:

- messy document handling
- grounded retrieval
- evidence-linked draft output
- improvement from edits

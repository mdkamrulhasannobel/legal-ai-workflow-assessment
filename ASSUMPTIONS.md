# Assumptions & Tradeoffs

## Technical Assumptions

1. OCR quality depends on source quality. Clean scans work much better than badly damaged pages.
2. The project should run without OpenAI or any paid API access.
3. Tesseract is available on the machine when OCR fallback is needed.
4. The sample dataset is small enough for a local JSON-backed retrieval store.

## Functional Assumptions

1. The chosen draft type is a case fact summary.
2. Synthetic legal-style documents are acceptable for the assessment.
3. The improvement loop only needs to show meaningful reuse of edit behavior, not production-grade personalization.
4. Single-document retrieval is enough for this scoped version.

## Tradeoffs Made

| Decision | What It Helps | What It Gives Up |
|----------|---------------|------------------|
| Local OCR + regex extraction | Easy to run and explain | Less robust than a larger ML pipeline |
| Hashed local embeddings | No downloads, low memory, offline | Lower semantic quality than transformer embeddings |
| JSON-backed retrieval store | Reviewer-friendly and inspectable | Not scalable like a real vector DB |
| Deterministic draft assembly | Works on low-spec hardware every time | Less fluent than an LLM-generated draft |
| JSON pattern store | Simple improvement loop | No multi-user or transactional guarantees |

## Limitations

1. Retrieval quality is intentionally lightweight and not tuned for production legal search.
2. Structured extraction is regex-based, so unusual document wording may be missed.
3. OCR confidence is approximated through heuristics rather than model confidence scores.
4. The draft is a strong first pass, not a substitute for legal review.

## Why This Scope

The assessment explicitly says to keep the scope practical and to prioritize engineering quality, grounding, and clarity over visual polish. This submission follows that advice by choosing a smaller implementation that reviewers can actually run and inspect on a normal machine.

## Future Improvements

- replace hashed embeddings with a stronger local encoder if hardware allows
- add document-level metadata filters and multi-document retrieval
- improve clause extraction with richer parsing
- add better OCR confidence estimation
- swap the JSON store for a production database if the system grows

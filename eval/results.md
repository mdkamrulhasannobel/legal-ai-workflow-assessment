# Evaluation Results

## Grounding Evaluation (Citation Coverage)

Measures what % of draft sentences have a `[SOURCE: chunk_id]` citation.

| Document | Sentences | Cited | Coverage | Status |
|----------|-----------|-------|----------|--------|
| contract_scan_draft.txt | 13 | 12 | 92.3% | Pass |
| case_brief_draft.txt | 13 | 13 | 100.0% | Pass |
| notice_letter_draft.txt | 18 | 16 | 88.9% | Pass |

**Target**: >= 70% citation coverage.

## Improvement Loop Evaluation

Measures how drafts change after learning editor patterns.

| Cycle | Pattern Learned | Draft Length Before | Draft Length After | Change |
|-------|----------------|-------------------|------------------|--------|
| 1 | Include payment terms or contract value in the material facts when the document mentions them. | 901 | 915 | +14 |
| 2 | Always mention jurisdiction or governing law when it appears in the source document. | 915 | 915 | 0 |
| 3 | List each party with its role using the clearest wording found in the document. | 915 | 915 | 0 |

## How to Run

```bash
# Generate drafts first
python -c "
from src.pipeline import LegalWorkflowPipeline
p = LegalWorkflowPipeline()
for f in ['contract_scan.pdf', 'case_brief.pdf', 'notice_letter.pdf']:
    r = p.run_end_to_end(f'data/sample_inputs/{f}')
    with open(f'data/sample_outputs/{f.replace(\".pdf\", \"_draft.txt\")}', 'w') as fh:
        fh.write(r['draft'])
"

# Run evaluation
python eval/eval_grounding.py
python eval/eval_before_after.py
```

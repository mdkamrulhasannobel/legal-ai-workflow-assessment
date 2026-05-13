"""Evaluates draft quality improvement before and after edit pattern learning.

Simulates: generate draft -> apply edit -> learn pattern -> regenerate draft.
Shows how the pattern changes the output.
"""
import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.feedback.diff_engine import DiffEngine
from src.feedback.pattern_store import PatternStore
from src.generation.drafter import DraftGenerator
from src.pipeline import LegalWorkflowPipeline


def simulate_improvement_cycle(
    draft_text: str,
    suggestion: str,
    pattern_store: PatternStore,
    pipeline: LegalWorkflowPipeline,
) -> dict:
    diff_engine = DiffEngine()
    drafter = DraftGenerator()

    edited = draft_text + f"\n\n[EDITOR NOTE: {suggestion}]"
    diff_result = diff_engine.compute_diff(draft_text, edited)
    pattern_text = drafter.extract_pattern(diff_result["diff_text"])
    pattern_store.add_pattern({
        "rule": pattern_text,
        "category": "style",
        "examples": [suggestion],
        "active": True,
    })
    return {
        "original_draft": draft_text,
        "suggestion": suggestion,
        "learned_pattern": pattern_text,
    }


def main():
    sample_file = Path(__file__).parent.parent / "data" / "sample_inputs" / "contract_scan.pdf"
    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return

    output_dir = Path(__file__).parent.parent / "data" / "sample_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "improvement_results.json"

    pipeline = LegalWorkflowPipeline()
    pattern_store = PatternStore()
    pattern_store.clear()

    print("=== BEFORE-AFTER EVALUATION ===\n")

    print("1. Processing document...")
    doc_result = pipeline.process_document(sample_file)
    print(f"   Extracted {len(doc_result['raw_text'])} chars, "
          f"{doc_result['num_chunks']} chunks indexed\n")

    print("2. Generating initial draft (no learned patterns)...")
    draft_before = pipeline.generate_draft(doc_result)
    print(f"   Initial draft generated ({len(draft_before)} chars)\n")

    print("3. Simulating editor feedback...")
    suggestions = [
        "Always include the contract value/payment terms in the MATERIAL FACTS section.",
        "Specifically state the governing law and jurisdiction in every case fact summary.",
        "List each party's full legal name and role in the PARTIES INVOLVED section.",
    ]

    cycles = []
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   Cycle {i}: Applying suggestion and learning pattern...")
        cycle = simulate_improvement_cycle(
            draft_before if i == 1 else cycles[-1].get("new_draft", draft_before),
            suggestion,
            pattern_store,
            pipeline,
        )
        cycles.append(cycle)

        print(f"   Pattern learned: {cycle['learned_pattern'][:80]}...")

        new_draft = pipeline.generate_draft(doc_result)
        cycle["new_draft"] = new_draft
        print(f"   New draft generated ({len(new_draft)} chars)\n")

    print("4. Generating final draft with all learned patterns...")
    draft_after = pipeline.generate_draft(doc_result)
    print(f"   Final draft ({len(draft_after)} chars)\n")

    print("5. Comparing before vs after...")
    diff_before_len = len(draft_before)
    diff_after_len = len(draft_after)
    print(f"   Draft length before: {diff_before_len} chars")
    print(f"   Draft length after:  {diff_after_len} chars")
    print(f"   Change: {'+' if diff_after_len > diff_before_len else ''}{diff_after_len - diff_before_len} chars")

    patterns = pattern_store.load_patterns()
    print(f"\n   Learned patterns ({len(patterns)}):")
    for p in patterns:
        print(f"     - {p['rule'][:100]}")

    results = {
        "patterns_learned": patterns,
        "draft_before": draft_before,
        "draft_after": draft_after,
        "cycles": cycles,
    }
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()

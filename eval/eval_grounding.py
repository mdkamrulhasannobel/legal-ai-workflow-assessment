"""Evaluates citation coverage of generated drafts."""

import re
from pathlib import Path


def extract_citations(draft_text: str) -> list[str]:
    return re.findall(r"\[SOURCE:\s*([^\]]+)\]", draft_text)


def count_sentences(draft_text: str) -> int:
    lines = [line.strip() for line in draft_text.splitlines() if line.strip()]
    content_lines = [
        line for line in lines
        if not line.endswith("SUMMARY")
        and line != "================="
        and not line.startswith("Document:")
        and not line.isupper()
    ]
    return len([line for line in content_lines if len(line) > 10])


def count_cited_sentences(draft_text: str) -> int:
    lines = [line.strip() for line in draft_text.splitlines() if line.strip()]
    content_lines = [
        line for line in lines
        if not line.endswith("SUMMARY")
        and line != "================="
        and not line.startswith("Document:")
        and not line.isupper()
    ]
    return sum(1 for line in content_lines if re.search(r"\[SOURCE:\s*[^\]]+\]", line))


def evaluate_draft(draft_text: str, doc_name: str = "unknown") -> dict:
    citations = extract_citations(draft_text)
    total_sentences = count_sentences(draft_text)
    cited_sentences = count_cited_sentences(draft_text)

    coverage = (cited_sentences / total_sentences * 100) if total_sentences > 0 else 0.0

    return {
        "document": doc_name,
        "total_sentences": total_sentences,
        "cited_sentences": cited_sentences,
        "total_citations": len(citations),
        "citation_coverage_pct": round(coverage, 1),
        "unique_sources": len(set(citations)),
        "passed": coverage >= 70.0,
    }


def main():
    output_dir = Path(__file__).parent.parent / "data" / "sample_outputs"
    results = []

    for draft_file in sorted(output_dir.glob("*_draft.txt")):
        draft_text = draft_file.read_text()
        result = evaluate_draft(draft_text, doc_name=draft_file.name)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['document']}: "
              f"{result['citation_coverage_pct']}% coverage "
              f"({result['cited_sentences']}/{result['total_sentences']} sentences cited)")

    if results:
        avg_coverage = sum(r["citation_coverage_pct"] for r in results) / len(results)
        print(f"\nAverage citation coverage: {avg_coverage:.1f}%")
        print(f"Documents evaluated: {len(results)}")


if __name__ == "__main__":
    main()

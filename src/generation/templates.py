import re
from typing import Optional


class DraftTemplate:
    def __init__(self, name: str = "case_fact_summary"):
        self.name = name

    def build_system_prompt(self, learned_patterns: Optional[list[str]] = None) -> str:
        prompt = """Offline legal drafting assistant.

Grounding rules:
1. Use only the provided document evidence.
2. Cite each factual statement with [SOURCE: chunk_id].
3. If a fact is missing, say "Insufficient information in source documents."
4. Mention OCR uncertainty when low-confidence regions exist."""
        if learned_patterns:
            patterns_text = "\n".join(f"- {pattern}" for pattern in learned_patterns)
            prompt += f"\n\nLearned editor preferences:\n{patterns_text}"
        return prompt

    def build_user_prompt(self, document_name: str, structured_fields: dict, retrieved_chunks: list[dict]) -> str:
        context_parts = []
        for chunk in retrieved_chunks:
            context_parts.append(
                f"[SOURCE: {chunk['metadata']['chunk_id']}] {chunk['text']}"
            )
        return (
            f"Document: {document_name}\n"
            f"Structured fields: {structured_fields}\n"
            f"Retrieved chunks:\n" + "\n".join(context_parts)
        )

    def compose_draft(
        self,
        document_name: str,
        structured_fields: dict,
        retrieved_chunks: list[dict],
        learned_patterns: Optional[list[str]] = None,
    ) -> str:
        chunk_lookup = {chunk["metadata"]["chunk_id"]: chunk for chunk in retrieved_chunks}
        parties = self._render_parties(structured_fields.get("parties", []), chunk_lookup)
        dates = self._render_dates(structured_fields.get("dates", []), chunk_lookup)
        facts = self._render_facts(retrieved_chunks)
        clauses = self._render_clauses(structured_fields.get("clause_markers", []), chunk_lookup)
        issues = self._render_issues(structured_fields, learned_patterns, chunk_lookup)

        return (
            "CASE FACT SUMMARY\n"
            "=================\n\n"
            f"Document: {document_name}\n\n"
            "PARTIES INVOLVED\n"
            f"{parties}\n\n"
            "KEY DATES\n"
            f"{dates}\n\n"
            "MATERIAL FACTS\n"
            f"{facts}\n\n"
            "APPLICABLE LAWS / CLAUSES\n"
            f"{clauses}\n\n"
            "OPEN ISSUES / UNCLEAR SECTIONS\n"
            f"{issues}"
        )

    def _render_parties(self, parties: list[dict], chunk_lookup: dict[str, dict]) -> str:
        if not parties:
            source = self._best_source_for_terms(chunk_lookup, ["party", "plaintiff", "defendant", "client", "firm"])
            return f"Insufficient information in source documents. {self._citation(source)}"
        source = self._best_source_for_terms(chunk_lookup, [party["name"] for party in parties])
        citation = self._citation(source)
        lines = []
        for party in parties[:6]:
            role = party.get("role", "Party")
            lines.append(f"- {party['name']} ({role}) {citation}")
        return "\n".join(lines)

    def _render_dates(self, dates: list[str], chunk_lookup: dict[str, dict]) -> str:
        if not dates:
            source = self._best_source_for_terms(chunk_lookup, ["date", "dated", "filed"])
            return f"Insufficient information in source documents. {self._citation(source)}"
        lines = []
        for date in dates[:6]:
            source = self._best_source_for_terms(chunk_lookup, [date])
            lines.append(f"- {date} {self._citation(source)}")
        return "\n".join(lines)

    def _render_facts(self, retrieved_chunks: list[dict]) -> str:
        if not retrieved_chunks:
            return "1. Insufficient information in source documents."
        lines = []
        for index, chunk in enumerate(retrieved_chunks[:5], start=1):
            sentence = self._compress_text(chunk["text"])
            lines.append(f"{index}. {sentence} [SOURCE: {chunk['metadata']['chunk_id']}]")
        return "\n".join(lines)

    def _render_clauses(self, markers: list[str], chunk_lookup: dict[str, dict]) -> str:
        if not markers:
            source = self._best_source_for_terms(chunk_lookup, ["section", "clause", "law"])
            return f"Insufficient information in source documents. {self._citation(source)}"
        lines = []
        for marker in markers[:6]:
            source = self._best_source_for_terms(chunk_lookup, [marker])
            lines.append(f"- {marker} {self._citation(source)}")
        return "\n".join(lines)

    def _render_issues(
        self,
        structured_fields: dict,
        learned_patterns: Optional[list[str]],
        chunk_lookup: dict[str, dict],
    ) -> str:
        items = []
        low_confidence = structured_fields.get("low_confidence_regions", [])
        for region in low_confidence[:5]:
            source = self._best_source_for_terms(chunk_lookup, [region.get("text", "")])
            items.append(
                f"- [LOW CONFIDENCE OCR] Line {region['line_number']}: {region['text']} {self._citation(source)}"
            )
        if learned_patterns:
            source = self._best_source_for_terms(chunk_lookup, ["agreement", "jurisdiction", "payment"])
            items.append(f"- Learned editor preferences are stored and applied on future drafts. {self._citation(source)}")
        if not items:
            source = self._best_source_for_terms(chunk_lookup, ["agreement", "notice", "brief", "facts"])
            items.append(f"- No major extraction issues detected in this document. {self._citation(source)}")
        return "\n".join(items)

    def _best_source_for_terms(self, chunk_lookup: dict[str, dict], terms: list[str]) -> Optional[str]:
        best_chunk_id = None
        best_score = -1
        for chunk_id, chunk in chunk_lookup.items():
            text = chunk["text"].lower()
            score = sum(text.count(term.lower()) for term in terms if term)
            if score > best_score:
                best_chunk_id = chunk_id
                best_score = score
        return best_chunk_id

    def _citation(self, chunk_id: Optional[str]) -> str:
        if not chunk_id:
            return "[SOURCE: unavailable]"
        return f"[SOURCE: {chunk_id}]"

    def _compress_text(self, text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        if len(normalized) <= 220:
            return normalized
        clipped = normalized[:217].rsplit(" ", 1)[0]
        return f"{clipped}..."

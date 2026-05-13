from typing import Optional

from src.generation.templates import DraftTemplate
from src.llm_client import LLMClient


class DraftGenerator:
    def __init__(self, model: Optional[str] = None, template: Optional[DraftTemplate] = None):
        self.template = template or DraftTemplate()
        self.llm = LLMClient(model=model)

    def generate(
        self,
        document_name: str,
        structured_fields: dict,
        retrieved_chunks: list[dict],
        learned_patterns: Optional[list[str]] = None,
    ) -> str:
        return self.template.compose_draft(
            document_name=document_name,
            structured_fields=structured_fields,
            retrieved_chunks=retrieved_chunks,
            learned_patterns=learned_patterns,
        )

    def extract_pattern(self, diff_text: str) -> str:
        payload = self.llm.extract_pattern_json(diff_text, self._extract_additions(diff_text), [])
        return payload["rule"]

    def _extract_additions(self, diff_text: str) -> list[str]:
        additions = []
        for line in diff_text.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                additions.append(line[1:])
        return additions

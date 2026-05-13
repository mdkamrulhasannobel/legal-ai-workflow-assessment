import json
import re
from typing import Optional


class LLMClient:
    """Heuristic local fallback so the project works without paid APIs."""

    def __init__(self, model: Optional[str] = None):
        self.model = model or "local-heuristic"

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:
        del system_prompt, temperature, max_tokens
        if json_mode:
            payload = self.extract_pattern_json(user_prompt, [], [])
            return json.dumps(payload)
        return self._summarize_prompt(user_prompt)

    def _summarize_prompt(self, user_prompt: str) -> str:
        lines = [line.strip() for line in user_prompt.splitlines() if line.strip()]
        summary = lines[:8]
        if not summary:
            return "Insufficient information in source documents."
        return "\n".join(summary)

    def extract_pattern_json(self, diff_text: str, additions: list[str], deletions: list[str]) -> dict:
        del diff_text, deletions
        rule = self._infer_rule(additions)
        return {
            "rule": rule,
            "category": self._categorize_rule(rule),
            "examples": [line.strip() for line in additions if line.strip()][:3],
        }

    def _infer_rule(self, additions: list[str]) -> str:
        combined = " ".join(additions).lower()
        if "jurisdiction" in combined or "governing law" in combined:
            return "Always mention jurisdiction or governing law when it appears in the source document."
        if "payment" in combined or "contract value" in combined:
            return "Include payment terms or contract value in the material facts when the document mentions them."
        if "party" in combined or "plaintiff" in combined or "defendant" in combined:
            return "List each party with its role using the clearest wording found in the document."
        return "Preserve editor-added factual detail when it is supported by the source document."

    def _categorize_rule(self, rule: str) -> str:
        lowered = rule.lower()
        if "cite" in lowered or "source" in lowered:
            return "citation"
        if "include" in lowered or "mention" in lowered or "list" in lowered:
            return "content"
        return "style"

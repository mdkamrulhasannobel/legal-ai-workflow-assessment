import os

from dotenv import load_dotenv

from src.llm_client import LLMClient

load_dotenv()


class PatternExtractor:
    def __init__(self, model: str | None = None):
        self.llm = LLMClient(model=model)

    def extract_pattern(self, diff_text: str, additions: list[str], deletions: list[str]) -> dict:
        return self.llm.extract_pattern_json(diff_text, additions, deletions)

import re
from typing import Iterator


class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, source_file: str = "", page_num: int = 0) -> list[dict]:
        paragraphs = self._split_paragraphs(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_len = len(para.split())
            if current_length + para_len > self.chunk_size and current_chunk:
                chunks.append(self._make_chunk(current_chunk, source_file, page_num, len(chunks)))
                overlap_text = self._get_overlap(current_chunk, self.chunk_overlap)
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text.split()) if overlap_text else 0

            current_chunk.append(para)
            current_length += para_len

        if current_chunk:
            chunks.append(self._make_chunk(current_chunk, source_file, page_num, len(chunks)))

        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _make_chunk(self, paragraphs: list[str], source_file: str, page_num: int, idx: int) -> dict:
        text = "\n\n".join(paragraphs)
        return {
            "text": text,
            "metadata": {
                "chunk_id": f"chunk_{idx:04d}",
                "source_file": source_file,
                "page_num": page_num,
                "chunk_index": idx,
                "word_count": len(text.split()),
            },
        }

    def _get_overlap(self, paragraphs: list[str], overlap_words: int) -> str:
        words = []
        for para in reversed(paragraphs):
            para_words = para.split()
            words = para_words + words
            if len(words) >= overlap_words:
                break
        return " ".join(words[-overlap_words:]) if words else ""

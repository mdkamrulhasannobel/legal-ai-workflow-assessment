import json
import math
from pathlib import Path
from typing import Optional

from src.retrieval.embedder import Embedder


class VectorStore:
    """Small-file JSON-backed store for offline retrieval demos."""

    def __init__(
        self,
        collection_name: str = "legal_documents",
        persist_dir: str = ".local_store",
        embedder: Optional[Embedder] = None,
    ):
        self.collection_name = collection_name
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.persist_dir / f"{collection_name}.json"
        self.embedder = embedder or Embedder()
        self._items = self._load()

    def upsert_chunks(self, chunks: list[dict]) -> int:
        if not chunks:
            return 0

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed_batch(texts)
        updated = 0

        for chunk, embedding in zip(chunks, embeddings):
            metadata = chunk["metadata"]
            item_id = f"{metadata['source_file']}_{metadata['chunk_id']}"
            item = {
                "id": item_id,
                "text": chunk["text"],
                "metadata": metadata,
                "embedding": embedding,
            }
            self._items[item_id] = item
            updated += 1

        self._save()
        return updated

    def query(self, query_text: str, top_k: int = 5, source_file: Optional[str] = None) -> list[dict]:
        query_embedding = self.embedder.embed(query_text)
        scored = []

        for item in self._items.values():
            if source_file and item["metadata"].get("source_file") != source_file:
                continue
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored.append({
                "chunk_id": item["metadata"]["chunk_id"],
                "text": item["text"],
                "metadata": item["metadata"],
                "score": score,
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self._items)

    def reset(self):
        self._items = {}
        self._save()

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        return sum(a * b for a, b in zip(left, right))

    def _load(self) -> dict[str, dict]:
        if not self.store_path.exists():
            return {}
        with open(self.store_path) as handle:
            data = json.load(handle)
        return {item["id"]: item for item in data}

    def _save(self):
        with open(self.store_path, "w") as handle:
            json.dump(list(self._items.values()), handle, indent=2)

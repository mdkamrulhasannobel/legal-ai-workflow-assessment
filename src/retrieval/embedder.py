import hashlib
import math
import re


class Embedder:
    """Lightweight local embedder based on hashed token frequencies."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        for token in self._tokenize(text):
            idx = self._token_index(token)
            vector[idx] += 1.0
        return self._normalize(vector)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    @property
    def dimension(self) -> int:
        return self._dimension

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def _token_index(self, token: str) -> int:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % self._dimension

    def _normalize(self, vector: list[float]) -> list[float]:
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector
        return [value / magnitude for value in vector]

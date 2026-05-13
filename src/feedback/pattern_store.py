import json
from pathlib import Path
from typing import Optional


class PatternStore:
    def __init__(self, store_path: str | Path = "edit_patterns.json"):
        self.store_path = Path(store_path)

    def load_patterns(self) -> list[dict]:
        if not self.store_path.exists():
            return []
        with open(self.store_path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get("patterns", [])

    def add_pattern(self, pattern: dict) -> list[dict]:
        patterns = self.load_patterns()
        patterns.append({
            **pattern,
            "id": f"pattern_{len(patterns) + 1:04d}",
            "version": len(patterns) + 1,
        })
        self._save(patterns)
        return patterns

    def get_active_patterns(self) -> list[str]:
        return [p["rule"] for p in self.load_patterns() if p.get("active", True)]

    def deactivate_pattern(self, pattern_id: str) -> bool:
        patterns = self.load_patterns()
        for p in patterns:
            if p["id"] == pattern_id:
                p["active"] = False
                self._save(patterns)
                return True
        return False

    def clear(self):
        self._save([])

    def _save(self, patterns: list[dict]):
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump({"patterns": patterns}, f, indent=2)

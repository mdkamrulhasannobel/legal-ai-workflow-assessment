import difflib


class DiffEngine:
    def compute_diff(self, original: str, edited: str) -> dict:
        original_lines = original.splitlines(keepends=True)
        edited_lines = edited.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            original_lines,
            edited_lines,
            fromfile="original_draft",
            tofile="edited_draft",
            lineterm="",
        ))

        additions = []
        deletions = []
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                additions.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                deletions.append(line[1:])

        return {
            "diff_text": "\n".join(diff),
            "additions": additions,
            "deletions": deletions,
            "summary": self._summarize_changes(additions, deletions),
        }

    def _summarize_changes(self, additions: list[str], deletions: list[str]) -> str:
        summary_parts = []
        if deletions:
            summary_parts.append(f"Removed {len(deletions)} line(s)")
        if additions:
            summary_parts.append(f"Added {len(additions)} line(s)")
        return "; ".join(summary_parts) if summary_parts else "No changes"

import re
from typing import Optional


class Structurer:
    def extract_fields(self, raw_text: str, ocr_used: bool = False) -> dict:
        return {
            "parties": self._extract_parties(raw_text),
            "dates": self._extract_dates(raw_text),
            "clause_markers": self._extract_clause_markers(raw_text),
            "jurisdiction": self._extract_jurisdiction(raw_text),
            "document_type": self._classify_document(raw_text),
            "low_confidence_regions": self._flag_low_confidence(raw_text, ocr_used),
        }

    def _extract_parties(self, text: str) -> list[dict]:
        parties = []
        seen = set()

        line_patterns = [
            (r"(?im)^\s*(Plaintiff|Defendant|Petitioner|Respondent|Appellant|Appellee)\s*:?\s*([A-Z][A-Za-z0-9\s.&,-]+)", True),
            (r"(?im)^\s*(To|From)\s*:?\s*([A-Z][A-Za-z0-9\s.&,-]+)", True),
        ]
        for pattern, has_role in line_patterns:
            for match in re.finditer(pattern, text):
                role = match.group(1).strip()
                name = match.group(2).split(",")[0].strip().rstrip(".")
                if name and self._is_valid_party_name(name) and name.lower() not in seen:
                    seen.add(name.lower())
                    parties.append({"name": name, "role": role})

        between_match = re.search(
            r"(?is)between:\s*([A-Z][A-Za-z0-9\s.&,-]+?)\s*,?\s+(?:a|an)\s+.+?\(\s*\"?.+?\"?\s*\),?\s+and\s+([A-Z][A-Za-z0-9\s.&,-]+?)\s*,?\s+(?:a|an)\s+",
            text,
        )
        if between_match:
            for name in between_match.groups():
                cleaned = name.strip().rstrip(".")
                if cleaned and cleaned.lower() not in seen:
                    seen.add(cleaned.lower())
                    parties.append({"name": cleaned, "role": self._infer_role(cleaned, text)})

        generic_org_matches = re.findall(
            r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z.&]+){1,5}\s+(?:LLP|LLC|Inc\.|Inc|Corporation|Corp\.|Corp))\b",
            text,
        )
        for name in generic_org_matches:
            cleaned = name.strip().rstrip(".")
            if cleaned and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                parties.append({"name": cleaned, "role": self._infer_role(cleaned, text)})
        return parties

    def _is_valid_party_name(self, name: str) -> bool:
        lowered = name.lower()
        invalid_fragments = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
            "agreement",
            "statement of facts",
            "case brief",
            "requests judgment",
            "entered into",
            "agreed to",
            "performed substantial work",
        ]
        return not any(fragment in lowered for fragment in invalid_fragments)

    def _infer_role(self, name: str, text: str) -> str:
        text_lower = text.lower()
        name_lower = name.lower()
        if "plaintiff" in text_lower and name_lower in text_lower.split("plaintiff")[-1][:60]:
            return "Plaintiff"
        if "defendant" in text_lower and name_lower in text_lower.split("defendant")[-1][:60]:
            return "Defendant"
        return "Party"

    def _extract_dates(self, text: str) -> list[str]:
        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(m.group() for m in re.finditer(pattern, text))
        return sorted(set(dates))

    def _extract_clause_markers(self, text: str) -> list[str]:
        markers = []
        patterns = [
            r"(?im)^\s*(?:WHEREAS|NOW THEREFORE|IN WITNESS WHEREOF|IT IS HEREBY AGREED)\b",
            r"(?im)^\s*(?:Article|Section|Clause|Paragraph)\s+\d+[.:]?",
            r"(?im)^\s*\d+\.\s+[A-Z]",
            r"(?im)^\s*[A-Z][A-Z\s]{2,}(?:\n|:)",  # ALL CAPS HEADINGS
        ]
        seen = set()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                marker = match.group().strip()
                if marker.lower() not in seen:
                    seen.add(marker.lower())
                    markers.append(marker)
        return markers

    def _extract_jurisdiction(self, text: str) -> Optional[str]:
        patterns = [
            r"(?i)(?:in\s+the\s+)[A-Z][A-Za-z\s]+(?:Court|Tribunal|Commission)",
            r"(?i)(?:United\s+States\s+(?:District\s+)?Court)",
            r"(?i)(?:Superior\s+Court\s+of\s+)(?:the\s+)?[A-Z][A-Za-z]+",
            r"\b[A-Z]{2}\s+(?:District|Circuit|County)\s+Court\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    def _classify_document(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["plaintiff", "defendant", "complaint", "petition"]):
            return "Legal Pleading"
        if any(w in text_lower for w in ["contract", "agreement", "hereby", "whereas"]):
            return "Contract/Agreement"
        if any(w in text_lower for w in ["notice", "notification", "pursuant to"]):
            return "Notice Letter"
        if any(w in text_lower for w in ["brief", "argument", "appellant", "appellee"]):
            return "Legal Brief"
        return "General Document"

    def _flag_low_confidence(self, text: str, ocr_used: bool) -> list[dict]:
        if not ocr_used:
            return []
        flags = []
        lines = text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if len(line) < 15 and any(c.isalpha() for c in line):
                flags.append({
                    "line_number": i + 1,
                    "text": line,
                    "reason": "Short/isolated text fragment (possible OCR artifact)",
                })
            if sum(1 for c in line if not c.isprintable()) > len(line) * 0.3:
                flags.append({
                    "line_number": i + 1,
                    "text": line[:80],
                    "reason": "High proportion of non-printable characters",
                })
        return flags

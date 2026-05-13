import io
from pathlib import Path
from typing import Optional

import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text

from src.processing.ocr_engine import OCRProcessor


class DocumentExtractor:
    def __init__(self, ocr_processor: Optional[OCRProcessor] = None):
        self.ocr = ocr_processor or OCRProcessor()

    def extract(self, file_path: str | Path) -> tuple[str, bool]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(file_path)
        elif suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
            return self._extract_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def _extract_pdf(self, file_path: Path) -> tuple[str, bool]:
        text, used_ocr = self._try_text_layer(file_path)
        if not text.strip():
            text = self._fallback_ocr_pdf(file_path)
            used_ocr = True
        return text, used_ocr

    def _try_text_layer(self, file_path: Path) -> tuple[str, bool]:
        text_parts = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            full_text = "\n\n".join(text_parts)
            if full_text.strip():
                return full_text, False
        except Exception:
            pass

        try:
            full_text = pdfminer_extract_text(str(file_path))
            if full_text.strip():
                return full_text, False
        except Exception:
            pass

        return "", False

    def _fallback_ocr_pdf(self, file_path: Path) -> str:
        return self.ocr.process_pdf(file_path)

    def _extract_image(self, file_path: Path) -> tuple[str, bool]:
        text = self.ocr.process_image(file_path)
        return text, True

    def extract_text_only(self, file_path: str | Path) -> str:
        text, _ = self.extract(file_path)
        return text

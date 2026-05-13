import tempfile
from pathlib import Path
from typing import Optional

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter


class OCRProcessor:
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = "eng"):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.lang = lang

    def process_pdf(self, file_path: str | Path, dpi: int = 300) -> str:
        images = convert_from_path(str(file_path), dpi=dpi)
        text_parts = []
        for i, image in enumerate(images):
            processed = self._preprocess_image(image)
            text = pytesseract.image_to_string(processed, lang=self.lang)
            text_parts.append(f"--- Page {i + 1} ---\n{text}")
        return "\n\n".join(text_parts)

    def process_image(self, file_path: str | Path) -> str:
        image = Image.open(file_path)
        processed = self._preprocess_image(image)
        return pytesseract.image_to_string(processed, lang=self.lang)

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        img = image.convert("L")
        img = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return img

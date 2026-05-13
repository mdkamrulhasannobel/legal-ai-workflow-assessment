"""Tests for document extraction, OCR, and structuring."""
import json
from pathlib import Path

import pytest

from src.processing.extractor import DocumentExtractor
from src.processing.structurer import Structurer

SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_inputs"


@pytest.fixture
def extractor():
    return DocumentExtractor()


@pytest.fixture
def structurer():
    return Structurer()


def test_contract_scan_extraction(extractor):
    path = SAMPLE_DIR / "contract_scan.pdf"
    text, used_ocr = extractor.extract(path)
    assert len(text) > 100, "Extracted text is too short"
    assert "SERVICE AGREEMENT" in text or "Service Agreement" in text or "service" in text.lower()


def test_case_brief_extraction(extractor):
    path = SAMPLE_DIR / "case_brief.pdf"
    text, used_ocr = extractor.extract(path)
    assert len(text) > 100
    assert "Pearson Specter" in text or "GlobalCorp" in text


def test_notice_letter_extraction(extractor):
    path = SAMPLE_DIR / "notice_letter.pdf"
    text, used_ocr = extractor.extract(path)
    assert len(text) > 100


def test_extract_parties(structurer):
    text = "This Agreement is between Pearson Specter Litt LLP and GlobalCorp Industries Inc."
    fields = structurer.extract_fields(text)
    assert len(fields["parties"]) > 0


def test_extract_dates(structurer):
    text = "This Agreement is made on January 15, 2024. Signed on 01/20/2024."
    fields = structurer.extract_fields(text)
    assert len(fields["dates"]) >= 2


def test_classify_contract(structurer):
    text = "This Agreement is hereby made pursuant to the WHEREAS clauses."
    assert structurer._classify_document(text) == "Contract/Agreement"


def test_classify_pleading(structurer):
    text = "The plaintiff alleges that the defendant breached the contract."
    assert "Legal Pleading" in structurer._classify_document(text)

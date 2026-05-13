from pathlib import Path
from typing import Optional

from src.processing.extractor import DocumentExtractor
from src.processing.structurer import Structurer
from src.retrieval.chunker import DocumentChunker
from src.retrieval.store import VectorStore
from src.generation.drafter import DraftGenerator
from src.feedback.pattern_store import PatternStore


class LegalWorkflowPipeline:
    def __init__(
        self,
        extractor: Optional[DocumentExtractor] = None,
        structurer: Optional[Structurer] = None,
        chunker: Optional[DocumentChunker] = None,
        store: Optional[VectorStore] = None,
        drafter: Optional[DraftGenerator] = None,
        pattern_store: Optional[PatternStore] = None,
    ):
        self.extractor = extractor or DocumentExtractor()
        self.structurer = structurer or Structurer()
        self.chunker = chunker or DocumentChunker()
        self.store = store or VectorStore()
        self.drafter = drafter or DraftGenerator()
        self.pattern_store = pattern_store or PatternStore()

    def process_document(self, file_path: str | Path) -> dict:
        file_path = Path(file_path)
        raw_text, used_ocr = self.extractor.extract(file_path)
        structured = self.structurer.extract_fields(raw_text, ocr_used=used_ocr)

        chunks = self.chunker.chunk(raw_text, source_file=file_path.name)
        num_indexed = self.store.upsert_chunks(chunks)

        return {
            "file_name": file_path.name,
            "raw_text": raw_text,
            "structured_fields": structured,
            "used_ocr": used_ocr,
            "num_chunks": len(chunks),
            "num_indexed": num_indexed,
        }

    def generate_draft(self, document_result: dict, query: Optional[str] = None) -> str:
        query = query or f"Draft a case fact summary for {document_result['file_name']}"
        chunks = self.chunker.chunk(
            document_result["raw_text"],
            source_file=document_result["file_name"],
        )
        self.store.upsert_chunks(chunks)
        retrieved = self.store.query(
            query,
            top_k=5,
            source_file=document_result["file_name"],
        )
        learned_patterns = self.pattern_store.get_active_patterns()

        draft = self.drafter.generate(
            document_name=document_result["file_name"],
            structured_fields=document_result["structured_fields"],
            retrieved_chunks=retrieved,
            learned_patterns=learned_patterns,
        )
        return draft

    def run_end_to_end(self, file_path: str | Path, query: Optional[str] = None) -> dict:
        doc_result = self.process_document(file_path)
        draft = self.generate_draft(doc_result, query)
        return {
            "document": doc_result,
            "draft": draft,
        }

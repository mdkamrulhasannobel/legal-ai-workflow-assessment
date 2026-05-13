"""Tests for document chunking and vector store."""
import tempfile
from pathlib import Path

import pytest

from src.retrieval.chunker import DocumentChunker
from src.retrieval.embedder import Embedder
from src.retrieval.store import VectorStore


@pytest.fixture
def chunker():
    return DocumentChunker(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def embedder():
    return Embedder()


def test_chunking_basic(chunker):
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunker.chunk(text)
    assert len(chunks) > 0
    for c in chunks:
        assert "text" in c
        assert "metadata" in c
        assert "chunk_id" in c["metadata"]


def test_chunk_metadata(chunker):
    text = "Test content.\n\nMore content."
    chunks = chunker.chunk(text, source_file="test.pdf", page_num=1)
    for c in chunks:
        assert c["metadata"]["source_file"] == "test.pdf"
        assert c["metadata"]["page_num"] == 1


def test_embedder_basic(embedder):
    vec = embedder.embed("This is a test sentence.")
    assert len(vec) > 0
    assert all(isinstance(v, float) for v in vec)


def test_embedder_dimension(embedder):
    assert embedder.dimension == 384


def test_embedder_batch(embedder):
    texts = ["First text.", "Second text.", "Third text."]
    vectors = embedder.embed_batch(texts)
    assert len(vectors) == 3


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmp:
        yield VectorStore(
            collection_name="test_collection",
            persist_dir=tmp,
        )


def test_store_upsert_and_count(store):
    chunks = [
        {
            "text": "This is a test chunk about legal matters.",
            "metadata": {"chunk_id": "chunk_0000", "source_file": "test.pdf", "page_num": 1},
        }
    ]
    count = store.upsert_chunks(chunks)
    assert count == 1
    assert store.count() == 1


def test_store_query(store):
    chunks = [
        {
            "text": "The parties agree to the terms of this contract.",
            "metadata": {"chunk_id": "chunk_0000", "source_file": "test.pdf", "page_num": 1},
        },
        {
            "text": "Weather reports for New York City area.",
            "metadata": {"chunk_id": "chunk_0001", "source_file": "test.pdf", "page_num": 1},
        },
    ]
    store.upsert_chunks(chunks)
    results = store.query("contract agreement terms", top_k=2)
    assert len(results) > 0

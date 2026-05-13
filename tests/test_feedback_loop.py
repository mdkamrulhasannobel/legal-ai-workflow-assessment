"""Tests for the edit feedback loop."""
import tempfile
from pathlib import Path

import pytest

from src.feedback.diff_engine import DiffEngine


@pytest.fixture
def diff_engine():
    return DiffEngine()


def test_diff_compute(diff_engine):
    original = "This is the original draft.\nIt has two lines."
    edited = "This is the edited draft.\nIt has two lines.\nAnd a third line."
    result = diff_engine.compute_diff(original, edited)
    assert "additions" in result
    assert "deletions" in result
    assert len(result["additions"]) > 0


def test_diff_no_changes(diff_engine):
    text = "Identical text."
    result = diff_engine.compute_diff(text, text)
    assert result["summary"] == "No changes"


def test_diff_summary_additions(diff_engine):
    original = "Line one."
    edited = "Line one.\nLine two.\nLine three."
    result = diff_engine.compute_diff(original, edited)
    assert "Added" in result["summary"]


def test_diff_summary_deletions(diff_engine):
    original = "Line one.\nLine two.\nLine three."
    edited = "Line one."
    result = diff_engine.compute_diff(original, edited)
    assert "Removed" in result["summary"]


def test_diff_summary_both(diff_engine):
    original = "Line one.\nOld line."
    edited = "Line one.\nNew line.\nExtra line."
    result = diff_engine.compute_diff(original, edited)
    assert "Removed" in result["summary"]
    assert "Added" in result["summary"]

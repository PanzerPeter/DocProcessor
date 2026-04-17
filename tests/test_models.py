"""Tests for DocumentResult model validation."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

# conftest.py inserts doc_processor/ onto sys.path
from models import DocumentCategory, DocumentResult


def _valid_payload(**overrides) -> dict:
    base = {
        "category": "invoice",
        "language": "English",
        "summary": "Test invoice for services rendered.",
        "key_fields": {"total": "100 USD"},
        "confidence": 0.95,
    }
    return {**base, **overrides}


def test_valid_result():
    result = DocumentResult(**_valid_payload())
    assert result.category == DocumentCategory.INVOICE
    assert result.confidence == 0.95


def test_confidence_bounds():
    with pytest.raises(ValidationError):
        DocumentResult(**_valid_payload(confidence=1.1))
    with pytest.raises(ValidationError):
        DocumentResult(**_valid_payload(confidence=-0.1))


def test_empty_summary_rejected():
    with pytest.raises(ValidationError):
        DocumentResult(**_valid_payload(summary="   "))


def test_unknown_category_rejected():
    with pytest.raises(ValidationError):
        DocumentResult(**_valid_payload(category="unknown"))


def test_to_dict_excludes_none():
    result = DocumentResult(**_valid_payload())
    d = result.to_dict()
    assert "page_count" not in d
    assert "char_count" not in d


def test_to_dict_includes_set_fields():
    result = DocumentResult(**_valid_payload(), page_count=3, char_count=1200)
    d = result.to_dict()
    assert d["page_count"] == 3
    assert d["char_count"] == 1200

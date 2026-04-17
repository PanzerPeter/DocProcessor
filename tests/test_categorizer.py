"""Tests for the categorizer — uses real API calls, requires ANTHROPIC_API_KEY."""
from __future__ import annotations

import os

import pytest

from categorizer import categorize
from models import DocumentCategory, DocumentResult

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live API tests",
)

SAMPLE_INVOICE = """
INVOICE #2026/03/042
Date: 2026-03-15
Vendor: Példa Kft.
Services: IT consulting for March 2026
Total: 450,000 HUF
Due: 2026-04-15
"""


def test_categorize_invoice():
    result = categorize(SAMPLE_INVOICE, source_file="test_invoice.txt")
    assert isinstance(result, DocumentResult)
    assert result.category == DocumentCategory.INVOICE
    assert result.confidence > 0.5
    assert result.source_file == "test_invoice.txt"


def test_categorize_returns_language():
    result = categorize(SAMPLE_INVOICE)
    assert result.language  # non-empty string


def test_categorize_extracts_key_fields():
    result = categorize(SAMPLE_INVOICE)
    # At least some key fields should be extracted
    assert len(result.key_fields) > 0

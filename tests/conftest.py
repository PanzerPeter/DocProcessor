"""Shared fixtures for DocProcessor tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make doc_processor importable without installation
sys.path.insert(0, str(Path(__file__).parent.parent / "doc_processor"))


FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_dir() -> Path:
    return FIXTURE_DIR

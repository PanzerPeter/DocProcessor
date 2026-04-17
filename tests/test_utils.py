"""Tests for file validation and collection utilities."""
from __future__ import annotations

import pytest

from exceptions import UnsupportedFileTypeError
from utils import collect_files, validate_file


def test_validate_file_not_found():
    with pytest.raises(FileNotFoundError):
        validate_file("/tmp/does_not_exist_abc123.pdf")


def test_validate_file_unsupported_extension(tmp_path):
    f = tmp_path / "doc.docx"
    f.write_text("content")
    with pytest.raises(UnsupportedFileTypeError):
        validate_file(str(f))


def test_validate_file_valid(tmp_path):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"%PDF-1.4")
    result = validate_file(str(f))
    assert result == f


def test_collect_files_from_directory(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    (tmp_path / "b.png").write_bytes(b"PNG")
    (tmp_path / "c.docx").write_text("ignored")
    collected = collect_files([str(tmp_path)])
    names = {p.split("/")[-1] for p in collected}
    assert "a.pdf" in names
    assert "b.png" in names
    assert "c.docx" not in names


def test_collect_files_single(tmp_path):
    f = tmp_path / "test.pdf"
    f.write_bytes(b"%PDF")
    collected = collect_files([str(f)])
    assert len(collected) == 1

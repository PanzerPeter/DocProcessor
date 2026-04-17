from __future__ import annotations

import os
from pathlib import Path

from exceptions import UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"})


def validate_file(filepath: str) -> Path:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{path.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    return path


def collect_files(inputs: list[str]) -> list[str]:
    """Expand files and directories into a flat list of supported file paths."""
    collected: list[str] = []
    for entry in inputs:
        path = Path(entry)
        if path.is_dir():
            for ext in SUPPORTED_EXTENSIONS:
                collected.extend(str(p) for p in sorted(path.rglob(f"*{ext}")))
        elif path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                collected.append(str(path))
        else:
            # Glob pattern already expanded by shell, or literal path that doesn't exist
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                collected.append(str(path))
    return collected


def get_file_size_mb(filepath: str) -> float:
    return os.path.getsize(filepath) / (1024 * 1024)

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # Claude API
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 1024
    max_input_chars: int = 8000

    # Retry
    api_retries: int = 3
    api_retry_delay: float = 2.0  # seconds, doubles each attempt

    # OCR
    tesseract_languages: str = "eng+hun"
    ocr_dpi: int = 300

    # Output
    output_indent: int = 2
    min_confidence: float = 0.0

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "WARNING"))

    @classmethod
    def from_env(cls) -> "Config":
        c = cls()
        if v := os.getenv("DOC_MODEL"):
            c.model = v
        if v := os.getenv("DOC_MAX_INPUT_CHARS"):
            c.max_input_chars = int(v)
        if v := os.getenv("DOC_OCR_LANGS"):
            c.tesseract_languages = v
        if v := os.getenv("DOC_MIN_CONFIDENCE"):
            c.min_confidence = float(v)
        if v := os.getenv("DOC_API_RETRIES"):
            c.api_retries = int(v)
        return c


# Module-level singleton — override in tests by reassigning config.CFG
CFG = Config.from_env()

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DocumentCategory(str, Enum):
    INVOICE = "invoice"
    CONTRACT = "contract"
    REPORT = "report"
    FORM = "form"
    OTHER = "other"


class DocumentResult(BaseModel):
    category: DocumentCategory
    language: str
    summary: str = Field(max_length=500)
    key_fields: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    source_file: str = ""

    # Populated by the extractor, not the AI
    page_count: int | None = None
    char_count: int | None = None

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v.strip()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

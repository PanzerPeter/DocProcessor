from __future__ import annotations

import json
import logging
import time

import anthropic
from pydantic import ValidationError

from config import CFG
from exceptions import CategorizationError
from models import DocumentResult

logger = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


SYSTEM = """You are a document categorizer.
Given raw document text, return ONLY a valid JSON object with these exact fields:
- category: string, one of: invoice, contract, report, form, other
- language: string (e.g. "English", "Hungarian")
- summary: string, max 2 sentences describing the document
- key_fields: object with important extracted key-value pairs (dates, names, amounts, IDs, etc.)
- confidence: float between 0 and 1

No preamble. No markdown fences. No explanation. Raw JSON only."""


def categorize(raw_text: str, source_file: str = "") -> DocumentResult:
    truncated = raw_text[: CFG.max_input_chars]
    if len(raw_text) > CFG.max_input_chars:
        logger.warning(
            "Input truncated from %d to %d chars", len(raw_text), CFG.max_input_chars
        )

    last_error: Exception | None = None
    for attempt in range(1, CFG.api_retries + 1):
        try:
            result = _call_api(truncated)
            result.source_file = source_file
            return result
        except (CategorizationError, ValidationError) as e:
            last_error = e
            if attempt < CFG.api_retries:
                delay = CFG.api_retry_delay * (2 ** (attempt - 1))
                logger.warning("Attempt %d failed (%s). Retrying in %.1fs.", attempt, e, delay)
                time.sleep(delay)
            else:
                logger.error("All %d attempts failed.", CFG.api_retries)

    raise CategorizationError(
        f"Categorization failed after {CFG.api_retries} attempts: {last_error}"
    )


def _call_api(text: str) -> DocumentResult:
    logger.debug("Calling Claude API (model=%s, input_chars=%d)", CFG.model, len(text))
    try:
        response = _get_client().messages.create(
            model=CFG.model,
            max_tokens=CFG.max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": text}],
        )
    except anthropic.APIError as e:
        raise CategorizationError(f"API error: {e}") from e

    raw = response.content[0].text
    logger.debug("Raw API response: %s", raw[:200])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise CategorizationError(f"Model returned invalid JSON: {e}\nResponse: {raw[:300]}") from e

    try:
        return DocumentResult(**data)
    except ValidationError as e:
        raise CategorizationError(f"Response failed schema validation: {e}") from e

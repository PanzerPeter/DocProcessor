# AGENTS.md — AI Agent Guidelines for DocProcessor

This file instructs AI coding assistants (Claude Code, Copilot, Cursor, etc.) on how to work within this codebase safely and correctly.

## Architecture

Three-stage linear pipeline. Each stage has one responsibility:

1. **`extractor.py`** — file I/O and text extraction only. No categorization logic here.
2. **`categorizer.py`** — Claude API call only. No file I/O, no extraction logic here.
3. **`main.py`** — orchestration and CLI only. Business logic belongs in the other modules.
4. **`utils.py`** — stateless helpers only. No side effects.

Do not collapse stages or add cross-stage dependencies. The separation is intentional.

## Claude API Usage

- Model: `claude-sonnet-4-6` — do not downgrade to Haiku for this workload; accuracy matters more than cost here.
- Input is capped at `MAX_INPUT_CHARS = 8000` in `categorizer.py`. Do not increase this without profiling token usage.
- System prompt in `categorizer.py` instructs the model to return only raw JSON. Do not add markdown fences, preamble, or examples to it — they make the output harder to parse.
- The response is parsed with `json.loads` directly. If you change the prompt, verify the output remains parseable.

## JSON Output Schema

The output schema is a public contract. Do not change field names, types, or remove fields without a version bump in `pyproject.toml` and a `CHANGELOG` entry.

```json
{
  "category": "string (invoice|contract|report|form|other)",
  "language": "string",
  "summary": "string",
  "key_fields": {},
  "confidence": 0.0,
  "source_file": "string"
}
```

## File Handling

- `validate_file()` in `utils.py` is the single entry point for path validation. Always call it before passing a path to `extract()`.
- Never write extracted text or intermediate results to disk. Keep everything in memory through the pipeline.
- Never log or print document content. It may contain PII.

## Dependencies

Do not add new dependencies without opening an issue first. The dependency list is intentionally minimal:

| Package | Purpose |
|---------|---------|
| `anthropic` | Claude API client |
| `pymupdf` | Native PDF parsing |
| `pytesseract` | Tesseract OCR binding |
| `Pillow` | Image loading and pixel manipulation |

Tesseract is a system dependency — do not replace it with a Python OCR library.

## Testing

- Tests live in `tests/` (not yet scaffolded — contributions welcome).
- Do not mock the Claude API in integration tests — use real API calls against test fixtures.
- Fixture documents must not contain real PII.

## Security

- `ANTHROPIC_API_KEY` comes from environment only. Never hardcode, log, or pass as CLI argument.
- Do not add any telemetry, analytics, or outbound calls beyond the Anthropic API.
- Do not store extracted document text outside the process.

## What to Avoid

- Do not refactor working code speculatively.
- Do not add error handling for impossible paths.
- Do not add retry logic to the Claude API call without discussing it first — silent retries can double costs.
- Do not change `lang="eng+hun"` in Tesseract calls without testing on Hungarian documents.

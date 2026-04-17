# DocProcessor

A lightweight, three-stage pipeline for extracting and categorizing documents (PDFs and images) using PyMuPDF, Tesseract OCR, and the Claude AI API.

```
Input (PDF / Image)
      │
      ▼
 [ Extractor ]        ← PyMuPDF + Tesseract OCR
      │
      ▼
 [ AI Categorizer ]   ← Claude API + Pydantic validation
      │
      ▼
 [ JSON / JSONL / CSV Output ]
```

## Features

- Native PDF text extraction via PyMuPDF — 10× faster than PyPDF2
- Automatic OCR fallback for scanned pages (per-page detection)
- Direct image input: PNG, JPG, TIFF, BMP, WebP
- AI categorization and structured key-field extraction via Claude API
- Pydantic-validated output schema — no silent data corruption
- Exponential-backoff retry on API failures
- Batch processing: files, globs, entire directories
- Output formats: JSON, JSONL, CSV
- Per-file output directory mode
- Confidence threshold filtering (`--min-confidence`)
- Rich progress bar and summary table
- Fully configurable via environment variables
- Bilingual OCR: English + Hungarian (`eng+hun`)

## Requirements

- Python ≥ 3.11
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed system-wide
- Anthropic API key

### Install Tesseract

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-hun
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:** Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

## Installation

```bash
git clone https://github.com/youruser/doc-processor.git
cd doc-processor
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e .
```

## Configuration

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Additional environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | **Required.** Anthropic API key |
| `DOC_MODEL` | `claude-sonnet-4-6` | Claude model to use |
| `DOC_MAX_INPUT_CHARS` | `8000` | Max chars sent to Claude |
| `DOC_OCR_LANGS` | `eng+hun` | Tesseract language string |
| `DOC_MIN_CONFIDENCE` | `0.0` | Global confidence threshold |
| `DOC_API_RETRIES` | `3` | API retry attempts |
| `LOG_LEVEL` | `WARNING` | Python log level |

## Usage

```bash
# Single file → stdout
doc-processor invoice.pdf

# Image file
doc-processor scan.png

# Batch — all PDFs in a directory
doc-processor docs/ --output-dir results/

# Multiple files, JSONL output
doc-processor *.pdf --format jsonl --output results.jsonl

# CSV export, skip low-confidence results
doc-processor docs/ --format csv --min-confidence 0.75 --output summary.csv

# Debug logging
doc-processor invoice.pdf --verbose
```

### Example Output

```json
{
  "category": "invoice",
  "language": "Hungarian",
  "summary": "Invoice from Példa Kft. for IT services in March 2026. Total amount is 450,000 HUF.",
  "key_fields": {
    "invoice_number": "2026/03/042",
    "date": "2026-03-15",
    "total": "450000 HUF",
    "vendor": "Példa Kft."
  },
  "confidence": 0.94,
  "source_file": "szamla_marc.pdf",
  "page_count": 2,
  "char_count": 3471
}
```

### Supported Categories

| Category | Description |
|----------|-------------|
| `invoice` | Bills, receipts, tax invoices |
| `contract` | Agreements, legal documents |
| `report` | Reports, analyses, summaries |
| `form` | Filled or blank forms |
| `other` | Anything not matching above |

## Project Structure

```
doc_processor/
├── main.py           # CLI entry point, batch orchestrator
├── extractor.py      # Text extraction (PyMuPDF + Tesseract)
├── categorizer.py    # Claude API call, retry logic
├── models.py         # Pydantic output schema
├── exceptions.py     # Custom exception hierarchy
├── config.py         # Config dataclass, env var loading
└── utils.py          # File validation, directory collection
tests/
├── conftest.py
├── test_models.py    # Pydantic validation tests
├── test_utils.py     # File helper tests
├── test_categorizer.py  # Live API tests (requires API key)
└── fixtures/         # Put test PDFs/images here
pyproject.toml
requirements.txt
```

## Running Tests

```bash
# Fast tests (no API key needed)
pytest tests/test_models.py tests/test_utils.py

# All tests including live API calls
ANTHROPIC_API_KEY=your_key pytest

# With coverage
pytest --cov=doc_processor
```

## Design Decisions

| Decision | Reason |
|----------|--------|
| PyMuPDF over PyPDF2 | 10× faster, handles scanned PDFs and multi-column layouts natively |
| Claude API for categorization | No custom ML model to train or maintain |
| Pydantic output validation | Catches malformed API responses before they corrupt downstream data |
| Exponential backoff on retries | Handles transient API rate limits gracefully |
| 8000-char input guard | Prevents token overflow on large documents |
| `lang="eng+hun"` | Covers both English and Hungarian documents |
| `rich` for CLI output | Progress bar + summary table — no printf debugging |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

GNU General Public License v3 with additional restrictions. See [LICENSE](LICENSE).

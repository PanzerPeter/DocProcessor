# DocProcessor

A lightweight, three-stage pipeline for extracting and categorizing documents (PDFs and images) using PyMuPDF, Tesseract OCR, and the Claude AI API.

```
Input (PDF / Image)
      │
      ▼
 [ Extractor ]        ← PyMuPDF + Tesseract
      │
      ▼
 [ AI Categorizer ]   ← Claude API
      │
      ▼
 [ JSON Output ]
```

## Features

- Native PDF text extraction via PyMuPDF
- Automatic OCR fallback for scanned pages via Tesseract
- Direct image input (PNG, JPG, TIFF, BMP, WebP)
- AI categorization and key-field extraction via Claude API
- Bilingual support: English + Hungarian (`eng+hun`)
- Structured JSON output — pipe into databases, scripts, or APIs

## Requirements

- Python ≥ 3.11
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

**Windows:** Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

## Installation

### Using uv (recommended)

```bash
git clone https://github.com/youruser/doc-processor.git
cd doc-processor
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Using pip

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_api_key_here
```

The `anthropic` library reads `ANTHROPIC_API_KEY` from the environment automatically.

## Usage

```bash
cd doc_processor
python main.py path/to/document.pdf
python main.py path/to/scan.png
python main.py invoice.pdf --output result.json
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
  "source_file": "szamla_marc.pdf"
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
├── main.py           # CLI entry point, orchestrates the pipeline
├── extractor.py      # Text extraction (PyMuPDF + Tesseract)
├── categorizer.py    # AI structuring via Claude API
└── utils.py          # File validation and helpers
pyproject.toml        # Project metadata and dependencies
requirements.txt      # Pinned dependencies
```

## Design Decisions

| Decision | Reason |
|----------|--------|
| PyMuPDF over PyPDF2 | 10× faster, handles scanned PDFs and multi-column layouts natively |
| Claude API for categorization | No custom ML model to train or maintain |
| 8000-char input guard | Prevents token overflow on large documents |
| `lang="eng+hun"` | Covers both English and Hungarian documents |
| Single JSON schema | Predictable output, easy to pipe into databases |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

GNU General Public License v3 with additional restrictions. See [LICENSE](LICENSE).

# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [0.1.0] - 2026-04-17

### Added
- Initial release
- PDF text extraction via PyMuPDF with automatic OCR fallback for scanned pages
- Image input support (PNG, JPG, TIFF, BMP, WebP)
- AI categorization and key-field extraction via Claude API (`claude-sonnet-4-6`)
- English + Hungarian OCR language support
- CLI with `--output` flag for writing JSON to file
- File validation with clear error messages

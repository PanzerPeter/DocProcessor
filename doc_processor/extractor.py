from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from config import CFG
from exceptions import EmptyDocumentError, ExtractionError

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    text: str
    page_count: int
    char_count: int
    method: str  # "native", "ocr", "mixed", "image"


def extract(filepath: str) -> ExtractionResult:
    path = Path(filepath)
    logger.info("Extracting: %s", path.name)
    try:
        if path.suffix.lower() == ".pdf":
            return _extract_pdf(filepath)
        return _extract_image(filepath)
    except (fitz.FileDataError, pytesseract.TesseractError, OSError) as e:
        raise ExtractionError(f"Failed to extract '{path.name}': {e}") from e


def _extract_pdf(path: str) -> ExtractionResult:
    doc = fitz.open(path)
    texts: list[str] = []
    native_pages = 0
    ocr_pages = 0

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            texts.append(text)
            native_pages += 1
            logger.debug("Page %d: native text (%d chars)", page_num, len(text))
        else:
            logger.debug("Page %d: no native text, running OCR", page_num)
            pix = page.get_pixmap(dpi=CFG.ocr_dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img, lang=CFG.tesseract_languages)
            texts.append(ocr_text)
            ocr_pages += 1

    full_text = "\n".join(texts)
    page_count = len(doc)

    if native_pages == page_count:
        method = "native"
    elif ocr_pages == page_count:
        method = "ocr"
    else:
        method = "mixed"

    logger.info(
        "PDF extraction complete: %d pages, method=%s, %d chars",
        page_count, method, len(full_text),
    )
    return ExtractionResult(
        text=full_text,
        page_count=page_count,
        char_count=len(full_text),
        method=method,
    )


def _extract_image(path: str) -> ExtractionResult:
    text = pytesseract.image_to_string(
        Image.open(path), lang=CFG.tesseract_languages
    )
    logger.info("Image OCR complete: %d chars", len(text))
    return ExtractionResult(
        text=text,
        page_count=1,
        char_count=len(text),
        method="image",
    )

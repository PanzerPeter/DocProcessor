import fitz
import pytesseract
from PIL import Image


def extract(filepath: str) -> str:
    if filepath.lower().endswith(".pdf"):
        return _extract_pdf(filepath)
    return _extract_image(filepath)


def _extract_pdf(path: str) -> str:
    doc = fitz.open(path)
    texts = []
    for page in doc:
        text = page.get_text()
        if not text.strip():
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang="eng+hun")
        texts.append(text)
    return "\n".join(texts)


def _extract_image(path: str) -> str:
    return pytesseract.image_to_string(Image.open(path), lang="eng+hun")

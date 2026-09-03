"""Document upload → OCR → PII-masked extraction."""

from __future__ import annotations

import re
from pathlib import Path

from . import config, llm
from .models import DocumentExtraction

# Malaysian NRIC (YYMMDD-XX-XXXX), emails, phone numbers.
_NRIC = re.compile(r"\b\d{6}-\d{2}-\d{4}\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?:\+?6?01)[0-9][\d -]{6,10}\d")


def extract_text(path: str | Path) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        import pdfplumber

        with pdfplumber.open(p) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(p))
    return p.read_text(encoding="utf-8", errors="ignore")


def mask_pii(text: str) -> str:
    out = _NRIC.sub("[REDACTED_NRIC]", text)
    out = _EMAIL.sub("[REDACTED_EMAIL]", out)
    out = _PHONE.sub("[REDACTED_PHONE]", out)
    return out


def extract(path: str | Path) -> DocumentExtraction:
    raw = extract_text(path)
    masked = mask_pii(raw)
    fields: dict = {}
    try:
        fields = llm.complete_json(
            "Extract structured fields from a vehicle document. Return ONLY JSON "
            "of key fields (owner_name, nric, vehicle_model, registration_plate, "
            "year, insurer, policy_number). Use null for missing fields.",
            masked,
        )
    except Exception:
        fields = {}
    return DocumentExtraction(text=masked, masked=masked != raw, fields=fields)

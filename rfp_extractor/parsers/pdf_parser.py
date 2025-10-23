from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import io

import pdfplumber


@dataclass
class PDFParseResult:
    text: str
    metadata: Dict[str, Any]


def parse_pdf_bytes(pdf_bytes: bytes) -> PDFParseResult:
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    full_text = "\n".join(part.strip() for part in text_parts if part and part.strip())
    return PDFParseResult(text=full_text, metadata={})

from __future__ import annotations
from typing import Dict, List

from rfp_extractor.schema import FIELD_SYNONYMS


SYSTEM_INSTRUCTIONS = (
    "You are an expert at extracting procurement RFP fields from messy text."
)


def build_extraction_prompt(text: str) -> str:
    fields = [
        "Bid Number",
        "Title",
        "Due Date",
        "Bid Submission Type",
        "Term of Bid",
        "Pre Bid Meeting",
        "Installation",
        "Bid Bond Requirement",
        "Delivery Date",
        "Payment Terms",
        "Any Additional Documentation Required",
        "MFG for Registration",
        "Contract or Cooperative to use",
        "Bid Summary",
        "Product Specification",
        "Model no",
        "Part no",
        "product contact info company name",
    ]

    synonyms_text = "\n".join(
        f"- {k}: {', '.join(v)}" for k, v in FIELD_SYNONYMS.items()
    )

    prompt = f"""
{SYSTEM_INSTRUCTIONS}
Extract the following fields from the provided document text.
Return ONLY a compact JSON object with these exact keys (use empty string if missing):
{fields}

Synonyms and hints (helpful but not exhaustive):
{synonyms_text}

Document text:
{text}
""".strip()
    return prompt

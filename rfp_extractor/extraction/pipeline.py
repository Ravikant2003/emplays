from __future__ import annotations
import json
import re
from typing import Dict, Any, Optional

from rfp_extractor.schema import RFPData, ProductSpec
from rfp_extractor.extraction.prompting import build_extraction_prompt


def simple_heuristic_extract(text: str) -> Dict[str, Any]:
    patterns = {
        "bid_number": r"(?i)bid\s*(number|no\.?):?\s*([\w\-\/]+)",
        "due_date": r"(?i)(due\s*date|closing|deadline)[^\n:]*[:\-]?\s*([^\n]+)",
        "title": r"(?i)(title|subject)[^\n:]*[:\-]?\s*([^\n]+)",
    }
    result: Dict[str, Any] = {}
    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            result[key] = m.group(2).strip()
    return result


class ExtractionPipeline:
    def __init__(self, llm=None):
        self.llm = llm

    def extract(self, text: str) -> RFPData:
        # Start with heuristics
        data = simple_heuristic_extract(text)

        # Use LLM for structured JSON
        llm_json = {}
        if self.llm:
            prompt = build_extraction_prompt(text[:8000])  # keep prompt size bounded
            try:
                raw = self.llm.extract_json(prompt)
                llm_json = self._safe_json_parse(raw)
            except Exception:
                llm_json = {}

        merged = self._merge(heur=data, llm=llm_json)
        # Build ProductSpec if relevant
        product = ProductSpec(
            model_no=merged.get("Model no"),
            part_no=merged.get("Part no"),
            product_contact_info_company_name=merged.get(
                "product contact info company name"
            ),
        )
        rfp = RFPData(
            bid_number=merged.get("Bid Number") or merged.get("bid_number"),
            title=merged.get("Title") or merged.get("title"),
            due_date=merged.get("Due Date") or merged.get("due_date"),
            bid_submission_type=merged.get("Bid Submission Type"),
            term_of_bid=merged.get("Term of Bid"),
            pre_bid_meeting=merged.get("Pre Bid Meeting"),
            installation=merged.get("Installation"),
            bid_bond_requirement=merged.get("Bid Bond Requirement"),
            delivery_date=merged.get("Delivery Date"),
            payment_terms=merged.get("Payment Terms"),
            additional_docs_required=merged.get("Any Additional Documentation Required"),
            mfg_for_registration=merged.get("MFG for Registration"),
            contract_or_coop_to_use=merged.get("Contract or Cooperative to use"),
            bid_summary=merged.get("Bid Summary"),
            product_specification=merged.get("Product Specification"),
            product=product,
        )
        return rfp

    @staticmethod
    def _safe_json_parse(s: str) -> Dict[str, Any]:
        try:
            return json.loads(s)
        except Exception:
            # try to locate JSON substring
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(s[start : end + 1])
                except Exception:
                    return {}
            return {}

    @staticmethod
    def _merge(heur: Dict[str, Any], llm: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(llm)
        for k, v in heur.items():
            if not merged.get(k):
                merged[k] = v
        # Normalize keys: title-case keys expected in JSON output
        key_map = {
            "bid_number": "Bid Number",
            "due_date": "Due Date",
            "title": "Title",
        }
        for k, v in list(merged.items()):
            if k in key_map:
                merged[key_map[k]] = v
                del merged[k]
        return merged

from __future__ import annotations
import json
from pathlib import Path
from typing import Union, Dict

from rfp_extractor.schema import RFPData


def to_full_alias_dict(data: RFPData) -> Dict[str, str]:
    product = data.product
    return {
        "Bid Number": data.bid_number or "",
        "Title": data.title or "",
        "Due Date": data.due_date or "",
        "Bid Submission Type": data.bid_submission_type or "",
        "Term of Bid": data.term_of_bid or "",
        "Pre Bid Meeting": data.pre_bid_meeting or "",
        "Installation": data.installation or "",
        "Bid Bond Requirement": data.bid_bond_requirement or "",
        "Delivery Date": data.delivery_date or "",
        "Payment Terms": data.payment_terms or "",
        "Any Additional Documentation Required": data.additional_docs_required or "",
        "MFG for Registration": data.mfg_for_registration or "",
        "Contract or Cooperative to use": data.contract_or_coop_to_use or "",
        "Bid Summary": data.bid_summary or "",
        "Product Specification": data.product_specification or "",
        "Model no": (product.model_no if product else None) or "",
        "Part no": (product.part_no if product else None) or "",
        "product contact info company name": (product.product_contact_info_company_name if product else None) or "",
    }


def save_json(data: RFPData, path: Union[str, Path]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(to_full_alias_dict(data), f, ensure_ascii=False, indent=2)

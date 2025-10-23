from __future__ import annotations
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ProductSpec(BaseModel):
    model_no: Optional[str] = Field(None, alias="Model no")
    part_no: Optional[str] = Field(None, alias="Part no")
    product_contact_info_company_name: Optional[str] = Field(
        None, alias="product contact info company name"
    )


class RFPData(BaseModel):
    bid_number: Optional[str] = Field(None, alias="Bid Number")
    title: Optional[str] = Field(None, alias="Title")
    due_date: Optional[str] = Field(None, alias="Due Date")
    bid_submission_type: Optional[str] = Field(None, alias="Bid Submission Type")
    term_of_bid: Optional[str] = Field(None, alias="Term of Bid")
    pre_bid_meeting: Optional[str] = Field(None, alias="Pre Bid Meeting")
    installation: Optional[str] = Field(None, alias="Installation")
    bid_bond_requirement: Optional[str] = Field(None, alias="Bid Bond Requirement")
    delivery_date: Optional[str] = Field(None, alias="Delivery Date")
    payment_terms: Optional[str] = Field(None, alias="Payment Terms")
    additional_docs_required: Optional[str] = Field(
        None, alias="Any Additional Documentation Required"
    )
    mfg_for_registration: Optional[str] = Field(None, alias="MFG for Registration")
    contract_or_coop_to_use: Optional[str] = Field(
        None, alias="Contract or Cooperative to use"
    )
    bid_summary: Optional[str] = Field(None, alias="Bid Summary")
    product_specification: Optional[str] = Field(None, alias="Product Specification")
    product: Optional[ProductSpec] = None

    class Config:
        allow_population_by_field_name = True


# Synonyms map for extraction heuristics/LLM guidance
FIELD_SYNONYMS: Dict[str, List[str]] = {
    "bid_number": ["bid no", "tender no", "rfp no", "solicitation number"],
    "title": ["rfp title", "tender title", "subject"],
    "due_date": ["bid due", "closing date", "submission deadline", "due date/time"],
    "bid_submission_type": ["submission method", "online submission", "hard copy"],
    "term_of_bid": ["contract term", "duration", "period of performance"],
    "pre_bid_meeting": ["pre-bid", "pre bid conference", "pre proposal"],
    "installation": ["installation required", "install", "setup"],
    "bid_bond_requirement": ["bid bond", "bonding", "security deposit"],
    "delivery_date": ["delivery", "completion date", "installation date"],
    "payment_terms": ["payment", "net", "milestone", "terms"],
    "additional_docs_required": ["supporting documents", "attachments", "forms"],
    "mfg_for_registration": ["manufacturer registration", "mfg registration"],
    "contract_or_coop_to_use": ["cooperative", "contract vehicle", "consortium"],
    "bid_summary": ["summary", "overview", "scope"],
    "product_specification": ["spec", "technical specification", "requirements"],
}

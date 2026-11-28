"""The deterministic layers: cheap, exact, no model call."""
from __future__ import annotations

import re

from pydantic import BaseModel, Field, ValidationError

from .verdict import Verdict


class ListingCopy(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=20, max_length=600)


class Record(BaseModel):
    """What the catalog says is true about the product."""
    sku: str
    supplier_name: str
    weight_capacity_lbs: int | None = None
    safety_claims: list[str] = []


# --8<-- [start:guard-schema]
def schema_check(raw: dict) -> tuple[Verdict, ListingCopy | None]:
    try:
        return Verdict(check="schema", passed=True), ListingCopy(**raw)
    except (ValidationError, TypeError) as e:
        return Verdict(check="schema", passed=False, reason=str(e)[:200]), None
# --8<-- [end:guard-schema]


# --8<-- [start:guard-claims]
CAPACITY = re.compile(
    r"(?:holds|supports|capacity of)\s+(?:up to\s+)?(\d+)\s*(?:lb|lbs|pounds)", re.I)
SAFETY_TERMS = ("ASTM F1427", "CPSC", "child-safe")


def claim_check(copy: ListingCopy, record: Record) -> Verdict:
    text = f"{copy.title} {copy.description}"
    for n in map(int, CAPACITY.findall(text)):
        if record.weight_capacity_lbs is not None and n > record.weight_capacity_lbs:
            return Verdict(check="claim", passed=False,
                           reason=f"claims {n} lb; record says {record.weight_capacity_lbs}")
    recorded = " ".join(record.safety_claims).lower()
    for term in SAFETY_TERMS:
        if term.lower() in text.lower() and term.lower() not in recorded:
            return Verdict(check="claim", passed=False,
                           reason=f"safety claim {term!r} is not in the record")
    return Verdict(check="claim", passed=True)
# --8<-- [end:guard-claims]


# --8<-- [start:guard-leaks]
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}")
COST = re.compile(r"(?:wholesale|cost|supplier price)\D{0,20}\$\s?\d", re.I)


def leak_check(copy: ListingCopy, record: Record) -> Verdict:
    text = f"{copy.title} {copy.description}"
    for label, pattern in (("email", EMAIL), ("phone", PHONE), ("cost", COST)):
        if pattern.search(text):
            return Verdict(check="leak", passed=False, reason=f"supplier {label} in copy")
    if record.supplier_name.lower() in text.lower():
        return Verdict(check="leak", passed=False, reason="supplier name in copy")
    return Verdict(check="leak", passed=True)
# --8<-- [end:guard-leaks]

"""The typed intermediate document: what code hands to extraction.

Extraction (2.2) never reads raw bytes. It reads this, and every value carries
the place it came from.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# --8<-- [start:ingest-document]
class Anchor(BaseModel):
    """Where a value came from: file plus cell, or file plus page (and table cell)."""
    file: str
    locator: str          # "row 3, col supplier_sku"; "page 1, table 1, row 2, col capacity_lbs"


class Element(BaseModel):
    kind: Literal["field", "text"]
    name: str             # column or label, e.g. "supplier_sku"
    value: str            # untrusted text: data, never instructions
    anchor: Anchor
    read_by: Literal["code", "vision"] = "code"   # which path produced it


class IngestResult(BaseModel):
    """A status and a reason, never a raw exception."""
    status: Literal["ok", "partial", "failed"]
    reason: str | None = None
    pages_ok: int = 0
    elements: list[Element] = []
# --8<-- [end:ingest-document]

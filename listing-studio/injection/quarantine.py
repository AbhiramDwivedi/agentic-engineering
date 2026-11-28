"""Dual LLM: a quarantined reader sees raw supplier text and may only return
a typed record; the privileged side builds the listing from that record."""
from __future__ import annotations

from enum import Enum
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError


# --8<-- [start:injection-record]
class Material(str, Enum):
    mdf = "mdf"
    steel = "steel"
    aluminum = "aluminum"


class Certification(str, Enum):
    bifma = "bifma"
    prop65 = "prop65"


class SpecRecord(BaseModel):
    # extra="forbid": a reader that returns anything but these fields fails.
    model_config = ConfigDict(extra="forbid")
    width_in: int = Field(ge=0, le=200)
    depth_in: int = Field(ge=0, le=200)
    materials: list[Material]
    certifications: list[Certification]
    # Free text is length-capped, shown to a human, and never put in a prompt.
    note: str = Field(max_length=120)
# --8<-- [end:injection-record]


# --8<-- [start:injection-quarantine]
def quarantined_read(raw_sheet: str, reader_fn: Callable[[str], dict]) -> dict:
    """The only place raw supplier text is read. It has no tools; whatever it
    returns is validated, so text cannot cross as anything but typed fields."""
    try:
        return {"ok": True, "record": SpecRecord(**reader_fn(raw_sheet))}
    except (ValidationError, TypeError) as exc:
        return {"ok": False, "error": f"reader output rejected: {exc.__class__.__name__}"}


def privileged_prompt(record: SpecRecord) -> str:
    """Built from enum values and integers only. `note` is left out."""
    return (
        "Write a listing for the Aldsworth desk (NV-ALDSWORTH-DM). "
        f"Width {record.width_in} in, depth {record.depth_in} in. "
        f"Materials: {', '.join(m.value for m in record.materials)}. "
        f"Certifications: {', '.join(c.value for c in record.certifications) or 'none'}."
    )
# --8<-- [end:injection-quarantine]

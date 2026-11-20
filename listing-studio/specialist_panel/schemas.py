"""Schemas for the specialist panel: what each persona returns, and what
the reconciler emits.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:panel-schemas]
class PersonaClaim(BaseModel):
    """One specialist's proposed value for one field, and why. `field` is
    a dotted path into the Listing (e.g. "content_blocks.faq"), never free
    text -- the reconciler matches claims by field, not by prose."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    rationale: str


class PersonaVerdict(BaseModel):
    """One persona's full opinion on this listing: a name from the fixed
    roster, and zero or more typed claims -- never a paragraph."""
    model_config = ConfigDict(extra="forbid")

    persona: str
    claims: list[PersonaClaim]


class AcceptedClaim(BaseModel):
    """A claim the reconciler kept, and which persona it came from."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    source_persona: str


class RejectedClaim(BaseModel):
    """A claim the reconciler dropped, and the reason it lost -- never a
    silent omission."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    source_persona: str
    reason: str


class Conflict(BaseModel):
    """Two or more personas claimed the same field with different values.
    `winner` names the persona whose claim survived and `rule` names what
    decided it -- the reconciler never blends the values into one averaged
    answer."""
    model_config = ConfigDict(extra="forbid")

    field: str
    dissenting_personas: list[str]
    winner: str
    rule: str


class MissingSpecialist(BaseModel):
    """A persona call that errored, timed out, or returned nothing --
    reported as a structured absence, never a silent gap in the panel."""
    model_config = ConfigDict(extra="forbid")

    persona: str
    reason: str


class PanelDecision(BaseModel):
    """The reconciler's typed output: what survived, what didn't and why,
    every conflict with its resolution, every specialist that didn't
    answer, and whether a human needs to see this before it ships."""
    model_config = ConfigDict(extra="forbid")

    accepted: list[AcceptedClaim]
    rejected: list[RejectedClaim]
    conflicts: list[Conflict]
    missing: list[MissingSpecialist]
    escalate: bool
# --8<-- [end:panel-schemas]

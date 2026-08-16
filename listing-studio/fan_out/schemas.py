"""Schemas for step 7's fan-out: the planner's output and the worker-result
contract both halves share.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:fanout-schemas]
class DeliverablePlan(BaseModel):
    """One extra deliverable the planner named for this product, and why."""
    model_config = ConfigDict(extra="forbid")

    deliverable_id: str  # stable key, e.g. "compliance_insert"
    reason: str           # why THIS product needs it


class FanOutPlan(BaseModel):
    """The planner's full output: zero or more extra deliverables, decided
    fresh from the finished listing -- never a fixed list your code already
    knows."""
    model_config = ConfigDict(extra="forbid")

    deliverables: list[DeliverablePlan]


class WorkerResult(BaseModel):
    """One worker's outcome, keyed by the same deliverable_id the planner
    (or the fixed list) named -- success or a structured failure, never a
    raised exception."""
    model_config = ConfigDict(extra="forbid")

    deliverable_id: str
    ok: bool
    content: str | None = None
    error: str | None = None
# --8<-- [end:fanout-schemas]

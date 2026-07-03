"""Schemas for the two-step prompt chain: categorize, then write copy.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:chain-schemas]
class CategoryDecision(BaseModel):
    """Step 3 (categorize) output: where the product belongs in the taxonomy."""
    model_config = ConfigDict(extra="forbid")

    category_path: str  # e.g. "office/desks/standing-desks"
    confidence: float    # 0.0-1.0; the model's stated confidence


class CopyDraft(BaseModel):
    """Step 4 (write copy) output: the drafted listing copy for one product."""
    model_config = ConfigDict(extra="forbid")

    description: str
    bullets: list[str]
# --8<-- [end:chain-schemas]

"""The PricingDecision schema: the typed contract the model must fill.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.

The reasoning field comes first. That ordering is deliberate — it is the
reason-then-format mitigation: the model writes free-text reasoning before it
commits to a number, which guards against the format constraint suppressing
useful thought (see coverage item 7).
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:pricing-schema]
class PricingDecision(BaseModel):
    """The model's complete pricing decision for one Listing Studio product.

    Fields are ordered so the model reasons before it commits to a number.
    reasoning comes first: free-text chain of thought that the model writes
    before it fills in the typed payload. price_cents and the rest follow.
    """
    model_config = ConfigDict(extra="forbid")  # schema-valid shape, no stray keys

    # Reason first: free-text chain of thought before the number is locked in.
    # This is the reason-then-format mitigation — the model thinks in prose
    # before it commits to a constrained integer (see coverage item 7).
    reasoning: str

    # The typed payload.
    price_cents: int           # listed price, e.g. 41900 for $419.00
    currency: str              # ISO-4217 code, e.g. "USD"
    confidence: float          # 0.0–1.0; the model's stated confidence
# --8<-- [end:pricing-schema]

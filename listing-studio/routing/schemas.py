"""Schemas for the merchant-helpdesk router: the route decision itself.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


# --8<-- [start:routing-schemas]
class Category(str, Enum):
    """The closed taxonomy an unlabeled merchant message can land in."""
    BILLING = "billing"
    LISTING_ISSUE = "listing_issue"
    ACCOUNT = "account"
    UNCLEAR = "unclear"


class RouteDecision(BaseModel):
    """Which category owns the message, and how confident the model is."""
    model_config = ConfigDict(extra="forbid")

    category: Category
    confidence: float  # 0.0-1.0; the model's stated confidence
# --8<-- [end:routing-schemas]

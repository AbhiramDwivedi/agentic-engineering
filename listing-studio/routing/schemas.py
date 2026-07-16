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
    """The closed taxonomy an unlabeled merchant message can land in.

    unclear is a member of the taxonomy, not a bolted-on afterthought: the
    classifier names it as the answer whenever nothing else fits, instead of
    a low-confidence guess getting forced into one of the real categories.
    """
    BILLING = "billing"
    LISTING_ISSUE = "listing_issue"
    ACCOUNT = "account"
    UNCLEAR = "unclear"


class RouteDecision(BaseModel):
    """The classifier's output: which category owns this message, and how
    sure it is."""
    model_config = ConfigDict(extra="forbid")

    category: Category
    confidence: float  # 0.0-1.0; the model's stated confidence
# --8<-- [end:routing-schemas]

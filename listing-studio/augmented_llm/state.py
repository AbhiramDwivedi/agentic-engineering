"""Shared listing state for the augmented-LLM chapter examples.

Every node in the Listing Studio pipeline reads the current Listing, does its
work, and hands a more complete Listing to the next node. The TypedDict below
is the minimal slice the price node needs: the product identifier and the
proposed price it will write.
"""
from __future__ import annotations

from typing import Optional, TypedDict

# --8<-- [start:state]
class ListingState(TypedDict):
    """Shared state threaded through every node in the pipeline.

    Each node receives the full state dict, reads what it needs, and returns
    a partial dict with only the keys it changed. LangGraph merges the result
    back into state automatically.
    """
    supplier_sku: str           # the join key from the supplier feed
    title: str                  # merchandised product title
    price_cents: Optional[int]  # the proposed listed price; None until the
                                # price node runs
# --8<-- [end:state]

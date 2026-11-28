"""Typed run state for one Listing run (chapter 5.1).

Extends the idea of ListingState (augmented_llm/state.py, left untouched) with
step status and one list that parallel nodes write. Every key that more than
one writer can touch carries a reducer; the rest overwrite on purpose.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict


# --8<-- [start:state-record]
def merge_status(old: dict, new: dict) -> dict:
    """Reducer: step status accumulates; a later write updates only its own step."""
    return {**old, **new}


class RunState(TypedDict):
    supplier_sku: str                              # overwrite: one writer
    price_cents: int | None                        # overwrite: last write wins
    step_status: Annotated[dict, merge_status]     # merged by step name
    flags: Annotated[list, operator.add]           # appended by parallel nodes
# --8<-- [end:state-record]

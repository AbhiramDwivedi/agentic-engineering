"""The deflated half of step 7: the three standard deliverables, always.

STANDARD_DELIVERABLES is a plain Python list your code wrote before any
listing existed. Nothing here reads the listing to decide what to run;
compare plan.py's propose_deliverables, which cannot answer that question
until a model call returns.
"""
from __future__ import annotations

from typing import Any

from .gather import FanOutSummary, gather


# --8<-- [start:fanout-fixed]
# Every product gets these three, every time. Your code decided this list
# once, when it was written; the model is never asked, and never sees it.
STANDARD_DELIVERABLES: list[str] = ["listing", "announcement_email", "ad_copy"]


def run_fixed_fanout(worker_fn: Any, listing: dict) -> FanOutSummary:
    """Write all three standard deliverables concurrently.

    This calls the exact same gather() the dynamic half calls from plan.py.
    The fan-in cannot tell, and does not need to, that this list came from a
    literal instead of a planner call -- only the source of deliverable_ids
    differs between the two halves of step 7.
    """
    return gather(worker_fn, STANDARD_DELIVERABLES, listing)
# --8<-- [end:fanout-fixed]

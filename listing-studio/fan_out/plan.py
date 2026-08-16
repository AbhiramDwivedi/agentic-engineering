"""The planner call: name the extra deliverables this product needs, then
cap it before any worker runs.

propose_deliverables owns the sequence -- ask, then enforce a hard ceiling --
the seam the provider variants inject (LangGraph / Responses / Anthropic);
see fan_out_langgraph.py, fan_out_responses.py, and fan_out_example.py.
Compare fixed.py: that list is a literal your code wrote once; this
function's list does not exist until planner_fn returns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .schemas import DeliverablePlan, FanOutPlan


# --8<-- [start:fanout-plan]
# The bounded-consumption cap (OWASP LLM10 Unbounded Consumption). Anthropic's
# own postmortem names "spawning 50 subagents for simple queries" as a
# failure mode it had to guardrail against explicitly -- this is that
# guardrail, sized for a launch step that names at most a handful of real
# deliverable types.
MAX_EXTRA_DELIVERABLES = 5


@dataclass
class PlanResult:
    """The capped plan: what actually runs, and whether the model asked for
    more than the cap allows."""
    deliverables: list[DeliverablePlan]
    truncated: bool


def propose_deliverables(planner_fn: Any, listing: dict) -> PlanResult:
    """Ask the model which extra deliverables this listing needs, then
    enforce the cap before any worker runs.

    planner_fn reads the finished listing and returns a FanOutPlan naming
    zero or more extra deliverables -- the count does not exist anywhere in
    this file until planner_fn returns it. A plan naming more than
    MAX_EXTRA_DELIVERABLES is not run in full: the excess is dropped, never
    silently spawned, and the caller gets truncated=True so it can log or
    alert instead of discovering the cap only in a cost report.
    """
    plan: FanOutPlan = planner_fn(listing)
    truncated = len(plan.deliverables) > MAX_EXTRA_DELIVERABLES
    return PlanResult(
        deliverables=plan.deliverables[:MAX_EXTRA_DELIVERABLES],
        truncated=truncated,
    )
# --8<-- [end:fanout-plan]

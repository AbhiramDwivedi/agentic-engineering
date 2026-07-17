"""The LLM-routing core: classify the unlabeled input, then hand off.

route_message owns the sequence -- classify, then either call the matched
category's handler or escalate -- the seam the provider variants inject
(LangGraph / Responses / Anthropic); see router_langgraph.py,
router_responses.py, and router_anthropic.py. Compare dispatch.py: that
table's decision is made once, when EVENT_HANDLERS is written; this
function's decision is made fresh on every call, by classify_fn.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .schemas import Category, RouteDecision


# --8<-- [start:routing-route]
@dataclass
class RouteResult:
    """The routing outcome: which category handled it, and whether it
    escalated instead of running a handler."""
    category: Category
    response: str
    escalated: bool


def route_message(
    classify_fn: Any,  # callable(message: str) -> RouteDecision
    handlers: dict[Category, Callable[[str], str]],
    message: str,
    *,
    confidence_floor: float = 0.6,
) -> RouteResult:
    """Classify message, then hand off to its category's handler.

    A model call decides the category fresh on every request -- the
    genuinely-new half of this chapter, in contrast to dispatch()'s static
    lookup. `unclear` and any confidence below confidence_floor both land on
    the same escalation path: the message never gets forced into a category
    it doesn't confidently belong to, and low confidence is a structured,
    expected outcome here, not an exception.
    """
    decision = classify_fn(message)

    if decision.category == Category.UNCLEAR or decision.confidence < confidence_floor:
        return RouteResult(
            category=Category.UNCLEAR,
            response=(
                f"could not route with confidence ({decision.confidence:.2f}); "
                "escalated to a human"
            ),
            escalated=True,
        )

    return RouteResult(
        category=decision.category,
        response=handlers[decision.category](message),
        escalated=False,
    )
# --8<-- [end:routing-route]

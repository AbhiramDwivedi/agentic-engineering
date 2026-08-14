"""The LLM-routing core: classify the unlabeled input, then hand off.

classify_fn is the seam the provider variants inject (LangGraph / Responses
/ Anthropic); see router_langgraph.py, router_responses.py, and
router_anthropic.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .schemas import Category, RouteDecision


# --8<-- [start:routing-route]
@dataclass
class RouteResult:
    """The routing outcome: category, response, and whether it escalated."""
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
    """Classify message, then hand off to its category's handler."""
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

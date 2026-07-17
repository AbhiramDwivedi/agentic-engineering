"""LLM routing against the OpenAI Responses API: the merchant helpdesk.

Illustration, not run in CI: needs an API key and a network call. The
default pane is router_langgraph.py; this is the OpenAI Responses variant,
and it reuses the tested route_message from route.py -- only the
classification call shape changes per provider, not the routing decision
itself.
"""
from __future__ import annotations

from openai import OpenAI

from .route import route_message
from .schemas import Category, RouteDecision

client = OpenAI()


# --8<-- [start:routing-responses]
def classify_fn(message: str) -> RouteDecision:
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": (
                    "Classify this merchant helpdesk message into billing, "
                    f"listing_issue, account, or unclear: {message}"
                ),
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "RouteDecision",
                "schema": RouteDecision.model_json_schema(),
                "strict": True,
            }
        },
    )
    return RouteDecision.model_validate_json(response.output_text)


HANDLERS = {
    Category.BILLING: lambda msg: f"[billing] {msg}",
    Category.LISTING_ISSUE: lambda msg: f"[listing_issue] {msg}",
    Category.ACCOUNT: lambda msg: f"[account] {msg}",
}

result = route_message(
    classify_fn,
    HANDLERS,
    "Why was I charged twice for my Stockwell subscription this month?",
)
print(result.response)
# --8<-- [end:routing-responses]

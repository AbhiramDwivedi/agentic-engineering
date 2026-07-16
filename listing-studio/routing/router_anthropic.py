"""LLM routing against the Anthropic Messages API: the merchant helpdesk.

Illustration, not run in CI: needs an API key and a network call. The
default pane is router_langgraph.py; this is the Anthropic Messages variant,
and it reuses the tested route_message from route.py -- only the
classification call shape changes per provider, not the routing decision
itself.
"""
from __future__ import annotations

import anthropic

from .route import route_message
from .schemas import Category, RouteDecision

client = anthropic.Anthropic()

_ROUTE_TOOL = {
    "name": "produce_route_decision",
    "description": "Classify a merchant helpdesk message into the routing taxonomy.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["billing", "listing_issue", "account", "unclear"],
            },
            "confidence": {"type": "number"},
        },
        "required": ["category", "confidence"],
        "additionalProperties": False,
    },
}


# --8<-- [start:routing-anthropic]
def classify_fn(message: str) -> RouteDecision:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_ROUTE_TOOL],
        tool_choice={"type": "tool", "name": "produce_route_decision"},
        messages=[
            {
                "role": "user",
                "content": f"Classify this merchant helpdesk message: {message}",
            }
        ],
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return RouteDecision.model_validate(tool_block.input)


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
# --8<-- [end:routing-anthropic]

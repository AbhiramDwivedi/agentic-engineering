"""Structured output using the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is structured_output_langgraph.py; this is the Anthropic Messages variant.

Anthropic structured outputs use tool-forcing: define the response schema as a
tool's input_schema, then set tool_choice to force the model to call exactly
that tool. The same constrained-decoding machinery as tool use, aimed at the
response schema instead of a real function.

Reference: platform.anthropic.com/docs/en/build-with-claude/structured-outputs
"""
from __future__ import annotations

import json

import anthropic

from .schema import PricingDecision

client = anthropic.Anthropic()

# The PricingDecision schema expressed as an Anthropic tool. tool_choice forces
# the model to call this tool — it cannot answer in free prose.
_PRICING_DECISION_TOOL = {
    "name": "produce_pricing_decision",
    "description": (
        "Produce a structured pricing decision for a Listing Studio product. "
        "Reason through the MAP floor and margin rules, then fill the schema."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reasoning": {
                "type": "string",
                "description": "Chain-of-thought: reasoning about MAP, margin, and market before committing to a price.",
            },
            "price_cents": {
                "type": "integer",
                "description": "The listed price in cents, e.g. 41900 for $419.00.",
            },
            "currency": {
                "type": "string",
                "description": "ISO-4217 currency code, e.g. 'USD'.",
            },
            "confidence": {
                "type": "number",
                "description": "Model's stated confidence in this decision, 0.0 to 1.0.",
            },
        },
        "required": ["reasoning", "price_cents", "currency", "confidence"],
        "additionalProperties": False,
    },
}


# --8<-- [start:pricing-call-anthropic]
# Anthropic Messages API: tool-forcing for structured output.
# Define the response schema as a tool's input_schema; tool_choice forces the
# model to call it. Same constrained-decoding machinery as tool use — the model
# fills the schema rather than answering in free prose.
reply = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[_PRICING_DECISION_TOOL],
    tool_choice={"type": "tool", "name": "produce_pricing_decision"},
    messages=[
        {
            "role": "user",
            "content": (
                "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
                "(SKU NV-ALDSWORTH-DM, MAP floor $399.00, landed cost $280.00). "
                "Reason through the MAP and margin rules, then produce a PricingDecision."
            ),
        }
    ],
)

# Guard: check for refusal or truncation before parsing (Gotcha — item 5).
if reply.stop_reason not in ("tool_use", "end_turn"):
    raise RuntimeError(
        f"unexpected stop_reason {reply.stop_reason!r}; "
        "may be a refusal or truncation — inspect reply.content"
    )

tool_block = next(b for b in reply.content if b.type == "tool_use")
decision = PricingDecision.model_validate(tool_block.input)
print(decision.price_cents)   # e.g. 41900
# --8<-- [end:pricing-call-anthropic]

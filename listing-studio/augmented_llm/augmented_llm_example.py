"""The augmented-LLM unit using the Anthropic Messages API.

Same illustration caveats as the LangGraph and Responses variants: this file
is compile-checked in CI but not executed (needs an API key and a network call).
The tool's pure logic lives in floor_price.py and is unit-tested offline.
The default pane is augmented_llm_langgraph.py; this is the Anthropic Messages
variant.
"""
from __future__ import annotations

import json
from typing import Any

import anthropic

from .floor_price import FLOOR_PRICE_TOOL_ANTHROPIC, lookup_floor_price
from .state import ListingState


# --8<-- [start:unit_anthropic]
# The same unit, Anthropic Messages shape: input_schema instead of parameters,
# no top-level type field. The model reads this description and decides when
# to call the tool.
FLOOR_PRICE_TOOL = {
    "name": "lookup_floor_price",
    "description": (
        "Look up the supplier's minimum advertised price (MAP) floor for a "
        "product. Call this before quoting a price."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"supplier_sku": {"type": "string"}},
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}
# --8<-- [end:unit_anthropic]


# --8<-- [start:node_anthropic]
def price_node(state: ListingState, _client: Any = None) -> dict:
    """One graph node: reads state, runs the augmented-LLM unit, writes state.

    Anthropic Messages API variant. The _client kwarg is injectable for offline
    testing without an API key.
    """
    client = _client or anthropic.Anthropic()
    messages = [
        {
            "role": "user",
            "content": (
                f"Set a listed price for {state['title']} "
                f"(SKU {state['supplier_sku']}). "
                "Use lookup_floor_price to check the MAP floor "
                "and price at least 5 % above it. "
                "Reply with only the integer price in cents."
            ),
        }
    ]

    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=64,
        tools=[FLOOR_PRICE_TOOL],
        messages=messages,
    )

    # Run the tool loop; cap prevents infinite spin if the model gets stuck.
    MAX_STEPS = 5
    steps = 0
    while reply.stop_reason == "tool_use":
        steps += 1
        if steps > MAX_STEPS:
            raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
        messages.append({"role": "assistant", "content": reply.content})
        results = []
        for block in reply.content:
            if block.type == "tool_use":
                output = lookup_floor_price(**block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(output),
                    }
                )
        messages.append({"role": "user", "content": results})
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=64,
            tools=[FLOOR_PRICE_TOOL],
            messages=messages,
        )

    price_cents = int(reply.content[0].text.strip())
    return {"price_cents": price_cents}
# --8<-- [end:node_anthropic]

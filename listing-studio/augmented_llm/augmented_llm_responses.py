"""The augmented-LLM unit using the OpenAI Responses API.

Same illustration caveats as the LangGraph variant: this file is
compile-checked in CI but not executed (needs an API key and a network call).
The tool's pure logic lives in floor_price.py and is unit-tested offline.
The default pane is augmented_llm_langgraph.py; this is the OpenAI Responses
variant.
"""
from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .floor_price import FLOOR_PRICE_TOOL_RESPONSES, lookup_floor_price
from .state import ListingState


# --8<-- [start:unit_responses]
# The same unit, OpenAI Responses shape: the tool is a JSON schema object you
# pass to the API; the model reads the description and decides when to call it.
FLOOR_PRICE_TOOL = {
    "type": "function",
    "name": "lookup_floor_price",
    "description": (
        "Look up the supplier's minimum advertised price (MAP) floor for a "
        "product. Call this before quoting a price."
    ),
    "parameters": {
        "type": "object",
        "properties": {"supplier_sku": {"type": "string"}},
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}
# --8<-- [end:unit_responses]


# --8<-- [start:node_responses]
def price_node(state: ListingState, _client: Any = None) -> dict:
    """One graph node: reads state, runs the augmented-LLM unit, writes state.

    OpenAI Responses API variant. The _client kwarg is injectable for offline
    testing without an API key.
    """
    client = _client or OpenAI()
    input_list = [
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

    response = client.responses.create(
        model="gpt-5.5",
        input=input_list,
        tools=[FLOOR_PRICE_TOOL],
    )

    # Run the tool loop; cap prevents infinite spin if the model gets stuck.
    MAX_STEPS = 5
    steps = 0
    while any(item.type == "function_call" for item in response.output):
        steps += 1
        if steps > MAX_STEPS:
            raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
        input_list += response.output
        for item in response.output:
            if item.type == "function_call":
                result = lookup_floor_price(**json.loads(item.arguments))
                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )
        response = client.responses.create(
            model="gpt-5.5",
            input=input_list,
            tools=[FLOOR_PRICE_TOOL],
        )

    price_cents = int(response.output_text.strip())
    return {"price_cents": price_cents}
# --8<-- [end:node_responses]

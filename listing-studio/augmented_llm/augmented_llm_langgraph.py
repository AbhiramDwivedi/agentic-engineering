"""The augmented-LLM unit as a LangGraph graph node (the default the chapter shows).

Illustration of the atom every later pattern builds on: a model call wrapped
with one tool, reading from and writing to a shared state object.  The
tool's pure logic lives in floor_price.py and is unit-tested offline.  The
model call (create_agent / agent.invoke) needs an API key; the test suite
compile-checks this file but does not execute it.  Raw-SDK variants:
augmented_llm_responses.py (OpenAI Responses) and augmented_llm_example.py
(Anthropic Messages).
"""
from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool

from .state import ListingState


# --8<-- [start:unit]
# The augmented-LLM unit: one model paired with one tool.
# The tool is a decorator over your plain function — LangGraph reads the
# description from the type hints and docstring; underneath it is a JSON schema.
@tool(parse_docstring=True)
def lookup_floor_price(supplier_sku: str) -> dict:
    """Look up the supplier's minimum advertised price (MAP) floor.

    Args:
        supplier_sku: the product SKU to look up.
    """
    return {"floor_cents": 39900}  # $399.00 MAP for the Aldsworth desk


# One model, one tool, one contract — the atom.
agent = create_agent("openai:gpt-5.5", tools=[lookup_floor_price])
# --8<-- [end:unit]


# --8<-- [start:node]
def price_node(state: ListingState, _agent: Any = None) -> dict:
    """One graph node: reads state, runs the augmented-LLM unit, writes state.

    Takes supplier_sku and title from the shared listing state; returns a
    partial dict with price_cents so LangGraph can merge it back.
    The _agent kwarg is the seam used in tests to inject a fake (no API key).
    """
    _agent = _agent or agent
    result = _agent.invoke(
        {
            "messages": [
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
        }
    )
    price_cents: int = result["price_cents"]
    return {"price_cents": price_cents}
# --8<-- [end:node]

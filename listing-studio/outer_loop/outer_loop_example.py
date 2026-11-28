"""Outer loop against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. Reuses the
tested run_outer_loop from loop.py; only the attempt function changes.
"""
from __future__ import annotations

import anthropic

from .loop import run_outer_loop
from .schemas import PriceCandidate
from .verifier import PriceRules

client = anthropic.Anthropic()

_PRICE_TOOL = {
    "name": "propose_price",
    "description": "Propose a price for a Listing Studio product.",
    "input_schema": {
        "type": "object",
        "properties": {"price_cents": {"type": "integer"}},
        "required": ["price_cents"],
        "additionalProperties": False,
    },
}


# --8<-- [start:outer-anthropic]
def attempt(failures: list[str]) -> int:
    prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
    if failures:
        prompt += " Earlier attempts were rejected: " + " | ".join(failures)
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        tools=[_PRICE_TOOL],
        tool_choice={"type": "tool", "name": "propose_price"},
        messages=[{"role": "user", "content": prompt}],
    )
    block = next(b for b in reply.content if b.type == "tool_use")
    return PriceCandidate.model_validate(block.input).price_cents


rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
outcome = run_outer_loop(attempt, rules, max_attempts=3)
print(outcome.status, outcome.price_cents)
# --8<-- [end:outer-anthropic]

"""Outer loop against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. Reuses the
tested run_outer_loop from loop.py; only the attempt function changes.
"""
from __future__ import annotations

from openai import OpenAI

from .loop import run_outer_loop
from .schemas import PriceCandidate
from .verifier import PriceRules

client = OpenAI()


# --8<-- [start:outer-responses]
def attempt(failures: list[str]) -> int:
    prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
    if failures:
        prompt += " Earlier attempts were rejected: " + " | ".join(failures)
    response = client.responses.create(
        model="gpt-6.2-sol",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "PriceCandidate",
                "schema": PriceCandidate.model_json_schema(),
                "strict": True,
            }
        },
    )
    return PriceCandidate.model_validate_json(response.output_text).price_cents


rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
outcome = run_outer_loop(attempt, rules, max_attempts=3)
print(outcome.status, outcome.price_cents)
# --8<-- [end:outer-responses]

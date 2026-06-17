"""Structured output using the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is structured_output_langgraph.py; this is the OpenAI Responses variant.

OpenAI strict json_schema mode: set strict=True and pass the Pydantic model's
JSON schema. The decoder cannot emit a token that violates the schema — this is
the constrained-decoding tier, more reliable than JSON mode alone.
"""
from __future__ import annotations

import json

from openai import OpenAI

from .schema import PricingDecision

client = OpenAI()


# --8<-- [start:pricing-call-openai]
# OpenAI Responses API: strict json_schema mode.
# response_format carries the JSON schema; strict=True engages the
# grammar-constrained decoder so the output is guaranteed to match the shape.
response = client.responses.create(
    model="gpt-5.5",
    input=[
        {
            "role": "user",
            "content": (
                "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
                "(SKU NV-ALDSWORTH-DM, MAP floor $399.00, landed cost $280.00). "
                "Reason through the MAP and margin rules, then produce a PricingDecision."
            ),
        }
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "PricingDecision",
            "schema": PricingDecision.model_json_schema(),
            "strict": True,
        }
    },
)

# Guard: check for a refusal or truncation before parsing (Gotcha — item 5).
if response.status == "incomplete":
    raise RuntimeError(
        f"response incomplete (finish reason: {response.incomplete_details}); "
        "cannot parse a truncated structured-output response"
    )

decision = PricingDecision.model_validate_json(response.output_text)
print(decision.price_cents)   # e.g. 41900
# --8<-- [end:pricing-call-openai]

"""Prompt chaining against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. The
default pane is prompt_chaining_langgraph.py; this is the OpenAI Responses
variant, and it reuses the tested run_chain from chain.py -- only the call
shape changes per provider, not the gate, the retry, or the abort.
"""
from __future__ import annotations

from openai import OpenAI

from .chain import run_chain
from .schemas import CategoryDecision, CopyDraft

client = OpenAI()


# --8<-- [start:chain-responses]
def categorize_fn(messages: list[dict]) -> CategoryDecision:
    response = client.responses.create(
        model="gpt-5.5",
        input=messages,
        text={
            "format": {
                "type": "json_schema",
                "name": "CategoryDecision",
                "schema": CategoryDecision.model_json_schema(),
                "strict": True,
            }
        },
    )
    return CategoryDecision.model_validate_json(response.output_text)


def write_copy_fn(messages: list[dict]) -> CopyDraft:
    response = client.responses.create(
        model="gpt-5.5",
        input=messages,
        text={
            "format": {
                "type": "json_schema",
                "name": "CopyDraft",
                "schema": CopyDraft.model_json_schema(),
                "strict": True,
            }
        },
    )
    return CopyDraft.model_validate_json(response.output_text)


copy = run_chain(
    categorize_fn,
    write_copy_fn,
    supplier_sku="NV-ALDSWORTH-DM",
    title="Aldsworth Dual-Motor Sit-Stand Desk",
)
print(copy.description)
# --8<-- [end:chain-responses]

"""Prompt chaining against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. The
default pane is prompt_chaining_langgraph.py; this is the Anthropic
Messages variant, and it reuses the tested run_chain from chain.py -- only
the call shape changes per provider, not the gate, the retry, or the abort.
"""
from __future__ import annotations

import anthropic

from .chain import run_chain
from .schemas import CategoryDecision, CopyDraft

client = anthropic.Anthropic()

_CATEGORY_TOOL = {
    "name": "produce_category_decision",
    "description": "Place a Listing Studio product in the catalog taxonomy.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category_path": {"type": "string"},
            "confidence": {"type": "number"},
        },
        "required": ["category_path", "confidence"],
        "additionalProperties": False,
    },
}

_COPY_TOOL = {
    "name": "produce_copy_draft",
    "description": "Write the listing copy for a Listing Studio product.",
    "input_schema": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "bullets": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["description", "bullets"],
        "additionalProperties": False,
    },
}


# --8<-- [start:chain-anthropic]
def categorize_fn(messages: list[dict]) -> CategoryDecision:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_CATEGORY_TOOL],
        tool_choice={"type": "tool", "name": "produce_category_decision"},
        messages=messages,
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return CategoryDecision.model_validate(tool_block.input)


def write_copy_fn(messages: list[dict]) -> CopyDraft:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_COPY_TOOL],
        tool_choice={"type": "tool", "name": "produce_copy_draft"},
        messages=messages,
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return CopyDraft.model_validate(tool_block.input)


copy = run_chain(
    categorize_fn,
    write_copy_fn,
    supplier_sku="NV-ALDSWORTH-DM",
    title="Aldsworth Dual-Motor Sit-Stand Desk",
)
print(copy.description)
# --8<-- [end:chain-anthropic]

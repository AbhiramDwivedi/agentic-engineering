"""Retrieval as a tool with the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

import anthropic

from .tool import search_docs

client = anthropic.Anthropic()


# --8<-- [start:retrieval-anthropic]
SEARCH_TOOL = {
    "name": "search_docs",
    "description": "Search the merchant helpdesk policy docs.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}


def answer(question: str, max_searches: int = 3) -> str:
    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=1024, tools=[SEARCH_TOOL], messages=messages
    )
    for _ in range(max_searches):
        if response.stop_reason != "tool_use":
            break  # the model answered without (another) search
        results = [
            {"type": "tool_result", "tool_use_id": block.id,
             "content": search_docs(**block.input).model_dump_json()}
            for block in response.content if block.type == "tool_use"  # one result per call
        ]
        messages += [{"role": "assistant", "content": response.content},
                     {"role": "user", "content": results}]
        response = client.messages.create(
            model="claude-sonnet-5-5", max_tokens=1024, tools=[SEARCH_TOOL], messages=messages
        )
    return "".join(block.text for block in response.content if block.type == "text")
# --8<-- [end:retrieval-anthropic]

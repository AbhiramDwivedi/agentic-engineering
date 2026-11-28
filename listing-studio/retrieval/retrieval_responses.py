"""Retrieval as a tool with the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

import json

from openai import OpenAI

from .tool import search_docs

client = OpenAI()


# --8<-- [start:retrieval-responses]
SEARCH_TOOL = {
    "type": "function",
    "name": "search_docs",
    "description": "Search the merchant helpdesk policy docs.",
    "parameters": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,
}


def answer(question: str, max_searches: int = 3) -> str:
    input_items = [{"role": "user", "content": question}]
    response = client.responses.create(model="gpt-6.2-sol", input=input_items, tools=[SEARCH_TOOL])
    for _ in range(max_searches):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            break  # the model answered without (another) search
        input_items += response.output  # keep every item, reasoning included
        for call in calls:
            result = search_docs(**json.loads(call.arguments))
            input_items.append({"type": "function_call_output", "call_id": call.call_id,
                                "output": result.model_dump_json()})
        response = client.responses.create(model="gpt-6.2-sol", input=input_items, tools=[SEARCH_TOOL])
    return response.output_text
# --8<-- [end:retrieval-responses]

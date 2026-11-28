"""OpenAI Responses: thread state is not memory, so you wire an external store.

Illustration, not run in CI: needs an API key and a network call.
The default pane is memory_langgraph.py; this is the OpenAI Responses variant.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from openai import OpenAI

from memory.store import MemoryStore

client = OpenAI()
store = MemoryStore()
REMEMBER = {
    "type": "function", "name": "remember",
    "description": "Save one short fact about the shopper for later visits.",
    "parameters": {
        "type": "object",
        "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
        "required": ["key", "value"], "additionalProperties": False,
    },
}


# --8<-- [start:memory-responses]
response = client.responses.create(
    model="gpt-6.2-sol",
    tools=[REMEMBER],
    input="My garage is 200 sq ft. Remember that for next time.",
)
for item in response.output:
    if item.type == "function_call" and item.name == "remember":
        args = json.loads(item.arguments)
        result = store.write(                  # your store polices the write
            "shopper-123", args["key"], args["value"],
            author="model", source="chat", now=datetime.now(timezone.utc),
        )
        # `result` (ok, or a structured error) goes back as a function_call_output
        # so the model can recover from a rejected write.
# --8<-- [end:memory-responses]

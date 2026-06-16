"""The real tool-use loop against the Anthropic Messages API.

This is an illustration, not part of the test suite: it needs an API key and a
network call. The tool's own logic lives in tools.py and is unit-tested; this
file shows how the model and the tool talk to each other. The same shape applies
to other vendors' tool-calling APIs.
"""
import json

import anthropic

from .tools import PRICE_CHECK_TOOL, check_price

client = anthropic.Anthropic()

# --8<-- [start:flow]
messages = [
    {
        "role": "user",
        "content": "Set a price for the Aldsworth sit-stand desk, SKU NV-ALDSWORTH-DM.",
    }
]

# Offer the tool. The model decides whether to use it.
reply = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[PRICE_CHECK_TOOL],
    messages=messages,
)

# While the model asks for the tool, run it and hand back the result.
# Cap the loop so a stuck model fails loudly instead of spinning (Gotcha 5).
MAX_STEPS = 5
steps = 0
while reply.stop_reason == "tool_use":
    steps += 1
    if steps > MAX_STEPS:
        raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
    messages.append({"role": "assistant", "content": reply.content})
    results = []
    for block in reply.content:
        if block.type == "tool_use":
            output = check_price(**block.input)  # your code runs, not the model
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                }
            )
    messages.append({"role": "user", "content": results})
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[PRICE_CHECK_TOOL],
        messages=messages,
    )

# No more tool calls: the model has settled on an answer.
print(reply.content[0].text)
# --8<-- [end:flow]

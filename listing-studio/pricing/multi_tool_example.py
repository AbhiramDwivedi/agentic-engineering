"""The multi-tool loop against the Anthropic Messages API.

Same illustration caveats as tool_use_example.py: needs an API key and a
network call, so it is compile-checked but not executed in CI. The structural
difference from the single-tool loop is small and lives in the `many_anthropic`
region: a registry, and dispatch by the name the model chose. The default loop
uses the OpenAI Responses API (multi_tool_responses.py); this is the Anthropic
variant.
"""
import json

import anthropic

from .tools import (
    COMPETITOR_PRICE_TOOL_ANTHROPIC,
    PRICE_CHECK_TOOL_ANTHROPIC,
    check_price,
    get_competitor_prices,
)

client = anthropic.Anthropic()

# --8<-- [start:many_anthropic]
# Several tools: the model picks by description; your code dispatches by name.
TOOLS = {
    "check_price": check_price,
    "get_competitor_prices": get_competitor_prices,
}


def run_tools(reply) -> list:
    """One tool_result per tool_use block, matched by id."""
    results = []
    for block in reply.content:
        if block.type == "tool_use":
            output = TOOLS[block.name](**block.input)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                }
            )
    return results
# --8<-- [end:many_anthropic]

messages = [
    {
        "role": "user",
        "content": (
            "Price the Aldsworth sit-stand desk, SKU NV-ALDSWORTH-DM, "
            "competitively against the market."
        ),
    }
]

reply = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[PRICE_CHECK_TOOL_ANTHROPIC, COMPETITOR_PRICE_TOOL_ANTHROPIC],
    messages=messages,
)

steps = 0
while reply.stop_reason == "tool_use":
    steps += 1
    if steps > 5:
        raise RuntimeError("tool loop hit the step cap; the model may be stuck")
    messages.append({"role": "assistant", "content": reply.content})
    messages.append({"role": "user", "content": run_tools(reply)})
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[PRICE_CHECK_TOOL_ANTHROPIC, COMPETITOR_PRICE_TOOL_ANTHROPIC],
        messages=messages,
    )

print(reply.content[0].text)

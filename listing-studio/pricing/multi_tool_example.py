"""The tool-use loop with more than one tool on offer.

Same illustration caveats as tool_use_example.py: needs an API key and a
network call, so it is compile-checked but not executed in CI. The structural
difference from the single-tool loop is small and lives in the `many` region:
a registry, and dispatch by the name the model chose.
"""
import anthropic

from .tools import (
    COMPETITOR_PRICE_TOOL,
    PRICE_CHECK_TOOL,
    check_price,
    get_competitor_prices,
)

client = anthropic.Anthropic()

# --8<-- [start:many]
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
                    "content": str(output),
                }
            )
    return results
# --8<-- [end:many]

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
    tools=[PRICE_CHECK_TOOL, COMPETITOR_PRICE_TOOL],
    messages=messages,
)

while reply.stop_reason == "tool_use":
    messages.append({"role": "assistant", "content": reply.content})
    messages.append({"role": "user", "content": run_tools(reply)})
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[PRICE_CHECK_TOOL, COMPETITOR_PRICE_TOOL],
        messages=messages,
    )

print(reply.content[0].text)

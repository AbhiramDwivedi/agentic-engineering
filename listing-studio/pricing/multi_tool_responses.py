"""The multi-tool loop against the OpenAI Responses API.

Same illustration caveats as tool_use_responses.py: needs an API key and a
network call, so it is compile-checked but not executed in CI. The structural
difference from the single-tool loop is small and lives in the `many` region:
a registry, and dispatch by the name the model chose.
"""
import json

from openai import OpenAI

from .tools import (
    COMPETITOR_PRICE_TOOL,
    PRICE_CHECK_TOOL,
    check_price,
    get_competitor_prices,
)

client = OpenAI()

# --8<-- [start:many_responses]
# Several tools: the model picks by description; your code dispatches by name.
TOOLS = {
    "check_price": check_price,
    "get_competitor_prices": get_competitor_prices,
}


def run_tools(response) -> list:
    """One function_call_output per function_call item, matched by call_id."""
    results = []
    for item in response.output:
        if item.type == "function_call":
            output = TOOLS[item.name](**json.loads(item.arguments))
            results.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(output),
                }
            )
    return results
# --8<-- [end:many_responses]

input_list = [
    {
        "role": "user",
        "content": (
            "Price the Aldsworth sit-stand desk, SKU NV-ALDSWORTH-DM, "
            "competitively against the market."
        ),
    }
]

response = client.responses.create(
    model="gpt-5.5",
    input=input_list,
    tools=[PRICE_CHECK_TOOL, COMPETITOR_PRICE_TOOL],
)

steps = 0
while any(item.type == "function_call" for item in response.output):
    steps += 1
    if steps > 5:
        raise RuntimeError("tool loop hit the step cap; the model may be stuck")
    input_list += response.output
    input_list += run_tools(response)
    response = client.responses.create(
        model="gpt-5.5",
        input=input_list,
        tools=[PRICE_CHECK_TOOL, COMPETITOR_PRICE_TOOL],
    )

print(response.output_text)

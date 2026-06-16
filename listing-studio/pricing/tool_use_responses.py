"""The tool-use loop against the OpenAI Responses API.

This is an illustration, not part of the test suite: it needs an API key and a
network call. The tool's own logic lives in tools.py and is unit-tested; this
file shows how the model and the tool talk to each other using the Responses API.
"""
import json

from openai import OpenAI

from .tools import PRICE_CHECK_TOOL, check_price

client = OpenAI()

# --8<-- [start:flow_responses]
input_list = [
    {
        "role": "user",
        "content": "Set a price for the Aldsworth sit-stand desk, SKU NV-ALDSWORTH-DM.",
    }
]

# Offer the tool. The model decides whether to use it.
response = client.responses.create(
    model="gpt-5.5",
    input=input_list,
    tools=[PRICE_CHECK_TOOL],
)

# While the model asks for the tool, run it and hand back the result.
# Cap the loop so a stuck model fails loudly instead of spinning (Gotcha 5).
MAX_STEPS = 5
steps = 0
while any(item.type == "function_call" for item in response.output):
    steps += 1
    if steps > MAX_STEPS:
        raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
    input_list += response.output
    for item in response.output:
        if item.type == "function_call":
            output = check_price(**json.loads(item.arguments))  # your code runs, not the model
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(output),
                }
            )
    response = client.responses.create(
        model="gpt-5.5",
        input=input_list,
        tools=[PRICE_CHECK_TOOL],
    )

# No more function calls: the model has settled on an answer.
print(response.output_text)
# --8<-- [end:flow_responses]

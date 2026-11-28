"""The same pause with the OpenAI Responses API as a plain loop (the 2.4 seam,
grown into a durable request): when the model calls set_price and the gate says
"ask", the loop does not run the tool. It saves an ApprovalRequest and stops;
a later call resumes it and returns the outcome as the function_call_output.

Illustration, not run in CI: needs the openai package and an API key. The model
ID is the current default; it reuses the tested ApprovalStore and reprice_step.
"""
from __future__ import annotations

import json

from openai import OpenAI

from .pause_resume import ApprovalStore, Effects, reprice_step

client = OpenAI()
MODEL = "gpt-6.2-sol"


# --8<-- [start:hitl-responses]
def run_until_pause(store: ApprovalStore, tools: list, user_text: str, requester: str):
    fx = Effects()
    response = client.responses.create(model=MODEL, input=user_text, tools=tools)
    for item in response.output:
        if item.type != "function_call" or item.name != "set_price":
            continue
        args = json.loads(item.arguments)
        outcome = reprice_step(store, item.call_id, requester, args, fx)
        if outcome.status == "paused":
            return {"paused": item.call_id, "response_id": response.id}  # return to the caller
        # Otherwise hand the outcome back; a rejection reason reaches the model here.
        return client.responses.create(
            model=MODEL, previous_response_id=response.id, tools=tools,
            input=[{"type": "function_call_output", "call_id": item.call_id,
                    "output": json.dumps(outcome.as_tool_result())}])
# --8<-- [end:hitl-responses]

"""Observer step against the OpenAI Responses API.

Illustration, compile-checked only: needs an API key and a network call.
Reuses the tested observed_step from events.py.
"""
from __future__ import annotations

from openai import OpenAI

from .events import Sink, StepResult, observed_step

client = OpenAI()


# --8<-- [start:observer-responses]
def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
    def step() -> StepResult:
        response = client.responses.create(
            model="gpt-6.2-sol",
            input=f"Write a listing description for {sku}.",
        )
        # An incomplete or refused response is still a normal return.
        details = response.incomplete_details
        refused = any(
            part.type == "refusal"
            for item in response.output
            if item.type == "message"
            for part in item.content
        )
        if refused or (details and details.reason == "content_filter"):
            reason = "refusal"
        elif details:  # max_output_tokens, or any other early stop
            reason = "max_tokens"
        else:
            reason = "end_turn"
        return StepResult(text=response.output_text, stop_reason=reason)

    return observed_step(sinks, run_id, "describe", step)
# --8<-- [end:observer-responses]

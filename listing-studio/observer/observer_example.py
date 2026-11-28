"""Observer step against the Anthropic Messages API.

Illustration, compile-checked only: needs an API key and a network call.
Reuses the tested observed_step from events.py.
"""
from __future__ import annotations

import anthropic

from .events import Sink, StepResult, observed_step

client = anthropic.Anthropic()


# --8<-- [start:observer-anthropic]
def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
    def step() -> StepResult:
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"Write a listing description for {sku}."}
            ],
        )
        # A refusal or truncation is an HTTP 200; stop_reason is the only tell.
        text = "".join(b.text for b in reply.content if b.type == "text")
        reason = reply.stop_reason or "end_turn"
        if reason == "model_context_window_exceeded":
            reason = "max_tokens"  # Anthropic's docs: treat it as truncated
        return StepResult(text=text, stop_reason=reason)

    return observed_step(sinks, run_id, "describe", step)
# --8<-- [end:observer-anthropic]

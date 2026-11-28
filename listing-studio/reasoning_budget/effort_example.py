"""One call at a chosen effort level, Anthropic Messages flavour.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

from .sweep import Case, ModelReply

# --8<-- [start:effort-anthropic]
import anthropic

client = anthropic.Anthropic()


def model_fn(case: Case, level: str, cap: int) -> ModelReply:
    if level == "none":  # answer without thinking first
        kwargs = {"thinking": {"type": "between_tools"}}
    else:
        kwargs = {"thinking": {"type": "adaptive"}, "output_config": {"effort": level}}
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=cap,
        messages=[{"role": "user", "content": case.prompt}],
        **kwargs,
    )
    text = "".join(b.text for b in reply.content if b.type == "text")
    if reply.stop_reason == "max_tokens":
        text = ""  # truncated: grade as a failure
    total = reply.usage.output_tokens
    thinking = reply.usage.output_tokens_details.thinking_tokens
    return ModelReply(text=text, visible_tokens=total - thinking, thinking_tokens=thinking)
# --8<-- [end:effort-anthropic]

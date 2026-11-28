"""One call at a chosen effort level, OpenAI Responses flavour.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

from .sweep import Case, ModelReply

# --8<-- [start:effort-responses]
from openai import OpenAI

client = OpenAI()


def model_fn(case: Case, level: str, cap: int) -> ModelReply:
    resp = client.responses.create(
        model="gpt-6.2-sol",
        input=case.prompt,
        reasoning={"effort": level},  # gpt-6.2-sol rejects "none"
        max_output_tokens=cap,
    )
    thinking = resp.usage.output_tokens_details.reasoning_tokens
    # status "incomplete" means the cap ran out, often mid-thinking
    text = resp.output_text if resp.status == "completed" else ""
    return ModelReply(
        text=text,
        visible_tokens=resp.usage.output_tokens - thinking,
        thinking_tokens=thinking,
    )
# --8<-- [end:effort-responses]

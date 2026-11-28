"""The editing pass against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

import anthropic

from .polish import polish_checked

client = anthropic.Anthropic()

# --8<-- [start:assembly-anthropic]
EDIT_PROMPT = (
    "Edit for one consistent voice. Reword only. Do not add, remove or change "
    "any number, name or [src:...] marker. Return the full text."
)


def edit_fn(text: str) -> str:
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=4096,
        system=EDIT_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    # Cut off mid-page: refuse it, and polish_checked keeps the original.
    if reply.stop_reason in ("max_tokens", "model_context_window_exceeded"):
        raise RuntimeError("editing pass cut off; keep the unpolished text")
    return next(b.text for b in reply.content if b.type == "text")


# polished, problems = polish_checked(edit_fn, assembled.text)
# --8<-- [end:assembly-anthropic]

"""The editing pass against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call.
"""
from __future__ import annotations

from openai import OpenAI

from .polish import polish_checked

client = OpenAI()

# --8<-- [start:assembly-responses]
EDIT_PROMPT = (
    "Edit for one consistent voice. Reword only. Do not add, remove or change "
    "any number, name or [src:...] marker. Return the full text."
)


def edit_fn(text: str) -> str:
    reply = client.responses.create(
        model="gpt-6.2-sol", instructions=EDIT_PROMPT, input=text
    )
    # status "incomplete" means cut off (reasoning tokens count against the
    # cap too): refuse it, and polish_checked keeps the original.
    if reply.status == "incomplete":
        raise RuntimeError("editing pass cut off; keep the unpolished text")
    return reply.output_text


# polished, problems = polish_checked(edit_fn, assembled.text)
# --8<-- [end:assembly-responses]

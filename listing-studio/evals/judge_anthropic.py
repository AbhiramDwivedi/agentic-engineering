"""The judge call against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. Same seam
as judge_langgraph.py: judge(prompt) -> str.
"""
from __future__ import annotations

import anthropic

client = anthropic.Anthropic()


# --8<-- [start:evals-judge-anthropic]
def judge(prompt: str) -> str:
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=8,
        messages=[{"role": "user", "content": prompt}],
    )
    return reply.content[0].text
# --8<-- [end:evals-judge-anthropic]

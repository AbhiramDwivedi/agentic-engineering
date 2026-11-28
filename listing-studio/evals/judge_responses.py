"""The judge call against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. Same seam
as judge_langgraph.py: judge(prompt) -> str.
"""
from __future__ import annotations

from openai import OpenAI

client = OpenAI()


# --8<-- [start:evals-judge-responses]
def judge(prompt: str) -> str:
    response = client.responses.create(model="gpt-6.2-sol", input=prompt)
    return response.output_text
# --8<-- [end:evals-judge-responses]

"""OpenAI Responses streaming feeding the translator. Illustration, not run in CI."""
from __future__ import annotations

from openai import APIError, OpenAI

from .events import UIEvent
from .translate import translate_openai

client = OpenAI()


def stream_ui_events(prompt: str, tools: list):
    try:
        stream = client.responses.create(model="gpt-6.2-sol", input=prompt, tools=tools, stream=True)
        yield from translate_openai(e.model_dump() for e in stream)
    except APIError as exc:  # a dropped or refused stream still ends the run visibly
        yield UIEvent(kind="error", text=str(exc))

"""Anthropic Messages streaming feeding the translator. Illustration, not run in CI."""
from __future__ import annotations

import anthropic

from .events import UIEvent
from .translate import translate_anthropic

client = anthropic.Anthropic()


def stream_ui_events(prompt: str, tools: list):
    try:
        with client.messages.stream(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
        ) as stream:
            raw = (e.model_dump() for e in stream)
            yield from translate_anthropic(raw)
    except anthropic.APIError as exc:  # the SDK raises instead of passing the error event on
        yield UIEvent(kind="error", text=str(exc))

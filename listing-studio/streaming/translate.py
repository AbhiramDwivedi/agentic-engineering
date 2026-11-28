"""Provider stream events -> UIEvents, translated once at the boundary.

Inputs are plain dicts (what the SDK events serialise to), so the tests can
script a stream without a network or an SDK.
"""
from __future__ import annotations

import json

from .events import UIEvent


# --8<-- [start:stream-translate-anthropic]
def translate_anthropic(events):
    """Anthropic Messages stream: content blocks arrive as start / delta / stop."""
    tool = None  # the open tool_use block: {"id", "name", "json"}
    for e in events:
        t = e["type"]
        if t == "content_block_start" and e["content_block"]["type"] == "tool_use":
            cb = e["content_block"]
            tool = {"id": cb["id"], "name": cb["name"], "json": ""}
        elif t == "content_block_delta":
            d = e["delta"]
            if d["type"] == "text_delta":
                yield UIEvent(kind="text", text=d["text"])
            elif d["type"] == "thinking_delta":
                yield UIEvent(kind="thinking", text=d["thinking"])
            elif d["type"] == "input_json_delta" and tool:
                tool["json"] += d["partial_json"]  # partial JSON: not parseable yet
        elif t == "content_block_stop" and tool:
            try:
                args = json.loads(tool["json"] or "{}")  # complete only now
                yield UIEvent(kind="tool_call", call_id=tool["id"], tool=tool["name"], args=args)
            except json.JSONDecodeError:  # possible with eager_input_streaming: never run it
                yield UIEvent(kind="error", call_id=tool["id"], tool=tool["name"],
                              text="invalid tool input")
            tool = None
        elif t == "message_stop":
            yield UIEvent(kind="done")
        elif t == "error":  # arrives as an event after a 200, not an HTTP error
            yield UIEvent(kind="error", text=e["error"]["message"])
        # ping and event types we do not know yet: ignored, never fatal
# --8<-- [end:stream-translate-anthropic]


# --8<-- [start:stream-translate-openai]
def translate_openai(events):
    """OpenAI Responses stream: argument deltas end in one `.done` event."""
    names = {}  # output_index -> (call_id, tool name); item.id is optional, the index is not
    for e in events:
        t = e["type"]
        if t == "response.output_text.delta":
            yield UIEvent(kind="text", text=e["delta"])
        elif t == "response.reasoning_summary_text.delta":
            yield UIEvent(kind="thinking", text=e["delta"])
        elif t == "response.output_item.added" and e["item"]["type"] == "function_call":
            item = e["item"]
            names[e["output_index"]] = (item["call_id"], item["name"])
        elif t == "response.function_call_arguments.done":
            if e["output_index"] not in names:  # never die mid-stream: say so instead
                yield UIEvent(kind="error", text="arguments for an unknown tool call")
                continue
            call_id, name = names[e["output_index"]]
            yield UIEvent(kind="tool_call", call_id=call_id, tool=name,
                          args=json.loads(e["arguments"]))
        elif t == "response.completed":
            yield UIEvent(kind="done")
        elif t in ("response.failed", "response.incomplete"):  # terminal, and not success
            r = e.get("response") or {}
            why = r.get("error") or r.get("incomplete_details") or {}
            yield UIEvent(kind="error", text=why.get("message") or why.get("reason") or t)
        elif t == "error":
            yield UIEvent(kind="error", text=e["message"])
        # every other event type: ignored, never fatal
# --8<-- [end:stream-translate-openai]

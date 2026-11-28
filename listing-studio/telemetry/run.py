"""One Listing Studio agent run, traced. The model is a scripted fake; nothing here is networked."""
from __future__ import annotations

from typing import Any, Callable

from .trace import Sink, span

MODEL = "claude-sonnet-5-5"
MAX_STEPS = 4  # loop cap: the run stops even if the model keeps asking for tools


# --8<-- [start:telemetry-model-span]
def traced_chat(sink: Sink, client: Callable[[list], dict], messages: list,
                capture_content: bool = False) -> dict:
    with span(sink, f"chat {MODEL}", **{
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": "anthropic",
        "gen_ai.request.model": MODEL,
    }) as s:
        reply = client(messages)
        s.attributes.update({
            "gen_ai.response.model": reply["model"],  # what actually answered
            "gen_ai.usage.input_tokens": reply["input_tokens"],
            "gen_ai.usage.output_tokens": reply["output_tokens"],
            "gen_ai.response.finish_reasons": [reply["finish_reason"]],
        })
        if capture_content:  # opt-in: content is off unless you ask for it
            s.attributes["gen_ai.input.messages"] = list(messages)  # a copy: the list grows later
            s.attributes["gen_ai.output.messages"] = reply["text"]
        return reply
# --8<-- [end:telemetry-model-span]


# --8<-- [start:telemetry-run]
def run_listing(sink: Sink, client: Callable[[list], dict],
                tools: dict[str, Callable[..., Any]], request: str,
                capture_content: bool = False) -> str:
    with span(sink, "invoke_agent listing-studio", **{"gen_ai.operation.name": "invoke_agent"}):
        messages: list = [{"role": "user", "content": request}]
        for _ in range(MAX_STEPS):
            reply = traced_chat(sink, client, messages, capture_content)
            call = reply.get("tool_call")
            if call is None:
                return reply["text"]
            with span(sink, f"execute_tool {call['name']}", **{
                "gen_ai.operation.name": "execute_tool",
                "gen_ai.tool.name": call["name"],
            }) as s:
                result = tools[call["name"]](**call["args"])
                if capture_content:
                    s.attributes["tool.arguments"] = call["args"]
            messages.append({"role": "tool", "content": result})
        return "stopped: step cap reached"
# --8<-- [end:telemetry-run]

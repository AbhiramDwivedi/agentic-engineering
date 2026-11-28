"""One call at a chosen effort level, LangGraph flavour (the chapter's default pane).

Illustration, not run in CI: needs an API key and a network call. The tested
sweep (sweep.py) takes any model_fn; this shows the shape of a real one.
"""
from __future__ import annotations

from .sweep import Case, ModelReply

# --8<-- [start:effort-langgraph]
from langchain.chat_models import init_chat_model


def model_fn(case: Case, level: str, cap: int) -> ModelReply:
    llm = init_chat_model(
        "openai:gpt-6.2-sol",
        reasoning_effort=level,  # gpt-6.2-sol rejects "none"
        max_tokens=cap,
    )
    msg = llm.invoke(case.prompt)
    usage = msg.usage_metadata or {}
    thinking = usage.get("output_token_details", {}).get("reasoning", 0)
    return ModelReply(
        text=msg.text,
        visible_tokens=usage.get("output_tokens", 0) - thinking,
        thinking_tokens=thinking,
    )
# --8<-- [end:effort-langgraph]

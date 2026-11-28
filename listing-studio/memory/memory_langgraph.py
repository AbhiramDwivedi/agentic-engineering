"""LangGraph: the model writes memory through a tool backed by a Store.

Illustration, not run in CI: needs an API key and a network call.
The default pane is this file; the OpenAI Responses and Anthropic variants are
memory_responses.py and memory_anthropic.py.
"""
from __future__ import annotations

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool
from langgraph.store.memory import InMemoryStore


@dataclass
class Context:
    user_id: str


# --8<-- [start:memory-langgraph]
@tool
def remember(key: str, value: str, runtime: ToolRuntime[Context]) -> str:
    """Save one short fact about the shopper for later visits."""
    if len(value) > 280:                       # same cap as MemoryStore; a Store won't enforce it
        return "too_large: keep a memory under 280 characters."
    # Namespaced by user; author and source ride along as provenance.
    runtime.store.put(
        ("memories", runtime.context.user_id), key,
        {"value": value, "author": "model", "source": "chat"},
    )
    return "saved"


agent = create_agent(
    init_chat_model("openai:gpt-6.2-sol"),
    tools=[remember],
    store=InMemoryStore(),                     # use a DB-backed store in production
    context_schema=Context,
)
# --8<-- [end:memory-langgraph]

"""Checkpointing with LangGraph (illustration, compile-checked only).

A checkpointer saves state after every node; the thread_id names the run to
resume. Not run in CI.
"""
from __future__ import annotations

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class ListingState(TypedDict):
    sku: str
    announced: bool
    published: bool


def announce(state: ListingState) -> dict:
    return {"announced": True}   # side effect: needs an idempotency key


def publish(state: ListingState) -> dict:
    return {"published": True}


# --8<-- [start:ckpt-langgraph]
builder = StateGraph(ListingState)
builder.add_node("announce", announce)
builder.add_node("publish", publish)
builder.add_edge(START, "announce")
builder.add_edge("announce", "publish")
builder.add_edge("publish", END)

# Use a durable saver (Postgres, SQLite) in production, not InMemorySaver.
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "listing-aldsworth-42"}}
graph.invoke({"sku": "LS-1001", "announced": False, "published": False}, config)
# After a crash, graph.invoke(None, config) resumes from the last checkpoint.
# --8<-- [end:ckpt-langgraph]

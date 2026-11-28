"""The same pause with LangGraph (the default the chapter shows): interrupt()
inside a node stops the graph and saves state under a thread_id; resuming with
Command(resume=...) re-runs that node FROM THE TOP, and interrupt() then returns
the human's answer instead of pausing.

Illustration, not run in CI: needs langgraph, which is not a declared dependency.
It reuses the tested gate_policy and action_digest. Anything written above the
interrupt() call runs twice, exactly like Effects.before_pause in pause_resume.py.
"""
from __future__ import annotations

from typing import Optional, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .gate import gate_policy
from .request import action_digest


class PriceState(TypedDict):
    args: dict
    result: Optional[dict]


# --8<-- [start:hitl-langgraph]
def approve_node(state: PriceState) -> dict:
    args = state["args"]
    band = gate_policy("set_price", args)
    if band == "deny":
        return {"result": {"status": "refused"}}
    if band == "ask":
        answer = interrupt({"digest": action_digest("set_price", args), "args": args})
        if answer["digest"] != action_digest("set_price", args):
            return {"result": {"status": "refused", "detail": "stale approval"}}
        if not answer["approve"]:
            return {"result": {"status": "rejected", "detail": answer.get("reason")}}
        args = answer.get("edited_args") or args
        if gate_policy("set_price", args) == "deny":
            return {"result": {"status": "refused", "detail": "edit below the floor"}}
    return {"result": {"status": "applied", "price": args["proposed_price_cents"]}}


builder = StateGraph(PriceState)
builder.add_node("approve", approve_node)
builder.add_edge(START, "approve")
builder.add_edge("approve", END)
graph = builder.compile(checkpointer=InMemorySaver())  # use a durable saver in production

config = {"configurable": {"thread_id": "reprice-aldsworth-1"}}  # same id on resume
# graph.invoke({"args": {...}, "result": None}, config)   -> pauses, returns __interrupt__
# graph.invoke(Command(resume={"digest": d, "approve": True}), config)
# --8<-- [end:hitl-langgraph]

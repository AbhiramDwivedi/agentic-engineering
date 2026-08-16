"""Dynamic fan-out with LangGraph (the default the chapter shows): a planner
node whose conditional edge returns a runtime-length list of Send objects,
one per named deliverable -- LangGraph's reference mechanism for a worker
count that does not exist in the graph definition.

Illustration, not run in CI: needs an API key and a network call. The
raw-SDK variants are fan_out_responses.py (OpenAI Responses) and
fan_out_example.py (Anthropic Messages); both reuse the tested
propose_deliverables (plan.py) and gather (gather.py) instead of
reimplementing the cap or the merge. Compare 3.2's route_after_classify: a
conditional edge that returns ONE node name, chosen from a fixed set. The
conditional edge below returns a LIST of Send(...) whose length is unknown
until plan_node's model call returns -- the code-level version of this
chapter's whole claim.
"""
from __future__ import annotations

import operator
from typing import Annotated, Optional, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .plan import MAX_EXTRA_DELIVERABLES
from .schemas import FanOutPlan, WorkerResult

llm = init_chat_model("openai:gpt-5.5")
planner_chain = llm.with_structured_output(FanOutPlan)


# --8<-- [start:fanout-langgraph]
class FanOutState(TypedDict):
    listing: dict
    plan: Optional[FanOutPlan]
    # Keyed by deliverable_id and merged with dict union -- never list
    # append, so two workers finishing in any order still land at the
    # right keys instead of depending on which one wrote first.
    results: Annotated[dict[str, WorkerResult], operator.or_]


def plan_node(state: FanOutState) -> dict:
    """The one model call: read the finished listing and name the extra
    deliverables it needs, zero or more, fresh for this product."""
    plan = planner_chain.invoke(
        "Given this finished Listing Studio product, name any extra launch "
        "deliverables it needs beyond the standard listing, announcement "
        f"email, and ad copy, and why: {state['listing']}"
    )
    return {"plan": plan}


def continue_to_workers(state: FanOutState) -> list[Send]:
    """The fan-out: one Send per named deliverable. This list's length does
    not exist until plan_node returns -- the worker count is nowhere in
    this file."""
    deliverables = state["plan"].deliverables[:MAX_EXTRA_DELIVERABLES]
    return [
        Send("worker", {"deliverable_id": d.deliverable_id, "listing": state["listing"]})
        for d in deliverables
    ]


def worker_node(state: dict) -> dict:
    """One worker, one deliverable. LangGraph invokes this once per Send;
    state here is whatever continue_to_workers passed for that Send, not
    the graph's full state."""
    content = llm.invoke(
        f"Write the {state['deliverable_id']} deliverable for this "
        f"Listing Studio product: {state['listing']}"
    ).content
    result = WorkerResult(deliverable_id=state["deliverable_id"], ok=True, content=content)
    return {"results": {state["deliverable_id"]: result}}


builder = StateGraph(FanOutState)
builder.add_node("plan", plan_node)
builder.add_node("worker", worker_node)
builder.add_edge(START, "plan")
builder.add_conditional_edges("plan", continue_to_workers)
builder.add_edge("worker", END)
graph = builder.compile()

result = graph.invoke(
    {"listing": {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"}}
)
print(result["results"])
# --8<-- [end:fanout-langgraph]

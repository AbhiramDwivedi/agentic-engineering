"""Demo 1: two parallel nodes write one key. Without a reducer the graph refuses."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from state.run_state import RunState

MAP_CENTS = 39900  # NV-ALDSWORTH-DM minimum advertised price


def check_map(state: dict) -> dict:
    below = state["price_cents"] < MAP_CENTS
    return {"flags": ["below MAP"] if below else []}


def check_title(state: dict) -> dict:
    return {"flags": ["title too long"]}


# --8<-- [start:state-unreduced]
class UnreducedState(TypedDict):
    price_cents: int
    flags: list          # no reducer: two writers in one step cannot both win


def build(schema):
    g = StateGraph(schema)
    g.add_node("check_map", check_map)
    g.add_node("check_title", check_title)
    g.add_edge(START, "check_map")      # both start in the same step
    g.add_edge(START, "check_title")
    g.add_edge("check_map", END)
    g.add_edge("check_title", END)
    return g.compile()


# build(UnreducedState).invoke({"price_cents": 39000, "flags": []})
# raises InvalidUpdateError (INVALID_CONCURRENT_GRAPH_UPDATE)
# --8<-- [end:state-unreduced]


# --8<-- [start:state-reduced]
def run_reduced() -> list:
    # Same graph, but RunState declares flags as Annotated[list, operator.add].
    out = build(RunState).invoke(
        {"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39000,
         "step_status": {}, "flags": []}
    )
    return out["flags"]     # both writes survive (order is not guaranteed)
# --8<-- [end:state-reduced]


def run_unreduced() -> list:
    return build(UnreducedState).invoke({"price_cents": 39000, "flags": []})["flags"]


def overwrite_demo() -> list:
    """Sequential writes to an unreduced key: the first write is silently lost."""
    class S(TypedDict):
        flags: list

    g = StateGraph(S)
    g.add_node("a", lambda s: {"flags": ["below MAP"]})
    g.add_node("b", lambda s: {"flags": ["title too long"]})
    g.add_edge(START, "a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    return g.compile().invoke({"flags": []})["flags"]

"""Specialist panel with LangGraph (the default the chapter shows): three
fixed persona nodes run from START, joined at one reconcile node -- three
static edges, not a Send-based fan-out, because the roster is fixed by
your code, not sized by a model.

Illustration, not run in CI: needs an API key and a network call. The
raw-SDK variants are specialist_panel_responses.py (OpenAI Responses) and
specialist_panel_example.py (Anthropic Messages); both reuse the tested
run_panel (roster.py) and reconcile (reconcile.py) instead of rebuilding
the graph. Compare 3.3's continue_to_workers: that conditional edge
returns a list of Send(...) whose length only exists after a model call
returns. Every edge below is written into the graph at build time, before
any persona has run -- the code-level version of this chapter's whole
claim.
"""
from __future__ import annotations

import operator
from typing import Annotated, Optional, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

from .reconcile import reconcile
from .roster import ROSTER
from .schemas import MissingSpecialist, PanelDecision, PersonaVerdict

# --8<-- [start:panel-langgraph]
llm = init_chat_model("openai:gpt-5.5")
persona_chain = llm.with_structured_output(PersonaVerdict)


class PanelState(TypedDict):
    listing: dict
    # Keyed by persona and merged with dict union -- three nodes write to
    # this key at once, and none of them needs to know the other two ran.
    verdicts: Annotated[dict[str, PersonaVerdict], operator.or_]
    decision: Optional[PanelDecision]


def make_persona_node(persona: str):
    """One node per roster entry, built at graph-definition time -- the
    roster decides the node count, never a model."""
    def _node(state: PanelState) -> dict:
        verdict = persona_chain.invoke(
            f"You are the {persona} specialist. Review this Listing Studio "
            f"product and return typed claims only for fields your role "
            f"covers: {state['listing']}"
        )
        return {"verdicts": {persona: verdict}}
    return _node


def reconcile_node(state: PanelState) -> dict:
    """The typed merge: a persona that never wrote to `verdicts` is
    reported, not silently absent."""
    missing = [
        MissingSpecialist(persona=p, reason="node did not report a verdict")
        for p in ROSTER if p not in state["verdicts"]
    ]
    return {"decision": reconcile(state["verdicts"], missing)}


builder = StateGraph(PanelState)
for _persona in ROSTER:
    builder.add_node(_persona, make_persona_node(_persona))
    builder.add_edge(START, _persona)
builder.add_node("reconcile", reconcile_node)
for _persona in ROSTER:
    builder.add_edge(_persona, "reconcile")
builder.add_edge("reconcile", END)
graph = builder.compile()

result = graph.invoke(
    {"listing": {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"}}
)
print(result["decision"].accepted, result["decision"].conflicts)
# --8<-- [end:panel-langgraph]

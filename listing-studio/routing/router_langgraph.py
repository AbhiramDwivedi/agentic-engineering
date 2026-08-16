"""LLM routing with LangGraph (the default the chapter shows): a classifier
node, then conditional edges to one of three specialist handler nodes, or to
an escalate-to-human node.

Illustration, not run in CI: needs an API key and a network call. The
raw-SDK variants are router_responses.py (OpenAI Responses) and
router_anthropic.py (Anthropic Messages); both reuse the tested
route_message from route.py instead of reimplementing the classify-then-
handle shape.
"""
from __future__ import annotations

from typing import Optional, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

from .schemas import Category, RouteDecision

llm = init_chat_model("openai:gpt-5.5")
classify_chain = llm.with_structured_output(RouteDecision)


# --8<-- [start:routing-langgraph]
class RouterState(TypedDict):
    message: str
    decision: Optional[RouteDecision]
    response: Optional[str]
    escalated: Optional[bool]


def classify_node(state: RouterState) -> dict:
    """The one model call: classify the unlabeled merchant message."""
    decision = classify_chain.invoke(
        "Classify this merchant helpdesk message into billing, "
        f"listing_issue, account, or unclear: {state['message']}"
    )
    return {"decision": decision}


def route_after_classify(state: RouterState) -> str:
    """Low confidence or an off-taxonomy read escalates instead of guessing."""
    decision = state["decision"]
    if decision.category == Category.UNCLEAR or decision.confidence < 0.6:
        return "escalate"
    return decision.category.value


def _handler_node(label: str):
    """One specialist node per category; only the label differs."""
    def node(state: RouterState) -> dict:
        return {"response": f"[{label}] {state['message']}", "escalated": False}
    return node


def escalate_node(state: RouterState) -> dict:
    """No handler is confident enough: hand off to a human."""
    decision = state["decision"]
    return {
        "response": (
            f"could not route with confidence ({decision.confidence:.2f}); "
            "escalated to a human"
        ),
        "escalated": True,
    }


builder = StateGraph(RouterState)
builder.add_node("classify", classify_node)
builder.add_node("billing", _handler_node("billing"))
builder.add_node("listing_issue", _handler_node("listing_issue"))
builder.add_node("account", _handler_node("account"))
builder.add_node("escalate", escalate_node)
builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "billing": "billing",
        "listing_issue": "listing_issue",
        "account": "account",
        "escalate": "escalate",
    },
)
builder.add_edge("billing", END)
builder.add_edge("listing_issue", END)
builder.add_edge("account", END)
builder.add_edge("escalate", END)
graph = builder.compile()

result = graph.invoke(
    {"message": "Why was I charged twice for my Stockwell subscription this month?"}
)
print(result["response"])
# --8<-- [end:routing-langgraph]

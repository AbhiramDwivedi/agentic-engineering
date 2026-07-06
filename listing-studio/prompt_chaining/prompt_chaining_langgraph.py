"""Prompt chaining with LangGraph (the default the chapter shows): a
StateGraph as the reference sequential-graph shape.

Illustration, not run in CI: needs an API key and a network call. The
raw-SDK variants are prompt_chaining_responses.py (OpenAI Responses) and
prompt_chaining_example.py (Anthropic Messages); both reuse the tested
run_chain from chain.py instead of reimplementing the gate. LangGraph's
control flow is graph edges, not Python function calls, so this tab
expresses the same gate + retry-once + loud-abort shape as graph nodes.
"""
from __future__ import annotations

from typing import Optional, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

from .gate import validate_category
from .schemas import CategoryDecision, CopyDraft

llm = init_chat_model("openai:gpt-5.5")
categorize_chain = llm.with_structured_output(CategoryDecision)
write_copy_chain = llm.with_structured_output(CopyDraft)


# --8<-- [start:chain-langgraph]
class ChainState(TypedDict):
    supplier_sku: str
    title: str
    category: Optional[CategoryDecision]
    category_error: Optional[str]  # the gate's structured error, fed back on retry
    attempt: int                   # how many times categorize has run
    copy: Optional[CopyDraft]


def categorize_node(state: ChainState) -> dict:
    """Step 3 (categorize), gated immediately after the call."""
    prompt = f"Categorize {state['title']} (SKU {state['supplier_sku']})."
    if state.get("category_error"):
        # Re-ask the SAME step, feeding back the gate's structured error.
        prompt += f" Previous attempt was rejected: {state['category_error']}"
    decision = categorize_chain.invoke(prompt)
    gate = validate_category(decision)
    return {
        "category": decision,
        "category_error": gate.error,
        "attempt": state.get("attempt", 0) + 1,
    }


def route_after_gate(state: ChainState) -> str:
    """The gate's routing decision: continue, retry once, or abort loudly."""
    if state["category_error"] is None:
        return "continue"
    if state["attempt"] < 2:
        return "retry"
    return "abort"


def abort_node(state: ChainState) -> dict:
    """The retry also failed: abort loudly. No silent pass-through."""
    raise RuntimeError(
        f"categorize step failed its gate twice: {state['category_error']}"
    )


def write_copy_node(state: ChainState) -> dict:
    """Step 4 (write copy): only the validated category_path crosses the gate."""
    decision = state["category"]
    draft = write_copy_chain.invoke(
        f"Write listing copy for {state['title']} (SKU {state['supplier_sku']}) "
        f"in category {decision.category_path}."
    )
    return {"copy": draft}


builder = StateGraph(ChainState)
builder.add_node("categorize", categorize_node)
builder.add_node("write_copy", write_copy_node)
builder.add_node("abort", abort_node)
builder.add_edge(START, "categorize")
builder.add_conditional_edges(
    "categorize",
    route_after_gate,
    {"continue": "write_copy", "retry": "categorize", "abort": "abort"},
)
builder.add_edge("write_copy", END)
builder.add_edge("abort", END)
chain = builder.compile()

result = chain.invoke(
    {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"}
)
print(result["copy"].description)
# --8<-- [end:chain-langgraph]

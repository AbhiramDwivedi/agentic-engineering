"""Clarify-attributes with LangGraph (the default the chapter shows): a
draft/evaluate/revise loop as a StateGraph, with the cap and the ratchet
wired into the conditional edge.

Illustration, not run in CI: needs an API key and a network call. The
raw-SDK variants are evaluator_optimizer_responses.py (OpenAI Responses)
and evaluator_optimizer_example.py (Anthropic Messages); both reuse the
tested run_loop (loop.py) instead of reimplementing the cap or the ratchet.
Compare 3.1's route_after_gate: that conditional edge retries at most once
against a deterministic check. The edge below routes back to the drafter
node on a "revise" verdict rendered by a model, bounded by the same cap
loop.py enforces -- a critic node whose verdict routes nowhere
produces no correction at all, only a display, and this wired edge is the
corrective.
"""
from __future__ import annotations

from typing import Optional, TypedDict

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

from .evaluate import evaluate
from .loop import DEFAULT_MAX_ITERATIONS
from .schemas import ClarifyingQuestions, Verdict

llm = init_chat_model("openai:gpt-5.5")
draft_chain = llm.with_structured_output(ClarifyingQuestions)
judge_chain = llm.with_structured_output(Verdict)


# --8<-- [start:eo-langgraph]
class ClarifyState(TypedDict):
    gaps: list[str]
    draft: Optional[ClarifyingQuestions]
    verdict: Optional[Verdict]
    best_draft: Optional[ClarifyingQuestions]
    best_verdict: Optional[Verdict]
    iteration: int


def draft_node(state: ClarifyState) -> dict:
    """Draft clarifying questions, informed by the prior verdict's reasons
    on every round after the first."""
    prompt = f"Draft one clarifying question per open attribute: {state['gaps']}."
    if state.get("verdict") is not None and not state["verdict"].passed:
        prompt += f" Fix these problems: {state['verdict'].reasons}"
    draft = draft_chain.invoke(prompt)
    return {"draft": draft, "iteration": state.get("iteration", 0) + 1}


def _judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
    return judge_chain.invoke(
        f"Grade these clarifying questions against gaps {gaps}: {draft.questions}"
    )


def evaluate_node(state: ClarifyState) -> dict:
    """Gate first, judge second -- the same evaluate() the plain-Python
    listing uses. The ratchet: best_* only moves forward on a strictly
    higher score."""
    verdict = evaluate(_judge_fn, state["gaps"], state["draft"])
    best_draft, best_verdict = state.get("best_draft"), state.get("best_verdict")
    if best_verdict is None or verdict.score > best_verdict.score:
        best_draft, best_verdict = state["draft"], verdict
    return {"verdict": verdict, "best_draft": best_draft, "best_verdict": best_verdict}


def route_after_evaluate(state: ClarifyState) -> str:
    """The wired revise edge: a "revise" verdict actually routes back to
    draft_node, bounded by DEFAULT_MAX_ITERATIONS -- never an unbounded
    loop, and never a verdict computed only to be displayed."""
    if state["verdict"].passed:
        return "done"
    if state["iteration"] < DEFAULT_MAX_ITERATIONS:
        return "revise"
    return "done"  # capped: state["best_draft"] carries the failure-return contract


builder = StateGraph(ClarifyState)
builder.add_node("draft", draft_node)
builder.add_node("evaluate", evaluate_node)
builder.add_edge(START, "draft")
builder.add_edge("draft", "evaluate")
builder.add_conditional_edges(
    "evaluate", route_after_evaluate, {"revise": "draft", "done": END}
)
graph = builder.compile()

result = graph.invoke({"gaps": ["leg_material", "weight_capacity_lbs"], "iteration": 0})
print(result["best_verdict"].passed, result["best_draft"].questions)
# --8<-- [end:eo-langgraph]

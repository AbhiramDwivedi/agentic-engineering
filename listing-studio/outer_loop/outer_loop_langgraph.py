"""Outer loop with LangGraph as the inner agent (the default pane).

Illustration, not run in CI: needs an API key and a network call. The
tested run_outer_loop in loop.py is shared by all three providers; only the
attempt function changes.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .loop import run_outer_loop
from .schemas import PriceCandidate
from .verifier import PriceRules

llm = init_chat_model("openai:gpt-6.2-sol")
propose = llm.with_structured_output(PriceCandidate)


# --8<-- [start:outer-langgraph]
def attempt(failures: list[str]) -> int:
    prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
    if failures:
        prompt += " Earlier attempts were rejected: " + " | ".join(failures)
    return propose.invoke(prompt).price_cents


rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
outcome = run_outer_loop(attempt, rules, max_attempts=3)
print(outcome.status, outcome.price_cents)
# --8<-- [end:outer-langgraph]

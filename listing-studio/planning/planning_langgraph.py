"""The planner call with LangGraph (the default pane): one structured-output
model call returns the whole Plan. Illustration, not run in CI: needs an API
key. The tested path is execute.run with a fake planner_fn.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .plan import Plan, planner_prompt

llm = init_chat_model("openai:gpt-6.2-sol")
planner_chain = llm.with_structured_output(Plan)


# --8<-- [start:plan-langgraph]
def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
    return planner_chain.invoke(planner_prompt(goal, done, failure))
# --8<-- [end:plan-langgraph]

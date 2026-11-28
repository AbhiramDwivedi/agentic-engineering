"""The planner call against the Anthropic Messages API. Illustration, not
run in CI: needs an API key. Same planner_fn seam as planning_langgraph.py;
the validation and the replan cap live in plan.py and execute.py, unchanged.
"""
from __future__ import annotations

import anthropic

from .plan import Plan, planner_prompt

client = anthropic.Anthropic()


# --8<-- [start:plan-anthropic]
def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
    reply = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        tools=[{
            "name": "write_plan",
            "description": "Write the ordered steps for this goal.",
            "input_schema": Plan.model_json_schema(),
        }],
        tool_choice={"type": "tool", "name": "write_plan"},
        messages=[{"role": "user", "content": planner_prompt(goal, done, failure)}],
    )
    block = next(b for b in reply.content if b.type == "tool_use")
    return Plan.model_validate(block.input)
# --8<-- [end:plan-anthropic]

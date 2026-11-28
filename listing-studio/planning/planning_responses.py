"""The planner call against the OpenAI Responses API. Illustration, not run
in CI: needs an API key. Same planner_fn seam as planning_langgraph.py; the
validation and the replan cap live in plan.py and execute.py, unchanged.
"""
from __future__ import annotations

from openai import OpenAI

from .plan import Plan, planner_prompt

client = OpenAI()


# --8<-- [start:plan-responses]
def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
    response = client.responses.create(
        model="gpt-6.2-sol",
        input=[{"role": "user", "content": planner_prompt(goal, done, failure)}],
        text={
            "format": {
                "type": "json_schema",
                "name": "Plan",
                "schema": Plan.model_json_schema(),
                "strict": True,
            }
        },
    )
    return Plan.model_validate_json(response.output_text)
# --8<-- [end:plan-responses]

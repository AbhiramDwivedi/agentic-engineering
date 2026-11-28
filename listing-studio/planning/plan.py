"""The plan the model writes once, and the checks your code runs on it
before anything executes.

No third-party imports beyond pydantic: importable in tests with no API key.
The provider files (planning_langgraph.py, planning_responses.py,
planning_example.py) only change how the plan is requested.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:plan-schema]
class Step(BaseModel):
    """One step the model proposes: which tool, with what input, and why."""
    model_config = ConfigDict(extra="forbid")

    tool: str
    arg: str
    why: str


class Plan(BaseModel):
    """The whole sequence, written once, before any step runs."""
    model_config = ConfigDict(extra="forbid")

    steps: list[Step]
# --8<-- [end:plan-schema]


# --8<-- [start:plan-validate]
# The allowlist and the cap are code, not prompt. A plan is text the model
# wrote after reading content you do not control (a supplier note, a
# competitor page), so it is checked as untrusted input before step one runs.
ALLOWED_TOOLS = {"draft_copy", "check_map_price", "set_price", "write_email"}
MAX_STEPS = 6


def validate_plan(plan: Plan) -> list[str]:
    """Return every reason to reject the plan; an empty list means run it."""
    problems = []
    if not plan.steps:
        problems.append("plan has no steps")
    if len(plan.steps) > MAX_STEPS:
        problems.append(f"plan has {len(plan.steps)} steps, cap is {MAX_STEPS}")
    for i, step in enumerate(plan.steps, start=1):
        if step.tool not in ALLOWED_TOOLS:
            problems.append(f"step {i}: tool {step.tool!r} is not on the allowlist")
    return problems
# --8<-- [end:plan-validate]


def planner_prompt(goal: str, done: list[str], failure: str | None) -> str:
    """The text every provider variant sends; only the call shape differs."""
    text = (
        f"Goal: {goal}\nWrite the shortest plan using only these tools: "
        f"{sorted(ALLOWED_TOOLS)}. Each step names a tool, one string input, "
        "and why."
    )
    if failure:
        text += f"\nAlready done: {done}\nIt failed: {failure}\nPlan the remaining work."
    return text

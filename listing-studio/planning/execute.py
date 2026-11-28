"""The executor: run a validated plan, and re-consult the model only when
your code's trigger fires.

planner_fn(goal, done, failure) is the seam the provider files inject. The
first call has done=[] and failure=None; a replan call carries what already
ran and what broke.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .plan import Plan, validate_plan


class StepFailed(Exception):
    """A tool ran and its own check said no (e.g. price below MAP)."""


@dataclass
class RunResult:
    status: str                      # "done" | "rejected" | "halted"
    log: list[str] = field(default_factory=list)
    replans: int = 0


# --8<-- [start:plan-run]
MAX_REPLANS = 1


def run(planner_fn: Callable[..., Plan], tools: dict[str, Any], goal: str) -> RunResult:
    result = RunResult(status="done")
    done: list[str] = []
    plan = planner_fn(goal, done, None)          # the model writes the plan once
    while True:
        problems = validate_plan(plan)           # code checks it before any step
        if problems:
            result.status = "halted" if result.replans else "rejected"
            result.log.append("rejected: " + "; ".join(problems))
            return result
        for step in plan.steps:
            try:
                out = tools[step.tool](step.arg)
            except StepFailed as exc:
                # The code-owned trigger: only a failed step asks the model
                # again, never an ordinary success.
                if result.replans >= MAX_REPLANS:
                    result.status = "halted"
                    result.log.append(f"halted: {step.tool} failed, no replans left")
                    return result
                result.replans += 1
                result.log.append(f"replan after {step.tool}: {exc}")
                plan = planner_fn(goal, done, f"{step.tool} failed: {exc}")
                break                            # discard the rest of the old plan
            done.append(f"{step.tool}: {out}")
            result.log.append(f"ran {step.tool}")
        else:
            return result                        # every step ran; plan complete
# --8<-- [end:plan-run]

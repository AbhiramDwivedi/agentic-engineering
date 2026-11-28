"""Per-run budget guard: the loop stops when the run has spent its tokens."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class RunResult:
    status: str  # "done" or "budget_exceeded"
    steps: int
    tokens_used: int
    answer: str = ""


# --8<-- [start:cost-budget]
def run_with_budget(
    step: Callable[[int], tuple[str, int, bool]],
    max_tokens: int,
    max_steps: int = 20,
) -> RunResult:
    """Call step(i) -> (output, tokens_spent, finished) while the next step fits."""
    used, biggest, latest = 0, 0, ""
    for i in range(1, max_steps + 1):
        if used + biggest > max_tokens:  # next step projected at the largest yet
            return RunResult("budget_exceeded", i - 1, used, latest)
        output, spent, finished = step(i)
        used += spent
        biggest = max(biggest, spent)
        latest = output  # keep the work done so far
        if finished:
            return RunResult("done", i, used, output)
    return RunResult("budget_exceeded", max_steps, used, latest)
# --8<-- [end:cost-budget]

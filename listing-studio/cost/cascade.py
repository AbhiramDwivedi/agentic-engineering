"""Cascade gate: try the cheap model first, escalate when a check fails."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class CascadeResult:
    answer: str
    model: str
    escalated: bool
    cost: int  # in cost units: cheap call = 1, strong call = 5


# --8<-- [start:cost-cascade]
CHEAP_COST, STRONG_COST = 1, 5


def cascade(
    task: str,
    cheap: Callable[[str], str],
    strong: Callable[[str], str],
    passes: Callable[[str], bool],
) -> CascadeResult:
    """Return the cheap answer if it passes the check, else pay for the strong one."""
    draft = cheap(task)
    if passes(draft):
        return CascadeResult(draft, "cheap", escalated=False, cost=CHEAP_COST)
    return CascadeResult(
        strong(task), "strong", escalated=True, cost=CHEAP_COST + STRONG_COST
    )
# --8<-- [end:cost-cascade]

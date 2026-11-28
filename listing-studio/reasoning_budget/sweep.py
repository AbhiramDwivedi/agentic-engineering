"""An effort sweep: the same cases, the same grader, every effort level.

Offline. ``model_fn`` is any callable that takes (case, level, cap) and returns
a ModelReply; the tests pass a scripted one, so nothing here touches a network.
Cost is in abstract units per 1,000 output tokens, because a real rate would
go stale; plug your own in.
"""
from __future__ import annotations

# --8<-- [start:sweep-types]
from collections.abc import Callable

from pydantic import BaseModel

# Supported levels are model-dependent; trim this list to what your model accepts.
LEVELS = ["none", "low", "medium", "high"]


class Case(BaseModel):
    id: str
    prompt: str
    expected: str


class ModelReply(BaseModel):
    text: str  # empty when the output cap was spent on thinking
    visible_tokens: int
    thinking_tokens: int


class LevelReport(BaseModel):
    level: str
    quality: float  # fraction of runs that passed
    output_tokens: int  # visible + thinking, summed over all runs
    cost: float
# --8<-- [end:sweep-types]


# --8<-- [start:sweep-run]
def run_sweep(
    model_fn: Callable[[Case, str, int], ModelReply],
    cases: list[Case],
    grade: Callable[[Case, str], bool],
    cap: int = 5000,  # max output tokens per call
    repeats: int = 3,
    units_per_1k: float = 1.0,
    levels: list[str] = LEVELS,
) -> list[LevelReport]:
    reports = []
    for level in levels:
        passed = tokens = runs = 0
        for case in cases:
            for _ in range(repeats):
                reply = model_fn(case, level, cap)
                runs += 1
                tokens += reply.visible_tokens + reply.thinking_tokens
                passed += bool(reply.text) and grade(case, reply.text)
        reports.append(
            LevelReport(
                level=level,
                quality=passed / runs,
                output_tokens=tokens,
                cost=tokens / 1000 * units_per_1k,
            )
        )
    return reports
# --8<-- [end:sweep-run]


# --8<-- [start:sweep-pick]
def cheapest_passing(
    reports: list[LevelReport], floor: float = 0.9, tolerance: float = 0.05
) -> LevelReport | None:
    """The cheapest level within `tolerance` of the best, or None if nothing reaches `floor`."""
    best = max(r.quality for r in reports)
    if best < floor:
        return None
    ok = [r for r in reports if r.quality >= max(floor, best - tolerance)]
    return min(ok, key=lambda r: r.cost)


def bill(reports: list[LevelReport]) -> str:
    return "\n".join(
        f"{r.level:<7} quality={r.quality:.2f} output_tokens={r.output_tokens} cost={r.cost:.2f}"
        for r in reports
    )
# --8<-- [end:sweep-pick]

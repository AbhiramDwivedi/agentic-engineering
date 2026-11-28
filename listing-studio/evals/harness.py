"""Repeat trials, report a rate with an error bar, refuse to call noise a win."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

from .cases import EvalCase
from .graders import grade_attributes


# --8<-- [start:evals-harness]
@dataclass(frozen=True)
class Rate:
    mean: float
    low: float
    high: float


def run_eval(system: Callable[[EvalCase], dict], cases: list[EvalCase],
             trials: int = 5) -> Rate:
    """Pass rate with a 95% interval from the standard error across cases.

    Each case's score is its pass fraction over `trials` runs. The cases are
    the sample, so the error bar is the CLT standard error of the per-case
    scores (Miller, arXiv 2411.00640), not a binomial over all trials as if
    they were independent questions.
    """
    scores = [
        sum(grade_attributes(c, system(c)).passed for _ in range(trials)) / trials
        for c in cases
    ]
    n = len(scores)
    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / (n - 1)
    half = 1.96 * math.sqrt(var / n)
    return Rate(mean, max(0.0, mean - half), min(1.0, mean + half))


def compare(a: Rate, b: Rate) -> str:
    """Call a winner only when the intervals do not overlap."""
    if b.low > a.high:
        return "b is better"
    if a.low > b.high:
        return "a is better"
    return "not distinguishable"
# --8<-- [end:evals-harness]

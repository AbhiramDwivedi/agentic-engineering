"""Best-of-N: the sibling that isn't a loop.

Sample N independent drafts, score each, keep the best -- no revision
step, no feedback carried between attempts. Compare loop.py: there, the
(n+1)th draft is informed by the nth draft's verdict; here, every draft
starts cold, and drafter_fn's signature (gaps only, no feedback) makes
that the code, not just the docstring.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evaluate import evaluate
from .schemas import ClarifyingQuestions, Verdict


# --8<-- [start:eo-best-of-n]
@dataclass
class BestOfNResult:
    draft: ClarifyingQuestions
    verdict: Verdict


def run_best_of_n(
    drafter_fn: Any,  # callable(gaps) -> ClarifyingQuestions -- no feedback arg
    judge_fn: Any,     # callable(gaps, draft) -> Verdict
    gaps: list[str],
    n: int,
) -> BestOfNResult:
    """Draw n independent drafts, score each, return the highest scorer."""
    candidates = [drafter_fn(gaps) for _ in range(n)]
    scored = [(draft, evaluate(judge_fn, gaps, draft)) for draft in candidates]
    best_draft, best_verdict = max(scored, key=lambda pair: pair[1].score)
    return BestOfNResult(draft=best_draft, verdict=best_verdict)
# --8<-- [end:eo-best-of-n]

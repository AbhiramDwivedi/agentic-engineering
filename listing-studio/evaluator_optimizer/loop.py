"""The clarify-attributes loop: draft, evaluate, revise -- capped,
ratcheted, and honest about how it stopped.

This is step 2 of the Listing Studio pipeline: a raw supplier feed row is
missing or ambiguous on some attributes; drafter_fn writes the clarifying
questions to send back to the supplier, and judge_fn grades them through
evaluate() (evaluate.py), which is where the cheap deterministic gate runs
before any judge call does. drafter_fn and judge_fn are the seam the
provider variants inject (LangGraph / Responses / Anthropic); see
evaluator_optimizer_langgraph.py, evaluator_optimizer_responses.py, and
evaluator_optimizer_example.py. In this plain-Python listing the "revise
edge" is just the top of the for loop; the LangGraph variant wires the same
idea as an explicit conditional edge back to the drafter node.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .evaluate import evaluate
from .schemas import ClarifyingQuestions, Verdict


# --8<-- [start:eo-loop]
# The cap guards a measured failure mode, not a hypothetical one: see
# "When Agents Do Not Stop" (arxiv.org/abs/2607.01641).
DEFAULT_MAX_ITERATIONS = 3


@dataclass
class LoopResult:
    """passed: whether the loop ended on a passing verdict. draft: the
    best-scoring attempt seen, not necessarily the last one drafted.
    verdict: the Verdict that scored `draft`. iterations: rounds run.
    stopped_reason: "passed" or "capped"."""
    passed: bool
    draft: ClarifyingQuestions
    verdict: Verdict
    iterations: int
    stopped_reason: str  # "passed" or "capped"


def run_loop(
    drafter_fn: Any,  # callable(gaps, feedback: Verdict | None) -> ClarifyingQuestions
    judge_fn: Any,     # callable(gaps, draft) -> Verdict
    gaps: list[str],
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> LoopResult:
    """Draft, evaluate, revise -- until the verdict passes or the cap trips.

    A revision that scores lower than the best draft so far still counts
    against `iterations` and is still discarded; `best` only moves forward
    on a strictly higher score.
    """
    best_draft: Optional[ClarifyingQuestions] = None
    best_verdict: Optional[Verdict] = None
    feedback: Optional[Verdict] = None

    for i in range(1, max_iterations + 1):
        draft = drafter_fn(gaps, feedback)
        verdict = evaluate(judge_fn, gaps, draft)

        if best_verdict is None or verdict.score > best_verdict.score:
            best_draft, best_verdict = draft, verdict

        if verdict.passed:
            return LoopResult(
                passed=True, draft=draft, verdict=verdict,
                iterations=i, stopped_reason="passed",
            )
        feedback = verdict  # the specific critique, never a bare "fail"

    return LoopResult(
        passed=False, draft=best_draft, verdict=best_verdict,
        iterations=max_iterations, stopped_reason="capped",
    )
# --8<-- [end:eo-loop]

"""The evaluator: a deterministic gate runs first, and only what survives
it costs an LLM-judge call.

Order is the whole point, made visible in code rather than left to a
comment: gate_draft() never touches a model, and evaluate() only calls
judge_fn once gate_draft() has already passed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .schemas import ClarifyingQuestions, Verdict


# --8<-- [start:eo-evaluate]
@dataclass
class GateResult:
    ok: bool
    reasons: list[str]


def gate_draft(gaps: list[str], draft: ClarifyingQuestions) -> GateResult:
    """Cheap, exact, no model call: no empty questions, no duplicates, and
    every named gap covered by at least one question."""
    reasons = []
    seen: set[str] = set()
    for q in draft.questions:
        if not q.strip():
            reasons.append("a clarifying question is empty")
            continue
        normalized = q.strip().lower()
        if normalized in seen:
            reasons.append(f"duplicate question: {q!r}")
        seen.add(normalized)

    for gap in gaps:
        if not any(gap.lower() in q.lower() for q in draft.questions):
            reasons.append(f"no question addresses the gap {gap!r}")

    return GateResult(ok=not reasons, reasons=reasons)


def evaluate(judge_fn: Any, gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
    """Cheap-first: gate_draft() runs before judge_fn ever does. A draft
    that fails the gate never reaches a model -- the judge call is the
    expensive step, so it only runs on what already cleared the free one.
    """
    gate = gate_draft(gaps, draft)
    if not gate.ok:
        return Verdict(passed=False, score=0.0, reasons=gate.reasons)
    return judge_fn(gaps, draft)
# --8<-- [end:eo-evaluate]

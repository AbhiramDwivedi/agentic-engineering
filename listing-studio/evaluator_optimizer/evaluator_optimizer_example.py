"""Clarify-attributes against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. The
default pane is evaluator_optimizer_langgraph.py; this is the Anthropic
Messages variant, and it reuses the tested run_loop (loop.py) -- only the
drafter and judge call shapes change per provider, not the cap, the
ratchet, or the gate.
"""
from __future__ import annotations

import anthropic

from .loop import run_loop
from .schemas import ClarifyingQuestions, Verdict

client = anthropic.Anthropic()

GAPS = ["leg_material", "weight_capacity_lbs"]

_DRAFT_TOOL = {
    "name": "produce_clarifying_questions",
    "description": "Draft one clarifying question per open attribute gap.",
    "input_schema": {
        "type": "object",
        "properties": {"questions": {"type": "array", "items": {"type": "string"}}},
        "required": ["questions"],
        "additionalProperties": False,
    },
}

_JUDGE_TOOL = {
    "name": "produce_verdict",
    "description": "Grade a set of clarifying questions against a rubric.",
    "input_schema": {
        "type": "object",
        "properties": {
            "passed": {"type": "boolean"},
            "score": {"type": "number"},
            "reasons": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["passed", "score", "reasons"],
        "additionalProperties": False,
    },
}


# --8<-- [start:eo-anthropic]
def drafter_fn(gaps: list[str], feedback: Verdict | None) -> ClarifyingQuestions:
    prompt = f"Draft one clarifying question per open attribute: {gaps}."
    if feedback is not None:
        prompt += f" Fix these problems: {feedback.reasons}"
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_DRAFT_TOOL],
        tool_choice={"type": "tool", "name": "produce_clarifying_questions"},
        messages=[{"role": "user", "content": prompt}],
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return ClarifyingQuestions.model_validate(tool_block.input)


def judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "produce_verdict"},
        messages=[
            {
                "role": "user",
                "content": f"Grade these clarifying questions against gaps {gaps}: {draft.questions}",
            }
        ],
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return Verdict.model_validate(tool_block.input)


result = run_loop(drafter_fn, judge_fn, GAPS)
print(result.stopped_reason, result.draft.questions)
# --8<-- [end:eo-anthropic]

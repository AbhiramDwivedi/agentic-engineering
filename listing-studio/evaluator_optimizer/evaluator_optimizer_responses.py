"""Clarify-attributes against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. The
default pane is evaluator_optimizer_langgraph.py; this is the OpenAI
Responses variant, and it reuses the tested run_loop (loop.py) -- only the
drafter and judge call shapes change per provider, not the cap, the
ratchet, or the gate.
"""
from __future__ import annotations

from openai import OpenAI

from .loop import run_loop
from .schemas import ClarifyingQuestions, Verdict

client = OpenAI()

GAPS = ["leg_material", "weight_capacity_lbs"]


# --8<-- [start:eo-responses]
def drafter_fn(gaps: list[str], feedback: Verdict | None) -> ClarifyingQuestions:
    prompt = f"Draft one clarifying question per open attribute: {gaps}."
    if feedback is not None:
        prompt += f" Fix these problems: {feedback.reasons}"
    response = client.responses.create(
        model="gpt-5.5",
        input=[{"role": "user", "content": prompt}],
        text={
            "format": {
                "type": "json_schema",
                "name": "ClarifyingQuestions",
                "schema": ClarifyingQuestions.model_json_schema(),
                "strict": True,
            }
        },
    )
    return ClarifyingQuestions.model_validate_json(response.output_text)


def judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": f"Grade these clarifying questions against gaps {gaps}: {draft.questions}",
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "Verdict",
                "schema": Verdict.model_json_schema(),
                "strict": True,
            }
        },
    )
    return Verdict.model_validate_json(response.output_text)


result = run_loop(drafter_fn, judge_fn, GAPS)
print(result.stopped_reason, result.draft.questions)
# --8<-- [end:eo-responses]

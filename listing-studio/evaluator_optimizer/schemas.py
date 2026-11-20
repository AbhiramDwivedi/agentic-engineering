"""Schemas for step 2's clarify-attributes loop: the drafted clarifying
questions and the evaluator's verdict.

No third-party imports beyond pydantic: this module is directly importable
in tests without an API key or SDK. The illustration files import from here
and pass the schema to whichever provider API they use.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# --8<-- [start:eo-schemas]
class ClarifyingQuestions(BaseModel):
    """The drafter's output: one clarifying question per attribute this
    supplier feed row left missing or ambiguous."""
    model_config = ConfigDict(extra="forbid")

    questions: list[str]


class Verdict(BaseModel):
    """The evaluator's judgment. `reasons` must be specific enough for the
    drafter's next attempt to act on."""
    model_config = ConfigDict(extra="forbid")

    passed: bool
    score: float          # 0.0-1.0; the ratchet compares drafts on this
    reasons: list[str]    # e.g. "question 2 duplicates question 1"
# --8<-- [end:eo-schemas]

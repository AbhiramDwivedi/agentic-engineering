"""The three question shapes, the answer a decision model returns, and a fake client.

A decision model call generates no text. It returns a probability distribution over
fixed options. Everything after that (threshold, abstain, escalate) is your code.
"""
from __future__ import annotations

from dataclasses import dataclass


# --8<-- [start:dm-shapes]
@dataclass(frozen=True)
class Question:
    kind: str                      # "predicate" | "choice" | "score"
    text: str
    options: tuple[str, ...]       # predicate: ("true", "false"); score: ordered levels


def predicate(text: str) -> Question:
    return Question("predicate", text, ("true", "false"))


def choice(text: str, options: tuple[str, ...]) -> Question:
    return Question("choice", text, options)


def score(text: str, levels: int) -> Question:
    return Question("score", text, tuple(str(i) for i in range(1, levels + 1)))


@dataclass(frozen=True)
class Answer:
    probs: dict[str, float] | None   # None: the vendor gave a label, not a distribution
    label: str | None = None         # the adapter-fallback label, when probs is None
    refused: bool = False            # the provider declined to decide
# --8<-- [end:dm-shapes]


class FakeDecisionClient:
    """Scripted stand-in for a vendor Decisions endpoint. Offline, deterministic."""

    def __init__(self, script: dict[str, Answer]):
        self.script = script
        self.calls = 0

    def decide(self, listing: str, question: Question) -> Answer:
        self.calls += 1
        return self.script[question.text]

    def decide_many(self, listing: str, questions: list[Question]) -> list[Answer]:
        # Several questions over one shared input, one request.
        self.calls += 1
        return [self.script[q.text] for q in questions]

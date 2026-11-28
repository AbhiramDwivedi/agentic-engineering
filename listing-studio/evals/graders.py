"""Two graders: code where the answer is checkable, a model judge where it is not."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cases import EvalCase


@dataclass(frozen=True)
class Grade:
    passed: bool
    problems: tuple = ()


# --8<-- [start:evals-code-grader]
def grade_attributes(case: EvalCase, listing: dict) -> Grade:
    """Pass only if every required attribute is present and right, and
    nothing forbidden was invented. A correct do-nothing passes."""
    problems = [
        f"{key}: want {want!r}, got {listing.get(key)!r}"
        for key, want in case.required.items()
        if listing.get(key) != want
    ]
    problems += [f"invented {key}" for key in case.forbidden if key in listing]
    return Grade(not problems, tuple(problems))
# --8<-- [end:evals-code-grader]


# --8<-- [start:evals-judge-grader]
JUDGE_PROMPT = (
    "You are grading one product listing against ONE criterion.\n"
    "Criterion: {criterion}\n\nListing:\n{listing}\n\n"
    "Answer with exactly one word: yes or no."
)


def parse_verdict(reply: str) -> bool:
    """Anything that is not a clear 'yes' counts as a fail: fail closed."""
    return reply.strip().lower().startswith("yes")


def judge_listing(
    judge: Callable[[str], str], criteria: list[str], listing_text: str
) -> dict[str, bool]:
    """One isolated call per criterion, one binary verdict each. The judge
    returns verdicts; it never decides what happens next."""
    return {
        c: parse_verdict(judge(JUDGE_PROMPT.format(criterion=c, listing=listing_text)))
        for c in criteria
    }
# --8<-- [end:evals-judge-grader]

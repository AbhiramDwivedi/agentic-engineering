"""The policy: run the layers cheapest first, stop at the first block, send it to review."""
from __future__ import annotations

from typing import Literal

import anyio

from .checks import Record, claim_check, leak_check, schema_check
from .classifier import FakeClassifier
from .verdict import Outcome, Verdict


# --8<-- [start:guard-classify]
async def classify_check(text: str, clf: FakeClassifier, *, threshold: float,
                         timeout: float, on_error: Literal["open", "closed"]) -> Verdict:
    try:
        with anyio.fail_after(timeout):
            risk = await clf.score(text)
    except Exception as e:  # a raise or a timeout: the policy decides, not luck
        # Closed holds the listing for a human; open lets it through, and says so.
        return Verdict(check="classifier", passed=on_error == "open",
                       reason=f"classifier {type(e).__name__}; failed {on_error}")
    return Verdict(check="classifier", passed=risk < threshold,
                   reason=f"risk {risk:.2f} against threshold {threshold:.2f}")
# --8<-- [end:guard-classify]


# --8<-- [start:guard-suite]
async def run_guards(raw: dict, record: Record, clf: FakeClassifier, *,
                     threshold: float = 0.5, timeout: float = 2.0,
                     on_error: Literal["open", "closed"] = "closed",
                     shadow: frozenset[str] = frozenset()) -> Outcome:
    verdicts: list[Verdict] = []

    def settle(v: Verdict) -> bool:          # True means stop: this layer blocks
        if v.check in shadow:
            v = v.model_copy(update={"mode": "shadow"})
        verdicts.append(v)
        return v.blocks

    v, copy = schema_check(raw)
    if settle(v) or copy is None:
        return Outcome(decision="review", verdicts=verdicts)
    for check in (claim_check, leak_check):  # cheapest first, model call last
        if settle(check(copy, record)):
            return Outcome(decision="review", verdicts=verdicts)
    text = f"{copy.title}\n{copy.description}"
    v = await classify_check(text, clf, threshold=threshold, timeout=timeout,
                             on_error=on_error)
    blocked = settle(v)
    return Outcome(decision="review" if blocked else "publish", verdicts=verdicts)
# --8<-- [end:guard-suite]

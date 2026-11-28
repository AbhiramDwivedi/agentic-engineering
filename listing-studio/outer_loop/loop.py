"""The outer loop: code runs the attempt, code runs the verifier, code stops."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .verifier import PriceRules, verify_price


# --8<-- [start:outer-loop]
@dataclass
class Outcome:
    status: str                      # "passed" or "gave_up"
    price_cents: int | None = None   # set only when the verifier passed
    attempts: int = 0
    failures: list[str] = field(default_factory=list)  # for the human on give-up


def run_outer_loop(
    attempt: Callable[[list[str]], int],  # one inner agent run: failures so far -> price
    rules: PriceRules,
    max_attempts: int = 3,                # hard attempt cap
) -> Outcome:
    failures: list[str] = []
    for n in range(1, max_attempts + 1):
        price = attempt(failures)              # the model decides inside this call
        verdict = verify_price(price, rules)   # the code decides here, on its own schedule
        if verdict.ok:
            return Outcome("passed", price, n, failures)
        if failures and verdict.feedback == failures[-1]:
            break                              # same failure twice: futile, stop early
        failures.append(verdict.feedback)
    # Give up explicitly: hand the failures to the merchandiser, never ship a bad price.
    return Outcome("gave_up", None, n, failures)
# --8<-- [end:outer-loop]

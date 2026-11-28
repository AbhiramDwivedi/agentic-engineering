"""Bounded retry with full jitter, a deadline and a retry budget."""
from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

from resilience.classify import TRANSIENT, ProviderError, classify

T = TypeVar("T")


# --8<-- [start:retry]
class RetryBudget:
    """Per-client cap: retries may use at most `ratio` of recent calls (SRE ch. 21)."""

    def __init__(self, ratio: float = 0.1, floor: int = 3):
        self.ratio, self.floor = ratio, floor
        self.calls = 0
        self.retries = 0

    def allow(self) -> bool:
        return self.retries < max(self.floor, self.ratio * self.calls)


def call_with_retry(
    fn: Callable[[], T],
    budget: RetryBudget,
    *,
    idempotent: bool = True,  # False for a write that carries no key
    max_attempts: int = 3,
    base: float = 0.5,
    cap: float = 8.0,
    deadline: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.monotonic,
    rng: random.Random = random.Random(),
) -> T:
    start = now()
    for attempt in range(1, max_attempts + 1):
        budget.calls += 1
        try:
            return fn()
        except ProviderError as err:
            if classify(err, idempotent) != TRANSIENT or attempt == max_attempts:
                raise  # terminal, or out of attempts: the caller decides
            if not budget.allow():
                raise  # shed load instead of piling on
            wait = err.retry_after
            if wait is None:
                wait = rng.uniform(0, min(cap, base * 2 ** attempt))  # full jitter
            if now() - start + wait > deadline:
                raise  # one deadline for all the waits, not one per attempt
            budget.retries += 1
            sleep(wait)
    raise AssertionError("unreachable")
# --8<-- [end:retry]

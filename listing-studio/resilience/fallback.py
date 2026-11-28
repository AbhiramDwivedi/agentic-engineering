"""An ordered fallback chain, tried only after retries are spent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from resilience.classify import TERMINAL, ProviderError, classify
from resilience.retry import RetryBudget, call_with_retry


@dataclass
class Answer:
    text: str
    model: str
    degraded: bool  # never substitute silently: the caller can label it


# --8<-- [start:fallback]
def answer_with_fallback(
    prompt: str,
    chain: list[tuple[str, Callable[[str], str]]],
    budget: RetryBudget,
    **retry_kwargs,
) -> Answer:
    last: ProviderError | None = None
    for i, (model, call) in enumerate(chain):
        try:
            text = call_with_retry(lambda: call(prompt), budget, **retry_kwargs)
            return Answer(text, model, degraded=i > 0)
        except ProviderError as err:
            if classify(err) == TERMINAL:
                raise  # terminal: stop, do not shop the call around
            last = err  # retries spent: try the next rung
    raise last  # every rung failed: stop and say so
# --8<-- [end:fallback]

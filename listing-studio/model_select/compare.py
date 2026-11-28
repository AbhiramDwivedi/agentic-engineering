"""Same step, N models, one scorer: the eval that gates a model swap.

The clients are plain callables (prompt -> text), so the comparison runs with
fakes and no network. A real client wraps a provider call behind the same shape.
"""
from __future__ import annotations

from typing import Callable

Client = Callable[[str], str]
Case = tuple[str, str]  # (prompt, expected answer)


def score(client: Client, cases: list[Case]) -> float:
    """Share of cases where the client's answer matches the expected one."""
    hits = sum(1 for prompt, expected in cases if client(prompt).strip() == expected)
    return hits / len(cases)


# --8<-- [start:model-compare]
def compare(clients: dict[str, Client], cases: list[Case]) -> dict[str, float]:
    """Run the same cases through every candidate model and score each."""
    return {model: score(client, cases) for model, client in clients.items()}


def choose(scores: dict[str, float], current: str) -> str:
    """Swap only when a candidate beats the current model on the eval."""
    best = max(scores, key=scores.get)
    return best if scores[best] > scores[current] else current
# --8<-- [end:model-compare]

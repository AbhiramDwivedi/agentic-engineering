"""Classify a failure before deciding what to do with it."""
from __future__ import annotations

from dataclasses import dataclass


# --8<-- [start:classify]
@dataclass
class ProviderError(Exception):
    """What a provider adapter raises, on an error status or on a 200 it cannot use."""
    code: int | str  # HTTP status, or the stop reason on a 200 ("max_tokens")
    kind: str = ""  # provider error type, e.g. "rate_limit_error", "timeout"
    detail: str = ""  # provider error code, e.g. "credit_balance_exhausted"
    retry_after: float | None = None  # seconds, from the retry-after header


TRANSIENT = "transient"  # the same call may succeed after a wait
TERMINAL = "terminal"    # resending the same call will not help

SPEND_CAPS = {
    "enforced_spend_limit_reached",  # Anthropic
    "credit_balance_exhausted", "organization_spend_limit_exceeded",  # OpenAI
    "project_spend_limit_exceeded", "organization_usage_limit_exceeded",
}


def classify(err: ProviderError, idempotent: bool = True) -> str:
    # A 429 has two meanings: a rate limit passes, a spend cap does not.
    if err.kind == "insufficient_quota" or err.detail in SPEND_CAPS:
        return TERMINAL
    if err.kind == "timeout":
        # Unknown outcome: replay only a call that is safe to repeat.
        return TRANSIENT if idempotent else TERMINAL
    if err.code in (408, 429, 500, 502, 503, 504, 529):
        return TRANSIENT
    # 400, 401, 403, 404, 413, a refusal, max_tokens, context overflow
    return TERMINAL
# --8<-- [end:classify]

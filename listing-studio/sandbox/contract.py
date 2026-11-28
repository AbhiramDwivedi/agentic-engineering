"""The execution contract: what any backend accepts and returns."""
from __future__ import annotations

# --8<-- [start:sandbox-contract]
from dataclasses import dataclass
from typing import Protocol

MAX_OUTPUT_CHARS = 2000  # a backend never returns unbounded output to the model


@dataclass(frozen=True)
class ExecResult:
    exit_code: int | None  # None when the run was killed by the timeout
    stdout: str
    stderr: str
    timed_out: bool = False
    truncated: bool = False


def bound(text: str, limit: int = MAX_OUTPUT_CHARS) -> tuple[str, bool]:
    """Cut text to the limit; report whether anything was dropped."""
    if len(text) <= limit:
        return text, False
    return text[:limit], True


class ExecutionBackend(Protocol):
    def run(self, code: str, timeout_s: float) -> ExecResult: ...
# --8<-- [end:sandbox-contract]

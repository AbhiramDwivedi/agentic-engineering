"""Pin the full configuration, gate a change on golden cases, roll back."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .template import VOICE_V1, PromptTemplate


# --8<-- [start:prompt-config]
@dataclass(frozen=True)
class RunConfig:
    """The prompt, model, and temperature that produced an output."""
    prompt: PromptTemplate
    model: str
    temperature: float


Case = tuple[dict[str, str], list[str], list[str]]   # data, must contain, must not
CallFn = Callable[[RunConfig, dict[str, str]], str]
# --8<-- [end:prompt-config]


# --8<-- [start:prompt-eval]
def run_golden(cfg: RunConfig, cases: list[Case], call: CallFn) -> list[str]:
    """Run every golden case; return the failures (empty list means pass)."""
    failures = []
    for data, must, must_not in cases:
        out = call(cfg, data)
        failures += [f"missing {s!r}" for s in must if s not in out]
        failures += [f"forbidden {s!r}" for s in must_not if s in out]
    return failures
# --8<-- [end:prompt-eval]


# --8<-- [start:prompt-release]
class Release:
    def __init__(self, live: RunConfig):
        self.live = live
        self.history: list[RunConfig] = []

    def propose(self, candidate: RunConfig, cases: list[Case], call: CallFn) -> list[str]:
        """Promote only if every golden case passes."""
        failures = run_golden(candidate, cases, call)
        if not failures:
            self.history.append(self.live)
            self.live = candidate
        return failures

    def rollback(self) -> RunConfig:
        """Restore the previous config whole."""
        self.live = self.history.pop()
        return self.live
# --8<-- [end:prompt-release]


LIVE_V1 = RunConfig(VOICE_V1, model="claude-sonnet-5-5", temperature=0.0)

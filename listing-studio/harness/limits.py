"""Run limits: step cap, spend cap, wall-clock timeout (injected clock)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


# --8<-- [start:limits]
@dataclass
class Limits:
    max_steps: int = 20
    max_spend_cents: int = 500
    timeout_s: float = 60.0
    clock: Callable[[], float] = field(default=lambda: 0.0)   # inject in tests
    started: float = 0.0

    def stop_reason(self, steps: int, spent_cents: int) -> str | None:
        """Checked before every model call; the model cannot raise a cap."""
        if steps >= self.max_steps:
            return "step_cap"
        if spent_cents >= self.max_spend_cents:
            return "spend_cap"
        if self.clock() - self.started >= self.timeout_s:
            return "timeout"
        return None
# --8<-- [end:limits]

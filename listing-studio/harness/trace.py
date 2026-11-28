"""Trace: one event per decision, so a run can be read back."""
from __future__ import annotations


# --8<-- [start:trace]
class Trace:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, step: int, kind: str, name: str, outcome: str, reason: str = ""):
        self.events.append(
            {"step": step, "kind": kind, "name": name, "outcome": outcome, "reason": reason}
        )
# --8<-- [end:trace]

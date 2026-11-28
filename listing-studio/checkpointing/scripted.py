"""A scripted model: returns different arguments each time it is asked.

Real models are not deterministic, so a replayed step can come back with
different arguments than the first attempt. This fake makes that visible.
"""
from __future__ import annotations


# --8<-- [start:ckpt-model]
class ScriptedModel:
    def __init__(self, replies: list[dict]):
        self.replies = list(replies)
        self.calls = 0

    def decide(self, step: str) -> dict:
        reply = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return reply
# --8<-- [end:ckpt-model]

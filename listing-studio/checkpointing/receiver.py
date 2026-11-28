"""The outside world: a receiver that performs side effects and dedupes by key.

Offline stand-in for an email provider or a price API that honours an
idempotency key. strict=True models a receiver that rejects a reused key
carrying different parameters.
"""
from __future__ import annotations


# --8<-- [start:ckpt-receiver]
class ParamMismatch(Exception):
    """Same idempotency key, different parameters."""


class Receiver:
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.seen: dict[str, dict] = {}  # key -> params
        self.effects: list[dict] = []    # what really happened

    def send(self, key: str, params: dict) -> str:
        if key in self.seen:
            if self.strict and self.seen[key] != params:
                raise ParamMismatch(f"key {key!r} reused with different params")
            return "deduped"
        self.seen[key] = params
        self.effects.append(params)
        return "done"
# --8<-- [end:ckpt-receiver]

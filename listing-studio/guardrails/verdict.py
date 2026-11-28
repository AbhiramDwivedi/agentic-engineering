"""One structured result per check, and the decision the policy draws from them."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# --8<-- [start:guard-verdict]
class Verdict(BaseModel):
    check: str                                   # which layer spoke
    passed: bool
    reason: str = ""                             # what the reviewer will read
    mode: Literal["enforce", "shadow"] = "enforce"

    @property
    def blocks(self) -> bool:
        # A shadow check records its finding but never holds a listing back.
        return self.mode == "enforce" and not self.passed
# --8<-- [end:guard-verdict]


class Outcome(BaseModel):
    decision: Literal["publish", "review"]
    verdicts: list[Verdict]

"""The one model-backed layer, scripted so tests run offline."""
from __future__ import annotations

import anyio


# --8<-- [start:guard-classifier]
class FakeClassifier:
    """Stands in for a moderation or safeguard model: returns a risk score in [0, 1].

    Scripted by substring; can also raise or run past the timeout. Records its calls.
    """

    def __init__(self, scores: dict[str, float] | None = None,
                 raises: Exception | None = None, delay: float = 0.0):
        self.scores, self.raises, self.delay = scores or {}, raises, delay
        self.calls: list[str] = []

    async def score(self, text: str) -> float:
        self.calls.append(text)
        await anyio.sleep(self.delay)
        if self.raises:
            raise self.raises
        return max((s for k, s in self.scores.items() if k in text), default=0.0)
# --8<-- [end:guard-classifier]

"""The probe: ask what the window still knows, and report what it lost."""
from __future__ import annotations

from pydantic import BaseModel

from .state import RunState, render
from .window import Message


class Question(BaseModel):
    ask: str     # what a later turn would need to answer
    expect: str  # the fact that must still be readable in the window


# --8<-- [start:compaction-probe]
def probe(history: list[Message], state: RunState, questions: list[Question]) -> list[str]:
    """A presence probe: is the expected fact anywhere in render(state) + history?
    It tests that the fact is still there, not that a model would recall it.
    Returns the questions the window can no longer answer."""
    window = " ".join(m.content for m in [render(state), *history]).lower()
    return [q.ask for q in questions if q.expect.lower() not in window]
# --8<-- [end:compaction-probe]

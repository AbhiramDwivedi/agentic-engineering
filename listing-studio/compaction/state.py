"""State your code owns: a record rendered into the window every call, so it
cannot be summarized away."""
from __future__ import annotations

from pydantic import BaseModel

from .window import Message


# --8<-- [start:compaction-state]
class RunState(BaseModel):
    decisions: dict[str, str] = {}  # written by code the moment a decision is made


def render(state: RunState) -> Message:
    """Put the state record back into the window. Call it every turn, after any compaction."""
    lines = [f"- {k}: {v}" for k, v in state.decisions.items()]
    return Message(role="user", content="Run state (kept by code):\n" + "\n".join(lines), pinned=True)
# --8<-- [end:compaction-state]

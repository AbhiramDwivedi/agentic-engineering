"""The window: a list of messages, and a rough count of what it costs."""
from __future__ import annotations

from pydantic import BaseModel


# --8<-- [start:compaction-window]
class Message(BaseModel):
    role: str                     # "user", "assistant" or "tool"
    content: str
    pinned: bool = False          # a pinned message is never masked, trimmed or summarized
    result_id: str | None = None  # set on tool results; the archive key


def estimate_tokens(history: list[Message]) -> int:
    """An estimate: one word counts as one token. Trigger on this, not on message count."""
    return sum(len(m.content.split()) for m in history)
# --8<-- [end:compaction-window]

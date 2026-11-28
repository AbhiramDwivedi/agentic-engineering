"""Compaction: shrink history when it grows, but keep pinned messages."""
from __future__ import annotations

from typing import Callable


# --8<-- [start:compact]
def compact(messages: list[dict], max_messages: int, keep_last: int,
            pre_compact: Callable[[list[dict]], None]) -> list[dict]:
    """Over the trigger, archive everything, then keep pinned messages
    plus the recent tail. The middle becomes one summary line."""
    if len(messages) <= max_messages:
        return messages
    pre_compact(list(messages))                  # archive before anything is lost
    pinned = [m for m in messages if m.get("pinned")]
    tail = [m for m in messages[-keep_last:] if not m.get("pinned")]
    dropped = len(messages) - len(pinned) - len(tail)
    summary = {"role": "user", "content": f"[{dropped} earlier messages compacted]"}
    return pinned + [summary] + tail
# --8<-- [end:compact]

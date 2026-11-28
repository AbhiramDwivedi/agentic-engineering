"""A per-user memory store the model writes into and your code polices.

Plain Python, no embeddings (retrieval craft is chapter 5.2). The model decides
what to remember; this code decides what is allowed to be stored.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from .schemas import MemoryEntry, WriteResult

MAX_VALUE_CHARS = 280
MAX_ENTRIES_PER_USER = 50
TTL_DAYS = 90
_KEY = re.compile(r"^[a-z][a-z0-9_]{0,39}$")


# --8<-- [start:memory-store]
class MemoryStore:
    def __init__(self) -> None:
        # One namespace per user: user_id is the outer key, so a lookup for
        # one shopper can never return another shopper's entry.
        self._data: dict[str, dict[str, MemoryEntry]] = {}

    def write(self, user_id: str, key: str, value: str, author: str,
              source: str, now: datetime,
              user_confirmed: bool = False) -> WriteResult:
        if not _KEY.match(key):
            return WriteResult(ok=False, error="bad_key",
                               detail="Use a short snake_case key like 'garage_size'.")
        if len(value) > MAX_VALUE_CHARS:
            return WriteResult(ok=False, error="too_large",
                               detail=f"Keep a memory under {MAX_VALUE_CHARS} characters.")
        # Text that came out of a tool result or a fetched page never becomes
        # memory unless the user confirmed it: this is the poisoning gate.
        if author == "tool" and not user_confirmed:
            return WriteResult(ok=False, error="untrusted_source",
                               detail="Tool output cannot be saved without the user's OK.")
        mine = self._data.setdefault(user_id, {})
        if key not in mine and len(mine) >= MAX_ENTRIES_PER_USER:
            return WriteResult(ok=False, error="quota_exceeded",
                               detail="Memory is full; forget something first.")
        # Same key replaces the old entry (supersede, never append a rival).
        mine[key] = MemoryEntry(
            key=key, value=value, author=author, source=source,
            written_at=now, expires_at=now + timedelta(days=TTL_DAYS),
        )
        return WriteResult(ok=True)

    def forget(self, user_id: str, key: str) -> bool:
        return self._data.get(user_id, {}).pop(key, None) is not None
# --8<-- [end:memory-store]


# --8<-- [start:memory-recall]
def recall(store: MemoryStore, user_id: str, query: str,
           now: datetime) -> list[MemoryEntry]:
    """Entries that match the query words and have not expired, newest first."""
    mine = store._data.get(user_id, {})
    for key in [k for k, e in mine.items() if e.expires_at <= now]:
        del mine[key]                          # expired entries are deleted
    words = set(query.lower().split())
    hits = [e for e in mine.values()
            if words & set(f"{e.key.replace('_', ' ')} {e.value}".lower().split())]
    return sorted(hits, key=lambda e: e.written_at, reverse=True)
# --8<-- [end:memory-recall]

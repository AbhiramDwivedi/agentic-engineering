"""What one remembered fact carries, and what a write returns."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


# --8<-- [start:memory-entry]
class MemoryEntry(BaseModel):
    key: str                                   # "garage_size", never a free-form path
    value: str
    author: Literal["user", "model", "tool"]   # write provenance: who put this here
    source: str                                # the turn, message or document it came from
    written_at: datetime
    expires_at: datetime                       # recall deletes the entry after this


class WriteResult(BaseModel):
    ok: bool
    error: Optional[Literal[
        "bad_key", "too_large", "quota_exceeded", "untrusted_source"
    ]] = None
    detail: str = ""                           # the model reads this and can recover
# --8<-- [end:memory-entry]

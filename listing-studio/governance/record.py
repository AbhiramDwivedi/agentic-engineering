"""The governance record: one append-only JSON line per consequential action.

Your code writes the record, never the model. Each line says who acted, what
happened, why, which model and prompt version produced the output, and whether
a human overrode it. Records are never edited: a correction is a new line that
points at the one it corrects.
"""
from __future__ import annotations

# --8<-- [start:governance-imports]
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel
# --8<-- [end:governance-imports]


# --8<-- [start:governance-record]
class DecisionRecord(BaseModel):
    record_id: str
    at: str                       # UTC timestamp, set by the writer
    actor: str                    # who acted: an agent name or a human id
    action: str                   # what happened, e.g. "publish_listing"
    reason: str                   # why, in the actor's words
    model: str                    # model version that produced the output
    prompt_version: str           # which prompt text was live
    overridden_by: Optional[str] = None   # human who changed the outcome
    corrects: Optional[str] = None        # record_id this line supersedes
# --8<-- [end:governance-record]


# --8<-- [start:governance-writer]
class RecordWriter:
    """Append-only: the file is opened in append mode and never rewritten."""

    def __init__(self, path: Path, now: Callable[[], datetime] | None = None):
        self.path = Path(path)
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._count = sum(1 for _ in self.path.open()) if self.path.exists() else 0

    def write(self, **fields) -> DecisionRecord:
        self._count += 1
        rec = DecisionRecord(
            record_id=f"rec-{self._count:06d}",
            at=self._now().isoformat(),
            **fields,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(rec.model_dump_json() + "\n")
        return rec

    def correct(self, record_id: str, **fields) -> DecisionRecord:
        # A correction is a new line; the original stays exactly as written.
        return self.write(corrects=record_id, **fields)

    def read_all(self) -> list[DecisionRecord]:
        with self.path.open(encoding="utf-8") as f:
            return [DecisionRecord(**json.loads(line)) for line in f]
# --8<-- [end:governance-writer]

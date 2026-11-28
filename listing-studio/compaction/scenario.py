"""The Listing Studio session the chapter runs: one long supplier-row ingest."""
from __future__ import annotations

from .probe import Question
from .window import Message

PIN = "Drafts only: never publish a listing; every change is saved as a draft."
DECISION = ("Supplier confirmed height_range_in for NV-ALDSWORTH-DM is 27-48. "
            "Use that, not the spec sheet's 25-50.")
QUESTIONS = [
    Question(ask="Are we allowed to publish?", expect="drafts only"),
    Question(ask="What height range do we use for the Aldsworth desk?", expect="27-48"),
]


def _row(i: int) -> list[Message]:
    feed = " ".join(f"field{j}=value{i}-{j}" for j in range(1, 13))
    return [Message(role="assistant", content=f"Reading supplier row {i}."),
            Message(role="tool", content=f"row {i}: {feed}", result_id=f"r{i}")]


def build_session(rows: int = 12) -> list[Message]:
    """A pinned rule, a mid-run decision held only in a message, then supplier rows."""
    h = [Message(role="user", content=PIN, pinned=True)]
    for i in range(1, 4):
        h += _row(i)
    h.append(Message(role="user", content=DECISION))
    for i in range(4, rows + 1):
        h += _row(i)
    return h

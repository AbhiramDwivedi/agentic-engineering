"""The compaction ladder, lightest rung first: clear old tool results, trim
long messages, then summarize. Each rung runs only if the window is still over
budget. Pure functions over a list of messages; the archive is a plain dict."""
from __future__ import annotations

from typing import Callable

from .window import Message, estimate_tokens

REFUSALS = ("i can't", "i cannot", "i'm sorry")


# --8<-- [start:compaction-mask]
def mask_observations(history: list[Message], keep_last: int, archive: dict) -> list[Message]:
    """Rung 1: replace old tool results with a placeholder that carries an archive key."""
    tool_idx = [i for i, m in enumerate(history) if m.role == "tool" and not m.pinned]
    old = set(tool_idx[: max(len(tool_idx) - keep_last, 0)])
    out = []
    for i, m in enumerate(history):
        if i in old:
            archive[m.result_id] = m.content  # the full text stays recoverable by key
            m = m.model_copy(update={"content": f"[result masked; archive key {m.result_id}]"})
        out.append(m)
    return out
# --8<-- [end:compaction-mask]


def trim_long(history: list[Message], max_words: int) -> list[Message]:
    """Rung 2: cut any unpinned message longer than max_words."""
    out = []
    for m in history:
        words = m.content.split()
        if not m.pinned and len(words) > max_words:
            m = m.model_copy(update={"content": " ".join(words[:max_words]) + " [trimmed]"})
        out.append(m)
    return out


def fake_summarizer(messages: list[Message]) -> str:
    """Scripted stand-in for a model: deterministic, and like a real summary it keeps
    the gist and drops specifics (exact values, reasons, instructions given once)."""
    return f"Summary of {len(messages)} earlier messages: supplier rows were ingested and checked."


def _usable(summary: str | None) -> bool:
    return bool(summary and summary.strip()) and not summary.strip().lower().startswith(REFUSALS)


# --8<-- [start:compaction-compact]
def compact(history: list[Message], summarize: Callable[[list[Message]], str],
            budget_tokens: int, keep_last: int, archive: dict) -> list[Message]:
    """Rung 3: summarize the middle. Triggers on the token estimate, archives the
    full history first, keeps pins and the last keep_last messages, and returns the
    history unchanged if the summarizer raises, returns nothing or refuses."""
    if estimate_tokens(history) <= budget_tokens:
        return history
    archive["history"] = [m.model_dump() for m in history]
    recent = history[-keep_last:]
    older = history[:-keep_last]
    try:
        summary = summarize([m for m in older if not m.pinned])
    except Exception:
        return history  # a failed summary must not cost the window
    if not _usable(summary):
        return history  # empty or refused: keep what we have
    pins = [m for m in older if m.pinned]
    return pins + [Message(role="assistant", content=summary)] + recent
# --8<-- [end:compaction-compact]


def shrink(history: list[Message], summarize: Callable[[list[Message]], str],
           budget_tokens: int, keep_last: int, archive: dict, max_words: int = 40) -> list[Message]:
    """The ladder: stop at the first rung that gets under budget."""
    rungs = (lambda h: mask_observations(h, keep_last, archive),
             lambda h: trim_long(h, max_words),
             lambda h: compact(h, summarize, budget_tokens, keep_last, archive))
    for rung in rungs:
        if estimate_tokens(history) <= budget_tokens:
            break
        history = rung(history)
    return history

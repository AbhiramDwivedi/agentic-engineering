"""The editing pass: one call over the assembled text, diffed against its input."""
from __future__ import annotations

import re
from collections import Counter
from typing import Callable


# --8<-- [start:assembly-polish]
def _facts(text: str) -> Counter:
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    ids = re.findall(r"\[src:[^\]]*\]", text)
    names = re.findall(r"\b[A-Z][A-Za-z0-9-]{2,}\b", text)
    return Counter(numbers + ids + names)


def fidelity_diff(before: str, after: str) -> list[str]:
    """What the pass added or dropped: numbers, source ids, capitalized names."""
    a, b = _facts(before), _facts(after)
    return [f"dropped {k!r}" for k in a - b] + [f"added {k!r}" for k in b - a]


def polish_checked(edit_fn: Callable[[str], str], text: str) -> tuple[str, list[str]]:
    """One editing pass, no retry loop (retrying until the diff is clean
    would be 3.7's outer loop). On a failed call or a changed fact, keep
    the unpolished text."""
    try:
        edited = edit_fn(text)
    except Exception as e:  # cut off, refused, provider error
        return text, [f"editing pass failed: {e}"]
    problems = fidelity_diff(text, edited)
    return (text if problems else edited), problems
# --8<-- [end:assembly-polish]

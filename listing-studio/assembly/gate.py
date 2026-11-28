"""The publish gate: code checks, then a person approves."""
from __future__ import annotations

import re

from .template import Assembled


# --8<-- [start:assembly-gate]
LEAK_MARKERS = ("{{", "TODO", "<tool_call", "[PLACEHOLDER")


def cited_ids(text: str) -> set[str]:
    groups = re.findall(r"\[src:([^\]]*)\]", text)
    return {i for g in groups for i in g.split(",") if i}


def publish_gate(
    assembled: Assembled, final: str, known_ids: set[str], max_chars: int = 6000
) -> list[str]:
    """Return the reasons not to publish; empty means ready for a person to
    approve. The approval itself is 4.3's human gate, not this function."""
    reasons = [f"required section missing: {s}" for s in assembled.blocked]
    reasons += [f"leaked text: {m}" for m in LEAK_MARKERS if m in final]
    reasons += [f"unknown source id: {i}" for i in sorted(cited_ids(final) - known_ids)]
    if not 200 <= len(final) <= max_chars:
        reasons.append(f"length out of bounds: {len(final)}")
    return reasons
# --8<-- [end:assembly-gate]

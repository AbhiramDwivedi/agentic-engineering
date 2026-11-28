"""Cross-section checks done in code: contradictions and repeats."""
from __future__ import annotations

import re
from dataclasses import dataclass


# --8<-- [start:assembly-checks]
@dataclass
class Conflict:
    key: str
    values: dict[str, str]    # section_id -> the value that section states
    winner: str | None        # canonical section's value, or None: escalate


def find_conflicts(
    tables: dict[str, dict[str, str]], canonical: str = "specs"
) -> list[Conflict]:
    """Compare per-section fact tables. Never average a disagreement away:
    the canonical section wins, or the conflict is surfaced unresolved."""
    by_key: dict[str, dict[str, str]] = {}
    for section, facts in tables.items():
        for key, value in facts.items():
            by_key.setdefault(key, {})[section] = value
    return [
        Conflict(key, values, values.get(canonical))
        for key, values in by_key.items()
        if len(set(values.values())) > 1
    ]


def _grams(body: str, n: int) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9']+", body.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def find_repeats(sections: dict[str, str], n: int = 5) -> list[tuple[str, str]]:
    """Pairs of sections sharing a run of n words: the same selling point twice."""
    grams = {sid: _grams(body, n) for sid, body in sections.items()}
    ids = sorted(grams)
    return [
        (a, b) for i, a in enumerate(ids) for b in ids[i + 1 :] if grams[a] & grams[b]
    ]
# --8<-- [end:assembly-checks]

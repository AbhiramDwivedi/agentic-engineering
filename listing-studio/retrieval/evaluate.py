"""recall@k over the labeled fixture: did the right chunk make the top k?"""
from __future__ import annotations

from typing import Callable

from .corpus import LABELED_QUERIES


# --8<-- [start:retrieval-recall]
def recall_at_k(retrieve: Callable[[str], list[str]], k: int = 3) -> float:
    """Share of labeled queries whose answering chunk appears in the top k."""
    hits = sum(1 for query, want in LABELED_QUERIES if want in retrieve(query)[:k])
    return hits / len(LABELED_QUERIES)
# --8<-- [end:retrieval-recall]

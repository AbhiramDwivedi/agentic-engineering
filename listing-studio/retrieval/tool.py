"""Retrieval wrapped as a tool: the model decides when to call it."""
from __future__ import annotations

from pydantic import BaseModel

from .corpus import CORPUS, Chunk
from .scoring import dense_scores, lexical_scores, rank, rrf


# --8<-- [start:retrieval-tool]
class Retrieval(BaseModel):
    query: str
    found: bool
    chunks: list[Chunk]
    note: str = ""


def search_docs(query: str, k: int = 3) -> Retrieval:
    """Hybrid search over the helpdesk docs. Empty is a result, not a guess."""
    ids = rrf([rank(lexical_scores(query, CORPUS)), rank(dense_scores(query, CORPUS))])[:k]
    by_id = {c.id: c for c in CORPUS}
    if not ids:
        return Retrieval(query=query, found=False, chunks=[],
                         note="No policy matches. Say so; do not answer from memory.")
    return Retrieval(query=query, found=True, chunks=[by_id[i] for i in ids])
# --8<-- [end:retrieval-tool]

"""Toy lexical and dense scorers, and reciprocal rank fusion. Pure Python."""
from __future__ import annotations

# --8<-- [start:retrieval-scorers]
import math
import re
from collections import Counter

from .corpus import Chunk

# Stand-in for an embedding model: words that mean the same thing share a concept.
CONCEPTS = {
    "refund": "money", "money": "money", "back": "money", "subscription": "money",
    "plan": "money", "fee": "money",
    "invoice": "invoice", "invoices": "invoice", "copy": "invoice",
    "rejected": "reject", "turned": "reject", "down": "reject",
    "photo": "image", "photos": "image", "pixels": "image", "size": "image",
    "password": "login", "login": "login", "credentials": "login", "forgot": "login",
    "teammate": "team", "colleague": "team", "invite": "team", "access": "team",
}

STOPWORDS = {
    "a", "an", "the", "of", "to", "my", "i", "is", "on", "in", "and", "for", "can",
    "do", "how", "was", "why", "where", "get", "from", "with", "or", "at", "your", "you",
}


def tokens(text: str) -> list[str]:
    """Lowercase words and numbers, stopwords dropped."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def lexical_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    """Exact-word overlap: precise on literal terms, blind to paraphrase."""
    q = set(tokens(query))
    return {c.id: float(len(q & set(tokens(c.text)))) for c in chunks}


def _vec(text: str) -> Counter:
    return Counter(CONCEPTS[t] for t in tokens(text) if t in CONCEPTS)


def dense_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    """Cosine over concept counts: finds paraphrase, blurs exact terms."""
    q = _vec(query)
    out = {}
    for c in chunks:
        d = _vec(c.text)
        dot = sum(q[k] * d[k] for k in q)
        norm = math.sqrt(sum(v * v for v in q.values())) * math.sqrt(sum(v * v for v in d.values()))
        out[c.id] = dot / norm if norm else 0.0
    return out
# --8<-- [end:retrieval-scorers]


# --8<-- [start:retrieval-rrf]
def rank(scores: dict[str, float]) -> list[str]:
    """Ids best-first; a zero score means no match and is dropped."""
    return [i for i, s in sorted(scores.items(), key=lambda kv: -kv[1]) if s > 0]


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal rank fusion: each list votes 1/(k + rank). Scores never mix."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for position, chunk_id in enumerate(ranking, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (k + position)
    return sorted(fused, key=lambda i: -fused[i])
# --8<-- [end:retrieval-rrf]

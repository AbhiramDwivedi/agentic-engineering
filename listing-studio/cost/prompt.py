"""Prompt builder: static content first, dynamic content last.

Provider prompt caches match on the exact prefix of a request, so anything
that varies per call (a timestamp, the listing being edited) must come after
everything that does not.
"""
from __future__ import annotations

# --8<-- [start:cost-prefix]
import hashlib

STATIC_RULES = (
    "You write product listings for Listing Studio.\n"
    "Follow the brand style guide. Never invent specifications.\n"
)


def build_prompt(catalog_context: str, listing: str, now: str) -> str:
    """Static parts first, per-call parts last, so the prefix stays identical."""
    static = STATIC_RULES + catalog_context
    dynamic = f"Current time: {now}\nListing to improve:\n{listing}"
    return static + "\n---\n" + dynamic


def prefix_hash(prompt: str) -> str:
    """Hash of everything before the dynamic section: the cacheable prefix."""
    prefix = prompt.split("\n---\n", 1)[0]
    return hashlib.sha256(prefix.encode()).hexdigest()[:12]
# --8<-- [end:cost-prefix]

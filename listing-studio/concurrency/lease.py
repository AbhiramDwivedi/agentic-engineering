"""An in-memory lease with a fencing token, and a store that rejects stale writers."""
from __future__ import annotations

# --8<-- [start:lease-fencing]
from dataclasses import dataclass


@dataclass
class Lease:
    holder: str
    token: int  # monotonically increasing; larger means newer
    expires_at: float


class LeaseManager:
    def __init__(self, ttl: float = 30.0):
        self.ttl = ttl
        self._last_token = 0
        self._current: Lease | None = None

    def acquire(self, holder: str, now: float) -> Lease | None:
        if self._current and self._current.expires_at > now:
            return None  # someone else still holds it
        self._last_token += 1
        self._current = Lease(holder, self._last_token, now + self.ttl)
        return self._current


class PriceStore:
    """Rejects any write whose token is below the highest token seen."""

    def __init__(self):
        self.prices: dict[str, int] = {}
        self.highest_token = 0

    def write(self, sku: str, cents: int, token: int) -> bool:
        if token < self.highest_token:
            return False  # a newer holder has already written
        self.highest_token = token
        self.prices[sku] = cents
        return True
# --8<-- [end:lease-fencing]

"""A write tool whose replay does not repeat the effect."""
from __future__ import annotations


class PriceStore:
    """Stand-in for the Repricer's price_cents write; counts real effects."""

    def __init__(self):
        self.prices: dict[str, int] = {}
        self.writes = 0

    def set_price(self, supplier_sku: str, price_cents: int) -> None:
        self.prices[supplier_sku] = price_cents
        self.writes += 1


# --8<-- [start:idempotent]
class IdempotentTool:
    def __init__(self, store: PriceStore):
        self.store = store
        self.seen: dict[str, str] = {}  # key -> first result, replayed after

    def set_price(self, run_id: str, step: int, sku: str, price_cents: int) -> str:
        key = f"{run_id}:{step}"  # same run and step, same key, on every replay
        if key in self.seen:
            return self.seen[key]  # the write already ran; return its result
        self.store.set_price(sku, price_cents)
        self.seen[key] = f"{sku} set to {price_cents}"
        return self.seen[key]
# --8<-- [end:idempotent]

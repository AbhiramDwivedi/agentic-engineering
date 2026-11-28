"""The Repricer's deterministic verifier: MAP and margin, no model involved."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceRules:
    sku: str
    map_cents: int       # minimum advertised price: never go below it
    cost_cents: int
    min_margin: float    # e.g. 0.20 = at least 20% of the price is margin


# --8<-- [start:outer-verifier]
@dataclass
class Verdict:
    ok: bool
    feedback: str | None = None  # structured failure, fed back into the next attempt


def verify_price(price_cents: int, rules: PriceRules) -> Verdict:
    """Pure function over pinned rules."""
    if price_cents < rules.map_cents:
        return Verdict(False, f"price {price_cents} is below MAP {rules.map_cents} "
                              f"for {rules.sku}; MAP is a hard floor.")
    margin = (price_cents - rules.cost_cents) / price_cents
    if margin < rules.min_margin:
        return Verdict(False, f"margin {margin:.0%} is under the {rules.min_margin:.0%} "
                              f"minimum at cost {rules.cost_cents}.")
    return Verdict(True)
# --8<-- [end:outer-verifier]

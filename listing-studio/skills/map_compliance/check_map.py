"""MAP-compliance check script bundled with the map-compliance skill.

Usage (called by the skill loader at Level 3):
    python check_map.py <supplier_sku> <proposed_price_cents>

Exits 0 and prints a JSON result on success.
Exits 1 and prints a JSON error on any failure.

The script's *output* (the JSON result) enters the model's context — not this
source code. That is the Level-3 contract: run a script, pass its stdout to
the model. The model never sees this file.

Business rules are hardcoded here for teaching clarity. In production they
come from a pricing-rules store keyed on SKU.
"""
from __future__ import annotations

import json
import sys


MAP_RULES: dict[str, dict] = {
    "NV-ALDSWORTH-DM": {
        "map_floor_cents": 39900,   # $399.00 MAP floor from Northvale Furnishings
        "cost_cents": 28000,         # $280.00 landed cost
        "margin_floor_pct": 0.20,    # 20 % gross-margin floor
    },
}


def main() -> None:
    if len(sys.argv) != 3:
        _fail("usage: check_map.py <supplier_sku> <proposed_price_cents>")

    supplier_sku = sys.argv[1]
    try:
        proposed_price_cents = int(sys.argv[2])
    except ValueError:
        _fail(f"proposed_price_cents must be an integer, got: {sys.argv[2]!r}")

    rules = MAP_RULES.get(supplier_sku)
    if rules is None:
        _fail(f"no MAP rules found for SKU {supplier_sku!r}")

    map_floor = rules["map_floor_cents"]
    cost = rules["cost_cents"]
    margin_floor_pct = rules["margin_floor_pct"]
    margin_floor_cents = int(cost / (1 - margin_floor_pct))

    if proposed_price_cents < map_floor:
        _fail(
            f"price {proposed_price_cents} undercuts MAP floor {map_floor}; "
            f"raise to at least {map_floor}"
        )

    if proposed_price_cents < margin_floor_cents:
        _fail(
            f"price {proposed_price_cents} does not meet the "
            f"{margin_floor_pct:.0%} margin floor (minimum {margin_floor_cents}); "
            f"raise to at least {margin_floor_cents}"
        )

    print(json.dumps({
        "ok": True,
        "supplier_sku": supplier_sku,
        "proposed_price_cents": proposed_price_cents,
        "map_floor_cents": map_floor,
        "margin_floor_cents": margin_floor_cents,
        "margin_pct": round(
            (proposed_price_cents - cost) / proposed_price_cents, 4
        ),
    }))
    sys.exit(0)


def _fail(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}))
    sys.exit(1)


if __name__ == "__main__":
    main()

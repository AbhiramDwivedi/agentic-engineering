"""A small golden set from the Listing Studio carrier.

Every case is tagged with the failure it came from: the point of a golden
set is that each row is a real way the pipeline went wrong once, not a
case somebody imagined.
"""
from __future__ import annotations

from dataclasses import dataclass


# --8<-- [start:evals-cases]
@dataclass(frozen=True)
class EvalCase:
    id: str
    failure_mode: str          # the failure this case came from
    feed: dict                 # the raw supplier feed row
    required: dict             # attributes the listing must carry, and their values
    forbidden: tuple = ()      # attributes the listing must NOT invent


DESK = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "height_range_in": "25-50",
    "weight_capacity_lbs": 250,
    "color": "walnut",
    "price_cents": 39900,
    "map_enforced": True,
}

GOLDEN = [
    EvalCase("desk-baseline", "none (control)", DESK,
             {"height_range_in": "25-50", "weight_capacity_lbs": 250}),
    EvalCase("desk-weight-overstated", "overstated weight capacity",
             {**DESK, "weight_capacity_lbs": "250 (static 300)"},
             {"weight_capacity_lbs": 250}),
    EvalCase("desk-below-map", "price below MAP",
             {**DESK, "note": "launch discount 15%"},
             {"price_cents": 39900, "map_enforced": True}),
    EvalCase("desk-prop65-missing", "missing compliance warning",
             DESK, {"prop65_warning": True}),
    EvalCase("desk-color-typo", "unnormalised attribute",
             {**DESK, "color": "Wlnut"}, {"color": "walnut"}),
    EvalCase("bunk-guardrail", "missing entrapment warning",
             {"supplier_sku": "NV-BUNKBED-01", "guardrail_height_in": 5},
             {"entrapment_warning": True}),
    EvalCase("bunk-weight-in-title", "attribute buried in free text",
             {"supplier_sku": "NV-BUNKBED-01", "title": "Bunk bed, 200 lb per bunk"},
             {"weight_capacity_lbs": 200}),
    EvalCase("phonecase-do-nothing", "invented compliance on a plain product",
             {"supplier_sku": "NV-PHONECASE-01", "color": "black"},
             {}, forbidden=("prop65_warning", "map_enforced", "assembly_required")),
]
# --8<-- [end:evals-cases]

from .models import PriceCheckRequest, PriceVerdict, PricingRule

# Aldsworth dual-motor sit-stand desk, supplier Northvale Furnishings.
ALDSWORTH_RULE = PricingRule(
    supplier_sku="NV-ALDSWORTH-DM",
    cost_cents=28000,
    map_floor_cents=39900,  # MAP: must not advertise below $399.00
    min_margin_pct=0.25,
)
RULES = {ALDSWORTH_RULE.supplier_sku: ALDSWORTH_RULE}


# --8<-- [start:tool]
def check_price(req: PriceCheckRequest) -> PriceVerdict:
    """A typed tool. A deterministic guardrail your code owns, not the model.

    The model decides whether to call this, and with what price. The verdict
    is something it cannot argue with: math, not opinion.
    """
    rule = RULES[req.supplier_sku]
    margin_floor = round(rule.cost_cents / (1 - rule.min_margin_pct))
    floor = max(rule.map_floor_cents, margin_floor)
    ok = req.proposed_price_cents >= floor
    reason = (
        "clears MAP and margin floor"
        if ok
        else (
            f"below binding floor of {floor} cents "
            f"(MAP {rule.map_floor_cents}, margin {margin_floor})"
        )
    )
    return PriceVerdict(
        ok=ok,
        proposed_price_cents=req.proposed_price_cents,
        map_floor_cents=rule.map_floor_cents,
        margin_floor_cents=margin_floor,
        floor_cents=floor,
        reason=reason,
    )
# --8<-- [end:tool]

from pydantic import BaseModel, Field


# --8<-- [start:contract]
class PriceCheckRequest(BaseModel):
    """What the model fills in when it decides to call the tool."""

    supplier_sku: str
    proposed_price_cents: int = Field(gt=0)


class PriceVerdict(BaseModel):
    """The structured verdict your code hands back to the model."""

    ok: bool
    proposed_price_cents: int
    map_floor_cents: int  # minimum advertised price
    margin_floor_cents: int  # lowest price that clears the margin rule
    floor_cents: int  # max(map, margin): the binding floor
    reason: str
# --8<-- [end:contract]


class PricingRule(BaseModel):
    """Per-SKU rules. In production this is a DB row; here it is a fixture."""

    supplier_sku: str
    cost_cents: int
    map_floor_cents: int
    min_margin_pct: float

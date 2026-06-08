# --8<-- [start:schema]
# What you describe to the model. It reads this, never your code, so the
# description and the schema have to be good. The same shape works on every
# major API.
PRICE_CHECK_TOOL = {
    "name": "check_price",
    "description": (
        "Check a proposed price for a product against the supplier's minimum "
        "advertised price (MAP) and margin floor. Call this before quoting a price."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
            "proposed_price_cents": {"type": "integer"},
        },
        "required": ["supplier_sku", "proposed_price_cents"],
        "additionalProperties": False,
    },
}
# --8<-- [end:schema]


# --8<-- [start:tool]
# The tool itself: plain code the model cannot argue with. The floor is
# hardcoded here for one desk; in production it is a lookup in your pricing rules.
def check_price(supplier_sku: str, proposed_price_cents: int) -> dict:
    floor_cents = 39900  # $399.00 MAP for the Aldsworth desk
    ok = proposed_price_cents >= floor_cents
    return {"ok": ok, "floor_cents": floor_cents}
# --8<-- [end:tool]

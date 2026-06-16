# --8<-- [start:schema_responses]
# What you describe to the model. It reads this, never your code, so the
# description and the schema have to be good. This is the OpenAI Responses
# shape; the Anthropic Messages API uses the same idea under `input_schema`.
PRICE_CHECK_TOOL = {
    "type": "function",
    "name": "check_price",
    "description": (
        "Check a proposed price for a product against the supplier's minimum "
        "advertised price (MAP) and margin floor. Call this before quoting a price."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
            "proposed_price_cents": {"type": "integer"},
        },
        "required": ["supplier_sku", "proposed_price_cents"],
        "additionalProperties": False,
    },
}
# --8<-- [end:schema_responses]

# --8<-- [start:schema_anthropic]
# The same tool, Anthropic Messages API shape: `input_schema` instead of
# `parameters`, and no top-level `type`.
PRICE_CHECK_TOOL_ANTHROPIC = {
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
# --8<-- [end:schema_anthropic]


# The tool itself: plain code the model cannot argue with. The floor is
# hardcoded here for one desk; in production it is a lookup in your pricing rules.
def check_price(supplier_sku: str, proposed_price_cents: int) -> dict:
    floor_cents = 39900  # $399.00 MAP for the Aldsworth desk
    ok = proposed_price_cents >= floor_cents
    return {"ok": ok, "floor_cents": floor_cents}


# A second tool (Responses shape), used by multi_tool_responses.py.
# Hardcoded for the illustration; in production this hits your market-data feed.
COMPETITOR_PRICE_TOOL = {
    "type": "function",
    "name": "get_competitor_prices",
    "description": (
        "Fetch the current competitor prices for a product, in cents, "
        "from the market-data feed."
    ),
    "parameters": {
        "type": "object",
        "properties": {"supplier_sku": {"type": "string"}},
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}

# The same second tool, Anthropic Messages API shape.
COMPETITOR_PRICE_TOOL_ANTHROPIC = {
    "name": "get_competitor_prices",
    "description": (
        "Fetch the current competitor prices for a product, in cents, "
        "from the market-data feed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"supplier_sku": {"type": "string"}},
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}


def get_competitor_prices(supplier_sku: str) -> dict:
    return {"prices_cents": [41900, 44500, 39900]}

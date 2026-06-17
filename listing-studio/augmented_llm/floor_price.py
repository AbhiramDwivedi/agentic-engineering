"""The MAP floor-price lookup: the pure function at the heart of the unit.

No third-party imports: this module is directly importable in tests without
an API key or SDK.  The illustration files (augmented_llm_langgraph.py, etc.)
import from here and wrap it in whichever SDK shape they need.

The JSON-schema tool descriptions live here too, mirroring the convention in
pricing/tools.py.
"""

# ---------------------------------------------------------------------------
# The tool body — plain Python, runs in your process, not inside the model.
# ---------------------------------------------------------------------------

def lookup_floor_price(supplier_sku: str) -> dict:
    """Return the supplier's minimum advertised price (MAP) floor in cents.

    In production this is a lookup in your pricing-rules store keyed on SKU.
    Here it is hardcoded to the Aldsworth desk illustration.
    """
    # $399.00 MAP for the Aldsworth dual-motor sit-stand desk.
    return {"floor_cents": 39900}


# ---------------------------------------------------------------------------
# Tool schema — LangGraph shape (auto-generated; shown for reference only).
# ---------------------------------------------------------------------------

# LangGraph generates this from type hints + docstring via @tool(parse_docstring=True).
# The schema below is the hand-written equivalent, kept here for cross-reference.

# ---------------------------------------------------------------------------
# Tool schema — OpenAI Responses API shape.
# ---------------------------------------------------------------------------

FLOOR_PRICE_TOOL_RESPONSES = {
    "type": "function",
    "name": "lookup_floor_price",
    "description": (
        "Look up the supplier's minimum advertised price (MAP) floor for a "
        "product. Call this before quoting a price."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
        },
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}

# ---------------------------------------------------------------------------
# Tool schema — Anthropic Messages API shape.
# ---------------------------------------------------------------------------

FLOOR_PRICE_TOOL_ANTHROPIC = {
    "name": "lookup_floor_price",
    "description": (
        "Look up the supplier's minimum advertised price (MAP) floor for a "
        "product. Call this before quoting a price."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
        },
        "required": ["supplier_sku"],
        "additionalProperties": False,
    },
}

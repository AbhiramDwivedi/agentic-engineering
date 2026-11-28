"""The gate: code decides which price changes need a person. Pure function."""
from pricing.tools import check_price

# --8<-- [start:hitl-gate]
AUTO_FROM_CENTS = 42900  # at or above this the change applies without a person


def gate_policy(action: str, args: dict) -> str:
    """Return "auto", "ask" or "deny". Deny is checked first and nothing below
    can widen it: a person is never asked to approve a price the floor refuses."""
    if action != "set_price":
        return "ask"  # an action we have no rule for goes to a person
    price = args["proposed_price_cents"]
    if not check_price(args["supplier_sku"], price)["ok"]:
        return "deny"  # below the 39900 MAP floor: code refuses, no human in the path
    return "auto" if price >= AUTO_FROM_CENTS else "ask"
# --8<-- [end:hitl-gate]

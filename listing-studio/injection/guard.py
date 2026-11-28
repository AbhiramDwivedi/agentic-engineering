"""Code-enforced action guard: what the session may change and send after it
has read untrusted text. Reuses 2.1's check_price for the MAP floor."""
from __future__ import annotations

from pricing.tools import check_price

# --8<-- [start:injection-guard]
EGRESS_ALLOWED_FIELDS = {"title", "description", "width_in", "depth_in", "price_cents"}


def guard_action(action: dict, untrusted_read: bool) -> dict:
    """Runs in code, after the model chose and before anything executes.
    Returns the action, or a structured refusal the loop can read."""
    kind = action.get("tool")
    if kind == "set_price" and untrusted_read:
        check = check_price("NV-ALDSWORTH-DM", action["price_cents"])
        if not check["ok"]:
            return {"ok": False, "error": "refused: price below MAP",
                    "floor_cents": check["floor_cents"]}
    if kind in ("publish", "send_email"):
        extra = sorted(set(action.get("payload", {})) - EGRESS_ALLOWED_FIELDS)
        if extra:
            return {"ok": False, "error": "refused: fields not allowed to leave",
                    "fields": extra}
    return {"ok": True, "action": action}
# --8<-- [end:injection-guard]

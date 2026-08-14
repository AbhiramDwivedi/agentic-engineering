"""The gate between step one and step two: category_path must be real."""
from __future__ import annotations

from dataclasses import dataclass

from .schemas import CategoryDecision

# In production this comes from the catalog taxonomy service, not a literal
# set. A handful of real Listing Studio category paths is enough here.
TAXONOMY = {
    "office/desks/standing-desks",
    "office/desks/fixed-height-desks",
    "bedroom/kids/bunk-beds",
}


# --8<-- [start:chain-gate]
@dataclass
class GateResult:
    ok: bool
    error: str | None = None  # structured message for the re-ask prompt if not ok


def validate_category(decision: CategoryDecision) -> GateResult:
    """category_path must be a real node in the catalog taxonomy."""
    if decision.category_path not in TAXONOMY:
        return GateResult(
            ok=False,
            error=(
                f"category_path {decision.category_path!r} is not in the "
                f"catalog taxonomy. Choose one of: {sorted(TAXONOMY)}."
            ),
        )
    return GateResult(ok=True)
# --8<-- [end:chain-gate]

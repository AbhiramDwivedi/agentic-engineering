"""Semantic validation for PricingDecision: valid shape is not valid content.

A schema-valid PricingDecision can still undercut the MAP floor, squeeze margin
below the required floor, or carry an out-of-range confidence score. Your code
catches those. The schema guarantees the shape; this module guarantees the meaning.

Also contains the bounded re-ask loop: when a parse or semantic failure occurs,
hand the model a structured, recoverable error message so it can self-correct on
retry, instead of raising a raw exception that ends the pipeline run.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .schema import PricingDecision


# ---------------------------------------------------------------------------
# Business rules for the Aldsworth desk.
# In production these come from your pricing-rules store, keyed on SKU.
# ---------------------------------------------------------------------------

MAP_FLOOR_CENTS = 39900       # $399.00 minimum advertised price
COST_CENTS = 28000            # $280.00 landed cost (for margin floor)
MARGIN_FLOOR_PCT = 0.20       # 20 % gross-margin floor
CONFIDENCE_FLOOR = 0.60       # reject decisions the model marks as uncertain


# --8<-- [start:pricing-validate]
@dataclass
class ValidationResult:
    ok: bool
    error: str | None = None  # structured message for the re-ask prompt if not ok


def validate_pricing_decision(
    decision: PricingDecision,
    map_floor_cents: int = MAP_FLOOR_CENTS,
    cost_cents: int = COST_CENTS,
    margin_floor_pct: float = MARGIN_FLOOR_PCT,
) -> ValidationResult:
    """Check a schema-valid PricingDecision for semantic correctness.

    Valid shape is not valid content. The schema guarantees the object parses;
    this function guarantees the price is within policy. Three checks:

    1. MAP floor — the price must not undercut the supplier's minimum advertised
       price or the listing is in breach of contract.
    2. Margin floor — the price must cover cost plus the required gross margin
       so the listing is profitable.
    3. Confidence floor — decisions the model marks as uncertain are held for
       human review rather than published automatically.
    """
    margin_floor_cents = int(cost_cents / (1 - margin_floor_pct))

    if decision.price_cents < map_floor_cents:
        return ValidationResult(
            ok=False,
            error=(
                f"price_cents {decision.price_cents} undercuts the MAP floor "
                f"({map_floor_cents}). Raise the price to at least {map_floor_cents}."
            ),
        )

    if decision.price_cents < margin_floor_cents:
        return ValidationResult(
            ok=False,
            error=(
                f"price_cents {decision.price_cents} does not meet the "
                f"{margin_floor_pct:.0%} gross-margin floor "
                f"(minimum {margin_floor_cents} given cost {cost_cents}). "
                f"Raise the price to at least {margin_floor_cents}."
            ),
        )

    if decision.confidence < CONFIDENCE_FLOOR:
        return ValidationResult(
            ok=False,
            error=(
                f"confidence {decision.confidence:.2f} is below the "
                f"floor ({CONFIDENCE_FLOOR}). Revise reasoning or flag for review."
            ),
        )

    return ValidationResult(ok=True)
# --8<-- [end:pricing-validate]


# --8<-- [start:pricing-reask]
def price_with_reask(
    call_fn: Any,          # callable(messages) -> PricingDecision | None
    messages: list[dict],
    max_retries: int = 3,  # loop cap — a stuck model fails loudly, not silently
) -> PricingDecision:
    """Bounded re-ask loop: parse + semantic validation, structured error on failure.

    On a parse failure or a MAP/margin/confidence violation, this function hands
    the model a structured, human-readable error message so it can self-correct on
    the next attempt. It does not raise a raw exception — that would end the run.
    Instead it appends the error as a user turn and tries again, up to max_retries.

    call_fn is the seam the provider variants inject (LangGraph / Responses /
    Anthropic). It receives the current message list and returns a PricingDecision
    on success, or None / raises pydantic.ValidationError on a parse failure.
    """
    from pydantic import ValidationError

    current_messages = list(messages)
    for attempt in range(1, max_retries + 1):
        try:
            decision = call_fn(current_messages)
        except (ValidationError, Exception) as exc:
            # Parse failure: the object did not fit the schema. Build a structured
            # error the model can act on, not a raw traceback.
            if attempt >= max_retries:
                raise RuntimeError(
                    f"structured-output call failed after {max_retries} attempts"
                ) from exc
            current_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Your previous response did not parse correctly: {exc}. "
                        "Please produce a valid PricingDecision JSON object."
                    ),
                }
            )
            continue

        result = validate_pricing_decision(decision)
        if result.ok:
            return decision

        # Semantic failure: the object parsed but violated policy. Feed the
        # structured error back so the model can self-correct on the next turn.
        if attempt >= max_retries:
            raise RuntimeError(
                f"pricing decision failed validation after {max_retries} attempts: "
                f"{result.error}"
            )
        current_messages.append(
            {"role": "user", "content": f"Invalid pricing decision: {result.error}"}
        )

    # Unreachable, but makes the type-checker happy.
    raise RuntimeError("price_with_reask exhausted retries")
# --8<-- [end:pricing-reask]

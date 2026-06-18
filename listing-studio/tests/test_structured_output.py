"""Tests for the structured-output chapter companion code.

All tests are offline: no API key, no network call.

- The PricingDecision schema and validate_pricing_decision logic are imported
  directly (no third-party deps beyond pydantic, which is pure Python).
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API keys).
- The price_with_reask loop is tested with a stub call_fn so it runs fully
  offline.
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from structured_output.schema import PricingDecision
from structured_output.validate import (
    CONFIDENCE_FLOOR,
    COST_CENTS,
    MAP_FLOOR_CENTS,
    validate_pricing_decision,
    price_with_reask,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "structured_output")

LANGGRAPH_FILE = os.path.join(PKG, "structured_output_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "structured_output_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "structured_output_example.py")


# ---------------------------------------------------------------------------
# PricingDecision schema (anchor: pricing-schema)
# ---------------------------------------------------------------------------

def test_pricing_decision_accepts_valid_object():
    """A well-formed decision parses without error."""
    d = PricingDecision(
        reasoning="MAP floor is $399; 5% above MAP gives ~$419.",
        price_cents=41900,
        currency="USD",
        confidence=0.92,
    )
    assert d.price_cents == 41900
    assert d.currency == "USD"


def test_pricing_decision_reasoning_field_is_first():
    """reasoning is the first field in model_fields — reason-then-format ordering."""
    fields = list(PricingDecision.model_fields.keys())
    assert fields[0] == "reasoning", (
        "reasoning must be the first field so the model writes free-text thought "
        "before committing to the typed payload (reason-then-format mitigation)."
    )


def test_pricing_decision_rejects_extra_fields():
    """extras='forbid' means a stray key is a ValidationError, not a silent drop."""
    with pytest.raises(ValidationError):
        PricingDecision(
            reasoning="fine",
            price_cents=41900,
            currency="USD",
            confidence=0.9,
            stray_key="not allowed",  # type: ignore[call-arg]
        )


def test_pricing_decision_rejects_wrong_type_for_price_cents():
    """price_cents must be an int; a float string is rejected."""
    with pytest.raises(ValidationError):
        PricingDecision(
            reasoning="fine",
            price_cents="not-an-int",  # type: ignore[arg-type]
            currency="USD",
            confidence=0.9,
        )


def test_pricing_decision_requires_all_fields():
    """All four fields are required; omitting any raises ValidationError."""
    with pytest.raises(ValidationError):
        PricingDecision(reasoning="fine", price_cents=41900, currency="USD")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Semantic validation (anchor: pricing-validate)
# Valid shape is not valid content.
# ---------------------------------------------------------------------------

def _good_decision(**overrides) -> PricingDecision:
    """Factory for a schema-valid, semantically correct decision."""
    defaults = dict(
        reasoning="Price above MAP and margin floor.",
        price_cents=41900,
        currency="USD",
        confidence=0.90,
    )
    defaults.update(overrides)
    return PricingDecision(**defaults)


def test_valid_decision_passes_validation():
    result = validate_pricing_decision(_good_decision())
    assert result.ok is True
    assert result.error is None


def test_sub_map_price_is_rejected():
    """A price below MAP is schema-valid but semantically wrong — caught here."""
    low_price = MAP_FLOOR_CENTS - 1  # e.g. $398.99 — undercuts the contract floor
    result = validate_pricing_decision(_good_decision(price_cents=low_price))
    assert result.ok is False
    assert "MAP floor" in result.error


def test_sub_margin_price_is_rejected():
    """A price above MAP but below the margin floor is also caught."""
    # MAP is $399 ($39900). Margin floor at 20% on $280 cost = $350 ($35000).
    # So MAP governs here; let's pick a cost/margin combo where margin floor > MAP.
    # cost=$300 ($30000), margin_floor=20% → floor=$375 ($37500), MAP=$399.
    # Use MAP=$300 override to isolate the margin check.
    result = validate_pricing_decision(
        _good_decision(price_cents=36000),  # $360 — above MAP=$300 but below margin
        map_floor_cents=30000,
        cost_cents=30000,  # $300 cost, 20% margin floor → need $37500
    )
    assert result.ok is False
    assert "margin" in result.error


def test_low_confidence_is_rejected():
    """A decision the model marks as uncertain is held back."""
    result = validate_pricing_decision(_good_decision(confidence=CONFIDENCE_FLOOR - 0.01))
    assert result.ok is False
    assert "confidence" in result.error


def test_exact_map_floor_is_accepted():
    """A price exactly at MAP is valid (the floor is a >=, not a > check)."""
    result = validate_pricing_decision(_good_decision(price_cents=MAP_FLOOR_CENTS))
    assert result.ok is True


# ---------------------------------------------------------------------------
# Re-ask loop (anchor: pricing-reask)
# Bounded re-ask: structured error, not raw exception.
# ---------------------------------------------------------------------------

def test_reask_loop_succeeds_on_first_try():
    """When call_fn returns a valid decision immediately, no retry needed."""
    expected = _good_decision()
    messages = [{"role": "user", "content": "price the desk"}]

    def call_fn(msgs):
        return expected

    result = price_with_reask(call_fn, messages, max_retries=3)
    assert result is expected


def test_reask_loop_recovers_after_map_violation():
    """A sub-MAP decision on attempt 1 is corrected on attempt 2."""
    call_count = 0
    messages = [{"role": "user", "content": "price the desk"}]

    def call_fn(msgs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First attempt: schema-valid but undercuts MAP — semantic failure.
            return _good_decision(price_cents=MAP_FLOOR_CENTS - 100)
        # Second attempt: corrected after seeing the structured error.
        return _good_decision(price_cents=MAP_FLOOR_CENTS + 1000)

    result = price_with_reask(call_fn, messages, max_retries=3)
    assert result.price_cents > MAP_FLOOR_CENTS
    assert call_count == 2


def test_reask_loop_appends_structured_error_on_failure():
    """After a semantic failure the error message is appended to messages."""
    appended: list[dict] = []
    messages = [{"role": "user", "content": "price the desk"}]

    def call_fn(msgs):
        # Record any appended messages after the first call.
        if len(msgs) > 1:
            appended.extend(msgs[1:])
            return _good_decision()  # succeed on retry
        return _good_decision(price_cents=MAP_FLOOR_CENTS - 100)

    price_with_reask(call_fn, messages, max_retries=3)
    assert appended, "expected the loop to append a structured error before retrying"
    assert any("MAP floor" in m["content"] for m in appended)


def test_reask_loop_raises_after_max_retries():
    """Persistent failures exhaust the retry budget and raise RuntimeError."""
    messages = [{"role": "user", "content": "price the desk"}]

    def call_fn(msgs):
        # Always returns a sub-MAP price — will never pass validation.
        return _good_decision(price_cents=MAP_FLOOR_CENTS - 500)

    with pytest.raises(RuntimeError, match="failed validation after"):
        price_with_reask(call_fn, messages, max_retries=3)


def test_reask_loop_handles_parse_error():
    """A ValidationError from call_fn is caught and leads to a re-ask, not a crash."""
    call_count = 0
    messages = [{"role": "user", "content": "price the desk"}]

    def call_fn(msgs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValidationError.from_exception_data(  # type: ignore[arg-type]
                title="PricingDecision",
                input_type="python",
                line_errors=[
                    {
                        "type": "missing",
                        "loc": ("price_cents",),
                        "msg": "Field required",
                        "input": {},
                        "url": "https://errors.pydantic.dev/2.0/v/missing",
                    }
                ],
            )
        return _good_decision()

    result = price_with_reask(call_fn, messages, max_retries=3)
    assert result.price_cents == 41900
    assert call_count == 2


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

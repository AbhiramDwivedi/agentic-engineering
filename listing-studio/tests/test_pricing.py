from pricing.agent import price_listing
from pricing.model_client import FakeModel, ToolCall
from pricing.models import PriceCheckRequest
from pricing.tools import ALDSWORTH_RULE, check_price

SKU = ALDSWORTH_RULE.supplier_sku  # "NV-ALDSWORTH-DM"


def _call(price: int) -> ToolCall:
    return ToolCall(
        name="check_price",
        request=PriceCheckRequest(supplier_sku=SKU, proposed_price_cents=price),
    )


# --- the guardrail (your code) ---


def test_guardrail_rejects_sub_map_price():
    # $389.00 is under the $399.00 MAP floor
    v = check_price(PriceCheckRequest(supplier_sku=SKU, proposed_price_cents=38900))
    assert v.ok is False
    assert v.floor_cents == 39900
    assert "below binding floor" in v.reason


def test_guardrail_accepts_in_policy_price():
    v = check_price(PriceCheckRequest(supplier_sku=SKU, proposed_price_cents=44900))
    assert v.ok is True


# --- the model-decides loop (fake model) ---


def test_model_calls_tool_then_adjusts_up_after_rejection():
    # First the model proposes $389 (under MAP); after the verdict it re-proposes $429.
    model = FakeModel(script=[_call(38900), _call(42900)])
    result = price_listing(model, prompt="Price the Aldsworth desk")
    assert result["checked"] is True
    assert result["price_cents"] == 42900
    assert result["verdict"].ok is True


def test_failure_mode_model_skips_tool_and_hallucinates_sub_map():
    # The model answers directly with $379, never calling the guardrail.
    model = FakeModel(script=[37900])  # a bare int = "I'll just answer"
    result = price_listing(model, prompt="Price the Aldsworth desk")
    assert result["checked"] is False  # the tell: nothing checked it
    assert result["price_cents"] == 37900  # a sub-MAP price shipped
    # and prove the guardrail WOULD have caught it, had the model called it
    assert (
        check_price(
            PriceCheckRequest(supplier_sku=SKU, proposed_price_cents=37900)
        ).ok
        is False
    )

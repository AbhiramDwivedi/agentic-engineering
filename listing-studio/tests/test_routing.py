"""Tests for the routing & dispatch chapter (3.2) companion code.

All tests are offline: no API key, no network call.

- dispatch() is pure Python and is tested directly: known event types run
  their handler, an unknown event type hits the deny branch and returns a
  structured DispatchResult instead of raising.
- Category / RouteDecision are imported directly (no third-party deps
  beyond pydantic, which is pure Python).
- route_message is tested with a stub classify_fn so the classify-then-
  handle shape and the unclear/low-confidence escalation path both run
  fully offline and deterministically.
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API
  keys and the heavy provider SDKs, which are not test dependencies).
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from routing.dispatch import EVENT_HANDLERS, DispatchResult, dispatch
from routing.route import RouteResult, route_message
from routing.schemas import Category, RouteDecision

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "routing")

LANGGRAPH_FILE = os.path.join(PKG, "router_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "router_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "router_anthropic.py")


# ---------------------------------------------------------------------------
# Static dispatch (anchor: routing-dispatch)
# ---------------------------------------------------------------------------

def test_known_event_type_dispatches_to_its_handler():
    result = dispatch({"event_type": "new_product", "supplier_sku": "NV-ALDSWORTH-DM"})
    assert isinstance(result, DispatchResult)
    assert result.ok is True
    assert "NV-ALDSWORTH-DM" in result.detail
    assert result.error is None


def test_each_known_event_type_reaches_its_own_handler():
    for event_type in EVENT_HANDLERS:
        result = dispatch({"event_type": event_type, "supplier_sku": "NV-ALDSWORTH-DM"})
        assert result.ok is True


def test_unknown_event_type_hits_the_deny_branch_not_a_keyerror():
    """An unrecognized key must never raise KeyError -- it returns a
    structured error the caller can log and act on."""
    result = dispatch({"event_type": "delete_catalog", "supplier_sku": "x"})
    assert isinstance(result, DispatchResult)
    assert result.ok is False
    assert result.error is not None
    assert "delete_catalog" in result.error


def test_missing_event_type_is_also_denied_not_a_keyerror():
    result = dispatch({"supplier_sku": "NV-ALDSWORTH-DM"})
    assert result.ok is False
    assert "None" in result.error


def test_dispatch_never_builds_a_handler_from_the_raw_string():
    """A crafted key that looks like an attribute/dunder must be denied by
    the same key-validation path, not reach getattr/eval on the module."""
    result = dispatch({"event_type": "__class__", "supplier_sku": "x"})
    assert result.ok is False
    assert "__class__" in result.error


# ---------------------------------------------------------------------------
# Schemas (anchor: routing-schemas)
# ---------------------------------------------------------------------------

def test_category_taxonomy_includes_unclear():
    assert Category.UNCLEAR.value == "unclear"
    assert {c.value for c in Category} == {
        "billing", "listing_issue", "account", "unclear",
    }


def test_route_decision_accepts_valid_object():
    d = RouteDecision(category=Category.BILLING, confidence=0.92)
    assert d.category == Category.BILLING


def test_route_decision_rejects_extra_fields():
    with pytest.raises(ValidationError):
        RouteDecision(category=Category.BILLING, confidence=0.9, stray="nope")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# route_message (anchor: routing-route)
# The classify-then-handle shape, and the unclear/low-confidence escalation.
# ---------------------------------------------------------------------------

HANDLERS = {
    Category.BILLING: lambda msg: f"[billing] {msg}",
    Category.LISTING_ISSUE: lambda msg: f"[listing_issue] {msg}",
    Category.ACCOUNT: lambda msg: f"[account] {msg}",
}


def _classify_as(category: Category, confidence: float = 0.9):
    def classify_fn(message: str) -> RouteDecision:
        return RouteDecision(category=category, confidence=confidence)
    return classify_fn


@pytest.mark.parametrize(
    "category",
    [Category.BILLING, Category.LISTING_ISSUE, Category.ACCOUNT],
)
def test_route_message_reaches_the_matching_handler(category):
    result = route_message(_classify_as(category), HANDLERS, "help me")
    assert isinstance(result, RouteResult)
    assert result.category == category
    assert result.escalated is False
    assert result.response == f"[{category.value}] help me"


def test_route_message_escalates_on_unclear_category():
    """unclear is part of the taxonomy, not an exception path."""
    result = route_message(_classify_as(Category.UNCLEAR, confidence=0.95), HANDLERS, "??")
    assert result.escalated is True
    assert result.category == Category.UNCLEAR
    assert "escalated to a human" in result.response


def test_route_message_escalates_on_low_confidence_even_if_on_taxonomy():
    """A confidently-named category with low stated confidence still
    escalates -- the model never gets to force a guess through."""
    result = route_message(_classify_as(Category.BILLING, confidence=0.2), HANDLERS, "hmm")
    assert result.escalated is True
    assert result.category == Category.UNCLEAR


def test_route_message_never_raises_on_off_taxonomy_input():
    """The failure-return contract: escalation is a structured signal, not
    an exception -- no handler ever runs for a message that doesn't clear
    the confidence floor."""
    calls = []
    handlers = {
        Category.BILLING: lambda msg: calls.append(msg) or "should not run",
        Category.LISTING_ISSUE: lambda msg: calls.append(msg) or "should not run",
        Category.ACCOUNT: lambda msg: calls.append(msg) or "should not run",
    }
    result = route_message(_classify_as(Category.UNCLEAR), handlers, "gibberish")
    assert result.escalated is True
    assert calls == []  # no handler was ever called


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

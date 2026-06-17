"""Tests for the augmented-LLM chapter companion code.

All tests are offline: no API key, no network call.

- The state TypedDict and floor_price logic are imported directly (no third-
  party deps in those modules).
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API keys).
"""
import os
import py_compile

from augmented_llm.floor_price import lookup_floor_price
from augmented_llm.state import ListingState

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "augmented_llm")

LANGGRAPH_FILE = os.path.join(PKG, "augmented_llm_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "augmented_llm_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "augmented_llm_example.py")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def test_listing_state_is_constructable():
    """The TypedDict can be instantiated and its fields read back."""
    state: ListingState = {
        "supplier_sku": "NV-ALDSWORTH-DM",
        "title": "Aldsworth Dual-Motor Sit-Stand Desk",
        "price_cents": None,
    }
    assert state["supplier_sku"] == "NV-ALDSWORTH-DM"
    assert state["price_cents"] is None


def test_listing_state_price_cents_is_writable():
    """A node writes price_cents; the new value is readable from state."""
    state: ListingState = {
        "supplier_sku": "NV-ALDSWORTH-DM",
        "title": "Aldsworth Dual-Motor Sit-Stand Desk",
        "price_cents": None,
    }
    # Simulate what a node's return dict merge would do.
    state.update({"price_cents": 41895})
    assert state["price_cents"] == 41895


# ---------------------------------------------------------------------------
# Floor-price tool (the unit's one tool, pure Python)
# ---------------------------------------------------------------------------

def test_floor_price_returns_map_floor():
    """The tool returns the correct MAP floor for the Aldsworth desk."""
    out = lookup_floor_price("NV-ALDSWORTH-DM")
    assert out == {"floor_cents": 39900}


def test_floor_price_floor_is_positive_integer():
    out = lookup_floor_price("NV-ALDSWORTH-DM")
    assert isinstance(out["floor_cents"], int)
    assert out["floor_cents"] > 0


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

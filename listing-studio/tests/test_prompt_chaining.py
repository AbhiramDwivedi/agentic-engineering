"""Tests for the prompt-chaining chapter (3.1) companion code.

All tests are offline: no API key, no network call.

- CategoryDecision / CopyDraft and validate_category are imported directly
  (no third-party deps beyond pydantic, which is pure Python).
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API keys).
- run_chain is tested with stub categorize_fn / write_copy_fn so the fixed
  order, the gate, the single re-ask, and the loud abort all run fully
  offline and deterministically.
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from prompt_chaining.chain import run_chain
from prompt_chaining.gate import TAXONOMY, validate_category
from prompt_chaining.schemas import CategoryDecision, CopyDraft

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "prompt_chaining")

LANGGRAPH_FILE = os.path.join(PKG, "prompt_chaining_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "prompt_chaining_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "prompt_chaining_example.py")

VALID_PATH = "office/desks/standing-desks"
INVALID_PATH = "furniture/office/desks"  # not in TAXONOMY

assert VALID_PATH in TAXONOMY  # keep the fixture honest


# ---------------------------------------------------------------------------
# Schemas (anchor: chain-schemas)
# ---------------------------------------------------------------------------

def test_category_decision_accepts_valid_object():
    d = CategoryDecision(category_path=VALID_PATH, confidence=0.92)
    assert d.category_path == VALID_PATH


def test_category_decision_rejects_extra_fields():
    with pytest.raises(ValidationError):
        CategoryDecision(category_path=VALID_PATH, confidence=0.9, stray="nope")  # type: ignore[call-arg]


def test_copy_draft_accepts_valid_object():
    d = CopyDraft(description="A sturdy sit-stand desk.", bullets=["Dual motor", "4 presets"])
    assert d.bullets[0] == "Dual motor"


def test_copy_draft_rejects_extra_fields():
    with pytest.raises(ValidationError):
        CopyDraft(description="x", bullets=[], stray="nope")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# The gate (anchor: chain-gate)
# ---------------------------------------------------------------------------

def test_valid_category_passes_the_gate():
    result = validate_category(CategoryDecision(category_path=VALID_PATH, confidence=0.9))
    assert result.ok is True
    assert result.error is None


def test_invalid_category_fails_the_gate():
    result = validate_category(CategoryDecision(category_path=INVALID_PATH, confidence=0.9))
    assert result.ok is False
    assert "taxonomy" in result.error


# ---------------------------------------------------------------------------
# run_chain (anchor: chain-run)
# The fixed order, the gate, the single re-ask, the loud abort, and the
# minimal-fields-forward all live here.
# ---------------------------------------------------------------------------

def test_run_chain_succeeds_when_category_is_valid_first_try():
    calls = {"categorize": 0, "write_copy": 0}

    def categorize_fn(messages):
        calls["categorize"] += 1
        return CategoryDecision(category_path=VALID_PATH, confidence=0.9)

    def write_copy_fn(messages):
        calls["write_copy"] += 1
        return CopyDraft(description="ok", bullets=["a"])

    result = run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")
    assert isinstance(result, CopyDraft)
    assert calls == {"categorize": 1, "write_copy": 1}


def test_run_chain_reasks_once_and_recovers():
    """A first invalid category is corrected on the single re-ask."""
    call_count = 0

    def categorize_fn(messages):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return CategoryDecision(category_path=INVALID_PATH, confidence=0.9)
        return CategoryDecision(category_path=VALID_PATH, confidence=0.9)

    def write_copy_fn(messages):
        return CopyDraft(description="ok", bullets=["a"])

    result = run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")
    assert isinstance(result, CopyDraft)
    assert call_count == 2


def test_run_chain_reask_feeds_back_the_structured_error():
    seen_messages = []

    def categorize_fn(messages):
        seen_messages.append(list(messages))
        if len(seen_messages) == 1:
            return CategoryDecision(category_path=INVALID_PATH, confidence=0.9)
        return CategoryDecision(category_path=VALID_PATH, confidence=0.9)

    def write_copy_fn(messages):
        return CopyDraft(description="ok", bullets=["a"])

    run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")
    assert len(seen_messages) == 2
    # The retry call carries the original message plus the structured error.
    assert len(seen_messages[1]) == 2
    assert "taxonomy" in seen_messages[1][1]["content"]


def test_run_chain_aborts_loudly_after_the_retry_also_fails():
    def categorize_fn(messages):
        return CategoryDecision(category_path=INVALID_PATH, confidence=0.9)

    def write_copy_fn(messages):
        pytest.fail("write_copy_fn must not run after the gate fails twice")

    with pytest.raises(RuntimeError, match="failed its gate twice"):
        run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")


def test_run_chain_does_not_retry_more_than_once():
    """The gate re-asks exactly once, not a bounded loop like 2.2's schema re-ask."""
    call_count = 0

    def categorize_fn(messages):
        nonlocal call_count
        call_count += 1
        return CategoryDecision(category_path=INVALID_PATH, confidence=0.9)

    def write_copy_fn(messages):
        pytest.fail("write_copy_fn must not run after the gate fails twice")

    with pytest.raises(RuntimeError):
        run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")
    assert call_count == 2  # one attempt, one re-ask, then abort -- never a third call


def test_run_chain_forwards_only_minimal_fields_to_write_copy():
    """The gate passes category_path and the identifiers, not the transcript."""

    def categorize_fn(messages):
        if len(messages) == 1:
            return CategoryDecision(category_path=INVALID_PATH, confidence=0.9)
        return CategoryDecision(category_path=VALID_PATH, confidence=0.9)

    captured = {}

    def write_copy_fn(messages):
        captured["messages"] = messages
        return CopyDraft(description="ok", bullets=["a"])

    run_chain(categorize_fn, write_copy_fn, "NV-ALDSWORTH-DM", "Aldsworth Desk")
    copy_messages = captured["messages"]
    assert len(copy_messages) == 1  # not the accumulated categorize transcript
    assert VALID_PATH in copy_messages[0]["content"]
    assert "Invalid category" not in copy_messages[0]["content"]
    assert "taxonomy" not in copy_messages[0]["content"]


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

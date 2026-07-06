"""The fixed two-step chain: categorize, gate, then write copy.

The pure, offline-testable heart of this chapter's example. run_chain owns
the order -- your code decides the sequence, not the model -- and applies
the gate between the two steps. categorize_fn and write_copy_fn are the
seam the provider variants inject (LangGraph / Responses / Anthropic); see
prompt_chaining_langgraph.py, prompt_chaining_responses.py, and
prompt_chaining_example.py.
"""
from __future__ import annotations

from typing import Any

from .gate import validate_category
from .schemas import CopyDraft


# --8<-- [start:chain-run]
def run_chain(
    categorize_fn: Any,  # callable(messages) -> CategoryDecision
    write_copy_fn: Any,  # callable(messages) -> CopyDraft
    supplier_sku: str,
    title: str,
) -> CopyDraft:
    """Categorize, gate, write copy -- in that fixed order, every time.

    write_copy_fn never runs until categorize_fn's output clears the gate.
    On a gate failure, categorize_fn is re-asked once with the validation
    error folded in as a structured message -- the same shape as 2.2's
    re-ask loop, applied to the gate instead of the schema. A second failure
    aborts the chain loudly; it does not let an uncategorized product flow
    into the copy step.
    """
    messages = [
        {"role": "user", "content": f"Categorize {title} (SKU {supplier_sku})."}
    ]
    decision = categorize_fn(messages)
    gate = validate_category(decision)

    if not gate.ok:
        # Re-ask the SAME step once, feeding back the gate's structured error.
        messages.append({"role": "user", "content": f"Invalid category: {gate.error}"})
        decision = categorize_fn(messages)
        gate = validate_category(decision)

    if not gate.ok:
        # The retry also failed: abort loudly. No silent pass-through of an
        # unvalidated category into the copy step.
        raise RuntimeError(f"categorize step failed its gate twice: {gate.error}")

    # Only the minimal validated fields cross the gate into step two -- not
    # the categorize transcript, not the rejected first attempt.
    copy_messages = [
        {
            "role": "user",
            "content": (
                f"Write listing copy for {title} (SKU {supplier_sku}) "
                f"in category {decision.category_path}."
            ),
        }
    ]
    return write_copy_fn(copy_messages)
# --8<-- [end:chain-run]

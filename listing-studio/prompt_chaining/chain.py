"""The fixed two-step chain: categorize, gate, then write copy.

categorize_fn and write_copy_fn are the seam the provider variants inject
(LangGraph / Responses / Anthropic); see prompt_chaining_langgraph.py,
prompt_chaining_responses.py, and prompt_chaining_example.py.
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
    """Categorize, gate, then write copy -- in that fixed order."""
    messages = [
        {"role": "user", "content": f"Categorize {title} (SKU {supplier_sku})."}
    ]
    decision = categorize_fn(messages)
    gate = validate_category(decision)

    if not gate.ok:
        messages.append({"role": "user", "content": f"Invalid category: {gate.error}"})
        decision = categorize_fn(messages)
        gate = validate_category(decision)

    if not gate.ok:
        raise RuntimeError(f"categorize step failed its gate twice: {gate.error}")

    # Only the validated category_path crosses the gate -- not the transcript.
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

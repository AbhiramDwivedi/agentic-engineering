"""Which model runs which Listing Studio step. Model IDs live only here."""
from __future__ import annotations

# --8<-- [start:model-config]
STEP_MODELS: dict[str, str] = {
    "categorize": "openai:gpt-6.2-sol",
    "write_copy": "anthropic:claude-sonnet-5-5",
    "price": "openai:gpt-6.2-sol",
    "polish": "anthropic:claude-sonnet-5-5",
}


def model_for(step: str) -> str:
    """One lookup per step. A step with no entry fails loudly, never falls back."""
    if step not in STEP_MODELS:
        raise KeyError(f"no model configured for step {step!r}")
    return STEP_MODELS[step]
# --8<-- [end:model-config]

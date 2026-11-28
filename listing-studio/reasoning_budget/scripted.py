"""A scripted model for the sweep. Its numbers are made up to show the shape of
a sweep, not measured on any real model: do not quote them as findings."""
from __future__ import annotations

from .sweep import Case, ModelReply

# --8<-- [start:sweep-cases]
CASES = [
    # Trivial: the category is in the title.
    Case(
        id="NV-PHONECASE-01",
        prompt="Store category for: 'Clear slim phone case, shock-absorbing corners'.",
        expected="phone-accessories",
    ),
    # Multi-step: the warning has to be worked out from the materials list.
    Case(
        id="NV-ALDSWORTH-DM",
        prompt=(
            "Which compliance notice does this need? Sit-stand desk; materials: "
            "steel frame, MDF top bonded with formaldehyde-based resin."
        ),
        expected="prop-65",
    ),
]


def exact_match(case: Case, text: str) -> bool:
    return text.strip() == case.expected
# --8<-- [end:sweep-cases]

# (case id, level) -> (answer, thinking tokens). The script makes the trivial
# case get worse at "high" (overthinking) and the hard case need "medium".
_SCRIPT = {
    ("NV-PHONECASE-01", "none"): ("phone-accessories", 0),
    ("NV-PHONECASE-01", "low"): ("phone-accessories", 200),
    ("NV-PHONECASE-01", "medium"): ("phone-accessories", 900),
    ("NV-PHONECASE-01", "high"): ("cases", 2400),
    ("NV-ALDSWORTH-DM", "none"): ("none-needed", 0),
    ("NV-ALDSWORTH-DM", "low"): ("none-needed", 400),
    ("NV-ALDSWORTH-DM", "medium"): ("prop-65", 1200),
    ("NV-ALDSWORTH-DM", "high"): ("prop-65", 2600),
}
VISIBLE_TOKENS = 20


def scripted_model(case: Case, level: str, cap: int) -> ModelReply:
    answer, thinking = _SCRIPT[(case.id, level)]
    if thinking + VISIBLE_TOKENS > cap:
        # The cap ran out during thinking: billed in full, no visible text.
        return ModelReply(text="", visible_tokens=0, thinking_tokens=cap)
    return ModelReply(text=answer, visible_tokens=VISIBLE_TOKENS, thinking_tokens=thinking)

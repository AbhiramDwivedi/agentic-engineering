"""AI-disclosure label: tell the person they are dealing with an AI system.

Pure function. Code decides when a label is required and what it says; the
model never writes its own disclosure.
"""
from __future__ import annotations


# --8<-- [start:governance-disclosure]
def disclosure_label(
    *, surface: str, ai_generated: bool, human_reviewed: bool = False
) -> str:
    """Return the label to show, or "" when nothing needs disclosing."""
    if not ai_generated:
        return ""
    if surface == "chat":
        return "You are chatting with an AI assistant."
    if human_reviewed:
        return "Written with AI, reviewed by a person."
    return "Written by AI."
# --8<-- [end:governance-disclosure]

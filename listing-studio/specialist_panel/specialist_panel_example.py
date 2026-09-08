"""Specialist panel against the Anthropic Messages API: three commerce
personas reasoning over one listing.

Illustration, not run in CI: needs an API key and a network call. The
default pane is specialist_panel_langgraph.py; this is the Anthropic
Messages variant, and it reuses the tested run_panel (roster.py) and
reconcile (reconcile.py) -- only the persona call shape changes per
provider, not the roster, the precedence rule, or the escalation check.
"""
from __future__ import annotations

import anthropic

from .reconcile import reconcile
from .roster import run_panel
from .schemas import PersonaVerdict

client = anthropic.Anthropic()

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
}

# --8<-- [start:panel-anthropic]
_VERDICT_TOOL = {
    "name": "produce_persona_verdict",
    "description": "Return this specialist's typed claims about the listing.",
    "input_schema": {
        "type": "object",
        "properties": {
            "persona": {"type": "string"},
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "value": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                    "required": ["field", "value", "rationale"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["persona", "claims"],
        "additionalProperties": False,
    },
}


def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_VERDICT_TOOL],
        tool_choice={"type": "tool", "name": "produce_persona_verdict"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are the {persona} specialist. Review this Listing "
                    f"Studio product and return typed claims only for fields "
                    f"your role covers: {listing}"
                ),
            }
        ],
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return PersonaVerdict.model_validate(tool_block.input)


panel = run_panel(persona_fn, ALDSWORTH_LISTING)
decision = reconcile(panel.verdicts, panel.missing)
print(decision.accepted, decision.conflicts)
# --8<-- [end:panel-anthropic]

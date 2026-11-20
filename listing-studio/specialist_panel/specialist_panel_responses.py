"""Specialist panel against the OpenAI Responses API: three commerce
personas reasoning over one listing.

Illustration, not run in CI: needs an API key and a network call. The
default pane is specialist_panel_langgraph.py; this is the OpenAI
Responses variant, and it reuses the tested run_panel (roster.py) and
reconcile (reconcile.py) -- only the persona call shape changes per
provider, not the roster, the precedence rule, or the escalation check.
"""
from __future__ import annotations

from openai import OpenAI

from .reconcile import reconcile
from .roster import run_panel
from .schemas import PersonaVerdict

client = OpenAI()

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
}


# --8<-- [start:panel-responses]
def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": (
                    f"You are the {persona} specialist. Review this Listing "
                    f"Studio product and return typed claims only for fields "
                    f"your role covers: {listing}"
                ),
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "PersonaVerdict",
                "schema": PersonaVerdict.model_json_schema(),
                "strict": True,
            }
        },
    )
    return PersonaVerdict.model_validate_json(response.output_text)


panel = run_panel(persona_fn, ALDSWORTH_LISTING)
decision = reconcile(panel.verdicts, panel.missing)
print(decision.accepted, decision.conflicts)
# --8<-- [end:panel-responses]

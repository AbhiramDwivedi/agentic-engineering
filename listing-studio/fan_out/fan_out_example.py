"""Dynamic fan-out against the Anthropic Messages API: the extra deliverables.

Illustration, not run in CI: needs an API key and a network call. The
default pane is fan_out_langgraph.py; this is the Anthropic Messages
variant, and it reuses the tested propose_deliverables (plan.py) and
gather (gather.py) -- only the planner and worker call shapes change per
provider, not the cap or the merge.
"""
from __future__ import annotations

import anthropic

from .gather import gather
from .plan import propose_deliverables
from .schemas import FanOutPlan

client = anthropic.Anthropic()

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
    "attributes": {"bulky_shipping": True, "assembly_required": True},
}

_PLAN_TOOL = {
    "name": "produce_fan_out_plan",
    "description": "Name the extra launch deliverables this product needs, and why.",
    "input_schema": {
        "type": "object",
        "properties": {
            "deliverables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "deliverable_id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["deliverable_id", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["deliverables"],
        "additionalProperties": False,
    },
}


# --8<-- [start:fanout-anthropic]
def planner_fn(listing: dict) -> FanOutPlan:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[_PLAN_TOOL],
        tool_choice={"type": "tool", "name": "produce_fan_out_plan"},
        messages=[
            {
                "role": "user",
                "content": (
                    "Given this finished Listing Studio product, name any extra "
                    "launch deliverables it needs beyond the standard listing, "
                    f"announcement email, and ad copy: {listing}"
                ),
            }
        ],
    )
    tool_block = next(b for b in reply.content if b.type == "tool_use")
    return FanOutPlan.model_validate(tool_block.input)


def worker_fn(deliverable_id: str, listing: dict) -> str:
    reply = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"Write the {deliverable_id} deliverable for: {listing}"}
        ],
    )
    return next(b.text for b in reply.content if b.type == "text")


plan = propose_deliverables(planner_fn, ALDSWORTH_LISTING)
summary = gather(
    worker_fn, [d.deliverable_id for d in plan.deliverables], ALDSWORTH_LISTING
)
print(summary.summary)
# --8<-- [end:fanout-anthropic]

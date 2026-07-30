"""Dynamic fan-out against the OpenAI Responses API: the extra deliverables.

Illustration, not run in CI: needs an API key and a network call. The
default pane is fan_out_langgraph.py; this is the OpenAI Responses variant,
and it reuses the tested propose_deliverables (plan.py) and gather
(gather.py) -- only the planner and worker call shapes change per provider,
not the cap or the merge.
"""
from __future__ import annotations

from openai import OpenAI

from .gather import gather
from .plan import propose_deliverables
from .schemas import FanOutPlan

client = OpenAI()

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
    "attributes": {"bulky_shipping": True, "assembly_required": True},
}


# --8<-- [start:fanout-responses]
def planner_fn(listing: dict) -> FanOutPlan:
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": (
                    "Given this finished Listing Studio product, name any extra "
                    "launch deliverables it needs beyond the standard listing, "
                    f"announcement email, and ad copy, and why: {listing}"
                ),
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "FanOutPlan",
                "schema": FanOutPlan.model_json_schema(),
                "strict": True,
            }
        },
    )
    return FanOutPlan.model_validate_json(response.output_text)


def worker_fn(deliverable_id: str, listing: dict) -> str:
    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {"role": "user", "content": f"Write the {deliverable_id} deliverable for: {listing}"}
        ],
    )
    return response.output_text


plan = propose_deliverables(planner_fn, ALDSWORTH_LISTING)
summary = gather(
    worker_fn, [d.deliverable_id for d in plan.deliverables], ALDSWORTH_LISTING
)
print(summary.summary)
# --8<-- [end:fanout-responses]

"""Skills with the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is skills_langgraph.py; this is the OpenAI Responses variant.

The Responses API tool schema is identical to the LangGraph shape; the
difference is how we invoke the agent loop and handle tool calls manually.
"""
from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from .loader import load_skill_meta, load_skill_body, run_skill_script

_SKILL_DIR = Path(__file__).parent / "map_compliance"
client = OpenAI()


# --8<-- [start:skill-responses]
# Level 1: name + description in the system prompt, Level 2: body on trigger.
skill = load_skill_meta(_SKILL_DIR)
skill_body = load_skill_body(skill)

CHECK_MAP_TOOL = {
    "type": "function",
    "name": "check_map_price",
    "description": (
        "Run the MAP-compliance check for a proposed price. Returns a JSON "
        "result confirming whether the price meets the MAP floor and margin rules."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
            "proposed_price_cents": {"type": "integer"},
        },
        "required": ["supplier_sku", "proposed_price_cents"],
        "additionalProperties": False,
    },
}

response = client.responses.create(
    model="gpt-5.5",
    instructions=(
        f"Available skill: {skill.name} — {skill.description}\n\n{skill_body}"
    ),
    input=[{
        "role": "user",
        "content": (
            "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
            "(SKU NV-ALDSWORTH-DM). Use the MAP-compliance skill to validate."
        ),
    }],
    tools=[CHECK_MAP_TOOL],
)

# If the model called a tool, run Level 3 and feed the result back.
for item in response.output:
    if item.type == "function_call" and item.name == "check_map_price":
        args = json.loads(item.arguments)
        # Level 3: run the bundled script; stdout enters context, not the source.
        tool_output = run_skill_script(
            skill, "check_map.py",
            [args["supplier_sku"], str(args["proposed_price_cents"])],
        )
        print("Script output injected into context:", tool_output)
# --8<-- [end:skill-responses]

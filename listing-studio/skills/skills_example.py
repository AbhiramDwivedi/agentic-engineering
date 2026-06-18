"""Skills with the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is skills_langgraph.py; this is the Anthropic Messages variant.
"""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from .loader import load_skill_meta, load_skill_body, run_skill_script

_SKILL_DIR = Path(__file__).parent / "map_compliance"
client = anthropic.Anthropic()


# --8<-- [start:skill-anthropic]
# Level 1: name + description in the system prompt, Level 2: body on trigger.
skill = load_skill_meta(_SKILL_DIR)
skill_body = load_skill_body(skill)

CHECK_MAP_TOOL = {
    "name": "check_map_price",
    "description": (
        "Run the MAP-compliance check for a proposed price. Returns a JSON "
        "result confirming whether the price meets the MAP floor and margin rules."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_sku": {"type": "string"},
            "proposed_price_cents": {"type": "integer"},
        },
        "required": ["supplier_sku", "proposed_price_cents"],
        "additionalProperties": False,
    },
}

reply = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=(
        f"Available skill: {skill.name} — {skill.description}\n\n{skill_body}"
    ),
    tools=[CHECK_MAP_TOOL],
    messages=[{
        "role": "user",
        "content": (
            "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
            "(SKU NV-ALDSWORTH-DM). Use the MAP-compliance skill to validate."
        ),
    }],
)

for block in reply.content:
    if block.type == "tool_use" and block.name == "check_map_price":
        # Level 3: run the bundled script; stdout enters context, not the source.
        tool_output = run_skill_script(
            skill, "check_map.py",
            [block.input["supplier_sku"], str(block.input["proposed_price_cents"])],
        )
        print("Script output injected into context:", tool_output)
# --8<-- [end:skill-anthropic]

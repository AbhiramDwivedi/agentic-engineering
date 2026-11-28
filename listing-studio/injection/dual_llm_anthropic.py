"""Anthropic Messages: the guard sits between the tool_use block and its
tool_result (compiled, not run)."""
import anthropic

from .guard import guard_action
from .quarantine import SpecRecord, privileged_prompt

client = anthropic.Anthropic()
raw_sheet = ""
SET_PRICE_TOOL = {"name": "set_price", "description": "Set the price in cents.",
                  "input_schema": {"type": "object",
                                   "properties": {"price_cents": {"type": "integer"}},
                                   "required": ["price_cents"]}}

# --8<-- [start:injection-anthropic]
read = client.messages.create(          # quarantined: forced typed output only
    model="claude-sonnet-5-5", max_tokens=512,
    tools=[{"name": "record", "description": "Spec fields.",
            "input_schema": SpecRecord.model_json_schema()}],
    tool_choice={"type": "tool", "name": "record"},
    messages=[{"role": "user", "content": raw_sheet}])
record = SpecRecord(**read.content[0].input)

response = client.messages.create(      # privileged: never sees raw_sheet
    model="claude-sonnet-5-5", max_tokens=512, tools=[SET_PRICE_TOOL],
    messages=[{"role": "user", "content": privileged_prompt(record)}])
for block in response.content:
    if block.type == "tool_use":
        verdict = guard_action({"tool": block.name, **block.input},
                               untrusted_read=True)
# --8<-- [end:injection-anthropic]

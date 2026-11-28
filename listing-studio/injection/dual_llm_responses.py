"""OpenAI Responses: the guard sits between the function_call and its output
(compiled, not run)."""
import json

from openai import OpenAI

from .guard import guard_action
from .quarantine import SpecRecord, privileged_prompt

client = OpenAI()
raw_sheet = ""

# --8<-- [start:injection-responses]
read = client.responses.parse(          # quarantined: no tools, typed output
    model="gpt-6.2-sol", input=raw_sheet, text_format=SpecRecord)
record = read.output_parsed

response = client.responses.create(     # privileged: never sees raw_sheet
    model="gpt-6.2-sol", input=privileged_prompt(record),
    tools=[{"type": "function", "name": "set_price",
            "parameters": {"type": "object",
                           "properties": {"price_cents": {"type": "integer"}},
                           "required": ["price_cents"],
                           "additionalProperties": False}}])
for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        verdict = guard_action({"tool": item.name, **args}, untrusted_read=True)
# --8<-- [end:injection-responses]

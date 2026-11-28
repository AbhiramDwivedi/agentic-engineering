"""The same output check as an OpenAI Agents SDK output guardrail.

Illustration, not run in CI: needs the openai-agents package and an API key.
Compile-checked only. The SDK runs the guardrail on the agent's final output and
raises OutputGuardrailTripwireTriggered; deciding what happens next (here: hold
for review) is still the application's job. API names checked against
openai.github.io/openai-agents-python/guardrails/ on 2026-11-28.
"""
from agents import (Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered,
                    RunContextWrapper, Runner, output_guardrail)
from pydantic import BaseModel

from .checks import ListingCopy, Record, claim_check, leak_check


class CopyOut(BaseModel):
    title: str
    description: str


RECORD = Record(sku="DESK-ALD-01", supplier_name="Northvale Furnishings",
                weight_capacity_lbs=250)


@output_guardrail
async def copy_guardrail(ctx: RunContextWrapper, agent: Agent,
                         output: CopyOut) -> GuardrailFunctionOutput:
    copy = ListingCopy(title=output.title, description=output.description)
    verdicts = [claim_check(copy, RECORD), leak_check(copy, RECORD)]
    return GuardrailFunctionOutput(
        output_info=[v.model_dump() for v in verdicts],
        tripwire_triggered=any(v.blocks for v in verdicts))


writer = Agent(name="Copywriter", instructions="Write listing copy.",
               output_type=CopyOut, output_guardrails=[copy_guardrail])


async def write_or_hold(prompt: str):
    try:
        return (await Runner.run(writer, prompt)).final_output
    except OutputGuardrailTripwireTriggered:
        return None   # route the listing to review

"""The same deny rule as an OpenAI Agents SDK tool input guardrail.

Illustration, not run in CI: needs the openai-agents package and a model key.
Compile-checked only. Names (tool_input_guardrail, ToolGuardrailFunctionOutput
.reject_content / .allow, @tool(tool_input_guardrails=[...])) checked against
openai.github.io/openai-agents-python/guardrails/ on 2026-11-28. The import
path for the decorators shown there is agents.decorators; the docs have moved
before, so re-check on upgrade.
"""
from __future__ import annotations

import json

from agents import Agent, ToolGuardrailFunctionOutput
from agents.decorators import tool, tool_input_guardrail

from .policy import decide
from .scenario import RULES


# --8<-- [start:harness-openai]
@tool_input_guardrail
def enforce_policy(data):
    args = json.loads(data.context.tool_arguments or "{}")
    verdict, reason = decide(RULES, "write_draft", args)
    if verdict != "allow":
        return ToolGuardrailFunctionOutput.reject_content(f"error: {reason}")
    return ToolGuardrailFunctionOutput.allow()


@tool(tool_input_guardrails=[enforce_policy])
def write_draft(supplier_sku: str, title: str, price_cents: int, target: str = "draft") -> str:
    """Write a listing draft."""
    return f"draft saved for {supplier_sku}"


agent = Agent(name="Ingest", model="gpt-6.2-sol", tools=[write_draft])  # no publish
# --8<-- [end:harness-openai]

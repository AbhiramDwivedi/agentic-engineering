"""Skills with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call. The raw-SDK
variants are skills_responses.py (OpenAI Responses) and skills_example.py
(Anthropic Messages).

Shows how the three load levels plug into a LangGraph pricing node:
  - Level 1 metadata goes into the system prompt at graph construction.
  - Level 2 body loads when the model selects the skill.
  - Level 3 script output is injected as a tool result.
"""
from __future__ import annotations

from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool

from .loader import load_skill_meta, load_skill_body, run_skill_script

_SKILL_DIR = Path(__file__).parent / "map_compliance"


# --8<-- [start:skill-langgraph]
# Level 1: load metadata at startup — tiny token budget, always in the system prompt.
skill = load_skill_meta(_SKILL_DIR)

# The system prompt carries only the name + description (Level 1).
# The full body (Level 2) is loaded below only when this skill is triggered.
SYSTEM_PROMPT = (
    "You are a pricing specialist for Stockwell. "
    f"Available skill: {skill.name} — {skill.description}"
)

# Level 2: load the full body on trigger (e.g. when the task is pricing-related).
skill_body = load_skill_body(skill)


@tool(parse_docstring=True)
def check_map_price(supplier_sku: str, proposed_price_cents: int) -> str:
    """Run the MAP-compliance check for a proposed price.

    Args:
        supplier_sku: the product SKU to check.
        proposed_price_cents: the proposed listed price in cents.
    """
    # Level 3: run the bundled script; its output enters context, not the source.
    return run_skill_script(skill, "check_map.py", [supplier_sku, str(proposed_price_cents)])


agent = create_agent(
    "openai:gpt-5.5",
    tools=[check_map_price],
    system_message=SYSTEM_PROMPT + "\n\n" + skill_body,
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
            "(SKU NV-ALDSWORTH-DM). Use the MAP-compliance skill to validate "
            "the price before confirming it."
        ),
    }]
})
print(result["messages"][-1].content)
# --8<-- [end:skill-langgraph]

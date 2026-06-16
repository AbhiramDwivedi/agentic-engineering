"""Tool use with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call. The raw-SDK
versions are tool_use_responses.py (OpenAI Responses) and tool_use_example.py
(Anthropic Messages).
"""
from langchain.agents import create_agent
from langchain.tools import tool


# --8<-- [start:tool]
# A tool is just your function. LangGraph reads a description generated from the
# type hints and the docstring; underneath it is a JSON schema (see the panes).
@tool(parse_docstring=True)
def check_price(supplier_sku: str, proposed_price_cents: int) -> dict:
    """Check a proposed price against the supplier's minimum advertised price.

    Args:
        supplier_sku: the product SKU.
        proposed_price_cents: the price to check, in cents.
    """
    floor_cents = 39900  # $399.00 MAP for the Aldsworth desk
    return {"ok": proposed_price_cents >= floor_cents, "floor_cents": floor_cents}
# --8<-- [end:tool]


@tool(parse_docstring=True)
def get_competitor_prices(supplier_sku: str) -> dict:
    """Fetch current competitor prices for a product, in cents.

    Args:
        supplier_sku: the product SKU.
    """
    return {"prices_cents": [41900, 44500, 39900]}


# --8<-- [start:flow]
# LangGraph runs the loop for you: build the agent, then invoke it.
agent = create_agent("openai:gpt-5.5", tools=[check_price])

result = agent.invoke(
    {"messages": [{"role": "user",
                   "content": "Set a price for the Aldsworth sit-stand desk, SKU NV-ALDSWORTH-DM."}]}
)
print(result["messages"][-1].content)
# --8<-- [end:flow]


# --8<-- [start:many]
# Several tools: hand them all to the agent; it routes by description.
agent = create_agent("openai:gpt-5.5", tools=[check_price, get_competitor_prices])
# --8<-- [end:many]

"""LangGraph: the guard wraps the tool the agent calls (compiled, not run).
The quarantined reader is a second model with no tools and structured output."""
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from .guard import guard_action
from .quarantine import SpecRecord

# --8<-- [start:injection-langgraph]
reader = init_chat_model("openai:gpt-6.2-sol").with_structured_output(SpecRecord)


@tool
def set_price(price_cents: int) -> dict:
    """Set the listing price in cents."""
    # A refusal is returned to the model as the tool result, not raised.
    return guard_action({"tool": "set_price", "price_cents": price_cents},
                        untrusted_read=True)


agent = create_agent("openai:gpt-6.2-sol", tools=[set_price])
# record = reader.invoke(raw_sheet)   # quarantined: no tools, typed output
# agent.invoke({"messages": [("user", privileged_prompt(record))]})
# --8<-- [end:injection-langgraph]

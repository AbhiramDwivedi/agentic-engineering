"""MCP consumer with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call. The raw-SDK
variants are helpdesk_mcp_responses.py (OpenAI Responses) and
helpdesk_mcp_example.py (Anthropic Messages).

Shows a LangGraph node driving the merchant helpdesk through an MCP session.
The trust guards (description check, consent gate, result validation,
stale-cache detection) live in guard.py and client.py; this file wires them
into a LangGraph tool node.
"""
from __future__ import annotations

import asyncio

from langchain.agents import create_agent
from langchain.tools import tool

from .client import DocsMCPSession, run_with_server
from .docs_server import make_docs_server


# --8<-- [start:mcp-langgraph]
# Build a LangGraph tool that delegates to the MCP docs server.
# The MCP session is kept alive for the duration of the agent run;
# in production it would be a long-lived connection managed by the host.

_server = make_docs_server()


@tool(parse_docstring=True)
def search_merchant_docs(query: str) -> str:
    """Search Stockwell merchant docs for a policy or how-to question.

    Args:
        query: the merchant's question or keyword.
    """
    async def _call(session: DocsMCPSession) -> str:
        return await session.call("search_docs", {"query": query})

    return asyncio.run(run_with_server(_server, _call))


agent = create_agent("openai:gpt-5.5", tools=[search_merchant_docs])

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "How do I set a MAP rule on my Stockwell storefront?",
    }]
})
print(result["messages"][-1].content)
# --8<-- [end:mcp-langgraph]

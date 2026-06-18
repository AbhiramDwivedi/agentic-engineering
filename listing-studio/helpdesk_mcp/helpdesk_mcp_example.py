"""MCP consumer with the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is helpdesk_mcp_langgraph.py; this is the Anthropic Messages variant.
"""
from __future__ import annotations

import asyncio
import json

import anthropic

from .client import DocsMCPSession, run_with_server
from .docs_server import make_docs_server

client = anthropic.Anthropic()
_server = make_docs_server()


# --8<-- [start:mcp-anthropic]
SEARCH_DOCS_TOOL = {
    "name": "search_merchant_docs",
    "description": "Search Stockwell merchant docs for a policy or how-to question.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
        "additionalProperties": False,
    },
}

reply = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[SEARCH_DOCS_TOOL],
    messages=[{
        "role": "user",
        "content": "How do I set a MAP rule on my Stockwell storefront?",
    }],
)

for block in reply.content:
    if block.type == "tool_use" and block.name == "search_merchant_docs":
        async def _call(session: DocsMCPSession) -> str:
            return await session.call("search_docs", {"query": block.input["query"]})

        tool_output = asyncio.run(run_with_server(_server, _call))
        print("Doc result:", tool_output)
# --8<-- [end:mcp-anthropic]

"""MCP consumer with the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call. The default
pane is helpdesk_mcp_langgraph.py; this is the OpenAI Responses variant.

Note on OpenAI hosted MCP: OpenAI also offers a hosted MCP integration via
the Responses API (`tools=[{"type": "mcp", ...}]`) where OpenAI runs the
MCP client for you. That is an aside — this file shows the spec-level
reference client pattern, which works against any MCP server.
"""
from __future__ import annotations

import asyncio
import json

from openai import OpenAI

from .client import DocsMCPSession, run_with_server
from .docs_server import make_docs_server

client = OpenAI()
_server = make_docs_server()


# --8<-- [start:mcp-responses]
# OpenAI Responses API: MCP tool as a manually-wired function.
# This shows the reference-client pattern (spec-level); for OpenAI's
# hosted-MCP shorthand see vendor docs.

SEARCH_DOCS_TOOL = {
    "type": "function",
    "name": "search_merchant_docs",
    "description": "Search Stockwell merchant docs for a policy or how-to question.",
    "parameters": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
        "additionalProperties": False,
    },
}

response = client.responses.create(
    model="gpt-5.5",
    input=[{
        "role": "user",
        "content": "How do I set a MAP rule on my Stockwell storefront?",
    }],
    tools=[SEARCH_DOCS_TOOL],
)

for item in response.output:
    if item.type == "function_call" and item.name == "search_merchant_docs":
        args = json.loads(item.arguments)

        async def _call(session: DocsMCPSession) -> str:
            return await session.call("search_docs", {"query": args["query"]})

        tool_output = asyncio.run(run_with_server(_server, _call))
        print("Doc result:", tool_output)
# --8<-- [end:mcp-responses]

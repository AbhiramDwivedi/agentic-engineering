"""A tiny in-memory MCP server that exposes Stockwell merchant docs.

Used in tests and the companion demo. Runs in-process through the real mcp
SDK's memory transport — no network, no subprocess, fully offline.

The merchant helpdesk asks this server for docs; the server exposes one
action tool (`update_listing_status`) to demonstrate the consent gate.
"""
from __future__ import annotations

import json

from mcp import types
from mcp.server.lowlevel import Server

# ---------------------------------------------------------------------------
# Fake docs corpus (in-process stand-in for a real retrieval store).
# ---------------------------------------------------------------------------

_DOCS: dict[str, str] = {
    "map-rules": (
        "MAP rules: suppliers set a minimum advertised price. Stockwell "
        "enforces MAP on all listings. Breach voids the supply agreement."
    ),
    "listing-status": (
        "Listing status flow: draft → review → published. "
        "A listing must pass compliance checks before moving to review."
    ),
    "returns-policy": (
        "Returns: merchants may configure a 30-day or 60-day window. "
        "Oversized items (>150 lb) require freight-return approval."
    ),
}


# ---------------------------------------------------------------------------
# Server factory — returns a configured lowlevel Server instance.
# ---------------------------------------------------------------------------

def make_docs_server() -> Server:
    """Return a fully-wired MCP docs server (no transport attached yet)."""
    server = Server("stockwell-docs")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="search_docs",
                description=(
                    "Search Stockwell merchant documentation. "
                    "Returns the most relevant doc excerpt for the query."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query.",
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(
                name="update_listing_status",
                description=(
                    "PRIVILEGED: move a listing from 'draft' to 'review'. "
                    "Requires explicit merchant approval before execution."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "supplier_sku": {"type": "string"},
                        "new_status": {
                            "type": "string",
                            "enum": ["review"],
                        },
                    },
                    "required": ["supplier_sku", "new_status"],
                    "additionalProperties": False,
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent]:
        if name == "search_docs":
            query = arguments.get("query", "").lower()
            for key, text in _DOCS.items():
                if any(word in text.lower() for word in query.split()):
                    return [types.TextContent(type="text", text=text)]
            return [types.TextContent(type="text", text="No matching docs found.")]

        if name == "update_listing_status":
            sku = arguments["supplier_sku"]
            status = arguments["new_status"]
            # This tool is gated by the consent hook on the client side.
            # If it is reached here, consent was already granted.
            return [types.TextContent(
                type="text",
                text=json.dumps({"ok": True, "supplier_sku": sku, "new_status": status}),
            )]

        raise ValueError(f"Unknown tool: {name!r}")

    return server

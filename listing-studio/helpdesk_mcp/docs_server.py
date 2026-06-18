"""A tiny in-memory MCP server that exposes Stockwell merchant docs.

Used in tests and the companion demo. Runs in-process through the real mcp
SDK's memory transport — no network, no subprocess, fully offline.

The merchant helpdesk asks this server for docs; the server exposes one
action tool (`update_listing_status`) to demonstrate the consent gate.

Server-author duties demonstrated here (per the MCP spec server MUSTs):
- Input schema AS the validation contract (list_tools).
- Application-level validation beyond what JSON schema expresses:
  empty/oversized strings, SKU format, unknown tool names.
- Structured errors (isError=True) — never raw stack traces back to the client.
- Sanitised output — no raw user input echoed in error messages.
"""
from __future__ import annotations

import json
import re

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

# Application-level limits (beyond what JSON schema expresses).
_QUERY_MAX_LEN = 500
_SKU_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9\-]{1,63}$")
_VALID_STATUSES = {"review"}


def _error(text: str) -> list[types.TextContent]:
    """Return a structured, sanitised error block (isError handled by caller)."""
    return [types.TextContent(type="text", text=text)]


# ---------------------------------------------------------------------------
# Server factory — returns a configured lowlevel Server instance.
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-server-expose]
def make_docs_server() -> Server:
    """Return a fully-wired MCP docs server (no transport attached yet).

    The server author's duties start here:
    - You choose what to expose (two tools, not the whole internal API).
    - The inputSchema is the validation contract: required fields, types,
      and enums declared here are checked by the SDK before call_tool runs.
    - PRIVILEGED tools are labelled in their description so every client
      can surface the consent gate without parsing business logic.
    """
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
                            "description": "The search query (1–500 characters).",
                            "minLength": 1,
                            "maxLength": _QUERY_MAX_LEN,
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
                        "supplier_sku": {
                            "type": "string",
                            "description": "Supplier SKU (uppercase letters, digits, hyphens).",
                            "pattern": r"^[A-Z0-9][A-Z0-9\-]{1,63}$",
                        },
                        "new_status": {
                            "type": "string",
                            "enum": list(_VALID_STATUSES),
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
    ) -> list[types.TextContent] | types.CallToolResult:
        return await _dispatch(name, arguments)

    return server
# --8<-- [end:mcp-server-expose]


# --8<-- [start:mcp-server-validate]
async def _dispatch(
    name: str, arguments: dict
) -> list[types.TextContent] | types.CallToolResult:
    """Route a validated call and apply application-level checks.

    The SDK's validate_input=True (the default) already enforces the JSON
    schema declared in list_tools — required fields, types, enum values,
    additionalProperties. This function adds the checks that live above the
    schema layer: string emptiness, length limits, SKU format, and unknown
    tool names. All failures return a structured CallToolResult(isError=True);
    no raw exception or user input reaches the client.
    """
    if name == "search_docs":
        query = arguments.get("query", "")
        # Application checks beyond the schema's minLength/maxLength.
        if not query.strip():
            return types.CallToolResult(
                isError=True,
                content=_error("search_docs: query must not be blank"),
            )
        if len(query) > _QUERY_MAX_LEN:
            return types.CallToolResult(
                isError=True,
                content=_error(
                    f"search_docs: query exceeds {_QUERY_MAX_LEN}-character limit"
                ),
            )
        # Search — return the first matching doc excerpt.
        for _key, text in _DOCS.items():
            if any(word in text.lower() for word in query.lower().split()):
                return [types.TextContent(type="text", text=text)]
        return [types.TextContent(type="text", text="No matching docs found.")]

    if name == "update_listing_status":
        sku = arguments.get("supplier_sku", "")
        status = arguments.get("new_status", "")
        # Enum and SKU shape are enforced by the JSON schema; these checks
        # are a defensive second layer — reject anything that slips through.
        if status not in _VALID_STATUSES:
            return types.CallToolResult(
                isError=True,
                content=_error(
                    f"update_listing_status: new_status must be one of "
                    f"{sorted(_VALID_STATUSES)}"
                ),
            )
        if not _SKU_PATTERN.match(sku):
            return types.CallToolResult(
                isError=True,
                content=_error(
                    "update_listing_status: supplier_sku must be "
                    "uppercase letters, digits, and hyphens (2–64 chars)"
                ),
            )
        # Consent was already granted by the client-side gate before this call.
        return [types.TextContent(
            type="text",
            text=json.dumps(
                {"ok": True, "supplier_sku": sku, "new_status": status}
            ),
        )]

    # Unknown tool: return a structured error, never raise.
    return types.CallToolResult(
        isError=True,
        content=_error(f"unknown tool {name!r}"),
    )
# --8<-- [end:mcp-server-validate]

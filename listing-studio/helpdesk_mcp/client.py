"""MCP consumer: connect, list tools, call a tool, guard results.

The merchant helpdesk connects to a docs MCP server (stockwell-docs) and:
  1. Initialises a session and lists the available tools.
  2. Guards each tool description against injection before using it.
  3. Applies the consent gate before calling any privileged/destructive tool.
  4. Validates tool results before they enter model context.
  5. Returns a structured, recoverable message on any failure.

Uses the real mcp Python SDK (mcp>=1.0). The transport is an in-memory
stream pair for offline testing; in production it would be stdio or
Streamable HTTP.

Chapter 2.4 owns the trust model here. For the general tool-call contract
see 2.1; for the consent gate in depth see 4.3.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

import anyio
from mcp import ClientSession, types
from mcp.server.lowlevel import Server
from mcp.shared.memory import create_client_server_memory_streams

from .guard import (
    check_description_for_injection,
    check_tool_list_staleness,
    validate_tool_result,
)


# ---------------------------------------------------------------------------
# Consent gate
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-consent]
# Privileged tools require explicit approval before they run.
# The gate is a callable so it can be swapped for a real UI prompt in production.
PRIVILEGED_TOOLS = {"update_listing_status"}  # destructive or privileged actions


def require_consent(
    tool_name: str,
    arguments: dict,
    *,
    approve: Callable[[str, dict], bool],
) -> bool:
    """Human gate for privileged MCP tool calls.

    Returns True only if the tool is not privileged or the approval callback
    grants consent. Never calls a destructive tool silently.

    `approve` is the seam: in production it shows a UI confirmation; in tests
    it is a simple lambda. See also 4.3 Human-in-the-Loop.
    """
    if tool_name not in PRIVILEGED_TOOLS:
        return True
    return approve(tool_name, arguments)
# --8<-- [end:mcp-consent]


# ---------------------------------------------------------------------------
# Failure return contract
# ---------------------------------------------------------------------------

def _mcp_error(context: str, detail: str) -> str:
    """Return a structured, recoverable error message for the model.

    Never raises. The model receives a human-readable explanation it can
    act on: retry with different parameters, escalate, or tell the user.
    """
    return (
        f"[mcp-error] {context}: {detail}. "
        "The MCP call did not produce a usable result."
    )


# ---------------------------------------------------------------------------
# Session façade — usable in tests (in-memory) and in production (stdio/HTTP)
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-connect]
@dataclass
class DocsMCPSession:
    """A live session to the stockwell-docs MCP server.

    Wraps a ClientSession with the trust guards the chapter requires:
    - description injection check on connect (list_tools)
    - consent gate on privileged call_tool
    - result validation before the result enters model context
    - stale-cache detection when tool list refreshes
    """
    _session: ClientSession
    _tool_cache: list[str] = field(default_factory=list)

    async def connect(self) -> None:
        """Initialise the session and load + guard the tool list."""
        await self._session.initialize()
        await self._refresh_tools()

    async def _refresh_tools(self) -> None:
        resp = await self._session.list_tools()
        current_names = [t.name for t in resp.tools]
        if self._tool_cache:
            # Guard against rug pulls: flag if the list changed since last fetch.
            staleness = check_tool_list_staleness(self._tool_cache, current_names)
            if not staleness.ok:
                raise RuntimeError(staleness.error)
        # Guard tool descriptions against injection before caching.
        for t in resp.tools:
            check = check_description_for_injection(t.description or "")
            if not check.ok:
                raise RuntimeError(
                    f"tool {t.name!r} description rejected: {check.error}"
                )
        self._tool_cache = current_names

    async def call(
        self,
        tool_name: str,
        arguments: dict,
        *,
        approve: Callable[[str, dict], bool] = lambda _n, _a: False,
        expected_result_keys: list[str] | None = None,
    ) -> str:
        """Call a tool, applying the consent gate and result validation.

        Returns the tool's text output on success, or a structured error
        message the model can act on.
        """
        if not require_consent(tool_name, arguments, approve=approve):
            return _mcp_error(
                tool_name,
                "consent denied — privileged tool call blocked by human gate",
            )

        try:
            result = await self._session.call_tool(tool_name, arguments)
        except Exception as exc:
            return _mcp_error(tool_name, f"server unreachable or error: {exc}")

        if result.isError:
            return _mcp_error(tool_name, f"server returned an error result")

        # Extract text content from the result list.
        text_parts = [
            c.text for c in result.content if isinstance(c, types.TextContent)
        ]
        raw_text = "\n".join(text_parts)

        # Validate result shape before passing to the model (optional).
        if expected_result_keys:
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError:
                # Non-JSON result: shape validation skipped; pass through.
                return raw_text
            guard = validate_tool_result(parsed, expected_result_keys)
            if not guard.ok:
                return _mcp_error(tool_name, guard.error or "result validation failed")

        return raw_text
# --8<-- [end:mcp-connect]


# ---------------------------------------------------------------------------
# Convenience: run a session against a server in-memory (used by tests)
# ---------------------------------------------------------------------------

async def run_with_server(
    server: Server,
    coro_fn,
):
    """Run coro_fn(DocsMCPSession) against server over in-memory streams.

    Offline helper for tests and the companion demo. coro_fn receives a
    connected DocsMCPSession; it should perform its calls and return a result.
    """
    # Capture the result in a list so the cancel_scope does not discard it.
    _result: list = []

    async with create_client_server_memory_streams() as (client_streams, server_streams):
        async with anyio.create_task_group() as tg:
            async def _run_server():
                await server.run(
                    server_streams[0],
                    server_streams[1],
                    server.create_initialization_options(),
                    raise_exceptions=True,
                )

            tg.start_soon(_run_server)

            async with ClientSession(
                client_streams[0], client_streams[1]
            ) as raw_session:
                session = DocsMCPSession(_session=raw_session)
                await session.connect()
                _result.append(await coro_fn(session))
                tg.cancel_scope.cancel()

    return _result[0] if _result else None

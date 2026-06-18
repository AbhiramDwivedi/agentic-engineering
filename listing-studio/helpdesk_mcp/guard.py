"""Trust guards for MCP tool results and descriptions.

Three guards, each testable offline without any MCP server:

1. **Result validation** — validate a tool result against an expected schema
   before it enters the model's context. An injected or malformed result does
   not reach the model. (Cross-refs 2.2 Structured Output.)

2. **Tool-poisoning description check** — tool *descriptions* are untrusted
   input from the server. Scan for imperative instructions in a description
   before accepting it; a poisoned description can hijack the model.

3. **Staleness check** — a cached tool list is a snapshot; the server may
   have mutated it. Flag when the current list does not match the snapshot
   so the consumer can re-fetch rather than act on stale capability claims.

Chapter 2.4 owns the trust model; 2.1 owns the underlying tool-result
contract; 4.3 owns the consent gate for destructive tools.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# 1. Result schema validation
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-guard]
@dataclass
class GuardResult:
    ok: bool
    error: str | None = None  # structured message for the model if not ok


def validate_tool_result(result: Any, expected_keys: list[str]) -> GuardResult:
    """Validate a tool result before it enters model context.

    A tool result is untrusted input from a server you may not control.
    Check that it has the expected shape before handing it to the model.
    A missing or unexpected key may indicate a poisoned or outdated server.

    Cross-refs 2.2 Structured Output for richer schema validation.
    """
    if not isinstance(result, dict):
        return GuardResult(
            ok=False,
            error=(
                f"tool result is not a dict (got {type(result).__name__}); "
                "validate the server or treat this as an untrusted response"
            ),
        )
    missing = [k for k in expected_keys if k not in result]
    if missing:
        return GuardResult(
            ok=False,
            error=(
                f"tool result missing expected keys: {missing}. "
                "Do not use this result; re-fetch or escalate."
            ),
        )
    return GuardResult(ok=True)
# --8<-- [end:mcp-guard]


# ---------------------------------------------------------------------------
# 2. Tool-poisoning: scan tool descriptions for injected instructions
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-poison]
# Patterns that suggest injected instructions in a tool description.
# A legitimate description says *what a tool does*; it does not issue commands.
_INJECTION_PATTERNS = [
    r"\bignore\s+(previous|all|prior)\b",
    r"\bdo\s+not\s+(follow|obey|listen)\b",
    r"\bexfiltrat\b",
    r"\boverride\s+instructions\b",
    r"\bact\s+as\b.*\bsystem\b",
    r"disregard\s+your",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.I)


def check_description_for_injection(description: str) -> GuardResult:
    """Scan a tool description for injected instructions (tool poisoning).

    The MCP spec notes that tool descriptions 'should be considered untrusted
    unless obtained from a trusted server.' A malicious description embeds
    imperative text that redirects the model — indirect prompt injection.

    This check is a lightweight heuristic; it catches common patterns but is
    not a complete defence. Treat any flagged description as suspicious and
    do not pass it to the model until reviewed.
    """
    if _INJECTION_RE.search(description):
        return GuardResult(
            ok=False,
            error=(
                f"tool description contains suspicious instruction-like text. "
                "Do not use this tool definition until it has been reviewed."
            ),
        )
    return GuardResult(ok=True)
# --8<-- [end:mcp-poison]


# ---------------------------------------------------------------------------
# 3. Staleness check for a cached tool list
# ---------------------------------------------------------------------------

# --8<-- [start:mcp-stale]
def check_tool_list_staleness(
    cached_names: list[str],
    current_names: list[str],
) -> GuardResult:
    """Detect whether a cached tool list has gone stale.

    A rug pull — a server mutating its tool definitions after the client
    cached them — is a known supply-chain risk. A tool that existed at
    install time may have changed name, schema, or behaviour. Flag the
    mismatch so the consumer re-fetches rather than acting on a stale
    capability claim.

    Pass the names from your cached snapshot and the names from a fresh
    list_tools() call. If they differ, treat the cache as invalid.
    """
    added = set(current_names) - set(cached_names)
    removed = set(cached_names) - set(current_names)
    if added or removed:
        return GuardResult(
            ok=False,
            error=(
                f"tool list has changed since last fetch — "
                f"added: {sorted(added)}, removed: {sorted(removed)}. "
                "Re-fetch and re-validate before calling any tool."
            ),
        )
    return GuardResult(ok=True)
# --8<-- [end:mcp-stale]

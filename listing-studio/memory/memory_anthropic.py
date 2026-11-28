"""Anthropic memory tool: the model issues file commands, your handler backs them.

Illustration, not run in CI: needs an API key and a network call.
The default pane is memory_langgraph.py; this is the Anthropic Messages variant.
"""
from __future__ import annotations

import anthropic

client = anthropic.Anthropic()


# --8<-- [start:memory-anthropic]
def safe_path(path: str) -> str:
    """The handler's job: refuse anything outside /memories."""
    import posixpath
    if "\\" in path or "%" in path:            # no Windows separators, no encoding
        raise ValueError("path must stay inside /memories")
    clean = posixpath.normpath(path)
    if clean != "/memories" and not clean.startswith("/memories/"):
        raise ValueError("path must stay inside /memories")
    return clean


message = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=2048,
    messages=[{"role": "user", "content": "My garage is 200 sq ft. Remember it."}],
    tools=[{"type": "memory_20250818", "name": "memory"}],
)
for block in message.content:
    if block.type == "tool_use" and block.name == "memory":
        # block.input["command"] is view, create, str_replace, insert, delete or
        # rename. Check every path it names (rename has two), then run it against
        # your own storage with a size cap and reply with a tool_result.
        try:
            for field in ("path", "old_path", "new_path"):
                if field in block.input:
                    safe_path(block.input[field])
        except ValueError as err:
            reply = {"type": "tool_result", "tool_use_id": block.id,
                     "content": str(err), "is_error": True}
# --8<-- [end:memory-anthropic]

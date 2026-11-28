"""Hooks: code that runs at fixed points in the loop, outside the model."""
from __future__ import annotations

from typing import Callable

# A pre_tool hook returns None (no opinion) or (verdict, reason).
PreHook = Callable[[str, dict], "tuple[str, str] | None"]
SEVERITY = {"allow": 0, "ask": 1, "deny": 2}


# --8<-- [start:hook]
def combine(policy: tuple[str, str], hooks: list[PreHook], tool: str, args: dict):
    """Strictest verdict wins, so a hook's allow never beats a deny or an ask.
    A hook that raises counts as a deny: the run fails closed."""
    verdict, reason = policy
    for hook in hooks:
        try:
            out = hook(tool, args)
        except Exception as exc:                    # fail closed, on purpose
            out = ("deny", f"hook {hook.__name__} failed: {exc!r}")
        if out and SEVERITY[out[0]] > SEVERITY[verdict]:
            verdict, reason = out
    return verdict, reason


def post_tool(hooks: list[Callable[[str, dict], "str | None"]], tool, result):
    """Check a tool's output before the model sees it; a string is an error."""
    for hook in hooks:
        try:
            problem = hook(tool, result)
        except Exception as exc:
            problem = f"post hook {hook.__name__} failed: {exc!r}"
        if problem:
            return problem
    return None
# --8<-- [end:hook]

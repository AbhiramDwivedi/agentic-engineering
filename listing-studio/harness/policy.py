"""Permission policy: deny / ask / allow, first match wins, default deny."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# --8<-- [start:policy]
@dataclass(frozen=True)
class Rule:
    verdict: str                         # "deny" | "ask" | "allow"
    tool: str                            # tool name, or "*"
    when: Callable[[dict], bool] = lambda args: True


def decide(rules: list[Rule], tool: str, args: dict) -> tuple[str, str]:
    """First matching rule wins. No match means deny, never allow."""
    for rule in rules:
        if rule.tool in (tool, "*") and rule.when(args):
            return rule.verdict, f"rule: {rule.verdict} {rule.tool}"
    return "deny", f"no rule allows {tool}; default is deny"


def session_tools(all_tools: dict, wanted: set[str]) -> dict:
    """Absent beats denied: a tool left out of the session is never offered
    to the model, so there is nothing to ask for or argue about."""
    return {name: fn for name, fn in all_tools.items() if name in wanted}
# --8<-- [end:policy]

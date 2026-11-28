"""Policy: what a sandbox may touch, and a fake backend that enforces it."""
from __future__ import annotations

# --8<-- [start:sandbox-policy]
import re
from dataclasses import dataclass

from .contract import ExecResult, bound


class PolicyError(ValueError):
    """The configuration itself is unsafe; refused before any code runs."""


@dataclass(frozen=True)
class Policy:
    allowed_paths: tuple[str, ...] = ("/workspace/",)
    allow_egress: bool = False
    mounts_private_data: bool = False

    def __post_init__(self) -> None:
        if self.mounts_private_data and self.allow_egress:
            raise PolicyError("private data and an outbound channel in one sandbox")

    def path_ok(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.allowed_paths) and ".." not in path
# --8<-- [end:sandbox-policy]


# --8<-- [start:sandbox-fake]
# Matches open('...') and fetch('...') / connect('...') calls written as literals.
_OPEN = re.compile(r"open\(['\"]([^'\"]+)['\"]")
_NET = re.compile(r"(?:fetch|connect)\(['\"]([^'\"]+)['\"]")


class PolicyBackend:
    """Regex-scans code for file and network intents; not OS-enforced."""

    def __init__(self, policy: Policy) -> None:
        self.policy = policy

    def run(self, code: str, timeout_s: float) -> ExecResult:
        for path in _OPEN.findall(code):
            if not self.policy.path_ok(path):
                return ExecResult(1, "", f"denied: path {path}")
        if _NET.search(code) and not self.policy.allow_egress:
            return ExecResult(1, "", "denied: network egress")
        out, cut = bound(f"ran {len(code)} chars")
        return ExecResult(0, out, "", truncated=cut)
# --8<-- [end:sandbox-fake]

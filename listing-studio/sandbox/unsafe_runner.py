"""The UNSAFE comparison: a bare subprocess with a timeout. No isolation."""
from __future__ import annotations

# --8<-- [start:sandbox-unsafe]
import subprocess
import sys

from .contract import ExecResult, bound


class UnsafeSubprocessBackend:
    """Same contract, no containment: the child inherits files, network and env."""

    def run(self, code: str, timeout_s: float) -> ExecResult:
        try:
            p = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(None, "", "timed out", timed_out=True)
        out, c1 = bound(p.stdout)
        err, c2 = bound(p.stderr)
        return ExecResult(p.returncode, out, err, truncated=c1 or c2)
# --8<-- [end:sandbox-unsafe]

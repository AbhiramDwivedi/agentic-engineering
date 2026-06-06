from typing import Optional, Protocol

from pydantic import BaseModel

from .models import PriceCheckRequest


# --8<-- [start:protocol]
class ToolCall(BaseModel):
    """The model's decision: call this tool with these typed args."""

    name: str
    request: PriceCheckRequest


class ModelClient(Protocol):
    """The boundary. A real impl wraps an LLM; the fake returns a script.

    propose() returns a ToolCall when the model decides to use a tool, or a
    final price in cents (int) when it decides to answer directly.
    """

    def propose(
        self, prompt: str, last_verdict: Optional[dict]
    ) -> "ToolCall | int": ...
# --8<-- [end:protocol]


class FakeModel:
    """A scripted model for tests. No network, fully deterministic."""

    def __init__(self, script: list):
        self._script = list(script)

    def propose(
        self, prompt: str, last_verdict: Optional[dict] = None
    ) -> "ToolCall | int":
        return self._script.pop(0)

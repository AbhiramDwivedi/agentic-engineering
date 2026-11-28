"""One UI event vocabulary, so the front end never learns a provider's stream."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# --8<-- [start:stream-vocabulary]
class UIEvent(BaseModel):
    kind: Literal["text", "thinking", "tool_call", "tool_result", "approval", "done", "error"]
    text: str = ""          # text / thinking delta, or an error message
    call_id: str = ""       # tool_call, tool_result, approval
    tool: str = ""
    args: dict = {}
    ok: bool = True         # tool_result only
# --8<-- [end:stream-vocabulary]

"""The same deny rule as a LangChain/LangGraph middleware (the chapter's
first framework example): wrap_tool_call sees every tool call before it runs and may
return a ToolMessage instead of calling the handler.

Illustration, not run in CI: needs langchain and a model key. Compile-checked
only. Names (wrap_tool_call, ToolCallRequest, create_agent) checked against
docs.langchain.com/oss/python/langchain/middleware/custom on 2026-11-28; ToolCall["id"] and ToolMessage(status="error") checked
against installed langchain-core 1.4.7 and langgraph's ToolCallRequest.
"""
from __future__ import annotations

from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command

from .scenario import RULES, read_supplier_row, write_draft
from .policy import decide


# --8<-- [start:harness-langgraph]
@wrap_tool_call
def enforce_policy(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    verdict, reason = decide(RULES, request.tool_call["name"], request.tool_call["args"])
    if verdict != "allow":                # an ask needs an approver; here: refuse
        return ToolMessage(content=f"error: {reason}",
                           tool_call_id=request.tool_call["id"], status="error")
    return handler(request)


agent = create_agent(
    "openai:gpt-6.2-sol",
    tools=[read_supplier_row, write_draft],     # publish is not in the list
    middleware=[enforce_policy],
)
# --8<-- [end:harness-langgraph]

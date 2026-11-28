"""The harness side: approval gate and the UI state that only tool results can finish."""
from __future__ import annotations

from .events import UIEvent

# Tools that change the world wait for a person. The rule lives here, in code,
# not in a prompt.
NEEDS_APPROVAL = {"update_price"}


# --8<-- [start:stream-approval]
def run_tool_call(call: UIEvent, tools: dict, approve):
    """Yield the UI events for one tool call; write tools wait for a human."""
    if call.tool in NEEDS_APPROVAL:
        yield UIEvent(kind="approval", call_id=call.call_id, tool=call.tool, args=call.args)
        if not approve(call):  # the person said no: the tool never runs
            yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool,
                          ok=False, text="declined")
            return
    try:
        out = tools[call.tool](**call.args)
        yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool, text=str(out))
    except Exception as exc:  # a failed tool must still end the step visibly
        yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool,
                      ok=False, text=str(exc))
# --8<-- [end:stream-approval]


# --8<-- [start:stream-ui-state]
def reduce(state: dict, e: UIEvent) -> dict:
    """The UI shows a step as done only when the harness reports a tool result."""
    if e.kind == "text":
        state["transcript"] += e.text  # model prose: display only
    elif e.kind == "tool_call":
        state["steps"][e.call_id] = "running"
    elif e.kind == "approval":
        state["steps"][e.call_id] = "awaiting approval"
    elif e.kind == "tool_result":
        state["steps"][e.call_id] = "done" if e.ok else "failed"
    elif e.kind == "error":  # the stream or a call broke: no step may keep spinning
        state["error"] = e.text
        for call_id, step in state["steps"].items():
            if step in ("running", "awaiting approval"):
                state["steps"][call_id] = "failed"
        if e.call_id:
            state["steps"][e.call_id] = "failed"
    return state
# --8<-- [end:stream-ui-state]


# --8<-- [start:stream-consumer]
def run_turn(provider_events, translate, tools, approve, state):
    """One model response: translate it, run each tool call, fold every event into state."""
    def emit(ui):
        reduce(state, ui)
        return ui  # in a web app, also send it to the browser as one SSE `data:` line
    for e in translate(provider_events):
        yield emit(e)
        if e.kind == "tool_call":
            for ui in run_tool_call(e, tools, approve):
                yield emit(ui)
# --8<-- [end:stream-consumer]

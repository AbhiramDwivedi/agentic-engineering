"""A small agent loop with the harness seats wired in.

NOTE: local copy. Chapter 2.5 (the agent loop) is not merged yet, so this is a
self-contained stand-in; swap it for 2.5's loop once that ships. The model is
any callable (messages, tool_names) -> Turn, so tests use a scripted fake.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .compact import compact
from .hook import combine, post_tool
from .policy import decide
from .trace import Trace


@dataclass
class Call:
    name: str
    args: dict


@dataclass
class Turn:
    text: str = ""
    calls: list[Call] = field(default_factory=list)
    cost_cents: int = 0


@dataclass
class Result:
    stop_reason: str
    messages: list[dict]
    trace: Trace
    spent_cents: int


# --8<-- [start:loop]
def run(model, tools, rules, messages, limits, *, pre=(), post=(), on_stop=None,
        approve=lambda tool, args: False, archive=lambda msgs: None,
        max_messages=12, keep_last=4) -> Result:
    trace, steps, spent = Trace(), 0, 0
    while True:
        if (why := limits.stop_reason(steps, spent)) is not None:
            trace.record(steps, "limit", why, "stop")
            return Result(why, messages, trace, spent)
        turn = model(messages, list(tools))
        steps, spent = steps + 1, spent + turn.cost_cents
        messages.append({"role": "assistant", "content": turn.text})
        for call in turn.calls:
            if call.name not in tools:                    # absent, not denied
                out, outcome = f"error: no such tool {call.name!r}", "absent"
            else:
                verdict, reason = combine(decide(rules, call.name, call.args),
                                          list(pre), call.name, call.args)
                if verdict == "ask" and approve(call.name, call.args):
                    verdict = "allow"
                if verdict == "allow":
                    out, outcome = tools[call.name](**call.args), "allow"
                    if (bad := post_tool(list(post), call.name, out)):
                        out, outcome = f"error: {bad}", "post_blocked"
                else:
                    out, outcome = f"error: {reason}", verdict   # denial is a result
            trace.record(steps, "tool", call.name, outcome)
            messages.append({"role": "tool", "content": str(out),
                             "is_error": str(out).startswith("error:")})
        if not turn.calls:                                # model says it is done
            note = on_stop(messages) if on_stop else None
            if not note:
                return Result("done", messages, trace, spent)
            messages.append({"role": "user", "content": note})
        messages[:] = compact(messages, max_messages, keep_last, archive)
# --8<-- [end:loop]

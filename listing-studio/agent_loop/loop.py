"""The agent loop that reports why it ended (chapter 2.5).

2.1 shows the basic loop. This one returns a Result that names the exit, so a
truncated reply, a stuck model, a false "done" and a hit cap are never mistaken
for an answer. The model is any function history -> Turn, so the tests script it
and each provider tab only has to map its response onto a Turn.
"""
import json
from collections import Counter
from dataclasses import dataclass

# --8<-- [start:loop-types]
CONTINUE, END = "tool_use", "end"  # the two stops that are not trouble

# The five ways a run ends. Only CLEAN is an answer.
CLEAN, ABNORMAL, STALLED, FALSE_DONE, CEILING = (
    "clean", "abnormal_stop", "stalled", "false_done", "ceiling",
)


@dataclass
class Call:
    id: str
    name: str
    args: dict


@dataclass
class Turn:  # one model reply, whichever provider produced it
    text: str
    calls: list
    stop: str  # CONTINUE, END, or the provider's own reason (max_tokens, refusal...)


@dataclass
class Result:
    exit: str  # one of the five above
    answer: str | None
    steps: int
    detail: str = ""  # the stop reason (ABNORMAL) or the claim (FALSE_DONE)
# --8<-- [end:loop-types]


# --8<-- [start:loop-run]
def run_tool(tools: dict, call: Call) -> tuple[str, bool]:
    """Return (content, is_error). A failure goes back to the model as a result."""
    try:
        return json.dumps(tools[call.name](**call.args)), False
    except Exception as exc:  # timeout, bad arguments, unknown tool
        return f"{type(exc).__name__}: {exc}", True


def run_loop(model, tools, history, verify, max_steps=8, max_repeats=3) -> Result:
    failures = Counter()  # how often each exact call has failed
    for step in range(1, max_steps + 1):
        turn = model(history)
        history.append({"role": "assistant", "text": turn.text, "calls": turn.calls})
        if turn.stop == END:
            # The model says it is done. Your code checks the claim.
            if verify():
                return Result(CLEAN, turn.text, step)
            return Result(FALSE_DONE, None, step, detail=turn.text)  # a claim, kept for logs
        if turn.stop != CONTINUE:
            # Truncated, refused, paused: no tool call, and no answer.
            return Result(ABNORMAL, None, step, detail=turn.stop)
        for call in turn.calls:
            content, is_error = run_tool(tools, call)
            history.append(
                {"role": "tool", "id": call.id, "content": content, "is_error": is_error}
            )
            if is_error:
                failures[(call.name, json.dumps(call.args, sort_keys=True))] += 1
        if max(failures.values(), default=0) >= max_repeats:
            return Result(STALLED, None, step)  # same call, same failure, again
    return Result(CEILING, None, max_steps)  # a cap hit is not "done"
# --8<-- [end:loop-run]

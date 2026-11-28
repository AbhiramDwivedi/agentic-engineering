"""Anthropic Messages mapping for the agent loop. Illustration: the client call
needs a key and a network, so only to_turn is exercised in tests."""
from .loop import CONTINUE, END, Call, Turn


# --8<-- [start:loop-anthropic]
def to_turn(reply) -> Turn:
    """Map a Messages reply onto a Turn. Branch on stop_reason, not on 'no tool_use'."""
    calls = [Call(b.id, b.name, b.input) for b in reply.content if b.type == "tool_use"]
    text = "".join(b.text for b in reply.content if b.type == "text")
    if reply.stop_reason == "tool_use":
        return Turn(text, calls, CONTINUE)
    if reply.stop_reason == "end_turn":
        return Turn(text, calls, END)
    # max_tokens, refusal, pause_turn, model_context_window_exceeded, stop_sequence
    return Turn(text, calls, reply.stop_reason)
# --8<-- [end:loop-anthropic]


def make_model(tool_schemas: list, model: str = "claude-sonnet-5-5"):
    import anthropic

    client = anthropic.Anthropic()

    def ask(history: list) -> Turn:
        messages = []
        for m in history:
            if m["role"] == "user":
                messages.append({"role": "user", "content": m["text"]})
            elif m["role"] == "assistant":
                blocks = ([{"type": "text", "text": m["text"]}] if m["text"] else []) + [
                    {"type": "tool_use", "id": c.id, "name": c.name, "input": c.args}
                    for c in m["calls"]
                ]
                messages.append({"role": "assistant", "content": blocks})
            else:  # a tool result; results for one turn share one user message
                block = {"type": "tool_result", "tool_use_id": m["id"],
                         "content": m["content"], "is_error": m["is_error"]}
                last = messages[-1]
                if last["role"] == "user" and isinstance(last["content"], list):
                    last["content"].append(block)
                else:
                    messages.append({"role": "user", "content": [block]})
        return to_turn(client.messages.create(
            model=model, max_tokens=1024, tools=tool_schemas, messages=messages))

    return ask

"""OpenAI Responses mapping for the agent loop. Illustration: the client call
needs a key and a network, so only to_turn is exercised in tests."""
import json

from .loop import CONTINUE, END, Call, Turn


# --8<-- [start:loop-responses]
def to_turn(response) -> Turn:
    """Map a Responses result onto a Turn. Look at status and refusals, not just calls."""
    calls = [
        Call(i.call_id, i.name, json.loads(i.arguments))
        for i in response.output
        if i.type == "function_call"
    ]
    if calls:
        return Turn(response.output_text, calls, CONTINUE)
    if response.status == "incomplete":  # max_output_tokens, content_filter
        return Turn(response.output_text, [], response.incomplete_details.reason)
    parts = [p for i in response.output if i.type == "message" for p in i.content]
    if any(p.type == "refusal" for p in parts):
        return Turn(response.output_text, [], "refusal")
    return Turn(response.output_text, [], END)
# --8<-- [end:loop-responses]


def make_model(tool_schemas: list, model: str = "gpt-6.2-sol"):
    from openai import OpenAI

    client = OpenAI()

    def ask(history: list) -> Turn:
        items = []
        for m in history:
            if m["role"] == "user":
                items.append({"role": "user", "content": m["text"]})
            elif m["role"] == "assistant":
                if m["text"]:
                    items.append({"role": "assistant", "content": m["text"]})
                items += [
                    {"type": "function_call", "call_id": c.id, "name": c.name,
                     "arguments": json.dumps(c.args)}
                    for c in m["calls"]
                ]
            else:
                items.append({"type": "function_call_output", "call_id": m["id"],
                              "output": m["content"]})
        return to_turn(client.responses.create(model=model, input=items, tools=tool_schemas))

    return ask

"""The editing pass with LangGraph's model interface (the default pane).

Illustration, not run in CI: needs an API key and a network call. It plugs
into the tested polish_checked (polish.py); only the model call changes per
provider, not the fidelity diff.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .polish import polish_checked

llm = init_chat_model("openai:gpt-6.2-sol")

# --8<-- [start:assembly-langgraph]
EDIT_PROMPT = (
    "Edit for one consistent voice. Reword only. Do not add, remove or change "
    "any number, name or [src:...] marker. Return the full text.\n\n"
)


def edit_fn(text: str) -> str:
    return llm.invoke(EDIT_PROMPT + text).content


# polished, problems = polish_checked(edit_fn, assembled.text)
# --8<-- [end:assembly-langgraph]

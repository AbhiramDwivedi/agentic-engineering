"""The judge call with LangGraph's model interface (the default pane).

Illustration, not run in CI: needs an API key and a network call. Each of
the three judge files exposes the same seam, judge(prompt) -> str, which is
what graders.judge_listing injects; only the call shape changes per provider.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-6.2-sol")


# --8<-- [start:evals-judge-langgraph]
def judge(prompt: str) -> str:
    """One isolated yes/no call; no tools, no memory, no say in what runs next."""
    return llm.invoke(prompt).content
# --8<-- [end:evals-judge-langgraph]

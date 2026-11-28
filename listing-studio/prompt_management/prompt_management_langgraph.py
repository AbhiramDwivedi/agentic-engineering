"""Prompt management with LangGraph (default pane). Illustration, not run in CI.

OpenAI Responses and Anthropic Messages variants: prompt_management_responses.py,
prompt_management_example.py.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .release import LIVE_V1


# --8<-- [start:prompt-langgraph]
cfg = LIVE_V1
llm = init_chat_model(cfg.model, temperature=cfg.temperature)
system, user = cfg.prompt.render(copy="The Aldsworth desk, $419.00, SKU NV-ALDSWORTH-DM")
reply = llm.invoke([("system", system), ("user", user)])
# Log cfg.prompt.version beside cfg.model with every call.
# --8<-- [end:prompt-langgraph]

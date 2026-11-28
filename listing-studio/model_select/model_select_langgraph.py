"""Per-step model with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call.
"""
from langchain.chat_models import init_chat_model

from .config import model_for

# --8<-- [start:model-langgraph]
llm = init_chat_model(model_for("categorize"))  # "openai:gpt-6.2-sol"
answer = llm.invoke("Categorize: Aldsworth dual-motor sit-stand desk")
# --8<-- [end:model-langgraph]

"""Observer step with LangGraph (the default the chapter shows).

Illustration, compile-checked only: needs an API key and a network call.
The tested core is events.py; only the stop-reason read changes per provider.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .events import Sink, StepResult, observed_step

llm = init_chat_model("openai:gpt-6.2-sol")


# --8<-- [start:observer-langgraph]
# Stop reasons as OpenAI and Anthropic name them; extend for other providers.
NORMALISED = {
    "length": "max_tokens",
    "max_tokens": "max_tokens",
    "model_context_window_exceeded": "max_tokens",
    "content_filter": "refusal",
    "refusal": "refusal",
}


def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
    def step() -> StepResult:
        message = llm.invoke(f"Write a listing description for {sku}.")
        # LangChain surfaces the provider's stop reason in response_metadata.
        meta = message.response_metadata
        reason = meta.get("finish_reason") or meta.get("stop_reason", "")
        return StepResult(
            text=message.text,
            stop_reason=NORMALISED.get(reason, "end_turn"),
        )

    return observed_step(sinks, run_id, "describe", step)
# --8<-- [end:observer-langgraph]

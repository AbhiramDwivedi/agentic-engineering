"""Structured output with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call. The raw-SDK
variants are structured_output_responses.py (OpenAI Responses) and
structured_output_example.py (Anthropic Messages).

with_structured_output wraps the chat model so it always returns a typed
PricingDecision object. Underneath, LangGraph uses strict json_schema mode —
the same constrained-decoding machinery as tool/function calling, aimed at the
response schema instead of a tool's input schema.
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model

from .schema import PricingDecision


# --8<-- [start:pricing-call]
# init_chat_model + with_structured_output: one line gives the model a contract
# it must fill. The returned object is a typed PricingDecision — no parsing,
# no regex, no free-text wrangling.
llm = init_chat_model("openai:gpt-5.5")
pricing_chain = llm.with_structured_output(PricingDecision)

decision: PricingDecision = pricing_chain.invoke(
    "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
    "(SKU NV-ALDSWORTH-DM, MAP floor $399.00, landed cost $280.00). "
    "Reason through the MAP and margin rules, then produce a PricingDecision."
)
print(decision.price_cents)   # e.g. 41900
# --8<-- [end:pricing-call]

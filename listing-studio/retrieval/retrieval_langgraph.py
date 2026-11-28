"""Retrieval as a tool with LangGraph (the default the chapter shows).

Illustration, not run in CI: needs an API key and a network call. The
tested tool is search_docs in tool.py; only the wiring differs here.
"""
from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool

from .tool import search_docs


# --8<-- [start:retrieval-langgraph]
@tool("search_docs")
def search_docs_tool(query: str) -> str:
    """Search the merchant helpdesk policy docs."""
    return search_docs(query).model_dump_json()


agent = create_agent(
    "openai:gpt-6.2-sol",
    tools=[search_docs_tool],
    system_prompt="Answer only from search_docs results. If found is false, say you don't know.",
)
# --8<-- [end:retrieval-langgraph]

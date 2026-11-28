"""LangGraph version of the agent loop (the default tab). Illustration: needs an
API key and a network call, so it is compile-checked, not run in CI."""
from .loop import ABNORMAL, CEILING, CLEAN, FALSE_DONE, Result
from .tools import make_tools, price_is_valid


# --8<-- [start:loop-langgraph]
def run_agent(task: str, sku: str, limit: int = 12) -> Result:
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langgraph.errors import GraphRecursionError

    submitted: list = []
    tools = [tool(fn) for fn in make_tools(submitted).values()]
    agent = create_agent("openai:gpt-6.2-sol", tools=tools)
    try:
        # LangGraph owns the loop; recursion_limit is your ceiling. Set it.
        result = agent.invoke(
            {"messages": [{"role": "user", "content": task}]},
            config={"recursion_limit": limit},
        )
    except GraphRecursionError:
        return Result(CEILING, None, limit)
    last = result["messages"][-1]
    reason = last.response_metadata.get("finish_reason")
    if reason != "stop":  # "length", "content_filter": not an answer
        return Result(ABNORMAL, None, 0, detail=str(reason))
    # Stall detection is not built in: add it as middleware, or own the loop.
    return Result(CLEAN if price_is_valid(submitted, sku) else FALSE_DONE, last.content, 0)
# --8<-- [end:loop-langgraph]

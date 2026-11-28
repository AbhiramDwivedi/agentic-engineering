"""LangGraph version of the agent loop (the default tab). Illustration: needs an
API key and a network call, so it is compile-checked, not run in CI."""
from .loop import ABNORMAL, CEILING, CLEAN, FALSE_DONE, Result
from .tools import make_tools, price_is_valid


# --8<-- [start:loop-langgraph]
def classify_end(last, submitted: list, sku: str) -> Result:
    """Name the exit from the final message. Only a clean stop with a valid price is CLEAN."""
    meta = last.response_metadata
    reason = meta.get("normalized_finish_reason") or meta.get("finish_reason")
    if last.additional_kwargs.get("refusal") or reason == "refusal":
        return Result(ABNORMAL, None, 0, detail="refusal")  # a refusal can finish "stop"
    if reason != "stop":  # "length", "content_filter": not an answer
        return Result(ABNORMAL, None, 0, detail=str(reason))
    # Stall detection is not built in: add it as middleware, or own the loop.
    if price_is_valid(submitted, sku):
        return Result(CLEAN, last.content, 0)
    return Result(FALSE_DONE, None, 0, detail=last.content)


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
    return classify_end(result["messages"][-1], submitted, sku)
# --8<-- [end:loop-langgraph]

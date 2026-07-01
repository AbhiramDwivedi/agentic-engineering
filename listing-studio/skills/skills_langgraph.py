"""LangGraph via deepagents — the recommended framework path for skills.

Illustration, not run in CI: needs an API key and a network call.
deepagents implements progressive disclosure in the harness (SkillsMiddleware),
so the same SKILL.md folder works across any tool-calling model — attach a
skill by path, don't hand-wrap it as a tool.

The OpenAI Responses and Anthropic Messages variants are in skills_responses.py
and skills_example.py respectively.
"""
from __future__ import annotations

from deepagents import create_deep_agent

# --8<-- [start:skill-langgraph]
# Point deepagents at the skill folder. SkillsMiddleware (in the default stack
# when you pass `skills`) does progressive disclosure for you: it reads only
# name + description at startup, loads the SKILL.md body when the model triggers
# the skill, and runs a bundled script on demand — the same three levels, but
# owned by the harness, not hand-rolled, and portable across models.
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",   # or "openai:gpt-5.5" — same skill, any model
    skills=["skills/map_compliance"],
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
            "(SKU NV-ALDSWORTH-DM). Use the map-compliance skill to validate "
            "the price before confirming it."
        ),
    }]
})
print(result["messages"][-1].content)
# --8<-- [end:skill-langgraph]

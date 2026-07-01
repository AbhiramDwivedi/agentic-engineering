"""Skills with the Anthropic Messages API — native skills path.

Illustration, not run in CI: needs an API key and a network call.
The skill is attached to the code-execution container via container.skills —
the platform discloses it progressively and runs the bundled script in its
own sandbox. You attach the uploaded custom skill by id (or Anthropic's
pre-built pptx/xlsx/docx/pdf by name); beta today.

The default pane is skills_langgraph.py; this is the Anthropic Messages variant.
"""
from __future__ import annotations

import anthropic

MAP_COMPLIANCE_SKILL_ID = "skill_01MapComplianceExample"
client = anthropic.Anthropic()


# --8<-- [start:skill-anthropic]
# Native skills ride on the code-execution tool: attach the skill to the
# container and Claude discloses it progressively (name+description, then body,
# then it runs check_map.py inside Anthropic's sandbox). Up to 8 skills per
# request. Beta today, so the feature is gated behind beta headers.
reply = client.beta.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    container={"skills": [
        {"type": "custom", "skill_id": MAP_COMPLIANCE_SKILL_ID, "version": "latest"},
    ]},
    messages=[{
        "role": "user",
        "content": (
            "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
            "(SKU NV-ALDSWORTH-DM). Use the map-compliance skill to validate."
        ),
    }],
)
print(reply.content[-1].text if reply.content else "")
# --8<-- [end:skill-anthropic]

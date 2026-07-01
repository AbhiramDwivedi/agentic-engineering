"""Skills with the OpenAI Responses API — native skills path.

Illustration, not run in CI: needs an API key and a network call.
The skill is attached to the hosted shell tool via environment.skills —
the platform loads metadata, discloses the body on demand, and runs the
bundled script in its own sandbox. You reference the uploaded skill by id,
not as a function tool.

The default pane is skills_langgraph.py; this is the OpenAI Responses variant.
"""
from __future__ import annotations

from openai import OpenAI

MAP_COMPLIANCE_SKILL_ID = "skill_map_compliance"
client = OpenAI()


# --8<-- [start:skill-responses]
# Native skills: mount the skill on the hosted shell tool. The platform adds the
# skill's name + description + path to context (Level 1), loads the SKILL.md body
# when the model triggers it (Level 2), and runs the bundled check_map.py inside
# its own container (Level 3). No function-tool wrapper, no local subprocess.
response = client.responses.create(
    model="gpt-5.5",
    tools=[{
        "type": "shell",
        "environment": {
            "type": "container_auto",
            "skills": [
                {"type": "skill_reference", "skill_id": MAP_COMPLIANCE_SKILL_ID},
            ],
        },
    }],
    input=(
        "Set a listed price for the Aldsworth Dual-Motor Sit-Stand Desk "
        "(SKU NV-ALDSWORTH-DM). Use the map-compliance skill to validate."
    ),
)
print(response.output_text)
# --8<-- [end:skill-responses]

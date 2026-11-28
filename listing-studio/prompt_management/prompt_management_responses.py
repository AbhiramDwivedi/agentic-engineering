"""Prompt management with the OpenAI Responses API. Illustration, not run in CI."""
from __future__ import annotations

from dataclasses import replace

from openai import OpenAI

from .release import LIVE_V1

client = OpenAI()

# --8<-- [start:prompt-responses]
cfg = replace(LIVE_V1, model="gpt-6.2-sol")   # the OpenAI-pinned config
system, user = cfg.prompt.render(copy="The Aldsworth desk, $419.00, SKU NV-ALDSWORTH-DM")
response = client.responses.create(
    model=cfg.model,
    temperature=cfg.temperature,
    instructions=system,
    input=user,
)
# Log cfg.prompt.version beside cfg.model with every call.
# --8<-- [end:prompt-responses]

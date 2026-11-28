"""Prompt management with the Anthropic Messages API. Illustration, not run in CI."""
from __future__ import annotations

import anthropic

from .release import LIVE_V1

client = anthropic.Anthropic()

# --8<-- [start:prompt-anthropic]
cfg = LIVE_V1
system, user = cfg.prompt.render(copy="The Aldsworth desk, $419.00, SKU NV-ALDSWORTH-DM")
message = client.messages.create(
    model=cfg.model,
    max_tokens=1024,
    temperature=cfg.temperature,
    system=system,
    messages=[{"role": "user", "content": user}],
)
# Log cfg.prompt.version beside cfg.model with every call.
# --8<-- [end:prompt-anthropic]

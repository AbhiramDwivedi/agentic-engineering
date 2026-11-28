"""Per-step model against the Anthropic Messages API.

Illustration, not run in CI: needs an API key and a network call.
"""
import anthropic

from .config import model_for

client = anthropic.Anthropic()

# --8<-- [start:model-anthropic]
provider, model = model_for("write_copy").split(":", 1)  # "anthropic", "claude-sonnet-5-5"
message = client.messages.create(
    model=model,
    max_tokens=512,
    messages=[{"role": "user", "content": "Write copy: Aldsworth dual-motor sit-stand desk"}],
)
# --8<-- [end:model-anthropic]

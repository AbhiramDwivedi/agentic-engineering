"""Per-step model against the OpenAI Responses API.

Illustration, not run in CI: needs an API key and a network call.
"""
from openai import OpenAI

from .config import model_for

client = OpenAI()

# --8<-- [start:model-responses]
provider, model = model_for("categorize").split(":", 1)  # "openai", "gpt-6.2-sol"
response = client.responses.create(
    model=model,
    input="Categorize: Aldsworth dual-motor sit-stand desk",
)
# --8<-- [end:model-responses]

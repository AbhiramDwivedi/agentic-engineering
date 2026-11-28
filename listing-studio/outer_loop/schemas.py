from pydantic import BaseModel, ConfigDict


class PriceCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price_cents: int

from pydantic import BaseModel


class PriceCandidate(BaseModel):
    price_cents: int

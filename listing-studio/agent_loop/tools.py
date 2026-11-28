"""The price step's tools (chapter 2.5). check_price is 2.1's, reused."""
from pricing.tools import check_price


def market_feed(supplier_sku: str) -> list[int]:
    # Hardcoded for the illustration; in production this hits the market-data feed.
    return [41900, 44500, 39900]


# --8<-- [start:loop-tools]
def make_tools(submitted: list) -> dict:
    def get_competitor_prices(supplier_sku: str) -> dict:
        """Competitor prices for a product, in cents."""
        # Raises TimeoutError when the feed is slow; the loop turns that into
        # an is_error result the model can read and retry.
        return {"prices_cents": market_feed(supplier_sku)}

    def submit_for_review(supplier_sku: str, price_cents: int) -> dict:
        """Queue a price for human review. It does not check the price."""
        submitted.append(price_cents)
        return {"queued": True, "price_cents": price_cents}

    return {
        "get_competitor_prices": get_competitor_prices,
        "check_price": check_price,
        "submit_for_review": submit_for_review,
    }


def price_is_valid(submitted: list, sku: str) -> bool:
    """The code check behind "done": something was submitted, and it clears the floor."""
    return bool(submitted) and check_price(sku, submitted[-1])["ok"]
# --8<-- [end:loop-tools]

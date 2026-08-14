"""Static dispatch: the front door for Listing Studio's supplier-feed events."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    ok: bool
    detail: str
    error: str | None = None  # structured, machine-readable reason on failure


def _handle_new_product(event: dict) -> DispatchResult:
    """A new supplier_sku enters the pipeline at step 1 (ingest)."""
    return DispatchResult(ok=True, detail=f"queued {event['supplier_sku']} for ingest")


def _handle_price_update(event: dict) -> DispatchResult:
    """An upstream price change; re-runs step 6 (price) only."""
    return DispatchResult(ok=True, detail=f"re-priced {event['supplier_sku']}")


def _handle_stock_update(event: dict) -> DispatchResult:
    """A stock-level change; no listing content changes, just availability."""
    return DispatchResult(ok=True, detail=f"stock updated for {event['supplier_sku']}")


# --8<-- [start:routing-dispatch]
EVENT_HANDLERS: dict[str, Callable[[dict], DispatchResult]] = {
    "new_product": _handle_new_product,
    "price_update": _handle_price_update,
    "stock_update": _handle_stock_update,
}


def dispatch(event: dict) -> DispatchResult:
    """Look up the handler for event["event_type"] and run it."""
    # event_type is untrusted (off the supplier feed): validate against the
    # known key set before the lookup, never a dynamic getattr/eval on it.
    event_type = event.get("event_type")

    if event_type not in EVENT_HANDLERS:
        logger.warning("dispatch: rejected unknown event_type %r", event_type)
        return DispatchResult(
            ok=False,
            detail="event rejected",
            error=f"unknown event_type {event_type!r}; known types: {sorted(EVENT_HANDLERS)}",
        )

    return EVENT_HANDLERS[event_type](event)
# --8<-- [end:routing-dispatch]

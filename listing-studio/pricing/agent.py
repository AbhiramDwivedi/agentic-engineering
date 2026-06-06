from .model_client import ModelClient, ToolCall
from .models import PriceVerdict
from .tools import check_price


# --8<-- [start:loop]
def price_listing(model: ModelClient, prompt: str, max_steps: int = 4) -> dict:
    """The model decides each step: call the typed tool, or just answer.

    Returns {"price_cents", "checked", "verdict"}. `checked` is False when the
    model skipped the tool, which is the demonstrable failure mode.
    """
    last_verdict = None
    for _ in range(max_steps):
        decision = model.propose(prompt, last_verdict)
        if isinstance(decision, ToolCall):
            verdict: PriceVerdict = check_price(decision.request)
            last_verdict = verdict.model_dump()
            if verdict.ok:
                return {
                    "price_cents": verdict.proposed_price_cents,
                    "checked": True,
                    "verdict": verdict,
                }
            # not ok: loop, so the model sees the floor and adjusts
            continue
        # decision is an int: the model answered without checking
        return {"price_cents": decision, "checked": False, "verdict": None}
    raise RuntimeError("model did not converge on an in-policy price")
# --8<-- [end:loop]

"""The fixed roster, run in parallel: three commerce personas reason over
one listing at once, and the fan-in never lets one bad call take the
others down.

Mirrors fan_out's gather(): each persona call runs in its own task, and a
raised exception becomes a MissingSpecialist instead of an exception that
propagates past run_panel(). Unlike fan_out's dynamic half, ROSTER is a
plain Python list -- your code decides the roster and the count, and the
model only ever supplies one persona's verdict, never a say in who else
sits on the panel.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import anyio

from .schemas import MissingSpecialist, PersonaVerdict


# --8<-- [start:panel-roster]
ROSTER: list[str] = ["seo", "pricing", "compliance"]


def _approx_tokens(text: str) -> int:
    """A rough proxy (~4 chars/token, the common estimate), not a
    provider's real usage report -- swap in the provider's own usage field
    once a variant is wired to a live API."""
    return max(1, len(text) // 4)


@dataclass
class CallStats:
    """What the panel actually cost, per persona -- visible on the
    returned object, never hidden in a log line only ops can see."""
    calls: dict[str, int] = field(default_factory=dict)
    tokens: dict[str, int] = field(default_factory=dict)

    @property
    def total_calls(self) -> int:
        return sum(self.calls.values())

    @property
    def total_tokens(self) -> int:
        return sum(self.tokens.values())


@dataclass
class PanelRun:
    verdicts: dict[str, PersonaVerdict]
    missing: list[MissingSpecialist]
    cost: CallStats


def _call_persona_safe(
    persona_fn: Any, persona: str, listing: dict, cost: CallStats
) -> PersonaVerdict | None:
    """Run one persona and turn any exception into `None`. The attempt is
    charged to `cost` either way -- a call that fails still cost
    something -- and run_panel() reports the absence as a
    MissingSpecialist, never as a raised exception that takes the other
    two personas down."""
    prompt = f"{persona} review of {listing.get('supplier_sku', 'this listing')}"
    cost.calls[persona] = cost.calls.get(persona, 0) + 1
    cost.tokens[persona] = cost.tokens.get(persona, 0) + _approx_tokens(prompt)
    try:
        verdict = persona_fn(persona, listing)
    except Exception:
        return None
    output = " ".join(f"{c.field} {c.value} {c.rationale}" for c in verdict.claims)
    cost.tokens[persona] += _approx_tokens(output)
    return verdict


async def _run_all(
    persona_fn: Any, listing: dict, cost: CallStats
) -> dict[str, PersonaVerdict | None]:
    results: dict[str, PersonaVerdict | None] = {}

    async def _one(persona: str) -> None:
        results[persona] = await anyio.to_thread.run_sync(
            _call_persona_safe, persona_fn, persona, listing, cost
        )

    async with anyio.create_task_group() as tg:
        for persona in ROSTER:
            tg.start_soon(_one, persona)
    return results


def run_panel(persona_fn: Any, listing: dict) -> PanelRun:
    """Run every persona in ROSTER concurrently over the same listing.

    persona_fn(persona, listing) -> PersonaVerdict is the seam the
    provider variants inject. A persona that raises or returns nothing
    usable is recorded in `missing`, never silently dropped from the
    panel -- reconcile() decides what a missing specialist means for the
    decision.
    """
    cost = CallStats()
    raw = anyio.run(_run_all, persona_fn, listing, cost)

    verdicts: dict[str, PersonaVerdict] = {}
    missing: list[MissingSpecialist] = []
    for persona, verdict in raw.items():
        if verdict is None:
            missing.append(MissingSpecialist(persona=persona, reason="call failed or timed out"))
        else:
            verdicts[persona] = verdict
    return PanelRun(verdicts=verdicts, missing=missing, cost=cost)
# --8<-- [end:panel-roster]

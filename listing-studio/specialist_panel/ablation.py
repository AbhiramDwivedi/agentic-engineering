"""The ablation harness: run the same input through the full panel and one
well-scoped single call, and report what the extra calls actually bought.

This is the panel's burden of proof, not a demo of three calls looking
more thorough than one. run_ablation() never asserts an answer -- it
returns the comparison and leaves the verdict to the caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .reconcile import reconcile
from .roster import run_panel
from .schemas import PersonaVerdict


# --8<-- [start:panel-ablation]
@dataclass
class AblationResult:
    """What the panel found and what it cost, next to the single-call
    baseline. `omissions_caught_by_panel` compares which fields got a
    claim at all, not whether two free-text values agree -- field coverage
    is the honest floor a mechanical comparison can answer."""
    panel_fields: set[str]
    single_fields: set[str]
    omissions_caught_by_panel: set[str]
    panel_calls: int
    single_calls: int


def run_ablation(
    persona_fn: Any,      # callable(persona, listing) -> PersonaVerdict
    single_call_fn: Any,  # callable(listing) -> PersonaVerdict, one call, every concern
    listing: dict,
) -> AblationResult:
    """Baseline: single_call_fn is one well-scoped prompt asked to cover
    every specialist's concern in a single pass, scored the same way the
    panel is -- by which fields it named. A panel that never runs this
    comparison cannot tell a real gain from a longer answer that says the
    same thing three ways.
    """
    panel = run_panel(persona_fn, listing)
    decision = reconcile(panel.verdicts, panel.missing)
    panel_fields = {c.field for c in decision.accepted} | {c.field for c in decision.rejected}

    single: PersonaVerdict = single_call_fn(listing)
    single_fields = {c.field for c in single.claims}

    return AblationResult(
        panel_fields=panel_fields,
        single_fields=single_fields,
        omissions_caught_by_panel=panel_fields - single_fields,
        panel_calls=panel.cost.total_calls,
        single_calls=1,
    )
# --8<-- [end:panel-ablation]

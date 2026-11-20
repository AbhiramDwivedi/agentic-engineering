"""The reconcile step: typed verdicts in, one typed decision out -- never
a blended paragraph.

reconcile() is pure code, no model call: letting a model merge the
panel's disagreement away is exactly the failure a specialist panel exists
to avoid, so the merge itself is a rule your code owns and can be read
back, not a judgment made and lost inside a prompt.
"""
from __future__ import annotations

from .schemas import (
    AcceptedClaim,
    Conflict,
    MissingSpecialist,
    PanelDecision,
    PersonaVerdict,
    RejectedClaim,
)


# --8<-- [start:panel-reconcile]
# Your code decided this order once, when it was written. On a field two
# personas both claimed, the earlier persona's value wins: compliance over
# pricing over discoverability, because a dropped disclosure costs more
# than a duller headline. PRECEDENCE must name every persona in ROSTER.
PRECEDENCE = ["compliance", "pricing", "seo"]

# A conflict escalates to a person when the persona whose claim would have
# settled it never answered -- the panel does not rule in a missing
# specialist's absence.
ESCALATE_ON_MISSING = {"compliance"}


def reconcile(
    verdicts: dict[str, PersonaVerdict], missing: list[MissingSpecialist]
) -> PanelDecision:
    """Merge typed verdicts into one typed decision, conflict intact.

    Two or more personas claiming the same field with different values is
    resolved by PRECEDENCE, never averaged: the losing claim lands in
    `rejected` with the rule that beat it, and the conflict itself lands in
    `conflicts` so a caller can see that it happened, not just its
    outcome.
    """
    by_field: dict[str, list[tuple[str, str]]] = {}
    for persona, verdict in verdicts.items():
        for claim in verdict.claims:
            by_field.setdefault(claim.field, []).append((persona, claim.value))

    accepted: list[AcceptedClaim] = []
    rejected: list[RejectedClaim] = []
    conflicts: list[Conflict] = []

    for field_name, claims in by_field.items():
        if len({value for _, value in claims}) == 1:
            # Every persona that touched this field agrees; nothing to
            # arbitrate.
            persona, value = claims[0]
            accepted.append(AcceptedClaim(field=field_name, value=value, source_persona=persona))
            continue

        ranked = sorted(claims, key=lambda c: PRECEDENCE.index(c[0]))
        winner_persona, winner_value = ranked[0]
        accepted.append(
            AcceptedClaim(field=field_name, value=winner_value, source_persona=winner_persona)
        )
        for persona, value in ranked[1:]:
            rejected.append(
                RejectedClaim(
                    field=field_name,
                    value=value,
                    source_persona=persona,
                    reason=f"overruled by {winner_persona} (precedence: {PRECEDENCE})",
                )
            )
        conflicts.append(
            Conflict(
                field=field_name,
                dissenting_personas=[p for p, _ in ranked[1:]],
                winner=winner_persona,
                rule="field-level precedence",
            )
        )

    missing_personas = {m.persona for m in missing}
    escalate = bool(missing_personas & ESCALATE_ON_MISSING)

    return PanelDecision(
        accepted=accepted, rejected=rejected, conflicts=conflicts,
        missing=missing, escalate=escalate,
    )
# --8<-- [end:panel-reconcile]

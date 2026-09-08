"""Tests for the specialist-panel chapter (3.5) companion code.

All tests are offline: no API key, no network call.

- PersonaClaim / PersonaVerdict / PanelDecision and friends are imported
  directly (no third-party deps beyond pydantic, which is pure Python).
- run_panel (roster.py) is tested for the fixed-roster claim: the roster
  is exactly three entries regardless of the listing, every persona runs,
  and a persona call that raises comes back as a MissingSpecialist instead
  of taking the other two down. Cost is asserted on the returned object.
- reconcile (reconcile.py) is tested for the load-bearing claim: a real
  conflict between two personas' claims resolves by a stated rule, with
  the losing claim visible in `rejected` and the conflict itself visible
  in `conflicts` -- never averaged away. Agreement, missing-specialist
  escalation, and the no-conflict path are covered too.
- run_ablation (ablation.py) is tested against a single-call stand-in that
  misses what the panel catches, and against one that matches it.
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API
  keys and the heavy provider SDKs, which are not test dependencies).
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from specialist_panel.ablation import AblationResult, run_ablation
from specialist_panel.reconcile import PRECEDENCE, reconcile
from specialist_panel.roster import ROSTER, CallStats, PanelRun, run_panel
from specialist_panel.schemas import (
    MissingSpecialist,
    PanelDecision,
    PersonaClaim,
    PersonaVerdict,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "specialist_panel")

LANGGRAPH_FILE = os.path.join(PKG, "specialist_panel_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "specialist_panel_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "specialist_panel_example.py")

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
}


def _verdict(persona: str, claims: list[tuple[str, str, str]]) -> PersonaVerdict:
    return PersonaVerdict(
        persona=persona,
        claims=[PersonaClaim(field=f, value=v, rationale=r) for f, v, r in claims],
    )


# A real conflict: SEO wants the punchy line, compliance requires the
# disclosure, on the same field. Pricing weighs in on a different field
# entirely, so it never collides with either.
SEO_VERDICT = _verdict("seo", [
    ("content_blocks.faq", "Rated to 250 lbs -- built for all-day use.", "keyword-dense, no legal copy"),
])
COMPLIANCE_VERDICT = _verdict("compliance", [
    (
        "content_blocks.faq",
        "Rated to 250 lbs. WARNING: California Prop 65 -- this product can expose you to chemicals known to the State of California to cause cancer.",
        "Prop 65 disclosure is required on every listing with this claim",
    ),
])
PRICING_VERDICT = _verdict("pricing", [
    ("content_blocks.comparison", "Priced at $419, MAP-safe against comparable premium desks.", "stays above the MAP floor"),
])


# ---------------------------------------------------------------------------
# Schemas (anchor: panel-schemas)
# ---------------------------------------------------------------------------

def test_persona_claim_rejects_extra_fields():
    with pytest.raises(ValidationError):
        PersonaClaim(field="x", value="y", rationale="z", stray="nope")  # type: ignore[call-arg]


def test_persona_verdict_accepts_zero_claims():
    v = PersonaVerdict(persona="seo", claims=[])
    assert v.claims == []


def test_panel_decision_rejects_extra_fields():
    with pytest.raises(ValidationError):
        PanelDecision(
            accepted=[], rejected=[], conflicts=[], missing=[], escalate=False,
            stray=True,  # type: ignore[call-arg]
        )


# ---------------------------------------------------------------------------
# run_panel (anchor: panel-roster)
# The fixed roster: your code decides the count, always three, run at once.
# ---------------------------------------------------------------------------

def test_roster_is_a_fixed_three_item_literal():
    assert ROSTER == ["seo", "pricing", "compliance"]


def test_run_panel_runs_every_roster_persona():
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        return _verdict(persona, [(f"{persona}_field", "value", "why")])

    run = run_panel(persona_fn, ALDSWORTH_LISTING)
    assert isinstance(run, PanelRun)
    assert set(run.verdicts) == {"seo", "pricing", "compliance"}
    assert run.missing == []


def test_run_panel_records_a_missing_specialist_without_raising():
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        if persona == "compliance":
            raise RuntimeError("timeout")
        return _verdict(persona, [(f"{persona}_field", "value", "why")])

    run = run_panel(persona_fn, ALDSWORTH_LISTING)
    assert set(run.verdicts) == {"seo", "pricing"}
    assert len(run.missing) == 1
    assert run.missing[0] == MissingSpecialist(persona="compliance", reason="call failed or timed out")
    # A failed attempt is still a call, and still costs something.
    assert run.cost.calls["compliance"] == 1


def test_run_panel_reports_per_persona_call_count_and_tokens():
    """Cost is visible on the returned object, not hidden -- three
    personas, three calls, and each has a nonzero token estimate."""
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        return _verdict(persona, [(f"{persona}_field", "some value", "some reason")])

    run = run_panel(persona_fn, ALDSWORTH_LISTING)
    assert isinstance(run.cost, CallStats)
    assert run.cost.total_calls == 3
    assert set(run.cost.calls) == {"seo", "pricing", "compliance"}
    assert all(n == 1 for n in run.cost.calls.values())
    assert all(t > 0 for t in run.cost.tokens.values())
    assert run.cost.total_tokens == sum(run.cost.tokens.values())


# ---------------------------------------------------------------------------
# reconcile (anchor: panel-reconcile)
# The load-bearing claim: a real conflict resolves by a stated rule, and
# the dissent stays visible -- never averaged away.
# ---------------------------------------------------------------------------

def test_reconcile_surfaces_a_real_conflict_rather_than_averaging():
    verdicts = {"seo": SEO_VERDICT, "compliance": COMPLIANCE_VERDICT}
    decision = reconcile(verdicts, missing=[])

    assert isinstance(decision, PanelDecision)
    # The compliance value wins outright -- not a blend of the two texts.
    assert len(decision.accepted) == 1
    assert decision.accepted[0].field == "content_blocks.faq"
    assert decision.accepted[0].source_persona == "compliance"
    assert "Prop 65" in decision.accepted[0].value

    # The SEO claim is not silently dropped: it is visible, with a reason.
    assert len(decision.rejected) == 1
    assert decision.rejected[0].source_persona == "seo"
    assert decision.rejected[0].value == SEO_VERDICT.claims[0].value
    assert "compliance" in decision.rejected[0].reason

    # The conflict itself is named: which field, who dissented, who won.
    assert len(decision.conflicts) == 1
    conflict = decision.conflicts[0]
    assert conflict.field == "content_blocks.faq"
    assert conflict.dissenting_personas == ["seo"]
    assert conflict.winner == "compliance"


def test_reconcile_precedence_order_is_compliance_then_pricing_then_seo():
    assert PRECEDENCE == ["compliance", "pricing", "seo"]


def test_reconcile_accepts_agreement_without_a_conflict():
    seo = _verdict("seo", [("title", "Aldsworth Dual-Motor Sit-Stand Desk", "matches spec sheet")])
    pricing = _verdict("pricing", [("title", "Aldsworth Dual-Motor Sit-Stand Desk", "matches catalog")])
    decision = reconcile({"seo": seo, "pricing": pricing}, missing=[])

    assert len(decision.accepted) == 1
    assert decision.conflicts == []
    assert decision.rejected == []


def test_reconcile_merges_non_overlapping_fields_from_every_persona():
    verdicts = {"seo": SEO_VERDICT, "compliance": COMPLIANCE_VERDICT, "pricing": PRICING_VERDICT}
    decision = reconcile(verdicts, missing=[])
    fields = {c.field for c in decision.accepted}
    assert "content_blocks.comparison" in fields
    assert len(decision.conflicts) == 1  # only the shared faq field conflicted


def test_reconcile_escalates_when_compliance_is_missing():
    missing = [MissingSpecialist(persona="compliance", reason="call failed or timed out")]
    decision = reconcile({"seo": SEO_VERDICT, "pricing": PRICING_VERDICT}, missing=missing)
    assert decision.escalate is True
    assert decision.missing == missing


def test_reconcile_does_not_escalate_on_a_clean_panel():
    decision = reconcile({"seo": SEO_VERDICT, "pricing": PRICING_VERDICT}, missing=[])
    assert decision.escalate is False


# ---------------------------------------------------------------------------
# run_ablation (anchor: panel-ablation)
# The panel proves it earned its extra calls -- or doesn't.
# ---------------------------------------------------------------------------

def test_ablation_shows_what_the_single_call_missed():
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        return {
            "seo": SEO_VERDICT, "compliance": COMPLIANCE_VERDICT, "pricing": PRICING_VERDICT,
        }[persona]

    def single_call_fn(listing: dict) -> PersonaVerdict:
        # A single well-scoped call that covers the headline but -- the
        # realistic failure mode -- never gets to the pricing comparison.
        return _verdict("single", [
            ("content_blocks.faq", "Rated to 250 lbs -- built for all-day use.", "one pass, general copy"),
        ])

    result = run_ablation(persona_fn, single_call_fn, ALDSWORTH_LISTING)

    assert isinstance(result, AblationResult)
    assert result.omissions_caught_by_panel == {"content_blocks.comparison"}
    assert result.panel_calls == 3
    assert result.single_calls == 1


def test_ablation_reports_no_omissions_when_the_single_call_matches():
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        return _verdict(persona, [("title", "same value", "why")])

    def single_call_fn(listing: dict) -> PersonaVerdict:
        return _verdict("single", [("title", "same value", "why")])

    result = run_ablation(persona_fn, single_call_fn, ALDSWORTH_LISTING)
    assert result.omissions_caught_by_panel == set()


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

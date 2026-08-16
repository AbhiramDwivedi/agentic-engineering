"""Tests for the orchestrator-workers chapter (3.3) companion code.

All tests are offline: no API key, no network call.

- DeliverablePlan / FanOutPlan / WorkerResult are imported directly (no
  third-party deps beyond pydantic, which is pure Python).
- run_fixed_fanout (fixed.py) is tested to show the deflated half's whole
  claim: the same three deliverables come back regardless of what the
  listing says, because the list is a literal, not a read of the listing.
- propose_deliverables (plan.py) is tested with a rule-based stand-in
  planner_fn so the "different listings name a different number of
  deliverables" claim, and the truncation cap, both run offline and
  deterministically.
- gather (gather.py) is tested for the three fan-in obligations: stable-key
  merge regardless of finish order, the partial-failure contract, and the
  untrusted-input boundary at render_for_synthesis.
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API keys
  and the heavy provider SDKs, which are not test dependencies).
"""
import os
import py_compile
import time

import pytest
from pydantic import ValidationError

from fan_out.fixed import STANDARD_DELIVERABLES, run_fixed_fanout
from fan_out.gather import FanOutSummary, gather, render_for_synthesis
from fan_out.plan import MAX_EXTRA_DELIVERABLES, PlanResult, propose_deliverables
from fan_out.schemas import DeliverablePlan, FanOutPlan, WorkerResult

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "fan_out")

LANGGRAPH_FILE = os.path.join(PKG, "fan_out_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "fan_out_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "fan_out_example.py")

ALDSWORTH_LISTING = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "title": "Aldsworth Dual-Motor Sit-Stand Desk",
    "compliance": {"map_enforced": True, "prop65": True, "safety_claims": ["BIFMA stability"]},
    "attributes": {"bulky_shipping": True, "assembly_required": True},
}

PHONE_CASE_LISTING = {
    "supplier_sku": "NV-PHONECASE-01",
    "title": "Slim Phone Case",
    "compliance": {"map_enforced": False, "prop65": False, "safety_claims": []},
    "attributes": {"bulky_shipping": False, "assembly_required": False},
}


def _rule_based_planner(listing: dict) -> FanOutPlan:
    """A deterministic stand-in for a model call: reads exactly the fields a
    real planner prompt would read and names deliverables from them. Used
    only in tests -- the illustration files show the real model call."""
    compliance = listing.get("compliance", {})
    attributes = listing.get("attributes", {})
    deliverables = []
    if compliance.get("prop65") or compliance.get("safety_claims"):
        deliverables.append(
            DeliverablePlan(
                deliverable_id="compliance_insert",
                reason="Prop 65 and BIFMA claims need a dedicated compliance insert",
            )
        )
    if compliance.get("map_enforced"):
        deliverables.append(
            DeliverablePlan(
                deliverable_id="price_safe_ad_variant",
                reason="MAP-enforced pricing needs an ad that never shows a lower price",
            )
        )
    if attributes.get("bulky_shipping"):
        deliverables.append(
            DeliverablePlan(
                deliverable_id="assembly_delivery_blurb",
                reason="bulky freight and required assembly need their own delivery blurb",
            )
        )
    return FanOutPlan(deliverables=deliverables)


def _echo_worker(deliverable_id: str, listing: dict) -> str:
    return f"content for {deliverable_id}"


# ---------------------------------------------------------------------------
# Schemas (anchor: fanout-schemas)
# ---------------------------------------------------------------------------

def test_deliverable_plan_accepts_valid_object():
    d = DeliverablePlan(deliverable_id="compliance_insert", reason="Prop 65 claim")
    assert d.deliverable_id == "compliance_insert"


def test_deliverable_plan_rejects_extra_fields():
    with pytest.raises(ValidationError):
        DeliverablePlan(deliverable_id="x", reason="y", stray="nope")  # type: ignore[call-arg]


def test_fan_out_plan_accepts_empty_deliverables():
    """A plan naming zero extra deliverables is valid -- the phone-case case."""
    plan = FanOutPlan(deliverables=[])
    assert plan.deliverables == []


def test_worker_result_rejects_extra_fields():
    with pytest.raises(ValidationError):
        WorkerResult(deliverable_id="x", ok=True, content="y", stray="nope")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Fixed fan-out (anchor: fanout-fixed)
# The deflated half: always these three, regardless of the listing.
# ---------------------------------------------------------------------------

def test_standard_deliverables_is_a_three_item_literal():
    assert STANDARD_DELIVERABLES == ["listing", "announcement_email", "ad_copy"]


def test_fixed_fanout_ignores_the_listing_entirely():
    """The whole claim of the deflated half: the worker set does not change
    with the listing, because the listing is never consulted to build it."""
    aldsworth = run_fixed_fanout(_echo_worker, ALDSWORTH_LISTING)
    phone_case = run_fixed_fanout(_echo_worker, PHONE_CASE_LISTING)
    assert set(aldsworth.results) == {"listing", "announcement_email", "ad_copy"}
    assert set(phone_case.results) == {"listing", "announcement_email", "ad_copy"}


def test_fixed_fanout_returns_a_fan_out_summary():
    result = run_fixed_fanout(_echo_worker, ALDSWORTH_LISTING)
    assert isinstance(result, FanOutSummary)
    assert result.ok_count == 3
    assert result.failed_count == 0


def test_fixed_fanout_also_gets_partial_failure_protection():
    """fixed.py reuses gather() -- one bad standard worker still leaves the
    other two intact, the same contract the dynamic half gets."""
    def worker(deliverable_id: str, listing: dict) -> str:
        if deliverable_id == "ad_copy":
            raise RuntimeError("rate limited")
        return f"content for {deliverable_id}"

    result = run_fixed_fanout(worker, ALDSWORTH_LISTING)
    assert result.ok_count == 2
    assert result.failed_count == 1
    assert result.results["listing"].ok is True
    assert result.results["announcement_email"].ok is True
    assert result.results["ad_copy"].ok is False
    assert "ad_copy" in result.summary


# ---------------------------------------------------------------------------
# The planner + cap (anchor: fanout-plan)
# The dynamic half: the worker count is not in the code.
# ---------------------------------------------------------------------------

def test_plan_varies_by_listing_content():
    """The same planner function, two different listings, two different
    deliverable counts -- the count is decided per input, not fixed."""
    aldsworth = propose_deliverables(_rule_based_planner, ALDSWORTH_LISTING)
    phone_case = propose_deliverables(_rule_based_planner, PHONE_CASE_LISTING)

    assert {d.deliverable_id for d in aldsworth.deliverables} == {
        "compliance_insert", "price_safe_ad_variant", "assembly_delivery_blurb",
    }
    assert phone_case.deliverables == []


def test_plan_result_type_and_no_truncation_under_the_cap():
    result = propose_deliverables(_rule_based_planner, ALDSWORTH_LISTING)
    assert isinstance(result, PlanResult)
    assert result.truncated is False
    assert len(result.deliverables) == 3


def test_plan_cap_truncates_when_the_model_overreaches():
    """A planner that names more than the cap does not get to run them all --
    the excess is dropped, and the caller is told, not left to find out from
    a cost report."""
    def greedy_planner(listing: dict) -> FanOutPlan:
        return FanOutPlan(
            deliverables=[
                DeliverablePlan(deliverable_id=f"extra_{i}", reason="because")
                for i in range(MAX_EXTRA_DELIVERABLES + 3)
            ]
        )

    result = propose_deliverables(greedy_planner, ALDSWORTH_LISTING)
    assert result.truncated is True
    assert len(result.deliverables) == MAX_EXTRA_DELIVERABLES
    # The kept items are the first N in the order the model returned them.
    assert [d.deliverable_id for d in result.deliverables] == [
        f"extra_{i}" for i in range(MAX_EXTRA_DELIVERABLES)
    ]


def test_plan_at_exactly_the_cap_is_not_truncated():
    def planner(listing: dict) -> FanOutPlan:
        return FanOutPlan(
            deliverables=[
                DeliverablePlan(deliverable_id=f"extra_{i}", reason="because")
                for i in range(MAX_EXTRA_DELIVERABLES)
            ]
        )

    result = propose_deliverables(planner, ALDSWORTH_LISTING)
    assert result.truncated is False
    assert len(result.deliverables) == MAX_EXTRA_DELIVERABLES


# ---------------------------------------------------------------------------
# gather (anchor: fanout-gather)
# The fan-in: stable-key merge, the partial-failure contract, untrusted
# worker output.
# ---------------------------------------------------------------------------

def test_gather_merges_under_stable_key_regardless_of_finish_order():
    """Workers are requested in one order and finish in the opposite order;
    the merge must still be correct when read back by key."""
    delays = {"a": 0.06, "b": 0.03, "c": 0.0}  # "c" finishes first, "a" last

    def slow_worker(deliverable_id: str, listing: dict) -> str:
        time.sleep(delays[deliverable_id])
        return f"content for {deliverable_id}"

    summary = gather(slow_worker, ["a", "b", "c"], {})
    assert set(summary.results) == {"a", "b", "c"}
    assert summary.results["a"].content == "content for a"
    assert summary.results["b"].content == "content for b"
    assert summary.results["c"].content == "content for c"
    assert summary.ok_count == 3
    assert summary.failed_count == 0


def test_gather_partial_failure_returns_a_structured_summary_not_an_exception():
    def worker(deliverable_id: str, listing: dict) -> str:
        if deliverable_id == "compliance_insert":
            raise RuntimeError("model timeout")
        return f"content for {deliverable_id}"

    summary = gather(
        worker,
        ["listing", "compliance_insert", "price_safe_ad_variant", "assembly_delivery_blurb"],
        ALDSWORTH_LISTING,
    )
    assert summary.ok_count == 3
    assert summary.failed_count == 1
    assert summary.results["compliance_insert"].ok is False
    assert summary.results["compliance_insert"].error == "model timeout"
    # The other three are untouched by the one failure.
    assert summary.results["listing"].ok is True
    assert summary.results["price_safe_ad_variant"].ok is True
    assert summary.results["assembly_delivery_blurb"].ok is True
    assert "3 of 4 completed" in summary.summary
    assert "compliance_insert" in summary.summary
    assert "model timeout" in summary.summary


def test_gather_never_raises_even_when_every_worker_fails():
    def worker(deliverable_id: str, listing: dict) -> str:
        raise RuntimeError(f"boom {deliverable_id}")

    summary = gather(worker, ["a", "b"], {})
    assert summary.ok_count == 0
    assert summary.failed_count == 2
    assert "0 of 2 completed" in summary.summary


def test_gather_with_no_deliverables_returns_an_empty_summary():
    """The phone-case case: zero extra deliverables, gather is a no-op, not
    an error."""
    summary = gather(_echo_worker, [], PHONE_CASE_LISTING)
    assert summary.results == {}
    assert summary.ok_count == 0
    assert summary.failed_count == 0


def test_render_for_synthesis_wraps_only_successful_workers_as_untrusted():
    def worker(deliverable_id: str, listing: dict) -> str:
        if deliverable_id == "compliance_insert":
            raise RuntimeError("model timeout")
        return f"content for {deliverable_id}"

    summary = gather(worker, ["ad_copy", "compliance_insert"], ALDSWORTH_LISTING)
    rendered = render_for_synthesis(summary)

    assert 'id="ad_copy"' in rendered
    assert "content for ad_copy" in rendered
    assert 'trust="untrusted"' in rendered
    # The failed worker contributes nothing to the synthesis text -- its
    # error is reported only through gather()'s own summary field.
    assert "compliance_insert" not in rendered
    assert "model timeout" not in rendered


def test_gather_end_to_end_matches_the_dynamic_plan():
    """propose_deliverables feeding straight into gather: the whole dynamic
    half, offline, on the Aldsworth desk."""
    plan = propose_deliverables(_rule_based_planner, ALDSWORTH_LISTING)
    summary = gather(_echo_worker, [d.deliverable_id for d in plan.deliverables], ALDSWORTH_LISTING)
    assert summary.ok_count == 3
    assert set(summary.results) == {
        "compliance_insert", "price_safe_ad_variant", "assembly_delivery_blurb",
    }


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

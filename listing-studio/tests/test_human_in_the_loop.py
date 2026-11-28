"""Chapter 4.3 tests: offline, stdlib + declared deps only. The LangGraph and
Responses files are illustrations and are only compile-checked."""
import os
import py_compile

import pytest

from human_in_the_loop.gate import gate_policy
from human_in_the_loop.pause_resume import ApprovalError, ApprovalStore, Effects, reprice_step
from human_in_the_loop.request import action_digest

PKG = os.path.join(os.path.dirname(__file__), "..", "human_in_the_loop")
SKU = "NV-ALDSWORTH-DM"


def args(price):
    return {"supplier_sku": SKU, "proposed_price_cents": price}


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def path(tmp_path):
    return str(tmp_path / "pending.json")


@pytest.mark.parametrize("price,band", [
    (39899, "deny"), (39900, "ask"), (39901, "ask"), (42899, "ask"), (42900, "auto"),
])
def test_gate_bands(price, band):
    assert gate_policy("set_price", args(price)) == band


def test_unknown_action_asks():
    assert gate_policy("delete_listing", {}) == "ask"


def test_deny_band_never_creates_a_request(path, clock):
    fx = Effects()
    out = reprice_step(ApprovalStore(path, clock), "r1", "repricer", args(39899), fx)
    assert out.status == "refused" and fx.applied == []
    assert not os.path.exists(path)


def test_auto_band_applies_without_a_person(path, clock):
    fx = Effects()
    out = reprice_step(ApprovalStore(path, clock), "r1", "repricer", args(42900), fx)
    assert out.status == "applied" and fx.applied == [42900]


def test_approve_in_a_fresh_store_applies_once_and_counts_reruns(path, clock):
    fx = Effects()
    first = reprice_step(ApprovalStore(path, clock), "r1", "repricer", args(41000), fx)
    assert first.status == "paused"
    assert (fx.before_pause, fx.applied) == (1, [])
    # a fresh object reads the pending request back from the JSON file
    fresh = ApprovalStore(path, clock)
    fresh.decide("r1", "merchandiser", first.detail)
    out = reprice_step(fresh, "r1", "repricer", args(41000), fx)
    assert out.status == "applied" and fx.applied == [41000]
    assert fx.before_pause == 2  # re-run from the top: written twice
    assert len(fx.applied) == 1  # written once


def test_duplicate_resume_applies_once(path, clock):
    fx = Effects()
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), fx).detail
    store.decide("r1", "merchandiser", d)
    reprice_step(store, "r1", "repricer", args(41000), fx)
    again = reprice_step(ApprovalStore(path, clock), "r1", "repricer", args(41000), fx)
    assert again.detail == "already applied" and fx.applied == [41000]


def test_edit_41000_to_42900_applies_the_edit(path, clock):
    fx = Effects()
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), fx).detail
    store.decide("r1", "merchandiser", d, edited_args=args(42900))
    out = reprice_step(store, "r1", "repricer", args(41000), fx)
    assert out.status == "applied" and fx.applied == [42900]


def test_edit_below_floor_is_refused_and_request_stays_pending(path, clock):
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), Effects()).detail
    with pytest.raises(ApprovalError, match="below the floor"):
        store.decide("r1", "merchandiser", d, edited_args=args(39899))
    assert store.load("r1").status == "pending"


def test_reject_returns_the_reason_to_the_model(path, clock):
    fx = Effects()
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), fx).detail
    store.decide("r1", "merchandiser", d, approve=False, reason="hold for the sale")
    out = reprice_step(store, "r1", "repricer", args(41000), fx)
    assert out.as_tool_result() == {"status": "rejected", "detail": "hold for the sale"}
    assert fx.applied == []


def test_stale_digest_is_refused_at_decision(path, clock):
    store = ApprovalStore(path, clock)
    reprice_step(store, "r1", "repricer", args(41000), Effects())
    old = action_digest("set_price", args(40100))
    with pytest.raises(ApprovalError, match="stale"):
        store.decide("r1", "merchandiser", old)


def test_args_altered_after_approval_are_refused_at_apply(path, clock):
    fx = Effects()
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), fx).detail
    store.decide("r1", "merchandiser", d)
    out = reprice_step(store, "r1", "repricer", args(40100), fx)  # not what was approved
    assert out.status == "refused" and fx.applied == []


def test_requester_cannot_approve_own_request(path, clock):
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), Effects()).detail
    with pytest.raises(ApprovalError, match="requester"):
        store.decide("r1", "repricer", d)


def test_expiry_resolves_to_reject(path, clock):
    fx = Effects()
    store = ApprovalStore(path, clock)
    d = reprice_step(store, "r1", "repricer", args(41000), fx).detail
    clock.t += 3601
    out = reprice_step(store, "r1", "repricer", args(41000), fx)
    assert out.status == "expired" and fx.applied == []
    with pytest.raises(ApprovalError, match="expired"):
        store.decide("r1", "merchandiser", d)


def test_fixtures_avoid_other_chapters_prices():
    assert 19900 not in (39899, 41000, 42900) and 44900 not in (39899, 41000, 42900)


@pytest.mark.parametrize("name", ["pause_resume_langgraph.py", "pause_resume_responses.py"])
def test_illustrations_compile(name):
    py_compile.compile(os.path.join(PKG, name), doraise=True)

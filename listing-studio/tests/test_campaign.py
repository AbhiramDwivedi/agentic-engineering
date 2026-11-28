"""Tests for the long-running agents chapter (9.1) companion code. Offline, stdlib only."""
import json

from campaign import Budget, accept_reprice, load_progress, run_session

PRICES = {"SKU-1": 20.0, "SKU-2": 30.0, "SKU-3": 40.0}


def check(sku, candidate):
    return accept_reprice(sku, candidate, floor=10.0, max_move=0.10, current=PRICES[sku])


def good(sku, snap):
    return {"sku": sku, "new_price": PRICES[sku] * 1.05, "tokens": 100}


def test_cumulative_budget_stops_across_relaunch(tmp_path):
    path = str(tmp_path / "progress.json")
    budget = Budget(cap=150)
    r1 = run_session(path, list(PRICES), good, check, budget)
    assert r1.stopped == "budget" and r1.steps == 2  # 100 + 100 crosses the 150 cap
    # a relaunch inherits spent=200 from the file and refuses to start again
    r2 = run_session(path, list(PRICES), good, check, budget)
    assert r2.stopped == "budget" and r2.steps == 0
    assert load_progress(path, []).spent == 200


def test_second_session_resumes_where_first_stopped(tmp_path):
    path = str(tmp_path / "progress.json")
    budget = Budget(cap=10_000)
    r1 = run_session(path, list(PRICES), good, check, budget, max_steps=2)
    assert r1.stopped == "step_limit" and len(load_progress(path, []).done) == 2
    seen = []

    def spy(sku, snap):
        seen.append(sku)
        return good(sku, snap)

    r2 = run_session(path, list(PRICES), spy, check, budget)
    assert seen == ["SKU-3"] and r2.stopped == "complete"


def test_agent_cannot_write_completion(tmp_path):
    path = str(tmp_path / "progress.json")

    def cheat(sku, snap):
        snap.done[sku] = 999.0  # mutates its copy only
        return {"sku": sku, "new_price": 1.0, "tokens": 1}  # below floor, fails the check

    run_session(path, ["SKU-1"], cheat, check, Budget(cap=100, max_attempts=2))
    assert "SKU-1" not in load_progress(path, []).done


def test_three_failures_then_escalation_record(tmp_path):
    path = str(tmp_path / "progress.json")

    def agent(sku, snap):
        if sku == "SKU-1":
            return {"sku": sku, "new_price": 1.0, "tokens": 5}
        return good(sku, snap)

    r = run_session(path, ["SKU-1", "SKU-2"], agent, check, Budget(cap=1000))
    p = load_progress(path, [])
    assert p.attempts["SKU-1"] == 3
    assert p.escalations == [{"sku": "SKU-1", "reason": "acceptance check failed", "attempts": 3}]
    assert "SKU-2" in p.done and r.stopped == "stuck"
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["escalations"][0]["sku"] == "SKU-1"

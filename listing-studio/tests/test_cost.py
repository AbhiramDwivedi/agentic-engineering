"""Tests for the controlling-cost chapter (8.4) companion code. Offline, stdlib only."""
from cost.budget import run_with_budget
from cost.cascade import cascade
from cost.prompt import build_prompt, prefix_hash

CTX = "Catalog: NV-ALDSWORTH-DM, denim jacket.\n"


def test_prefix_stable_when_only_dynamic_parts_change():
    a = build_prompt(CTX, "Listing A", "2026-11-28T10:00")
    b = build_prompt(CTX, "Listing B", "2026-11-28T10:05")
    assert a != b
    assert prefix_hash(a) == prefix_hash(b)


def test_timestamp_in_the_prefix_breaks_it():
    def bad(now: str) -> str:  # the mistake: dynamic content placed first
        return f"Time: {now}\n" + build_prompt(CTX, "L", "x")

    assert prefix_hash(bad("10:00")) != prefix_hash(bad("10:05"))


def test_cascade_keeps_cheap_answer_when_check_passes():
    r = cascade("t", lambda t: "good", lambda t: "strong", lambda a: a == "good")
    assert (r.model, r.escalated, r.cost) == ("cheap", False, 1)


def test_cascade_escalates_when_check_fails():
    calls = []

    def strong(t):
        calls.append(t)
        return "strong answer"

    r = cascade("t", lambda t: "bad", strong, lambda a: a == "good")
    assert (r.answer, r.escalated, r.cost) == ("strong answer", True, 6)
    assert len(calls) == 1


def test_budget_guard_stops_at_budget():
    r = run_with_budget(lambda i: (f"draft {i}", 400, False), max_tokens=1000)
    assert r.status == "budget_exceeded"
    # Step three would project to 1,200, so the guard stops before it runs.
    assert (r.steps, r.tokens_used) == (2, 800)
    assert r.answer == "draft 2"  # the work done so far is kept


def test_budget_guard_finishes_within_budget():
    r = run_with_budget(lambda i: ("ok", 100, i == 2), max_tokens=1000)
    assert (r.status, r.steps, r.answer) == ("done", 2, "ok")


def test_budget_guard_step_cap():
    r = run_with_budget(lambda i: (f"draft {i}", 1, False), max_tokens=10**6, max_steps=5)
    assert (r.status, r.steps, r.answer) == ("budget_exceeded", 5, "draft 5")


def test_budget_guard_can_still_cross_on_an_unusually_large_step():
    # The projection is the largest step so far, so a bigger step can still cross.
    spends = {1: 100, 2: 900}
    r = run_with_budget(lambda i: (f"draft {i}", spends[i], False), max_tokens=500)
    assert (r.status, r.steps, r.tokens_used, r.answer) == (
        "budget_exceeded", 2, 1000, "draft 2"
    )

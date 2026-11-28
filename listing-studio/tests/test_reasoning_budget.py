"""Tests for the reasoning-budget chapter (4.5) companion code.

Offline: the scripted model's numbers are made up to show the shape of a
sweep; they are not measurements of any real model. The three illustration
files are compile-checked only.
"""
import os
import py_compile

from reasoning_budget.scripted import CASES, exact_match, scripted_model
from reasoning_budget.sweep import bill, cheapest_passing, run_sweep

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "reasoning_budget")


def _sweep(cap):
    return {r.level: r for r in run_sweep(scripted_model, CASES, exact_match, cap=cap)}


def test_sweep_picks_cheapest_passing_level_not_the_highest():
    reports = run_sweep(scripted_model, CASES, exact_match, cap=5000)
    by = {r.level: r for r in reports}
    assert by["none"].quality == 0.5  # hard case fails with no thinking
    assert by["medium"].quality == 1.0
    assert by["high"].quality == 0.5  # overthinks the trivial case (scripted)
    assert cheapest_passing(reports).level == "medium"


def test_cost_rises_with_effort_and_bill_prints_every_level():
    by = _sweep(5000)
    assert by["none"].output_tokens == 120  # 3 repeats x 2 cases x 20 visible
    assert by["none"].cost < by["low"].cost < by["medium"].cost < by["high"].cost
    assert len(bill(list(by.values())).splitlines()) == 4


def test_cap_spent_on_thinking_gives_no_text_but_still_bills():
    by = _sweep(2000)
    assert by["high"].quality == 0.0  # both cases truncated, no visible answer
    assert by["high"].output_tokens == 3 * 2 * 2000  # billed at the full cap
    assert cheapest_passing(list(by.values())).level == "medium"


def test_no_pick_when_nothing_reaches_the_floor():
    reports = run_sweep(scripted_model, CASES, exact_match, cap=5000, levels=["none", "low"])
    assert cheapest_passing(reports) is None  # best is 0.50, below the 0.9 floor


def test_default_cap_matches_the_companion_run():
    default = {r.level: r for r in run_sweep(scripted_model, CASES, exact_match)}
    assert default == _sweep(5000)


def test_main_prints_the_bill_and_the_pick(capsys):
    from reasoning_budget.__main__ import main

    main()
    out = capsys.readouterr().out
    assert len(out.splitlines()) == 5 and out.strip().endswith("ship: medium")


def test_scripted_model_truncates_over_cap():
    reply = scripted_model(CASES[1], "high", 1000)
    assert reply.text == "" and reply.thinking_tokens == 1000


def test_illustration_files_compile():
    for f in ("effort_langgraph.py", "effort_responses.py", "effort_example.py"):
        py_compile.compile(os.path.join(PKG, f), doraise=True)

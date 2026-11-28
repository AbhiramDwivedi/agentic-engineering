"""Tests for the evaluation chapter (4.2) companion code.

All offline and deterministic. The judge provider files are compile-checked
only (they need API keys and the heavy SDKs).
"""
import os
import py_compile

from evals.calibrate import agreement, choose_floor, cohens_kappa, trust_judge
from evals.cases import GOLDEN
from evals.example import (
    CLASSIFIER_SLICE, LABELLED, careful_judge, fake_system, judge_verdicts,
    lenient_judge,
)
from evals.graders import grade_attributes, judge_listing, parse_verdict
from evals.harness import Rate, compare, run_eval

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evals")
CASES = {c.id: c for c in GOLDEN}


def test_golden_set_is_small_tagged_and_has_the_do_nothing_case():
    assert 6 <= len(GOLDEN) <= 10
    assert all(c.failure_mode for c in GOLDEN)
    assert CASES["phonecase-do-nothing"].required == {}


def test_code_grader_passes_correct_and_fails_wrong_or_missing():
    case = CASES["desk-weight-overstated"]
    assert grade_attributes(case, {"weight_capacity_lbs": 250}).passed
    assert not grade_attributes(case, {"weight_capacity_lbs": 300}).passed
    assert not grade_attributes(case, {}).passed


def test_code_grader_passes_a_correct_do_nothing_and_fails_an_invention():
    case = CASES["phonecase-do-nothing"]
    assert grade_attributes(case, {"color": "black"}).passed
    bad = grade_attributes(case, {"prop65_warning": True})
    assert not bad.passed and "invented prop65_warning" in bad.problems


def test_judge_makes_one_isolated_call_per_criterion():
    prompts = []

    def judge(p):
        prompts.append(p)
        return "Yes." if "alpha" in p else "no"

    out = judge_listing(judge, ["alpha", "beta"], "text")
    assert out == {"alpha": True, "beta": False}
    assert len(prompts) == 2
    assert "beta" not in prompts[0] and "alpha" not in prompts[1]


def test_unparseable_judge_reply_fails_closed():
    assert parse_verdict("YES") is True
    assert parse_verdict("I think so") is False


def test_kappa_and_agreement_hand_computed():
    j = [True, True, False, False]
    h = [True, False, False, False]
    assert agreement(j, h) == 0.75
    # observed .75; chance = .5*.25 + .5*.75 = .5; kappa = .5
    assert cohens_kappa(j, h) == 0.5
    assert cohens_kappa(h, h) == 1.0


def test_calibration_catches_the_length_biased_judge():
    human = [h for _, h in LABELLED]
    assert not trust_judge(judge_verdicts(lenient_judge), human)
    assert trust_judge(judge_verdicts(careful_judge), human)


def test_choose_floor_picks_lowest_floor_at_target_and_matches_routing_default():
    assert choose_floor(CLASSIFIER_SLICE, 0.95) == 0.6  # 3.2's confidence_floor
    assert choose_floor([(0.9, False), (0.8, False)], 0.9) is None


def test_gate_refuses_overlapping_intervals_and_accepts_clear_gaps():
    assert compare(Rate(.65, .44, .86), Rate(.85, .71, .99)) == "not distinguishable"
    assert compare(Rate(.3, .2, .4), Rate(.8, .7, .9)) == "b is better"
    assert compare(Rate(.8, .7, .9), Rate(.3, .2, .4)) == "a is better"


def test_example_run_v2_looks_better_but_gate_refuses():
    v1 = run_eval(fake_system("v1", 0), GOLDEN)
    v2 = run_eval(fake_system("v2", 1), GOLDEN)
    assert v2.mean - v1.mean >= 1 / len(GOLDEN)
    assert compare(v1, v2) == "not distinguishable"


def test_run_eval_is_reproducible_for_a_seed():
    assert run_eval(fake_system("v1", 7), GOLDEN) == run_eval(fake_system("v1", 7), GOLDEN)


def test_judge_provider_files_compile():
    for name in ("judge_langgraph.py", "judge_responses.py", "judge_anthropic.py"):
        py_compile.compile(os.path.join(PKG, name), doraise=True)

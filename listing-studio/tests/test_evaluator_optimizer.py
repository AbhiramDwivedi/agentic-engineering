"""Tests for the evaluator-optimizer chapter (3.4) companion code.

All tests are offline: no API key, no network call.

- ClarifyingQuestions / Verdict are imported directly (no third-party deps
  beyond pydantic, which is pure Python).
- gate_draft / evaluate (evaluate.py) are tested for the cheap-first
  ordering: the deterministic gate catches duplicates, empty questions, and
  uncovered gaps on its own, and evaluate() never calls the judge on a
  draft the gate already failed.
- run_loop (loop.py) is tested with stub drafter_fn / judge_fn so the cap,
  the ratchet, and the failure-return contract all run fully offline and
  deterministically.
- run_best_of_n (best_of_n.py) is tested to show the contrast with
  run_loop: independent draws, no feedback, highest scorer wins.
- The three illustration files (LangGraph / Responses / Anthropic) are
  compile-checked via py_compile; they are not executed (they need API keys
  and the heavy provider SDKs, which are not test dependencies).
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from evaluator_optimizer.best_of_n import BestOfNResult, run_best_of_n
from evaluator_optimizer.evaluate import GateResult, evaluate, gate_draft
from evaluator_optimizer.loop import DEFAULT_MAX_ITERATIONS, LoopResult, run_loop
from evaluator_optimizer.schemas import ClarifyingQuestions, Verdict

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "evaluator_optimizer")

LANGGRAPH_FILE = os.path.join(PKG, "evaluator_optimizer_langgraph.py")
RESPONSES_FILE = os.path.join(PKG, "evaluator_optimizer_responses.py")
ANTHROPIC_FILE = os.path.join(PKG, "evaluator_optimizer_example.py")

# The Aldsworth desk again: this time step 2, not step 7 -- two attributes
# the supplier feed left missing or ambiguous.
GAPS = ["leg_material", "weight_capacity_lbs"]


def _good_shaped_draft(tag: str) -> ClarifyingQuestions:
    """A draft that always clears the deterministic gate: one non-empty,
    non-duplicate question per gap, tagged so a test's judge_fn can tell
    which call produced it."""
    return ClarifyingQuestions(
        questions=[f"What is the {gap} ({tag})?" for gap in GAPS]
    )


# ---------------------------------------------------------------------------
# Schemas (anchor: eo-schemas)
# ---------------------------------------------------------------------------

def test_clarifying_questions_accepts_valid_object():
    d = ClarifyingQuestions(questions=["What is the leg_material?"])
    assert d.questions == ["What is the leg_material?"]


def test_clarifying_questions_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ClarifyingQuestions(questions=["x"], stray="nope")  # type: ignore[call-arg]


def test_verdict_accepts_valid_object():
    v = Verdict(passed=False, score=0.4, reasons=["question 2 duplicates question 1"])
    assert v.passed is False
    assert v.reasons


def test_verdict_rejects_extra_fields():
    with pytest.raises(ValidationError):
        Verdict(passed=True, score=1.0, reasons=[], stray="nope")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# The deterministic gate + evaluate (anchor: eo-evaluate)
# Cheap-first ordering: the gate never touches a model, and the judge only
# runs once the gate has already passed.
# ---------------------------------------------------------------------------

def test_gate_passes_a_well_shaped_draft():
    result = gate_draft(GAPS, _good_shaped_draft("v1"))
    assert result == GateResult(ok=True, reasons=[])


def test_gate_rejects_an_empty_question():
    draft = ClarifyingQuestions(questions=["", "What is the weight_capacity_lbs?"])
    result = gate_draft(GAPS, draft)
    assert result.ok is False
    assert any("empty" in r for r in result.reasons)


def test_gate_rejects_duplicate_questions():
    draft = ClarifyingQuestions(
        questions=["What is the leg_material?", "What is the leg_material?"]
    )
    result = gate_draft(GAPS, draft)
    assert result.ok is False
    assert any("duplicate" in r for r in result.reasons)


def test_gate_rejects_an_uncovered_gap():
    draft = ClarifyingQuestions(questions=["What is the leg_material?"])
    result = gate_draft(GAPS, draft)
    assert result.ok is False
    assert any("weight_capacity_lbs" in r for r in result.reasons)


def test_evaluate_short_circuits_before_any_judge_call():
    """The deterministic gate fails; the judge is never spent on it."""
    judge_calls = {"n": 0}

    def judge_fn(gaps, draft):
        judge_calls["n"] += 1
        return Verdict(passed=True, score=1.0, reasons=[])

    bad_draft = ClarifyingQuestions(questions=["", ""])
    verdict = evaluate(judge_fn, GAPS, bad_draft)

    assert verdict.passed is False
    assert judge_calls["n"] == 0


def test_evaluate_calls_the_judge_once_the_gate_passes():
    judge_calls = {"n": 0}

    def judge_fn(gaps, draft):
        judge_calls["n"] += 1
        return Verdict(passed=True, score=0.95, reasons=[])

    verdict = evaluate(judge_fn, GAPS, _good_shaped_draft("v1"))

    assert verdict.passed is True
    assert judge_calls["n"] == 1


# ---------------------------------------------------------------------------
# run_loop (anchor: eo-loop)
# The cap, the ratchet, and the failure-return contract.
# ---------------------------------------------------------------------------

def test_loop_passes_on_round_one_with_no_wasted_judge_calls():
    draft_calls = {"n": 0}
    judge_calls = {"n": 0}

    def drafter_fn(gaps, feedback):
        draft_calls["n"] += 1
        return _good_shaped_draft(f"v{draft_calls['n']}")

    def judge_fn(gaps, draft):
        judge_calls["n"] += 1
        return Verdict(passed=True, score=0.9, reasons=[])

    result = run_loop(drafter_fn, judge_fn, GAPS)

    assert isinstance(result, LoopResult)
    assert result.passed is True
    assert result.stopped_reason == "passed"
    assert result.iterations == 1
    assert draft_calls["n"] == 1
    assert judge_calls["n"] == 1  # exactly one judge call -- nothing wasted


def test_loop_revises_and_then_passes():
    scores = [0.4, 0.9]
    passed_flags = [False, True]
    draft_calls = {"n": 0}
    judge_calls = {"n": 0}

    def drafter_fn(gaps, feedback):
        draft_calls["n"] += 1
        if draft_calls["n"] > 1:
            assert feedback is not None and feedback.reasons  # the critique crossed, not a bare "fail"
        return _good_shaped_draft(f"v{draft_calls['n']}")

    def judge_fn(gaps, draft):
        idx = judge_calls["n"]
        judge_calls["n"] += 1
        reasons = [] if passed_flags[idx] else ["not specific enough"]
        return Verdict(passed=passed_flags[idx], score=scores[idx], reasons=reasons)

    result = run_loop(drafter_fn, judge_fn, GAPS, max_iterations=3)

    assert result.passed is True
    assert result.stopped_reason == "passed"
    assert result.iterations == 2
    assert draft_calls["n"] == 2
    assert judge_calls["n"] == 2
    assert "v2" in result.draft.questions[0]


def test_loop_caps_out_and_returns_the_failure_contract_intact():
    # None of the three rounds pass; round 2 scores highest.
    scores = [0.3, 0.5, 0.4]
    draft_calls = {"n": 0}

    def drafter_fn(gaps, feedback):
        draft_calls["n"] += 1
        return _good_shaped_draft(f"v{draft_calls['n']}")

    def judge_fn(gaps, draft):
        idx = draft_calls["n"] - 1
        return Verdict(passed=False, score=scores[idx], reasons=[f"round {idx + 1} still weak"])

    result = run_loop(drafter_fn, judge_fn, GAPS, max_iterations=3)

    assert result.passed is False
    assert result.stopped_reason == "capped"
    assert result.iterations == DEFAULT_MAX_ITERATIONS
    # The caller can tell "capped out" from "passed" without reading prose,
    # and still gets a real draft and a real verdict -- never None.
    assert result.draft is not None
    assert result.verdict is not None
    assert result.verdict.score == 0.5
    assert "v2" in result.draft.questions[0]


def test_loop_ratchet_discards_a_worse_revision():
    """A revision that scores worse than the draft it replaced is graded
    and counted, but never becomes the returned draft."""
    scores = [0.8, 0.3]  # the revision is strictly worse
    draft_calls = {"n": 0}

    def drafter_fn(gaps, feedback):
        draft_calls["n"] += 1
        return _good_shaped_draft(f"v{draft_calls['n']}")

    def judge_fn(gaps, draft):
        idx = draft_calls["n"] - 1
        return Verdict(passed=False, score=scores[idx], reasons=["needs work"])

    result = run_loop(drafter_fn, judge_fn, GAPS, max_iterations=2)

    assert result.stopped_reason == "capped"
    assert result.iterations == 2  # both rounds ran and were graded
    assert result.verdict.score == 0.8  # the earlier, better verdict
    assert "v1" in result.draft.questions[0]  # the earlier, better draft


# ---------------------------------------------------------------------------
# run_best_of_n (anchor: eo-best-of-n)
# The sibling that isn't a loop: independent draws, no feedback, highest
# scorer wins.
# ---------------------------------------------------------------------------

def test_best_of_n_picks_the_highest_scorer():
    # run_best_of_n draws every candidate before scoring any of them, so the
    # judge identifies a draft by its own tag, not by a shared call counter.
    scores = {"v1": 0.4, "v2": 0.9, "v3": 0.6}
    draft_calls = {"n": 0}

    def drafter_fn(gaps):
        draft_calls["n"] += 1
        return _good_shaped_draft(f"v{draft_calls['n']}")

    def judge_fn(gaps, draft):
        tag = draft.questions[0].split("(")[-1].rstrip("?)")
        return Verdict(passed=scores[tag] >= 0.8, score=scores[tag], reasons=[])

    result = run_best_of_n(drafter_fn, judge_fn, GAPS, n=3)

    assert isinstance(result, BestOfNResult)
    assert result.verdict.score == 0.9
    assert "v2" in result.draft.questions[0]
    assert draft_calls["n"] == 3  # all three drawn independently, up front


def test_best_of_n_never_revises():
    """drafter_fn here takes gaps only -- no feedback parameter exists for
    run_best_of_n to pass, so a revision is not just discouraged, it is not
    representable."""
    calls = []

    def drafter_fn(gaps):
        calls.append(gaps)
        return _good_shaped_draft(f"v{len(calls)}")

    def judge_fn(gaps, draft):
        return Verdict(passed=False, score=float(len(calls)), reasons=[])

    run_best_of_n(drafter_fn, judge_fn, GAPS, n=4)

    assert len(calls) == 4
    assert all(call == GAPS for call in calls)  # every draw sees the same, cold input


# ---------------------------------------------------------------------------
# Illustration files: compile-check only (they need API keys to run)
# ---------------------------------------------------------------------------

def test_langgraph_illustration_is_valid_python():
    py_compile.compile(LANGGRAPH_FILE, doraise=True)


def test_responses_illustration_is_valid_python():
    py_compile.compile(RESPONSES_FILE, doraise=True)


def test_anthropic_illustration_is_valid_python():
    py_compile.compile(ANTHROPIC_FILE, doraise=True)

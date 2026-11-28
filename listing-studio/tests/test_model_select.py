"""Tests for the which-model chapter (8.2) companion code. Offline, fakes only."""
import os
import py_compile

import pytest

from model_select.compare import choose, compare, score
from model_select.config import STEP_MODELS, model_for

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "model_select")

CASES = [("desk", "Office Desks"), ("bunk bed", "Kids Beds"), ("phone case", "Phone Cases")]
TRUTH = dict(CASES)


def fake(wrong: set[str]):
    return lambda p: "Misc" if p in wrong else TRUTH[p]


def test_model_for_each_step_and_unknown_fails_loudly():
    for step, model in STEP_MODELS.items():
        assert model_for(step) == model
    with pytest.raises(KeyError):
        model_for("not_a_step")


def test_score_is_share_correct():
    assert score(fake({"bunk bed"}), CASES) == pytest.approx(2 / 3)


def test_compare_scores_every_model():
    clients = {"a": fake(set()), "b": fake({"bunk bed", "phone case"})}
    assert compare(clients, CASES) == {"a": 1.0, "b": pytest.approx(1 / 3)}


def test_swap_only_when_candidate_beats_current():
    assert choose({"cur": 2 / 3, "new": 1.0}, "cur") == "new"
    assert choose({"cur": 1.0, "new": 1.0}, "cur") == "cur"  # tie keeps current
    assert choose({"cur": 1.0, "new": 2 / 3}, "cur") == "cur"


@pytest.mark.parametrize(
    "fname",
    ["model_select_langgraph.py", "model_select_responses.py", "model_select_example.py"],
)
def test_illustrations_compile(fname):
    py_compile.compile(os.path.join(PKG, fname), doraise=True)

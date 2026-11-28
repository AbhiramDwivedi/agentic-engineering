"""Offline tests for the decision-models companion code (stdlib only)."""
from decision_models.calibrate import calibrate
from decision_models.policy import compliance_gate, decide
from decision_models.question import (
    Answer, FakeDecisionClient, choice, predicate, score,
)

P65 = predicate("Is a required Prop 65 warning missing from the listing?")
SAFE = predicate("Does it make an unverified safety claim?")
LOAD = predicate("Does it overstate weight_capacity_lbs?")


def test_shapes():
    assert predicate("x").options == ("true", "false")
    assert choice("x", ("a", "b", "c")).options == ("a", "b", "c")
    assert score("x", 5).options == ("1", "2", "3", "4", "5")


def test_threshold_acts_or_escalates():
    assert decide(Answer({"true": 0.95, "false": 0.05}), P65) == "true"
    assert decide(Answer({"true": 0.60, "false": 0.40}), P65) == "escalate"


def test_refusal_abstains():
    assert decide(Answer(None, refused=True), P65) == "abstain"


def test_label_without_distribution_escalates():
    assert decide(Answer(None, label="true"), P65) == "escalate"


def test_choice_and_score_use_argmax():
    cat = choice("category?", ("desk", "chair", "case"))
    assert decide(Answer({"desk": 0.93, "chair": 0.05, "case": 0.02}), cat) == "desk"
    s = score("brand voice 1-5", 5)
    assert decide(Answer({"4": 0.97, "3": 0.03}), s) == "4"


def _client(a, b, c):
    return FakeDecisionClient({P65.text: a, SAFE.text: b, LOAD.text: c})


CLEAN = Answer({"true": 0.02, "false": 0.98})


def test_gate_pass_block_escalate_one_request():
    qs = [P65, SAFE, LOAD]
    c = _client(CLEAN, CLEAN, CLEAN)
    assert compliance_gate(c, "NV-ALDSWORTH-DM", qs) == "pass"
    assert c.calls == 1
    bad = Answer({"true": 0.98, "false": 0.02})
    assert compliance_gate(_client(CLEAN, bad, CLEAN), "NV-ALDSWORTH-DM", qs) == "block"
    unsure = Answer({"true": 0.55, "false": 0.45})
    assert compliance_gate(_client(CLEAN, unsure, CLEAN), "NV-PHONECASE-01", qs) == "escalate"
    refused = Answer(None, refused=True)
    assert compliance_gate(_client(CLEAN, refused, CLEAN), "NV-PHONECASE-01", qs) == "escalate"


FIXTURE = [(0.98, True), (0.95, True), (0.92, True), (0.90, True), (0.05, False),
           (0.08, False), (0.70, False), (0.65, True), (0.30, False), (0.55, False)]


def test_calibration_fixture():
    r = calibrate(FIXTURE)
    assert 0.0 <= r["ece"] < 0.3
    assert r["threshold"] == 0.9


def test_calibrate_perfect_model_has_zero_ece():
    assert calibrate([(1.0, True), (0.0, False)])["ece"] == 0.0


def test_empty_or_malformed_distribution_escalates():
    assert decide(Answer({}), P65) == "escalate"
    assert decide(Answer({"true": -3.0, "false": 4.0}), P65) == "escalate"
    assert decide(Answer({"true": float("nan"), "false": 0.5}), P65) == "escalate"


class _ShortClient:
    def __init__(self, answers):
        self.answers = answers

    def decide_many(self, listing, questions):
        return self.answers


def test_gate_escalates_on_missing_judgments():
    qs = [P65, SAFE, LOAD]
    assert compliance_gate(_ShortClient([]), "NV-ALDSWORTH-DM", qs) == "escalate"
    assert compliance_gate(_ShortClient([CLEAN, CLEAN]), "NV-ALDSWORTH-DM", qs) == "escalate"
    assert compliance_gate(_ShortClient([]), "NV-ALDSWORTH-DM", []) == "escalate"

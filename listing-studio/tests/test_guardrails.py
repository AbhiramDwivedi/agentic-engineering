"""Tests for the guardrails chapter (4.4) companion code.

Offline: stdlib + pydantic + anyio only. The classifier is scripted, so there is
no latency to measure; the tests assert verdicts, call order and call counts.
"""
import os
import py_compile

import anyio

from guardrails.checks import Record
from guardrails.classifier import FakeClassifier
from guardrails.pipeline import finish_listing
from guardrails.suite import run_guards

DESK = Record(sku="DESK-ALD-01", supplier_name="Northvale Furnishings",
              weight_capacity_lbs=250, safety_claims=["BIFMA stability"])
BUNK = Record(sku="BUNK-KID-02", supplier_name="Northvale Furnishings",
              safety_claims=["ASTM F1427 guardrail height"])
CASE = Record(sku="CASE-PH-03", supplier_name="Harbor Mobile")

DESK_DRAFT = {"title": "Aldsworth Dual-Motor Sit-Stand Desk",
              "description": "Dual motors, four presets, and a frame that holds up to 250 lb."}
DESK_POLISHED = {"title": "Aldsworth Dual-Motor Sit-Stand Desk",
                 "description": "Dual motors, four presets, and a frame that holds 300 lb with ease."}
BUNK_COPY = {"title": "Kids' Bunk Bed",
             "description": "A sturdy bunk bed with full-length guardrails, CPSC certified."}
LEAK_COPY = {"title": "Aldsworth Dual-Motor Sit-Stand Desk",
             "description": "Ask Dana at dana@northvale.example or 555-014-2297. Wholesale $142.50."}
CASE_COPY = {"title": "Slim Phone Case",
             "description": "A slim case with raised edges and a soft-touch finish for daily use."}


def run(raw, record, clf=None, **kw):
    clf = clf or FakeClassifier()
    return clf, anyio.run(lambda: run_guards(raw, record, clf, **kw))


def test_desk_overclaim_blocked_by_claim_check_not_classifier():
    clf, out = run(DESK_POLISHED, DESK)
    assert out.decision == "review"
    assert [v.check for v in out.verdicts] == ["schema", "claim"]
    assert out.verdicts[-1].reason == "claims 300 lb; record says 250"
    assert clf.calls == []                       # the model was never asked


def test_desk_draft_with_recorded_capacity_publishes():
    clf, out = run(DESK_DRAFT, DESK)
    assert out.decision == "publish"
    assert [v.check for v in out.verdicts] == ["schema", "claim", "leak", "classifier"]
    assert len(clf.calls) == 1


def test_bunk_bed_unsupported_safety_claim_blocked():
    clf, out = run(BUNK_COPY, BUNK)
    assert out.decision == "review"
    assert out.verdicts[-1].reason == "safety claim 'CPSC' is not in the record"
    assert clf.calls == []


def test_supplier_leak_blocked_by_leak_check():
    clf, out = run(LEAK_COPY, DESK)
    assert out.decision == "review"
    assert out.verdicts[-1].check == "leak"
    assert out.verdicts[-1].reason == "supplier email in copy"
    assert clf.calls == []


def test_supplier_name_alone_is_a_leak():
    raw = {"title": "Slim Phone Case",
           "description": "Made for you by Harbor Mobile with a soft-touch finish."}
    _, out = run(raw, CASE)
    assert out.verdicts[-1].reason == "supplier name in copy"


def test_schema_failure_blocks_first():
    clf, out = run({"title": "", "description": "short"}, CASE)
    assert out.decision == "review"
    assert [v.check for v in out.verdicts] == ["schema"]
    assert clf.calls == []


def test_phone_case_passes_every_layer():
    clf, out = run(CASE_COPY, CASE)
    assert out.decision == "publish"
    assert all(v.passed for v in out.verdicts) and len(out.verdicts) == 4
    assert len(clf.calls) == 1


def test_polish_reintroduces_overclaim_and_post_polish_guard_catches_it():
    def polish(d):
        return DESK_POLISHED                     # the rewrite the draft never had
    assert anyio.run(lambda: run_guards(DESK_DRAFT, DESK, FakeClassifier())).decision == "publish"
    clf = FakeClassifier()
    polished, out = anyio.run(lambda: finish_listing(DESK_DRAFT, polish, DESK, clf))
    assert polished == DESK_POLISHED
    assert out.decision == "review" and out.verdicts[-1].check == "claim"


MINI_SET = [  # (marker in text, classifier risk, truly bad?)
    ("alpha", 0.80, True), ("bravo", 0.45, True),
    ("charlie", 0.30, False), ("delta", 0.55, False),
]


def _counts(threshold):
    fp = miss = 0
    for marker, risk, bad in MINI_SET:
        raw = {"title": "Slim Phone Case",
               "description": f"A slim case, style {marker}, with a soft-touch finish."}
        _, out = run(raw, CASE, FakeClassifier({marker: risk}), threshold=threshold)
        blocked = out.decision == "review"
        fp += blocked and not bad
        miss += (not blocked) and bad
    return fp, miss


def test_threshold_flip_changes_outcome_on_labelled_set():
    assert _counts(0.5) == (1, 1)    # blocks alpha and delta; misses bravo
    assert _counts(0.4) == (1, 0)    # catches bravo; delta is still a false positive
    assert _counts(0.9) == (0, 2)    # blocks nothing


def test_classifier_error_fail_closed_goes_to_review():
    clf = FakeClassifier(raises=RuntimeError("503"))
    _, out = run(CASE_COPY, CASE, clf, on_error="closed")
    assert out.decision == "review"
    assert out.verdicts[-1].reason == "classifier RuntimeError; failed closed"


def test_classifier_error_fail_open_publishes_and_says_so():
    clf = FakeClassifier(raises=RuntimeError("503"))
    _, out = run(CASE_COPY, CASE, clf, on_error="open")
    assert out.decision == "publish"
    assert out.verdicts[-1].reason == "classifier RuntimeError; failed open"


def test_classifier_timeout_follows_the_same_policy():
    slow = lambda: FakeClassifier(delay=1.0)     # noqa: E731
    _, closed = run(CASE_COPY, CASE, slow(), timeout=0.05, on_error="closed")
    _, opened = run(CASE_COPY, CASE, slow(), timeout=0.05, on_error="open")
    assert closed.decision == "review" and opened.decision == "publish"
    assert closed.verdicts[-1].reason == "classifier TimeoutError; failed closed"


def test_default_policy_is_fail_closed():
    clf = FakeClassifier(raises=RuntimeError("503"))
    _, out = run(CASE_COPY, CASE, clf)
    assert out.decision == "review"


def test_shadow_check_records_finding_but_does_not_block():
    clf, out = run(DESK_POLISHED, DESK, shadow=frozenset({"claim"}))
    claim = [v for v in out.verdicts if v.check == "claim"][0]
    assert not claim.passed and claim.mode == "shadow"
    assert out.decision == "publish"             # later layers still ran and passed
    assert len(clf.calls) == 1


def test_illustration_compiles():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "guardrails", "guardrails_openai_illustration.py")
    py_compile.compile(path, doraise=True)

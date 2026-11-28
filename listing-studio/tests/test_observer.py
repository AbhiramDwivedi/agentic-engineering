"""Tests for the observer chapter (7.2) companion code. Offline: stdlib only.

The three provider files are compile-checked, not executed.
"""
import os
import py_compile

import pytest

from observer.events import BoundedSink, StepResult, observed_step, outcome_of

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "observer")


def _run(step, sinks):
    return observed_step(sinks, "run-1", "describe", step)


def test_ok_run_emits_start_then_end_ok():
    seen = []
    _run(lambda: StepResult("A sturdy 20L dry bag.", "end_turn"), [seen.append])
    assert [(e.kind, e.outcome) for e in seen] == [("start", None), ("end", "ok")]
    assert seen[0].step_id == "run-1:describe" and seen[0].run_id == "run-1"


def test_raising_sink_does_not_break_the_run():
    def broken(_event):
        raise RuntimeError("dashboard down")

    seen = []
    result = _run(lambda: StepResult("text", "end_turn"), [broken, seen.append])
    assert result.text == "text"
    assert len(seen) == 2  # the healthy sink after the broken one still got both events


def test_empty_result_ends_empty():
    seen = []
    _run(lambda: StepResult("  ", "end_turn"), [seen.append])
    assert seen[-1].kind == "end" and seen[-1].outcome == "empty"


def test_refusal_is_end_refused_not_error():
    seen = []
    _run(lambda: StepResult("", "refusal"), [seen.append])
    assert [e.kind for e in seen] == ["start", "end"]
    assert seen[-1].outcome == "refused"


def test_max_tokens_is_truncated():
    assert outcome_of(StepResult("half a sentence and", "max_tokens")) == "truncated"


def test_step_exception_emits_error_and_reraises():
    seen = []

    def boom():
        raise ValueError("bad feed")

    with pytest.raises(ValueError):
        _run(boom, [seen.append])
    assert seen[-1].kind == "error" and seen[-1].outcome == "error"
    assert seen[-1].error_class == "ValueError"


def test_malformed_result_emits_error_not_just_start():
    seen = []
    with pytest.raises(AttributeError):
        _run(lambda: None, [seen.append])  # a worker that hands back nothing
    assert [e.kind for e in seen] == ["start", "error"]
    assert seen[-1].error_class == "AttributeError"


def test_sink_failure_logs_class_name_only(caplog):
    def leaky(_event):
        raise RuntimeError("supplier price 41.20")

    with caplog.at_level("WARNING"):
        _run(lambda: StepResult("text", "end_turn"), [leaky])
    assert "RuntimeError" in caplog.text
    assert "41.20" not in caplog.text


def test_full_queue_drops_and_counts():
    sink = BoundedSink(maxsize=2)
    _run(lambda: StepResult("ok text", "end_turn"), [sink])  # 2 events fill it
    _run(lambda: StepResult("ok text", "end_turn"), [sink])  # 2 more dropped
    assert sink.queue.qsize() == 2
    assert sink.dropped == 2


@pytest.mark.parametrize(
    "fname", ["observer_langgraph.py", "observer_responses.py", "observer_example.py"]
)
def test_illustrations_compile(fname):
    py_compile.compile(os.path.join(PKG, fname), doraise=True)

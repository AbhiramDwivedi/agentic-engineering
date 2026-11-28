"""Tests for the checkpointing chapter (7.3). Offline: stdlib only."""
import pytest

from checkpointing.checkpoint import Saver, content_key, journaled_send, run, step_key
from checkpointing.receiver import ParamMismatch, Receiver
from checkpointing.scripted import ScriptedModel

FIRST = {"to": "aldsworth", "subject": "Your listing is live"}
SECOND = {"to": "aldsworth", "subject": "Your listing has launched"}


def test_step_in_flight_reruns_and_finished_steps_skip():
    saver, calls = Saver(), []

    def a(s):
        calls.append("a")
        return {**s, "a": 1}

    def b(s):
        calls.append("b")
        if calls.count("b") == 1:
            raise RuntimeError("crash")
        return {**s, "b": 1}

    steps = [("a", a), ("b", b)]
    with pytest.raises(RuntimeError):
        run(steps, saver, {})
    assert saver.done == ["a"]
    out = run(steps, saver, {})
    assert calls == ["a", "b", "b"]  # a skipped, b (in flight) re-ran
    assert out["a"] == 1 and out["b"] == 1


def test_content_key_fails_on_mutated_replay():
    receiver, model = Receiver(), ScriptedModel([FIRST, SECOND])
    for _ in range(2):  # the step ran, crashed before checkpoint, ran again
        params = model.decide("announce")
        receiver.send(content_key(params), params)
    assert len(receiver.effects) == 2  # new wording, new key: duplicate email


def test_step_key_against_strict_receiver_raises_mismatch():
    receiver, model = Receiver(strict=True), ScriptedModel([FIRST, SECOND])
    receiver.send(step_key("r1", "announce"), model.decide("announce"))
    with pytest.raises(ParamMismatch):
        receiver.send(step_key("r1", "announce"), model.decide("announce"))


def test_journaled_replay_dedupes_cleanly():
    receiver, saver = Receiver(strict=True), Saver()
    model = ScriptedModel([FIRST, SECOND])
    assert journaled_send(saver, receiver, "r1", "announce", model) == "done"
    assert journaled_send(saver, receiver, "r1", "announce", model) == "deduped"
    assert len(receiver.effects) == 1
    assert model.calls == 1  # the replay never asked the model again

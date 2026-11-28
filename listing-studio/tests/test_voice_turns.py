"""Tests for the voice-turns chapter (6.4) companion code. Offline, fake clock."""
import os

from voice_turns.turns import FakeClock, State, TurnConfig, TurnTaker


def _taker() -> TurnTaker:
    return TurnTaker(FakeClock(), TurnConfig(endpoint_ms=700, min_interrupt_ms=300))


def _user_turn(t: TurnTaker, talk_ms: int = 1000) -> None:
    t.vad("speech_start")
    t.clock.advance(talk_ms)
    t.vad("speech_end")


def _speaking(t: TurnTaker) -> None:
    _user_turn(t)
    t.clock.advance(700)
    t.tick()
    t.speak(["it", "should", "heat", "a", "200", "square", "foot", "garage"], 250)


def test_endpointing_waits_for_the_silence_timeout():
    t = _taker()
    _user_turn(t)
    t.clock.advance(699)
    t.tick()
    assert t.state == State.ENDPOINTING
    t.clock.advance(1)
    t.tick()
    assert t.state == State.AGENT_THINKING


def test_a_pause_mid_thought_is_not_the_end_of_the_turn():
    t = _taker()
    _user_turn(t)
    t.clock.advance(400)
    t.vad("speech_start")  # user resumes before 700 ms
    assert t.state == State.USER_SPEAKING
    t.clock.advance(5000)
    t.tick()
    assert t.state == State.USER_SPEAKING


def test_barge_in_truncates_at_what_was_actually_played():
    t = _taker()
    _speaking(t)
    t.clock.advance(1000)          # 4 words played
    t.vad("speech_start")
    t.clock.advance(300)           # the user keeps talking: a real interruption
    t.tick()
    assert t.state == State.USER_SPEAKING
    assert t.history == ["it should heat a [interrupted]"]


def test_a_late_playback_completion_does_not_restore_unheard_words():
    t = _taker()
    _speaking(t)
    t.clock.advance(1000)
    t.vad("speech_start")
    t.clock.advance(300)
    t.tick()                       # barge-in: history holds the truncated reply
    t.finish()                     # a stale "playback done" event arrives late
    assert t.state == State.USER_SPEAKING
    assert t.history == ["it should heat a [interrupted]"]


def test_false_interruption_resumes_and_the_reply_stays_whole():
    t = _taker()
    _speaking(t)
    t.clock.advance(1000)
    t.vad("speech_start")
    t.clock.advance(200)           # a cough, shorter than 300 ms
    t.vad("speech_end")
    assert t.state == State.AGENT_SPEAKING
    t.clock.advance(1000)
    t.finish()
    assert t.history[-1] == "it should heat a 200 square foot garage"


def test_barge_in_cancels_an_uncommitted_tool_call():
    t = _taker()
    _user_turn(t)
    t.clock.advance(700)
    t.tick()
    t.begin_tool("add_to_cart")
    t.vad("speech_start")          # the user speaks before the action ran
    assert t.cancelled == ["add_to_cart"]
    assert t.pending_tool is None
    assert t.state == State.USER_SPEAKING


def test_package_has_no_provider_imports():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "voice_turns", "turns.py"), encoding="utf-8") as f:
        src = f.read()
    for name in ("langgraph", "openai", "anthropic"):
        assert f"import {name}" not in src

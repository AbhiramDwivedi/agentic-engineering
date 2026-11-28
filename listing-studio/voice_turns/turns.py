"""A turn-taking state machine for a voice agent, driven by scripted VAD events.

This models the decision logic only (when has the user finished, what did the
user actually hear, was that an interruption), not the signal path. There is no
audio and no network: time comes from an injected clock, so tests are exact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FakeClock:
    """Milliseconds you advance by hand; the real system would read a monotonic clock."""

    def __init__(self) -> None:
        self.now_ms = 0

    def advance(self, ms: int) -> None:
        self.now_ms += ms


# --8<-- [start:voice-states]
class State(str, Enum):
    IDLE = "idle"
    USER_SPEAKING = "user_speaking"
    ENDPOINTING = "endpointing"          # user went quiet; is the turn over?
    AGENT_THINKING = "agent_thinking"    # waiting on the model and any tool call
    AGENT_SPEAKING = "agent_speaking"


@dataclass
class TurnConfig:
    endpoint_ms: int = 700        # silence that closes the user's turn
    min_interrupt_ms: int = 300   # shorter overlap is a cough or "mm-hm", not a barge-in
# --8<-- [end:voice-states]


@dataclass
class TurnTaker:
    clock: FakeClock
    cfg: TurnConfig = field(default_factory=TurnConfig)
    state: State = State.IDLE
    history: list[str] = field(default_factory=list)  # what the model will be told was said
    cancelled: list[str] = field(default_factory=list)
    pending_tool: str | None = None

    _quiet_since: int = 0
    _words: list[str] = field(default_factory=list)
    _ms_per_word: int = 0
    _started_at: int = 0
    _paused_total: int = 0
    _paused_at: int | None = None     # set while the user may be interrupting
    _paused_played: int = 0           # ms of the reply that had played when we paused

    def vad(self, event: str) -> None:
        on_vad(self, event)

    def tick(self) -> None:
        tick(self)

    def begin_tool(self, name: str) -> None:
        """The model asked for an action that has not committed yet."""
        self.pending_tool = name

    def speak(self, words: list[str], ms_per_word: int) -> None:
        """Start playing a reply, word by word."""
        self._words, self._ms_per_word = words, ms_per_word
        self._started_at, self._paused_total = self.clock.now_ms, 0
        self.state = State.AGENT_SPEAKING

    def finish(self) -> None:
        """Playback ended on its own: the whole reply was heard."""
        if self.state != State.AGENT_SPEAKING or self._paused_at is not None:
            return  # stale completion after a barge-in, or playback is paused
        self.history.append(" ".join(self._words))
        self.pending_tool = None
        self.state = State.IDLE


# --8<-- [start:voice-endpoint]
def on_vad(t: "TurnTaker", event: str) -> None:
    """Feed one scripted VAD event: "speech_start" or "speech_end"."""
    tick(t)
    now = t.clock.now_ms
    if event == "speech_start":
        if t.state == State.AGENT_SPEAKING:
            pause_playback(t, now)  # maybe a barge-in; decided in tick()
        elif t.state == State.AGENT_THINKING:
            cancel_pending_tool(t)  # the user spoke before the action ran
            t.state = State.USER_SPEAKING
        else:
            t.state = State.USER_SPEAKING  # also: a pause mid-thought, not the end
    elif event == "speech_end":
        if t._paused_at is not None:
            resume_playback(t, now)  # too short to be an interruption
        elif t.state == State.USER_SPEAKING:
            t.state = State.ENDPOINTING
            t._quiet_since = now


def tick(t: "TurnTaker") -> None:
    """Check the timers against the clock; call it whenever time has moved."""
    now = t.clock.now_ms
    if t.state == State.ENDPOINTING and now - t._quiet_since >= t.cfg.endpoint_ms:
        t.state = State.AGENT_THINKING   # silence long enough: the turn is over
    elif t._paused_at is not None and now - t._paused_at >= t.cfg.min_interrupt_ms:
        interrupt(t)
# --8<-- [end:voice-endpoint]


# --8<-- [start:voice-bargein]
def pause_playback(t: "TurnTaker", now: int) -> None:
    t._paused_at = now
    t._paused_played = now - t._started_at - t._paused_total


def resume_playback(t: "TurnTaker", now: int) -> None:
    t._paused_total += now - t._paused_at   # silence we inserted, not audio played
    t._paused_at = None


def interrupt(t: "TurnTaker") -> None:
    """A real barge-in: stop, and record only what the user heard."""
    heard = t._words[: t._paused_played // t._ms_per_word]
    t.history.append(" ".join(heard) + " [interrupted]")  # honest truncation
    cancel_pending_tool(t)
    t._paused_at = None
    t.state = State.USER_SPEAKING


def cancel_pending_tool(t: "TurnTaker") -> None:
    if t.pending_tool:
        t.cancelled.append(t.pending_tool)   # never committed, so nothing to undo
        t.pending_tool = None
# --8<-- [end:voice-bargein]

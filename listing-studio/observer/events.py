"""The observer pattern for an agent run: one event per step boundary.

Offline and stdlib-only. The steps here are stubs standing in for the
nine-step Listing Studio graph (step 9 is publish); a real step would call
a model and hand back its stop reason.
"""
# --8<-- [start:observer-event]
from __future__ import annotations

import logging
import queue
import time
from dataclasses import dataclass
from typing import Callable, Literal

logger = logging.getLogger(__name__)


Outcome = Literal["ok", "empty", "truncated", "refused", "error"]


@dataclass(frozen=True)
class Event:
    run_id: str
    step_id: str
    parent_id: str | None
    kind: Literal["start", "end", "error"]
    outcome: Outcome | None  # set on "end" and "error" only
    at: float  # monotonic seconds
    error_class: str | None = None


@dataclass(frozen=True)
class StepResult:
    text: str
    stop_reason: str  # normalised: "end_turn", "max_tokens" or "refusal"


def outcome_of(result: StepResult) -> Outcome:
    """Structural check only: presence and stop reason, never meaning."""
    if result.stop_reason == "refusal":
        return "refused"
    if result.stop_reason == "max_tokens":
        return "truncated"
    if not result.text.strip():
        return "empty"
    return "ok"
# --8<-- [end:observer-event]


# --8<-- [start:observer-emit]
Sink = Callable[[Event], None]


def emit(sinks: list[Sink], event: Event) -> None:
    """Fail open: a broken subscriber is logged, never allowed to break the run."""
    for sink in sinks:
        try:
            sink(event)
        except Exception as exc:
            # Class name only: a sink's error message can carry customer data.
            logger.warning("observer sink failed (%s); run continues",
                           type(exc).__name__)
# --8<-- [end:observer-emit]


# --8<-- [start:observer-step]
def observed_step(
    sinks: list[Sink],
    run_id: str,
    name: str,
    step: Callable[[], StepResult],
    parent_id: str | None = None,
) -> StepResult:
    """Run one step, reporting start and end (or error) around it."""
    step_id = f"{run_id}:{name}"

    def event(kind, outcome=None, error_class=None) -> Event:
        return Event(run_id, step_id, parent_id, kind, outcome,
                     time.monotonic(), error_class)

    emit(sinks, event("start"))
    try:
        result = step()
        outcome = outcome_of(result)  # a malformed result is an error too
    except Exception as exc:
        emit(sinks, event("error", "error", type(exc).__name__))
        raise  # the observer reports; deciding what happens next is not its job
    emit(sinks, event("end", outcome))
    return result
# --8<-- [end:observer-step]


# --8<-- [start:observer-sink]
class BoundedSink:
    """A queue-backed sink that drops when full, and counts what it dropped."""

    def __init__(self, maxsize: int = 100) -> None:
        self.queue: queue.Queue[Event] = queue.Queue(maxsize=maxsize)
        self.dropped = 0

    def __call__(self, event: Event) -> None:
        try:
            self.queue.put_nowait(event)
        except queue.Full:
            self.dropped += 1  # a slow reader never stalls the run
# --8<-- [end:observer-sink]

"""Checkpointing: save state between steps, resume from the last saved one.

The step in flight is not saved, so it runs again on resume.
"""
from __future__ import annotations

# --8<-- [start:ckpt-step]
import hashlib
import json
from typing import Callable

from .receiver import Receiver
from .scripted import ScriptedModel

Step = Callable[[dict], dict]  # a step maps state to new state
# --8<-- [end:ckpt-step]


# --8<-- [start:ckpt-saver]
class Saver:
    """In-memory stand-in for a durable store (a database row in production)."""

    def __init__(self):
        self.done: list[str] = []   # names of steps that finished
        self.state: dict = {}       # state as of the last finished step
        self.journal: dict[str, dict] = {}  # step -> the effect it first issued
# --8<-- [end:ckpt-saver]


# --8<-- [start:ckpt-run]
def run(steps: list[tuple[str, Step]], saver: Saver, state: dict) -> dict:
    """Run steps in order; checkpoint after each. Resume skips finished steps."""
    state = {**state, **saver.state}
    for name, step in steps:
        if name in saver.done:
            continue                       # finished before the crash
        state = step(state)                # if this raises, nothing is saved
        saver.done.append(name)            # checkpoint: between steps only
        saver.state = dict(state)
    return state
# --8<-- [end:ckpt-run]


# --8<-- [start:ckpt-keys]
def content_key(params: dict) -> str:
    """Fragile: a replayed step with new wording gets a new key."""
    return hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]


def step_key(run_id: str, step: str) -> str:
    """Stable across replays, but the receiver must compare parameters."""
    return f"{run_id}:{step}"
# --8<-- [end:ckpt-keys]


# --8<-- [start:ckpt-journal]
def journaled_send(saver: Saver, receiver: Receiver, run_id: str,
                   step: str, model: ScriptedModel) -> str:
    """Replay returns the first attempt's recorded effect, not the model's new one."""
    if step not in saver.journal:
        saver.journal[step] = model.decide(step)   # record before sending
    return receiver.send(step_key(run_id, step), saver.journal[step])
# --8<-- [end:ckpt-journal]

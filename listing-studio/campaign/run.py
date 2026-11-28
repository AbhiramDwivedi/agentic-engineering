"""One campaign session of the Repricer, relaunched until the task list is done.

Offline and local: the agent is any callable, the state lives in one JSON file.
The agent never gets the file. It gets a read-only snapshot and returns a candidate;
only this module writes completion records, and only after an acceptance check passes.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable


# --8<-- [start:campaign-progress]
@dataclass
class Progress:
    """Everything a fresh session needs to know. The context window holds none of it."""
    tasks: list[str]                                          # SKUs the campaign must reprice
    done: dict[str, float] = field(default_factory=dict)      # sku -> accepted price (code-written)
    attempts: dict[str, int] = field(default_factory=dict)    # sku -> failed attempts so far
    spent: int = 0                                            # cumulative tokens across relaunches
    escalations: list[dict] = field(default_factory=list)     # items waiting for a human

    def pending(self) -> list[str]:
        stuck = {e["sku"] for e in self.escalations}
        return [t for t in self.tasks if t not in self.done and t not in stuck]


def load_progress(path: str, tasks: list[str]) -> Progress:
    """Read the progress file at startup; first launch seeds it from the task list."""
    if not os.path.exists(path):
        return Progress(tasks=list(tasks))
    with open(path, encoding="utf-8") as f:
        return Progress(**json.load(f))


def save_progress(path: str, p: Progress) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(p.__dict__, f, indent=2)
    os.replace(tmp, path)  # a crash mid-write never leaves a half file
# --8<-- [end:campaign-progress]


# --8<-- [start:campaign-budget]
@dataclass
class Budget:
    """A cap on the whole campaign, not on one session. `spent` is restored from the file."""
    cap: int
    max_attempts: int = 3

    def left(self, p: Progress) -> int:
        return self.cap - p.spent
# --8<-- [end:campaign-budget]


# --8<-- [start:campaign-accept]
def accept_reprice(sku: str, candidate: dict, floor: float, max_move: float, current: float) -> bool:
    """The acceptance check: code decides whether a task is done, never the agent."""
    price = candidate.get("new_price")
    if candidate.get("sku") != sku or not isinstance(price, (int, float)):
        return False
    return price >= floor and abs(price - current) / current <= max_move
# --8<-- [end:campaign-accept]


@dataclass
class SessionResult:
    stopped: str  # "complete" | "budget" | "stuck" | "step_limit"
    steps: int = 0


Agent = Callable[[str, Progress], dict]  # (sku, read-only snapshot) -> candidate incl. "tokens"
Check = Callable[[str, dict], bool]


# --8<-- [start:campaign-session]
def run_session(path: str, tasks: list[str], agent: Agent, check: Check,
                budget: Budget, max_steps: int = 20) -> SessionResult:
    p = load_progress(path, tasks)                       # 1. resume from the file, not from memory
    steps = 0
    while steps < max_steps:                             # 2. stop condition: steps
        todo = p.pending()
        if not todo:
            return SessionResult("complete" if not p.escalations else "stuck", steps)
        if budget.left(p) <= 0:                          # 3. stop condition: cumulative budget
            save_progress(path, p)
            return SessionResult("budget", steps)
        sku = todo[0]
        snapshot = Progress(**json.loads(json.dumps(p.__dict__)))  # the agent gets a copy
        candidate = agent(sku, snapshot)
        steps += 1
        p.spent += int(candidate.get("tokens", 0))
        if check(sku, candidate):                         # 4. only code writes completion
            p.done[sku] = candidate["new_price"]
        else:
            p.attempts[sku] = p.attempts.get(sku, 0) + 1
            if p.attempts[sku] >= budget.max_attempts:   # 5. give up loudly, hand to a human
                p.escalations.append({"sku": sku, "reason": "acceptance check failed",
                                      "attempts": p.attempts[sku]})
        save_progress(path, p)
    return SessionResult("step_limit", steps)
# --8<-- [end:campaign-session]

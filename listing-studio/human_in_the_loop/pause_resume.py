"""Pause and resume in plain Python: the request is JSON on disk, so a fresh
process (or a fresh object) can pick it up. Resuming re-runs the step from the
top, which is how LangGraph's interrupt() behaves too."""
import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from .gate import gate_policy
from .request import ApprovalRequest, action_digest

TTL_SECONDS = 3600


class ApprovalError(Exception):
    """A decision the store refuses: stale digest, own request, bad edit."""


@dataclass
class Effects:
    """What the step did to the world, so tests can count it."""
    before_pause: int = 0  # an audit write placed before the pause
    applied: list = field(default_factory=list)  # prices actually written


@dataclass
class Outcome:
    status: str  # applied | paused | rejected | refused | expired
    detail: str = ""

    def as_tool_result(self) -> dict:
        return {"status": self.status, "detail": self.detail}  # the model reads this


# --8<-- [start:hitl-store]
class ApprovalStore:
    def __init__(self, path: str, now: Callable[[], float] = time.time):
        self.path, self.now = path, now

    def _all(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def save(self, req: ApprovalRequest) -> None:
        data = self._all()
        data[req.request_id] = req.model_dump()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, request_id: str) -> Optional[ApprovalRequest]:
        raw = self._all().get(request_id)
        if raw is None:
            return None
        req = ApprovalRequest(**raw)
        if req.status == "pending" and self.now() >= req.expires_at:
            req.status = "expired"  # silence resolves to reject, never to approve
            self.save(req)
        return req

    def decide(self, request_id, approver, digest, approve=True, reason=None, edited_args=None):
        req = self.load(request_id)
        if req.status != "pending":
            raise ApprovalError(f"request is {req.status}")
        if approver == req.requester:
            raise ApprovalError("the requester cannot approve their own request")
        if digest != req.digest:
            raise ApprovalError("stale approval: it was given for a different action")
        if approve and edited_args is not None:
            if gate_policy(req.action, edited_args) == "deny":
                raise ApprovalError("edit refused: below the floor")  # re-banded after the edit
            req.edited_args = edited_args
        req.status = "approved" if approve else "rejected"
        req.decided_by, req.reason = approver, reason
        self.save(req)
# --8<-- [end:hitl-store]


# --8<-- [start:hitl-step]
def reprice_step(store, request_id, requester, args, fx: Effects) -> Outcome:
    """Runs from the top every time it is called, first run and every resume."""
    fx.before_pause += 1  # a write before the pause happens again on resume
    action = "set_price"
    band = gate_policy(action, args)
    if band == "deny":
        return Outcome("refused", "below the MAP floor")
    if band == "ask":
        req = store.load(request_id)
        if req is None:
            req = ApprovalRequest(
                request_id=request_id, requester=requester, action=action, args=args,
                digest=action_digest(action, args), expires_at=store.now() + TTL_SECONDS)
            store.save(req)
        if req.digest != action_digest(action, args):
            return Outcome("refused", "arguments changed since the request was made")
        if req.status == "pending":
            return Outcome("paused", req.digest)  # the person sees this
        if req.status in ("rejected", "expired"):
            return Outcome(req.status, req.reason or "no decision")
        if req.status == "applied":
            return Outcome("applied", "already applied")  # duplicate resume writes nothing
        args = req.edited_args or args
        req.status = "applied"
        store.save(req)
    fx.applied.append(args["proposed_price_cents"])  # the write that must happen once
    return Outcome("applied", str(args["proposed_price_cents"]))
# --8<-- [end:hitl-step]

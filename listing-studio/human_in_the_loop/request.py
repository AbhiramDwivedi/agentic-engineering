"""What the person is shown, and the digest their answer is bound to."""
import hashlib
import json
from typing import Optional

from pydantic import BaseModel


# --8<-- [start:hitl-request]
def action_digest(action: str, args: dict) -> str:
    """Hash of the exact action. An approval carries this, so approving one
    price cannot be replayed against another."""
    canonical = json.dumps({"action": action, "args": args}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


class ApprovalRequest(BaseModel):
    request_id: str  # the idempotency key, and the thread the step resumes on
    requester: str
    action: str
    args: dict
    digest: str
    expires_at: float
    status: str = "pending"  # pending | approved | rejected | expired | applied
    decided_by: Optional[str] = None
    reason: Optional[str] = None
    edited_args: Optional[dict] = None
# --8<-- [end:hitl-request]

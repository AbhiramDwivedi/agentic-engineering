"""Where the guard sits: after the polish step, on the text that would ship."""
from __future__ import annotations

from typing import Callable

from .checks import Record
from .classifier import FakeClassifier
from .suite import run_guards
from .verdict import Outcome


# --8<-- [start:guard-pipeline]
async def finish_listing(draft: dict, polish: Callable[[dict], dict],
                         record: Record, clf: FakeClassifier) -> tuple[dict, Outcome]:
    polished = polish(draft)               # step 8 may rewrite anything
    outcome = await run_guards(polished, record, clf)   # so check what it returned
    return polished, outcome               # "review" means a human reads it; no rewrite here
# --8<-- [end:guard-pipeline]

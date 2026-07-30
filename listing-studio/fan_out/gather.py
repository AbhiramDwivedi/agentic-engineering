"""The fan-in: run every named deliverable concurrently, merge under a
stable key, and never let one bad worker take down the other N-1.

gather() is the shared core both halves of step 7 call: fixed.py's literal
three deliverables and plan.py's model-named extras both end up here, and
this file cannot tell which kind of list it was handed. That is the point
this chapter makes at the code level -- the fan-in has no idea, and does not
need one, whether the count above it was decided by code or by a model.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import anyio

from .schemas import WorkerResult


# --8<-- [start:fanout-gather]
@dataclass
class FanOutSummary:
    """The fan-in's output: every result keyed by deliverable_id -- never by
    the order workers happened to finish in -- plus a structured summary a
    synthesizer or a human can read without inspecting results by hand."""
    results: dict[str, WorkerResult]
    ok_count: int
    failed_count: int
    summary: str  # e.g. "2 of 3 completed; worker `compliance_insert` failed: timeout"


def _run_worker_safe(worker_fn: Any, deliverable_id: str, listing: dict) -> WorkerResult:
    """Run one worker and turn any exception into a structured failure.

    A raised exception here must never propagate past gather() and take the
    other N-1 workers down with it -- the partial-failure contract this
    chapter promises.
    """
    try:
        content = worker_fn(deliverable_id, listing)
        return WorkerResult(deliverable_id=deliverable_id, ok=True, content=content)
    except Exception as exc:
        return WorkerResult(deliverable_id=deliverable_id, ok=False, error=str(exc))


async def _run_all(
    worker_fn: Any, deliverable_ids: list[str], listing: dict
) -> dict[str, WorkerResult]:
    results: dict[str, WorkerResult] = {}

    async def _one(deliverable_id: str) -> None:
        # Written under its own key -- not appended -- so two workers
        # finishing in any order still land at the right place.
        results[deliverable_id] = await anyio.to_thread.run_sync(
            _run_worker_safe, worker_fn, deliverable_id, listing
        )

    async with anyio.create_task_group() as tg:
        for deliverable_id in deliverable_ids:
            tg.start_soon(_one, deliverable_id)
    return results


def gather(worker_fn: Any, deliverable_ids: list[str], listing: dict) -> FanOutSummary:
    """Run every deliverable_id's worker concurrently and merge the results.

    Three obligations live here. Results land in `results` keyed by
    deliverable_id, so a caller reading results["price_safe_ad_variant"]
    gets the right answer regardless of which worker actually finished
    first -- never trust arrival order. A failing worker never raises past
    this function: it comes back as a WorkerResult with ok=False, folded
    into `summary` as a structured, recoverable line, while the other N-1
    results are still complete. And every `.content` string in `results` is
    untrusted output from a model that read whatever the listing and
    supplier feed handed it -- see render_for_synthesis, the only
    sanctioned way to pass it on.
    """
    if not deliverable_ids:
        return FanOutSummary(
            results={}, ok_count=0, failed_count=0,
            summary="0 of 0 deliverables (nothing to run)",
        )

    results = anyio.run(_run_all, worker_fn, deliverable_ids, listing)
    failed = sorted(k for k, v in results.items() if not v.ok)
    ok_count = len(results) - len(failed)

    if failed:
        failure_notes = "; ".join(f"worker `{k}` failed: {results[k].error}" for k in failed)
        summary = f"{ok_count} of {len(results)} completed; {failure_notes}"
    else:
        summary = f"{ok_count} of {len(results)} completed"

    return FanOutSummary(results=results, ok_count=ok_count, failed_count=len(failed), summary=summary)


def render_for_synthesis(summary: FanOutSummary) -> str:
    """Render every successful worker's output as untrusted input -- the
    same discipline 2.1 Tool Use applies to a single tool result, now
    required at every worker boundary. A failed worker's error text never
    enters this string; only gather()'s own `summary` line reports failures
    to whatever reads this next.
    """
    blocks = []
    for deliverable_id in sorted(summary.results):
        result = summary.results[deliverable_id]
        if not result.ok:
            continue
        blocks.append(
            f'<worker_output id="{deliverable_id}" trust="untrusted">\n'
            f"{result.content}\n"
            "</worker_output>"
        )
    return "\n".join(blocks)
# --8<-- [end:fanout-gather]

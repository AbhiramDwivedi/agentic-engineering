"""The typed result of one section, and the truncation rule.

Imports only pydantic and fan_out's WorkerResult, so it runs offline.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from fan_out.schemas import WorkerResult


# --8<-- [start:assembly-schemas]
class SectionResult(BaseModel):
    """One section's outcome: its status, its text and the sources it used."""
    model_config = ConfigDict(extra="forbid")

    section_id: str
    status: Literal["ok", "failed", "truncated"]
    body: str = ""
    source_ids: list[str] = []
    reason: str | None = None


def from_worker(worker: WorkerResult, source_ids: list[str]) -> SectionResult:
    """Wrap 3.3's WorkerResult and attach the ids its schema does not carry."""
    if not worker.ok:
        return SectionResult(
            section_id=worker.deliverable_id, status="failed", reason=worker.error
        )
    return SectionResult(
        section_id=worker.deliverable_id,
        status="ok",
        body=worker.content or "",
        source_ids=source_ids,
    )


# Anthropic: stop_reason "max_tokens" or "model_context_window_exceeded".
# OpenAI Responses: status "incomplete" (reason "max_output_tokens").
CUT_OFF = {"max_tokens", "model_context_window_exceeded", "incomplete"}


def from_reply(
    section_id: str, text: str, stop: str, source_ids: list[str]
) -> SectionResult:
    if stop in CUT_OFF:
        return SectionResult(
            section_id=section_id,
            status="truncated",
            body=text,
            source_ids=source_ids,
            reason=f"output cut off ({stop})",
        )
    return SectionResult(
        section_id=section_id, status="ok", body=text, source_ids=source_ids
    )
# --8<-- [end:assembly-schemas]

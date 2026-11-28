"""In-memory job queue: the endpoint, the worker lease, the idempotency key, the supervisor.

Time is passed in as a plain number (``now``) so tests control it; no sleeping, no threads.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

# --8<-- [start:jobs-record]
LEASE_SECONDS = 30.0


@dataclass
class Job:
    job_id: str
    idempotency_key: str
    payload: dict
    status: str = "queued"  # queued | running | done | abandoned
    worker: str | None = None
    lease_expires: float = 0.0
    attempts: int = 0
    result: str | None = None


@dataclass
class JobStore:
    jobs: dict[str, Job] = field(default_factory=dict)
    by_key: dict[str, str] = field(default_factory=dict)
    effects: dict[str, str] = field(default_factory=dict)  # idempotency key -> recorded side effect
# --8<-- [end:jobs-record]


# --8<-- [start:jobs-endpoint]
def submit(store: JobStore, payload: dict, idempotency_key: str) -> str:
    """The endpoint: enqueue and return a job id."""
    if idempotency_key in store.by_key:
        return store.by_key[idempotency_key]
    job = Job(job_id=uuid.uuid4().hex[:8], idempotency_key=idempotency_key, payload=payload)
    store.jobs[job.job_id] = job
    store.by_key[idempotency_key] = job.job_id
    return job.job_id
# --8<-- [end:jobs-endpoint]


# --8<-- [start:jobs-lease]
def claim(store: JobStore, worker: str, now: float) -> Job | None:
    """The worker takes the oldest queued job under a lease that expires unless renewed."""
    for job in store.jobs.values():
        if job.status == "queued":
            job.status, job.worker = "running", worker
            job.lease_expires = now + LEASE_SECONDS
            job.attempts += 1
            return job
    return None


def heartbeat(store: JobStore, job_id: str, worker: str, now: float) -> bool:
    """Renew the lease. False means the job was reclaimed and this worker must stop."""
    job = store.jobs[job_id]
    if job.status != "running" or job.worker != worker:
        return False
    job.lease_expires = now + LEASE_SECONDS
    return True
# --8<-- [end:jobs-lease]


# --8<-- [start:jobs-idempotent]
def complete(store: JobStore, job: Job, worker: str, side_effect: str) -> bool:
    """Finish a job. The side effect is recorded once per idempotency key, however often it runs."""
    if job.worker != worker:  # lost the lease; a newer worker owns this job
        return False
    if job.idempotency_key not in store.effects:
        store.effects[job.idempotency_key] = side_effect
    job.status, job.result = "done", store.effects[job.idempotency_key]
    return True
# --8<-- [end:jobs-idempotent]


# --8<-- [start:jobs-supervisor]
def reclaim_stalled(store: JobStore, now: float, max_attempts: int = 3) -> list[str]:
    """The supervisor: requeue running jobs whose lease lapsed. Past max_attempts, stop retrying."""
    reclaimed = []
    for job in store.jobs.values():
        if job.status == "running" and job.lease_expires < now:
            job.worker = None
            job.status = "queued" if job.attempts < max_attempts else "abandoned"
            reclaimed.append(job.job_id)
    return reclaimed
# --8<-- [end:jobs-supervisor]

"""Tests for the deployment & runtimes chapter (8.7) companion code. Offline, stdlib only."""
from jobs.queue import LEASE_SECONDS, JobStore, claim, complete, heartbeat, reclaim_stalled, submit


def test_submit_returns_id_without_running_and_is_idempotent():
    s = JobStore()
    a = submit(s, {"sku": "LS-1"}, "key-1")
    b = submit(s, {"sku": "LS-1"}, "key-1")
    assert a == b and len(s.jobs) == 1
    assert s.jobs[a].status == "queued" and s.jobs[a].attempts == 0


def test_heartbeat_extends_lease_and_prevents_reclaim():
    s = JobStore()
    jid = submit(s, {}, "k")
    job = claim(s, "w1", now=0)
    assert heartbeat(s, jid, "w1", now=25)
    assert reclaim_stalled(s, now=LEASE_SECONDS + 1) == []
    assert job.status == "running"


def test_stalled_job_is_reclaimed_and_redelivery_applies_side_effect_once():
    s = JobStore()
    jid = submit(s, {}, "k")
    job = claim(s, "w1", now=0)
    assert reclaim_stalled(s, now=LEASE_SECONDS + 1) == [jid]
    assert job.status == "queued"
    claim(s, "w2", now=40)
    assert heartbeat(s, jid, "w1", now=41) is False  # the old worker is told to stop
    assert complete(s, job, "w2", "published") is True
    assert complete(s, job, "w1", "published-again") is False
    assert s.effects == {"k": "published"} and job.attempts == 2


def test_same_key_resubmitted_after_done_does_not_repeat_effect():
    s = JobStore()
    jid = submit(s, {}, "k")
    job = claim(s, "w1", now=0)
    complete(s, job, "w1", "published")
    assert submit(s, {}, "k") == jid
    assert len(s.effects) == 1


def test_three_attempts_then_abandoned():
    s = JobStore()
    jid = submit(s, {}, "k")
    now = 0.0
    for _ in range(3):
        claim(s, "w", now=now)
        now += LEASE_SECONDS + 1
        reclaim_stalled(s, now=now)
    assert s.jobs[jid].status == "abandoned" and s.jobs[jid].result is None
    assert s.jobs[jid].attempts == 3

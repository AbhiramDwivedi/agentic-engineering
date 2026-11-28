"""Tests for the state-not-memory chapter (5.1) companion code. Fully offline:
no model call anywhere; the LangGraph graphs here run for real."""
import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import ErrorCode, InvalidUpdateError

from state.durable import FileSaver, recover, run_once
from state.parallel import overwrite_demo, run_reduced, run_unreduced
from state.run_state import merge_status


def test_unreduced_parallel_write_raises():
    with pytest.raises(InvalidUpdateError) as e:
        run_unreduced()
    assert ErrorCode.INVALID_CONCURRENT_GRAPH_UPDATE.value in str(e.value)


def test_reduced_parallel_write_keeps_both():
    assert sorted(run_reduced()) == ["below MAP", "title too long"]


def test_sequential_overwrite_silently_loses_first_write():
    assert overwrite_demo() == ["title too long"]


def test_merge_status_updates_only_its_own_step():
    assert merge_status({"a": "done"}, {"b": "failed"}) == {"a": "done", "b": "failed"}


def test_in_memory_saver_loses_thread_after_restart():
    run_once(InMemorySaver())
    assert recover(InMemorySaver()) == {}      # new instance = restarted process


def test_durable_saver_keeps_thread_after_restart(tmp_path):
    path = tmp_path / "checkpoints.pkl"
    run_once(FileSaver(path))
    assert recover(FileSaver(path)) == {
        "supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39900}

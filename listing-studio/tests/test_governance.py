"""Tests for the governance chapter (8.6) companion code. Offline, stdlib + pydantic."""
import json
from datetime import datetime, timezone

from governance import RecordWriter, disclosure_label

FIXED = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


def _writer(tmp_path):
    return RecordWriter(tmp_path / "records.jsonl", now=lambda: FIXED)


def _write(w, **over):
    base = dict(actor="listing-agent", action="publish_listing", reason="passed review",
                model="claude-sonnet-5-5", prompt_version="copy-v3")
    base.update(over)
    return w.write(**base)


def test_one_json_line_per_record(tmp_path):
    w = _writer(tmp_path)
    _write(w)
    _write(w, action="reprice")
    lines = (tmp_path / "records.jsonl").read_text().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["record_id"] == "rec-000001"
    assert first["at"] == FIXED.isoformat()
    assert first["overridden_by"] is None


def test_override_is_recorded(tmp_path):
    w = _writer(tmp_path)
    _write(w, overridden_by="merchant-42")
    assert w.read_all()[0].overridden_by == "merchant-42"


def test_append_only_correction_leaves_original_untouched(tmp_path):
    w = _writer(tmp_path)
    _write(w)
    before = (tmp_path / "records.jsonl").read_text()
    fix = w.correct("rec-000001", actor="reviewer-7", action="unpublish_listing",
                    reason="wrong price", model="claude-sonnet-5-5", prompt_version="copy-v3")
    after = (tmp_path / "records.jsonl").read_text()
    assert after.startswith(before)
    assert fix.corrects == "rec-000001" and fix.record_id == "rec-000002"


def test_reopen_continues_numbering(tmp_path):
    _write(_writer(tmp_path))
    assert _write(_writer(tmp_path)).record_id == "rec-000002"


def test_disclosure_label():
    assert disclosure_label(surface="chat", ai_generated=True).startswith("You are chatting")
    assert disclosure_label(surface="listing", ai_generated=True) == "Written by AI."
    assert "reviewed by a person" in disclosure_label(
        surface="listing", ai_generated=True, human_reviewed=True)
    assert disclosure_label(surface="listing", ai_generated=False) == ""

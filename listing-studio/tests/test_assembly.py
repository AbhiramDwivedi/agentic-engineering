"""Tests for the synthesis chapter (6.2) companion code. Offline: stdlib and
pydantic only; the fake editing pass is a plain function.

The three polish_* illustration files are compile-checked, not executed.
"""
import os
import py_compile

import pytest
from pydantic import ValidationError

from assembly.checks import find_conflicts, find_repeats
from assembly.gate import publish_gate
from assembly.polish import fidelity_diff, polish_checked
from assembly.schemas import SectionResult, from_reply, from_worker
from assembly.template import LAUNCH_TEMPLATE, assemble
from fan_out.schemas import WorkerResult

PKG = os.path.join(os.path.dirname(__file__), "..", "assembly")

BODIES = {
    "description": "The Aldsworth desk lifts smoothly across a 60 inch top.",
    "specs": "Desktop 60 x 30 in. Capacity 250 lbs. Dual motor.",
    "bullets": "Dual motor lift. Holds 250 lbs. Four memory presets.",
    "prop65": "WARNING: this product can expose you to chemicals known to the State of California.",
}


def ok(sid, body=None):
    return SectionResult(
        section_id=sid, status="ok", body=body or BODIES[sid], source_ids=[f"spec-{sid}"]
    )


def all_ok():
    return {sid: ok(sid) for sid in BODIES}


def test_layout_is_fixed_by_template_not_arrival_order():
    results = dict(reversed(list(all_ok().items())))
    text = assemble(LAUNCH_TEMPLATE, results).text
    heads = [h for h in text.split("\n") if h.startswith("## ")]
    assert heads == [
        "## Description", "## Specifications", "## Highlights",
        "## California Prop 65 notice",
    ]


def test_source_ids_survive_assembly():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text
    assert "[src:spec-specs]" in text


def test_failed_required_section_blocks_publishing():
    results = all_ok()
    results["prop65"] = SectionResult(section_id="prop65", status="failed", reason="timeout")
    a = assemble(LAUNCH_TEMPLATE, results)
    assert a.blocked == ["prop65"]
    reasons = publish_gate(a, a.text, {f"spec-{s}" for s in BODIES})
    assert "required section missing: prop65" in reasons


def test_failed_optional_section_is_marked_omitted():
    a = assemble(LAUNCH_TEMPLATE, all_ok())
    assert a.omitted == ["faq"] and a.blocked == []


def test_truncated_section_is_not_ok():
    r = from_reply("bullets", "Dual motor lift. Holds", "max_tokens", ["s"])
    assert r.status == "truncated"
    assert from_reply("bullets", "done.", "end_turn", ["s"]).status == "ok"
    assert from_reply("bullets", "x", "incomplete", ["s"]).status == "truncated"
    a = assemble(LAUNCH_TEMPLATE, {**all_ok(), "bullets": r})
    assert a.blocked == ["bullets"]


def test_from_worker_wraps_fan_out_result():
    good = from_worker(WorkerResult(deliverable_id="specs", ok=True, content="x"), ["a"])
    bad = from_worker(WorkerResult(deliverable_id="specs", ok=False, error="boom"), ["a"])
    assert (good.status, good.source_ids) == ("ok", ["a"])
    assert (bad.status, bad.reason, bad.body) == ("failed", "boom", "")


def test_section_result_forbids_extra_fields():
    with pytest.raises(ValidationError):
        SectionResult(section_id="a", status="ok", surprise=1)


def test_contradiction_found_and_canonical_wins():
    tables = {
        "description": {"desktop_size_in": "60x28"},
        "specs": {"desktop_size_in": "60x30"},
    }
    (c,) = find_conflicts(tables)
    assert c.key == "desktop_size_in" and c.winner == "60x30"


def test_unresolved_conflict_has_no_winner():
    tables = {"description": {"weight": "250"}, "bullets": {"weight": "300"}}
    (c,) = find_conflicts(tables)
    assert c.winner is None


def test_no_conflict_when_sections_agree():
    assert find_conflicts({"a": {"w": "250"}, "b": {"w": "250"}}) == []


def test_repeated_selling_point_detected():
    sections = {
        "description": "Whisper quiet dual motors lift the desk in seconds.",
        "faq": "Is it loud? Whisper quiet dual motors lift the desk.",
        "specs": "Capacity 250 lbs.",
    }
    assert find_repeats(sections) == [("description", "faq")]


def test_failed_editing_call_keeps_unpolished_text():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text

    def cut_off(t):
        raise RuntimeError("editing pass cut off")

    out, problems = polish_checked(cut_off, text)
    assert out == text and problems == ["editing pass failed: editing pass cut off"]


def test_context_window_stop_is_truncated():
    r = from_reply("specs", "60 x 30 in, 250", "model_context_window_exceeded", ["s"])
    assert r.status == "truncated"


def test_polish_that_rewords_is_accepted():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text
    out, problems = polish_checked(lambda t: t.replace("lifts smoothly", "glides up"), text)
    assert problems == [] and out != text


def test_polish_that_changes_a_number_is_rejected():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text
    out, problems = polish_checked(lambda t: t.replace("250", "300"), text)
    assert out == text
    assert "dropped '250'" in problems and "added '300'" in problems


def test_polish_that_drops_prop65_notice_is_rejected():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text
    cut = text.split("## California")[0]
    out, problems = polish_checked(lambda t: cut, text)
    assert out == text and problems


def test_polish_that_loses_a_source_id_is_rejected():
    text = assemble(LAUNCH_TEMPLATE, all_ok()).text
    assert fidelity_diff(text, text.replace("[src:spec-specs]", ""))


def test_gate_passes_clean_page():
    a = assemble(LAUNCH_TEMPLATE, all_ok())
    assert publish_gate(a, a.text, {f"spec-{s}" for s in BODIES}) == []


def test_gate_catches_leaks_unknown_ids_and_length():
    a = assemble(LAUNCH_TEMPLATE, all_ok())
    bad = a.text + " {{price}} <tool_call> [src:ghost]"
    reasons = publish_gate(a, bad, {f"spec-{s}" for s in BODIES})
    assert "leaked text: {{" in reasons
    assert "leaked text: <tool_call" in reasons
    assert "unknown source id: ghost" in reasons
    assert any(r.startswith("length out of bounds") for r in publish_gate(a, "short", set()))


@pytest.mark.parametrize(
    "fname", ["polish_langgraph.py", "polish_responses.py", "polish_anthropic.py"]
)
def test_illustration_files_compile(fname):
    py_compile.compile(os.path.join(PKG, fname), doraise=True)

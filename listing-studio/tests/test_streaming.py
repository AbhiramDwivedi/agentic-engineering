"""Tests for the streaming & agent UX chapter (6.3). Offline: scripted streams only."""
import os
import py_compile

from streaming.events import UIEvent
from streaming.harness import reduce, run_tool_call, run_turn
from streaming.translate import translate_anthropic, translate_openai

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "streaming")

ANTHROPIC = [
    {"type": "message_start"},
    {"type": "ping"},
    {"type": "content_block_start", "content_block": {"type": "text"}},
    {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Repricing "}},
    {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "now."}},
    {"type": "content_block_stop"},
    {"type": "content_block_start",
     "content_block": {"type": "tool_use", "id": "t1", "name": "update_price"}},
    {"type": "content_block_delta", "delta": {"type": "input_json_delta", "partial_json": '{"supplier_sku": "NV-ALDSWORTH-DM'}},
    {"type": "content_block_delta", "delta": {"type": "input_json_delta", "partial_json": '", "price_cents": 41900}'}},
    {"type": "content_block_stop"},
    {"type": "brand_new_event_type"},
    {"type": "message_stop"},
]

OPENAI = [
    {"type": "response.output_text.delta", "delta": "Repricing "},
    {"type": "response.output_text.delta", "delta": "now."},
    {"type": "response.output_item.added", "output_index": 1,
     "item": {"type": "function_call", "id": "i1", "call_id": "t1", "name": "update_price"}},
    {"type": "response.function_call_arguments.delta", "item_id": "i1", "output_index": 1,
     "delta": '{"supplier_sku": '},
    {"type": "response.function_call_arguments.done", "item_id": "i1", "output_index": 1,
     "arguments": '{"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 41900}'},
    {"type": "response.something_new"},
    {"type": "response.completed"},
]


def _shape(events):
    return [(e.kind, e.text, e.call_id, e.tool, e.args) for e in events]


def test_both_providers_translate_to_the_same_ui_events():
    a = list(translate_anthropic(ANTHROPIC))
    o = list(translate_openai(OPENAI))
    assert _shape(a) == _shape(o)
    assert [e.kind for e in a] == ["text", "text", "tool_call", "done"]
    assert a[2].args == {"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 41900}


def test_midstream_error_becomes_error_event():
    out = list(translate_anthropic([{"type": "error", "error": {"message": "overloaded"}}]))
    assert out == [UIEvent(kind="error", text="overloaded")]


def _call():
    return UIEvent(kind="tool_call", call_id="t1", tool="update_price",
                   args={"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 41900})


def test_write_tool_waits_for_approval_and_declined_never_runs():
    ran = []
    tools = {"update_price": lambda supplier_sku, price_cents: ran.append(supplier_sku) or "ok"}
    out = list(run_tool_call(_call(), tools, approve=lambda c: False))
    assert [e.kind for e in out] == ["approval", "tool_result"]
    assert out[-1].ok is False and ran == []


def test_approved_write_runs_and_read_tool_skips_approval():
    tools = {"update_price": lambda supplier_sku, price_cents: "ok", "get_price": lambda supplier_sku: 41900}
    out = list(run_tool_call(_call(), tools, approve=lambda c: True))
    assert [e.kind for e in out] == ["approval", "tool_result"] and out[-1].ok
    read = UIEvent(kind="tool_call", call_id="t2", tool="get_price", args={"supplier_sku": "NV-ALDSWORTH-DM"})
    assert [e.kind for e in run_tool_call(read, tools, approve=lambda c: False)] == ["tool_result"]


def test_done_state_comes_from_tool_results_not_model_text():
    state = {"transcript": "", "steps": {}}
    for e in [UIEvent(kind="text", text="Price updated, all done!"), _call()]:
        reduce(state, e)
    assert state["steps"] == {"t1": "running"}  # the model said done; the UI does not
    tools = {"update_price": lambda supplier_sku, price_cents: 1 / 0}
    for e in run_tool_call(_call(), tools, approve=lambda c: True):
        reduce(state, e)
    assert state["steps"] == {"t1": "failed"}


def test_illustrations_compile():
    for f in ("stream_anthropic.py", "stream_openai.py"):
        py_compile.compile(os.path.join(PKG, f), doraise=True)


def test_openai_failed_and_incomplete_end_the_run_as_errors():
    failed = {"type": "response.failed", "response": {"error": {"message": "server_error"}}}
    incomplete = {"type": "response.incomplete",
                  "response": {"incomplete_details": {"reason": "max_output_tokens"}}}
    assert list(translate_openai([failed])) == [UIEvent(kind="error", text="server_error")]
    assert list(translate_openai([incomplete])) == [UIEvent(kind="error", text="max_output_tokens")]


def test_openai_item_without_id_still_maps_and_unknown_call_does_not_crash():
    stream = [e for e in OPENAI if e["type"] != "response.output_item.added"]
    added = {"type": "response.output_item.added", "output_index": 1,
             "item": {"type": "function_call", "call_id": "t1", "name": "update_price"}}
    assert _shape(translate_openai([added, *stream])) == _shape(translate_openai(OPENAI))
    assert [e.kind for e in translate_openai(stream)] == ["text", "text", "error", "done"]


def test_invalid_tool_json_is_an_error_not_a_call():
    bad = [{"type": "content_block_start",
            "content_block": {"type": "tool_use", "id": "t1", "name": "update_price"}},
           {"type": "content_block_delta",
            "delta": {"type": "input_json_delta", "partial_json": '{"supplier_sku": "NV-'}},
           {"type": "content_block_stop"}]
    out = list(translate_anthropic(bad))
    assert [(e.kind, e.call_id) for e in out] == [("error", "t1")]
    state = reduce({"transcript": "", "steps": {}}, out[0])
    assert state["steps"] == {"t1": "failed"}


def test_error_fails_every_open_step():
    state = {"transcript": "", "steps": {}}
    for e in [_call(), UIEvent(kind="approval", call_id="t1"),
              UIEvent(kind="tool_call", call_id="t2", tool="get_price"),
              UIEvent(kind="error", text="overloaded")]:
        reduce(state, e)
    assert state["steps"] == {"t1": "failed", "t2": "failed"}
    assert state["error"] == "overloaded"


def test_run_turn_wires_translator_harness_and_reducer():
    ran = []
    tools = {"update_price": lambda supplier_sku, price_cents: ran.append(price_cents) or "ok"}
    state = {"transcript": "", "steps": {}}
    out = list(run_turn(ANTHROPIC, translate_anthropic, tools, lambda c: False, state))
    assert [e.kind for e in out] == ["text", "text", "tool_call", "approval", "tool_result", "done"]
    assert state == {"transcript": "Repricing now.", "steps": {"t1": "failed"}} and ran == []

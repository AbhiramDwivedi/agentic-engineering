"""Tests for 8.1 telemetry. Offline: scripted fake model, in-memory sink, stdlib only."""
import os
import py_compile

from telemetry.run import MAX_STEPS, run_listing
from telemetry.trace import InMemorySink, RedactingSink

HERE = os.path.dirname(os.path.abspath(__file__))
MERCHANT = "dana@stockwell-merchant.example"


def _script(*replies):
    it = iter(replies)
    return lambda messages: next(it)


def _reply(text="", tool=None, finish="end_turn"):
    r = {"text": text, "model": "claude-sonnet-5-5-20261101", "input_tokens": 100,
         "output_tokens": 20, "finish_reason": finish}
    if tool:
        r["tool_call"] = tool
        r["finish_reason"] = "tool_use"
    return r


def _tool_run(sink, capture=False):
    client = _script(
        _reply(tool={"name": "lookup_sku", "args": {"sku": "NV-ALDSWORTH-DM", "note": MERCHANT}}),
        _reply(text="Listing drafted."),
    )
    tools = {"lookup_sku": lambda sku, note: f"{sku} ok"}
    return run_listing(sink, client, tools, f"Draft a listing, contact {MERCHANT}", capture)


def test_trace_is_parent_linked():
    sink = InMemorySink()
    _tool_run(sink)
    by_name = {s.name: s for s in sink.spans}
    root = by_name["invoke_agent listing-studio"]
    assert root.parent_id is None
    assert len({s.trace_id for s in sink.spans}) == 1
    assert [s.attributes["gen_ai.operation.name"] for s in sink.spans] == [
        "chat", "execute_tool", "chat", "invoke_agent"]
    assert all(s.parent_id == root.span_id for s in sink.spans if s is not root)


def test_model_span_has_tokens_and_no_content_by_default():
    sink = InMemorySink()
    _tool_run(sink)
    chat = sink.spans[0].attributes
    assert chat["gen_ai.usage.input_tokens"] == 100
    assert chat["gen_ai.response.model"] == "claude-sonnet-5-5-20261101"
    assert not any("messages" in k or k == "tool.arguments"
                   for s in sink.spans for k in s.attributes)


def test_opt_in_captures_content():
    sink = InMemorySink()
    _tool_run(sink, capture=True)
    assert MERCHANT in str(sink.spans[0].attributes["gen_ai.input.messages"])
    assert sink.spans[1].attributes["tool.arguments"]["sku"] == "NV-ALDSWORTH-DM"


def test_redactor_removes_merchant_contact_before_export():
    inner = InMemorySink()
    _tool_run(RedactingSink(inner), capture=True)
    exported = str([s.attributes for s in inner.spans])
    assert MERCHANT not in exported
    assert "[contact]" in exported


def test_raising_redactor_does_not_crash_and_leaks_nothing():
    def boom(text):
        raise RuntimeError("redactor bug")

    inner = InMemorySink()
    out = _tool_run(RedactingSink(inner, redact=boom), capture=True)
    assert out == "Listing drafted."  # the run finished
    assert len(inner.spans) == 4  # every span still exported, ids intact
    assert MERCHANT not in str([s.attributes for s in inner.spans])
    assert all("gen_ai.input.messages" not in s.attributes for s in inner.spans)


def test_step_cap_stops_a_looping_model():
    sink = InMemorySink()
    loop = {"name": "lookup_sku", "args": {"sku": "X", "note": ""}}
    client = lambda m: _reply(tool=loop)
    out = run_listing(sink, client, {"lookup_sku": lambda sku, note: "ok"}, "go")
    assert out == "stopped: step cap reached"
    assert sum(s.attributes["gen_ai.operation.name"] == "chat" for s in sink.spans) == MAX_STEPS


def test_otel_illustration_compiles():
    py_compile.compile(os.path.join(HERE, "..", "telemetry", "telemetry_otel.py"), doraise=True)


def test_failing_exporter_does_not_take_the_run_down():
    class BrokenSink:
        def export(self, span):
            raise RuntimeError("export failed")

    assert _tool_run(BrokenSink()) == "Listing drafted."


def test_captured_input_is_a_snapshot():
    sink = InMemorySink()
    _tool_run(sink, capture=True)
    first_chat = next(s for s in sink.spans if s.name.startswith("chat"))
    assert len(first_chat.attributes["gen_ai.input.messages"]) == 1

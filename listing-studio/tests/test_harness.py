"""Tests for chapter 2.6 (the harness). Offline: a scripted model, no network.

The three illustration files (LangGraph / OpenAI Agents SDK / Anthropic Agent
SDK) are compile-checked only; they need provider SDKs that are not test deps.
"""
import os
import py_compile

from harness import scenario
from harness.compact import compact
from harness.hook import combine, post_tool
from harness.limits import Limits
from harness.loop import Call, Turn, run
from harness.policy import Rule, decide, session_tools

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "harness")


def _reset():
    scenario.DRAFTS.clear()


def test_scenario_outcomes_in_order():
    _reset()
    res = scenario.run_ingest()
    outcomes = [(e["name"], e["outcome"]) for e in res.trace.events]
    assert outcomes == [
        ("read_supplier_row", "allow"), ("write_draft", "allow"),
        ("read_supplier_row", "allow"), ("write_draft", "allow"),
        ("publish", "absent"), ("write_draft", "deny"),
        ("write_draft", "ask"), ("write_draft", "post_blocked"),
        ("spend_cap", "stop"),
    ]
    assert res.stop_reason == "spend_cap" and res.spent_cents == 400


def test_publish_absent_and_never_ran():
    _reset()
    res = scenario.run_ingest()
    assert all(d["status"] == "draft" for d in scenario.DRAFTS.values())
    errs = [m["content"] for m in res.messages if m.get("is_error")]
    assert any("no such tool 'publish'" in e for e in errs)


def test_draft_only_rule_survives_compaction_when_pinned():
    _reset()
    archived = []
    res = scenario.run_ingest(archive=archived.append)
    assert archived, "pre_compact archive should have fired"
    assert any(m["content"] == scenario.DRAFT_ONLY for m in res.messages)
    assert any("compacted" in m["content"] for m in res.messages)


def test_unpinned_rule_is_lost_in_compaction():
    msgs = [{"role": "system", "content": "draft only"}] + [
        {"role": "user", "content": str(i)} for i in range(20)]
    out = compact(msgs, max_messages=10, keep_last=3, pre_compact=lambda m: None)
    assert not any(m["content"] == "draft only" for m in out)


def test_deny_returns_to_model_as_error_result_with_reason():
    _reset()
    res = scenario.run_ingest()
    denied = [m for m in res.messages if "rule: deny write_draft" in m["content"]]
    assert denied and denied[0]["is_error"] is True


def test_default_is_deny():
    assert decide([], "anything", {})[0] == "deny"
    assert decide([Rule("allow", "a")], "b", {})[0] == "deny"


def test_first_match_wins():
    rules = [Rule("deny", "t"), Rule("allow", "t")]
    assert decide(rules, "t", {})[0] == "deny"


def test_session_tools_leaves_out_unwanted():
    assert set(session_tools({"a": 1, "b": 2}, {"a"})) == {"a"}


def test_raising_hook_fails_closed():
    def broken(tool, args):
        raise RuntimeError("boom")
    verdict, reason = combine(("allow", "rule"), [broken], "t", {})
    assert verdict == "deny" and "boom" in reason


def test_raising_post_hook_blocks():
    def broken(tool, result):
        raise RuntimeError("boom")
    assert "boom" in post_tool([broken], "t", {})


def test_hook_allow_does_not_beat_deny_or_ask():
    always_allow = lambda tool, args: ("allow", "hook says fine")
    assert combine(("deny", "r"), [always_allow], "t", {})[0] == "deny"
    assert combine(("ask", "r"), [always_allow], "t", {})[0] == "ask"


def test_hook_can_tighten_an_allow():
    block = lambda tool, args: ("deny", "frozen")
    assert combine(("allow", "r"), [block], "t", {}) == ("deny", "frozen")


def test_hook_reason_reaches_the_model():
    model = scenario.ScriptedModel([Turn(calls=[Call("t", {})])])
    freeze = lambda tool, args: ("deny", "code freeze: no changes")
    res = run(model, {"t": lambda: "ok"}, [Rule("allow", "t")],
              [{"role": "user", "content": "go"}], Limits(), pre=[freeze])
    assert any("code freeze: no changes" in m["content"] for m in res.messages)


def test_on_stop_hook_can_send_the_run_back():
    notes = iter(["check the drafts first", None])
    model = scenario.ScriptedModel([Turn("done?"), Turn("really done")])
    res = run(model, {}, [], [{"role": "user", "content": "go"}], Limits(),
              on_stop=lambda msgs: next(notes))
    assert res.stop_reason == "done"
    assert any(m["content"] == "check the drafts first" for m in res.messages)


def test_step_cap_stops_the_run():
    loop_forever = lambda msgs, names: Turn(calls=[Call("t", {})])
    res = run(loop_forever, {"t": lambda: "ok"}, [Rule("allow", "t")],
              [{"role": "user", "content": "go"}], Limits(max_steps=3))
    assert res.stop_reason == "step_cap"


def test_timeout_uses_injected_clock():
    ticks = iter([0.0, 5.0, 100.0, 100.0, 100.0])
    limits = Limits(timeout_s=60, clock=lambda: next(ticks))
    assert limits.stop_reason(0, 0) is None
    assert limits.stop_reason(1, 0) is None
    assert limits.stop_reason(2, 0) == "timeout"


def test_ask_approved_runs_the_tool():
    model = scenario.ScriptedModel([Turn(calls=[Call("t", {})])])
    res = run(model, {"t": lambda: "ok"}, [Rule("ask", "t")],
              [{"role": "user", "content": "go"}], Limits(),
              approve=lambda tool, args: True)
    assert res.trace.events[0]["outcome"] == "allow"


def test_trace_has_one_event_per_decision():
    _reset()
    res = scenario.run_ingest()
    tool_events = [e for e in res.trace.events if e["kind"] == "tool"]
    assert len(tool_events) == 8


def test_illustrations_are_valid_python():
    for name in ("harness_langgraph.py", "harness_openai_agents.py",
                 "harness_claude_agent_sdk.py"):
        py_compile.compile(os.path.join(PKG, name), doraise=True)

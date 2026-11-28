"""Offline tests for chapter 2.5: a scripted model, the five exits, no network."""
from types import SimpleNamespace as NS

from agent_loop import agent_loop_example, agent_loop_responses, tools as tools_mod
from agent_loop.loop import (
    ABNORMAL, CEILING, CLEAN, CONTINUE, END, FALSE_DONE, STALLED, Call, Turn, run_loop,
)
from agent_loop.tools import make_tools, price_is_valid

SKU = "NV-ALDSWORTH-DM"


def scripted(turns):
    """A fake model: replays the given turns; when they run out, repeats the last."""
    it = iter(turns)
    last = []

    def model(history):
        if (t := next(it, None)) is not None:
            last[:] = [t]
        return last[0]

    return model


def call(name, i=1, **args):
    return Turn("", [Call(f"c{i}", name, args)], CONTINUE)


def run(turns, **kw):
    submitted = []
    history = [{"role": "user", "text": "Price the desk."}]
    result = run_loop(
        scripted(turns), make_tools(submitted), history,
        verify=lambda: price_is_valid(submitted, SKU), **kw,
    )
    return result, history, submitted


def flaky_feed(failures):
    state = {"n": 0}

    def feed(sku):
        state["n"] += 1
        if state["n"] <= failures:
            raise TimeoutError("market feed timed out after 5s; retry")
        return [41900, 44500, 39900]

    return feed


def test_timeout_is_an_error_result_the_model_recovers_from(monkeypatch):
    monkeypatch.setattr(tools_mod, "market_feed", flaky_feed(1))
    result, history, submitted = run([
        call("lookup_market", 1, supplier_sku=SKU),
        call("lookup_market", 2, supplier_sku=SKU),  # the retry
        call("check_price", 3, supplier_sku=SKU, proposed_price_cents=41900),
        call("submit_for_review", 4, supplier_sku=SKU, price_cents=41900),
        Turn("Submitted 41900.", [], END),
    ])
    assert result.exit == CLEAN and result.steps == 5 and result.answer
    tool_msgs = [m for m in history if m["role"] == "tool"]
    assert tool_msgs[0]["is_error"] and "TimeoutError" in tool_msgs[0]["content"]
    assert not tool_msgs[1]["is_error"]
    assert submitted == [41900]


def test_truncated_reply_is_not_an_answer():
    result, _, _ = run([call("check_price", supplier_sku=SKU, proposed_price_cents=41900),
                        Turn("The price should be", [], "max_tokens")])
    assert result.exit == ABNORMAL and result.answer is None
    assert result.detail == "max_tokens"


def test_refusal_is_not_an_answer():
    result, _, _ = run([Turn("", [], "refusal")])
    assert result.exit == ABNORMAL and result.detail == "refusal"


def test_same_failing_call_repeated_stalls(monkeypatch):
    monkeypatch.setattr(tools_mod, "market_feed", flaky_feed(99))
    result, _, _ = run([call("lookup_market", supplier_sku=SKU)], max_steps=10)
    assert result.exit == STALLED and result.steps == 3


def test_retry_with_different_arguments_is_not_a_stall(monkeypatch):
    monkeypatch.setattr(tools_mod, "market_feed", flaky_feed(99))
    turns = [call("lookup_market", i, supplier_sku=f"S{i}") for i in range(1, 4)]
    result, _, _ = run(turns + [Turn("gave up", [], END)])
    assert result.exit == FALSE_DONE  # not STALLED: three different calls


def test_done_without_submitting_is_false_done():
    result, _, submitted = run([Turn("All done.", [], END)])
    assert result.exit == FALSE_DONE and not submitted


def test_done_after_a_price_below_the_floor_is_false_done():
    result, _, submitted = run([
        call("submit_for_review", supplier_sku=SKU, price_cents=38900),
        Turn("Submitted, done.", [], END),
    ])
    assert submitted == [38900] and result.exit == FALSE_DONE


def test_step_cap_ends_a_model_that_never_stops():
    turns = [call("check_price", i, supplier_sku=SKU, proposed_price_cents=40000 + i)
             for i in range(1, 20)]
    result, history, _ = run(turns, max_steps=4)
    assert result.exit == CEILING and result.answer is None and result.steps == 4


def test_anthropic_stop_reasons_map_to_turns():
    def reply(stop, *blocks):
        return NS(stop_reason=stop, content=list(blocks))

    text = NS(type="text", text="hi")
    use = NS(type="tool_use", id="t1", name="check_price", input={"supplier_sku": SKU})
    to_turn = agent_loop_example.to_turn
    assert to_turn(reply("tool_use", use)).stop == CONTINUE
    assert to_turn(reply("tool_use", use)).calls[0].id == "t1"
    assert to_turn(reply("end_turn", text)).stop == END
    for stop in ("max_tokens", "refusal", "pause_turn", "model_context_window_exceeded"):
        assert to_turn(reply(stop, text)).stop == stop


def test_responses_status_and_refusal_map_to_turns():
    def resp(output, status="completed", reason=None):
        return NS(output=output, output_text="x", status=status,
                  incomplete_details=NS(reason=reason) if reason else None)

    fn = NS(type="function_call", call_id="k1", name="check_price",
            arguments='{"supplier_sku": "S", "proposed_price_cents": 1}')
    msg = NS(type="message", content=[NS(type="output_text")])
    refused = NS(type="message", content=[NS(type="refusal")])
    to_turn = agent_loop_responses.to_turn
    assert to_turn(resp([fn])).calls[0].args["proposed_price_cents"] == 1
    assert to_turn(resp([msg])).stop == END
    assert to_turn(resp([msg], "incomplete", "max_output_tokens")).stop == "max_output_tokens"
    assert to_turn(resp([refused])).stop == "refusal"

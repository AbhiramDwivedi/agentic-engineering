import os
import py_compile

from pricing.tools import check_price, get_competitor_prices

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(HERE, "..", "pricing", "tool_use_example.py")
MULTI_EXAMPLE = os.path.join(HERE, "..", "pricing", "multi_tool_example.py")


def test_guardrail_rejects_sub_map_price():
    # $389.00 is under the $399.00 MAP floor.
    out = check_price("NV-ALDSWORTH-DM", 38900)
    assert out["ok"] is False
    assert out["floor_cents"] == 39900


def test_guardrail_accepts_in_policy_price():
    out = check_price("NV-ALDSWORTH-DM", 44900)
    assert out["ok"] is True


def test_competitor_prices_have_the_expected_shape():
    out = get_competitor_prices("NV-ALDSWORTH-DM")
    assert out["prices_cents"], "feed must return at least one price"
    assert all(isinstance(p, int) for p in out["prices_cents"])


def test_examples_are_valid_python():
    # The illustrations need a key and a network call to run, so we do not execute
    # them. We do guarantee they stay valid, importable Python.
    py_compile.compile(EXAMPLE, doraise=True)
    py_compile.compile(MULTI_EXAMPLE, doraise=True)

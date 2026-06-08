import os
import py_compile

from pricing.tools import check_price

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(HERE, "..", "pricing", "tool_use_example.py")


def test_guardrail_rejects_sub_map_price():
    # $389.00 is under the $399.00 MAP floor.
    out = check_price("NV-ALDSWORTH-DM", 38900)
    assert out["ok"] is False
    assert out["floor_cents"] == 39900


def test_guardrail_accepts_in_policy_price():
    out = check_price("NV-ALDSWORTH-DM", 44900)
    assert out["ok"] is True


def test_example_is_valid_python():
    # The illustration needs a key and a network call to run, so we do not execute
    # it. We do guarantee it stays valid, importable Python.
    py_compile.compile(EXAMPLE, doraise=True)

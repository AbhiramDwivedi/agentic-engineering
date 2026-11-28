"""Offline tests for 4.1. A fake model obeys whichever rules its prompt states."""
import os
import py_compile

import pytest
from dataclasses import replace

from prompt_management.release import LIVE_V1, Release, run_golden
from prompt_management.template import VOICE_V1

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "prompt_management")

DATA = {"copy": "The Aldsworth desk, $419.00, SKU NV-ALDSWORTH-DM"}
CASES = [(DATA, ["$419.00", "NV-ALDSWORTH-DM"], ["best-in-class"])]

# v2 "improves" the voice but drops the guard rules; a stricter-sounding
# prompt that loses the price is the regression the gate must catch.
VOICE_V2_BAD = replace(
    VOICE_V1, version="voice@2",
    instructions="You polish Stockwell copy into a punchy, premium voice.",
)
VOICE_V3_GOOD = replace(
    VOICE_V1, version="voice@3",
    instructions=VOICE_V1.instructions + "\n3. Prefer short sentences.",
)


def fake_model(cfg, data):
    """Deterministic stand-in: keeps price/SKU only if rule 1 is in the prompt."""
    system, user = cfg.prompt.render(**data)
    if "Keep every price and SKU" in system:
        return "A friendly desk. " + data["copy"]
    return "A best-in-class premium desk."


def test_render_separates_instructions_from_data():
    system, user = VOICE_V1.render(**DATA)
    assert system == VOICE_V1.instructions
    assert "$419.00" not in system
    assert user.startswith("<copy>") and "$419.00" in user


def test_render_raises_on_missing_slot():
    with pytest.raises(KeyError, match="copy"):
        VOICE_V1.render()


def test_golden_passes_for_live_and_fails_for_bad():
    assert run_golden(LIVE_V1, CASES, fake_model) == []
    bad = replace(LIVE_V1, prompt=VOICE_V2_BAD)
    assert run_golden(bad, CASES, fake_model)


def test_bad_change_is_blocked_and_live_untouched():
    rel = Release(LIVE_V1)
    failures = rel.propose(replace(LIVE_V1, prompt=VOICE_V2_BAD), CASES, fake_model)
    assert failures and rel.live is LIVE_V1 and rel.history == []


def test_good_change_promotes_then_rolls_back_whole_config():
    rel = Release(LIVE_V1)
    cand = replace(LIVE_V1, prompt=VOICE_V3_GOOD, model="gpt-6.2-sol")
    assert rel.propose(cand, CASES, fake_model) == []
    assert rel.live.prompt.version == "voice@3"
    back = rel.rollback()
    assert back is LIVE_V1 and back.model == "claude-sonnet-5-5"


def test_illustration_files_compile():
    for f in ("prompt_management_langgraph.py", "prompt_management_responses.py",
              "prompt_management_example.py"):
        py_compile.compile(os.path.join(PKG, f), doraise=True)

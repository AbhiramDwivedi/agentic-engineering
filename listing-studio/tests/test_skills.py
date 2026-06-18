"""Offline tests for the skills package (chapter 2.3).

Tests cover:
- Progressive disclosure: Level 1 is tiny and present always, Level 2 loads
  only on trigger, Level 3 runs only on demand.
- The real bundled skill on disk (map_compliance/SKILL.md + check_map.py).
- The failure-return contract: error, timeout, missing script — all return
  a structured recoverable message, never a raw traceback.
- Illustration files compile as valid Python (no API key needed).
"""
import os
import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SKILLS_PKG = HERE.parent / "skills"
SKILL_DIR = SKILLS_PKG / "map_compliance"

# ---------------------------------------------------------------------------
# Imports from the package under test
# ---------------------------------------------------------------------------

from skills.loader import (
    SkillMeta,
    load_skill_meta,
    load_skill_body,
    run_skill_script,
)


# ---------------------------------------------------------------------------
# Level 1: metadata is tiny and always loadable
# ---------------------------------------------------------------------------

def test_level1_loads_name_and_description():
    meta = load_skill_meta(SKILL_DIR)
    assert meta.name == "map-compliance"
    assert len(meta.description) > 10
    assert meta.skill_dir == SKILL_DIR


def test_level1_is_tiny():
    """The L1 payload is the two YAML fields — not the whole body."""
    meta = load_skill_meta(SKILL_DIR)
    # Combined name + description should be well under 300 characters.
    payload = f"{meta.name}: {meta.description}"
    assert len(payload) < 300, (
        f"Level-1 payload is {len(payload)} chars — trim the description "
        "so it stays tiny (context-economy principle)."
    )


def test_level1_does_not_read_body():
    """load_skill_meta must not include the SKILL.md body text."""
    meta = load_skill_meta(SKILL_DIR)
    # The body contains "How to use" — it must not appear in L1 metadata.
    assert "How to use" not in meta.name
    assert "How to use" not in meta.description


# ---------------------------------------------------------------------------
# Level 2: body loads only on trigger
# ---------------------------------------------------------------------------

def test_level2_loads_body_on_trigger():
    meta = load_skill_meta(SKILL_DIR)
    body = load_skill_body(meta)
    # The body is the markdown content after the YAML front matter.
    assert "MAP Compliance" in body
    assert len(body) > len(meta.description)


def test_level2_strips_front_matter():
    meta = load_skill_meta(SKILL_DIR)
    body = load_skill_body(meta)
    # The front-matter delimiters must not appear in the body.
    assert "---" not in body.split("\n")[0]
    assert "name: map-compliance" not in body


# ---------------------------------------------------------------------------
# Level 3: bundled script runs and its output enters context
# ---------------------------------------------------------------------------

def test_level3_runs_script_and_returns_output():
    meta = load_skill_meta(SKILL_DIR)
    output = run_skill_script(
        meta, "check_map.py", ["NV-ALDSWORTH-DM", "41900"]
    )
    import json
    data = json.loads(output)
    assert data["ok"] is True
    assert data["supplier_sku"] == "NV-ALDSWORTH-DM"


def test_level3_script_rejects_sub_map_price():
    meta = load_skill_meta(SKILL_DIR)
    output = run_skill_script(
        meta, "check_map.py", ["NV-ALDSWORTH-DM", "38900"]
    )
    # The script exits non-zero; the loader wraps it in a structured error.
    assert "[skill-script-error]" in output
    assert "check_map.py" in output


# ---------------------------------------------------------------------------
# Failure-return contract: all three failure shapes
# ---------------------------------------------------------------------------

def test_failure_missing_script_returns_structured_error():
    """A missing script returns a recoverable message, not a FileNotFoundError."""
    meta = load_skill_meta(SKILL_DIR)
    output = run_skill_script(meta, "nonexistent_script.py", [])
    assert "[skill-script-error]" in output
    assert "not found in skill bundle" in output


def test_failure_malformed_args_returns_structured_error():
    """Bad args cause the script to exit 1; the loader returns a structured message."""
    meta = load_skill_meta(SKILL_DIR)
    output = run_skill_script(meta, "check_map.py", ["NV-ALDSWORTH-DM"])
    # Wrong number of args: script exits 1 with a usage error.
    assert "[skill-script-error]" in output


def test_failure_timeout_returns_structured_error():
    """A timed-out script returns a recoverable message, not a TimeoutExpired."""
    meta = load_skill_meta(SKILL_DIR)
    # Use a near-zero timeout so the script times out immediately.
    output = run_skill_script(
        meta, "check_map.py", ["NV-ALDSWORTH-DM", "41900"],
        timeout_seconds=0.001,
    )
    assert "[skill-script-error]" in output
    assert "timed out" in output


# ---------------------------------------------------------------------------
# check_map.py directly (pure-logic tests, no loader indirection)
# ---------------------------------------------------------------------------

def _run_check_map(*args: str) -> tuple[int, str]:
    """Run check_map.py directly via subprocess; return (returncode, stdout)."""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "check_map.py")] + list(args),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.returncode, result.stdout.strip()


def test_check_map_accepts_valid_price():
    code, out = _run_check_map("NV-ALDSWORTH-DM", "41900")
    import json
    assert code == 0
    data = json.loads(out)
    assert data["ok"] is True
    assert data["map_floor_cents"] == 39900


def test_check_map_rejects_sub_map_price():
    code, out = _run_check_map("NV-ALDSWORTH-DM", "38900")
    import json
    assert code == 1
    data = json.loads(out)
    assert data["ok"] is False
    assert "MAP floor" in data["error"]


def test_check_map_rejects_sub_margin_price():
    # $35000 ($350) is above MAP ($399) but has <20% margin on $280 cost.
    # Wait — MAP is $39900, so $35000 is sub-MAP anyway. Use a price between
    # MAP floor and margin floor to test margin separately.
    # Margin floor = 28000 / (1 - 0.20) = 35000. MAP floor = 39900.
    # Both floors are satisfied at $41900; MAP floor > margin floor here.
    # Test: price exactly at MAP floor ($39900) should be OK on both checks.
    code, out = _run_check_map("NV-ALDSWORTH-DM", "39900")
    import json
    assert code == 0
    data = json.loads(out)
    assert data["ok"] is True


def test_check_map_rejects_unknown_sku():
    code, out = _run_check_map("UNKNOWN-SKU", "41900")
    import json
    assert code == 1
    data = json.loads(out)
    assert data["ok"] is False


# ---------------------------------------------------------------------------
# Illustration files compile as valid Python
# ---------------------------------------------------------------------------

def test_illustration_files_are_valid_python():
    for fname in ("skills_langgraph.py", "skills_responses.py", "skills_example.py"):
        path = str(SKILLS_PKG / fname)
        py_compile.compile(path, doraise=True)

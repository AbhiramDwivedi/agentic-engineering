"""Skill loader: progressive disclosure at three levels.

The model only ever holds what the current task needs:

  Level 1 — metadata (name + description from the SKILL.md YAML front matter).
             Always injected into the system prompt. Tiny: ~100 tokens.
  Level 2 — the SKILL.md body. Loaded only when the skill is triggered.
             The full how-to, rules, and file manifest for the model.
  Level 3 — bundled script output. A referenced script is executed; its
             *stdout* enters context. The source never enters context —
             only the result. Loaded only on demand.

Chapter 2.3 owns this mechanism. 2.1 owns the tool-call contract a skill
may package; 1.5 owns the general context-economy principle.

Security: a Skill is untrusted code + instructions. Scope what scripts can
touch (least-privilege); audit the SKILL.md body before deploying; never
pass untrusted input to subprocess arguments without sanitisation.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

# --8<-- [start:skill-meta]
@dataclass
class SkillMeta:
    """Level-1 payload — always in the system prompt.

    Tiny by design: the model reads name + description for every skill in the
    registry. The full body (Level 2) loads only when the skill is triggered.
    Everything that can be deferred, is deferred.
    """
    name: str          # YAML front-matter `name` field
    description: str   # YAML front-matter `description` field
    skill_dir: Path    # path to the skill bundle on disk
# --8<-- [end:skill-meta]


# --8<-- [start:skill-loader]
def load_skill_meta(skill_dir: Path) -> SkillMeta:
    """Level 1 — parse only the YAML front matter from SKILL.md.

    Returns a SkillMeta without reading the body. Called at startup so that
    every registered skill contributes a tiny name+description token budget
    to the system prompt, regardless of whether it is ever triggered.
    """
    skill_md = skill_dir / "SKILL.md"
    raw = skill_md.read_text(encoding="utf-8")
    fm = _parse_front_matter(raw)
    return SkillMeta(
        name=fm["name"].strip(),
        description=fm["description"].strip(),
        skill_dir=skill_dir,
    )


def load_skill_body(meta: SkillMeta) -> str:
    """Level 2 — load the full SKILL.md body.

    Called only when the skill is triggered (the model chose this skill or
    the runtime matched a keyword). The body contains the detailed how-to
    instructions that fill the model's context for this task.
    """
    skill_md = meta.skill_dir / "SKILL.md"
    raw = skill_md.read_text(encoding="utf-8")
    # Strip the YAML front matter; return the markdown body.
    return _strip_front_matter(raw).strip()


def run_skill_script(
    meta: SkillMeta,
    script_name: str,
    args: list[str],
    timeout_seconds: float = 10.0,
) -> str:
    """Level 3 — run a bundled script and return its stdout as a string.

    The script's *output* enters the model's context, never the source.
    Any error (non-zero exit, timeout, malformed output) returns a
    structured, recoverable message — never a raw stack trace.

    Security: the script runs in an isolated subprocess with the arguments
    you supply. Never pass untrusted input as arguments without sanitising.
    Scope what the script can reach: it should read only what you give it
    and write nothing.
    """
    script_path = meta.skill_dir / script_name
    if not script_path.exists():
        return _script_error(
            script_name,
            f"script {script_name!r} not found in skill bundle",
        )

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + args,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return _script_error(script_name, f"timed out after {timeout_seconds}s")
    except Exception as exc:
        return _script_error(script_name, f"failed to launch: {exc}")

    if result.returncode != 0:
        # The script itself returned a structured error (JSON); pass it through.
        stderr_hint = result.stderr.strip()[:200] if result.stderr else ""
        output = result.stdout.strip() or stderr_hint or "(no output)"
        return _script_error(script_name, f"exit {result.returncode}: {output}")

    output = result.stdout.strip()
    if not output:
        return _script_error(script_name, "script exited 0 but produced no output")

    return output
# --8<-- [end:skill-loader]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_front_matter(text: str) -> dict[str, str]:
    """Extract key: value pairs from a YAML front-matter block (--- ... ---)."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        raise ValueError("SKILL.md has no YAML front-matter block")
    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().lstrip(">").strip()
    return result


def _strip_front_matter(text: str) -> str:
    """Remove the YAML front-matter block and return the body."""
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)


def _script_error(script_name: str, detail: str) -> str:
    """Return a structured, recoverable error message for the model.

    The format is intentionally human-readable: the model should be able to
    understand what went wrong and either retry with different arguments,
    escalate, or tell the user the step failed — not silently proceed on
    missing data.
    """
    return (
        f"[skill-script-error] {script_name}: {detail}. "
        "The script did not produce a usable result. "
        "Check the arguments or escalate to a human reviewer."
    )

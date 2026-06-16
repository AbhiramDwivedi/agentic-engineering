"""Guarantee the code shown in the docs matches the tested source.

The chapters inline their code (rather than using build-time includes) so they
read cleanly on GitHub and everywhere else. This test keeps that inline code
honest: each ``# --8<-- [start:NAME] ... [end:NAME]`` region in the pricing
package must appear verbatim as a fenced ```python block in the chapter. Edit the
source and forget the doc (or vice versa) and CI fails here.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CHAPTER = os.path.join(ROOT, "docs", "the-unit", "tool-use.md")
PRICING = os.path.join(ROOT, "listing-studio", "pricing")

# anchor name -> source file that defines it
ANCHORS = {
    "tool": "tool_use_langgraph.py",
    "flow": "tool_use_langgraph.py",
    "many": "tool_use_langgraph.py",
    "schema_responses": "tools.py",
    "flow_responses": "tool_use_responses.py",
    "many_responses": "multi_tool_responses.py",
    "schema_anthropic": "tools.py",
    "flow_anthropic": "tool_use_example.py",
    "many_anthropic": "multi_tool_example.py",
}


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def _region(src: str, name: str) -> str:
    m = re.search(
        rf"# --8<-- \[start:{name}\]\n(.*?)\n[ \t]*# --8<-- \[end:{name}\]",
        src,
        re.S,
    )
    assert m, f"anchor {name!r} not found in source"
    return m.group(1).strip("\n")


def _python_blocks(md: str) -> list[str]:
    return [b.strip("\n") for b in re.findall(r"```python\n(.*?)```", md, re.S)]


def test_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(CHAPTER))
    for name, fname in ANCHORS.items():
        region = _region(_read(os.path.join(PRICING, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/the-unit/tool-use.md with listing-studio/pricing/{fname}."
        )

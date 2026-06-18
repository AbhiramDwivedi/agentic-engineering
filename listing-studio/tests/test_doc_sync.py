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

# Chapter 2.3 — Skills
SKILLS_CHAPTER = os.path.join(ROOT, "docs", "the-unit", "skills.md")
SKILLS_PKG = os.path.join(ROOT, "listing-studio", "skills")

SKILLS_ANCHORS = {
    "skill-meta":       "loader.py",
    "skill-loader":     "loader.py",
    "skill-langgraph":  "skills_langgraph.py",
    "skill-responses":  "skills_responses.py",
    "skill-anthropic":  "skills_example.py",
}

# Chapter 2.4 — MCP
MCP_CHAPTER = os.path.join(ROOT, "docs", "the-unit", "mcp.md")
MCP_PKG = os.path.join(ROOT, "listing-studio", "helpdesk_mcp")

MCP_ANCHORS = {
    "mcp-guard":       "guard.py",
    "mcp-poison":      "guard.py",
    "mcp-stale":       "guard.py",
    "mcp-consent":     "client.py",
    "mcp-connect":     "client.py",
    "mcp-langgraph":   "helpdesk_mcp_langgraph.py",
    "mcp-responses":   "helpdesk_mcp_responses.py",
    "mcp-anthropic":   "helpdesk_mcp_example.py",
}

# Chapter 2.2 — Structured Output
STRUCTURED_OUTPUT_CHAPTER = os.path.join(ROOT, "docs", "the-unit", "structured-output.md")
STRUCTURED_OUTPUT_PKG = os.path.join(ROOT, "listing-studio", "structured_output")

STRUCTURED_OUTPUT_ANCHORS = {
    "pricing-schema":          "schema.py",
    "pricing-call":            "structured_output_langgraph.py",
    "pricing-call-openai":     "structured_output_responses.py",
    "pricing-call-anthropic":  "structured_output_example.py",
    "pricing-validate":        "validate.py",
    "pricing-reask":           "validate.py",
}

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

# Chapter 1.4 — The Augmented LLM
AUGMENTED_LLM_CHAPTER = os.path.join(ROOT, "docs", "foundations", "the-augmented-llm.md")
AUGMENTED_LLM_PKG = os.path.join(ROOT, "listing-studio", "augmented_llm")

AUGMENTED_LLM_ANCHORS = {
    "state":           "state.py",
    "unit":            "augmented_llm_langgraph.py",
    "node":            "augmented_llm_langgraph.py",
    "unit_responses":  "augmented_llm_responses.py",
    "node_responses":  "augmented_llm_responses.py",
    "unit_anthropic":  "augmented_llm_example.py",
    "node_anthropic":  "augmented_llm_example.py",
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
    import textwrap
    blocks = []
    for b in re.findall(r"[ \t]*```python\n(.*?)[ \t]*```", md, re.S):
        blocks.append(textwrap.dedent(b).strip("\n"))
    return blocks


def test_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(CHAPTER))
    for name, fname in ANCHORS.items():
        region = _region(_read(os.path.join(PRICING, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/the-unit/tool-use.md with listing-studio/pricing/{fname}."
        )


def test_augmented_llm_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(AUGMENTED_LLM_CHAPTER))
    for name, fname in AUGMENTED_LLM_ANCHORS.items():
        region = _region(_read(os.path.join(AUGMENTED_LLM_PKG, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/foundations/the-augmented-llm.md with "
            f"listing-studio/augmented_llm/{fname}."
        )


def test_structured_output_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(STRUCTURED_OUTPUT_CHAPTER))
    for name, fname in STRUCTURED_OUTPUT_ANCHORS.items():
        region = _region(_read(os.path.join(STRUCTURED_OUTPUT_PKG, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/the-unit/structured-output.md with "
            f"listing-studio/structured_output/{fname}."
        )


def test_skills_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(SKILLS_CHAPTER))
    for name, fname in SKILLS_ANCHORS.items():
        region = _region(_read(os.path.join(SKILLS_PKG, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/the-unit/skills.md with listing-studio/skills/{fname}."
        )


def test_mcp_chapter_code_matches_tested_source():
    blocks = _python_blocks(_read(MCP_CHAPTER))
    for name, fname in MCP_ANCHORS.items():
        region = _region(_read(os.path.join(MCP_PKG, fname)), name)
        assert region in blocks, (
            f"chapter code for {name!r} (from {fname}) does not match the source.\n"
            f"Re-sync docs/the-unit/mcp.md with listing-studio/helpdesk_mcp/{fname}."
        )

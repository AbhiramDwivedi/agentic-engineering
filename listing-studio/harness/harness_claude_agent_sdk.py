"""The same deny rule as a Claude Agent SDK PreToolUse hook.

Illustration, not run in CI: needs claude-agent-sdk and a key. Compile-checked
only. Names (ClaudeAgentOptions, HookMatcher, the hookSpecificOutput shape with
permissionDecision / permissionDecisionReason) checked against
code.claude.com/docs/en/agent-sdk/hooks on 2026-11-28; disallowed_tools
against code.claude.com/docs/en/agent-sdk/agent-loop ("blocks listed tools,
regardless of other settings"). Per Claude Code's
permission docs a matching deny rule beats a hook's allow; verify before relying
on it for your version.
"""
from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher


# --8<-- [start:harness-anthropic]
async def no_live_writes(input_data, tool_use_id, context):
    args = input_data["tool_input"]
    if args.get("target", "draft") != "draft":
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": "Draft only: this session may not write live.",
        }}
    return {}                      # no opinion: normal permissions still apply


options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="mcp__studio__write_draft",
                                      hooks=[no_live_writes])]},
    disallowed_tools=["mcp__studio__publish"],
)
# --8<-- [end:harness-anthropic]

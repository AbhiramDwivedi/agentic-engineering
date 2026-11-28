# Coverage map: The Agent Loop (chapter 2.5)

> Research-derived spec for what the chapter must cover and where to stop. Angles run: vendor
> docs (Anthropic, OpenAI, LangGraph, Google ADK), academic (ReAct), practitioner (SDK issue
> trackers), daily-tool (Claude Code, Agent SDK), alias sweep, incidents. Skeptical-read angle:
> skipped (no named defender of the contested claims was found; see Contested). Skipped: OWASP
> (injection belongs to 2.1/4.6), benchmarks. Bar: definitive but tight; spec, not essay.

## The mental model

The loop is one cycle: the model reads everything so far, asks for a tool or stops; your code runs
the tool and appends the result. 2.1 section 3 already ships the cycle, its diagram and a capped
loop; link there, do not re-teach it. What 2.5 adds is one question: **why did the loop end?** A
turn with no tool call is not the same as an answer.

**Thesis (proposed):** In the agent loop the model's "I'm done" is a claim, not a fact. The loop
ends when the model stops asking for tools, so the engineering lives in what the model sees between
calls and in the ceiling that ends the run when its judgment is wrong.

## Seams

- **2.1 Tool Use:** one call's contract, the basic loop, statelessness, id pairing, actionable
  errors. Each item below carries a "beyond 2.1" clause; the carrier example must not repeat
  2.1's `check_price` walkthrough.
- **2.6 The Harness:** ceilings, permissions, hooks as engineering. **3.7 The Outer Loop:** a
  code- or user-owned stop condition and a verifier around this loop; `/goal`, `/loop`. **9.1:**
  running a loop unattended. **3.4:** a self-judging loop (do not confuse). Say which loop
  whenever "autonomous" appears.

## Carrier

Listing Studio, a multi-turn **price step** 2.1 did not show: several tools (market lookup,
`check_price`, `submit_for_review`), one real `is_error` result (a timed-out lookup), and the
model repeating the same failing call. Cents as integers (`price_cents`). The Repricer (the
bible's one autonomous loop) only if the pipeline cannot show a point.

## Must-cover (ranked)

1. **Why the loop ended: five exits.** `tool_use` means continue. Otherwise read the stop reason:
   (a) clean end (`end_turn`, or OpenAI's final output "of the desired type"); (b) abnormal stop
   (`max_tokens`, `model_context_window_exceeded`, `pause_turn` needing a resend, `refusal`,
   `stop_sequence`), none of which is an answer; (c) stall; (d) false "done"; (e) code ceiling.
   Beyond 2.1: its loop exits on "no more calls" and would ship a truncated reply as success.
   **Standard** for the branching. (Anthropic, *Handling stop reasons*; OpenAI *Running agents*,
   `error_handlers` keys `max_turns`, `model_refusal`, `invalid_final_output`.)
2. **Who decides (litmus).** Model picks the step and declares done; code executes, appends,
   bounds. Anthropic: agents are "typically just LLMs using tools based on environmental feedback
   in a loop". One tight section. **Standard.** (*Building effective agents*; *How Claude Code
   works*.)
3. **Ground truth each step.** Lead with *Building effective agents*: agents must "gain 'ground
   truth' from the environment at each step". ReAct (Yao et al., ICLR 2023) supports a trade-off,
   not a clean win: in Table 1 ReAct trails CoT on HotpotQA and beats it on Fever, the best
   results combine the two, and its error analysis shows less hallucination but more reasoning
   errors. State in words; freeze no numbers. **Established.**
4. **Stall: the repeat.** ReAct documents the model "repetitively generat[ing] the previous
   thoughts and actions". This is the cited source for the stall guard: a code-side repeat
   detector (same call, same arguments) plus the turn cap. Beyond 2.1: it caps steps, not
   repeats. **Established.**
5. **False "done" (one line, link 3.7).** The inner loop cannot check its own claim of
   completion; the verifier is 3.7. Name it, argue it in the thesis, defer depth.
6. **Imposed stops, and reporting which.** Turn cap, spend cap, no-progress guard; the result must
   say why it ended (`success`, `error_max_turns`, `error_max_budget_usd`, `error_during_execution`,
   `error_max_structured_output_retries`; `MaxTurnsExceeded`; `GraphRecursionError`). A cap hit
   with no final answer is not done. Defaults differ: Agent SDK "No limit"; OpenAI ships a
   default; LangGraph's recursion default is now about 10,000 super-steps, so set your own.
   **Standard.**
7. **Failure and retry, beyond 2.1.** `is_error: true` mechanics, who owns the retry (model
   chooses, code caps; 7.1 owns code-owned retry), permission denials returned as results. 2.1
   already says "actionable error, not a stack trace". **Standard.** (Agent SDK loop docs;
   *Writing tools for agents*.)
8. **Context growth, whoever stores it.** The model reads the whole accumulated context every
   turn; a client that re-sends it, or an OpenAI `previous_response_id` / `conversation_id` store
   that does not, still pays the tokens and the attention cost. Compaction can drop early
   instructions (5.4). Beyond 2.1's one-line statelessness. **Standard.**
9. **Parallel calls, beyond 2.1's one sentence.** One `tool_result` per block, results first,
   none omitted even on failure (the 400 error text). Read-only concurrent, mutating sequential
   is Agent SDK behaviour: attribute it. **Established.**
10. **Gotcha: forced `tool_choice` builds a loop that never exits.** `tool_choice` is per-request
    and "persists" only because the caller resends it. OpenAI's docs now state the framework
    resets it to `auto` after a tool call (`reset_tool_choice`). History: issue #191, PR #263.
    A gotcha, no tier.

Dropped: hooks as a ranked item (one sentence, 2.6/4.3; one vendor doc); the loop-variant taxonomy
(pointer to 3.7/9.1).

## Mention-and-link

2.1 (contract, basic loop); 2.2; 2.3; 2.4; 2.6 harness, hooks; 5.4 compaction; 3.7 outer loop,
`/goal`, `/loop`, false done; 3.4 self-judging; 4.3 approval; 4.5 thinking; 4.6 injection chains
actions through the loop; 7.1 retry; 8.1 tracing; 8.4 spend caps; 9.1 unattended loops; 1.3
workflow vs agent (agency is a spectrum, not a switch); 1.6 graph runtimes.

## Out of scope

Plan-and-execute, reflection, orchestrator-workers (Part III); multi-agent topology (Part IX);
provider option tables; hosted loops (8.7); self-improving loops (9.7).

## Contested and not-this

- An inner loop with no ceiling is an anti-pattern, not Contested.
- Non-synonym: Google ADK `LoopAgent` is "not controlled by an AI model, and is deterministic"
  (code decides; `max_iterations` defaults to `None`). Put it in the aliases box.
- "Reasoning models collapse the loop": no named claimant found; omit unless the author supplies one.

## Maturity

**Proposed verdict: Standard** for the shape and stop-reason branching; Established for ground
truth and stall. The tuning of when to stop is less settled (one argued sentence). Fast-moving:
option names, defaults, subtypes, and Claude Code's 25,000-token tool-response default (verify
before quoting). **Last reviewed: 2026-11.**

## Aliases

*the agent loop*, *the agentic loop*, *the ReAct loop* (Yao et al.), *the tool-use loop*, *turn*
(Agent SDK; OpenAI), *super-step* (LangGraph), *iteration limit / max turns / recursion limit*.
The SDK "tool runner" is a helper, not a synonym. Non-synonyms: ADK `LoopAgent`; `/loop`, `/goal`
(3.7). Perceive/Plan/Act/Observe: omit until a primary source is confirmed. Gulli: single-loop
material has a home here; outer loop, handoffs, graphs are 3.7, 9.2, 1.6.

## Reader-verifiable anchors

1. Agent SDK: set `max_turns` equal to the tool rounds; observe `error_max_turns` and no `result`.
2. OpenAI Agents SDK: tool plus `max_turns=2`; observe `MaxTurnsExceeded`, add the handler.
3. Messages API: set `max_tokens` very low on a tool task; observe `max_tokens` and no tool call.

## Incidents

No vendor postmortem of a runaway inner loop found. Issue #191 (closed not-planned, 2025-10) and
PR #263 (merged 2025-03-25) give the forced-`tool_choice` mechanism. Do not cite blog cost figures.

## Named ideas (author accepts or strikes)

**"Natural stop vs imposed stop"** is defensible. Struck by review: "the loop decides, the ceiling
stops" (the model decides, not the loop) and "everything is the tool result" (non-tool stops exist).

## Sources (every URL opened and read)

- Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, arXiv:2210.03629
  (v1 2022-10-06; v3 2023-03-10; ICLR 2023). https://arxiv.org/abs/2210.03629
- Anthropic, *Building effective agents*, 2024-12-19.
  https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, *Handling stop reasons*. https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
- Google ADK, *LoopAgent* (non-synonym; opened by the second reviewer).
- Anthropic, *Handle tool calls* (Claude API docs).
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
- Anthropic, *How the agent loop works* (Agent SDK docs).
  https://code.claude.com/docs/en/agent-sdk/agent-loop
- Anthropic, *How Claude Code works*. https://code.claude.com/docs/en/how-claude-code-works
- Anthropic, *Writing effective tools for agents*, 2025-09-11.
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, *Getting started with loops*, 2026-06-30 (de Oliveira, Segner).
  https://claude.com/blog/getting-started-with-loops
- OpenAI Agents SDK, *Running agents*. https://openai.github.io/openai-agents-python/running_agents/
- OpenAI Agents SDK issue #191 and PR #263 (merged 2025-03-25).
  https://github.com/openai/openai-agents-python/issues/191 ;
  https://github.com/openai/openai-agents-python/pull/263
- LangGraph, *Graph API* (recursion limit). https://docs.langchain.com/oss/python/langgraph/graph-api

**Verify before quoting:** SDK option names, result subtypes, turn-counting rule, default recursion
limit, budget-overshoot behavior, and Claude Code's 25,000-token tool-response cap are all
version-dependent; re-open the live page at draft time.

## Orchestrator rulings (Stage 1.6, 2026-11-28)

Settled so the chapter could be written; reversible at PR review.

1. **Thesis, tightened from the researcher's:** *"An agent is a loop in which the model decides
   the next step and when to stop, so its "done" is a claim your code still has to check. The
   engineering is in what the model sees between calls, in knowing which exit ended the run, and in
   a ceiling the model cannot talk its way past."* The researcher's version said the loop ends
   "when the model stops asking for tools", which reintroduces the BLOCKER (abnormal stops also
   arrive with no tool call); the five-exit framing replaces it.
2. **Budget row: standard pattern (~2,000-2,800 prose words).** Ten must-cover items only fit
   because items 2, 5, 7 and 9 are one clause plus a link (to 1.2, 3.7 and 2.1).
3. **Maturity: "Standard (the loop shape and branching on stop reason) · Established (ground
   truth each step; stall detection)", Last reviewed 2026-11.** The tuning of when to stop gets the
   one argued sentence, no tier.
4. **Carrier: the Listing Studio multi-turn price step in the Carrier section.** No Repricer.
5. **The second review was a Claude Opus pass, not an independent engine** (codex at its usage
   limit). Disclosed in the PR; the author may re-run the codex review.

## Author-only questions

1. Accept a named idea (above) or none? *Default: none; plain titles only.*
2. Any first-hand "From production:" loop story (a real runaway, a cap that saved a run)? *Default:
   none; omit the callout rather than invent one.*
3. Which provider tab leads the code? *Default: LangGraph, with Anthropic Messages and OpenAI
   Responses as tabs, per the repo convention.*
4. (Moot after review: the loop-variant taxonomy is handed to 3.7/9.1 as a pointer.) Adopt the
   proposed thesis ("the model's 'I'm done' is a claim, not a fact")? *Default: yes.*
5. Include the Perceive/Plan/Act/Observe alias? *Default: omit until a primary source is confirmed.*

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

Checked against: Anthropic *Handling stop reasons* (live), ReAct via ar5iv (live), shipped 2.1
(`docs/the-unit/tool-use.md`), carrier bible. Review notes folded in below.

- **B1** accepted. Stop-reasons page lists seven values; only `end_turn` is a natural finish;
  `max_tokens`, `pause_turn`, `refusal`, context-exceeded arrive with no tool call. Item 1 rebuilt.
- **M1** accepted. 2.1 ships the loop, `MAX_STEPS`, "stateless, resend", id matching, actionable
  errors (verified). Items 1, 7, 8, 9 now carry "beyond 2.1" clauses.
- **M2** accepted. Item 10 dropped to a pointer (3.7/9.1); Author question 4 closed.
- **M3** accepted. Table 1 verified: ReAct 27.4 vs CoT 29.4 on HotpotQA, 60.9 vs 56.3 on Fever;
  best are combos. Lead cite moved to *Building effective agents*; no numbers frozen.
- **M4** accepted. Repetition quote verified in ReAct; item 4 (stall) and item 5 (false done) added.
- **M5** accepted in substance. Item 8 reworded to "whoever stores it"; the 25,000 cap moved to
  verify-before-quoting. OpenAI `conversation_id` claim taken from the reviewer, not re-fetched.
- **M6** accepted. Strawman Contested claims cut or marked no-claimant; skeptical angle declared
  skipped; ADK added. ADK quote taken from the reviewer, not re-fetched.
- **M7** accepted. 2.1's floor walkthrough and `price_cents` verified; Carrier section added (a
  multi-turn price step with a real `is_error` and a repeat).
- **M8** accepted. Thesis replaced; Author question 4 now asks for sign-off. 1.3 conflict noted.
- **m1** accepted. Item 9 attributed; hooks dropped; item 10 a gotcha with no tier; the
  no-ceiling line is an anti-pattern.
- **m2** accepted, not re-fetched (`reset_tool_choice`); item 10 reworded. **m3** accepted
  (subtypes and default contrast in item 6; subtypes not re-fetched). **m4** accepted, not
  re-fetched; 3.7 map's "1,000" is for its owner to fix.
- **m5** accepted (ADK, `/loop`, `/goal`, tool-runner note). **m6** accepted (two ideas struck).
- **m7** accepted (3.4, 4.6, 7.1, 8.4, 9.1 added). **m8** accepted; body trimmed, ICLR 2023 added.

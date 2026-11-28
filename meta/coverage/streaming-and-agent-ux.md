# Coverage map: Streaming & Agent UX (chapter 6.3)

> Research-derived spec for what the chapter must cover so a reader can put an agent in front of a
> person without lying to them or losing control. Angles run: vendor docs, protocol specs, daily
> tools, everyday engineer, skeptical read, alias sweep, security. The one academic source is cited
> in item 3. Bar: definitive but tight.

## Thesis, litmus and budget

**Thesis.** An agent UI is a two-way control surface, not a typewriter: every token streamed early
trades away moderation and schema safety, and everything the UI displays (a tool call, a plan, a
progress line) must come from what the harness did, not from what the model says it did.

**Litmus.** Your code decides: event translation, progress rendering, approval enforcement and
output sanitising. SSE is a transport, not a pattern. The model decides only which registered
component to request in catalogue-bound generative UI (an application of 2.1/2.2), never code.

**Budget.** Standard pattern row, about 2,000 to 2,800 words.

## Must-cover

Ranked. `[+]` = the chapter is a stub, so everything is new.

1. **The event stream, not the token stream** `[+]` - SSE as the transport. Anthropic: `message_start`,
   per block `content_block_start` / `content_block_delta` / `content_block_stop`, then
   `message_delta`, `message_stop`, plus `ping` and in-stream `error`; `usage` in `message_delta` is
   cumulative. OpenAI Responses: semantic events (`response.created`, `response.output_text.delta`,
   `response.function_call_arguments.delta`, `response.completed`, `error`); verify
   `response.failed` / `response.incomplete` against the REST reference. Gemini streams over SSE
   too (verify). Errors mid-stream arrive as events after a 200, not as an HTTP error. Bedrock
   `bedrock-runtime` "does not stream plain server-sent events". Handle unknown event types.
   *Skip it:* a UI handling only text deltas breaks on the first tool call. **Standard.**
2. **Translate once, at your edge** `[+]` - one internal vocabulary (run started, text delta, tool
   started, tool finished, approval needed, run finished or failed) mapped from provider events and
   framework modes (LangGraph `messages`, `updates`, `custom`, `values`; inner agents stay silent
   without `subgraphs=True`). *Skip it:* every provider change is a UI change. **Established**; the
   vocabulary itself is not standardised.
3. **Show tool calls, progress and reasoning honestly** `[+]` - render the call when arguments are
   complete, show a result or error state, never a spinner that outlives the work; separate "model
   is writing" from "your code is running a tool". Tool-argument deltas are partial JSON, buffered
   by Anthropic by default (`eager_input_streaming` removes it). Reasoning streams (Anthropic
   thinking deltas, OpenAI reasoning summaries, Gemini thought summaries; verify each): collapse
   or summarise by default, never present as a faithful audit log (Chen et al., "Reasoning Models
   Don't Always Say What They Think", arXiv:2505.05410, 8 May 2025), never render opaque or
   redacted thinking. 7.2 emits events; this chapter renders them. *Skip it:* a plan the harness is
   not following, a green tick on a failed tool. **Established** (tool display); **Contested**
   (reasoning as explanation).
4. **Interruption and steering mid-run** `[+]` - stop (close the connection; `POST
   /v1/responses/{id}/cancel` for background runs; Agent SDK `interrupt()`, which keeps the session
   open); queue a message (reaches the model after the running tool calls finish); reconnect
   (OpenAI `starting_after` the last `sequence_number`). Two failure modes to verify before
   drafting: closing the browser connection must abort the upstream provider request or tokens keep
   burning, and an interrupted tool call must leave history valid (a cancelled `tool_result`, or
   roll back the turn). Anthropic recovery: 4.5 and earlier continue with an assistant message; 4.6
   and later use a user message asking the model to continue; tool-use and thinking blocks "cannot
   be partially recovered". Durable background runs -> 7.3, 8.7. *Skip it:* the stop button leaves
   a half-written action. **Established** (stop); **Emerging** (queued steering).
5. **The approval UI, as a rendering of 4.3** `[+]` - the pause is an event; show exact action,
   arguments and consequence, bound to the tool-call ID; handle expired and already-resolved
   states. AI SDK: part state `approval-requested`, `addToolApprovalResponse`. Server-side
   verification is 4.3's job. *Skip it:* a modal the client can forge, or a prompt that approves
   whatever runs next. **Established** (pattern); **Emerging** (protocol states). The gate in 4.3 is
   Standard.
6. **Partial and streamed structured output** `[+]` - the AI SDK says partial outputs "cannot be
   validated against your provided schema"; with `streamText` and `Output.array()`, `elementStream`
   yields elements once complete and validated. Never act on a partial object or parse tool JSON
   before `content_block_stop`. 2.2 excludes streaming; this chapter owns it. *Skip it:* a
   half-parsed price reaches a write. **Established** (rule); **Emerging** (library APIs).
7. **Streaming, moderation and rendered-output safety** `[+]` - OpenAI warns streaming "makes it more
   difficult to moderate the content of the completions"; shown text cannot be unsent. Decide per
   surface: stream, buffer, or stream with a retract path. The rendering boundary is OWASP LLM05:2025
   Improper Output Handling (browsers interpreting model-generated Markdown or JavaScript): strip raw
   HTML, allowlist image and link fetches in streamed Markdown, set a CSP, never execute
   model-authored UI code. Injection itself -> 4.6; validation -> 4.4. *Skip it:* the user reads
   what the guardrail would have blocked. **Established.**
8. **Generative UI: three layers, not three rivals** `[+]` - AG-UI: event transport between backend
   and frontend (lifecycle `RunStarted` / `RunFinished` / `RunError`, text, tool call, state,
   reasoning; `THINKING_*` deprecated for `REASONING_*`). A2UI: declarative JSON from a registered
   catalogue, "never executable code". MCP Apps: a tool names a `ui://` resource rendered in a
   sandboxed iframe, JSON-RPC over `postMessage`. One boundary: never render model-authored HTML.
   Ecosystem comparison and payments -> 9.3. *Skip it:* a protocol picked for the wrong layer.
   **Emerging.**

Gotchas seed list (one line each in prose, not a must-cover): proxy or CDN buffering defeats SSE;
blocking calls inside an async streaming handler; LangGraph `get_stream_writer` on async Python
below 3.11.

## Mention-and-link

- Emitting events -> 7.2 Observer. Approval semantics, resume -> 4.3. Voice, barge-in -> 6.4.
- Constrained decoding -> 2.2. Validation and retract -> 4.4. Injection -> 4.6.
- Durable runs -> 7.3; serving shape -> 8.7; protocol landscape and payments -> 9.3.
- UI state snapshots are not model context; keep them out. Bounding tool-result history in long
  sessions -> 5.4 Compaction.

## Out of scope

Frontend framework tutorials; visual design; building MCP servers (2.4); speech streaming (6.4).

## Maturity summary

- **Standard:** SSE streaming of text and events.
- **Established:** tool-call display; edge event translation; stop and cancel; partial objects as
  display-only; the streaming-vs-moderation trade-off; approval UI pattern.
- **Emerging:** queued steering; resume semantics; AG-UI, A2UI, MCP Apps; library partial APIs.
- **Contested:** unconstrained, model-authored generative UI (A2UI's own pitch is the opposite);
  streamed reasoning as an explanation.
- **Projected chapter verdict:** **Established (streaming and event rendering) / Emerging
  (generative UI protocols).**

## Aliases (for `*Also called:*`)

streaming, token streaming, Server-Sent Events, SSE; time to first token; agent UI, agentic UX;
AG-UI; generative UI, A2UI (Google, verify), declarative UI payload; MCP Apps; UI message stream and
data parts (Vercel AI SDK); thinking indicator, reasoning summary, progress card, tool-call card.

## Reader-verifiable anchors

- Collapsible tool-call cards with running, completed and error states in a coding agent or chat
  product the reader already uses.
- A streamed Anthropic tool call: `input_json_delta` `partial_json` is not parseable until
  `content_block_stop`. (Anthropic Streaming messages.)
- Agent SDK `interrupt()` ends the response and leaves the session open. Cite Claude Code's
  interactive-mode docs for any key binding; do not assert equivalence.

## Incidents

None verified from a primary source. Candidates to open before drafting: EchoLeak (CVE-2025-32711,
Microsoft 365 Copilot) and Markdown-image exfiltration disclosures; neither was confirmed here.

## Named-idea candidate (author accepts or strikes)

- **The UI is a claim** (what you show must match what the harness did).

## Carrier

Listing Studio dashboard: a merchandiser watching a listing run, tool-call rows, a stop button.
Repricing agent: a pricing approval card (price figures must match 4.3 and the Aldsworth desk
artifact before drafting). Shopper assistant: token streaming, a moderation trade-off, a product
card from a catalogue. Production claims: none; any "From production:" callout is the author's.

## Sources (opened 2026-11-28 unless marked)

Anthropic, "Streaming messages," platform.claude.com/docs/en/build-with-claude/streaming. Anthropic
Agent SDK, code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode. OpenAI, "Streaming API
responses" and "Background mode," developers.openai.com/api/docs/guides. LangGraph "Streaming,"
docs.langchain.com/oss/python/langgraph/streaming. Vercel AI SDK, ai-sdk.dev/docs: chatbot tool
usage, streaming data, generating structured data. AG-UI, docs.ag-ui.com/concepts/events. A2UI,
a2ui.org. MCP Apps, modelcontextprotocol.io/extensions/apps/overview. OWASP, LLM05:2025 Improper
Output Handling, genai.owasp.org/llmrisk/llm052025-improper-output-handling/. Chen et al.,
arXiv:2505.05410. Not yet opened: Gemini streaming and thought-summary docs, Google ADK.

## Open questions for the author

1. Depth of generative UI protocols in 6.3 versus 9.3 (map keeps three layers only).
2. Does `listing-studio/` get a runnable event-translator and approval demo, or research only?
3. Reasoning-stream UX inside item 3, or its own item?
4. Sign-off on the thesis and the budget row.

## Map review (Stage 1.5)

Second engine: independent. Verified against pages opened 2026-11-28.

1. Missing thesis and budget: accepted, added thesis and budget.
2. Missing litmus call: accepted, added.
3. OWASP LLM05 and incidents: accepted-modified, OWASP verified and folded into item 7; EchoLeak CVE could not be confirmed from NVD or MSRC, so it is only an unverified candidate.
4. Reasoning-stream UX: accepted-modified, Chen et al. verified; Amershi CHI 2019 not opened so not cited; "no founding paper" header removed.
5. Cancellation propagation and orphaned tool_use: accepted-modified, added to item 4 flagged verify (provider rules not opened).
6. Gemini and ADK omitted: accepted-modified, noted as parity, listed as not yet opened; Google attribution of A2UI marked verify.
7. Item 8 bloat: accepted, cut to three layers, payments and Apps SDK detail to 9.3.
8. Seam overlaps and Item 9: accepted, 7.3/8.7 and 4.3 deferred, item 9 dissolved into item 1 and a gotchas list.
9. Maturity contradictions: accepted, reconciled; Contested populated.
10. Unverified quotes: accepted-modified, the AG-UI "without exposing raw chain-of-thought" quote verified verbatim (not a paraphrase); `response.failed` / `response.incomplete` flagged to verify; fetch-tool sentence deleted.
11a. AG-UI SCREAMING_SNAKE_CASE: rejected for prose, which uses the type names (`RunStarted`); the events page does show constant families such as `THINKING_*` and `REASONING_*` (corrected at Stage 5); also the page says THINKING_* "will be removed" in 1.0.0, so "removed" was corrected to "deprecated".
11b. Anthropic 4.6 user-message recovery: accepted, verified on the streaming page.
11c. `streamObject` deprecation: accepted-modified, page documents `streamText` with `Output.array()` and `elementStream` but never mentions `streamObject`, so no deprecation claim made.
11d. MCP-UI client and server SDKs: rejected, unverified; the MCP-UI alias dropped.
12. Anchors: accepted-modified, daily-tool anchor added, Escape claim removed.
13. Carrier conflation: accepted, "dashboard" used; 4.3 price figures dropped pending check.
14. Open questions: accepted, added.
15. `message_delta` precision: accepted-modified, "cumulative" verified; no further citation needed.
16. Inverted context note: accepted, merged.
17. Aliases and named ideas: accepted, synonyms added, two weak named ideas struck.
18. Process leakage: accepted, sentence deleted.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Thesis and verdicts.** Thesis as folded. Verdict: Established, with generative UI protocols Emerging. The two Contested items each get one sentence.
2. **Generative UI depth.** One section in 6.3 covering what the protocols are (AG-UI, MCP-UI/A2UI where verified) and the trust boundary. 9.3 owns the future depth; refer to it in plain text.
3. **Code.** Yes, a small one: a new `listing-studio/streaming/` package. It contains:
   - an event translator that maps scripted provider stream events to one UI event vocabulary, done once at the boundary;
   - an approval-gate event;
   - a test that the UI's "done" state comes from harness tool results, not model text.

   It is offline, with tests on stdlib, pydantic and anyio only. Provider tabs show the Anthropic and OpenAI stream event names as compile-checked illustrations.
4. **Reasoning-stream UX** stays inside item 3, not as its own item.
5. **Unverified items.** Gemini/ADK, `response.failed`, the cancellation contract and EchoLeak ship only if the fact-checker opens a primary source; otherwise they are cut.
6. **Exclusions.** No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

**Prose critic**

- PC1 (a tool that raises vs the Gotchas; the code broke the thesis): fixed. `reduce` now fails every open step on an error. The provider wrappers turn SDK exceptions into `error`. Tests added.
- PC2 (Standard and Established disagree): fixed. The verdict is split: Standard for event streaming, Established for rendering from harness events, Emerging for the protocols. The footer matches the prose.
- PC3 (the maturity paragraph reads as apparatus): fixed. The trust scale is glossed once, and each verdict carries its reason.
- PC4 (confidence ahead of the citation): fixed. The claim about model-authored UI code is downgraded from Contested to a recommendation. The protocol claim is cited [^11].
- PC5 (carrier continuity): fixed. The carrier is now the Aldsworth desk, `supplier_sku` `NV-ALDSWORTH-DM` at `price_cents` 41900. The change is made in the code, tests, prose and SVG.
- PC6 (provider section too long): fixed. Cut the opener, the `ping` events and the LangGraph mode list. Compressed the argument-buffering detail.
- PC7 (rules said to hold on both, sourced to one vendor): fixed. Added [^5] to both rules.
- PC8 (scope narration): fixed. The neighbours paragraph names each owner without narrating scope.
- PC9 (signposting and vague attribution in Ecosystem): fixed. The section is rewritten with a named source for each protocol.
- PC10 (Wiring heading level and placement): fixed. Promoted to `###` and moved after "What the provider actually sends".
- PC11 (alias padding): fixed. Trimmed to true synonyms. The author confirms in the PR.
- PC12 (narrated-significance opener): fixed. Cut.
- PC13 ("common case" uncited; exfiltration unsourced): softened. The frequency claim is cut. The mechanism is explained without attribution.
- PC14 ("switch models"): fixed. Now "switch providers".
- PC15 (an absolute that restates L11): fixed. Cut.
- PC16 ("says plainly"): fixed. Now "says".
- PC17 ("a handful of kinds"): fixed. Now "a small fixed vocabulary"; the body says seven.

**Fact checker**

- FC1 (maturity contradiction): fixed. See PC2.
- FC2 (recovery is version-gated): fixed. Claude 4.5 and earlier resume mid-stream. Claude 4.6 and later get a continue instruction. Tool use and thinking blocks cannot be partially recovered.
- FC3 (the A2UI catalogue): fixed. Now "the catalogue you, the developer, registered".
- FC4 (the Vercel quote): fixed. The quote names `streamText` and drops "plainly".
- FC5 (coverage gaps):
  - Covered: `response.failed` and `incomplete`; cancel, through `POST /v1/responses/{id}/cancel` and `interrupt()`; reconnect, through `starting_after`.
  - Cut, because no primary source confirmed them: Gemini and Bedrock, AI SDK approval, the disconnect-abort point, `get_stream_writer`, and EchoLeak.
- FC6 (terms used without a gloss): fixed. Glossed SSE, reducer, typewriter UI, CSP, generative UI and the trust scale.
- FC7 (unsourced AG-UI deprecation): fixed. Cited [^11]; the deprecation detail is cut from the prose.

**Cold reader**

- CR terms: fixed. Glossed reducer, SSE, typewriter UI, CSP, generative UI and the trust scale.
- CR missing reasoning steps (why `done` is not the run; why the server must bind approvals): fixed. `done` is defined as closing one model response. The server check is assigned to 4.3.
- CR picture-alone test (the alt text says five kinds): fixed. The alt text and the `<desc>` now say seven kinds: five from the translator and two from the harness.
- CR build test: fixed. Added the `run_turn` consumer listing, with a sentence stating its scope.

**Second-engine review**

- CX1 (response vs run completion): fixed. `done` closes one model response, stated in the prose and the alt text.
- CX2 (cancellation dropped): fixed, briefly. Cited the OpenAI cancel endpoint and the Agent SDK `interrupt()`. A step cut off by a stop states whether its tool ran.
- CX3 (failure paths left broken): fixed in code.
  - `response.failed` and `response.incomplete` map to `error`.
  - SDK exceptions are wrapped.
  - An unknown call does not crash the stream.
  - Tests added.
- CX4 (a closed block assumed to be valid input): fixed in code. The parse is guarded for `eager_input_streaming` [^13]. An invalid parse yields `error`, and the call never runs.
- CX5 (no reconnect): fixed, briefly. Covered the OpenAI `starting_after` reconnect and Anthropic's version-gated recovery.
- CX6 (protocol layers wrong): fixed.
  - AG-UI is an event protocol, independent of transport.
  - A2UI draws its components from a registered catalogue.
  - MCP Apps runs a server's HTML app in a sandbox.
- CX7 (audience treated as a safety exemption): fixed. Each surface is decided by what its text contains and can set off, not by who reads it.
- CX8 (carrier contract): fixed. See PC5.
- CX9 (carrying an ID is not binding): fixed. The prose qualifies the claim and assigns the server check to 4.3. A gotcha about forgeable approvals is added.
- CX10 (incident left unresolved): softened. EchoLeak is not named and no unopened source is cited. The mechanism is described generically.
- CX11 (verdicts exceed the evidence): fixed. See PC2 and PC4.
- CX12 (the thesis is broader than the demo): mostly rejected. The demo exercises the thesis: a step's state comes only from harness events. The structural-decision sentence is narrowed.
- CX13 (related terms listed as aliases): fixed. See PC11.
- CX14 (wrong nomenclature ruling in 11a): fixed in the map. The AG-UI page does list `THINKING_*` and `REASONING_*`.
- CX15 (code allocation crosses the approval seam): rejected. The minimal approval gate stays in the companion code as an illustration. Enforcement belongs to 4.3, as the prose says.
- CX16 (map language): fixed.

**Orchestrator QA notes**

- `translate_openai` on `response.failed` and `response.incomplete`: fixed. It emits `error` on both. Tested.
- `reduce` handles `error`: fixed and tested.
- Mirrored blocks: synced, and the doc-sync test passes.
- The badge agrees with the prose: fixed. See PC2.
- Carrier drift: fixed. See PC5.
- Alt text, five vs seven kinds: fixed. See CR picture-alone.
- Anthropic recovery for 4.6 and later: fixed. See FC2.
- The A2UI developer registers the catalogue: fixed. See FC3.
- OWASP claim: fixed. Narrowed to cross-site scripting and Markdown injection.
- "Reducer": fixed. Defined at first use.
- Build test: fixed. See CR build test.
- Optional `item["id"]`: fixed. Calls are matched by `output_index`, and the unknown-index case is tested.
- "The UI is a claim": left as a possible coinage in the author checklist. Not promoted in the prose.

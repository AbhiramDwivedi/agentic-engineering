# 9.5 Computer Use & Browser Agents

*A model that drives a screen. It picks each next click or keystroke from what it sees; your code decides what it sees, runs the action, and proves the job got done.*

## Why you'd reach for it

An agent is asked to fetch a CSV from a web page. It finds the button labelled *Download price list*, clicks it, sees the page sitting there unchanged, and tells you the job is done. The click worked. The file never arrived, and nothing in the agent's view of the page said so.

Agents that operate software through its screen fail this way because the model acts on a picture of an interface, and a picture is a weak witness: stale a second after it was taken, silent about the one thing that changed, and open to text that someone other than you put there. Anthropic's documentation warns that the model "sometimes acts as if its actions succeeded without explicitly checking their results."[^1]

Some software has no other door: an old supplier portal, a desktop accounting package, a canvas app, with no API and no feed. A scripted browser can reach it, but a script breaks the morning someone moves a button. An agent that looks at the page can survive the redesign, and pays for it with every problem above.

Take the Repricer, an agent on a commerce platform that adjusts a merchant's prices within rules. It needs each supplier's nightly price sheet. Most suppliers send a feed. One publishes its list only on a public web page: pick a region from a dropdown, press *Export*, get a CSV. If the agent picks the wrong region, or reports a download that failed, the Repricer prices the next day against stale numbers or the wrong region's, and nothing upstream notices because the agent said *"done."*

So let the model choose the next action, and make your code own everything around it. Your code decides what the model observes, executes each action and reports failures honestly, isolates the browser, and checks the end state (the file on disk, parsed and plausible) instead of taking the model's word.

Reach for screen-driving when:

- **The software has no API or feed**, and the task recurs often enough to automate.
- **The layout changes** often enough to keep breaking a fixed script.
- **The task needs judgment about the page**, such as finding the right row in a table whose structure varies.

The counter-trigger: when an API, a feed or a stable export exists, use it. Otherwise prefer a structured browser that reads the page's elements, and pixels last. That ordering is editorial judgment from cost and fragility, not a measured result.

## What it actually is

A computer-use agent is the ordinary tool loop with a screen on the other end. The model receives an observation (a screenshot, an accessibility snapshot, or both; the snapshot is a text outline of the page's buttons, links and fields, the structure screen readers use), returns one or more UI actions as tool calls (click here, type this, press Enter), and your harness executes them against a real browser or desktop, observes again, and sends the result back. The model decides what to do next; your code decides what it sees, whether an action runs, and when the task is finished.

![A loop diagram. Your code, drawn as rectangles, captures an observation (a screenshot or an accessibility snapshot) and sends it to the model; the model, drawn rounded, chooses the next UI action; your code executes that action in an isolated browser, returns a structured error if it failed, and observes again. Outside the loop, a separate rectangle owned by your code verifies the end state, such as the downloaded file, before anything downstream uses it.](computer-use-and-browser-agents-loop.svg)

The model chooses the next action from what it observes, so this is agentic. A Playwright script (Playwright is Microsoft's open-source library for driving browsers from code) that clicks through a fixed sequence is automation you already know, even when a model wrote it. Mechanically nothing is new: it is the request, execute, result cycle of [Tool Use](../the-unit/tool-use.md) running inside [the agent loop](../the-unit/the-agent-loop.md). What is new is the observation, and the step from what the model sees to what it acts on, which researchers call *grounding*: turning an intention like *"click the export button"* into a coordinate or a page element. The SeeAct study of GPT-4V as a web agent concluded that "grounding still remains a major challenge."[^2]

Anthropic, OpenAI and Google ship the same shape: Anthropic a computer-use tool for whole desktops and a browser tool that works through page structure as well as screenshots,[^1][^3] OpenAI a computer tool that returns an ordered list of actions per call,[^4] Gemini a computer-use model that returns function calls your client executes.[^5]

**Maturity: Established for the capability and for scoped structured browsing; Emerging for general desktop autonomy, injection defences and evaluation method.** Established describes the loop as shipped engineering rather than proven reliability: three vendor APIs, and Playwright MCP, Microsoft's server that exposes Playwright to a model and drives browsers from snapshots by default.[^11] The benchmarks are the evidence for the Emerging tier. OSWorld, a suite of real desktop tasks across operating systems and applications, launched with humans completing over 72% against 12.24% for the best model, which struggled mainly with GUI grounding and operational knowledge.[^6] On WebArena, a set of self-hosted websites with realistic tasks, the best GPT-4 agent reached 14.41% against 78.24% for humans.[^7] Vendor scores have since climbed far higher, and harder suites followed. OSWorld 2.0's long-horizon workflows find agents losing track of constraints, missing information that arrives mid-task, guessing instead of asking the user, and skipping verification. They fail most when a task hinges on hidden state they must recover.[^8] Long runs are [9.1 Long-Running Agents](when-you-want-autonomy.md).

Read any score with three questions kept apart. First, the protocol. When Emergence re-ran OpenAI's Operator on WebVoyager, a benchmark of tasks on live public websites, under a standardized evaluation protocol, it scored 68.6% against the 87% OpenAI had reported.[^9] The climb from OSWorld's 12% to that 87% compares two different benchmarks, the second scored under the vendor's own protocol. Second, the evaluator. An audit of 150 failed trajectories (a trajectory is the full record of one run's observations and actions) found 15.3% of the FAIL verdicts were wrong, so some scores understate the agent.[^10] Third, the agent: only what survives both is genuine task failure. So ask who ran the number, on which model version, with what step budget (the cap on actions per task), and how success was judged, and check the live leaderboard rather than a launch post. Vendor-reported reliability on real tasks remains contested. Measuring your own flow is [4.2 Evaluation](../craft/proving-it-works.md).

Two neighbours get confused with this. A tool that calls a supplier's API is plain tool use. And [MCP](../the-unit/mcp.md) is a transport: it carries tool calls between the model and the server that runs them. An MCP server can expose an API, DOM operations or raw pixel actions, so "it uses MCP" says how the tool is wired and nothing about which surface (API, structured page, pixels) it touches.

## How to do it

Five contracts carry the loop, and your code owns each of them.

**Observe fresh, and map coordinates back.** An observation goes stale the moment the page navigates or changes materially, so observe again after every navigation and after any failed action. If you send screenshots, the model answers in the pixel space of the image it received: when you scale a screenshot down, keep the factor and scale the returned coordinates back up before clicking. A macOS Retina display captures at twice the logical resolution, so a click that lands in the wrong place is often a missing divide-by-two.[^1]

**Prefer structure where the page has it; keep pixels for reach.** Pixels reach anything with a screen: desktop apps, canvases, remote desktops. Structured access reads the page's accessibility tree, the source of that snapshot, and hands the model element references instead of coordinates, which is cheaper and more deterministic but needs a DOM. The two combine. Anthropic's browser tool returns references such as `ref_2`, scoped to the tab that produced them and valid until that tab navigates or its DOM changes materially. The API cannot detect a stale reference, so your executor must return an error ("ref_3 is stale or not found on the current page") and let the model read the page again.[^3]

Playwright MCP drives a browser from accessibility snapshots by default and needs no vision model; its coordinate tools are opt-in with `--caps=vision`.[^11] The flag enables those tools without making pixels an automatic fallback, so your harness decides when the agent may use them.

**Run batches in order and stop at the first failure.** Some interfaces return several actions per turn. Anthropic's contract says to run the blocks in the order they appear, stop at the first failure, answer the failed block with a tool result flagged `is_error`, and answer every later block with an `is_error` result reading "Not executed: an earlier computer action in this turn failed." Leave any block unanswered and the request is rejected. If a person confirms consequential actions, check before each block, because a batch can complete a multistep action inside one turn.[^1] A gate that checks once per turn can see a form only after the batch has filled it and pressed *Submit*. OpenAI's `computer_call` likewise carries an ordered `actions` array.[^4] Batching also lets you observe once per batch instead of after every keystroke.

**Treat completion as an event you verify.** A click that starts a download proves the download started. Anthropic's browser tool has your harness report a download as three asynchronous events correlated by a `download_id` you assign (`download_started`, `download_completed`, `download_failed`).[^3] Wait for the completed event, then check that the file exists, parses and has the columns you expected before anything downstream reads it. The reported URL often carries signed query-string credentials (a temporary access token in the URL) after redirects, so strip it before it reaches the model's context or a log.[^3] Parsing the file belongs to [6.1 Ingestion](../io-boundary/getting-the-mess-in.md). When the model says the task is complete, treat that as a claim for [the outer loop](../composition/the-outer-loop.md), the code-owned verify-and-retry cycle around the agent, to check.

**Fail into the loop, with limits.** Return a failed action as a structured error the model can act on, never as an exception that kills the run. Cap steps, time and spend, and log every action with the observation that prompted it. Those limits belong to [the harness](../the-unit/the-harness.md), the code that wraps the model, and they turn a looping agent into a failed run you can read.

One run of the Repricer's price-sheet fetch, in an isolated browser with no stored credentials:

1. Your code opens the supplier's public price-list page and sends the model an accessibility snapshot. The model asks to open the region dropdown by its reference.
2. Opening the dropdown re-renders part of the page, so the reference the model tries next is stale. Your executor returns the stale-reference error; the model asks for a fresh snapshot and selects "North America."
3. The model clicks *Export (CSV)*. Your code reports `download_started` with a `download_id`, and strips the signed query string from the URL before the model sees it.
4. A later result carries `download_completed`, and the model reports success.
5. Your code, outside the loop, opens the file, checks that it parses and that every row's region column reads North America, and only then hands it to the Repricer. Had step 4 brought `download_failed`, the run would end as a structured failure and the Repricer would keep yesterday's prices, flagged stale.

## Security & trust

A screen-driving agent reads text written by strangers and acts with whatever authority its browser holds, which makes it a direct target for prompt injection: instructions planted in content the model reads, which the model then follows. The threat is established. In August 2025 Brave showed that Perplexity's Comet browser, asked to summarize a Reddit thread, would follow instructions hidden behind a spoiler tag in one comment: find the user's email address, trigger a one-time-password login, read the code from the user's logged-in Gmail, and post both back as a reply. Comet passed page content to its model without separating it from the user's request.[^12]

Defences are improving, and neither Anthropic nor OpenAI claims a complete one. Anthropic reported that Claude for Chrome's attack success rate on its red-team tests fell from 23.6% to 11.2% in autonomous mode after mitigations.[^13] In November 2025 it reported lower rates for newer models on a different evaluation, and wrote that even a 1% rate "still represents meaningful risk."[^14] OpenAI wrote that prompt injection "is unlikely to ever be fully 'solved.'"[^15] Treat everything the page supplies as untrusted: visible and hidden text, tab titles, URLs, download names. Anthropic advises building page reads from what the page renders rather than raw DOM source, so hidden text never reaches the model.[^3] The full treatment is in [Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md).

Three boundaries limit the damage, and they blur easily. **Host isolation** means running the browser and its executor in a dedicated VM or container with minimal privileges, so a hijacked agent cannot reach your filesystem or internal network;[^1][^3] a fresh browser profile on your laptop is not a process or filesystem boundary, so it does not give you that. **Session authority** is whatever the logged-in browser can do, because a hijacked agent can do all of it. That is why the Repricer's fetch runs with no credentials at all; an agent that must log in needs a deliberately scoped account ([8.5 Locks, PII & Identity](../production/locks-pii-identity.md)). **Network enforcement** restricts reachable hosts at the network layer to an allowlist (only listed hosts are reachable) and re-checks after redirects, because an allowed page can redirect to one that is not.[^3] Playwright MCP's README says its `--allowed-origins` filter "does not serve as a security boundary and does not affect redirects,"[^11] so treat it as a convenience and enforce the allowlist below the browser. Isolation in depth is [9.4 Sandboxing](sandboxing.md).

Confirmation is the last boundary, and vendors build one in. Gemini attaches a `safety_decision` to a proposed action; when it reads `require_confirmation`, your client must ask the user and, on approval, set `safety_acknowledgement` in the function result.[^5] OpenAI's computer tool can return pending safety checks, which stop its sample code unless you add a human-approval path.[^4] Claude for Chrome asks before publishing, purchasing or sharing personal data.[^13] A vendor classifier decides when to ask, and it does not know what counts as consequential in your domain. Your application owns authorization: decide which actions need a person, treat a denied or unanswered confirmation as a clean stop, and let a person take over. The general pattern is in [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md).

## Gotchas

1. **Some interactions stay fragile.** Anthropic notes that dropdowns and scrollbars can be hard to drive with mouse movements and suggests prompting for keyboard shortcuts instead, and that slow pages need a delay after actions.[^1] Pop-ups and cookie banners land between observation and click; a consistent environment (fixed resolution, fixed browser, banners pre-dismissed) removes most of that class of failure.
2. **The wrong element, confidently.** A click on the neighbouring row looks like success in the next screenshot unless something checks. Prefer references over coordinates where the page allows, and verify the effect of any action that matters.
3. **Observations cost tokens and attention.** Anthropic puts a screenshot at roughly 1,000 to 1,800 input tokens.[^1] Structured observations cost too: Playwright's README says its CLI is more token-efficient than its MCP server because it avoids loading "large tool schemas and verbose accessibility trees" into context.[^11] Send the smallest observation that answers the step and drop old screenshots, which also spares the model's attention. Pruning keeps a long run affordable without making it reliable. General techniques are in [5.4 Compaction](../knowledge/compaction-and-the-window.md) and [8.4 Controlling Cost](../production/controlling-cost.md).
4. **Screen-driving what has an API.** It is slower and costlier than the call it replaces, and easier to attack, because every page it reads can carry injected instructions. It survives because it worked in the demo.

## In short

Use the API when there is one. When there is not, let the model choose the clicks and make your code own the rest: fresh observations, references over pixels where the page has structure, batches that stop at the first failure, downloads verified as files on disk, and an isolated, credential-free browser behind a network allowlist and a confirmation gate you control. Trust the end state your code checked over the model's report of it, and read every benchmark score with its protocol attached.

<small class="chapter-meta">**Maturity: Established (capability, scoped structured browsing) / Emerging (general desktop autonomy, injection defences, evaluation method)** (three labs ship the loop and Playwright MCP defaults to snapshot browsing; long-horizon reliability and injection resistance are not settled, and vendor reliability claims are contested) · *Who decides:* the model (the next UI action) / your code (the observation, the execution, the proof of done) · *Grounding:* research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Computer use tool" (API documentation; batch-action rules, coordinate scaling, isolation and confirmation guidance, screenshot token cost). <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>
[^2]: Zheng, B., et al., "GPT-4V(ision) is a Generalist Web Agent, if Grounded" (2024). <https://arxiv.org/abs/2401.01614>
[^3]: Anthropic, "Browser use tool" (API documentation; element references, download events, URL sanitizing, isolation precautions). <https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool>
[^4]: OpenAI, "Computer use" (API guide; ordered `actions` array, pending safety checks). <https://developers.openai.com/api/docs/guides/tools-computer-use>
[^5]: Google, "Computer use" (Gemini API documentation; `safety_decision` and `safety_acknowledgement`). <https://aistudio.google.com/docs/computer-use#safety-decisions>
[^6]: Xie, T., et al., "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments" (2024). <https://arxiv.org/abs/2404.07972>
[^7]: Zhou, S., et al., "WebArena: A Realistic Web Environment for Building Autonomous Agents" (2023). <https://arxiv.org/abs/2307.13854>
[^8]: Yuan, M., et al., "OSWorld 2.0: Benchmarking Computer Use Agents on Long-Horizon Real-World Tasks," arXiv:2606.29537. Failure classes as stated in the abstract. <https://arxiv.org/abs/2606.29537>
[^9]: Akkil, D., et al., "Emergence WebVoyager: Toward Consistent and Transparent Evaluation of (Web) Agents in The Wild" (2026). The re-evaluation standardizes task instantiation, failure handling, annotation and reporting, so the gap reflects a changed protocol as well as the agent. <https://arxiv.org/abs/2603.29020>
[^10]: Dong, Z., et al., "How Benchmarks Mis-Score Computer-Use Agents" (2026). The audit covers trajectories scored as failures only, so it says nothing about false passes. <https://arxiv.org/abs/2607.28367>
[^11]: Microsoft, Playwright MCP README (snapshot default, `--caps=vision`, origin filters, CLI versus MCP). <https://github.com/microsoft/playwright-mcp>
[^12]: Brave, "Agentic Browser Security: Indirect Prompt Injection in Perplexity Comet" (2025-08-20). <https://brave.com/blog/comet-prompt-injection/>
[^13]: Anthropic, "Piloting Claude in Chrome" (2025-08-25; attack success rates and site permissions and action confirmations). <https://claude.com/blog/claude-for-chrome>
[^14]: Anthropic, "Mitigating prompt injections in browser use" (2025-11-24). The figures come from a different evaluation than the August post and are not a like-for-like trend. <https://www.anthropic.com/research/prompt-injection-defenses>
[^15]: OpenAI, "Continuously hardening ChatGPT Atlas against prompt injection attacks" (2025-12-22). <https://openai.com/index/hardening-atlas-against-prompt-injection>

## See also

- [2.1 Tool Use](../the-unit/tool-use.md), the request, execute, result cycle this loop is built on.
- [2.4 MCP](../the-unit/mcp.md), the transport a browser tool often arrives through.
- [2.6 The Harness](../the-unit/the-harness.md), where the step caps, logging and execution boundary live.
- [3.7 The Outer Loop](../composition/the-outer-loop.md), for checking the end state and retrying from outside the model.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md), for enforcing the confirmation gate and action limits as code.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md), the full threat model behind the Security & trust section.
- [9.4 Sandboxing](sandboxing.md), for isolating the browser and its executor in depth.
- [9.6 Coding Agents](coding-agents.md), agents that drive a browser to check their own work.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for "screen-driving what has an API."

## Further reading

- [Anthropic, Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool): a detailed public executor contract, covering references, downloads and isolation.
- [Playwright MCP](https://github.com/microsoft/playwright-mcp): the structured-browsing approach you can run today, with its own stated limits.
- [OSWorld 2.0](https://osworld-v2.xlang.ai/): long-horizon desktop tasks and where agents still fail on them.
- [How Benchmarks Mis-Score Computer-Use Agents](https://arxiv.org/abs/2607.28367): how often a reported failure is the evaluator's mistake.
- [Brave on Comet](https://brave.com/blog/comet-prompt-injection/): the clearest public walk-through of an agentic-browser injection.

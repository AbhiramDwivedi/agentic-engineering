# 9.3 The Protocol Landscape

*Which connection are you on? An agent system has four kinds of connection (to tools and data, to other agents, to a person, to a payer), and a growing set of protocols standardises each one. Pick per connection, check that both ends speak the same version, and keep the decision to act in your own code, because no protocol makes it for you.*

## Why you'd reach for it

Suppose your agent finds a supplier's agent through its published Agent Card, a JSON file in which an agent describes itself, and hands it a restocking task. Every message validates against the specification. The remote agent replies that the order is placed. Nothing in that exchange asked whether your agent was allowed to place an order, with that supplier, for that amount, and nothing in the protocol could have. The protocol carried the conversation; the permission check belonged to your harness, the code around the model that owns permissions and the execution boundary, and nobody ran it.

A common failure starts with the wrong question: does this new protocol replace MCP, or which commerce protocol will win? Both treat tools with different jobs as one market. MCP, the Model Context Protocol, connects an application to tools and data; A2A, the Agent2Agent protocol, connects one agent to another it cannot see inside. Asking "which protocol?" before asking "which connection?" is how a team ends up wrapping a database in an agent protocol, or wiring checkout through a spec that is still in beta.

The cost of getting it wrong runs in two directions. Adopt too early and you pay for churn: MCP's 2026-07-28 revision removed the opening handshake that every earlier server expects before it answers anything,[^mcp-changelog] and the specification says a client on the new revision talking to a server that only knows the old one fails.[^mcp-versioning] Adopt too trustingly and you pay in exposure: a published analysis of A2A found eleven protocol-level vulnerabilities, each exploitable by an agent that follows the specification to the letter.[^a2abreak]

You need this chapter when:

- **A second team or vendor owns the other end,** so the shared contract is the protocol.
- **A host you do not control has to load your capability,** the case MCP exists for.
- **The other end is stateful and opaque:** a remote agent that negotiates, asks for input and runs for minutes.
- **Money moves on the agent's say-so.** Payment and checkout protocols exist because "the model said buy it" is not evidence a merchant or a payment processor will accept.

The counter-trigger: when you own both ends, or the other end is a plain API with a stable contract, call it directly.

## What it actually is

The protocol landscape is a map of connections, each with its own standards and maturity, and one rule holds across all of them: a protocol defines how two parties exchange requests, state and results, and none of them decides whether your agent may act on what it receives. Instruction files such as AGENTS.md and Agent Skills tell an agent how to behave rather than how to connect, and they belong to [2.3 Skills](../the-unit/skills.md).

![Your agent sends four lanes, one per connection: MCP to tools and data, A2A to an opaque remote agent, MCP Apps, A2UI and AG-UI to a person, and UCP, ACP, AP2, x402 and MPP to a merchant and payer. Every reply returns along one rail into a single box, "your code: authority check", which asks whether this agent may act, with this party, for this amount, and passes or refuses before any action.](protocol-landscape-connections.svg)

The agentic part sits upstream of the wire. When the model chooses to delegate to a remote agent, it is deciding (2.5 The Agent Loop, 9.2 Multi-Agent); the protocol only shapes the delegation once it is chosen.

MCP as a way to connect is Standard: hosts from several vendors support it,[^mcp-apps] and it is a hosted project of the Agentic AI Foundation (AAIF) under the Linux Foundation, alongside A2A.[^aaif-a2a] Its 2026-07-28 revision is Emerging: four months old, and it breaks old pairings. A2A in practice is Emerging; the foundation names Huawei as a user and Tencent's WeChat as integrating it,[^aaif-a2a] and independent evidence of cross-vendor production use is thin so far. Everything on the person and payment edges is Emerging.

### The resource edge: MCP

MCP connects a host application to servers that expose tools, resources and prompts; [2.4 MCP](../the-unit/mcp.md) teaches it in depth. Revision 2026-07-28 made the protocol stateless: it dropped the `initialize` handshake and the `Mcp-Session-Id` header, every request now carries its protocol version and client capabilities in a `_meta` field, and every server must implement `server/discover`, a call that returns what the server supports.[^mcp-changelog] "MCP 2.0" is informal shorthand for it. A server may support both eras, before and after this revision, at once, and the versioning page's era matrix, a grid of old and new clients against old and new servers, shows which pairs work.[^mcp-versioning] Migration detail belongs to 2.4.

### The peer edge: A2A

A2A connects your agent to another agent that keeps its own state, reasoning and tools out of view. The project draws the line this way: tools are "primitives with well-defined, structured inputs and outputs", while agents keep state over longer interactions, and A2A is for the second.[^a2a-mcp]

An A2A agent publishes an Agent Card at `/.well-known/agent-card.json`, optionally signed as a JSON Web Signature.[^a2a-spec] The specification defines three bindings, meaning wire formats the same operations can travel over: JSON-RPC, gRPC and HTTP+JSON. A simple exchange is a `Message`; committed work is a `Task` with a lifecycle. A task can be working, can pause in `input-required` or `auth-required`, and ends in one of four terminal states: completed, canceled, rejected or failed. A terminal task cannot restart; a follow-up starts a new task in the same context.[^a2a-task] Results come back as artifacts, separate from conversational messages; progress arrives by streaming or push notification when the Agent Card advertises them.[^a2a-spec]

Suppose Stockwell, the fictional commerce platform behind this book's examples, gives its repricing agent a restock job: ordering stock from a supplier. The supplier's agent is this kind of peer: it may stop in `input-required` to ask whether a substitute pack size will do, and runs for minutes. Record the version you tested as release v1.0.1 (2026-05-28), which corrected the media type and TaskStatus values; the specification header still reads 1.0.0.[^a2a-release]

### The person-facing edge

**MCP Apps** lets a tool declare `_meta.ui.resourceUri` pointing at a `ui://` resource, which the host renders as HTML in a sandboxed iframe in the conversation.[^mcp-apps] **A2UI** has the agent send declarative JSON that a native renderer draws, and the agent can place only components the developer has registered, never executable code.[^a2ui] **AG-UI** is an event protocol for the channel between an agent backend and the frontend a user sees; its documentation describes A2UI as a different thing that pairs well with it.[^agui] Choose by who owns the screen: inside someone else's chat host, MCP Apps; in your own native app, A2UI; in your own web frontend, AG-UI, carrying A2UI if you want generated components. Streaming and approval UX are 6.3 Streaming & Agent UX.

### The payment edge

Five protocols do three jobs here. Checkout, an agent buying from a merchant the way a shopper would, has two competitors. **UCP**, the Universal Commerce Protocol, can ride as an A2A extension that a business advertises in its Agent Card.[^aaif-fits] **ACP**, the Agentic Commerce Protocol from OpenAI and Stripe, is in beta with its latest stable release dated 2026-04-17.[^acp][^ibm-acp] Authorisation is **AP2**'s job. It carries mandates: signed records of what a user agreed to, named Checkout Mandate and Payment Mandate.[^ap2] Paying per request is the third job. **x402** returns HTTP 402 until the client pays, mainly in stablecoins, tokens pegged to a currency;[^x402] **MPP**, the Machine Payments Protocol from Stripe and Tempo (2026-03-18), lets an agent receive a payment request, authorise it and get the resource, in ordinary currency or stablecoin.[^mpp]

Run the restock order through that. If the supplier charges per lookup on its stock-level feed, that is an x402 or MPP job, small enough to run on a capped balance. The order itself is not a checkout job yet. We would have the agent negotiate the order over A2A and a person confirm it in the supplier's own purchase flow, until both ends support AP2 mandates and your policy holds a cap.

Not every one of these proves that a person authorised the spend. UCP is explicit about the gap: a checkout "has to be finalized manually by the user through a trusted UI unless the AP2 Mandates extension is supported."[^ucp-checkout] A mandate is evidence of intent. The decision to spend is shared between the user, the merchant and payment parties who validate that evidence, and your harness, whose policy should refuse a spend the user never bounded with a limit, a counterparty and an expiry. Counterparty enforcement protects the counterparty; your policy is the only part you control. Identity and tokens are 8.5 Locks, PII & Identity.

## How to do it

Record the decision as one dated row per connection, because these cells move.

| Connection | Protocol | Maturity | Cost of adopting early | Do-nothing option | Reviewed |
|---|---|---|---|---|---|
| Agent to tools and data | MCP, revision 2026-07-28 | Standard (MCP); Emerging (this revision) | New clients fail against old-only servers; SDK and host support lag | Native tool definitions and a direct API call ([2.1 Tool Use](../the-unit/tool-use.md)) | 2026-11 |
| Agent to opaque peer agent | A2A 1.0.x | Emerging | Every task state needs handling; published protocol-level attacks | Wrap the peer's API as a tool | 2026-11 |
| Agent to person (embedded app) | MCP Apps | Emerging | Host support varies by client | Return text or structured output | 2026-11 |
| Agent to person (native UI) | A2UI | Emerging | A component catalog and a renderer per platform | Your own components | 2026-11 |
| Agent backend to frontend | AG-UI | Emerging | Event plumbing to adopt | The streaming you already have | 2026-11 |
| Agent to merchant checkout | UCP or ACP (competing) | Emerging; adoption Contested | Two young specs that may both need supporting | Hand the person to the merchant's own checkout | 2026-11 |
| Payment authorisation | AP2 | Emerging | Mandate signing on both sides | A person confirms in a trusted UI | 2026-11 |
| Pay per request | x402 or MPP | Emerging | Settlement setup on both sides | An API key and an invoice | 2026-11 |

Then, before you build against a row, run the compatibility check:

1. **Name the connection.** An instruction file or an in-process call is not a protocol question.
2. **Match the binding.** An A2A client that speaks only JSON-RPC cannot talk to an agent that serves only gRPC.
3. **Match the revision.** MCP declares a date-string version on every request; A2A versions by major and minor. Read the other end's `server/discover` result or Agent Card, never a blog post about it.
4. **Match the extensions.** An extension is an optional feature on top of the core protocol that each side has to opt into. MCP Apps, MCP Tasks (requests that run long and are checked on later) and AP2 Mandates are extensions. In MCP, if only one side supports an extension, the supporting side must fall back to core behaviour or reject the request.[^mcp-versioning] UCP drops any capability the two sides have no shared version of.[^ucp-overview]
5. **Record the outcome with a date and a source.** "Compatible as of 2026-11, per the server's discover result" is a row; "supports MCP" is not.

When the check fails, the outcome is **no compatible interface**, and it is a legitimate result. Then build an adapter you own, call the counterparty's plain API, or do not connect. For versions, MCP's specification says to select a mutually supported version or "surface an error to the user if no compatible version exists."[^mcp-versioning] Silently falling back to whatever half-works is the option to refuse.

### Returning a remote failure to the model

An A2A task can end in more ways than a tool call, and the model learns only what your code tells it:

1. Your code sends `SendMessage` with the task and receives a `Task` in the working state.
2. It follows the task by stream, push notification or polling until the task reaches an interrupted or terminal state.
3. On `input-required`, your code decides whether the model or a person answers. On `auth-required`, your harness handles the credential, and the model never sees it.
4. On rejected, failed or canceled, your code returns a structured error to the model: the state, the remote agent's message marked as untrusted text, and whether a fresh task is worth trying.
5. On completed, the artifacts come back as untrusted data, and your authority check runs before anything in them is acted on.

Retry and resumption mechanics are 7.1 Retry & Graceful Degradation and 7.3 Checkpointing.

### The authority check

This is the check nobody ran in the opening. It sits in your code between a reply and an action, and it reads its limits from your own policy, never from the reply. For the restock order:

```text
acting:        restock agent, on behalf of merchant M      (your identity system)
counterparty:  supplier S                                   (your approved-supplier list)
action:        place order, 1,840 USD                       (from the A2A artifact: untrusted)
bound:         2,000 USD per order, 5,000 USD per week,
               approved suppliers only, expires 2026-12-31  (set by the merchant, or a signed mandate)

pass      every field inside the bound
refuse    counterparty not on the list, or a cap exceeded
ask       the reply wants something the bound does not cover, such as a substitute pack size
```

Only the action line comes from the remote agent, and it is checked against the rest. Asking a person is 4.3 Human-in-the-Loop.

### When A2A is overkill

Default to a direct call or a tool wrapper, even across a company boundary; a partner's REST API is still an API. Reach for A2A when the other side is a stateful peer you cannot inspect. The restock supplier qualifies; a supplier that publishes only a price list does not. Whether A2A is needed at all is Contested, and no published comparison settles it. Wrap the peer as a tool first, and move to A2A when you catch yourself hand-building a task lifecycle.

> **In Listing Studio.** The product-content pipeline reads catalog data through tools, so only the MCP row applies; the restock agent is what fills the A2A and payment rows.

## Security & trust

An Agent Card or a `server/discover` result is a claim the publisher makes about itself. A2A's specification says clients should verify signatures when present,[^a2a-spec] and a signature proves who published the card, not that the agent behaves as described. A2ABreak found attacks that live here: cross-client context injection through unprotected context identifiers, credential harvesting as identity is lost across multi-hop delegation, and exfiltration through rogue agents advertising capabilities without attestation.[^a2abreak] A separate benchmark, A2ASecBench, found protocol-aware attacks effective across A2A demo systems in travel, healthcare and finance.[^a2asecbench] Both are research results, not disclosed incidents; MCP's disclosed incidents are in [2.4 MCP](../the-unit/mcp.md).

Treat every card, artifact and returned message as untrusted text (4.6 Prompt Injection & the Lethal Trifecta). Scope authority per connection: the credential the restock agent presents to supplier S can place orders with S and do nothing else, so a rogue peer that harvests it gains little.

## Gotchas

- **MCP's old HTTP+SSE transport can go at any revision now.** SEP-2596, the proposal that set MCP's deprecation policy, went Final on 2026-05-18,[^sep-2596] and the registry makes HTTP+SSE removable three months later, so from about August 2026. Roots, Sampling, Logging and Dynamic Client Registration follow in the first revision on or after 2027-07-28.[^mcp-deprecated] SDKs and hosts can drop a feature sooner, so check what the other end serves today.
- **Old guides teach dead method names.** Tutorials using `agent.json`, `/tasks/send` or `message/send` for A2A do not match the 1.0.x specification, which uses `agent-card.json` and PascalCase methods such as `SendMessage`.[^a2a-spec] MCP guides with a handshake describe the previous revision.
- **AP2 renamed its mandates.** Older write-ups describe Intent and Cart mandates; the current site names Checkout and Payment mandates,[^ap2] so quote the dated spec.
- **Membership counts measure sign-ups.** A foundation's member list tells you who joined; for adoption, look for a named deployment carrying cross-vendor traffic.

## In short

Draw your system's connections first and fill the table second. MCP is the safe default on the resource edge; check which revision each server speaks before you upgrade a client. Wrap a remote agent as a tool until you need a task lifecycle, then move to A2A. Treat the person and payment edges as experiments with a date on them. Whatever the protocol, let it carry the request, and let your code decide whether the answer is acted on.

<small class="chapter-meta">**Maturity: n/a** (a map of connections; each protocol carries its own verdict, Standard for MCP connectivity, Emerging for the rest, Contested for the need for A2A and for commerce "winner" claims) · *Who decides:* your code (protocols carry the interaction; the model's choice to delegate is taught in 2.5 and 9.2) · *Grounding:* research · *Last reviewed:* 2026-11</small>

## Sources

[^mcp-changelog]: Model Context Protocol, "Key Changes," specification revision 2026-07-28. <https://modelcontextprotocol.io/specification/2026-07-28/changelog>
[^mcp-versioning]: Model Context Protocol, "Versioning and Compatibility," specification revision 2026-07-28, including the extension fallback rule and the client and server era compatibility matrix. <https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning>
[^mcp-deprecated]: Model Context Protocol, "Deprecated Features" registry, revision 2026-07-28. Earliest removal marks eligibility; actual removal is a Core Maintainer decision. <https://modelcontextprotocol.io/specification/2026-07-28/deprecated>
[^aaif-a2a]: Agentic AI Foundation, "A2A joins AAIF" (2026-08-17). Adoption examples are the foundation's own claims. <https://aaif.io/blog/a2a-joins-aaif>
[^aaif-fits]: Agentic AI Foundation, "Where A2A fits in the open agent ecosystem" (2026-08-20), including UCP advertised as an A2A extension in a business's Agent Card. <https://aaif.io/blog/where-a2a-fits-in-the-open-agent-ecosystem>
[^sep-2596]: Model Context Protocol, "SEP-2596: Specification Feature Lifecycle and Deprecation Policy," merged with the `final` label on 2026-05-18. <https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596>
[^a2a-mcp]: A2A Project, "A2A and MCP." <https://a2a-protocol.org/latest/topics/a2a-and-mcp/>
[^a2a-spec]: A2A Project, Agent2Agent Protocol Specification, at release tag v1.0.1 (the document's header reads 1.0.0). Agent Card signing, the three bindings, streaming and push capabilities, task states, method names and the well-known URI. <https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md>
[^a2a-task]: A2A Project, "Life of a Task." <https://a2a-protocol.org/latest/topics/life-of-a-task/>
[^a2a-release]: A2A Project, release v1.0.1 (published 2026-05-28; changelog dated 2026-05-26). <https://github.com/a2aproject/A2A/releases/tag/v1.0.1>
[^mcp-apps]: Model Context Protocol, "MCP Apps" overview, including the Excalidraw example and the client support list. <https://modelcontextprotocol.io/extensions/apps/overview>
[^a2ui]: A2UI project site (v1.0). <https://a2ui.org/>
[^agui]: AG-UI, "Introduction." <https://docs.ag-ui.com/introduction>
[^acp]: Agentic Commerce Protocol repository (beta; date-versioned; latest stable 2026-04-17 at time of review). <https://github.com/agentic-commerce-protocol/agentic-commerce-protocol>
[^ibm-acp]: Not to be confused with IBM's Agent Communication Protocol, also ACP, an agent-to-agent protocol. IBM Research's project page notes it is now part of A2A under the Linux Foundation. <https://research.ibm.com/projects/agent-communication-protocol>
[^ap2]: AP2 project site. The page links a v0.2 release and a FIDO Alliance donation. <https://ap2-protocol.org/>
[^x402]: x402 project site. <https://www.x402.org/>
[^mpp]: Stripe, "Machine Payments Protocol" (2026-03-18). <https://stripe.com/blog/machine-payments-protocol>
[^ucp-checkout]: Universal Commerce Protocol, Checkout capability, specification version 2026-08-25. <https://ucp.dev/2026-08-25/specification/shopping/checkout/>
[^ucp-overview]: Universal Commerce Protocol, specification overview (version selection and capability negotiation). Version 2026-08-25. <https://ucp.dev/2026-08-25/specification/overview/>
[^a2abreak]: Lotfi, A., Rahman, M. M., Karim, I., and Bertino, E., "A2ABreak: Systematic Security Analysis of the A2A Protocol," arXiv:2609.10871 (submitted 2026-09-09; v3 revised 2026-10-24). A preprint; the vulnerabilities were derived from a state model of the specification and validated against expert review. <https://arxiv.org/abs/2609.10871>
[^a2asecbench]: Li, T., et al., "A2ASecBench: A Protocol-Aware Security Benchmark for Agent-to-Agent Multi-Agent Systems," ICLR 2026. <https://safo-lab.github.io/A2ASecBench/>

## See also

- [2.4 MCP](../the-unit/mcp.md), for the resource edge in depth, its supply-chain risks and its incidents.
- [2.1 Tool Use](../the-unit/tool-use.md), the do-nothing option for most connections: a function the model can call.
- [2.3 Skills](../the-unit/skills.md), for instruction formats, which are not connection protocols.
- [1.5 Context Engineering](../foundations/context-engineering.md), on what every exposed schema and result costs the window.
- [3.3 Orchestrator-Workers](../composition/fan-out.md), for delegation you own on both sides, where no peer protocol is needed.
- 9.2 Multi-Agent, for when the model should delegate at all.

## Further reading

- [MCP Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning): the era matrix that tells you which client and server pairs work.
- [A2A specification at v1.0.1](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md): the pinned normative text for the task lifecycle and Agent Cards.
- [A2ABreak](https://arxiv.org/abs/2609.10871): the skeptical read, and why a compliant peer can still be an adversary.
- [Where A2A fits in the open agent ecosystem](https://aaif.io/blog/where-a2a-fits-in-the-open-agent-ecosystem) (AAIF, 2026-08-20): the foundation's own account of how A2A, MCP, UCP and AP2 fit together.
- [UCP Checkout](https://ucp.dev/2026-08-25/specification/shopping/checkout/): a dated commerce spec, useful for seeing where user authorisation is and is not proven.

# 1.4 The Augmented LLM

<small class="chapter-meta">**Maturity: Standard** (the accepted base unit of agentic systems) · *Who decides:* the model (it chooses whether and when to call the tool) · *Grounding:* production + research</small>

*The atom every agentic pattern builds on: a model call paired with a contract (a state object) and at least one tool.*

## 1. Why you'd reach for it

Ask a bare model to set the listed price for the Aldsworth desk and it will answer. It will give you a number, in a confident sentence, every time. The number is the problem. The model has no way to know Northvale's minimum advertised price, because that floor lives in Stockwell's pricing rules, not in the model's weights, and a price below it is a contract violation with the supplier. A plain model call cannot look the floor up, cannot enforce it, and cannot hand you a value your code can act on without re-parsing English. It is fluent and unconnected, a bad combination for a step where a wrong number is a liability.

That is the gap. A model on its own can reason about a task but cannot take action in your world or return a result on a contract. When you wire it into a pipeline anyway, the failure is quiet: the price node emits a plausible-looking figure, the listing publishes, and the gap surfaces later as a chargeback or a pulled listing rather than as an exception you could have caught.

The fix is small. You give the model one tool, a plain function that looks up the MAP floor, and you let the model decide to call it; your code runs the lookup, enforces the constraint, and writes the result into a typed state object the rest of the pipeline reads. Model plus tool plus a state contract: that combination is the augmented LLM, and it is the smallest thing in this reference that can both act and be trusted by the code around it.

Reach for the augmented unit when:

- a step needs to act on something outside the model's training data: a current price, a customer record, a live inventory count;
- a step's output has to be consumed by code rather than only read by a human, so it needs a contract a downstream node can rely on;
- you are about to build any larger pattern in this reference, because every one of them is an arrangement of this unit and you need it solid first.

You do not need it when a plain model call already does the job: a one-shot summary, a classification a human reads, a draft nobody's code depends on. If nothing downstream acts on the result and the model needs nothing it doesn't already hold, a bare call is the simpler thing, and you should use it.

## 2. What it actually is

The augmented LLM is not a product or a framework. It is a unit of composition: one model call, paired with one or more tools the model can invoke, and a typed state object the node reads from and writes back to. Nothing else. Anthropic describes this as the base unit of any agentic system,[^anthropic] and the framing is useful precisely because it is minimal: if you understand this unit, you understand what every more complex pattern (fan-out, evaluator-optimizer, specialist panel) is built from.

Three parts, all mandatory:

- **State.** A typed record the node reads from and writes to. Later nodes read what this one wrote; the pipeline's contract is in the schema.
- **The tool.** A plain function in your code, described to the model as a JSON schema. The model decides when to call it; your code runs it and owns the result.
- **The node.** The function that ties them together: it reads state, invokes the model-plus-tool unit, and writes a partial dict back for the graph to merge.

The pricing step of Listing Studio illustrates all three. The model cannot know the supplier's MAP floor, since that lives in your pricing rules, not in its weights. You give it a tool that looks the floor up, the model calls it, and your code enforces the constraint. The result is written to `price_cents` in state and becomes visible to every downstream node.

**The augmentations, and where each is taught.** Tools are the one this chapter shows, but they are not the only thing you can bolt onto a model call. Anthropic's framing names a small family: tools to reach outside the weights, retrieval to widen what the model knows, and memory to carry context across turns.[^anthropic] Tools and a structured-output contract are the load-bearing pair, the two you reach for in most pipeline steps; retrieval and memory are real and proven but situational, and most batch pipelines never need them. This chapter assembles the unit and points to where each part is taught in depth, rather than re-teaching all four here:

- **Tools** let the model call a typed function in your code. Full treatment in [2.1 Tool Use](../the-unit/tool-use.md).
- **Structured output** is the typed contract on the model's result, the junior partner to tool use. See [2.2 Structured Output](../the-unit/structured-output.md).
- **Retrieval (RAG)** augments the unit with fetched knowledge for questions the weights can't answer. See [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md).
- **Memory** is what the unit retains across turns, and it is often confused with pipeline state. See [5.3 Memory](../knowledge/real-memory.md), and the distinction in [5.1 State, Not Memory](../knowledge/state-not-memory.md).

**Why this is the atom.** The reason to define the unit so tightly is that every larger pattern in the reference is an arrangement of it, not a new primitive. Prompt chaining is this node run in sequence. Fan-out is several of these nodes run in parallel. The evaluator-optimizer is two of them in a loop, one drafting and one grading. The specialist panel is the same node wearing different personas. Get the augmented unit and the substrate it runs on, and the rest of the book is composition. This is where the reference's thesis that building with agents is still engineering ([1.1 It's Still Engineering](its-still-engineering.md)) cashes out: if the parts are familiar and the arrangements are familiar, the novelty has to live somewhere specific, and it does.

**The litmus reading, and why it makes the unit Standard.** This is the first place in the reference where the model actually decides something. Apply the test from [1.2 Who Decides?](who-decides.md): inside the unit the *model* decides whether and when to call the tool, while *your code* owns the node wiring, the contract, and whether a result is allowed to matter. That single model-made judgment, the choice to reach for `lookup_floor_price` on this turn, is what makes the augmented LLM the seed of every genuinely-new pattern; remove it and you are back to a deterministic function call. The maturity verdict follows from how settled this is. Anthropic names the augmented LLM the basic building block of agentic systems;[^anthropic] the major vendor SDKs all ship tools and structured output as first-class features ([2.1](../the-unit/tool-use.md), [2.2](../the-unit/structured-output.md)); and the dominant orchestration frameworks are built on the state-graph-of-nodes runtime this chapter assumes.[^langgraph] When the primary source, the vendor SDKs, and the framework ecosystem all converge on the same base unit, the honest tier is **Standard**: this is the accepted default, not a contested bet.

**The substrate: a node on a state graph.** The unit does not run in a vacuum. It sits in a *node* on a *state graph*: the node reads the current state, calls the augmented unit, and returns an enriched state for the next node; *edges* sequence the nodes. That is the runtime model the whole reference stands on, and the LangGraph code below is one concrete instance of it.[^langgraph] This chapter introduces just enough vocabulary, node, state, edge, to read the diagrams in later chapters. Reducers, persistence, and checkpointing are real and they matter, but they are [5.1 State, Not Memory](../knowledge/state-not-memory.md)'s job, not this chapter's. One property of the unit is worth naming here: every tool schema, every retrieved chunk, and every memory item rides in the context window on each call and taxes both the token bill and the model's attention. Name the cost now, then see [1.5 Context Engineering](context-engineering.md) for the general principle and [2.1 Tool Use](../the-unit/tool-use.md) for tool-schema bloat in particular.

**State, the pipeline's contract:**

```python
class ListingState(TypedDict):
    """Shared state threaded through every node in the pipeline.

    Each node receives the full state dict, reads what it needs, and returns
    a partial dict with only the keys it changed. LangGraph merges the result
    back into state automatically.
    """
    supplier_sku: str           # the join key from the supplier feed
    title: str                  # merchandised product title
    price_cents: Optional[int]  # the proposed listed price; None until the
                                # price node runs
```

## 3. How to do it

The unit and the node look like this across the three provider shapes. It is deliberately the smallest thing that shows all three parts at once: one model call, one tool, one typed state object, with nothing extra to read past. The mental model is shared across providers; the wire format is not, so each tab is one vendor's shape. LangGraph leads because it is the carrier's stack; the raw OpenAI Responses and Anthropic Messages variants follow for readers on those SDKs. The shape of the unit is identical in all three; only the field names move (Anthropic's `input_schema` against OpenAI's `parameters`, and so on).

**The unit, one model and one tool:**

=== "LangGraph"

    ```python
    # The augmented-LLM unit: one model paired with one tool.
    # The tool is a decorator over your plain function — LangGraph reads the
    # description from the type hints and docstring; underneath it is a JSON schema.
    @tool(parse_docstring=True)
    def lookup_floor_price(supplier_sku: str) -> dict:
        """Look up the supplier's minimum advertised price (MAP) floor.

        Args:
            supplier_sku: the product SKU to look up.
        """
        return {"floor_cents": 39900}  # $399.00 MAP for the Aldsworth desk


    # One model, one tool, one contract — the atom.
    agent = create_agent("openai:gpt-5.5", tools=[lookup_floor_price])
    ```

=== "OpenAI Responses API"

    ```python
    # The same unit, OpenAI Responses shape: the tool is a JSON schema object you
    # pass to the API; the model reads the description and decides when to call it.
    FLOOR_PRICE_TOOL = {
        "type": "function",
        "name": "lookup_floor_price",
        "description": (
            "Look up the supplier's minimum advertised price (MAP) floor for a "
            "product. Call this before quoting a price."
        ),
        "parameters": {
            "type": "object",
            "properties": {"supplier_sku": {"type": "string"}},
            "required": ["supplier_sku"],
            "additionalProperties": False,
        },
    }
    ```

=== "Anthropic Messages API"

    ```python
    # The same unit, Anthropic Messages shape: input_schema instead of parameters,
    # no top-level type field. The model reads this description and decides when
    # to call the tool.
    FLOOR_PRICE_TOOL = {
        "name": "lookup_floor_price",
        "description": (
            "Look up the supplier's minimum advertised price (MAP) floor for a "
            "product. Call this before quoting a price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"supplier_sku": {"type": "string"}},
            "required": ["supplier_sku"],
            "additionalProperties": False,
        },
    }
    ```

**The node reads state, invokes the unit, writes state.** The node is the load-bearing piece: it reads `supplier_sku` and `title` out of state, runs the model-plus-tool unit, and returns a partial dict (`price_cents`) that the graph merges back. The next node reads what this one wrote, which is the whole substrate in one sentence. Because the unit consumes its own tool results, the loop runs until the model stops asking for tools, capped by `MAX_STEPS` so a stuck model fails loud instead of spinning. The deep version of that loop, and the rule that a failed tool comes back to the model as a recoverable message rather than a raw exception, belong to [2.1 Tool Use](../the-unit/tool-use.md); here the cap is just a property of any unit that loops.

=== "LangGraph"

    ```python
    def price_node(state: ListingState, _agent: Any = None) -> dict:
        """One graph node: reads state, runs the augmented-LLM unit, writes state.

        Takes supplier_sku and title from the shared listing state; returns a
        partial dict with price_cents so LangGraph can merge it back.
        The _agent kwarg is the seam used in tests to inject a fake (no API key).
        """
        _agent = _agent or agent
        result = _agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Set a listed price for {state['title']} "
                            f"(SKU {state['supplier_sku']}). "
                            "Use lookup_floor_price to check the MAP floor "
                            "and price at least 5 % above it. "
                            "Reply with only the integer price in cents."
                        ),
                    }
                ]
            }
        )
        price_cents: int = result["price_cents"]
        return {"price_cents": price_cents}
    ```

=== "OpenAI Responses API"

    ```python
    def price_node(state: ListingState, _client: Any = None) -> dict:
        """One graph node: reads state, runs the augmented-LLM unit, writes state.

        OpenAI Responses API variant. The _client kwarg is injectable for offline
        testing without an API key.
        """
        client = _client or OpenAI()
        input_list = [
            {
                "role": "user",
                "content": (
                    f"Set a listed price for {state['title']} "
                    f"(SKU {state['supplier_sku']}). "
                    "Use lookup_floor_price to check the MAP floor "
                    "and price at least 5 % above it. "
                    "Reply with only the integer price in cents."
                ),
            }
        ]

        response = client.responses.create(
            model="gpt-5.5",
            input=input_list,
            tools=[FLOOR_PRICE_TOOL],
        )

        # Run the tool loop; cap prevents infinite spin if the model gets stuck.
        MAX_STEPS = 5
        steps = 0
        while any(item.type == "function_call" for item in response.output):
            steps += 1
            if steps > MAX_STEPS:
                raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
            input_list += response.output
            for item in response.output:
                if item.type == "function_call":
                    result = lookup_floor_price(**json.loads(item.arguments))
                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(result),
                        }
                    )
            response = client.responses.create(
                model="gpt-5.5",
                input=input_list,
                tools=[FLOOR_PRICE_TOOL],
            )

        price_cents = int(response.output_text.strip())
        return {"price_cents": price_cents}
    ```

=== "Anthropic Messages API"

    ```python
    def price_node(state: ListingState, _client: Any = None) -> dict:
        """One graph node: reads state, runs the augmented-LLM unit, writes state.

        Anthropic Messages API variant. The _client kwarg is injectable for offline
        testing without an API key.
        """
        client = _client or anthropic.Anthropic()
        messages = [
            {
                "role": "user",
                "content": (
                    f"Set a listed price for {state['title']} "
                    f"(SKU {state['supplier_sku']}). "
                    "Use lookup_floor_price to check the MAP floor "
                    "and price at least 5 % above it. "
                    "Reply with only the integer price in cents."
                ),
            }
        ]

        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=64,
            tools=[FLOOR_PRICE_TOOL],
            messages=messages,
        )

        # Run the tool loop; cap prevents infinite spin if the model gets stuck.
        MAX_STEPS = 5
        steps = 0
        while reply.stop_reason == "tool_use":
            steps += 1
            if steps > MAX_STEPS:
                raise RuntimeError("tool loop hit MAX_STEPS; the model may be stuck")
            messages.append({"role": "assistant", "content": reply.content})
            results = []
            for block in reply.content:
                if block.type == "tool_use":
                    output = lookup_floor_price(**block.input)
                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(output),
                        }
                    )
            messages.append({"role": "user", "content": results})
            reply = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=64,
                tools=[FLOOR_PRICE_TOOL],
                messages=messages,
            )

        price_cents = int(reply.content[0].text.strip())
        return {"price_cents": price_cents}
    ```

> **In the companion repo.** `listing-studio/augmented_llm/` holds the state TypedDict, the MAP-floor tool, and all three provider variants of `price_node`. The tool logic is unit-tested offline; the illustration files are compile-checked.

## 4. Gotchas

The unit is simple enough that its costs hide in plain sight. Three are worth naming before you build a pipeline of these.

**Every tool schema rides in the window, on every call.** The tool's name, description, and parameter schema are sent to the model each time the node runs, and they count against the context budget twice: once in tokens and dollars, once in the model's attention. One tool is free in practice. Ten tools, each with a paragraph of description, is a tax you pay on every step whether the model uses them or not, and it is a common cause of a node that quietly gets slower and dumber as it grows. Keep the unit's tool set to what this step actually needs, and see [1.5 Context Engineering](context-engineering.md) for the budget and [2.1 Tool Use](../the-unit/tool-use.md) for trimming the schema itself.

**The tool loop needs a cap, and the cap should fail loud.** A model that misreads its tool results can call the same tool again, and again, and a loop with no ceiling will burn calls until something else kills it. The `MAX_STEPS` guard in the node above is not decoration; it converts a silent, expensive spin into a raised error you can see and alert on. Pick the ceiling deliberately and raise on it rather than returning a half-finished result, which is the pattern this gotcha feeds in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md).

**State contract drift is the failure that doesn't show up in this chapter.** A single node is honest because the contract is right there in the `TypedDict`. The risk arrives when you have a dozen nodes and one of them starts writing a key another never reads, or renames a field, or leaves `price_cents` `None` on a path a downstream node assumes is set. The schema documents the shape but does not enforce that producers and consumers agree on meaning; that agreement is a thing you maintain. The depth lives in [5.1 State, Not Memory](../knowledge/state-not-memory.md); the warning here is that the unit looks safer in isolation than a graph of units will be.

## 5. In short

Default to the augmented unit whenever a step has to act on the world or hand a result to code: a model call, one or more tools the model may choose to invoke, and a typed state object the node reads and writes. Keep the tool set minimal so the schema does not tax every call, cap any tool loop so a stuck model fails loud, and treat the state contract as something you maintain across nodes, not something the schema guarantees. When a step needs none of that, a bare model call is the simpler and correct choice; do not reach for the unit out of habit. Build this one well and the rest of the reference is arrangements of it: chain them, fan them out, loop one against another, and the patterns in Part III fall out of the same atom.

## Sources

[^anthropic]: Anthropic, "Building Effective Agents" (19 Dec 2024). Names the **augmented LLM** as the basic building block of agentic systems: "The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory." Recommends building from simple, composable patterns. Quote and date verified against the published article. <https://www.anthropic.com/research/building-effective-agents>
[^langgraph]: LangGraph Graph API overview (LangChain docs). The state-graph runtime model this chapter assumes: nodes are functions that take the current state and return a partial update, state carries a schema with reducers, and edges sequence the nodes. Cited as one concrete instance of the node-on-a-graph substrate, not the only framework. The `create_agent` factory used in the LangGraph tab lives in the `langchain` package (<https://reference.langchain.com/python/langchain/agents/factory/create_agent>); the call surface is verified against the version pinned in `listing-studio/pyproject.toml`. <https://docs.langchain.com/oss/python/langgraph/graph-api>

## See also

- [2.1 Tool Use](../the-unit/tool-use.md) for a full treatment of the tool mechanism, the loop, and the guardrails the unit only sketches here.
- [2.2 Structured Output](../the-unit/structured-output.md) for the typed contract on the model's result, the load-bearing partner to tool use.
- [1.2 Who Decides?](who-decides.md) for the litmus test this chapter grounds: the unit is the first place the model actually decides.
- [1.5 Context Engineering](context-engineering.md) for why every tool schema and retrieved chunk the unit carries taxes the window.
- [5.1 State, Not Memory](../knowledge/state-not-memory.md) for the substrate in depth: reducers, persistence, and the state-versus-memory distinction this chapter defers.
- [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md) and [5.3 Memory](../knowledge/real-memory.md) for the optional augmentations, taught where they are load-bearing.

# 5.2 Retrieval (RAG)

*Look it up before you answer. Your code, or the model through a tool, searches a corpus you own and the best passages go into the prompt, so the answer can only be as good as what the search returned.*

*Also called: retrieval-augmented generation, RAG, knowledge-base retrieval, grounding (the broader vendor term), agentic RAG or agentic search (when the model runs the search), semantic or vector search (one kind of retrieval, often used as a synonym).*

## Why you'd reach for it

A merchant types *"what does error LST-4012 mean?"* into the merchant helpdesk assistant, and the assistant explains, fluently and at length, how to fix a listing title that broke the style rules. The page that answers the question exists. It sits in the assistant's own document index, one line long: the daily listing limit was reached, try again after midnight UTC. The search never returned it. An embedding (a vector that places text by meaning) often has little grip on an opaque code like `LST-4012`, so the nearest neighbours were other pages that talk about listings and errors. The model wrote a plausible answer from the passages it was handed.

A model knows nothing about your private documents, your current policies or yesterday's changes, so you fetch the relevant text at question time and put it in the prompt. From that moment the search sets the ceiling. If the right passage is missing, ranked too low, or crowded out of the window, no prompt and no model upgrade gets it back, and the model often does not flag the gap; it answers from whatever it was given. Barnett and colleagues, drawing on three case studies of RAG systems, list seven failure points, and the first three (the content is missing, the right document is not ranked high enough, the document is retrieved but does not make it into the context) all happen before the model writes a word.[^barnett]

So when a RAG answer is wrong, suspect the search first. Whether your code retrieves up front or the model searches through a tool, answer quality and tenant safety (each merchant sees only its own documents) are bounded by what the search returns, which means you build, measure and secure the search before you touch the prompt.

In the helpdesk above, a lexical search would have found `LST-4012`, and merging its ranking with the embedding ranking keeps the paraphrase matches. That is a few dozen lines of code, and a small labelled test set with one error-code query would have caught the miss before a merchant did.

Reach for retrieval when:

- **The corpus is too big or changes too often to live in the prompt.** Policy docs, a catalog, a ticket history.
- **Answers must point at a source.** A support reply that quotes the refund policy and names the page.
- **Different users may see different documents.** Each merchant's private docs.
- **The facts postdate the model's training.** Tuesday's price change.

If the whole corpus fits in the window and rarely changes, skip the index: put it in the prompt and cache it, which is Anthropic's own advice for small knowledge bases.[^contextual]

## What it actually is

Retrieval-augmented generation (RAG) is a search step wired to a model call: given a question, search a corpus you own, put the top few passages into the prompt, and have the model answer from them, ideally naming the passage it used. Lewis and colleagues named the pattern in 2020, pairing a generator with a dense index over Wikipedia.[^lewis]

![Two lanes run from a question to an answer through the same large search box. In classic RAG, rectangles for your code embed the question, search and fill a template before a rounded model box answers. In agentic retrieval, a rounded model box writes the query, calls the search box (tenant filter, lexical and dense scoring, rank fusion, a result cap) and may loop back to search again; a found-nothing exit returns a structured empty result.](retrieval-rag-two-lanes.svg)

The two wirings differ in who decides. In **classic RAG**, your code runs the same lookup on every question: embed it, fetch the top k chunks (the k best-scoring passages), fill a template, call the model. Structurally that is a search engine feeding a template. In **agentic retrieval**, the search becomes a tool the model calls ([2.1 Tool Use](../the-unit/tool-use.md)): it decides whether to search, writes its own query, reads the results, and searches again or stops. Anthropic's augmented LLM describes this: a model generating its own search queries.[^bea] Your code still owns everything inside the tool: which documents this user may see, how results are ranked, how many come back, and how many searches a turn may run ([2.5 The Agent Loop](../the-unit/the-agent-loop.md) and [2.6 The Harness](../the-unit/the-harness.md) cover the caps).

Claude Code is an agentic variant you can watch: it loads its project instructions file up front and then explores with glob and grep on demand instead of querying a pre-built embedding index. Anthropic names the cost: runtime exploration is slower than retrieving pre-computed data.[^context-eng]

**Maturity: Standard** for grounding a model in a corpus too large or too volatile for the window. The pipeline dates to 2020, and its parts (lexical search, dense search, offline relevance metrics) are older still. Search wrapped as a tool is **Established**, for the two reasons above. Autonomous multi-step query planning, including models trained with reinforcement learning to interleave reasoning with search, is **Emerging**; the research is active and the production record is thin.[^survey][^search-r1] The claim that long context makes retrieval unnecessary is **Contested**.[^li] GraphRAG, which builds a graph of entities and community summaries to answer corpus-wide questions such as "what are the main themes?", is an Emerging variant for a question shape plain top-k handles poorly.[^graphrag]

Two neighbours get confused with this. [5.1 State, Not Memory](state-not-memory.md) holds the facts of the current run; retrieval reaches into a corpus that outlives any run. [5.3 Memory](real-memory.md) covers what an agent writes and later recalls about users and episodes; the semantic knowledge base, documents people wrote that the agent searches, belongs here.

## How to do it

Build the search before you wire it to anything. Four choices decide most of its quality: how you cut documents into chunks, how you score them, how you rank, and what you filter before ranking.

**Chunking.** Chunk size and boundaries change recall. A chunk that is too large carries several topics, so its embedding matches none of them well; one that is too small splits the answer across chunks. Cutting on headings or paragraphs with a little overlap is a common starting point; then measure. A chunk also loses context when it is cut from its document: "the fee is refundable within 14 days" no longer says which fee. Anthropic's contextual retrieval prepends a short model-written note to each chunk before indexing, with prompt caching to keep the cost down. Treat it as Emerging and test it on your corpus.[^contextual] Parsing source files into clean text comes first and is [6.1 Ingestion](../io-boundary/getting-the-mess-in.md)'s job.

**Scoring, lexical and dense.** A lexical scorer (BM25 in production, which weights rare words above common ones) matches the words in the query. It is precise on exact strings like SKUs and error codes and tends to miss paraphrase. A dense scorer compares embeddings; it finds paraphrase and blurs exact strings. On the BEIR benchmark, BM25 held up as a strong baseline across domains where several dense retrievers trained on one dataset did not.[^beir] The companion code uses tiny stand-ins for both, so the failure modes are visible without a vector database. A `Chunk` is a pydantic model with an `id` and a `text`, and `CORPUS` is the list of seven helpdesk chunks:

```python
import math
import re
from collections import Counter

from .corpus import Chunk

# Stand-in for an embedding model: words that mean the same thing share a concept.
CONCEPTS = {
    "refund": "money", "money": "money", "back": "money", "subscription": "money",
    "plan": "money", "fee": "money",
    "invoice": "invoice", "invoices": "invoice", "copy": "invoice",
    "rejected": "reject", "turned": "reject", "down": "reject",
    "photo": "image", "photos": "image", "pixels": "image", "size": "image",
    "password": "login", "login": "login", "credentials": "login", "forgot": "login",
    "teammate": "team", "colleague": "team", "invite": "team", "access": "team",
}

STOPWORDS = {
    "a", "an", "the", "of", "to", "my", "i", "is", "on", "in", "and", "for", "can",
    "do", "how", "was", "why", "where", "get", "from", "with", "or", "at", "your", "you",
}


def tokens(text: str) -> list[str]:
    """Lowercase words and numbers, stopwords dropped."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def lexical_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    """Exact-word overlap: precise on literal terms, blind to paraphrase."""
    q = set(tokens(query))
    return {c.id: float(len(q & set(tokens(c.text)))) for c in chunks}


def _vec(text: str) -> Counter:
    return Counter(CONCEPTS[t] for t in tokens(text) if t in CONCEPTS)


def dense_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    """Cosine over concept counts: finds paraphrase, blurs exact terms."""
    q = _vec(query)
    out = {}
    for c in chunks:
        d = _vec(c.text)
        dot = sum(q[k] * d[k] for k in q)
        norm = math.sqrt(sum(v * v for v in q.values())) * math.sqrt(sum(v * v for v in d.values()))
        out[c.id] = dot / norm if norm else 0.0
    return out
```

The dense stand-in maps words to hand-picked concepts and takes the cosine (how closely the two count vectors point the same way); a real system calls an embedding model at that point. Each scorer returns a score per chunk id. In the toy, zero means no match; a real embedding scores every chunk, so you set a cutoff.

**Ranking by fused rank.** Run both scorers and merge their rankings. Their scores live on different scales, so adding them tells you nothing. Reciprocal rank fusion (RRF) sidesteps the scales by giving each chunk a vote of 1/(k + rank) from every list it appears in and sorting by the total. Here k is a smoothing constant, unrelated to the top-k cutoff; Cormack and colleagues fixed it at 60 in a pilot and kept it there:[^rrf]

```python
def rank(scores: dict[str, float]) -> list[str]:
    """Ids best-first; a zero score means no match and is dropped."""
    return [i for i, s in sorted(scores.items(), key=lambda kv: -kv[1]) if s > 0]


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal rank fusion: each list votes 1/(k + rank). Scores never mix."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for position, chunk_id in enumerate(ranking, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (k + position)
    return sorted(fused, key=lambda i: -fused[i])
```

A chunk ranked first by one scorer and absent from the other keeps a strong vote; in this fixture that is what rescues the `LST-4012` query. Reranking is the next step up: retrieve wide (dozens of candidates from the fused list), score each one against the query with a cross-encoder (a model that reads query and passage together and scores the pair) or an LLM, and keep the best few. BEIR found rerankers among the strongest zero-shot approaches, at a much higher compute cost per query.[^beir] The companion code stops at fusion.

**Query and filter.** A conversational follow-up such as *"what about the annual plan?"* retrieves noise when embedded raw, because its subject is three turns back. Rewriting it into a standalone question before searching is a common fix.[^ma] Filters for tenant, category or access rights go before ranking, as a pre-filter. Filter after you take the top k (a post-filter) and a merchant whose documents all ranked just below the cutoff gets nothing back.

Then hand the search to the model as a tool whose contract makes "nothing found" a result:

```python
class Retrieval(BaseModel):
    query: str
    found: bool
    chunks: list[Chunk]
    note: str = ""


def search_docs(query: str, k: int = 3) -> Retrieval:
    """Hybrid search over the helpdesk docs. Empty is a result, not a guess."""
    ids = rrf([rank(lexical_scores(query, CORPUS)), rank(dense_scores(query, CORPUS))])[:k]
    by_id = {c.id: c for c in CORPUS}
    if not ids:
        return Retrieval(query=query, found=False, chunks=[],
                         note="No policy matches. Say so; do not answer from memory.")
    return Retrieval(query=query, found=True, chunks=[by_id[i] for i in ids])
```

Keep the `found=False` branch. An empty string invites the model to answer from memory; a structured empty result with a note tells it what to do instead. `found=True` only means candidates: *"what is the password policy for Canada?"* returns the password-reset page, which cannot answer it, so the model must still check support.

One illustrative run of the agentic version over the companion corpus (the tests check the retrieval steps; the model's steps are illustrative):

1. A merchant asks *"what does error LST-4012 mean?"* The model, offered `search_docs`, calls it with the query `LST-4012`.
2. Your code runs both scorers. The lexical scorer matches the tokens `lst` and `4012` in the error page. The dense stand-in returns nothing, because neither token maps to a concept; a real embedding would likely return the wrong pages instead.
3. RRF fuses the two lists. The lexical hit is the only candidate, and `search_docs` returns `found=true` with the `error-lst-4012` chunk.
4. The model answers from that chunk (the daily listing limit was reached; try again after midnight UTC) and names the page.
5. The merchant asks *"what is the shipping rate to Canada?"* Neither scorer matches, the tool returns `found=false` with its note, and the model should say the docs do not cover it. That is model behaviour, so put the case in your evaluation set.

The scale-up is from one corpus to many tenants. The search takes the caller's tenant from your session, never from the model's arguments, and filters before scoring, so the model never chooses whose documents it reads. The companion corpus has one tenant and does not implement this filter.

> **In the companion repo.** [`listing-studio/retrieval/`](https://github.com/AbhiramDwivedi/agentic-engineering/tree/main/listing-studio/retrieval) holds the toy scorers, the fusion, the tool and `LABELED_QUERIES`, a fixture of eight queries each paired with its answering chunk; `tests/test_retrieval.py` checks the structured empty result and the recall figures quoted under Evaluating it.

#### Wiring it to a provider

All three tabs wrap the same `search_docs` and return its result as JSON, so the model sees `found` and `note`. The raw-SDK tabs send back one result per tool call and loop, with a cap, until the model stops searching. They compile, but no test calls the real APIs.

=== "LangGraph"

    ```python
    @tool("search_docs")
    def search_docs_tool(query: str) -> str:
        """Search the merchant helpdesk policy docs."""
        return search_docs(query).model_dump_json()


    agent = create_agent(
        "openai:gpt-6.2-sol",
        tools=[search_docs_tool],
        system_prompt="Answer only from search_docs results. If found is false, say you don't know.",
    )
    ```

=== "OpenAI Responses API"

    ```python
    SEARCH_TOOL = {
        "type": "function",
        "name": "search_docs",
        "description": "Search the merchant helpdesk policy docs.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    }


    def answer(question: str, max_searches: int = 3) -> str:
        input_items = [{"role": "user", "content": question}]
        response = client.responses.create(model="gpt-6.2-sol", input=input_items, tools=[SEARCH_TOOL])
        for _ in range(max_searches):
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                break  # the model answered without (another) search
            input_items += response.output  # keep every item, reasoning included
            for call in calls:
                result = search_docs(**json.loads(call.arguments))
                input_items.append({"type": "function_call_output", "call_id": call.call_id,
                                    "output": result.model_dump_json()})
            response = client.responses.create(model="gpt-6.2-sol", input=input_items, tools=[SEARCH_TOOL])
        return response.output_text
    ```

=== "Anthropic Messages API"

    ```python
    SEARCH_TOOL = {
        "name": "search_docs",
        "description": "Search the merchant helpdesk policy docs.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    }


    def answer(question: str, max_searches: int = 3) -> str:
        messages = [{"role": "user", "content": question}]
        response = client.messages.create(
            model="claude-sonnet-5-5", max_tokens=1024, tools=[SEARCH_TOOL], messages=messages
        )
        for _ in range(max_searches):
            if response.stop_reason != "tool_use":
                break  # the model answered without (another) search
            results = [
                {"type": "tool_result", "tool_use_id": block.id,
                 "content": search_docs(**block.input).model_dump_json()}
                for block in response.content if block.type == "tool_use"  # one result per call
            ]
            messages += [{"role": "assistant", "content": response.content},
                         {"role": "user", "content": results}]
            response = client.messages.create(
                model="claude-sonnet-5-5", max_tokens=1024, tools=[SEARCH_TOOL], messages=messages
            )
        return "".join(block.text for block in response.content if block.type == "text")
    ```

## Security & trust

The model reads retrieved text like the rest of the prompt, so whatever is in your index is untrusted input. The first risk is leaks across users. A shared index with no access partitioning lets one merchant's question retrieve another merchant's private policy. OWASP's LLM08 entry describes this leak in multi-tenant vector stores, and the pre-filter above is Standard practice against it.[^owasp] Where the caller's identity comes from is [8.5 Locks, PII & Identity](../production/locks-pii-identity.md).

The second is poisoning and injection: whoever can write to the corpus can steer the answers. PoisonedRAG reports around 90% attack success from five crafted texts per target question injected into a knowledge base of millions, on its own test setup.[^poisonedrag] The public incidents ran through retrieval too. In August 2024 PromptArmor showed a message posted in a public Slack channel, retrieved alongside a secret from a private one, making Slack AI render a link that carried the secret out.[^slack] EchoLeak (CVE-2025-32711) used a crafted email, retrieved by Microsoft 365 Copilot, to exfiltrate data without a click from the victim.[^echoleak] Defenses against poisoning and injection are Contested; [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md) covers the mechanism and what partially works.

## Evaluating it

Measure the search apart from the answer, because the two fail for different reasons and need different fixes. Build a set of labelled queries, each paired with the chunk that answers it, and compute recall@k, the share of queries whose answering chunk lands in the top k:

```python
def recall_at_k(retrieve: Callable[[str], list[str]], k: int = 3) -> float:
    """Share of labeled queries whose answering chunk appears in the top k."""
    hits = sum(1 for query, want in LABELED_QUERIES if want in retrieve(query)[:k])
    return hits / len(LABELED_QUERIES)
```

On the companion fixture, at the tool's default of k=3, recall@3 is 5/8 for the lexical scorer, 7/8 for the dense stand-in and 8/8 for the fused ranking. These are toy figures from a hand-built concept map; they show each scorer's blind spot (dense misses `LST-4012`, lexical misses *"give a colleague access"*), not real-world recall. Offline relevance metrics like this one are long-standing retrieval practice; BEIR is built on them.[^beir]

Then evaluate generation on the queries where retrieval succeeded: does the answer stick to the retrieved passages (faithfulness), and does it answer the question? LLM-judged metrics such as RAGAS score these without hand-written reference answers. They are Emerging, and the judge needs checking in its own right ([4.2 Evaluation](../craft/proving-it-works.md)).[^ragas] When a query fails, Barnett's seven failure points make a workable triage list: missing content, missed top-ranked documents, not in context, not extracted, wrong format, incorrect specificity, incomplete.[^barnett] The first three send you to the search, the rest to the prompt and the model. Keep end-to-end cases as well: questions the docs cannot answer, and ones the model should answer without searching.

## Gotchas

**Long context as a replacement.** Li and colleagues found that long-context models beat RAG on average when given enough resources, that RAG cost far less, and that routing each query to one or the other kept most of the accuracy at a fraction of the cost.[^li] Long windows also use information in the middle of the context worse than information at either end.[^lost-middle] Measure both on your own queries before you route. Routing between the two is [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md), and the spend is [8.4 Controlling Cost](../production/controlling-cost.md).

**Over-retrieval.** Raising k feels safe and dilutes the window: more distractors, more tokens, and the relevant passage pushed toward the middle where it is used least.[^lost-middle] Rerank and keep a few.

**Citations that do not support the claim.** The right passage in context does not guarantee a faithful citation. The ALCE benchmark found that model-generated citations often fail to fully support the statements they are attached to.[^alce] Check citations against the cited passage; groundedness checks are part of [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md).

**A stale or drifting index.** Deleted documents still come back, access changes never reach the index, and an index built with an embedding model you can no longer call has to be re-embedded in full before you can switch. These are pipeline problems, and freshness belongs to [6.1 Ingestion](../io-boundary/getting-the-mess-in.md).

**The cost of letting the model search.** Each extra search adds latency and tokens, and dead-end results stay in the window, spending context the answer needed. Cap searches per turn and stop on a structured empty result ([2.5 The Agent Loop](../the-unit/the-agent-loop.md)).

## In short

Start with the cheapest thing that answers. If the corpus fits, put it in the prompt and cache it. When it does not, build the search as a system you own: chunk on the document's structure, score lexically and densely, fuse by rank, filter by tenant before ranking, and return an explicit empty result. Label a few dozen real queries and track recall@k before you tune anything downstream. Hand the search to the model as a tool when questions need follow-up searches, and keep ranking and caps in your code. Treat everything retrieved as untrusted.

<small class="chapter-meta">**Maturity: Standard** (grounding over a corpus too large for the window; search as a tool is Established, multi-step search planning Emerging, long context versus RAG Contested) · *Who decides:* your code (the classic pipeline) / the model (search as a tool) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^lewis]: Lewis, P. et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020; arXiv 2020-05-22). The original RAG formulation: a pretrained generator paired with a dense retriever over a Wikipedia index. <https://arxiv.org/abs/2005.11401>
[^barnett]: Barnett, S. et al., "Seven Failure Points When Engineering a Retrieval Augmented Generation System" (arXiv 2024-01-11). The seven failure points, drawn from case studies of RAG systems. <https://arxiv.org/abs/2401.05856>
[^bea]: Anthropic, "Building Effective Agents" (2024-12-19). The augmented LLM (retrieval, tools, memory) and models generating their own search queries. <https://www.anthropic.com/research/building-effective-agents>
[^context-eng]: Anthropic, "Effective context engineering for AI agents" (2025-09-29). Just-in-time retrieval; Claude Code loading CLAUDE.md up front and using glob and grep on demand; runtime exploration being slower than retrieving pre-computed data. <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
[^survey]: Singh, A. et al., "Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG" (arXiv 2025-01-15). A survey and taxonomy of agentic RAG variants. <https://arxiv.org/abs/2501.09136>
[^search-r1]: Jin, B. et al., "Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning" (arXiv 2025-03). Cited as an example of RL-trained search, not as a method this chapter teaches. <https://arxiv.org/abs/2503.09516>
[^li]: Li, Z. et al., "Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach" (EMNLP 2024 industry track). Long context ahead on average when resourced, RAG far cheaper, and routing between them (Self-Route). <https://arxiv.org/abs/2407.16833>
[^contextual]: Anthropic, "Introducing Contextual Retrieval" (2024-09-19). Model-written chunk context, prompt caching to amortize indexing, reranking on top of hybrid search, and the advice to put a small knowledge base straight into the prompt. The improvement figures are the vendor's own, on its own evaluation, and are not reproduced here. <https://www.anthropic.com/news/contextual-retrieval>
[^beir]: Thakur, N. et al., "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models" (NeurIPS 2021 Datasets and Benchmarks; arXiv 2021-04). BM25 as a robust zero-shot baseline, rerankers strong at higher compute cost, evaluation by offline relevance metrics. <https://arxiv.org/abs/2104.08663>
[^ma]: Ma, X. et al., "Query Rewriting for Retrieval-Augmented Large Language Models" (EMNLP 2023; arXiv 2023-05-23). <https://arxiv.org/abs/2305.14283>
[^owasp]: OWASP, "LLM08:2025 Vector and Embedding Weaknesses," Top 10 for LLM Applications 2025. Unauthorized access and context leakage in multi-tenant vector stores, and data poisoning. <https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/>
[^lost-middle]: Liu, N. F. et al., "Lost in the Middle: How Language Models Use Long Contexts" (TACL 2024; arXiv 2023-07-06). <https://arxiv.org/abs/2307.03172>
[^alce]: Gao, T. et al., "Enabling Large Language Models to Generate Text with Citations" (ALCE; EMNLP 2023; arXiv 2023-05-24). <https://arxiv.org/abs/2305.14627>
[^ragas]: Es, S. et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation" (arXiv 2023-09). Reference-free faithfulness and relevance metrics. <https://arxiv.org/abs/2309.15217>
[^poisonedrag]: Zou, W. et al., "PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models" (arXiv 2024-02). The roughly 90% success rate holds for the paper's own setup only. <https://arxiv.org/abs/2402.07867>
[^slack]: PromptArmor, "Data Exfiltration from Slack AI via Indirect Prompt Injection" (August 2024). <https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via>
[^echoleak]: Reddy, P. and Gujral, A., "EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System" (arXiv 2025-09-06). CVE-2025-32711 in Microsoft 365 Copilot. <https://arxiv.org/abs/2509.10540>
[^rrf]: Cormack, G. V., Clarke, C. L. A. and Büttcher, S., "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (SIGIR 2009). The RRF formula, with k=60 fixed during a pilot investigation. <https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf>
[^graphrag]: Edge, D. et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization" (arXiv 2024-04). <https://arxiv.org/abs/2404.16130>

## See also

- [1.5 Context Engineering](../foundations/context-engineering.md): retrieval is one supplier to the window, and this chapter assumes its budget discipline.
- [2.1 Tool Use](../the-unit/tool-use.md): the mechanism that turns the search into something the model calls.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md): the stop conditions and caps a searching model needs.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md): routing queries between long context and retrieval.
- [4.2 Evaluation](../craft/proving-it-works.md): judge mechanics for the generation half of the evaluation.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md): why retrieved text is an attack surface, in depth.
- [5.1 State, Not Memory](state-not-memory.md): the facts of the current run, as opposed to a corpus that outlives it.
- [5.3 Memory](real-memory.md): what the agent writes and recalls about users and episodes.
- [6.1 Ingestion](../io-boundary/getting-the-mess-in.md): parsing, cleaning and keeping the index fresh.
- [8.5 Locks, PII & Identity](../production/locks-pii-identity.md): the identity your retrieval filter enforces.

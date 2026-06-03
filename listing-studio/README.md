# Listing Studio — the companion code

This is the **carrier**: a fictional commerce platform whose code earns every chapter of the
reference. Code samples in the docs are included from the files here (via MkDocs snippet
includes), so the prose in the site can never drift from code that actually runs.

> **Confidentiality:** this is a public, invented system. It is *not* the private production
> code it was inspired by. Everything here is safe to publish.

## Surfaces

| Surface | Use-case family | Status |
|---|---|---|
| **Listing Studio** (pipeline) | batch document → merchandised listing | the primary anchor |
| **Shopper assistant** | conversational agent (memory, HITL) | planned |
| **Merchant helpdesk** | RAG over policies/docs | planned |
| **Repricing agent** | true autonomy (the one real agent loop) | planned |
| **Category-research agent** | research fan-out + synthesis | planned |

## Status

Scaffolding. The companion code is built chapter by chapter, alongside the v1 docs. The first
target is the nine-step pipeline:

`ingest → clarify → categorize → write copy → content blocks → price → assemble launch package
→ brand-voice polish → publish`

Built once in LangGraph (matching the real stack it's recast from); other frameworks appear as
prose asides and one bake-off, not as parallel maintained codebases.

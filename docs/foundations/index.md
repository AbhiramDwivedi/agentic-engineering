# Part I: Foundations

The pure, durable core, read these first. What agentic engineering is, the litmus test applied to everything later, where your system sits on the workflow-to-agent spectrum, the augmented LLM as the base unit, context engineering, and the build-vs-buy question.

## The running example: Listing Studio

The patterns in this reference are easier to trust when you watch them crowd into one real-shaped system, so the whole book teaches through a single fictional commerce platform, **Listing Studio**. Its main surface is a batch pipeline: a merchandiser uploads a supplier's spreadsheet and a folder of photos, clicks *Generate listing*, and roughly thirty model calls fire across nine steps to turn a raw supplier feed into a finished storefront listing.

`ingest → clarify → categorize → write copy → content blocks → price → assemble launch package → brand-voice polish → publish`

The same company runs a few sibling surfaces (a shopper assistant, a merchant helpdesk, a repricing agent, a category-research agent) that the reference reaches for only when a batch pipeline cannot make the point. The patterns are drawn from a real production system, recast in this commerce setting so the ideas travel without the domain baggage. **[How to Read This](../about/how-to-read.md)** gives the full tour and the shape every chapter shares.

## In this part

- **1.1 It's Still Engineering**
- **1.2 Who Decides?**
- **1.3 Workflow or Agent?**
- **1.4 The Augmented LLM**
- **1.5 Context Engineering**
- **1.6 Do You Even Need a Framework?**

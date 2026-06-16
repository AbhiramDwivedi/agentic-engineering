# The Carrier Bible: Listing Studio and its world

> **Why this exists:** every chapter draws its examples from one consistent world. A reference
> that invents a fresh example per chapter reads as assembled, not authored. This file is the
> single source of truth for that world. When you write a chapter, pull specifics from here. Do
> not invent new field names, personas, or numbers that contradict it. If the world needs to
> grow, grow it *here* first, then use it.

!!! warning "Numbers come from the code, not from imagination"
    Quantitative specifics (latencies, token counts, costs, pass rates) must come from running
    the companion code in `listing-studio/`, never invented. Until a number is measured, write
    qualitatively ("the slowest step", "a few cents a listing") and mark it for backfill. This
    rule is the whole project in miniature: we do not make up evidence.

---

## 1. The company

**Stockwell** is a commerce platform. Mid-market
merchants run their online storefronts on it: catalog, pricing, content, fulfilment hooks. It is
a SaaS product, multi-tenant, the kind of company with a few hundred engineers and real revenue,
not a hyperscaler and not a two-person startup. That scale is deliberate. It is the scale where
"a wrong answer costs money" is true but the team still has to be pragmatic about cost and
headcount, which is the scale most readers actually work at.

Stockwell ships several AI surfaces. The reference teaches through them. Only the first,
**Listing Studio**, is a close recast of a real production system, so only it carries first-hand
*From production* war stories. The others are built in the companion repo or reasoned about.

**The people** (use these roles in examples; do not invent new ones):

- **Maya, a merchandiser.** Stockwell's customer's employee. She onboards products and runs
  Listing Studio. The human in most pipeline stories.
- **A merchant.** Stockwell's paying customer, the business owner. Uses the helpdesk.
- **A shopper.** The merchant's customer. Uses the shopper assistant.
- **Devon, a platform engineer at Stockwell.** Builds and operates the AI surfaces. The "you" of
  most How-to sections.

**How the reference uses these people** (settled 2026-06-16; supersedes the placeholder note in
Settled choices). A reference is read one page at a time, landed on from search, so every name is a
pointer to a definition the reader may never have loaded. Artifacts are not: the Aldsworth desk, a
`supplier_sku`, `price_cents`, `draft → review` define themselves, and they carry the concreteness.
Names cost a lookup, so spend them carefully.

- **Devon is the second person.** In How-to and reference prose the platform engineer is *you* and
  *your code*, never "Devon" in the third person. Naming him beside "your code" makes two labels for
  one role. His first name belongs in the warmer distribution blog posts, not the chapters.
- **Name a human only where a human is in the mechanism:** a review gate, a person racing the agent
  for the same row. If the sentence still works with "your code" or "a person," the name is
  decoration; cut it.
- **Introduce by role on first mention, every page.** Prefer the role noun, which defines itself:
  "a merchandiser edits the same desk," not "Maya edits the same desk." Attach the name only when
  the person recurs on the page and the recurrence carries meaning ("Maya, a merchandiser, ...").

---

## 2. The data model

The object the pipeline builds is a **Listing**. Canonical fields (use these exact names in code
and prose):

| Field | Type | Notes |
|---|---|---|
| `supplier_sku` | string | the supplier's identifier; the join key on the raw feed |
| `gtin` | string? | barcode; often missing or malformed in the feed |
| `title` | string | merchandised product title |
| `attributes` | map | typed key-values: `height_range_in`, `weight_capacity_lbs`, `desktop_size_in`, `color`, ... |
| `category_path` | string | e.g. `office/desks/standing-desks` |
| `copy` | object | the written product page: `description`, `bullets[]` |
| `content_blocks` | list | page sections: hero, specs, FAQ, comparison |
| `price_cents` | int | the listed price |
| `compliance` | object | flags: `map_enforced`, `prop65`, `safety_claims[]` |
| `images` | list | `{role: hero|lifestyle|spec, url, alt}` |
| `launch_package` | object | the assembled deliverable: listing + email + ad copy |
| `status` | enum | `draft → review → published` |

---

## 3. Listing Studio: the nine-step pipeline

The flagship. Maya uploads a supplier's spreadsheet, drags in a folder of product photos and spec
sheets, and clicks **Generate listing**. Behind that one click, roughly **thirty model calls fire
across nine steps** (the exact count is a measured number, to be confirmed from the code). Each
step is a node on a shared state graph; each reads the current Listing, does its work, and hands a
more complete Listing to the next. A dashboard shows Maya live progress, and **nothing publishes
until every step has reported back**.

| # | Step | What it does | Pattern home |
|---|---|---|---|
| 1 | **ingest** | parse the spreadsheet, spec sheets, images into a draft Listing | ingestion, tool use |
| 2 | **clarify attributes** | find missing/ambiguous attributes, draft questions, grade them, loop | evaluator-optimizer |
| 3 | **categorize** | place it in the catalog taxonomy | structured output |
| 4 | **write copy** | draft `description` and `bullets` | prompt chaining |
| 5 | **content blocks** | build page sections, each from a specialist viewpoint | specialist panel |
| 6 | **price** | set `price_cents` within MAP and margin rules | tool use, guardrails |
| 7 | **assemble launch package** | fan out to write listing + email + ad copy in parallel | orchestrator-workers |
| 8 | **brand-voice polish** | rewrite everything to one voice, less robotic | the humanizer |
| 9 | **publish** | validate, write to the catalog, mark `published` | dispatch, observer |

The **front door** that maps the *Generate listing* event to this graph is the dispatcher (the
"router that isn't one"). The **dashboard** is the observer target on every step.

---

## 4. The hero example

Reuse one product across chapters so the reader builds familiarity.

**The Aldsworth dual-motor sit-stand desk**, from supplier *Northvale Furnishings*. It is a good
teaching object because it exercises everything at once and is mundane enough not to distract:

- **Attributes** that matter and are often missing or messy in the feed: `height_range_in`
  (25-50), `desktop_size_in` (60×30), `weight_capacity_lbs` (250), `motor` (dual), `presets` (4),
  `color` (walnut / white / black).
- **Compliance** with real teeth, even for furniture: a BIFMA stability/durability claim, a
  `weight_capacity_lbs` rating you must not overstate (a wrong number is a liability and a returns
  wave), pinch-point warnings, and a Prop 65 warning (formaldehyde in the MDF top). Plus
  `map_enforced` pricing, which is near-universal in this category.
- **Pricing** nuance: a minimum advertised price the model must not undercut, and margin rules.
- **Logistics**: assembly required, bulky/oversized shipping. These shape the copy and the price.
- **Images**: a hero shot, a lifestyle shot (a real office), and a spec sheet with the dimension
  diagram to read.

When a chapter needs a second product (to show variety), use **a kids' bunk bed** from the same
supplier: compliance-heavy in a different way (entrapment and guardrail rules), assembly-
intensive, bulky-shipping.

---

## 5. The sibling surfaces

Reach for these only when the pipeline cannot show the concept.

- **Shopper assistant.** A conversational agent on the storefront. A shopper asks "will this heat
  my 200 sq ft garage?" and it answers from the catalog. Teaches multi-turn, state vs. memory,
  human-in-the-loop. *Built in the companion repo.*
- **Merchant helpdesk.** A retrieval agent over Stockwell's policy and how-to docs. A merchant
  asks "how do I set a MAP rule?" Teaches RAG, semantic memory, grounding. *Built in the
  companion repo.*
- **Repricer.** An autonomous agent that watches competitor prices and adjusts within rules. It
  plans its own steps and acts. Teaches real autonomy, model-driven planning, blast-radius
  guardrails. *Built in the companion repo. The one genuinely autonomous loop.*
- **Category scout.** A research agent that studies a product category before a merchant stocks
  it. Teaches research fan-out and synthesis. *Reasoned / lightly built.*

The coding-agent archetype is referenced as an external category, not built into Stockwell.

---

## 6. The tech substrate

Generic on purpose (confidentiality: keep infra ordinary, drop fingerprints). The graph and nodes
run in **LangGraph** (matches the real stack we recast from). State persists in **Postgres**. Work
runs on an **async pool**. Models come through a **multi-provider** layer, so "swap the model" is a
config change. Example code defaults to **LangGraph** (the carrier's real stack), with the raw
OpenAI Responses API (`gpt-5.5`) and Anthropic Messages API (`claude-sonnet-4-6`) shown in
Material content tabs. No proprietary, identifying artifacts. Other frameworks appear as prose asides and
one bake-off, not as parallel maintained codebases.

---

## 7. The specialist panel personas

For step 5 (content blocks) and anywhere multi-persona reasoning appears, the three specialist
personas are commerce ones:

- **the SEO specialist**: discoverability, search terms, titles;
- **the pricing analyst**: margin, MAP, competitive position;
- **the compliance reviewer**: safety claims, required warnings, category rules.

They reason independently, then a reconcile step merges them.

---

## 8. Consistency rules

- One world, one set of names. Pull from this file; do not coin synonyms.
- Code identifiers match section 2 exactly.
- Numbers are measured from `listing-studio/`, never invented (see the warning up top).
- If a chapter needs a new specific, add it here first, then use it.
- People follow the usage policy in §1: Devon is *you*; introduce a named human by role on first
  mention; prefer the role noun; cut decorative names.

---

## Settled choices

1. **Company name:** **Stockwell** (decided 2026-06-03).
2. **Hero product:** the **Aldsworth dual-motor sit-stand desk** from Northvale Furnishings
   (decided 2026-06-03). Secondary product for variety: a kids' bunk bed.
3. **Persona first names:** Maya (merchandiser) / Devon (Stockwell platform engineer) are
   placeholders for warmth without identifying anyone. Change freely if better ones come up.

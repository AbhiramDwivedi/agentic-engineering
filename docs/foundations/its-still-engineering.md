# 1.1 It's Still Engineering

<small class="chapter-meta">**Maturity: n/a** (a framing chapter, not a technique) · *Grounding:* reflection on production experience</small>

*The thesis the rest of the reference rests on: building with agents is still engineering, most "agentic patterns" are familiar design patterns with a model dropped into one slot, and the way to tell the genuinely new ones apart is to ask who makes the decision.*

## Why you'd reach for it

A while ago I made a list of the agentic design patterns in a system I had built. A dozen of them. I was a little proud of the list.

Then I looked harder. One pattern I was about to file under "routing," a named entry in the workflow canon, turned out in my code to be a dictionary. The caller hands it an event label, it looks up a function, it calls that function. I had been writing that exact thing since the 2000s, long before anyone attached the word "agent" to it. A few of the others were retry loops and callbacks that happened to live inside an agent. The list was shorter than I thought.

Here is the cost of getting that wrong, and it is a leadership cost, not a vocabulary one. A dictionary lookup is deterministic: the same input gives the same output, you cover it with a unit test, and you can promise a stakeholder it behaves. A model making the same choice is non-deterministic: it is right most of the time, wrong some of the time in ways you cannot fully enumerate, and the only way to trust it is to measure it with evals and design for the failures. Those are different engineering disciplines with different costs, different test strategies, and different blast radii. When you call them by the same name, you hide exactly the risk a technical leader needs to see, and you budget for the wrong thing.

So the question worth asking is not "what are the agentic patterns?" It is narrower and more useful: of the patterns in front of you, which are genuinely new because a model is making a decision, and which are the ones you already know, with a model now sitting in one of the slots?

Reach for this framing when:

- you are evaluating a tool, a framework, or a vendor pitch that calls itself "agentic" and you need to know what is actually new;
- you are sizing the cost, the test strategy, or the risk of a system, and the answer depends on whether your code or a model owns each decision;
- you are deciding how much of a problem needs a model in the loop at all, and how much is ordinary software you already know how to build.

You do not need it when the system is small enough to hold in your head, or when nobody is selling you a label.

## What it actually is

The thesis is one sentence: **building with agents is still engineering.** Most of what gets sold as a new "agentic pattern" is an ordinary design pattern with a language model dropped into one slot. A few are genuinely new. The reference is the work of telling those apart and saying, for each, how proven it is and what the evidence is.

This is a defensible position, not a neutral fact, and it deserves to be argued rather than asserted. It is in honest dialogue with the framing the field has converged on. Three independent sources describe the same base unit and the same caution. Anthropic's "Building Effective Agents" draws the line between workflows, where "LLMs and tools are orchestrated through predefined code paths," and agents, where "LLMs dynamically direct their own processes and tool usage."[^1] Google's Antonio Gulli frames an agent as a goal-directed system that perceives its environment and acts to reach an objective, not a single-prompt responder.[^2] OpenAI's practical guide describes agents as systems that independently carry out tasks on a user's behalf.[^3] They differ in wording but agree on the shape, and on the caution: add complexity only when it demonstrably improves outcomes.[^1] A vocabulary list is not a system, though, and naming the patterns is not the same as knowing which ones changed anything. That gap is what this reference exists to close.

The deflation is the honest read of that shared framing, not a contradiction of it. The field gave us a useful vocabulary quickly. The next move, the one this reference makes, is to hold each pattern up to a single test and sort it.

The test is: **who makes the structural decision, the model or your code?** Sort a real pattern set that way and it falls into three groups, plus one honest exception:

- **Genuinely new, where the model decides.** It reaches for a tool, judges its own draft and loops, decides how many workers to spawn, picks which kind of expert to reason as. Nothing in the old toolbox made a judgment call in the middle of control flow. These do.
- **Just engineering, where your code decides.** A lookup that routes a request, a loop that retries on failure, a callback that fires when a step finishes. Useful, necessary, and not new. The routing-is-a-dictionary case is the one that started this whole exercise.
- **Features and coinages.** A model capability that gets miscalled a pattern, or a name someone invented for a local trick. Honest about what each actually is.

And one draw: prompt chaining, splitting a task into a sequence of steps. Your code controls the order, so by the test it is just a pipeline, an old idea. But you split the task because one model call could not hold it reliably. Old structure, new reason.

This chapter names that the three-way split exists and that the reference is organized around it. It does not run the test or sort the patterns here. The test itself, the worked sort of a real pattern set, and the full split table live in **[1.2 Who Decides?](who-decides.md)**, which owns the lens. Treat this chapter as the reason you would want such a test, and 1.2 as the test.

The patterns are drawn from a production system I work on, recast here in a commerce setting (a fictional platform called Listing Studio) so the ideas travel without the domain baggage; **[How to Read This](../about/how-to-read.md)** introduces that carrier and the shape every chapter shares.

## How the argument cashes out

A thesis has no runtime shape, so there is no diagram and no code here. What it has is a consequence: once you ask who decides, your engineering decisions change.

Take the price step in a product-listing pipeline. If a lookup table sets the price from a rules file, you test it the way you test any function: feed it inputs, assert the outputs, ship it with confidence. If instead a model proposes the price and your code checks it against the supplier's floor, you have a non-deterministic component in a path where a wrong number is a contract violation, and now you need evals over a range of products, a hard gate in code that the model cannot talk its way past, and a plan for the call that fails. Same step in the pipeline, two different cost and test profiles, and the only thing that changed is which one decides. Asking the question early is what lets you budget for the right one. (That price step is **[Tool Use](../the-unit/tool-use.md)**, the first genuinely-new pattern; the chapter shows the gate.)

This is also why the distinction is practical rather than pedantic, the stakes argument that **[1.2 Who Decides?](who-decides.md)** develops in full: mislabelling a deterministic component as an agentic one sets the wrong expectations for cost, failure, and testing, and a leader who budgets for a dictionary when they are actually shipping a model will be surprised in production. Name it correctly and you can plan for it.

The litmus test, the workflow-versus-agent spectrum, and the five named workflow patterns are the machinery this framing sets up, and each has its own chapter: **[1.2 Who Decides?](who-decides.md)** for the test, **[1.3 Workflow or Agent?](workflow-or-agent.md)** for the spectrum and the five workflows, **[1.4 The Augmented LLM](the-augmented-llm.md)** for the base unit they all build on, and **[1.6 Do You Even Need a Framework?](do-you-need-a-framework.md)** for the build-versus-buy call.

## The skeptical read

The framing has a flip side, and ignoring it would make the trust-map promise sound self-congratulatory rather than honest. If building with agents is still engineering, then a great deal of what is currently marketed as "agentic" is older or simpler than the marketing claims. The industry has a name for the practice: "agent washing," rebranding an LLM with a single API call, or a chatbot with a script, as an autonomous agent.

This is genuinely Contested territory, and the honest move is to be specific and generous rather than dismissive. The ambition behind the agent push is real and worth respecting: people are trying to get software to take useful action in the world, which is a hard and worthwhile goal. The skepticism is about the gap between the label and the substance, not about the goal. Gartner has flagged that gap directly, predicting a large share of agentic-AI projects will be scrapped before they mature and noting that only a small fraction of self-described agentic vendors deliver real autonomy.[^4] Those figures are directional and will move, so the finding is what matters, not a frozen number: a credible analyst house is on record that the label runs well ahead of the substance. Practitioner write-ups land in the same place, observing that many production "agents" are, on inspection, workflows or wrappers around a chatbot.[^5]

That gap is not a reason to disengage. It is the reason this reference exists. If you can tell which decision a model is actually making, you can tell agent from agent-washing on your own, without trusting the badge on the box.

## In short

Treat agentic engineering as engineering. When you meet a new "pattern," ask who makes the structural decision: if the model decides, take it seriously as something new and plan for its non-determinism with evals and gates; if your code decides, recognize the design pattern you already know and test it the way you always have. Do not let a label move a component into the wrong cost-and-risk bucket. The rest of this reference makes one promise in exchange for reading on: every technique is labelled by how proven it is, from Standard down to Contested, and every non-obvious claim cites its evidence, so you can tell signal from noise yourself. How those labels work is spelled out in **[How We Label](../about/how-we-label.md)**.

## Sources

[^1]: Anthropic, "Building Effective Agents" (2024-12-19). The workflow-versus-agent distinction ("LLMs and tools are orchestrated through predefined code paths" versus "LLMs dynamically direct their own processes and tool usage"), the augmented-LLM base unit, and the guidance to "add complexity only when it demonstrably improves outcomes." <https://www.anthropic.com/research/building-effective-agents>
[^2]: Antonio Gulli (Google), *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems* (Springer Nature, 2025; ISBN 9783032014016). The goal-directed definition of an agent: a system that perceives its environment and acts to reach a goal, not a single-prompt responder. Verify exact wording against the print edition before quoting. <https://link.springer.com/book/10.1007/978-3-032-01402-3>
[^3]: OpenAI, "A Practical Guide to Building Agents" (April 2025). Agents as systems that independently accomplish tasks on a user's behalf. <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>
[^4]: Gartner, "Over 40% of Agentic AI Projects Will Be Canceled by End of 2027" (newsroom, 2025-06-25), with the related "agent washing" framing. Figures are directional; cite the finding, not the number. <https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027>
[^5]: Practitioner accounts that many production "agents" are workflows or chatbot wrappers on inspection, corroborating the overclaim the deflation answers. See, for example, SDxCentral, "Was 2025 really the year of the AI agent?" <https://www.sdxcentral.com/analysis/was-2025-really-the-year-of-the-ai-agent/>

## See also

- **[1.2 Who Decides?](who-decides.md)** owns the litmus test this chapter only names: the "who decides?" question, the worked sort, the three-way split table, and why the distinction changes cost and risk.
- **[1.3 Workflow or Agent?](workflow-or-agent.md)** for the spectrum between predefined paths and model-directed control, and the five named workflow patterns.
- **[1.4 The Augmented LLM](the-augmented-llm.md)** for the base unit (model plus tools plus a contract) every pattern here builds on.
- **[1.6 Do You Even Need a Framework?](do-you-need-a-framework.md)** for the build-versus-buy decision once you know which decisions are the model's.
- **[How We Label](../about/how-we-label.md)** for the maturity lens and the evidence rules this reference promises.
- **[How to Read This](../about/how-to-read.md)** for the Listing Studio carrier and the shape every chapter shares.

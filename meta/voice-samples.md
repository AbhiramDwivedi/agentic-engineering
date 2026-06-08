# Voice samples

> Real prose from the references we want to read like. Feed this file to the writer and the
> editor on every chapter. The point is to pattern against actual sentences, not an abstract
> description of a register. Pair with `voice-and-style.md`.

## Martin Fowler (martinfowler.com)

Verbatim fragments:

- "What most appeals to me about the debt metaphor is how it frames how I think about how to deal with this cruft."
- "If I have a terrible area of the code base, one that's a nightmare to change, it's not a problem if I don't have to modify it."

What to copy:

- First person, and unembarrassed about it ("What most appeals to me", "If I have").
- Plain, slightly informal nouns for technical things: *cruft*, *a nightmare to change*. He does not
  reach for grand vocabulary.
- He states a position and the reason behind it, then stops. No flourish, no windup.

## trunkbaseddevelopment.com (Paul Hammant)

Verbatim:

- "A source-control branching model, where developers collaborate on code in a single branch called 'trunk' and resist any pressure to create other long-lived development branches."
- "They therefore avoid merge hell, do not break the build, and live happily ever after."
- "When individuals on a team are committing their changes to the trunk multiple times a day it becomes easy to satisfy the core requirement of Continuous Integration."

What to copy:

- Short, declarative, practical. State the practice, then the benefit, then move on.
- One dry, human touch per stretch ("merge hell", "live happily ever after"), never more.
- Credibility comes from specifics ("multiple times a day", "at least once every 24 hours"), not
  from adjectives.

## The register, in one line

A specific person explaining something to a competent colleague: first person where it helps,
concrete and a little informal, declarative, dry rather than punchy, and always more interested
in the fact than in the phrasing.

## Anti-samples (our own drafts, and the fix)

These are real lines this project shipped and had to cut. They are here so the same tell is
caught next time.

- **Manufactured antithesis.** "Tool use is how it stops talking and starts doing." / "an agent
  stops being a chatbot and gets the power to do harm." The "stops X and starts Y" shape sounds
  composed and says little. *Fix:* state the capability plainly. "A tool lets the model act on
  the real system."
- **Hollow signpost fragment.** "Pricing shows the gap." A three-word sentence that announces a
  point instead of making it. *Fix:* go straight to the concrete case. "Take pricing. You ask the
  model to set a price, and..."
- **The manufactured aphorism as a closer.** "The model may propose, your tool disposes." Cute,
  and it replaces a real sentence. *Fix:* say the rule. "Let the model propose the price; let your
  code decide whether it ships."
- **Balanced-for-effect closer.** "useful and unreliable at the same time, and the design has to
  answer for the second half." *Fix:* "These models are fluent enough that the unreliability is
  easy to miss. Design for it anyway."

# 8.6 Governance & Compliance

*The controls under the paperwork. The regimes keep asking your system the same few questions, and your code, never the model, holds the answers.*

## Why you'd reach for it

A customer asked Air Canada's website chatbot about a fare policy, got a wrong answer, and booked on the strength of it. When he claimed the refund the chatbot had promised, the airline argued, in effect, that the chatbot was responsible for its own words. The British Columbia Civil Resolution Tribunal disagreed and held the airline liable for negligent misrepresentation (a careless false statement that someone reasonably relied on), awarding CAD 812.02.[^1]

The award is small and the forum is a small-claims tribunal, so it settles no grand question of law. The tribunal applied ordinary negligent-misrepresentation law, and the chatbot being a model changed nothing. The same year the US Federal Trade Commission's Operation AI Comply, a batch of enforcement actions against deceptive AI claims, targeted DoNotPay, which had marketed "the world's first robot lawyer" without testing it; the proposed settlement order carried $193,000.[^2] Both cases ran on existing law: negligence, and deceptive advertising. Consumer protection law has no AI exemption, and the AI-specific regimes arrive on top of it.

Say the system ships, then an enterprise merchant's security review, a regulator's letter or an angry shopper arrives, and someone asks a plain question: which model wrote this, which prompt was live, who approved it, and did the person on the other end know they were talking to a machine? The answers exist only by accident. Traces were sampled and expired, prompts were edited in place, and the approval happened in a chat thread.

Put that in a product-listing pipeline, the kind that turns a supplier feed into storefront pages. A kids' bunk bed goes live with a claim about the height of the safety rail around the top bunk, which the model wrote and nobody checked against the spec sheet. A parent complains. You need to show who let the claim through and which model and prompt produced it. A trace store that keeps a sample of runs for a few weeks may never have kept that run, or may have deleted it before the complaint arrived.

The fix is a control plane: a small set of deterministic controls that your code runs beside the AI system, built once. Then you map whichever rule applies onto those controls, rather than building a compliance project per regulation.

You need it when:

- **The system acts or publishes** on behalf of the business: a listing goes live, a price changes, a customer gets an answer they will rely on.
- **A person talks to it** without necessarily knowing it is a model.
- **The use touches people's opportunities**, such as hiring, credit, or access to services, which is where the heavy regimes concentrate.
- **Someone outside will ask**: an enterprise buyer, an auditor, a regulator.

The counter-trigger: an internal prototype with no users and no actions needs an owner and an inventory entry, and nothing more. Building conformity machinery for it (the documentation and assessments that prove a system meets a rule) wastes the effort you will need for the system that does matter.

## What it actually is

Governance is the set of decisions an organisation can show it made about an AI system: what it is for, who may change it, what it may do, what gets recorded, and who can stop it. Compliance is the narrower act of showing that evidence to an outside party under a specific rule. The engineering is four controls, owned by your code: a classified inventory, a durable decision record, an enforceable override, and a user-facing disclosure. Regimes differ in dates, paperwork and penalties, and keep asking for those four.

![A rectangle labelled your code holds four numbered controls. Control 1, the inventory row, records owner, purpose, risk class, role, model, prompt and tools. A model box inside drafts a bunk-bed listing with a rail-height claim, the only decision the model makes. Control 3, the override, is a publish gate where a merchandiser cuts the claim. Control 4, a code-rendered label, reads "Written with AI, reviewed by a person." The gate writes control 2, the decision record: rec-000001 from the listing agent, and rec-000002, the correction pointing back at it. The model never touches the record. To the right, four regimes draw on the same four controls.](governance-and-compliance-control-plane.svg)

Structurally, none of this is new. Inventories, change control, audit logs and kill switches are what regulated software teams have run for decades, and your code makes every decision in the picture: the model writes the listing, and code decides whether it publishes, records who decided, and labels the result. Two things are new. Some actors in your log are models whose behaviour can change when a vendor ships a new version, so the record has to carry the model and prompt version or it explains nothing. And in an agent loop the model chooses the next action, so the record has to be written at each step the harness executes, not once per run.

How proven is it? The core runtime controls are established practice: risk-based classification, audit logging and human override have long use in regulated software, and the NIST vocabulary below dates from 2023. The AI-specific layer is still emerging. ISO/IEC 42001, an AI management-system standard you can be certified against, was first published in December 2023,[^10] and the EU AI Act's obligations apply in phases, so its enforcement practice is still forming.[^6] Machine-readable marking of generated text has no settled method. For images there is at least a working standard: Content Credentials (C2PA) embed a signed provenance record you can inspect yourself at verify.contentauthenticity.org.[^12] On audits, Raji and colleagues argue for internal auditing built into every stage of development, noting that earlier audits were mostly external and came after deployment.[^11]

Three neighbours: [8.1 Observability](seeing-inside.md) keeps sampled, disposable traces for debugging, while the decision record is complete and kept for a fixed period; [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md) builds the approval gate, and governance keeps the evidence it ran; [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md) blocks bad outputs, and governance records decisions about the ones that got through.

### Classify first, then map the rule

Classification comes first, because it decides how much of the rest you build. The EU AI Act (Regulation (EU) 2024/1689) sorts systems by what they are used for. A short list of practices is banned outright (Art. 5). Systems used in the eight areas listed in Annex III, which include employment, education, access to essential services such as credit, and law enforcement, "shall be considered to be high-risk" (Art. 6(2)).[^3] None of the eight covers product descriptions or advertising, so copy for a phone case falls outside the list. A hypothetical model that screened applicants for the company's warehouse jobs would be employment, and on the list. The same team can run both.

Your role matters as much as the use. The provider develops a system and puts it on the market under its own name; the deployer uses one under its authority. Art. 25(1) turns a deployer into a provider, with the heavier duties, if it puts its own name on a high-risk system, substantially modifies one, or changes its intended purpose.[^4] Wrapping a vendor's model and pointing it at a high-risk use is the case to look at hard.

The duties a commerce team is most likely to meet are the transparency rules in Art. 50.[^5] Providers must make systems that talk to people tell them they are dealing with AI (Art. 50(1)), and must mark synthetic output in a machine-readable way, except where the system only assists standard editing (Art. 50(2)). Deployers must disclose deep fakes (realistic generated or altered images, audio or video of real people, places or events) and AI-written text published to inform the public on matters of public interest, unless a person reviewed it and holds editorial responsibility (Art. 50(4)). A chat assistant looks like the Art. 50(1) case. Product copy reads as commercial rather than public-interest text, which suggests Art. 50(4) does not reach it. If you built the listing generator yourself, though, you may be its provider, and then Art. 50(2) marking is the open question: the visible label in this chapter tells a person, and it does not mark the text for a machine. Art. 4 separately asks providers and deployers to take measures to support AI literacy among their staff; the penalty rules are in the notes.[^6]

If a system does land in high-risk, the runtime duties are ones you would recognise: automatic event logs (Art. 12(1)), human oversight "commensurate with the risks, level of autonomy and context of use", including a way to stop the system (Art. 14(3)-(4)), and deployers keeping the logs under their control for at least six months (Art. 26(6)).[^7]

Outside the EU, the NIST AI Risk Management Framework (NIST AI 100-1, January 2023) gives a vocabulary many US governance conversations already use, in four functions: GOVERN sets the policies, roles and risk culture; MAP establishes the context and risks of a given system; MEASURE analyses and monitors those risks; MANAGE allocates resources to treat them.[^8] Its Generative AI Profile (NIST AI 600-1, July 2024) adds risks specific to generative systems, including value-chain and component integration, which is the risk of building on someone else's model.[^9] ISO/IEC 42001 sets the requirements for an AI management system and, unlike NIST, can be certified against.[^10] US state laws and sector rules are beyond a single page.

None of this is legal advice. Which article binds you, and in what role, is a question for counsel, and that includes the Art. 50 readings above. The engineering question is whether, when counsel answers it, your system already produces the evidence.

## How to do it

Start with the inventory, because it is the cheapest control and it drives the others. A table in the repo is enough to start, one row per AI system, with its vendors noted too; the companion code does not include one. Beside it sit a change log (who changed the model, prompt or tools, and who approved) and an incident log. Two rows might read:

| System | Owner | Purpose | Risk class | Role | Model, prompt | Tools |
|---|---|---|---|---|---|---|
| Listing pipeline | Catalog lead | Draft product pages | Not high-risk; Art. 50 with counsel | Provider | pinned, `listing-copy@v14` | `publish_listing` |
| Warehouse screen (hypothetical) | HR lead | Rank applicants | High-risk (Annex III) | Deployer | vendor, `screen@v3` | none |

Then the decision record. Your code writes one JSON line per consequential action: a publish, a price change, an answer a customer will rely on. The model never writes it and never sees it. The companion module imports only the standard library and pydantic:

```python
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel
```

The contract is the record itself:

```python
class DecisionRecord(BaseModel):
    record_id: str
    at: str                       # UTC timestamp, set by the writer
    actor: str                    # who acted: an agent name or a human id
    action: str                   # what happened, e.g. "publish_listing"
    reason: str                   # why, in the actor's words
    model: str                    # model version that produced the output
    prompt_version: str           # which prompt text was live
    overridden_by: Optional[str] = None   # human who changed the outcome
    corrects: Optional[str] = None        # record_id this line supersedes
```

`model` and `prompt_version` are the fields easiest to leave out and most missed later, because a review signed off last month says nothing about the model your vendor shipped last week. `overridden_by` is the override made visible: an empty field means no person changed the outcome. `corrects` is how the record stays append-only when something was wrong.

The writer:

```python
class RecordWriter:
    """Append-only: the file is opened in append mode and never rewritten."""

    def __init__(self, path: Path, now: Callable[[], datetime] | None = None):
        self.path = Path(path)
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._count = sum(1 for _ in self.path.open()) if self.path.exists() else 0

    def write(self, **fields) -> DecisionRecord:
        self._count += 1
        rec = DecisionRecord(
            record_id=f"rec-{self._count:06d}",
            at=self._now().isoformat(),
            **fields,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(rec.model_dump_json() + "\n")
        return rec

    def correct(self, record_id: str, **fields) -> DecisionRecord:
        # A correction is a new line; the original stays exactly as written.
        return self.write(corrects=record_id, **fields)

    def read_all(self) -> list[DecisionRecord]:
        with self.path.open(encoding="utf-8") as f:
            return [DecisionRecord(**json.loads(line)) for line in f]
```

The clock is injected so tests are deterministic, and the record id comes from a count of lines already on disk, so reopening the file continues the numbering.

One run, for the bunk bed:

1. The listing agent drafts the copy, including a rail-height claim. Because it is a safety claim, your publish gate (the check your code runs before anything goes live) holds it for a person.
2. Your code writes `rec-000001`: actor `listing-agent`, action `publish_listing`, the reason, the model version, and `prompt_version` `listing-copy@v14`. `overridden_by` is empty.
3. A merchandiser checks the claim against the spec sheet, finds it overstated, and cuts it before approving.
4. Your code calls `correct("rec-000001", ...)`, which appends `rec-000002` with `corrects: "rec-000001"`, the merchandiser's id as actor and as `overridden_by`, and the reason. `rec-000001` is still in the file, byte for byte.
5. When the complaint arrives, `read_all()` returns both lines: what the model proposed, which model and prompt proposed it, who changed it, and why.

The companion code stops at the record and the label. The gate and the override are yours to write, and both are small: the gate is the function in your publish path that holds a draft with safety claims until a named person signs off, and the override is that person's power there to change or reject it, recorded through `correct`. An unchanged approval appends a line with the merchandiser as actor and `overridden_by` empty.

The disclosure label is the last control, and it is a pure function so that code, never the model, decides what the user is told:

```python
def disclosure_label(
    *, surface: str, ai_generated: bool, human_reviewed: bool = False
) -> str:
    """Return the label to show, or "" when nothing needs disclosing."""
    if not ai_generated:
        return ""
    if surface == "chat":
        return "You are chatting with an AI assistant."
    if human_reviewed:
        return "Written with AI, reviewed by a person."
    return "Written by AI."
```

Letting the model introduce itself is the tempting shortcut, and it fails silently when a prompt edit or a long conversation drops the line. A label in the page template depends on neither. The caller already knows `surface` and `ai_generated`: which template it renders, and whether a model wrote the text.

> **In Listing Studio.** The drafting step includes a compliance-reviewer persona, a model prompted to read the draft as a compliance officer would; it is advisory. The control is the publish gate. The pipeline lists the draft's safety claims, such as rail heights or weight limits, in `compliance.safety_claims[]`, and a non-empty list means no listing goes live without a merchandiser's sign-off and a decision record. The shopper assistant, the platform's customer-facing chat, shows the chat label on every session.

### From one surface to many agents

The record gets harder as agents multiply and start choosing their own steps, and three things change.

The `actor` has to name the human who delegated the authority as well as the agent that used it. When the repricer, an agent that adjusts prices within set rules, changes a price at 3 a.m., the record should say which person approved the rule it ran under.

Model and prompt versions have to be pinned and changed on purpose, with a re-evaluation before a new version goes live, since silent upstream drift voids a prior review. [4.1 Prompt Architecture & Management](../craft/prompts-are-source-code.md) covers versioning prompts and [8.2 Which Model?](which-model.md) covers choosing models.

The tools an agent may call belong in the inventory, as an approved registry, so a new MCP server is a change with an approver like any other ([2.4 MCP](../the-unit/mcp.md), [2.6 The Harness](../the-unit/the-harness.md), [8.5 Locks, PII & Identity](locks-pii-identity.md)).

## Gotchas

1. **Treating traces as the record.** Observability stores sample runs and expire them on a debugging schedule. A compliance record is unsampled and kept for a set period, at least six months for a high-risk deployer under Art. 26(6).[^7] Write it separately, so a change to trace retention cannot delete it.
2. **Calling append-only tamper-proof.** The companion writer is append-only by convention: nothing in it stops someone with file access from editing a line, and its tests prove only that a correction leaves the original bytes alone. For a record outsiders must trust, put it on storage with a write-once retention lock (storage that refuses edits and deletes until a set date), or chain each line to the hash of the one before so an edit shows. The companion code does neither. It also reads its line count once, at construction, so two writers on one file hand out the same id; put one writer service in front of the store, or take the id from a database sequence.
3. **Mistaking the persona for the control.** A compliance-reviewer prompt is a useful first read, and still a model's opinion. The control is the deterministic gate and the record it writes.
4. **Becoming a provider by accident.** Branding a high-risk system as your own, modifying it substantially, or pointing it at a new purpose can move you into the provider's duties.[^4] Re-check the inventory row when the purpose changes, as well as when the code does.
5. **Building the binder instead of the controls.** A policy document, a risk register and a model card with no runtime control behind them produce paperwork that describes a system nobody can show is behaving.
6. **Letting the harness change itself unrecorded.** A system that edits its own prompts or tools needs the diff and an approver in the record like any other change; [9.7 Self-Improving Systems](../frontier/self-improving-systems.md) takes that further.

## In short

Give every AI system an inventory row with an owner and a risk class. Have your code write a decision record, with the model and prompt version, on every consequential action; keep it apart from your traces, and do not call it tamper-evident until the storage makes it so. Make the override stop the action and show in the record, and render the disclosure label in code. Then hand the classification question to counsel, and map the answer onto controls you already run.

<small class="chapter-meta">**Maturity: Established (core runtime controls) · Emerging (enforcement and AI-specific standards)** · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: *Moffatt v. Air Canada*, 2024 BCCRT 149 (British Columbia Civil Resolution Tribunal, 14 February 2024). <https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html>. A tribunal decision, not a court judgment.
[^2]: US Federal Trade Commission, "FTC Announces Crackdown on Deceptive AI Claims and Schemes" (25 September 2024), the Operation AI Comply announcement including DoNotPay. <https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes>. The $193,000 figure is the proposed order as announced.
[^3]: Regulation (EU) 2024/1689 (the AI Act), Arts. 5 and 6 and Annex III. <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>; article text also at <https://artificialintelligenceact.eu/article/6/> and <https://artificialintelligenceact.eu/annex/3/>.
[^4]: Regulation (EU) 2024/1689, Art. 25(1). <https://artificialintelligenceact.eu/article/25/>
[^5]: Regulation (EU) 2024/1689, Art. 50(1), 50(2) and 50(4); Art. 4 on AI literacy. <https://artificialintelligenceact.eu/article/50/>, <https://artificialintelligenceact.eu/article/4/>
[^6]: Regulation (EU) 2024/1689, Art. 99(1) and 99(4). <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>. Member States set the penalties (Art. 99(1)). For the listed operator obligations, which include the deployer duties in Art. 26 and the transparency duties in Art. 50, Art. 99(4) allows fines of up to EUR 15,000,000 or 3% of worldwide annual turnover, whichever is higher. Art. 4 is not on that list, so its enforcement falls to national rules under Art. 99(1). Application dates for the Act's obligations are phased and subject to amendment; check the consolidated text on EUR-Lex for the current ones.
[^7]: Regulation (EU) 2024/1689, Art. 12(1), Art. 14(3)-(4), Art. 26(6) and Art. 73. <https://artificialintelligenceact.eu/article/12/>, <https://artificialintelligenceact.eu/article/14/>, <https://artificialintelligenceact.eu/article/26/>, <https://artificialintelligenceact.eu/article/73/>. Providers of high-risk systems must also report serious incidents to the market surveillance authorities where they occur (Art. 73(1)). Providers of general-purpose AI models have a separate set of duties in Chapter V of the Act.
[^8]: NIST, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1 (January 2023). <https://doi.org/10.6028/NIST.AI.100-1>
[^9]: NIST, *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*, NIST AI 600-1 (July 2024). <https://doi.org/10.6028/NIST.AI.600-1>
[^10]: ISO/IEC 42001:2023, *Information technology: Artificial intelligence: Management system*, first edition, December 2023. <https://www.iso.org/standard/81230.html>. Quoted from the publisher's abstract; the full text is paywalled and was not read.
[^11]: Raji, I. D., et al., "Closing the AI Accountability Gap: Defining an End-to-End Framework for Internal Algorithmic Auditing" (2020). <https://arxiv.org/abs/2001.00973>
[^12]: Content Authenticity Initiative, Content Credentials verification tool (C2PA standard). <https://verify.contentauthenticity.org/>

## See also

- [8.1 Observability](seeing-inside.md), for the traces the decision record must not be confused with.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md), for building the approval gate whose outcome the record keeps.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md) and [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md), for the filters and red-teaming that sit in front of the record.
- [4.1 Prompt Architecture & Management](../craft/prompts-are-source-code.md), for the prompt versions the record points at.
- [8.2 Which Model?](which-model.md), for the model and vendor choices whose versions you pin.
- [8.4 Controlling Cost](controlling-cost.md), for spend caps, the other runtime limit an approver signs off.
- [8.5 Locks, PII & Identity](locks-pii-identity.md), for the identity and data-protection engineering this chapter leaves out.
- [9.7 Self-Improving Systems](../frontier/self-improving-systems.md), for governing a harness that changes itself.
- [The Security Posture Map](../catalogs/security-posture.md), for the security controls catalogued in one place.

## Further reading

- [Regulation (EU) 2024/1689 on EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj): the AI Act itself, the only authoritative text; Arts. 6, 25, 26 and 50 are the ones a product team reads first.
- [NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1): the AI RMF and its four functions, the shared vocabulary for governance conversations.
- [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1): the Generative AI Profile, with the risks specific to building on foundation models.
- Raji et al., ["Closing the AI Accountability Gap"](https://arxiv.org/abs/2001.00973): a strong argument for audits that run through development instead of after it.

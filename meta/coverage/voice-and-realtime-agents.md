# Coverage map: Voice & Realtime Agents (chapter 6.4)

> Research-derived spec for what the chapter must cover. Angles run: vendor primary docs,
> academic, practitioner/framework docs, everyday-engineer gotchas, security, incidents,
> skeptical read, alias sweep. Review and trim **Must-cover**; that sets the scope.

**Thesis (one sentence).** A voice agent fails on turn detection, barge-in truncation and audio
transport before model quality shows up, so a cascaded streaming pipeline is the default
whenever inspectable control and predictable cost matter more than prosody.

**Budget:** Standard pattern, ~2,000 to 2,800 prose words. **Grounding:** companion repo plus
research (no production claim).

**Litmus.** Your code decides transport, echo control, fixed-timeout VAD, playback flushing and
truncation offsets. The model decides semantic end-of-turn, overlap and backchannel handling in
native S2S or full-duplex, and which tool to call.

## The mental model

The user judges a voice agent by how long the silence lasts after they stop talking and whether
it shuts up when they cut in. Fix the latency budget first and choose the architecture backwards
from it. The hard problems are deciding when the turn has ended, what to do on interruption, and
keeping the conversation record equal to what the user actually heard.

## Must-cover

Ranked. `[+]` = new content (the chapter is a stub).

1. **The latency budget, first** `[+]`: end of user speech to first audible agent audio,
   decomposed into endpointing wait, STT finalisation, LLM first token, TTS first byte, network
   and playback buffering. Measure median and p95; measure the filler ("I'm checking")
   separately from the useful answer. Human baseline: Stivers et al., PNAS 2009
   (doi:10.1073/pnas.0903616106), transitions across 10 languages peak within 200 ms. Do not
   freeze a "feels broken above N seconds" rule. *Skip it:* you tune the model while endpointing
   dominates. **Established** (as method). (OpenAI voice-agents guide; Stivers.)
2. **Turn detection and VAD** `[+]`: VAD finds speech, not finished thoughts. Three layers:
   silence-timeout (`server_vad`: `threshold`, `prefix_padding_ms`, `silence_duration_ms`),
   semantic end-of-turn (`semantic_vad` with `eagerness`; LiveKit turn detector; Pipecat Smart
   Turn), manual/push-to-talk. Short timeout cuts people off, long feels slow. Gemini's docs warn
   that very short silence settings can split one utterance (verify the exact field name,
   `silenceDurationMs`, on the Live API page). **Established** (VAD), **Emerging** (learned
   end-of-turn). (OpenAI realtime-vad; Gemini Live; LiveKit turns; Smart Turn README.)
3. **Barge-in and an honest transcript** `[+]`: stop playback, flush queued audio, truncate the
   conversation to what was heard. OpenAI WebSocket: you send `conversation.item.truncate` with
   `audio_end_ms`; on WebRTC and SIP the server truncates unplayed audio. Gemini discards the
   cancelled generation and sends `interrupted`. Twilio `clear` plus `mark` show what never
   played. False interruptions (cough, "mm-hm"): LiveKit `interruption.min_duration`,
   `min_words`, `resume_false_interruption`. *Skip it:* the model "remembers" saying what the
   user never heard. **Established** (playback flush), **Emerging** (transcript truncation,
   false-interruption resume). (OpenAI realtime-conversations; Gemini Live; LiveKit turns.)
4. **Speech-to-speech versus cascaded** `[+]`: S2S (OpenAI `gpt-realtime`, Gemini Live) buys
   latency and prosody; cascaded (STT, text LLM, TTS) buys inspectable text, model choice,
   per-stage swap, checks before speech. OpenAI frames it as control versus integration and
   suggests chained when "each stage needs to be visible or replaceable". Contest "S2S is the
   only viable design": Pipecat and LiveKit are built on streaming cascaded pipelines and host
   S2S too. Third shape: full-duplex (Moshi, arXiv:2410.00037, Défossez, Mazaré, Orsini, Royer,
   Pérez, Jégou, Grave, Zeghidour; "theoretical latency of 160ms, 200ms in practice") and GPT-Live.
   **Security gotcha:** in S2S, raw audio reaches the tool-calling model with no text gate to
   inspect; hidden audio prompt injection is documented (AudioHijack, arXiv:2604.14604, Chen et
   al., 2026; Piggybacking on Perception, arXiv:2607.28165, Liu et al., 2026, 69.10% average
   attack success against Gemini 3 Pro). Phone-channel speaker spoofing: state as risk, no
   source yet. **Established** (cascaded streaming), **Emerging** (S2S, full-duplex).
5. **Transport, echo, and telephony** `[+]`: WebRTC (media tracks plus data channel; OpenAI
   recommends it over WebSockets "for more consistent performance"), WebSocket (server side),
   SIP. Without echo cancellation the agent hears itself and interrupts itself; browser
   capture offers it, raw WebSocket pipelines must supply it (verify against MDN/WebRTC; the
   OpenAI WebRTC page is silent on AEC). SIP: OpenAI sends `realtime.call.incoming`, you
   accept or reject, then control over WebSocket by `call_id`; webhooks repeat, so deduplicate.
   Twilio Media Streams: `audio/x-mulaw`, 8000 Hz, mono, base64; DTMF inbound only. Resample
   8 kHz mu-law to model rates. Pipecat (BSD-2) and LiveKit Agents are the public frameworks
   that wrap this; named plainly, not endorsed. **Standard** (WebRTC, SIP as protocols),
   **Emerging** (vendor SIP bridges, framework APIs). (OpenAI realtime-webrtc, realtime-sip;
   Twilio media-streams; docs.pipecat.ai; docs.livekit.io/agents.)
6. **Tool calls inside a voice turn** `[+]`: a tool call is dead air. Speak a filler first, keep
   talking while it runs, or (GPT-Live) delegate to a backend. OpenAI flow: function call item
   with `call_id`, you send `function_call_output`, then `response.create`. A barge-in can
   cancel a pending call (Gemini says so), so tools must be idempotent or confirmed before side
   effects; return structured errors the model can speak around. **Established** (tool use),
   **Emerging** (async/delegated). (OpenAI realtime-conversations; Gemini Live.)
7. **Economics, structurally** `[+]`: two billing shapes. Token-billed (`gpt-realtime`,
   Gemini Live): audio tokens (user about 1 token per 100 ms per OpenAI; verify the assistant
   rate), the conversation is resent each response so later turns cost more, caching is
   best-effort, truncation settings trade cost against memory. Duration-billed (GPT-Live):
   per-second active and standby rates, backend calls billed separately, and creating a WebRTC
   session bills 15 seconds while it initialises, credited once it runs. Cascaded: STT plus
   LLM tokens plus TTS. **No dollar figures in prose**; point to the live pricing pages and 8.4.
   **n/a** (vendor billing). (OpenAI realtime costs, voice-latency-cost; Gemini pricing.)
8. **Session lifecycle and audio context growth** `[+]`: audio fills context fast and long
   histories cost tokens and attention (mitigation: compaction). Gemini Live: without
   compression audio-only sessions are limited to 15 minutes and audio+video to 2; a connection
   lives about 10 minutes and you get a `GoAway` with `timeLeft`; sliding-window context
   compression and session resumption (tokens valid 2 hours) extend it. OpenAI: a Realtime
   session lasts at most 60 minutes; SIP calls ring 3 min, last 2 h (from earlier read, verify).
   Plan reconnection and carry-over. **Emerging** (compression, resumption); limits are **n/a**.
9. **Evaluating voice** `[+]`: transcripts hide timing failures. Test turn-taking
   deterministically (fake clock, scripted VAD events) and measure latency on real calls.
   External benchmark for full-duplex turn-taking: Full-Duplex-Bench (arXiv:2503.04721, Lin et
   al., Mar 2025, pauses, backchannels, turn changes, interruptions). One paragraph; depth is
   4.2. **Emerging.**

## Mention-and-link (plain text, no links until chapters merge)

2.1 Tool Use and 4.3 Human-in-the-loop (tool turns); 4.2 Evaluation; 4.4 Guardrails and 4.6
Prompt Injection (spoken injection, one line each); 5.4 Compaction (audio context); 6.1
Ingestion (audio as input); 6.3 Streaming & Agent UX; 7.1 Retry & Degradation (reconnect);
8.4 Controlling Cost; 8.5 Locks, PII & Identity and 8.6 Governance (recording, consent: one
sentence, point to counsel); 8.7 Deployment (stateful workers); 9.5 Computer Use.

## Out of scope

STT/TTS and codec internals (Mimi, Whisper); carrier setup and trunk configuration; avatars,
video, music; voice cloning and TTS quality comparisons.

## Maturity summary

- **Standard:** WebRTC and SIP as protocols.
- **Established:** cascaded streaming pipeline; VAD; playback flush; latency-first budgeting.
- **Emerging:** S2S and full-duplex; learned end-of-turn; transcript truncation; compression and
  resumption; vendor SIP bridges and frameworks.
- **Contested:** "S2S is the only viable architecture"; any single universal latency threshold.
- **Chapter verdict: split. Established (cascaded streaming pipelines), Emerging (native S2S and
  full-duplex).** Carries "Last reviewed".

## Aliases (chapter-level)

voice agents; realtime agents (OpenAI Realtime API); speech-to-speech, S2S, versus "chained"
architecture (OpenAI voice-agents guide); spoken dialogue models (Full-Duplex-Bench title);
full-duplex (Moshi). Google ADK and Gulli names not yet swept; author sign-off on any alias.

## Reader-verifiable anchors

- OpenAI Realtime: `session.update` with `turn_detection` of `server_vad` or `semantic_vad`
  (developers.openai.com/api/docs/guides/realtime-vad).
- LiveKit Agents: `turn_detection` modes `vad`, `stt`, `realtime_llm`, `manual`
  (docs.livekit.io/agents/build/turns).

## Incidents

Public, press-reported, not postmortems. McDonald's ended its IBM drive-thru voice test in 100+
restaurants (CNBC, 2024-06-17; no technical reason given). Taco Bell reconsidered voice AI at
busy drive-thrus in 2025 after viral clips (one showed 18,000 waters); its CDTO Dane Mathews
spoke to it, and parent Yum reported 2 million+ orders across 300+ stores, so it did not drop
it. Lessons: noisy-channel STT, unbounded tool arguments (2.1, 4.4), no loop detection. Cite
the press, not the AI Incident Database, until opened. No "From production:" callout.

## Carrier

Shopper assistant voice channel ("will this heat my 200 sq ft garage?"): catalog lookup is a
tool, filler while it runs, barge-in cancelling an uncommitted action. The carrier bible lists
the shopper assistant without a voice channel; amend the bible first (open question).

## Code seam

New small package `listing-studio/voice_turns` (name to confirm at the code stage): a pure
turn-taking state machine (idle, user_speaking, endpointing, agent_thinking, agent_speaking,
interrupted) driven by scripted VAD events and an injected fake clock. Asserts endpointing
timeout, barge-in truncation point (ms actually played), false-interruption resume, tool-call
cancel on interrupt. No audio, no network, CI-safe. The chapter must say it models the logic,
not the signal path.

## Named-idea candidates

None needed; barge-in and endpointing are canon. Possible plain label: "honest truncation".
Author decides.

## Open questions for the author

1. Amend carrier-bible section 5 to give the shopper assistant a voice channel?
2. Accept the split maturity verdict, or force one word?
3. Keep item 9, or fold it into the code seam and 4.2?
4. Approve `voice_turns` as the new package?
5. Is the Taco Bell and McDonald's material worth a paragraph given it is press, not primary?

## Sources

OpenAI: developers.openai.com/api/docs/guides/ realtime, realtime-vad, realtime-conversations,
realtime-webrtc, realtime-sip, voice-agents, voice-latency-cost; pricing page. Google: Live API
and session management (aistudio.google.com/docs/live-api). Pipecat docs; Smart Turn
(github.com/pipecat-ai/smart-turn); LiveKit agents turns. Twilio media-streams. arXiv:2410.00037,
2604.14604, 2607.28165, 2503.04721. Stivers et al. 2009 (abstract via secondary summary; PNAS
returned 403). CNBC 2024-06-17; TechSpot and PYMNTS on Taco Bell.

## Map review (Stage 1.5)

Reviewer: an independent second model. Each finding verified against the page or paper named.

1. Thesis, budget, litmus missing: accepted-modified; added, with a reworded thesis.
2. Billing conflates gpt-realtime and gpt-live: accepted; confirmed per-second GPT-Live billing and the 15 s WebRTC init charge.
3. Transport and AEC missing: accepted-modified; new item 5, but the OpenAI page is silent on AEC so that claim is flagged to verify.
4. Security skip and 4.6 link: accepted; both arXiv papers opened and match.
5. Session ceilings and context growth: accepted; Gemini 10 min, GoAway, 15/2 min, 60 min OpenAI confirmed.
6. Bloat and academic baselines: accepted-modified; frameworks folded into 5, Stivers added (abstract only), Full-Duplex-Bench added; v1.5/v2/v3/VoiceBench IDs unopened so omitted.
7. "None found" incidents: accepted-modified; McDonald's date corrected to June 2024 per CNBC, bacon-on-ice-cream claim dropped as unsourced.
8. Maturity verdicts: accepted-modified; split verdict adopted, frameworks and SIP bridges downgraded, vendor session and rate limits carry no maturity verdict.
9. Frozen pricing and unverified sources: accepted; prices removed, Moshi authors and 160/200 ms confirmed, narrowband claim cut.
10. Confidentiality and carrier bible: accepted; masking sentence and callout prompt removed, bible amendment raised.
11. Named ideas and open questions: accepted; both sections added.
12. SDK names and URL: accepted-modified; LiveKit `min_duration` and `min_words` were already right under `interruption`, `resume_false_interruption` confirmed; the ai.google.dev URL 301s to aistudio.google.com, so the map's URL stands; `silenceDurationMs` left as verify.
13. Aliases: accepted-modified; narrowed to chapter-level, unsourced Google ADK names withheld.
14. Seam pointers: accepted; added as plain text, no links.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Thesis and verdict.** Keep the thesis as folded. The verdict is split: Established for cascaded streaming pipelines and Emerging for native speech-to-speech and full-duplex. The top line names Emerging, which is the conservative choice for the chapter as a whole, and the prose argues the split. (Author checklist.)
2. **Carrier.** Do not amend the carrier bible; that is the author's call. In the chapter, the shopper assistant gets a voice channel as a hypothetical ("if the shopper assistant took calls"). (Author checklist.)
3. **Evaluation.** Keep one short evaluation paragraph and point to 4.2 in plain text for the depth.
4. **Code.** Approve `listing-studio/voice_turns/`, a pure state machine driven by a fake clock and scripted VAD events. Tests use stdlib and pydantic only.
5. **Incidents.** Drop the press-reported incidents paragraph, since the sources are secondary.
6. **Unverified items.** The AEC claim, the Stivers figure, Gemini `silenceDurationMs`, audio token rates and SIP limits ship only if the fact-checker opens a primary source; otherwise cut them. For the Stivers figure, cite the abstract only if the number is in it.
7. **Excluded.** No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

Sources: prose critique (PC), fact check (FC), cold read (CR), independent second-model draft review (SE). Each finding was checked against the chapter, the companion code or the cited page before it was acted on.

- PC1 / SE5, opening says the failures have nothing to do with the model while semantic VAD puts end-of-turn in a model: fixed. The opening now says a smarter reply model fixes neither failure and the timing layer is usually your code; the definition paragraph and the SVG note that the diagram shows the fixed-timeout design.
- PC2 / SE9, "model matters far less" unqualified: softened to the raw ability of the reply model.
- PC3 / FC19, rebuttal of an uncited "S2S is the only viable design" claim: cut. Replaced with LiveKit's `realtime_llm` turn-detection mode as evidence that the two can be mixed.
- PC4, Cost names two billing shapes without saying what each rewards: fixed, one recommendation per shape.
- PC5, transport paragraph has no lead claim: fixed, opens on which transport to use where.
- PC6, "where voice and text agents diverge most": cut.
- PC7 / CR, "Real systems count played milliseconds" is abrupt: fixed, merged with the duplicate sentence and tied to `audio_end_ms`; the word slice is labelled a simplification.
- PC8, Gotcha 2 repeats the latency-budget line: fixed, the gotcha now gives Gemini's 500 to 800 ms recommendation.
- PC9, the separate shopper-assistant paragraph repeats the opening: fixed, cut. The carrier now appears as a hypothetical in the walkthrough lead-in (per Stage 1.6 ruling 2), so the opening stays on the concept.
- PC10, filler utterance as a bare quote: fixed, italicised.
- PC11 / CR, unclear what 1,000 ms is measured from: fixed, "1,000 ms into playback".
- PC12, "at 200 ms, a cough,": fixed, parenthesised.
- PC13, Emerging verdict vs a cascaded recommendation: rejected for now; the split is argued in the prose; author checklist.
- PC14, voice identity buried in Gotcha 3: rejected; kept as one cross-link sentence to stay inside the budget.
- PC15, "The contract is two numbers.": cut.
- PC16, editorial code comments: rejected; the comments are in synced snippets and are not wrong.
- PC17, "fills a context window quickly": softened to "long audio fills the context window".
- PC18, "errors the model can speak around": fixed, a spoken apology or a retry offer.
- FC2, [^1] does not support the S2S trade-off: fixed. The gains (latency, lost "emotion or non-speech sounds") now cite the Moshi abstract [^9]; the costs (no inspectable or transformable intermediate text, no per-stage replacement, no check before speech) cite [^1], which describes the chained path and its pre-response policy checks. The "frames the design around that same chain" sentence is cut; [^1] now backs only the advice to time acknowledgements separately.
- FC3, `gpt-realtime` unverified: fixed, made generic ("OpenAI's Realtime API"); the guide's sample uses a versioned model name.
- FC7, SIP flow currency (GPT-Live uses a different incoming event): softened, the chapter no longer names the event.
- FC9, 60-minute cap is on the Realtime conversations guide: fixed, cited to [^7]; the old [^17] is removed.
- FC10, [^4] root page lacks the specifics: fixed, points to the capabilities and session-management subpages.
- FC13, [^8] overview page lacks format, `clear` and `mark`: fixed, points to the WebSocket messages page; mono confirmed there (channel count always 1).
- FC15, MDN covers only browser echo cancellation: fixed, [^12] backs the browser half; the other half is advice, not a citation.
- FC16 / SE15, short titles in [^13] and [^15]: fixed, full titles. The Chen paper's venue was not checked and is not added.
- FC18, Stivers [^2] unverified by fetch (PNAS and PubMed blocked automated access): unchanged. The chapter makes no numeric claim from it, and the wording matches the published abstract. Author checklist.
- FC19, "Pipecat and LiveKit are built on cascaded pipelines": softened to "support them".
- FC23, "each of which you can swap": softened to "you can swap any one".
- CR, undefined terms: glossed p95, endpointing (at first use), speech-to-text finalisation, prosody, SIP, WebRTC, idempotent, GPT-Live and `TurnTaker`. Not glossed: mulaw (the format string is self-describing), Lethal Trifecta (a cross-reference to 4.6).
- CR, other terms (full-duplex, bare `semantic_vad` at first mention, Twilio `mark` and `clear`, compaction, the shopper assistant): partly fixed. Full-duplex is now glossed as listening and speaking at once; `mark` and `clear` are explained in their sentence; `semantic_vad` is explained in How. Compaction and the shopper assistant are left as cross-references for budget.
- CR, why the maturity split follows the architecture: fixed by the rewritten maturity paragraph, which gives each architecture's gains and costs with sources.
- CR, conditions behind the 69.10% figure: rejected for budget; the sentence names the attack class (hidden audio prompt injection) and the target, and the footnote gives the paper.
- CR, build test (who calls `tick`, imports, repo location): rejected. The chapter states the full class is in the companion repo and names the file path; the listings show the logic, not a runnable module.
- CR, the filler mechanism is missing: fixed, the filler counts as the first audio.
- CR, "furthest the decision has moved" is uncited: cut.
- CR, idempotency step missing: fixed with SE2.
- SE1, the transcript guarantee goes beyond the APIs: partly rejected. OpenAI's Realtime conversations guide says `conversation.item.truncate` "will cut the audio at a given place and remove the text transcript for the unplayed portion". Gemini's capabilities page confirms that "only the information already sent to the client is retained in the session history", so the chapter now says Gemini's history can hold more than played. The word-aligned demo is now labelled a simplification that relies on the provider to cut the transcript.
- SE2, idempotency does not settle cancellation races: fixed. Calls are tracked as pending, running or committed; a running call may commit after the caller changes their mind.
- SE3, the streaming internals of a cascade (interim transcripts, text aggregation) are missing: rejected for budget; out of scope at 2,800 words.
- SE4, GPT-Live missing from the architecture discussion: fixed. It is defined in the maturity paragraph as a full-duplex model with a separate backend, per [^1]; full duplex is no longer framed as research-only.
- SE6, a late `finish()` after a barge-in restores the unheard words: fixed in code. `TurnTaker.finish` ignores completion unless playback is running and not paused, and `test_a_late_playback_completion_does_not_restore_unheard_words` covers it.
- SE7, voice snippet anchors are declared but never tested: fixed. Added `test_voice_chapter_code_matches_tested_source`.
- SE8, a Twilio `clear` returns pending marks: fixed (verified on the WebSocket messages page); marks are matched by name.
- SE10, the WebRTC initialisation charge is missing its credit, and OpenAI's history-cost account is applied to Gemini: fixed. The credit is stated and the resend and caching claims are scoped to OpenAI.
- SE11, the evaluation omits business-state checks: fixed, one sentence.
- SE12, no failure or cancellation contract demonstrated: softened. Structured-error guidance is made concrete; no new code, for budget.
- SE13, category-wide maturity labels: rejected; the chapter labels architectures, not categories.
- SE14, the alias line mixes architecture names: rejected for now; aliases need author sign-off. Author checklist.
- SE16, Twilio "resample before a model sees it" is absolute: fixed, converted only when the model expects another format (OpenAI's guide describes 24 kHz PCM).
- SE15b, [^14]'s page title is now "Cost optimization": fixed (checked on the page), along with the credit sentence.
- SE17, too many listings, and diagram values not marked as examples: partly fixed. The alt text and SVG description mark 700 and 300 ms as test values; the listings stay because the sync test pins them.

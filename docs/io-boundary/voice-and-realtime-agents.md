# 6.4 Voice & Realtime Agents

*A voice agent has to decide when you have stopped talking, what to do when you talk over it, and what it actually said. Get those three right inside a latency budget and the raw ability of the reply model matters less than you expect.*

*Also called: voice agents, realtime agents, speech-to-speech (S2S), chained or cascaded voice pipelines, spoken dialogue models, full-duplex agents.*

## Why you'd reach for it

You ask a voice agent whether a heater will cover your garage, pause to remember the square footage, and it starts answering the question you had not finished. You cut it off halfway through its answer, and on the next turn it builds on a sentence you never heard. A smarter reply model fixes neither failure. Both come from the timing layer between the microphone and the model, which is usually your code.

In a text chat, the user ends each turn by pressing send. Speech has no send button. Something has to decide from a stream of audio that the user is done, and that decision is a trade. Wait too little and you cut people off mid-thought; wait too long and every answer arrives after an awkward silence. Then the agent talks, and the user may talk over it. Your system has to stop the audio, throw away what was queued, and make the conversation record match what the user actually heard, or the model will carry on as if its full reply landed.

People are fast at this. A study of ten languages found that speakers in all of them avoid overlapping talk and keep the silence between turns short.[^2] That is the bar a voice agent is judged against, which makes a latency budget the useful first artifact for a voice project. Measure the time from the end of the user's speech to the first audible audio of the reply, and break it into its parts: the endpointing wait (deciding the user's turn is over), speech-to-text finalisation (settling the last words of the transcript), the model's first token, text-to-speech's first byte of audio, and network and playback buffering. Track the median and the p95 (the latency 95 percent of turns beat). Time a filler such as *"let me check that"* separately from the answer, as OpenAI's voice guidance also advises: the filler counts as the first audio, so a fast one can hide a slow answer in your averages.[^1] Skip this step and you end up tuning the model while the endpointing timeout eats the budget.

You need this chapter when:

- users speak to the agent and hear it reply, in a browser, an app, or on the phone;
- the agent calls tools mid-conversation, so a turn can contain dead air;
- you have to account for what the user heard, for support, compliance, or the next turn's context.

You don't, if push-to-talk is acceptable (releasing the button ends the turn, and most of the turn-taking problem goes with it), or if the interaction can be text with optional speech synthesis on the output. Both are cheaper; propose them first.

## What it actually is

A voice agent is an agent loop wrapped in a turn-taking controller: code that turns a continuous audio stream into discrete user turns, plays the agent's replies as audio, handles the user speaking over a reply (barge-in), and keeps the transcript equal to what was actually heard. The model sits inside that controller. It can be a text model behind speech-to-text and text-to-speech (a cascaded, or chained, pipeline) or a single speech-to-speech model that hears audio and speaks audio.

![The caller's audio stream enters the turn-taking controller, a rectangle where your code decides. It has four duties, shown with the companion repo's test values: endpointing (700 ms of silence closes the turn), barge-in (300 ms of talking over a reply is an interruption), flushing playback, and truncating the transcript to the words that played. A closed turn passes to a rounded node inside it where the model decides the reply and the tool call; the model is either speech-to-text, a text model and text-to-speech in a chain, or one speech-to-speech model. The reply leaves as audio. A truncation arrow writes back only what played: the caller's "it's about 200 square feet", then the agent's "it should heat a [interrupted]".](voice-and-realtime-agents-turn-controller.svg)

Most of the hard part is your code's job. Transport, echo control, a fixed silence timeout, flushing playback, and the offset at which you truncate the transcript are deterministic engineering that predates language models. The model's decisions are narrower. It chooses the reply and which tool to call, as in any agent loop, and in the newer designs, which the diagram leaves out, it also judges whether a pause means the user has finished: OpenAI's `semantic_vad` and learned end-of-turn detectors such as LiveKit's turn detector and Pipecat's Smart Turn put that call in a model.[^3][^5][^6] In a full-duplex model the network itself handles overlap and backchannels ("mm-hm").

The maturity is split, and the split follows the architecture. Cascaded streaming pipelines are Established: Pipecat and LiveKit Agents, two open-source frameworks for voice agents, support them, and OpenAI recommends the chained design when "each stage needs to be visible or replaceable".[^1][^16] Native speech-to-speech, through OpenAI's Realtime API and Gemini Live, is Emerging. The Moshi authors' case for it is that a cascade adds latency and its text step loses "emotion or non-speech sounds", the prosody (rhythm and tone) a transcript flattens.[^9] What it gives up is the text checkpoint between hearing and speaking, where a chained pipeline lets you inspect or transform the words, check a reply before it is spoken, and replace any one stage.[^1] Full-duplex models, which listen and speak at once, are newer still. Moshi reports a theoretical latency of 160 ms and about 200 ms in practice,[^9] and OpenAI's GPT-Live is a full-duplex model that handles the spoken side and hands reasoning and tool calls to a separate backend.[^1] LiveKit Agents also offers a speech-to-speech model as one turn-detection mode beside its cascaded ones, so a team can mix the two.[^5]

Two neighbours get confused with it. Streaming text to a screen (see 6.3 Streaming & Agent UX) shares the token stream but has no turn-taking: the user cannot interrupt a paragraph by reading over it. Tool use (see [2.1 Tool Use](../the-unit/tool-use.md)) is unchanged in what it decides, and changed in what it costs, because in voice every tool call is audible silence.

## How to do it

Start with turn detection, because it sets the floor of your latency budget. There are three layers, and you pick one per product. A silence timeout is the oldest: a voice activity detector (VAD) flags speech and silence, and once silence has lasted a fixed number of milliseconds, the turn is over. OpenAI exposes this as `server_vad`, with `silence_duration_ms` as the wait.[^3] Semantic end-of-turn replaces the fixed wait with a model's judgment of whether the utterance sounds finished, tuned in OpenAI's `semantic_vad` by an `eagerness` setting.[^3] Manual turn-taking, push-to-talk, hands the decision to the user.

A VAD finds speech, and a pause is weak evidence that a thought is finished. A short timeout cuts people off at every hesitation, and Gemini's documentation warns that short silence settings can split one utterance into several turns.[^4] A long one makes every reply feel slow. The state machine below is the silence-timeout layer and the barge-in rule as plain code, with no audio and no network: VAD events arrive as scripted strings and time comes from a fake clock, which makes the timing testable.

```python
class State(str, Enum):
    IDLE = "idle"
    USER_SPEAKING = "user_speaking"
    ENDPOINTING = "endpointing"          # user went quiet; is the turn over?
    AGENT_THINKING = "agent_thinking"    # waiting on the model and any tool call
    AGENT_SPEAKING = "agent_speaking"


@dataclass
class TurnConfig:
    endpoint_ms: int = 700        # silence that closes the user's turn
    min_interrupt_ms: int = 300   # shorter overlap is a cough or "mm-hm", not a barge-in
```

`endpoint_ms` is the silence that closes a turn, and `min_interrupt_ms` is how long the user has to keep talking over a reply before it counts as a barge-in. They are the companion repo's test values, not recommendations; tune both against recordings of your own users. Each handler below takes a `TurnTaker`, the object holding the state, clock, playing reply and history (the full class is in the companion repo).

```python
def on_vad(t: "TurnTaker", event: str) -> None:
    """Feed one scripted VAD event: "speech_start" or "speech_end"."""
    tick(t)
    now = t.clock.now_ms
    if event == "speech_start":
        if t.state == State.AGENT_SPEAKING:
            pause_playback(t, now)  # maybe a barge-in; decided in tick()
        elif t.state == State.AGENT_THINKING:
            cancel_pending_tool(t)  # the user spoke before the action ran
            t.state = State.USER_SPEAKING
        else:
            t.state = State.USER_SPEAKING  # also: a pause mid-thought, not the end
    elif event == "speech_end":
        if t._paused_at is not None:
            resume_playback(t, now)  # too short to be an interruption
        elif t.state == State.USER_SPEAKING:
            t.state = State.ENDPOINTING
            t._quiet_since = now


def tick(t: "TurnTaker") -> None:
    """Check the timers against the clock; call it whenever time has moved."""
    now = t.clock.now_ms
    if t.state == State.ENDPOINTING and now - t._quiet_since >= t.cfg.endpoint_ms:
        t.state = State.AGENT_THINKING   # silence long enough: the turn is over
    elif t._paused_at is not None and now - t._paused_at >= t.cfg.min_interrupt_ms:
        interrupt(t)
```

One run, as if the storefront's shopper assistant took calls:

1. The user asks about the garage heater and goes quiet. The state moves from `user_speaking` to `endpointing` and the clock starts.
2. At 400 ms of silence the user adds "it's about 200 square feet". The state returns to `user_speaking`, and the turn stays open.
3. After 700 ms of uninterrupted silence, `tick` closes the turn and the state becomes `agent_thinking`. In the test, 699 ms is not enough.
4. The reply starts playing at 250 ms per word. At 1,000 ms into playback the user starts talking, so playback pauses with four words played.
5. The user keeps talking for 300 ms. That crosses `min_interrupt_ms`, so the barge-in is real: the history records "it should heat a [interrupted]" and nothing after it. Had the user stopped at 200 ms (a cough), playback would resume and the full reply would be recorded.

```python
def pause_playback(t: "TurnTaker", now: int) -> None:
    t._paused_at = now
    t._paused_played = now - t._started_at - t._paused_total


def resume_playback(t: "TurnTaker", now: int) -> None:
    t._paused_total += now - t._paused_at   # silence we inserted, not audio played
    t._paused_at = None


def interrupt(t: "TurnTaker") -> None:
    """A real barge-in: stop, and record only what the user heard."""
    heard = t._words[: t._paused_played // t._ms_per_word]
    t.history.append(" ".join(heard) + " [interrupted]")  # honest truncation
    cancel_pending_tool(t)
    t._paused_at = None
    t.state = State.USER_SPEAKING


def cancel_pending_tool(t: "TurnTaker") -> None:
    if t.pending_tool:
        t.cancelled.append(t.pending_tool)   # never committed, so nothing to undo
        t.pending_tool = None
```

The slice of `_words` in `interrupt` keeps `history`, which the model's next turn is built from, equal to what played before the user cut in. Without it, the model refers back to a recommendation the caller never heard. The word slice is a simplification: real systems count played milliseconds, which is the `audio_end_ms` below, and rely on the provider to cut its transcript to match.

> **In the companion repo.** `listing-studio/voice_turns/turns.py` is the state machine above, and `tests/test_voice_turns.py` drives it with scripted VAD events and a fake clock: the 699 ms and 700 ms endpointing boundary, the four-word truncation, the 200 ms false interruption that resumes, a pending tool call cancelled by speech, and a late playback-complete event that must not restore the unheard words. It runs in CI with no audio device and no model key.

Each vendor implements barge-in differently, and the differences decide who owns the transcript. On OpenAI's Realtime API over a WebSocket, you stop playback yourself and send `conversation.item.truncate` with `audio_end_ms`, the amount of audio that actually played; over WebRTC (the browser standard for real-time audio and video) and SIP (Session Initiation Protocol, the signalling the phone network uses), the server truncates the unplayed audio for you.[^7] Gemini Live discards the cancelled generation and sends an `interrupted` signal, but history keeps whatever was already sent to you, possibly more than played.[^4] On a Twilio phone stream, you send `clear` to drop queued audio and use named `mark` messages to learn which audio played. Match marks by name, because a `clear` also sends back every pending mark, and a returned mark is not proof that its audio played.[^8] False interruptions are the other half: LiveKit can require a minimum overlap duration and word count before it interrupts, and resumes the reply after a false interruption with `resume_false_interruption`.[^5]

In text, a two-second lookup shows a spinner. In voice it is two seconds of silence on the line. Speak a short filler, keep the line alive, or hand long work to a backend and come back. OpenAI's flow is a function call item carrying a `call_id`, your `function_call_output`, then a `response.create` to get the spoken answer.[^7] A barge-in can cancel a pending call (Gemini documents this),[^4] so track each call as pending, running or committed. A pending call can be dropped. A running one may still commit after the caller has changed their mind, so a tool with side effects must be idempotent (safe to apply twice) or must wait for confirmation before it commits. The state machine above shows the pending case: speech during `agent_thinking` drops an `add_to_cart` that had not run. Return structured errors the model can turn into a spoken apology or a retry offer, and see 4.3 Human-in-the-Loop for the confirmation step.

Use WebRTC from a browser or app, WebSockets between servers, and SIP for phone calls, or let a framework such as Pipecat or LiveKit Agents own the plumbing.[^16] OpenAI recommends WebRTC over WebSockets "for more consistent performance".[^10] SIP connects you to the phone network: OpenAI announces an incoming call with a webhook, and you accept it and control it over a WebSocket.[^11] Phone audio from Twilio Media Streams arrives as base64-encoded `audio/x-mulaw` at 8,000 Hz, mono,[^8] so you convert it whenever the model expects another format, such as the 24 kHz PCM in OpenAI's Realtime guide.[^7] An agent that hears its own voice through the user's speaker will interrupt itself. Browser capture can apply echo cancellation through the `echoCancellation` constraint;[^12] outside the browser, check that your audio stack supplies it.

Sessions end, and long audio fills the context window. OpenAI caps a Realtime session at 60 minutes.[^7] Gemini Live limits audio-only sessions to 15 minutes without context compression, closes each connection after about 10 minutes, and warns you with a `GoAway` message; sliding-window compression and session resumption extend it.[^4] Plan the reconnect as normal and carry the conversation over (see 5.4 Compaction and 7.1 Retry & Graceful Degradation).

## Cost

Voice is billed in two shapes, and they reward different designs. Token-billed speech-to-speech models charge for audio tokens. On OpenAI's Realtime API the conversation is resent with each response, so later turns cost more than early ones; caching helps on a best-effort basis, and truncation settings trade cost against how much the model remembers.[^14] Duration-billed offerings such as GPT-Live charge per second of session, with backend calls billed separately, and a WebRTC session bills a fixed initialisation period that is credited once the session runs.[^14] A cascaded pipeline adds three bills: speech-to-text, model tokens and text-to-speech, and you can swap any one for a cheaper vendor. Under token billing, keep turns short and truncate history hard; under duration billing, close idle sessions promptly. Prices move too fast to quote; model your own call lengths against live pricing (see 8.4 Controlling Cost).

## Evaluating it

Transcripts hide timing failures. A call where the agent cut the user off three times reads as a fine transcript. Test turn-taking deterministically, as the companion repo does, and measure latency on real calls, split by stage. For full-duplex models, Full-Duplex-Bench scores pauses, backchannels, turn changes and interruptions as separate behaviours.[^15] Timing tests cannot show that the right action happened, so pair them with assertions on business state, including a barge-in during a consequential action such as `add_to_cart`. The broader method is in 4.2 Evaluation.

## Gotchas

1. **The transcript lies by default.** Do nothing on barge-in and the history holds the whole reply, including words nobody heard. On a WebSocket transport, truncating is your job.[^7]

2. **The silence timeout sits in front of every reply.** Gemini's documentation suggests 500 to 800 ms of silence, and all of it passes before the model produces a token.[^4] Measure the stage breakdown before you change models.

3. **Audio reaches the tool-calling model with no text gate.** In speech-to-speech, raw audio goes straight to the model that calls your tools, with no transcript to inspect first, and hidden audio prompt injection is documented: one 2026 study reports a 69.10% average attack success rate against Gemini 3 Pro.[^13] Keep consequential tools behind confirmation, and see 4.4 Guardrails & Safety and 4.6 Prompt Injection & the Lethal Trifecta. A caller's voice is also weak evidence of who they are; treat it as a claim to verify (8.5 Locks, PII & Identity).

4. **The agent interrupts itself.** Missing echo cancellation makes the agent's own audio trigger the VAD. Test on a laptop speaker before you test on a headset.

5. **Coughs are not barge-ins.** Without a minimum overlap, every "mm-hm" stops the reply; set it too high and users cannot cut in. Tune it on real audio.

6. **Sessions die mid-call.** Session caps and connection lifetimes are short enough to hit in normal use.[^4][^7] A reconnect that loses context sounds to the user like the agent forgot them.

7. **Recording is regulated.** Call recordings and transcripts carry consent rules that vary by jurisdiction; take it to counsel (8.6 Governance & Compliance).

## In short

Write the latency budget before you choose a model, and build the turn-taking controller as tested code with a fake clock. For most teams that means a cascaded streaming pipeline on a framework such as Pipecat or LiveKit Agents, a silence timeout tuned on your users' recordings, playback that flushes on barge-in, and a transcript truncated to what was heard. Reach for speech-to-speech when prosody and the last few hundred milliseconds are worth losing the text checkpoint, and keep every tool with side effects behind confirmation either way.

<small class="chapter-meta">**Maturity: Emerging** (cascaded streaming pipelines are Established; native speech-to-speech and full-duplex are still settling) · *Who decides:* your code (transport, timeouts, flushing, truncation) / the model (semantic end-of-turn, the reply, tool calls) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: OpenAI, "Voice agents" (guide). <https://developers.openai.com/api/docs/guides/voice-agents>
[^2]: Stivers, T., et al., "Universals and cultural variation in turn-taking in conversation," *PNAS* 106(26) (2009). <https://doi.org/10.1073/pnas.0903616106>
[^3]: OpenAI, "Voice activity detection" (Realtime API guide). <https://developers.openai.com/api/docs/guides/realtime-vad>
[^4]: Google, "Live API: capabilities" and "Session management" (Gemini). <https://aistudio.google.com/docs/live-api/capabilities>; <https://aistudio.google.com/docs/live-api/session-management>
[^5]: LiveKit, "Turn detection and interruptions" (LiveKit Agents). <https://docs.livekit.io/agents/build/turns>
[^6]: Pipecat, "Smart Turn" (open-source end-of-turn model). <https://github.com/pipecat-ai/smart-turn>
[^7]: OpenAI, "Realtime conversations" (guide). <https://developers.openai.com/api/docs/guides/realtime-conversations>
[^8]: Twilio, "Media Streams: WebSocket messages." <https://www.twilio.com/docs/voice/media-streams/websocket-messages>
[^9]: Défossez, A., Mazaré, L., Orsini, M., Royer, A., Pérez, P., Jégou, H., Grave, E., Zeghidour, N., "Moshi: a speech-text foundation model for real-time dialogue" (2024). <https://arxiv.org/abs/2410.00037>
[^10]: OpenAI, "Realtime API with WebRTC" (guide). <https://developers.openai.com/api/docs/guides/realtime-webrtc>
[^11]: OpenAI, "Realtime API with SIP" (guide). <https://developers.openai.com/api/docs/guides/realtime-sip>
[^12]: MDN Web Docs, "MediaTrackConstraints: echoCancellation." <https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints/echoCancellation>
[^13]: Liu, et al., "Piggybacking on Perception" (2026), arXiv:2607.28165, reporting the 69.10% figure. <https://arxiv.org/abs/2607.28165> See also Chen, M., et al., "Hijacking Large Audio-Language Models via Context-Agnostic and Imperceptible Auditory Prompt Injection" (2026), arXiv:2604.14604. <https://arxiv.org/abs/2604.14604> Both are preprints.
[^14]: OpenAI, "Cost optimization" (voice agents guide). <https://developers.openai.com/api/docs/guides/voice-latency-cost>
[^15]: Lin, G.-T., et al., "Full-Duplex-Bench: A Benchmark to Evaluate Full-duplex Spoken Dialogue Models on Turn-taking Capabilities" (2025), arXiv:2503.04721. <https://arxiv.org/abs/2503.04721>
[^16]: Pipecat documentation <https://docs.pipecat.ai>; LiveKit Agents documentation <https://docs.livekit.io/agents>.

## See also

- [2.1 Tool Use](../the-unit/tool-use.md), for the tool loop a voice turn wraps.
- 6.3 Streaming & Agent UX, for the text-side streaming this chapter builds on.
- 4.3 Human-in-the-Loop, for confirming an action before a barge-in can strand it.
- 4.6 Prompt Injection & the Lethal Trifecta, for spoken injection.
- 5.4 Compaction, for keeping a long audio session inside the window.
- 8.4 Controlling Cost, for modelling per-minute and per-token voice spend.
- 8.7 Deployment & Runtimes, for the stateful workers a live call needs.
- 9.5 Computer Use & Browser Agents, the other agent that acts in real time against a live interface.

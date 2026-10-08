# AGENTS.md — Chan Robot Project

## Project direction

**Chan** is a personal home robot built on a stock **M5Stack StackChan with
CoreS3**, purchased from the official M5Stack store. Target this hardware and
confirm its actual revision before selecting drivers or firmware definitions.
This is an independent project with no dependency on dravix-os or its fork.

The agreed architecture is:

1. **ESPHome firmware** on the robot.
2. **A custom Chan integration in Home Assistant**, developed in this project.
3. **Home Assistant Assist** as the voice pipeline, with support for connecting
   a compatible live conversation integration.
4. **Frigate** as the backend for person/face recognition and tracking coordinates.

The Chan integration owns server-side coordination, personalization, and memory.
Do not introduce a separate coordinator service, HA add-on, or standalone web
application into the baseline architecture. Discuss a concrete limitation with
the owner before changing this boundary.

Reuse suitable open-source drivers and integrations after checking licenses and
hardware compatibility. Avoid importing a complete robot platform for one feature.
Requirements below are not claims of implemented or verified functionality.

## Intended experience and scope

Chan should feel alive during an explicitly activated interaction and remain
quiet and still otherwise. It must not constantly move, speak, greet passersby,
or start conversations simply because a person is detected.

After activation, the intended experience is a visible expressive face, smooth
head movement toward the interaction target, face tracking, and live Ukrainian
conversation with context across turns and voice interruption. Use the current
speaker's profile and separate memory when speaker identity is reliable.
Expressions and occasional gestures should suit the question and response
without becoming distracting.

The initial modes are **Sleep** and **Conversation**. Listening, thinking, and
speaking are conversation states, not additional modes. **Guard** is a future
extension; do not implement surveillance behavior or patrol in the initial scope.

Agree activation methods (touch, HA control, and/or wake word), inactivity
timeout, inactive screen/microphone/camera behavior, and servo rest behavior
before implementation. Ending an interaction must stop its voice session,
tracking, and scheduled gestures safely.

## Responsibilities

### ESPHome firmware

Firmware controls the microphone, speaker, display, camera, head servos, touch,
sensors, and immediate local feedback. It reports device state and executes
bounded commands from the Chan integration. Keep identity recognition, personal
memory, model credentials, and high-level behavior on the HA/server side.

Start from verified M5Stack definitions and schematics. Do not change GPIOs,
power rails, codecs, or wiring assumptions without checking the actual hardware
revision. A CoreS3 example does not prove support for the complete stock assembly.

Firmware must enforce movement and speed limits, smooth motion, and safe handling
of stale commands and connection loss. Basic local controls and safe motion
handling must remain available when optional backends fail.

Prefer the existing ESPHome native API and supported HA interfaces. Add an
external ESPHome component only for a demonstrated gap. Verify concurrent audio,
display, camera, and servo operation on the actual robot.

### Chan Home Assistant integration

The custom integration is required. It provides robot entities, actions, settings,
and diagnostics through standard HA UI and coordinates:

- Activation, termination, modes, and conversation state.
- The selected tracking target and association with the current speaker.
- Per-person context, profiles, and persistent memory.
- Expressions, gestures, and arbitration of head movement.
- Frigate data and the selected Assist/live voice integration.

Use nonblocking HA patterns and manage subscriptions, tasks, and connections
through the integration lifecycle. Keep audio, vision, memory, and behavior
independently testable without speculative frameworks.

Head movement must have one explicit coordinator. Tracking and gestures must
not issue competing servo commands. Do not add autonomous idle motion outside
an active interaction. Transitions and failures must cancel obsolete work.

Home Assistant authorizes and executes home actions through existing interfaces
and exposed tools. Face identity and personalized prompts must not grant
home-control permissions by themselves.

### Assist and live conversation

Assist is the voice path. Reuse a compatible existing live integration rather
than building an independent voice engine by default. Gemini Live through an
Assist-compatible integration is a candidate to verify, not a confirmed working
StackChan configuration. Isolate provider-specific behavior and keep providers
replaceable. Credentials remain on the HA/server side.

Verify the selected integration's audio transport, custom HA LLM tools, session
events, speaker-specific context, and conversation lifecycle. Document gaps
before adapting it. Do not infer these capabilities from the provider API alone.

Distinguish streamed voice turns, follow-up conversation without another wake
word, and full-duplex voice interruption. The requirement is interruption while
Chan speaks; listening again only after playback is not equivalent.

Verify simultaneous capture/playback, acoustic echo handling, interruption
propagation, response cancellation, and clearing buffered device audio on the
actual hardware. Cancel pending reactions for interrupted turns. Do not claim
barge-in works until measured on the robot.

The primary conversation and product UI language is **Ukrainian**, including
interaction with children.

### Expressions and gestures

Provide a constrained expression tool through the Chan integration's HA LLM API
when supported by the chosen voice integration. HA scripts are not the baseline
implementation of robot behavior.

The model may choose an expression and an allowed gesture from conversation
context. The integration validates requests and controls timing; firmware renders
the face and executes safe motion. Do not expose arbitrary servo angles as tools.

Listening/thinking/speaking feedback comes from actual voice state. Contextual
expressions are separate and are not measurements of a person's emotions.
Face recognition does not imply emotion recognition.

Prefer a small expression set, restrained intensity, and occasional gestures.
Associate reactions with the active session/turn, discard stale requests, and
return to a suitable neutral state. Tool calls alone do not guarantee word-level
synchronization; verify playback events before implementing finer alignment.

### Person profiles and memory

Maintain separate profiles and persistent memory for each reliably identified
speaker, distinct from temporary conversation context. Profiles may contain
preferred address, interaction style, and personalized prompt instructions.
Persistent memory should contain selected facts and useful summaries rather
than automatically retaining every transcript.

Use stable internal person identifiers and explicit mappings to Frigate names.
Choose small local persistence compatible with HA lifecycle and backups; avoid
unnecessary vector databases or external memory services. Provide a way to
inspect and delete personal memory.

Only load or write a person's memory when speaker association is sufficiently
reliable. For unknown or ambiguous speakers, use neutral context and avoid
reading or writing another person's private memory. A speaker change must not
leak previous personal context. Verify whether a new voice session is needed
to enforce this boundary.

### Vision and Frigate

Frigate is the intended source of identity and tracking coordinates. The built-in
robot camera is the initial candidate; confirm its use and verify transport,
frame rate, latency, and concurrent resource usage. Do not assume an ESPHome
camera is directly usable as a Frigate source.

Keep these tasks distinct:

- Tracking locates a face/person and supplies fresh position data for movement.
- Recognition estimates identity, including unknown and uncertain results.
- Speaker association decides whether a visible recognized person is speaking.

Check camera origin, object identifiers, coordinate meaning, timestamps, and
confidence. A person bounding box is not a face bounding box. Recognition events
are not necessarily a continuous coordinate feed. Measure whether Frigate's
interfaces are fresh enough for smooth tracking. Discuss demonstrated gaps
before adding a separate vision processor.

Do not equate the last recognized person with the current speaker. With multiple
people or ambiguous identity, use neutral address or request clarification.
Handle lost targets and stale frames without chasing old coordinates or switching
erratically between people. An unknown face alone does not establish a threat.

## Engineering principles

- Compact scope: few dependencies, small configuration surface, standard HA UI.
- Evidence: separate requirements, proposals, untested compatibility, and measured
  device results.
- Reuse: inspect components and record license obligations for code and assets.
- Reproducibility: pin dependencies where applicable and record verified ESPHome,
  HA, voice integration/provider model, and Frigate versions.
- Reliability: recover from network, provider, vision, and hardware failures
  without uncontrolled motion or cross-person memory access.
- Performance: measure audio latency, buffering, interruption response, camera
  throughput, and tracking behavior under concurrent operation.
- Privacy: keep credentials, personal images, face libraries, transcripts,
  personal memory, and private HA configuration out of Git. Prefer local vision.
- Incremental delivery: prove audio and interruption feasibility first, then
  camera/Frigate transport, tracking, personalization/memory, and richer behavior.
- Recovery: document installation, configuration, flashing, and recovery steps.

## Collaboration

Communicate with the owner in **Ukrainian**. Use **English** for identifiers,
technical documentation, commits, issues, and pull requests.

Discuss architecture and scope before implementation when the owner requests
a plan. Provide concrete installation and configuration guidance. This file
is enduring context, not authorization to implement every product goal.

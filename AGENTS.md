# Chan project instructions

## Current direction

The current conversation supersedes the previous Assist-first design.
Target the official M5Stack StackChan AI Desktop Robot with ESPHome.
Prioritize Gemini Live through kyvaith/pipecat-homeassistant.
HA Assist is a later separate mode. A custom Chan HA integration is not currently
required; do not rebuild the removed integration without a demonstrated need.

Intended modes: sleep, Pipecat conversation, HA Assist. Future work includes
faces, touch reactions, bounded gestures, Frigate tracking/identity, and
server-side personal prompts with a guest fallback. These are requirements, not
implemented capabilities. Coordinator placement remains to be decided when needed.

## Engineering

- Read docs/VALIDATION.md before changing hardware or audio.
- Preserve the demonstrated official BSP baseline.
- Do not change GPIOs, power rails, or codecs without source evidence.
- Prove Pipecat input/output and repeated start/stop on hardware before adding
  behavior. Compilation is not a successful device test.
- Account for shared audio resources and sample rates; prevent competing playback.
- Voice interruption requires measured echo control and buffer cancellation.
- Resolve the Y-angle mismatch before motion; enforce calibrated limits and use
  one owner to arbitrate tracking and gestures.
- Frigate identity does not establish the speaker or grant HA permissions.
- Keep credentials, personal profiles, and memory server-side and out of Git.
- Pin BSP, external drivers, and voice components for releases.
- Preserve license notices and Git history; do not delete historical tags/releases.
- No new release until physical validation; record exact tested versions.

## Communication

Use Ukrainian with the owner and English for identifiers, documentation, and
commits. Keep scope incremental. Distinguish observations from assumptions.

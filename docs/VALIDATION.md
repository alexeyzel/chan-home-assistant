# Device validation

## 2026-10-09: official M5Stack BSP

Hardware: official-store StackChan AI Desktop Robot; exact assembly revision
not independently confirmed.

- ESPHome: 2026.9.1.
- Upstream project label: m5stack.stackchan-bsp 2026.3.0.
- BSP/drivers: upstream main; exact build commit unknown.
- HA version and Pipecat Assist add-on version: not supplied.

Evidence: owner-provided logs and owner confirmation. Raw logs are not committed.

## Confirmed observations

- setup() completed; power and IO expanders initialized.
- 8 MB PSRAM available; Wi-Fi connected.
- Camera produced a frame, without establishing sustained streaming quality.
- Screen touch coordinates appeared after an initial driver-start error.
- Both servos reported positions; an initial ping warning subsequently cleared.
- HA TTS FLAC decoded as mono 48 kHz / 16-bit PCM. Playback started and stopped
  without an error in the supplied excerpt.
- Owner heard speech. Increasing HA volume made it acceptable, though not ideal.

## Open issues

- Y servo reported 190 degrees outside its configured 0..90 range. Resolve
  calibration/position conversion before commanding motion.
- FT6336U startup error followed by working touch events: repeat cold boots.
- AW88298 reported Initialized: NO despite setup completion and audible playback.
  Inspected upstream setup did not set the flag; this alone is not audio failure.
- Initial log covered about 21 seconds, not a long stability test.
- Microphone capture, head-touch transitions, and concurrent load remain unverified.
- Pipecat YAML was proposed in chat, but compilation and device operation have
  not been confirmed. It is not a tested release.

## Next acceptance test

1. Record Pipecat add-on version and exact dependency commits.
2. Validate and compile the proposed Pipecat configuration.
3. Confirm authenticated connection, microphone transcript, and audible reply.
4. Repeat conversation turns and explicit start/stop cycles.
5. Verify stop clears audio and microphone streaming; test reconnection.
6. Evaluate echo and interruption separately after basic conversation works.

Before a new release, record results, pin sources, and document recovery and
limitations. No new release was created by this cleanup.

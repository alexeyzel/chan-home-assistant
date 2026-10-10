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
- Head-touch transitions and sustained concurrent load remain unverified.
- Subsequent owner tests confirmed clear microphone recordings and audible
  Pipecat replies with barge-in disabled. Exact deployed YAML/revisions are still
  needed for reproducibility; this is not a tested release.
- Enabling barge-in produced repeated `Parent bus is busy` speaker start errors
  while capture continued. Reverting restored conversation, per owner report.
  See FULL_DUPLEX_POC.md for the next milestone.

## Next acceptance test

1. Record Pipecat add-on version and exact dependency commits.
2. Validate and compile the proposed Pipecat configuration.
3. Confirm authenticated connection, microphone transcript, and audible reply.
4. Repeat conversation turns and explicit start/stop cycles.
5. Verify stop clears audio and microphone streaming; test reconnection.
6. Evaluate echo and interruption separately after basic conversation works.

Before a new release, record results, pin sources, and document recovery and
limitations. No new release was created by this cleanup.

## 2026-10-10: experimental duplex build validation

- Local toolchain: ESPHome 2026.9.1, ESP-IDF 5.5.5, Windows, Python 3.12.
- Raw duplex and AEC example configurations passed ESPHome schema validation.
- Final raw duplex example (including diagnostics) compiled successfully:
  image 1,180,615 bytes, static DIRAM usage 120,655 / 341,760 bytes. These figures
  do not measure runtime heap/PSRAM headroom or audio performance.
- AEC variant compiled successfully: image 1,236,623 bytes, static DIRAM usage
  123,879 / 341,760 bytes. No device-level AEC effectiveness is claimed.
- Generated C++ contains Audio Stack microphone/speaker, no legacy I2S
  microphone/speaker, and both ES7210/AW88298 are configured for 48 kHz.
- Generated AW88298 source hash matches the pinned M5Stack checkout.
- Builds used placeholder Wi-Fi credentials. Do not install their local binaries;
  compile the YAML in the owner's ESPHome environment with real secrets.
- No experimental firmware has been installed or physically validated.

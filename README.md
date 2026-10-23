# Chan for Home Assistant

> **Development status: experimental / work in progress.**
> This project is being developed with **OpenAI Codex**, with hardware testing
> performed by the owner. It is not a stable or production-ready firmware.
> Historical releases are kept as drafts. A new public release will follow only
> after a working version is validated on the robot.

ESPHome firmware experiments for the official M5Stack StackChan AI Desktop Robot,
with Gemini Live through [Pipecat Assist](https://github.com/kyvaith/pipecat-homeassistant).

Active development is maintained on **main**. This branch is experimental;
merging development here does not create a release.

## Current state — 2026-10-23

**Active candidate:** [headroom / pre-AGC audio lab](firmware/stackchan-audio-lab-headroom.example.yaml).
**New candidate:12dB and simultaneous pre/post-AGC capture; hardware testing pending.**
Compiled with ESPHome2026.10.0 / ESP-IDF5.5.6; ESP32-S3 image verified.
The preceding buffered lab had partial hardware progress in log41.
This lab deliberately omits Pipecat to isolate playback, microphone saturation and AFE.

The preceding native-16k Lab 1 recorded clear speech without clipping. Lab 2
revealed about 21–23% clipped microphone samples and irregular playback feeding.
The buffered candidate plays7s in7.098s without middle-playback underruns. At18dB,
microphones still clip0.77%/0.32%, and quiet processed speech is low. Echo control
and reliable interruption remain unproven. See [log41 analysis](docs/LAB41_ANALYSIS.md).

The owner previously demonstrated Pipecat replies and some human interruptions,
but ordinary-voice interruption, startup reliability and recognition remain
inconsistent. There is no qualified full-duplex firmware release.

## Continue in a new chat

Read [AGENTS.md](AGENTS.md), then [CURRENT_STATE.md](docs/CURRENT_STATE.md).
The latter identifies the exact active artifact, latest evidence, unresolved
questions and next action. [Documentation index](docs/README.md) separates current
instructions from historical experiments.

- [Current test protocol](docs/HEADROOM_AUDIO_LAB.md)
- [Experiment history and firmware catalog](docs/EXPERIMENT_HISTORY.md)
- [Pinned references and dependencies](docs/REFERENCE_INDEX.md)
- [Build and workspace notes](docs/DEVELOPMENT.md)
- [Chronological evidence ledger](docs/VALIDATION.md)

Copy the entire active YAML into ESPHome, set your capture password and keep
Wi-Fi credentials in Secrets. No manual component/header uploads are needed.
For Lab 1, count roughly two seconds, say a short normal-volume sentence, then
wait for END without Stop. Exact timing is unnecessary. Save all six WAVs, including pre-agc.wav, before
Lab 2; remain silent during Lab 2. See the protocol for download links and limits.

## Product direction

ESPHome; sleep, Gemini Live/Pipecat, and later HA Assist modes. Future work:
faces/emotions, touch reactions, bounded gestures, Frigate person tracking and
identity, server-side personal prompts plus a guest profile. These are intended
features, not completed capabilities. Audio reliability comes first.

User volume is a comfort control, not an AEC tuning knob. Keep the official board
power/pins and one I2S owner. Resolve the Y-servo position mismatch before motion.
Keep credentials, personal profiles and recordings out of Git. Preserve rollback
artifacts and exact source revisions; do not publish a release until hardware
acceptance. The old Assist-first integration history/tags v0.1.1 and v0.1.2 are
not releases of the current Pipecat direction.

## License

Original material: [MIT](LICENSE). External software retains its licenses;
see [THIRD_PARTY.md](THIRD_PARTY.md).

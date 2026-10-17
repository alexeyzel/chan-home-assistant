# Chan for Home Assistant

ESPHome project for the official M5Stack StackChan AI Desktop Robot.

This repository is being rebuilt from a hardware baseline tested on the owner's
robot. Half-duplex Gemini Live conversation was confirmed by the owner through the existing
[Pipecat Assist add-on](https://github.com/kyvaith/pipecat-homeassistant).
There is no new tested Pipecat firmware release yet.

## Full-duplex experiment

Current AFE test: [performance-profile YAML](firmware/stackchan-afe-perf.example.yaml), adapting
the Waveshare SR/MMR graph and its compiler/cache/PSRAM performance profile to StackChan.
The first [full AFE YAML](firmware/stackchan-full-afe.example.yaml) suffered sustained
input drops and missing output in log 31; keep it only for comparison. See the
[port notes and test procedure](docs/AFE_PORT.md). Hardware testing is pending.

Current copy-paste experiment: [startup recovery and uplink gain YAML](firmware/stackchan-hwref-uplink.example.yaml).
It adds a bounded retry for a connection lost immediately after Start and 4x
post-AEC microphone gain, adjustable through the `pipecat_mic_gain` substitution.
Both changes await owner testing. Gain also amplifies residual echo and noise.
The [hardware reference baseline](firmware/stackchan-hwref.example.yaml) restored
audible replies and enabled human interruption in log 26, but log 27 showed that
interruption remains unreliable at ordinary speaking volume. Preserve it for
comparison and rollback. See [validation notes](docs/VALIDATION.md) and
[source research](docs/AUDIO_REFERENCE_RESEARCH.md).
The separate [160 ms reference-delay probe](firmware/stackchan-duplex-probe.example.yaml)
suppressed self-interruption in one owner test, but deliberate human interruption
failed at maximum volume. It remains a limited baseline, not a completed POC.
Both configurations are single files with remote dependencies.

The immediate milestone is simultaneous capture/playback and echo-controlled
voice interruption. Start with [raw duplex](firmware/stackchan-duplex.example.yaml),
then test [AEC](firmware/stackchan-duplex-aec.example.yaml). Follow the
[device test instructions](docs/DUPLEX_TEST.md). These configurations are
experimental; retain the owner-tested half-duplex firmware for rollback.

## Current baseline

Copy [official-baseline.example.yaml](firmware/official-baseline.example.yaml)
into ESPHome Device Builder. Supply credentials through ESPHome Secrets,
validate, compile, and install. Preserve the working binary before making changes.

The baseline booted with ESPHome 2026.9.1. Home Assistant TTS was audible through
media_player.stackchan; raising HA volume made it acceptable.
See [validation notes](docs/VALIDATION.md) for remaining issues.

The example reproduces the tested configuration using upstream main. Rebuilding
can fetch changed code: the successful build's exact upstream commit is unknown.
Pin both the BSP and external drivers before publishing a new firmware release.

## Intended behavior

- ESPHome firmware.
- Sleep, Gemini Live conversation via Pipecat, and later a separate HA Assist mode.
- Local face animation, touch reactions, and bounded conversational gestures.
- Frigate identity and tracking with calibrated coordinate mapping.
- Server-side personal prompts and an unknown/guest profile.

Pipecat microphone capture and audible replies were confirmed by the owner.
Simultaneous capture/playback and some human interruptions were demonstrated.
Reliable interruption across volumes, tracking and personalization remain unverified. Do not command motion until the reported
Y-angle mismatch is resolved.

## Development and releases

Prove Pipecat input/output, repeated turns, and start/stop first. Add behavior
incrementally. Keep credentials, raw logs, personal profiles, and local device
configuration out of Git. Publish only after physical validation and dependency
pinning, with exact versions and limitations recorded.

The previous Assist-first integration, firmware overlays, HACS metadata, patch,
and associated tests/build workflow have been removed from the current tree.
They remain recoverable in Git history and historical tags v0.1.1 and v0.1.2.
Those tags are not releases of the new Pipecat direction. This cleanup does not
uninstall anything already installed in Home Assistant.

## License

Original material: [MIT](LICENSE).
External software retains its own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).

### AFE runtime diagnostic test

[Copy-paste YAML](firmware/stackchan-afe-profile.example.yaml) adds task CPU and
AFE callback timing measurements while preserving the afe-perf audio settings.
[Procedure and interpretation](docs/AFE_PROFILING.md). Hardware results pending.

[Core-balance test YAML](firmware/stackchan-afe-balanced.example.yaml) moves only
the audio bus task to core 1 based on log 33; profiling and audio settings remain.
See [test criteria](docs/AFE_PROFILING.md#core-balance-follow-up-log-33).

### Isolated audio lab

[Local lab YAML](firmware/stackchan-audio-lab.example.yaml) captures pre/post-AFE
audio without Pipecat. Set its capture password first.
[Recording/download procedure](docs/AUDIO_LAB.md). Hardware validation pending.

# Chan for Home Assistant

ESPHome project for the official M5Stack StackChan AI Desktop Robot.

This repository is being rebuilt from a hardware baseline tested on the owner's
robot. The next milestone is Gemini Live through the existing
[Pipecat Assist add-on](https://github.com/kyvaith/pipecat-homeassistant).
There is no new tested Pipecat firmware release yet.

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

Pipecat on the robot, microphone capture, echo handling, interruption, tracking,
and personalization remain unverified. Do not command motion until the reported
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

# Validation record and first-device checklist

## Software baseline

Prepared on 2026-10-08 for version 0.1.0:

| Component | Version/reference |
| --- | --- |
| Home Assistant Core | 2026.10.0 |
| HA test Python | 3.14.2 |
| ESPHome | 2026.9.1 |
| ESPHome build Python | 3.12.10 |
| ESP-IDF | 5.5.5 |
| M5Stack ESPHome drivers | cc708ddcc9dea7cfc746b408d2495ce281bbf2d2 |
| Gemini Live integration inspected | matt123p/ha-gemini-live 1.0.9, d4ad0e523eca92f1c395e82da14d6da0fafd71be |

ESPHome configuration validation and a full ESP32-S3 compile succeeded. The
original Windows build path with spaces failed during ESP-IDF linker-script
generation; rebuilding in a path without spaces succeeded. The compile used
public example secrets, not deployment credentials. That binary is not a
ready-to-flash personal deployment and is not published.

All Chan modules import on the pinned HA release. All 22 automated tests passed.
The tests use actual HA
classes with simulated firmware entities; they do not prove audio, display,
touchscreen, provider interoperability, or physical behavior on a robot.

A local SDK check reproduced a ToolResult serialization failure in the inspected
Gemini Live integration. The supplied compatibility patch passed success/error/
nested result conversion and Google GenAI 2.21.0 FunctionResponse validation
without cloud calls. See [the patch instructions](GEMINI_LIVE.md).

## Hardware checks (not yet performed)

Record results and actual versions locally. Do not upload credentials, face
images, transcripts, or private HA configuration with test reports.

1. Confirm the SKU, controller revision, and official firmware recovery route.
2. Boot with screen dark, no voice capture session, and no head movement.
3. Add ESPHome to HA, configure an Assist pipeline, then add the Chan integration.
4. Activate from HA. Confirm the face appears and microphone audio reaches Assist.
5. Ask a short Ukrainian question. Measure time from end of speech to first
   audible response and confirm intelligible playback.
6. Check state feedback against actual listening, processing, and playback.
7. Test each expression manually and verify the eight-second reset.
8. Enable optional touch activation and test activation and stop by screen tap.
9. Stop from HA during playback; measure residual audio and verify the screen
   remains dark even if late provider/pipeline events arrive.
10. Disconnect HA and Wi-Fi separately. Confirm safe inactivity and no automatic
    reactivation after reconnection. Reboot and confirm the same default.
11. Reactivate and verify conversation context was reset. Within one activation,
    verify follow-up context across turns.
12. Test Gemini Live with a dedicated pipeline and both Assist and Chan LLM APIs.
    Inspect expression tool calls, device-ID propagation, and timing.
13. Start a new turn or stop during a delayed expression tool call; verify no
    stale reaction appears in the next interaction.

## Explicitly unverified requirements

- Ukrainian live conversation quality and latency on the physical robot.
- Streaming playback compatibility with the selected Gemini Live integration.
- Reliable voice interruption, acoustic echo cancellation, and full duplex.
- Camera transport into Frigate and fresh tracking coordinates.
- Simultaneous audio/video/display/servo operation and movement calibration.
- Reliable current-speaker association, profile injection, and isolated memory.

These require later hardware milestones. No guard behavior, tracking, motion,
or personal memory is claimed by this release.

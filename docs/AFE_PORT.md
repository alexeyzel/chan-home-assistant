# StackChan full AFE experiment

Source configuration: [Waveshare Audio VA](https://github.com/jyoushiki/esphome-waveshare-esp32-s3-audio-va/blob/c86ecd3c5124db85181c03ad35aec6578b82b849/waveshare-va.yaml).
The adapted AFE settings retain the upstream MIT notice in LICENSES/waveshare-audio-va-MIT.txt.

Copy firmware/stackchan-full-afe.example.yaml in full. All components are fetched
remotely at pinned revisions. No local headers or uploads are required.

## Reused processing graph

- Espressif AFE SR/low_cost, MMR (two microphones and a playback reference).
- AEC filter length 4, aggressive NLP, two-microphone Speech Enhancement/BSS.
- No separate NS stage, matching ESP-SR's dual-microphone graph.
- Local VAD disabled: continuous processed audio goes to Pipecat's detector.
- Post-AFE AGC enabled, compression gain 15, target level 3.
- Feed/fetch storage in PSRAM; ESP-SR pinned at 2.5.5.

## StackChan adaptations

- Retain official power rails, GPIOs, ES7210 and AW88298 driver.
- Retain the owner-tested 48 kHz four-slot bus and AW88298 0x14E8 clock setting.
- Capture microphone slots 0 and 2; slot 1 remains hardware reference. This
  matches the ES7210 0x4231 layout with MIC1/2/3 selected. The second physical
  microphone's acoustic quality still needs device verification.
- Keep the previous 6 dB microphone gain and 0 dB reference gain. The donor's
  30 dB analog settings belong to another board and feedback circuit.
- Connect AFE directly as processor_id. Remove the old synchronous AecProbe
  wrapper so AFE's asynchronous feed/fetch interface is not obscured.
- Set Pipecat MicrophoneSource gain to 1: no fixed x4 multiplication after AGC.
- Retain patched Audio Stack 4541119 and matching upstream esp_afe 0482d74.
  This avoids replacing the tested codec-less TX fix during the AFE comparison.
- Remove standalone AEC mode buttons; they cannot select modes on this AFE graph.
- Keep volume, Speaker Test, diagnostics and bounded initial connection retry.

## What this does not establish

This is a source-based port, not a verified StackChan release. Compiling does not
prove speech preservation, usable barge-in, or both microphone channels.
Pipecat's previously observed WebSocket disconnections are not fixed by changing
AEC to AFE; the five-second startup retry is still only an initial workaround.

## Owner test

1. Enable Pipecat audio recording before opening a fresh server session.
2. Press Audio Diagnostics after boot; retain the boot and test log.
3. In quiet, start and say: "Rozkazhy meni dovhu istoriiu" in Ukrainian at normal
   loudness. Compare the input recording with the spoken phrase, not just the
   returned transcript. Repeat three times at the same position.
4. Ask for a long reply. First remain silent to check for self-interruption,
   then say a complete stop request at ordinary loudness during playback.
5. Retain input/output recordings, speaker volume and distance. Only after the
   first comparison succeeds repeat at other audible volumes.

Inspect runtime AFE configuration, both mic-slot levels, hardware reference,
feed/fetch drops/timeouts, and Pipecat connection status. A disconnect invalidates
that segment as a test of speech understanding. Use the previous YAML to roll
back. No robot is flashed automatically.

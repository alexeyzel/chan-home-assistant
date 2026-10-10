# StackChan full-duplex Pipecat proof of concept

Priority agreed with the owner on 2026-10-10: prove simultaneous capture and
playback, echo control and conversational interruption before faces, movement,
Frigate, or HA Assist. The result should be reusable in a standalone firmware or
potential Dravix integration. No hardware-validated full-duplex build exists yet.

## Evidence

- Owner confirmed audible Pipecat/Gemini replies with barge-in disabled, including
  recovery after reverting the barge-in experiment.
- With barge-in enabled, the supplied device log reports `Parent bus is busy`
  and repeated speaker driver start failures while microphone uplink continues.
- Incoming audio accumulates in the playback queue. This is a local audio-bus
  ownership failure, not evidence that Gemini failed to generate audio.
- Earlier WebSocket failures remain a separate stability issue; their cause has
  not been demonstrated or fixed.
- Dravix's inspected StackChan config also stops microphone consumers to release
  the shared I2S bus before playback. It is not a demonstrated duplex solution.

## Preferred implementation candidate

Evaluate https://github.com/n-IA-hane/esphome-audio-stack at inspected revision
`0482d741a938378ef948e3b8f3dd31536f9f2cc9`.

It provides shared-bus duplex, standard ESPHome microphone/speaker interfaces,
resampling, and optional AEC/AFE. ES7210 input codec support exists. No StackChan
profile or AW88298 codec backend was found in the inspected checkout. Integration
must establish AW88298 initialization, enable/mute and volume handling; do not
assume replacing the speaker platform preserves its audio_dac callbacks.

Preserve official board GPIOs, power configuration and proven codec behavior.
One owner must allocate and configure the shared I2S RX/TX channels. Do not remove
the stock mutex or declare competing masters on the same clock pins.

Shared RX/TX must agree on physical sample rate and slot format. The existing
16 kHz microphone and 48 kHz playback settings cannot simply be combined as two
independent masters. Select a codec-compatible common bus format, then convert
capture to Pipecat's 16 kHz PCM and playback from its 24 kHz PCM. Verify the
format against both codec drivers before choosing the experimental configuration.

Start echo cancellation with a software reference from actual playback PCM.
Do not assume a hardware feedback channel exists without schematic evidence.

## Staged acceptance

1. **Duplex transport:** start with processing disabled. Play a known recording
   while capturing speech. Verify both signals, correct speed, no bus errors,
   no growing queues and no resets. This alone is not an echo-safe live assistant.
2. **Echo control:** compare capture with AEC off/on at the same output level.
   Confirm the robot's reply is suppressed while overlapping human speech remains
   intelligible. Include periods with nobody speaking.
3. **Pipecat interruption:** enable barge-in with processed input. Confirm a human
   interruption stops queued/local output and receives a relevant new answer.
   Measure interruption latency and check for stale audio after cancellation.
4. **Repeatability:** at least ten interruption trials, a ten-minute conversation,
   repeated Stop/Start, cold boot and a network reconnection. Record failures,
   output volume, dependency revisions, and actual measured latency.

Keep the last working half-duplex YAML as a rollback artifact. Obtain the exact
owner-tested configuration and installed add-on version before claiming a
reproducible baseline. Publish a tested PoC only after device validation; preserve
audio transport/processing as a separable layer for possible Dravix reuse.

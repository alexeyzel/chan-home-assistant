# Experimental duplex firmware: device test

These are experimental source configurations, not hardware-tested releases.
Keep your actual working half-duplex YAML and binary. The official baseline in
this repository does not include your working Pipecat overlay.

## Install the raw duplex experiment

1. Copy `firmware/stackchan-duplex.example.yaml` into your existing ESPHome device
   configuration. Preserve its actual name, Wi-Fi secrets and any API/OTA security
   settings from your local configuration. The supplied name matches the earlier
   owner logs (`stackchan-test`). Do not replace credentials with build placeholders.
2. Use ESPHome 2026.9.1, validate, then build and install over OTA. A clean build
   is appropriate when replacing the audio implementation. No flash erase or
   factory USB installation is required for this source change.
3. Open logs from boot. Confirm ES7210 is configured for 48000 Hz, Audio Stack
   output microphone rate is 16000 Hz, and Pipecat reports `Barge-in: YES`.
   There must be no legacy `i2s_audio.speaker`/microphone driver in the configuration.
4. Check `Duplex Volume` in HA; start around 80%. Start Pipecat, ask a question,
   then speak briefly during the answer. Save both Audio debug Input and Output
   and device/server logs. Press `Audio Diagnostics` during playback.
5. Verify the input recording still captures your voice during audible output,
   at normal speed. `Audio Stack state: duplex` is useful evidence of requested
   activity, but does not by itself prove capture/playback quality.

Without AEC the device may hear and interrupt itself. This first test establishes
the audio path only. Stop if output is distorted, the device resets, capture
stops, or speaker initialization fails; preserve the log before reverting.

## Then test AEC

Place both example YAML files in the same ESPHome directory. Build the AEC file;
its relative include must point to the raw duplex file. If you renamed that file
to `chan.yaml`, change the include accordingly. Do not run two firmware builds
with the same device name/build directory simultaneously.

The AEC variant adds a software playback reference and an `Echo Cancellation`
switch, initially on. At a fixed volume, compare recordings with it on and off:

- With nobody speaking, does speaker audio trigger a false user turn?
- When you speak over the reply, is your speech intelligible in the input WAV?
- Does Pipecat stop the previous reply and answer the new question?
- Does stopped audio remain stopped rather than leaking from a downstream buffer?

Record the add-on version, exact YAML, volume, distance, and ten interruption
trials. A ten-minute conversation plus repeated Stop/Start and a cold boot are
required before calling this a working full-duplex PoC.

## Implementation boundaries

- Official M5Stack power/reset and I2C codec initialization remain in use.
- Audio Stack exclusively owns I2S RX/TX at 48 kHz, 16-bit slots, Philips format,
  MCLK 256x. ES7210 uses that same rate and converts to 16 kHz through Audio Stack.
  Pipecat's 24 kHz playback is resampled to 48 kHz.
- The AW88298 remains initialized/enabled by the official driver. The new speaker
  uses software volume; it does not invoke the old speaker's audio_dac mute hooks.
  No speculative register writes or duplicated I2S masters were added. Hardware
  compatibility of this shared format still needs the physical test.
- Camera and BLE provisioning are omitted from this audio experiment. The old
  media_player is removed to prevent another producer claiming playback.
- The BSP contains a mutable external driver source; our later pinned source
  takes precedence in ESPHome's component loader. The resolved build sources
  must match the pinned commit before publishing a release.
- AEC timing/gain and WebSocket stability remain measurement tasks. Neither
  validated YAML nor a successful compile establishes successful device audio.

# Experimental duplex firmware: device test

> Status note (2026-10-22): Historical raw/standalone-AEC experiments; self-interruption persisted. Do not restart this sequence as the next action. Read CURRENT_STATE.md.

## Current inline signal probe

Current controlled experiment delays the AEC reference by 2560 samples (160 ms
at 16 kHz). It does not delay speaker playback or uplink mic audio. The envelope
probe now sees the delayed reference, so `aec_delay` reports residual lag.
The reference history is cleared after a processing gap longer than 250 ms.
This is an experiment based on log 21, not a calibrated hardware constant.
Keep audible volume fixed for the first comparison. If feedback improves,
test deliberate interruption and then different comfortable volume levels.
The legacy upstream full-frame reference gating remains unchanged.

The latest probe also estimates coarse envelope lag between pre-AEC mic and
the reference supplied to AEC. It uses 4 ms mean-absolute-value bins, a 1.024 s
history, a common 512 ms comparison interval and lags from -256 to +256 ms.
Positive lag means the mic envelope follows the reference. It logs every
2.048 s of processed audio. Correlation and the best alternative more than
12 ms away are reported; edge hits, weak or similarly strong alternatives
are ambiguous. No adaptive delay adjustment is made. This is not a DMA
timestamp measurement or a phase-accurate acoustic path estimate.

At boot ADC gain is set to 18 dB and the master volume curve floor to -30 dB.
The speaker output layer stays at unity. 50% now means -15 dB rather than
-24.5 dB; 0% remains mute and 100% remains unity. Compare with previous tests
at matched audible loudness, not equal slider positions.
Begin at 30%, set a comfortable audible level, then request a long answer
and remain silent. Collect `aec_delay`, `aec_probe` and performance lines.
Do not infer AEC effectiveness from an envelope correlation alone.

Use `stackchan-duplex-probe.example.yaml` as one copy-paste configuration.
The wrapper is installed at boot priority 1000, before the audio components
start; it delegates processing unchanged to the pinned standalone AEC.
It logs RMS/peak for mic and reference before processing and output immediately
after processing every 32 frames (about 1 second at the current frame size).
Output levels exclude any subsequent microphone gain applied by Audio Stack.
`zero_ref` counts all-zero/missing reference frames; `failed` counts unsuccessful
processor calls. Idle reference silence is normal. Compare during robot speech.
This does not record three audio tracks; the added envelope estimate is coarse.

The output speaker layer is unity; use Duplex Volume as the volume control.
Start at 50%, then choose an audible level before starting the test.
With Echo Cancellation on, request a long story and remain silent for 15 seconds.
Stop if it self-interrupts repeatedly. Return logs including `aec_probe` lines
and the Pipecat Input recording. No need for another SR comparison yet.

## Previous single-file FD experiment

Copy the entire `stackchan-duplex-fd.example.yaml` into the existing device YAML.
Only the existing ESPHome Wi-Fi secrets are needed; all dependencies are remote.
Retain local API/OTA credentials if configured. The older two-file AEC example
below is historical and is not required for this test.

Start with Echo Cancellation on and Duplex Volume at a clearly audible, fixed
level. `fd_low_cost` is selected at boot. Ask for a story and remain silent for
15 seconds; then deliberately interrupt once. Capture the Input/Output WAVs and
device logs. Diagnostics are automatic every 10 seconds while capture runs.

To compare the old mode, press AEC Mode SR, wait for the actual mode in the log,
then press Pipecat Start. The buttons stop the local conversation before changing
mode; they do not restart it automatically. Return with AEC Mode FD. A failed
upstream mode change can retain the previous mode, so inspect the configuration
dump rather than treating a button press as proof of success.

Telemetry reports frame timing, underruns, memory and queue state. The standalone
AEC implementation does not populate AFE-specific counters; zeros in those lines
are not proof of echo suppression. This build does not measure reference RMS or
acoustic delay. Input recordings and controlled A/B tests remain necessary.

The separate Gemini session-expiration failure is not fixed by this YAML. If
the server reports `ready=False session=False`, restore the backend connection
before comparing AEC modes.

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

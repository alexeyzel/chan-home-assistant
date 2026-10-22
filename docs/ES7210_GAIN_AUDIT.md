# ES7210 gain audit and local lab v2 (2026-10-20)

> Status note (2026-10-22): Historical gain audit. Official36dB improved quiet capture but clipped during playback (log40). The current18dB buffered-lab trial is unvalidated;36dB is not a duplex recommendation.

## Evidence from pinned source snapshots

| Reference | Gain configuration | PCM path |
| --- | --- | --- |
| Our local lab v1 | ES7210 microphones 6 dB; ADC channel 2/reference 0 dB | PCM16, 48 kHz four-slot TDM -> selected 2 microphones + reference -> 16 kHz -> AFE/post-AGC |
| Official StackChan ESPHome BSP, cc708ddcc9dea7cfc746b408d2495ce281bbf2d2 | `audio_adc.mic_gain: 36` | microphone PCM16 at 16 kHz; not our shared 48 kHz duplex path |
| Official StackChan voice-assistant base, same commit | `mic_gain: 36` | PCM16 microphone configuration |
| Stock StackChan, 1b5765599fba8aaad1811d9a79358ccc7051f5f3 | `input_gain_ = 60`, passed to codec API for channel 0 | input/output 24 kHz, PCM16; Read copies codec PCM without an additional multiplier |
| Waveshare AFE reference, c86ecd3c5124db85181c03ad35aec6578b82b849 | ES7210 microphones 30 dB AND reference 30 dB | PCM16 48 -> 16 kHz, sparse TDM, MMR AFE; post-AGC gain 15 |
| Dravix, 07d468506490dc1ae40be4a0af82e132aeee13e1 | inherits ES7210 36 dB from its exact pinned BSP; wake-word gain factor 4; Assist auto_gain 31dBFS and volume_multiplier 2 | inherits BSP microphone; additional processing is not equivalent to analog ADC gain |

Sources:
- https://github.com/jyoushiki/esphome-waveshare-esp32-s3-audio-va/blob/c86ecd3c5124db85181c03ad35aec6578b82b849/waveshare-va.yaml
- https://github.com/m5stack/esphome-yaml/blob/238ba9825e7874d5626709631dae6be92e861b17/examples/kit/stackchan-bsp.factory.yaml
- https://github.com/m5stack/esphome-yaml/blob/cc708ddcc9dea7cfc746b408d2495ce281bbf2d2/examples/kit/stackchan-bsp.factory.yaml
- https://github.com/m5stack/esphome-yaml/blob/cc708ddcc9dea7cfc746b408d2495ce281bbf2d2/common/stackchan-voice-assistant-base.yaml
- https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/cores3_audio_codec.cc
- https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/config.h
- https://github.com/YossiKon/dravix-os/blob/07d468506490dc1ae40be4a0af82e132aeee13e1/deploy/esphome/stackchan-dravix.yaml

Dravix pins a different BSP (238ba9825e7874d5626709631dae6be92e861b17).
Fetched that exact historical commit and verified mic_gain=36 and PCM16/16 kHz
in its StackChan BSP. Dravix's comment calling the mic
PDM is not evidence of hardware topology. Stock's requested 60 is not proof of
60 dB analog gain: our installed esp_codec_dev ES7210 driver saturates its mapping
at 37.5 dB. Its enum maps 6 dB to 2 and 36 dB to 13.

Our 16-bit RX path extracts selected int16 samples directly, then calls Espressif
rate conversion; the separate 32-to-16-bit converter is used only for 32-bit input.
No explicit right-shift or fixed attenuation was found in the selected 16-bit path.
This is source evidence, not a measured proof of converter frequency response.

## Owner's Lab 1 measurements

All four WAVs contain 113152 samples (7.072 seconds), mono PCM16/16 kHz.
Mic0 peak -42.63 dBFS, RMS -64.10; mic2 peak -44.20, RMS -63.93;
processed peak -36.11, RMS -57.52; reference peak -74.75, RMS -89.75.
No all-zero 256-sample blocks; log reports missing_blocks=0 and skipped=0.
The low reference is expected in a silent-playback test and does not establish
reference quality during playback. This run ended without LOCAL TEST END and
without retained stimulus. Exact interruption cause is not established by the log.
CPU snapshots overlap idle and active periods; they do not prove steady-state headroom.

## Change and next test

Use `firmware/stackchan-audio-lab-v2.example.yaml`. Microphone hardware gain becomes
36 dB, matching the official StackChan BSP; reference stays 0 dB. No extra digital
gain, AFE algorithm change, pin, amplifier gain or sample-format change is made.
The 30 dB increase corresponds to about 31.6x amplitude if the analog path is linear.
It is a test hypothesis, not a guaranteed acoustic improvement or final AEC tuning.

After audio starts, adc_probe reads ES7210 format registers 0x11/0x12 and gain
registers 0x43..0x46 over the existing I2C bus. Expected low nibbles: MIC1/MIC2=13,
MIC3/reference=0. Failed reads are explicitly logged; no diagnostic register writes.
Every second pcm_probe logs existing native 48 kHz slot RMS probes before resampling.
After capture stops, it logs full-record 16 kHz RMS, peak and near-clipped samples
(abs>=32760) for both microphones, reference and processed output. Native probes
are sparse per-frame snapshots, not aligned full-record statistics; compare trends,
not exact RMS differences between these windows.

Repeat ONLY Lab 1 at the same distance and ordinary voice. Wait for LOCAL TEST END
without pressing Stop. Download the same four files, retain full log. If manually
stopped, v2 explicitly logs early stop and retains a partial quiet stimulus. Do not
run playback tests until quiet speech is clear and unclipped. Authentication and
RAM-only storage are unchanged; set capture_password before installing.

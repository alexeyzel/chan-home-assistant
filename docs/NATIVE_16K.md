# Native 16 kHz shared audio bus (2026-10-20)

The owner chose to test 16 kHz directly instead of first testing 36 dB at 48 kHz.
Two standalone copy-paste configurations are provided:

- firmware/stackchan-audio-lab-16k.example.yaml: isolated local Lab 1/2/3 and
  password-protected RAM WAV downloads; no Pipecat component.
- firmware/stackchan-pipecat-16k.example.yaml: conversational variant derived
  from the balanced AFE configuration, using the existing Pipecat add-on.

Both set ES7210 microphone gain to 36 dB and reference gain to 0 dB. AFE settings,
physical pins, sparse TDM slot assignment and master-volume behavior are retained.
The lab retains ADC register and PCM diagnostics from lab v2.

## Signal path and source evidence

Shared RX/TX bus and AW88298 DAC are now 16000 Hz. ESPHome package override uses
`id: !extend aw88298_dac`, preserving the official driver and changing its rate.
The pinned AW88298 driver maps 16000 Hz to sample-rate code 0x3 (48000 was 0x8).
Startup checks require left-channel Philips I2S at 16 kHz, then retain 64 BCLK/frame
and 32-bit TX slots: expected I2SCTRL changes from 0x14e8 to 0x14e3.
No power, amplifier-volume or physical pin configuration change is made.

The audio stack supports equal bus and processor rates (ratio=1). It still
extracts/deinterleaves microphone and reference slots; its rate converter returns
channel distribution directly at ratio<=1, without executing rate conversion.
The physical sample rate, MCLK and BCLK are configured through the existing drivers.

Pipecat component a538d1d1bacc8609061719f0b05c1622147ccb4b declares incoming
speaker PCM16/mono/24000; ESPHome resampler output is now 16000, feeding the
native 16000 speaker. Microphone transport remains 16000. Only output 24->16
conversion remains in the normal conversation path. This reduces output bandwidth
above 8 kHz and does not eliminate AFE computation, which was already at 16 kHz.

Local lab stimulus is stored and played at 16000 directly: 160 samples per
10 ms chunk; previous 3x sample repetition is removed. The 8-second queue target
is 256000 bytes. The live firmware's separate 1 kHz speaker diagnostic uses
160 samples per chunk, a 16-sample sine period and a 32000-byte one-second target.
Those byte counts describe queue acceptance, not acoustic success.

Source references:
- m5stack/esphome-yaml cc708dd: components/aw88298/aw88298.h and .cpp
- our audio stack 4541119: audio_effects_rate_converter.cpp process_multi_t_
- ESPHome 2026.9.1: components/resampler/speaker and components/audio/audio_resampler
- kyvaith/pipecat-homeassistant a538d1d: components/va_pipecat/va_pipecat.cpp

## Hardware test

Start with the lab YAML, set capture_password and retain normal Wi-Fi secrets.
Keep a full log, press Lab 1, speak normally after two seconds, wait for END.
Download mic0.wav, mic2.wav, reference.wav, processed.wav through authenticated
HTTP port 8088. Check ADC readback, native/captured levels, clipping, missing
blocks and expected I2SCTRL=0x14e3. Do not infer the cause of a change solely from
comparison with the old 6 dB/48 kHz test: gain and rate changed together by choice.

If quiet speech is clean, Lab 2 checks native 16 kHz speaker output/reference;
Lab 3 compares instrumentation overhead. Download WAVs before the next test.
The separate live YAML uses the existing Pipecat connection configuration and
Start button, not the WAV server. Test start/stop, audible output, self-echo and
normal-voice interruption only after the local audio path is validated.

Hardware operation at 16 kHz and end-to-end interruption remain unverified.

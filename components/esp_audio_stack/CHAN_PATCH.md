# Chan Audio Stack patch

Vendored from n-IA-hane/esphome-audio-stack, commit
0482d741a938378ef948e3b8f3dd31536f9f2cc9, directory
esphome/components/esp_audio_stack. Original MIT license is included.

## Codec-less TX correction (4541119)

Original local change: codec_dev_backend.cpp, CodecDevBackend::read_layout_.
When TX has no codec interface because AW88298 is managed by the official
ESPHome driver, do not ask codec-dev 2.0.0-beta5 for codec channel identities.
That query returns NOT_SUPPORT and aborts the entire duplex startup.

Instead validate the live I2S bus against the requested format and accept
only single-slot, 16-bit TDM TX with matching slot/data widths and a valid
slot mask. Keep memory map zero (unavailable); it is diagnostic metadata,
not used to reorder or pack audio. Do not invent a codec channel map.
RX and managed TX still require the codec layout query to succeed.
No changes to PCM, volume, ADC gain, AEC, or Pipecat.

This deliberately narrow workaround does not add support for codec-less
standard I2S or multi-slot TX. Subsequent log 26 demonstrated playback and some
barge-in after the separate amplifier clock correction; robust interruption is
still unqualified. See docs/CURRENT_STATE.md for current evidence.

## ESPHome 2026.10 compatibility (80e0d8c)

audio_core_ring_buffer_caps.h now selects the stored handle_ field for older
ESPHome or handle_() for2026.10+. Installation and destruction respect each
base-class storage ownership pattern; reject reinstallation of a live ring and
clear storage after derived cleanup to avoid double deletion. Audio processing
and buffer policy are not changed. Tests compile the production header against
exact2026.9.1/2026.10.0 headers with debug on/off; full native16k builds passed
on2026.10.0. Stub tests do not establish runtime allocator correctness.

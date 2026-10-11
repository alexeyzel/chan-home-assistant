# Chan Audio Stack patch

Vendored from n-IA-hane/esphome-audio-stack, commit
0482d741a938378ef948e3b8f3dd31536f9f2cc9, directory
esphome/components/esp_audio_stack. Original MIT license is included.

Local change: codec_dev_backend.cpp, CodecDevBackend::read_layout_.
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
standard I2S or multi-slot TX. Hardware playback and barge-in remain unverified.

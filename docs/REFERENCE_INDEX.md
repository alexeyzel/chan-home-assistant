# Reference implementations and dependency pins

Current pins come from the delivered YAML, not from the newest upstream main.
Do not update them merely to refresh documentation. Hardware changes need source
and measurement evidence. A donor working on another board is not a tested
StackChan configuration.

## Active buffered lab dependencies

| Role | Repository/revision | Why retained |
| --- | --- | --- |
| Official BSP and external board drivers | m5stack/esphome-yaml `cc708ddcc9dea7cfc746b408d2495ce281bbf2d2` | Power, pins, AW88298 and board peripherals |
| AFE capture component | alexeyzel/chan-home-assistant `12c218e0170c06d478effd00d9a1e3f5aa2ab833` | Authenticated RAM captures and profiling |
| Audio Stack | alexeyzel/chan-home-assistant `80e0d8c96044ec3c1c5ba370ac88354046952611` | Single bus, codec-less TX correction, ESPHome 2026.10 RingBuffer compatibility |
| ESP-SR | `2.5.5` | Fixed AFE dependency; see generated managed-components lock for transitive details |

The deferred native16k Pipecat YAML uses the same BSP/audio-stack pins, AFE
`e48a26e57a7c6d5017e9ee92f856956bd487ae51` (profiling, without the lab capture
variant), and va_pipecat `a538d1d1bacc8609061719f0b05c1622147ccb4b`. Its microphone
ADC remains36dB; do not describe it as having the buffered lab's18dB trial.

## Donors and what they establish

1. [Official StackChan ESPHome BSP](https://github.com/m5stack/esphome-yaml/blob/cc708ddcc9dea7cfc746b408d2495ce281bbf2d2/examples/kit/stackchan-bsp.factory.yaml).
   Reference for board hardware and36dB microphone setting. Original independent
   microphone16k/speaker48k configuration is not a shared-bus duplex recipe.
2. [Stock StackChan codec](https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/cores3_audio_codec.cc)
   and [board configuration](https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/config.h).
   Shared duplex, standardTX/TDMRX,24k, hardware reference enabled, codec write
   path. Requested input_gain60 is not proof of60dB analog gain; our codec-dev
   mapping tops out at37.5dB. This source is not a verified match to the owner's
   factory binary, and its build-time AEC flags are unknown.
3. [Xiaozhi v2.2.4 AFE](https://github.com/78/xiaozhi-esp32/blob/v2.2.4/main/audio/processors/afe_audio_processor.cc).
   Stock dependency; conditionally enabled device AEC and M/R processing. A
   wake-word abort is not arbitrary-speech barge-in. Do not copy high-performance
   AFE settings without checking S3 CPU and installed build flags.
4. [Waveshare AFE YAML](https://github.com/jyoushiki/esphome-waveshare-esp32-s3-audio-va/blob/c86ecd3c5124db85181c03ad35aec6578b82b849/waveshare-va.yaml).
   Donor SR/low_cost MMR graph, SE, post-AGC and performance profile. It sets
   mic/reference30dB on different hardware. Keep our reference0dB; runtime
   post-AFE gain is distinct from ADC gain. Snapshot retained locally as
   `waveshare-afe-reference.yaml` in the workspace parent; license preserved.
5. [Pipecat component](https://github.com/kyvaith/pipecat-homeassistant/blob/a538d1d1bacc8609061719f0b05c1622147ccb4b/components/va_pipecat/va_pipecat.cpp).
  16k microphone /24k speaker PCM, buffered drain and accepted-byte accounting.
   Transport reconnection alone does not prove session resumption. Firmware pin
   does not identify the installed HA add-on version (still unknown).
6. [Original Audio Stack](https://github.com/n-IA-hane/esphome-audio-stack/tree/0482d741a938378ef948e3b8f3dd31536f9f2cc9).
   Shared-bus architecture and ESPHome speaker/microphone interfaces. Vendored
   with license; local codec-less TX and RingBuffer fixes must be preserved.
   See components/esp_audio_stack/CHAN_PATCH.md and tests/.
7. [Dravix snapshot](https://github.com/YossiKon/dravix-os/blob/07d468506490dc1ae40be4a0af82e132aeee13e1/deploy/esphome/stackchan-dravix.yaml).
   Possible future integration, not a demonstrated solution to our duplex issue.
   Inspected config pins BSP238ba9825e7874d5626709631dae6be92e861b17 with36dB;
   extra wake-word/Assist gain is not analog gain. It releases mic consumers
   before playback. Owner encountered errors and missing desired live features.

## Hardware sources

- [StackChan Core documentation](https://docs.m5stack.com/en/core/StackChan_Core)
  links [CoreS3 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/490/Sch_M5_CoreS3_v1.0.pdf):
  amplifier differential output feeds ES7210 MIC3 through the feedback circuit.
  Exact owner assembly revision remains unconfirmed.
- [AW88298 datasheet](https://doc.awinic.com/doc/20230609wm/78b5dc17-223f-4371-9a31-a6640f883a0c.pdf):
  clock format registers; preserve64fs correction and validate readback.
- [ESPHome 2026.10 RingBuffer](https://github.com/esphome/esphome/blob/2026.10.0/esphome/components/ring_buffer/ring_buffer.h):
  handle_() replaces stored handle_. Compatibility fix also handles base/derived
  destructor ownership. See corresponding.cpp and test_ring_buffer_compat.py.

HA Voice PE's XMOS processing is an architectural reference, not functionality
that can be obtained on StackChan by copying YAML. Dotty and stackchan-idf are
owner-reported prior attempts; no exact successful reference build is recorded.

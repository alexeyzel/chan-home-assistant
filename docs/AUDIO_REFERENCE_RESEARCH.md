# Stock audio comparison, 2026-10-11

Stock source inspected: m5stack/StackChan commit
1b5765599fba8aaad1811d9a79358ccc7051f5f3. This is public source, not a verified
match to the owner's previously installed factory binary.

- firmware/repos.json pins 78/xiaozhi-esp32 v2.2.4 plus local patches.
- firmware/main/hal/board/config.h sets AUDIO_INPUT_REFERENCE true and both
  input/output rates to 24000 Hz.
- cores3_audio_codec.cc uses shared duplex I2S, standard TX and TDM RX.
  Input reference enables two channels; EnableInput selects channels 0 and 1.
  This differs from our mono input and software-derived playback reference.
  Physical routing/channel identity must be checked against the board before
  changing the ESPHome bus configuration. A reference-enabled codec does not
  by itself establish that device AEC is enabled in the factory binary.
- Kconfig device AEC defaults off, with board dependencies; server AEC also
  defaults off and requires server support. Actual installed build flags unknown.
- Xiaozhi v2.2.4 afe_audio_processor.cc constructs M/R input from codec channels,
  selects AFE_TYPE_VC and AEC_MODE_VOIP_HIGH_PERF; aec_init is conditional on
  CONFIG_USE_DEVICE_AEC. Do not copy high-performance settings blindly.
- Xiaozhi application separates realtime listening and wake-word abort. A
  working wake-word interruption is not proof of arbitrary speech barge-in.

Primary sources:
- https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/cores3_audio_codec.cc
- https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/config.h
- https://github.com/78/xiaozhi-esp32/blob/v2.2.4/main/audio/processors/afe_audio_processor.cc
- https://github.com/78/xiaozhi-esp32/blob/v2.2.4/main/application.cc
- https://docs.espressif.com/projects/esp-sr/en/latest/esp32/acoustic_echo_cancellation/README.html
- https://www.home-assistant.io/voice-pe/

Espressif documents FD nonlinear suppression levels: default aggressive can
affect near-end speech; normal is less destructive. This is a hypothesis to
test, not an established reason for the owner's lost stop commands.
Home Assistant Voice PE uses XMOS audio processing; its AEC cannot be reproduced
on StackChan merely by copying YAML.

Log 23: owner reports four unsuccessful stop requests at maximum volume.
Master gain is 1.0. Pre-AEC microphone repeatedly reaches 32768; uplink remains
active. No stop transcript appears. Barge-in at 11:05:52 and transcript
"Ukraini" at 11:05:54 do not prove response to the owner's stop requests.
Need recorded input and/or raw/processed capture to distinguish clipping,
near-end suppression and server detection failure. Full-duplex POC incomplete.

Next priorities: verify captured reference-channel routing, establish headroom
at maximum intended speaker loudness, and validate simultaneous human speech
preservation before changing server VAD. Keep the 160 ms experiment as a
limited successful echo-only baseline, not a general barge-in solution.

## Hardware reference experiment

The official StackChan Core page links the CoreS3 v1.0 schematic:
https://docs.m5stack.com/en/core/StackChan_Core
https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/490/Sch_M5_CoreS3_v1.0.pdf
On its audio sheet, AW88298 SPK_VOP/SPK_VON feed AEC_P/AEC_N through
150 kohm resistors and coupling capacitors, into ES7210 MIC3P/MIC3N.
This is evidence for physical feedback routing, not confirmation of the
owner's board revision or successful AEC on that board.

`firmware/stackchan-hwref.example.yaml` enables MIC1/MIC2/MIC3 and TDM RX
through Audio Stack's codec-dev input driver, replacing the native ES7210
driver. It retains the official AW88298 driver and power handling. ADC gain
is 6 dB to test headroom; MIC3 reference gain is 0 dB. The bundled codec-dev
driver maps gain channel index 2 to MIC3 register 0x45. This index differs
from the proposed TDM reference slot 1; diagnostics expose all four slots
so the mapping can be checked physically. No 160 ms software delay remains.

Audio Stack uses TDM TX as well as RX, whereas the stock code uses standard
TX and TDM RX. Playback compatibility, correct slot mapping, clipping,
human voice preservation, and interruption all require device testing.
The fixed-delay baseline is unchanged. This is not a release or a confirmed
replacement for stock audio processing.

# Device validation

## 2026-10-09: official M5Stack BSP

Hardware: official-store StackChan AI Desktop Robot; exact assembly revision
not independently confirmed.

- ESPHome: 2026.9.1.
- Upstream project label: m5stack.stackchan-bsp 2026.3.0.
- BSP/drivers: upstream main; exact build commit unknown.
- HA version and Pipecat Assist add-on version: not supplied.

Evidence: owner-provided logs and owner confirmation. Raw logs are not committed.

## Confirmed observations

- setup() completed; power and IO expanders initialized.
- 8 MB PSRAM available; Wi-Fi connected.
- Camera produced a frame, without establishing sustained streaming quality.
- Screen touch coordinates appeared after an initial driver-start error.
- Both servos reported positions; an initial ping warning subsequently cleared.
- HA TTS FLAC decoded as mono 48 kHz / 16-bit PCM. Playback started and stopped
  without an error in the supplied excerpt.
- Owner heard speech. Increasing HA volume made it acceptable, though not ideal.

## Open issues

- Y servo reported 190 degrees outside its configured 0..90 range. Resolve
  calibration/position conversion before commanding motion.
- FT6336U startup error followed by working touch events: repeat cold boots.
- AW88298 reported Initialized: NO despite setup completion and audible playback.
  Inspected upstream setup did not set the flag; this alone is not audio failure.
- Initial log covered about 21 seconds, not a long stability test.
- Head-touch transitions and sustained concurrent load remain unverified.
- Subsequent owner tests confirmed clear microphone recordings and audible
  Pipecat replies with barge-in disabled. Exact deployed YAML/revisions are still
  needed for reproducibility; this is not a tested release.
- Enabling barge-in produced repeated `Parent bus is busy` speaker start errors
  while capture continued. Reverting restored conversation, per owner report.
  See FULL_DUPLEX_POC.md for the next milestone.

## Next acceptance test

1. Record Pipecat add-on version and exact dependency commits.
2. Validate and compile the proposed Pipecat configuration.
3. Confirm authenticated connection, microphone transcript, and audible reply.
4. Repeat conversation turns and explicit start/stop cycles.
5. Verify stop clears audio and microphone streaming; test reconnection.
6. Evaluate echo and interruption separately after basic conversation works.

Before a new release, record results, pin sources, and document recovery and
limitations. No new release was created by this cleanup.

## 2026-10-10: experimental duplex build validation

- Local toolchain: ESPHome 2026.9.1, ESP-IDF 5.5.5, Windows, Python 3.12.
- Raw duplex and AEC example configurations passed ESPHome schema validation.
- Final raw duplex example (including diagnostics) compiled successfully:
  image 1,180,615 bytes, static DIRAM usage 120,655 / 341,760 bytes. These figures
  do not measure runtime heap/PSRAM headroom or audio performance.
- AEC variant compiled successfully: image 1,236,623 bytes, static DIRAM usage
  123,879 / 341,760 bytes. No device-level AEC effectiveness is claimed.
- Generated C++ contains Audio Stack microphone/speaker, no legacy I2S
  microphone/speaker, and both ES7210/AW88298 are configured for 48 kHz.
- Generated AW88298 source hash matches the pinned M5Stack checkout.
- Builds used placeholder Wi-Fi credentials. Do not install their local binaries;
  compile the YAML in the owner's ESPHome environment with real secrets.
- At this build checkpoint, no experimental firmware had been installed.

## Subsequent owner device tests, 2026-10-10

- Owner installed both raw-duplex and SR AEC variants and heard replies while
  microphone transmission continued. Shared-bus blocking was not observed in
  the supplied tests.
- SR AEC initialized and was enabled, but reply fragments were recognized as
  user speech and triggered repeated interruptions. At 50% volume the issue
  persisted with reported uplink peaks below int16 saturation. Uplink peaks
  alone do not locate clipping or quantify echo cancellation.
- Pipecat also suffered a separate expired Gemini session: connection task
  exception followed by `ready=False session=False` despite live audio ingress.
- The next experiment is the single-file FD AEC configuration with runtime
  mode comparison and diagnostic logging. It is not an established echo fix.

## FD diagnostic build, 2026-10-10

- `stackchan-duplex-fd.example.yaml` passed schema validation and compiled with
  ESPHome 2026.9.1 / ESP-IDF 5.5.5. Flash usage: 1,239,383 bytes; static DIRAM:
  124,175 / 341,760 bytes. Runtime memory and echo suppression remain untested.
- Build uses a separate directory after Windows denied cleanup of the old build.
- FD is the boot default; runtime FD/SR buttons stop the session and print the
  actual processor configuration. Automatic diagnostics run during capture.
- Firmware binaries contain placeholder Wi-Fi settings; use the copy-paste YAML
  with the owner's secrets, not these locally generated binaries.

## FD owner test: echo still triggers interruption

- Owner log (17) confirms `fd_low_cost`, initialized YES, AEC enabled, and
  simultaneous capture/playback with no reported I2S error.
- At 18:24:20 assistant says "Chym mozhu dopomohty"; at 18:24:23 server sends
  barge_in and at 18:24:24 user transcript contains "mozhe dopomohty".
  Further assistant phrases reappear as user speech. FD did not solve feedback.
- Input WAV is mono PCM16 / 16 kHz, 17.568 s, peak 32710; only 0.0146% of
  samples have absolute value >=32000. This does not establish ADC clipping.
- Volume has two software layers: output 0.8 and master 0.8 yield logged
  combined linear gain 0.105. The on-boot speaker volume is not the master
  volume entity and compounds its attenuation.
- Underrun counts include idle periods and cannot alone establish playback
  starvation. Zero AFE counters are unsupported standalone-AEC telemetry.
- Next diagnosis needs raw mic, playback reference, and processed mic aligned
  in time; current logs and processed input alone cannot isolate reference
  alignment, gain, or acoustic distortion. Avoid claiming an AEC-mode fix.

## Inline signal probe build

- Single-file `stackchan-duplex-probe.example.yaml` validated and compiled on
  ESPHome 2026.9.1 / ESP-IDF 5.5.5: flash 1,241,427 bytes; static DIRAM 124,343
  / 341,760 bytes. Hardware test pending.
- Inline AudioProcessor wrapper delegates to EspAec and logs mic/reference/output
  RMS and peaks every 32 frames, including zero-reference and failure counts.
  It measures input before processing (buffers can alias) and output on success.
  This provides levels, not acoustic delay or separate audio recordings.
- Speaker output gain is unity, leaving the master-volume entity as the user
  control. Begin the owner test at 50%, since attenuation is now lower.

## Owner signal-probe tests, 2026-10-11

- Log 18: reference is nonzero during playback, processor calls succeed, but
  pre-AEC mic peaks reach 32768 and reply text reappears as user speech.
- Owner applied ES7210 mic_gain 18 instead of inherited 36. Logs 19 and 20
  have lower mic levels, without full-scale peaks in probe windows, yet feedback
  persists. Log 20 at 10:28:09: mic RMS 434, reference 170, output 428;
  10:28:10: mic 382, reference 279, output 377. Gain reduction is not a fix.
- Supplied session 254a82c2 WAVs: input PCM16 mono 16 kHz, 71.424 s, peak
  18001; output PCM16 mono 24 kHz, 46.644 s, peak 28681. They are server-side
  recordings, not synchronized raw-mic / actual-TX / processed-mic tracks;
  no device AEC reference delay estimate is established from them.
- Pinned Audio Stack applies software volume before deriving reference, so
  user-volume awareness is already present. Reference is saved only on full
  speaker frames; its timing versus actual DMA playback still needs measurement.
- Software master curve defaults to -49 dB at the lower end. At 50%, gain is
  about -24.5 dB / 0.060 amplitude, explaining strong digital attenuation but
  not measuring acoustic loudness. Volume UX and AEC timing are separate work.
- Owner requires comfortable volume control without manual AEC retuning;
  acceptance must include multiple audible levels and changes during playback.

## Coarse envelope delay probe, 2026-10-11

- Compiled on ESPHome 2026.9.1: flash 1,242,391 bytes; static DIRAM 126,415
  / 341,760 bytes. Device runtime and CPU overhead are not yet measured.
- Positive/negative lag and gain scaling were checked with deterministic
  synthetic envelopes; constant silence is rejected. This does not validate
  real-world echo delay estimation or solve echo cancellation.
- Added 4 ms envelope correlation over +/-256 ms, including alternative peak
  reporting. No audio delay or microphone gating is applied by the probe.
- Boot sets ADC gain 18 dB, output unity and volume floor -30 dB. Real DMA
  timestamps and sample-continuous TX reference changes remain outstanding.

## Log 21 and fixed-reference-delay experiment

- Log 21 candidates: 176 ms (0.822), 168 ms (0.822), 164 ms (0.951),
  160 ms (0.760). The 204 ms candidate has a close alternative (0.844 vs
  0.814); low-correlation candidates are not reliable delay measurements.
- Added fixed 160 ms reference delay ahead of AEC; diagnostic correlation now
  measures residual lag. Mic and speaker paths are not intentionally delayed.
- Synthetic impulse verified exact 2560-sample shift across frame/ring
  boundaries. ESPHome 2026.9.1 compile passed: flash 1,242,667 bytes,
  static DIRAM 132,567 / 341,760 bytes. Physical effectiveness pending.
- This delay is not a hardware constant. Buffer configuration, scheduling,
  conversion and signal-processing latency can contribute. Load dependence
  and exact DMA alignment have not been measured.

## First successful echo-suppression device test: log 22

- Owner reports no self-interruption with the fixed 160 ms reference delay
  (configuration from commit 002c866). Response playback spans approximately
  11:01:55 through 11:02:19 without subsequent server barge_in in the supplied
  log. The initial barge_in at 11:01:51 precedes the user's request.
- At 11:01:56 pre-AEC mic RMS 1195 becomes output RMS 2; at 11:02:08,
  1129 becomes 16; at 11:02:15, 1810 becomes 95. These are observed window
  level reductions, not calibrated ERLE measurements.
- Strong residual envelope-lag estimates mostly cluster near zero (e.g. 4 ms
  at correlation 0.971, 0 ms at 0.842). Other windows are ambiguous/outlying.
- This supports reference alignment as a material cause of the previous echo
  failure. One successful session does not validate all volumes/load conditions.
- Preserve this firmware as the experimental baseline. Next: deliberate human
  barge-in during playback, comfortable volume changes, repeated start/stop and
  reboot. No product release or adaptive alignment claim yet.

## Hardware-reference experiment: owner validation pending

- Final YAML compiled on ESPHome 2026.9.1 / ESP-IDF 5.5.5, with
  esp_codec_dev 2.0.0-beta5: flash 1,301,287 bytes; static DIRAM 126,847 /
  341,760 bytes. Generated configuration confirms MIC3 gain channel index 2.
  Compilation is not physical validation; runtime memory headroom is unmeasured.
- Log 23 failed deliberate human interruption at maximum volume despite
  continuous uplink. Mic peaks again reached full scale; see
  AUDIO_REFERENCE_RESEARCH.md for source comparison and schematic evidence.
- New independent configuration: firmware/stackchan-hwref.example.yaml.
  ES7210 codec-dev TDM capture, slots 0/1 provisionally mic/reference, all four
  slot levels exposed. ADC mic gain 6 dB, MIC3 feedback gain 0 dB. No software
  reference delay. Existing 160 ms configuration is preserved.
- Copy the whole YAML into ESPHome; dependencies are pinned remote sources.
  Retain local Wi-Fi secrets and any installation-specific API/OTA settings.
  No uploaded headers or local components are required.
- Capture logs from boot. Verify normal input and intelligible playback first
  at a comfortable level, then maximum intended level. Stop if audio is
  distorted; this may indicate bus/slot incompatibility, not an AEC setting.
- During an active session, speak with playback silent, then request a long
  response and remain silent for its first seconds. Slot 1 should primarily
  follow speaker output rather than room speech. Record input/output WAVs and
  the log, including slot levels, aec_probe and Audio Diagnostics.
- Say a distinctive interruption phrase during the response. Check preserved
  words in recorded input, server barge_in, and immediate playback cancellation
  separately. A quiet processed mic alone is not success.
- Qualification also requires several audible volumes, volume changes during
  playback, repeated sessions and reboot. Hardware effectiveness is unverified.

## Hardware-reference startup failure: log 24

- Owner test of the hardware-reference YAML fails before microphone capture.
  At 19:13:03 and 19:13:17 TX/RX TDM initialization succeeds, then codec-dev
  reports layout resolution error 0x106 and Audio Stack reports
  `Cannot query effective TX codec layout`. Backend open fails and I2S closes.
- Pipecat WebSocket connects at 19:13:09. Subsequent no-frames warnings and
  the 7000 ms no-speech timeout are consequences of the unavailable microphone,
  not evidence of Gemini/VAD failure.
- Source confirms Audio Stack creates a TX codec-dev handle even without an
  output codec, then unconditionally queries its layout. The bundled codec-dev
  sample-format layout resolver returns NOT_SUPPORT without a codec interface.
  AW88298 is intentionally owned by the separate official driver; adding an
  unrelated output codec or ignoring all layout failures would be incorrect.
- Hardware-reference configuration is currently blocked at startup. Compilation
  passed but did not validate this runtime path. No conclusion about actual
  reference mapping, echo cancellation or double-talk can be drawn from log 24.
  A driver correction for codec-less TX layout handling is required before
  repeating the hardware test; clean builds or volume changes do not address it.

## Log 24 driver correction

- Vendored Audio Stack at upstream 0482d741a938378ef948e3b8f3dd31536f9f2cc9
  with its MIT license. Only codec_dev_backend.cpp differs from the upstream
  component source; see components/esp_audio_stack/CHAN_PATCH.md.
- Codec-less TX uses live bus validation for single-slot 16-bit TDM. It keeps
  the diagnostic memory map zero/unavailable instead of querying missing codec
  channel identities. Rate, data width, slot count/mask and slot width checks
  remain active. RX and managed TX retain mandatory codec layout queries.
- 17 compile-time C++ mock scenarios exercise the production read_layout_
  body. They include the reported failure, bus query failures, format/mask
  mismatches, and RX/managed-TX layout failures/successes. Patched code passes;
  unpatched code fails scenario 0. This tests control flow, not physical I2S.
- YAML fetches the patched component at repository commit
  4541119291c9b67b6fa44f75fe27e04ae0480026. Remote configuration validation
  passed. The alternate build directory avoids a local Windows cleanup failure;
  clean building itself is not the runtime fix.
- Full compile passed with ESPHome 2026.9.1 / ESP-IDF 5.5.5, first with local
  source and then with the exact delivered YAML using the GitHub dependency.
  Flash: 1,301,575 bytes; static DIRAM: 126,847 / 341,760 bytes.
  The delivered file was compiled under an ignored local filename to reuse
  its build metadata; file contents were identical. No robot was flashed here.
- Owner retest must confirm `TX externally managed: validated I2S bus`,
  audio-stack startup, actual mic frames and audible output. Hardware reference
  effectiveness and human interruption still require the earlier test plan.

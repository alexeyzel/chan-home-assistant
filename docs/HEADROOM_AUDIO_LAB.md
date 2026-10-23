# Headroom and simultaneous pre/post-AGC lab

Active candidate: `firmware/stackchan-audio-lab-headroom.example.yaml`.
Supersedes buffered lab for the next owner test; log41 remains its baseline.

## Changes

- Fixed microphone12dB (ES7210 nibble4), reference0dB. User volume unchanged.
- Same native16k bus, clock guard, 500ms speaker ring and capacity-driven feeding.
- AFE/AGC settings unchanged. New `/pre-agc.wav` captures the same output frames
  immediately before post-AGC. `/processed.wav` still captures after it.
- AGC has its own buffering latency; align signals before numerical comparison.
  A pre-AGC tap isolates the post stage, not all nonlinear AFE processing.
- Additional256000 bytes PSRAM and2048 bytes staging storage; no stack-sized
  frame arrays or new audio task. Stage supports up to1024 samples; oversized
  valid frames produce zeros in pre-AGC capture and increment pre_agc_missing.
- Missing-output count now excludes callbacks after the8s buffer is full and
  reports first_missing_sample (-1 means none). pre_agc_missing reports tap errors.
- Only retained stimulus is peak-normalized to-3dBFS, now bounded to+30dB to
  accommodate the6dB ADC reduction. Minimum original peak733. Too-quiet recordings
  still disable playback. No raw/processed/pre-AGC gain is added.
- New stimulus comes from this boot's Lab1. It is identical across repeated Lab2
  tests in that boot, but is NOT identical to log41; do not claim controlled
  same-waveform comparison across firmware installations.

## Owner procedure

Copy the entire YAML, set capture_password (12-64 letters/digits), retain Wi-Fi
secrets, compile and install. This is an isolated local lab without Pipecat.

1. Lab1: count roughly two seconds, say a short phrase in your normal voice,
   wait for END without pressing Stop. No stopwatch is needed.
2. Save all six WAVs before another test.
3. Lab2: stay silent, wait for END and download all six WAVs plus the full log.
   Keep normal audible volume; do not turn it down to avoid echo.
4. If Lab2 is disabled for low stimulus level, send Lab1 files/log; do not shout
   or adjust ADC gain to force the test through.

Use `http://ROBOT_IP:8088/` followed by each exact filename:
`mic0.wav`, `mic2.wav`, `reference.wav`, `pre-agc.wav`, `processed.wav`, `stimulus.wav`.
Username diagnostic and your capture_password. No root index page. Server starts
on successful test begin; next test overwrites capture; reboot clears RAM.
Save with lab1-/lab2- prefixes to distinguish sets.

## Acceptance

No clipped ADC samples and useful peak margin at audible volume; complete timely
playback; no saved-frame misses/tap overflow; pre-AGC echo low compared with normal
speech; processed speech usable without saturation. These are hardware questions,
not guaranteed outcomes of compilation. Do not test double talk/Pipecat until the
quiet and echo-only results are assessed. No public release.

## Build validation

Final delivered YAML compiled with ESPHome2026.10.0 / ESP-IDF5.5.6,
config hash0xfd5de467. Image-info: ESP32-S3, chip ID9,16MB, valid checksum/hash.
Remote AFE pin2bbcfbd1e98bf0a22f2f077550b3e3399379c474 verified in generated source.
Known Windows ldgen batch suffix issue resolved by direct inspected argument-list
invocation; final incremental build passed. No flashing or hardware result yet.

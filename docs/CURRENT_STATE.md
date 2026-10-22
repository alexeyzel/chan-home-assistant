# Current project state

Updated 2026-10-22 after delivering the buffered lab and clarifying test timing.
No hardware results for that candidate have been received. This file is the
starting point for another chat; historical “pending”/“next” paragraphs elsewhere
must not override it.

## Immediate next action

Await/analyze owner Lab 1 and Lab 2 results from
`firmware/stackchan-audio-lab-buffered.example.yaml` (introduced c933d10,
whitespace cleanup 0e51724). Do not begin another speculative AEC/VAD rewrite or
send an older YAML. No need to recompile the unchanged firmware for documentation.

Current candidate is **compile-validated, NOT hardware-validated**. Last full
build: ESPHome 2026.10.0, ESP-IDF 5.5.6, config hash 0xadeb4280, ESP32-S3 chip ID 9,
16 MB, valid checksum/hash. Static RAM 172587/341760, image 1855715/8126464 bytes;
these are not runtime headroom measurements. No new release exists.

The local-lab protocol is [BUFFERED_AUDIO_LAB](BUFFERED_AUDIO_LAB.md). User-facing
instruction: press Lab 1, count roughly “one, two”, say a short normal-volume
sentence, wait for END. Do not require a stopwatch or exact seven-second speech
cutoff. Lab 2 plays only the first seven seconds, so a late phrase tail may be
omitted without invalidating the basic distortion/clipping check. Never ask the
owner to press Stop at an exact time. Save Lab 1 files, then Lab 2 in silence.

## Goal and hard constraints

Official-store M5Stack StackChan AI Desktop Robot (ESP32-S3; exact assembly
revision not independently confirmed). Firmware must be ESPHome. Gemini Live
must use existing kyvaith/pipecat-homeassistant. HA Assist is deferred. Prove
simultaneous capture/playback, intelligible ordinary speech and reliable barge-in
without self-interruption before faces, motors, camera, Frigate or personalization.

Future modes: sleep, Pipecat live, HA Assist. Future Frigate coordinates/identity
can drive bounded tracking and server-side person/guest prompts. Recognizing a
face neither identifies the current speaker nor authorizes HA actions.

Owner requires one copy-paste YAML with pinned remote components, no header or
component uploads. Explain in Ukrainian; identifiers/docs in English. User volume
must work independently of AEC tuning. Do not solve echo by making playback quiet
or requiring shouting. Do not flash automatically. Preserve source evidence before
hardware changes; do not move servos until Y-angle mismatch is resolved.

## Latest hardware evidence

| Run | Artifact/result | What it proves / does not prove |
| --- | --- | --- |
| Log 39, Lab 1 | Original native16k lab, mic36dB/ref0. Five 8s mono PCM16/16k WAVs. Owner says speech sounds normal. | Quiet recording works for this run; no proof of echo cancellation. |
| Log 40, Lab 2 | Same lab. Mic0 clipped22.58%, mic2 clipped20.96%. Reference not clipped. Owner hears distorted/slowed microphones; stimulus normal. | Significant pre-AFE saturation plus faulty test feeding. AEC quality cannot be judged cleanly. |
| Buffered lab | 18dB trial, capacity-driven playback, compiled only | No hardware result yet; do not state that clipping or slowdown is fixed. |

Log 39: mic0 RMS−26.88/peak−5.84dBFS; mic2 −26.62/−5.05;
processed −18.14/−1.80; reference RMS−87.11 (silent speaker expected).
All 128000 samples/channel, missing_blocks=0, skipped=0, no clipped samples or
all-zero256-sample blocks. Stimulus exactly matched processed PCM in that version.
ADC MIC1/2 gain registers low nibble13 (36dB); reference nibble0. AW88298=0x14e3.

Log 40: mic0 RMS−4.75, mic2−5.04; reference RMS−24.22/peak−12.79;
processed RMS−10.81/peak−1.72dBFS. Same 128000 samples and no recorded capture
misses. Playback accepted256000 bytes over about10s, not nominal8s; middle
windows had87–94 short speaker frames per128. Code fed10ms audio then slept10ms,
adding scheduler overhead. Zero capture misses does not imply continuous TX.
Post-AGC RMS difference is not ERLE. Saturated ADC samples cannot be restored
by later processing. Exact analog-vs-format cause still needs controlled tests.

CPU: log 39 afe_feed≈72% of one core in a transition-overlapping window; log 40≈85%,
IDLE0≈14.4%, IDLE1≈70.9%. Eight-second tests straddle ten-second counters. These
are not steady-state camera/motor headroom measurements or proof CPU is solved.

## Current candidate design

- Single I2S owner, native RX/TX16k; no input48→16 conversion. Live candidate
  (separate, deferred) retains only Pipecat output24→16 resampling.
- Fixed mic18dB/ref0; 18dB is a hypothesis, not a proven setting. Earlier 18dB
  standalone-AEC tests also failed echo control; gain alone is not the solution.
- Lab-only speaker ring500ms. Capacity-driven nonblocking writes; advance only
  accepted bytes; 1ms yield is scheduling, not PCM pacing. Wait for drain and
  flag incomplete/too-slow playback. Do not copy this queue size into live
  barge-in without checking cancellation latency.
- Lab 1 retained stimulus only: normalize peak to−3dBFS, maximum about+24dB;
  insufficient-level recordings disable Lab 2. Raw/processed WAVs are unchanged.
  Stimulus will therefore no longer be bit-identical to processed. Stable peak
  is not constant RMS or perceived loudness.
- First7s stimulus/8s capture, test at least8.5s. Stop while idle does nothing;
  aborted quiet test retains partial WAVs but invalidates stimulus.
- AFE/AGC/pins/amplifier are unchanged from native16k lab. See YAML for exact values.

## Hardware/processing invariants

| Item | Current configuration |
| --- | --- |
| MCLK/BCLK/LRCLK/DIN/DOUT | GPIO0/34/33/14/13 |
| ADC | ES7210 at0x40; MIC1/2/3 selected0x07; four16-bit TDM slots |
| Slot selection | mic0=slot0, mic2=slot2, hardware reference=slot1; reference ADC index2 is a different numbering system |
| Amplifier | Official AW88298 driver, 64BCLK/frame,32-bit left slot, readback0x14e3 at16k (older48k:0x14e8) |
| AFE | SR low_cost, MMR, filter4/aggressive NLP, dual-mic SE, NS/VAD off, post-AGC15/target3, ESP-SR2.5.5 |
| Tasks | Audio bus core 1/priority 19; AFE feed core 0; CPU 240MHz, retained donor performance profile |

One successful cold-start touch/servo report does not clear their historical
warnings. Log 39 still includes a touch-driver startup error; no new touch fix.

## Downloads and diagnosis

Password-protected HTTP on trusted LAN explicitly approved by owner. Username
`diagnostic`; set `capture_password` (recommend12–64 letters/digits); placeholder
rejected. Server8088 starts after a successful begin. Use exact endpoints
`http://ROBOT_IP:8088/mic0.wav`, `/mic2.wav`, `/reference.wav`, `/processed.wav`,
`/stimulus.wav`; there is no registered index page at `/`. RAM-only, no cloud;
next capture replaces diagnostic files, reboot erases all. HTTP Basic is not TLS.

Log 38 connection refused was **unset/invalid password**: “Set capture_password”
and samples0. It was not caused by Stop. Busy/incomplete/download contention can
return503. Inspect the log before changing network/firmware. Robot IP was last
seen as192.168.1.92; verify current address rather than assuming it persists.

## What comes after the pending run

1. Identify exact YAML/version and match logs/WAVs; retain owner description.
2. Check ADC gain readback, complete128000-sample files, clipping/zero blocks.
3. Check DRAIN224000/224000 bytes for a full stimulus, roughly7s drain, no pending
   output, and continuous middle-of-playback reference. Startup/tail underruns
   alone are not failure. If timing fails, fix feeding/format before tuning AEC.
4. If saturation persists, investigate native input/analog and format headroom;
   changing post-AFE gain or server VAD cannot recover the clipped signal.
5. If quiet speech and echo-only playback are sound, test overlapping normal
   human speech, then return to live Pipecat and repeated start/stop/reconnection.
6. Qualify multiple audible volumes, volume changes, at least 10 interruptions,
   longer conversation and cold boot before release. No faces/motors yet.

Unknowns: installed Pipecat add-on version, exact previously successful owner
half-duplex YAML/binary, assembly revision, robust live performance. Do not invent
them. See history for partial successes and transport failures.

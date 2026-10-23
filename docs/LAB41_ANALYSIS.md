# Log 41: buffered audio lab hardware results

Analyzed 2026-10-23. Evidence: `chan-logs (41).txt` and the ten owner WAVs
`lab1-{mic0,mic2,reference,processed,stimulus}.wav` and corresponding `lab2-*`.
Raw recordings stay private. Numerical PCM inspection, not a listening assessment.
Active artifact: firmware/stackchan-audio-lab-buffered.example.yaml (c933d10,
whitespace cleanup 0e51724). No firmware changed for this analysis.

## Measurements

All files: mono PCM16, 16000 Hz, 128000 samples / 8 seconds. RMS includes silence;
it is not a standardized speech loudness measurement.

| Channel | Lab 1 RMS / peak dBFS | Lab 2 RMS / peak dBFS | Lab 2 exact full-scale samples |
| --- | --- | --- | --- |
| mic0 | -51.75 / -31.24 | -15.24 / 0 | 980 (0.766%) |
| mic2 | -51.31 / -31.97 | -16.89 / 0 | 410 (0.320%) |
| reference | -86.67 / -72.25 | -26.86 / -12.91 | 0 |
| processed | -42.41 / -21.44 | -24.57 / -1.13 | 0 |
| stimulus | -23.98 / -3.01 | -23.98 / -3.01 | 0 |

Lab 1 has no clipping. First-second mic background RMS is -74.35/-73.70 dBFS.
The retained stimulus is amplified 8.344x (+18.43 dB); both stimulus files are
identical. Normal stimulus loudness does NOT establish adequate live uplink level:
processed.wav remains unnormalized. Earlier log39 processed RMS was -18.14 dBFS,
but speech/distance were not controlled, so the entire difference cannot be
attributed to the 36-to-18 dB gain change.

Gain readback confirms mic18 dB/ref0; master and speaker volume are 1.000,
unmuted. Lab 2 clipping is reduced relative to log40 (22.58%/20.96%) but remains
concentrated on loud peaks: in seconds 2.0-2.5, near-full-scale samples reach
8.66% of mic0 and 3.41% of mic2. Log near-clip count981 for mic0 includes one
sample that is near, not exactly at, full scale. Different stimulus RMS and feeding
prevent attributing the entire improvement to gain alone.

## Playback timing: passed in this run

DRAIN accepted224000/224000 bytes, elapsed7098 ms, buffered=NO, max_feed_gap36 ms.
Seven seconds of PCM therefore drained in 7.098 s. Middle playback windows show
zero underruns, no feed rejection/input drops/output drops and no AFE glitches.
Startup/tail underruns are not middle-playback starvation.

Stimulus-to-hardware-reference correlation is 0.969 at lag1573 samples (98.31 ms).
One-second windows at source seconds2-6 retain approximately98.31-98.38 ms lag.
This supports stable playback speed and fixes the prior test's timing problem.
It is NOT the microphone-to-reference delay and must not become an AEC delay knob.

## Echo and capture limits

Assuming the prescribed silent Lab 2, processed output still contains substantial
playback-related energy: RMS -24.57 versus quiet-speech Lab 1 -42.41 dBFS.
This is not a calibrated echo suppression ratio: inputs differ, AFE includes
speech enhancement/AGC, and channels require time alignment. No clean ERLE or
successful double-talk claim follows. Remaining ADC saturation obstructs AEC
assessment. Do not simply add +18 dB to live output: Lab 2 already peaks -1.13 dBFS.

Lab 1 missing_blocks=0; Lab 2 missing_blocks=1; skipped=0 in both. No aligned
all-zero 256-sample WAV blocks were found. Source inspection of chan_capture.h
shows missing can increment when the capture buffer is already full and appended
sample count becomes zero. Therefore this counter alone cannot locate or prove a
missing block inside the saved WAV. GMF read errors occur during shutdown, with
normal deinitialization, not evidence of a device crash in this run.

Final CPU sample: afe_feed77.8%, IDLE0 22.3%, IDLE1 76.5%. Earlier overlapping
sample: afe_feed60.4%. These short/transition-dependent windows do not establish
steady-state headroom for Pipecat, camera and other planned features.

## Proposed next experiment (not implemented)

1. Preserve native16k, official pins/clock, capacity-driven playback and audible
   user volume. Reuse exactly the same stimulus for gain comparisons where possible.
2. Test fixed mic12 dB/ref0 (one 6 dB step) for ADC headroom; record quiet speech
   and echo-only separately. This is a hypothesis, not a proven final gain.
   Require no clipping plus margin on peaks before judging AEC.
3. Expose/measure AFE output before post-AGC, or use a controlled AGC-off comparison
   if a tap is unavailable. Separate echo removal from output-level amplification;
   preserve the existing processed capture as a comparison. Correct missing-block
   counting to count only samples actually stored and report their positions.
4. After clean input and echo suppression are demonstrated, calibrate speech
   output level without clipping. Then test normal-voice double talk and return
   to Pipecat with repeated start/stop and interruption recovery.

No VAD threshold rewrite, speculative reference delay or public release is justified.

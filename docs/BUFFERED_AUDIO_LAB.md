# Buffered native-16k local audio lab

## Evidence and reference review

Owner logs 39/40 and WAVs: quiet capture has no clipped samples, but playback
capture clips 22.58% of mic0 and 20.96% of mic2 samples. Reference does not clip.
Playback accepts 256000 bytes over about 10 seconds instead of nominal 8 seconds,
with 87-94 short speaker frames per 128 during the middle of playback. The old
YAML fed 160 samples then delayed 10 ms, adding scheduler/loop overhead to every
10 ms audio packet. Missing capture blocks=0 is not proof of continuous playback.

Reviewed implementations:
- Stock StackChan writes PCM through esp_codec_dev_write. It requests input gain
  60 through its codec API; that is not evidence of 60 dB physical gain or a gain
  value safe for this shared-bus implementation.
  https://github.com/m5stack/StackChan/blob/1b5765599fba8aaad1811d9a79358ccc7051f5f3/firmware/main/hal/board/cores3_audio_codec.cc
- Pipecat speaker drain offers queued bytes, advances only by accepted bytes and
  checks downstream buffered audio; it does not sleep for each packet duration.
  https://github.com/kyvaith/pipecat-homeassistant/blob/a538d1d1bacc8609061719f0b05c1622147ccb4b/components/va_pipecat/va_pipecat.cpp
- Waveshare snapshot c86ecd3 uses fixed ADC gain and post-AFE user gain. Its
  30 dB microphone/reference settings are board-specific. Our hardware reference
  remains 0 dB. See ES7210_GAIN_AUDIT.md for the source and BSP/Dravix comparison.
- Our pinned audio stack 80e0d8c uses nonblocking ring writes, has a byte-count
  capacity/occupancy API, and has_buffered_data includes pending speaker output.

## Candidate

Copy firmware/stackchan-audio-lab-buffered.example.yaml; set capture_password.
All dependencies remain pinned, no local includes or manual files are needed.

- Native RX/TX/AFE 16000 remains unchanged, as do pins, amplifier, AFE and AGC.
- Speaker ring is 500 ms (16000 mono PCM16 bytes) in this diagnostic firmware.
  The cooperative feeder fills available space, retries unaccepted bytes, and
  yields 1 ms only to give the main loop time. Audio time comes from I2S.
  This diagnostic queue size is not a live interruption latency recommendation.
- The test sends the first 7 seconds of retained stimulus (224000 bytes for a
  complete capture), waits for ring/pending output drain and allows a capture tail.
  Capture retains 8 seconds, test waits at least 8.5 seconds. Enqueue timeout is
  12 seconds, drain timeout 2 seconds; incomplete playback or elapsed time over
  nominal duration plus 750 ms is explicitly logged as an error.
- DRAIN logs accepted/target bytes, elapsed milliseconds and maximum successful
  feed gap. Seven seconds should drain in approximately seven seconds, not nine.
  Speaker underruns before initial fill and after drain are expected; assess
  middle-of-playback windows and reference WAV continuity, not whole-test totals.
- Fixed microphone gain defaults to 18 dB (ES7210 nibble 6); reference remains 0.
  This is a measurement hypothesis for ADC headroom, not a copied proven setting.
  It stays fixed through quiet and playback runs and never follows user volume.
  Clipped samples cannot tell us how far above full scale the original was, so
  18 dB is not guaranteed to eliminate clipping. Do not claim full duplex solved.
- Only retained stimulus is normalized to -3 dBFS peak after a complete quiet
  recording. Raw/processed WAVs and live processing are not normalized. The
  multiplier is bounded to approximately +24 dB; too-quiet recordings disable
  playback instead of amplifying arbitrary background noise. This keeps ADC
  gain changes from silently reducing the subsequent test signal's peak level.
  Peak normalization does not equalize perceived loudness or speech RMS.
- Stop on idle is a no-op. Early quiet Stop retains partial diagnostic WAVs but
  invalidates stimulus, requiring another complete Lab 1.

## Test protocol

1. Install with your own capture password, preserve normal listening volume.
2. Lab 1: wait two seconds, speak normally, finish the phrase before second 7,
   wait for END. Download all four WAVs and stimulus before starting another test.
3. Lab 2: remain silent throughout playback, wait for END. Download all five WAVs
   and full log. Do not reboot between Lab 1 and Lab 2 (stimulus is RAM-only).
4. Check timing, native ADC gain readback, clipping, reference continuity and
   residual echo. Only then test double talk or move changes into live Pipecat.

Quiet speech may be quieter at 18 dB; evaluate raw speech/background and processed
speech before adding gain. Post-AFE gain cannot repair ADC saturation. Lab 3 is
available for no-copy CPU comparison, but not needed for the first repeat.

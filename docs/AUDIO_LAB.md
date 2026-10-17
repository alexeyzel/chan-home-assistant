# Local audio lab

Use `firmware/stackchan-audio-lab.example.yaml`. This diagnostic firmware omits
the Pipecat component entirely: no Gemini, voice WebSocket, Pipecat microphone
sender or resampler task participates. ESPHome API/Wi-Fi remain for buttons/logs.
Restore the balanced YAML afterwards for conversations. Hardware tests pending.

## Configuration and access

Change `capture_password` at the top of the YAML to 12-64 letters/digits.
The placeholder password is rejected. Username is `diagnostic`. The owner
explicitly approved password-protected HTTP downloads on the trusted LAN.
HTTP Basic authentication does not encrypt traffic. No cloud or flash storage
is involved. Endpoints appear at the robot IP, port 8088, after the first test.
Every endpoint requires authentication. While recording, downloads return 503;
a download owns the completed buffer and blocks the next capture until finished.
The latest capture replaces the previous one. Reboot erases everything.

## Test sequence

Start the ESPHome log, wait 30 seconds, press Audio Diagnostics.

1. Lab 1 Quiet Capture: after the LOCAL TEST START message, leave two seconds
   of silence, then say a short sentence at ordinary volume/distance. Stop
   speaking before eight seconds. Wait for LOCAL TEST END and the capture
   summary. Download all four files and save them with a quiet- prefix BEFORE
   running Lab 2. The processed quiet recording is also retained as stimulus.
2. Lab 2 Playback Capture: the robot replays that retained phrase while recording
   the four channels. Let it speak alone initially; from approximately second
   four, say a different short phrase such as a stop request. Wait for END.
   Download the four files with a playback- prefix and also stimulus.wav.
   If the stimulus is inaudible or badly distorted, report that; do not treat
   the test as valid echo-cancellation evidence.
3. Lab 3 Playback No Capture: repeats the same playback with microphone and AFE
   active but no audio copying into the capture buffer. Say the same phrase.
   Use its task/frame telemetry to estimate capture overhead. This clears the
   downloadable capture, so download Lab 2 first. Wait 20 seconds afterwards.

Lab Stop cancels the test and closes local playback/microphone. Starting a test
while another runs is ignored. Tests require the amplifier clock check to pass;
playback tests require a prior quiet recording. No microphone gain or AFE graph
change is made. User playback volume remains a comfort setting.

## Files and interpretation

At `http://ROBOT_IP:8088/`:

- mic0.wav: first physical microphone, TDM slot 0, before AFE.
- mic2.wav: second physical microphone, TDM slot 2, before AFE.
- reference.wav: hardware amplifier feedback used by AFE, slot 1.
- processed.wav: actual post-AFE/post-AGC output, including zero-filled misses.
- stimulus.wav: the retained processed quiet recording used for local playback.

Each file is mono PCM16 / 16 kHz, up to eight seconds. Raw here means before
AFE, AFTER the audio stack's 48-to-16-kHz conversion; this is not untouched
codec PCM. If already corrupt, a later capture before conversion is required.
Input and output share callback cadence but AFE output has asynchronous delay;
compare with lag alignment, not sample-wise subtraction at zero lag.
Playback uses sample repetition 16-to-48 kHz (no extra resampler task), so the
stimulus is a controlled diagnostic signal, not a production playback algorithm.
The driver reference is captured separately to measure what AFE actually sees.

Recording reserves 1,024,000 PSRAM bytes plus 256,000 bytes for retained stimulus.
Allocation failure cancels the test. No network calls or heap allocation occur
in the audio callback. The copying is bounded to one process frame and logs
its maximum wall time and any skipped capture blocks. Full buffer remains
locked until the test finishes. Playback reports accepted bytes vs 768,000;
this is queue acceptance, not proof of uninterrupted acoustic playback.
A stopped/slow capture can be shorter than eight seconds; inspect sample count.

FreeRTOS CPU diagnostics remain and ESPHome runtime_stats reports time by
component plus main-loop overhead every ten seconds. These have measurement
overhead and are not exclusive component CPU timings. Compare idle, local
capture, playback capture and playback without capture. Eight-second tests may
straddle ten-second reporting windows; use timestamps and the full log.

Provide the log and recordings. No claims of speech quality, channel identity
in the physical microphone layout, successful echo suppression or CPU reserve
can be made from compilation alone. This lab does not test server VAD/barge-in.

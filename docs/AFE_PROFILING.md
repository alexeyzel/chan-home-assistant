# AFE runtime profiling test

Use `firmware/stackchan-afe-profile.example.yaml` as a complete copy-paste
configuration. It fetches the diagnostic component from a pinned Git commit.
No local header upload is needed. This is a diagnostic firmware, not a claimed
fix for recognition, interruptions or audio gaps.

## Controlled comparison

The audio graph, microphone gain, AEC/SE/AGC, task priorities/affinities, queue
sizes, amplifier settings and Pipecat transport are unchanged from afe-perf.
Only runtime statistics and bounded diagnostic aggregation were added.
ESP32-S3 and the previously compiled performance profile are retained.

Log 32 still showed approximately 26-31 missing output frames per 128 during
reply playback, with input drops. The supplied WAV contained 678 entirely zero
256-sample blocks out of 3993 (16.98%). This is improvement over log 31, but
neither proves CPU saturation nor establishes the cause of misrecognition.

## Measurements every ten seconds

- `input_queue_wait`: wall time spent receiving an input ring item. It includes
  scheduling delays during that call. Low values with a full queue suggest the
  consumer has work available; high values alone do not prove compute load.
- `outside_reader_wall`: from successful reader return to next reader entry.
  The GMF manager calls ESP-SR feed in this interval. It includes feed work,
  downstream blocking, scheduling and manager overhead; it is NOT exclusive
  DSP CPU time. Compare with the printed feed budget (64 ms for 1024/16 kHz).
- `output_callback_gap`: time between nonempty output callbacks. Callback
  payload sizes may differ, so this alone is not a per-frame deadline metric.
- Existing `AFE ... +glitch/+in_drop`, feed/fetch counts and queue depths remain.
- `chan_cpu`: task runtime deltas, normalized to one core. 100% means one core;
  aggregate task use across two cores can reach 200%. IDLE0 and IDLE1 show
  per-core idle opportunity. A task newly created since the previous snapshot
  gets its first percentage on the next snapshot; the first sample is baseline.
  State is an instantaneous FreeRTOS task state, not time spent blocked.
- `snapshot_us`: wall cost of taking the task snapshot. FreeRTOS task snapshots
  briefly suspend scheduling and scan stack watermarks; profiling has overhead.
  There is no per-audio-frame logging from the new instrumentation. Allocation
  is bounded to 96 task statuses; allocation/capacity errors are logged.

Interval aggregates are approximate at reset boundaries. Start/stop transition
windows should be excluded from steady-state comparisons. The 32-bit runtime
clock uses short-interval unsigned deltas; avoid interpreting a sample spanning
an entire clock wrap. Sufficient idle time does not guarantee real-time deadlines
or reserve for camera streaming. This does not benchmark display/motor/camera
load or change servo movement.

## Owner test

1. Install the YAML using your existing Wi-Fi/Pipecat configuration. Preserve
   the earlier YAML for rollback. Start capturing the ESPHome log.
2. Leave Pipecat stopped for 30 seconds, to capture idle task baselines.
3. Press Audio Diagnostics, then Pipecat Start once. Ask a short question;
   leave about 20 seconds for listening/response samples.
4. Ask for a long story. After 15 seconds of playback, say the same normal-volume
   stop phrase. Do not compensate by lowering playback volume or shouting.
5. Press Stop; continue logging for 20 seconds. Send the complete log and Pipecat
   Input recording; report the intended phrase and approximate time of speech.

Interpretation: saturated relevant core plus high AFE task runtime supports a
compute-budget issue; substantial idle plus long feed intervals requires checking
blocking/scheduling/buffer exchange. These are hypotheses to refine, not automatic
proofs. A later controlled SE-off test is justified only after these measurements.
